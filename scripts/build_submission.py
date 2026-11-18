"""Build the Team 8 end-semester submission folders from one commit of this repository.

Upload 1 (UMAT/UPF code and FE model files) and the LaTeX/PDF part of Upload 2 are built from a clean
`git archive` of the commit, so nothing untracked (raw data, .venv, credentials, scratch) can enter.
The Canva presentation exports are copied in only if given (--presentation DIR with
Team8_Presentation.pptx / .pdf).

Usage:
  python scripts/build_submission.py [--commit REV] [--out DIR] [--presentation DIR] [--latex-bin DIR]

Defaults: --commit HEAD, --out %USERPROFILE%/Documents/Team8_Submission. --latex-bin is the folder with
pdflatex/bibtex; when given, the LaTeX source zip is test-compiled on its own in a temporary folder.
"""
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = 'https://github.com/SaravananRamar06/MMM-ML'
SCRATCH = {'.rst', '.db', '.full', '.esav', '.emat', '.err', '.lock', '.page', '.r001', '.rdb', '.ldhi', '.mntr', '.bat'}
FIG_EXT = ('.pdf', '.png', '.jpg')


def git(*args):
    return subprocess.run(['git', '-C', str(ROOT), *args], check=True, capture_output=True, text=True).stdout.strip()


def export(commit, dest):
    """Extract the tracked tree of `commit` into dest (git archive), nothing else."""
    data = subprocess.run(['git', '-C', str(ROOT), 'archive', '--format=tar', commit], check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(dest, filter='data')


def copy(src, dst, skip_scratch=False):
    src, dst = Path(src), Path(dst)
    if src.is_dir():
        for f in sorted(src.rglob('*')):
            if f.is_file() and not (skip_scratch and f.suffix.lower() in SCRATCH):
                copy(f, dst / f.relative_to(src))
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def manifest(folder, commit, title):
    files = sorted(f for f in folder.rglob('*') if f.is_file() and f.name != 'MANIFEST.txt')
    total = sum(f.stat().st_size for f in files)
    lines = [title, f'Repository: {REPO_URL}', f'Commit: {commit}', f'Files: {len(files)}   Total size: {total:,} bytes',
             '', f"{'size (bytes)':>14}  {'sha256':<64}  path"]
    lines += [f'{f.stat().st_size:>14,}  {sha256(f)}  {f.relative_to(folder).as_posix()}' for f in files]
    write(folder / 'MANIFEST.txt', '\n'.join(lines) + '\n')
    return len(files), total


def zip_dir(folder, zpath, arc_root=None):
    zpath.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(folder.rglob('*')):
            if f.is_file():
                rel = f.relative_to(folder).as_posix()
                z.write(f, f'{arc_root}/{rel}' if arc_root else rel)


def py(*args, cwd):
    subprocess.run([sys.executable, *args], check=True, cwd=cwd, capture_output=True, text=True)


def numbers(snap):
    n = json.loads((snap / 'report/numbers.json').read_text())
    return {k: v.replace('{,}', ',') for k, v in n.items()}


# ---------------------------------------------------------------------------------------------- Upload 1
def build_upload1(snap, out, commit, N):
    u1 = out / 'Upload_1_UMAT_UPF_and_FE_model'
    a = u1 / '01_USERMAT_ANSYS_UPF'
    copy(snap / 'umat/jc_pinn_usermat3d.F', a / 'jc_pinn_usermat3d.F')
    copy(snap / 'umat/templates', a / 'generator/templates')
    copy(snap / 'scripts/write_umat.py', a / 'generator/write_umat.py')
    copy(snap / 'umat/verification.json', a / 'verification/verification.json')
    copy(snap / 'umat/test', a / 'verification/offline_test_driver')
    for f in ('single_element.mac', 'expected_single_element.csv', 'compare.py'):
        copy(snap / 'umat/ansys_test' / f, a / 'single_element_test' / f)
    copy(snap / 'umat/ansys_test/results_2026-11-17', a / 'single_element_test/results_2026-11-17_MAPDL2024R1_PASS')
    copy(snap / 'umat/ansys_test/results_2026-11-17/build_ifx.bat', a / 'build/build_ifx.bat')
    copy(snap / 'umat/ansys_test/results_2026-11-17/build_log_tail.txt', a / 'build/build_log_tail.txt')
    write(a / 'README.md', README_USERMAT.format(**N))

    c = u1 / '03_FE_model_ANSYS'
    copy(snap / 'bracket/ansys', c / 'workbench_project', skip_scratch=True)
    wb = snap / 'bracket/ansys_usermat/workbench_2024R1'
    for f in sorted(wb.iterdir()):
        if f.name != 'results_2026-11-18':
            copy(f, c / 'workbench_2024R1_USERMAT' / f.name, skip_scratch=f.suffix.lower() != '.bat')
    copy(snap / 'bracket/cad', c / 'cad')
    for f in sorted((snap / 'bracket/ansys_usermat').glob('*')):
        if f.is_file() and f.suffix in ('.py', '.mac'):
            copy(f, c / 'scripts' / f.name)
    decks = c / 'mapdl_decks'
    tool = snap / 'bracket/ansys_usermat'
    py(str(tool / 'make_decks.py'), str(decks / '5mm'), cwd=snap)
    py(str(tool / 'make_decks.py'), '--porosity', str(decks / 'porosity_density_only'), cwd=snap)
    py(str(tool / 'make_decks.py'), '--porosity-gphi', str(decks / 'porosity_G_coupled_D5'), cwd=snap)
    with tempfile.TemporaryDirectory() as tmp:
        fine, fine_ep = Path(tmp) / 'ds_fine.dat', Path(tmp) / 'ds_fine_ep.dat'
        py(str(tool / 'refine_mesh.py'), str(fine), cwd=snap)
        py(str(tool / 'refine_mesh.py'), str(fine_ep), str(snap / 'bracket/ansys/Elastic_files/dp0/SYS/MECH/ds.dat'), cwd=snap)
        py(str(tool / 'make_decks.py'), '--source', str(fine), '--label', 'fine', str(decks / '2p5mm'), cwd=snap)
        py(str(tool / 'make_decks.py'), '--source', str(fine_ep), '--label', 'fine', '--kinds', 'ep_miso', str(decks / '2p5mm'), cwd=snap)
    write(c / 'README.md', README_FE.format(**N))

    d = u1 / '04_Results'
    for name in ('results_2026-11-17', 'porosity_2026-11-17', 'porosity_gphi_2026-11-17', 'mesh_2026-11-17', 'mesh_ep_2026-11-17'):
        copy(snap / 'bracket/ansys_usermat' / name, d / name)
    copy(wb / 'results_2026-11-18', d / 'workbench_usermat_2026-11-18')
    write(d / 'README.md', README_RESULTS)

    e = u1 / '05_ML_model'
    for f in ('equation.json', 'selection_lock.json'):
        copy(snap / 'reports/jc_pinn_20261107' / f, e / 'locked_run' / f)
    copy(snap / 'src/jc_pinn.py', e / 'jc_pinn.py')
    copy(snap / 'configs/jc_pinn.json', e / 'jc_pinn.json')
    copy(snap / 'notebooks/jc_pinn_colab.ipynb', e / 'jc_pinn_colab.ipynb')
    write(e / 'README.md', README_ML.format(**N))

    write(u1 / 'README.md', README_TOP.format(commit=commit, repo=REPO_URL, **N))
    return u1


# ---------------------------------------------------------------------------------------------- Upload 2
def build_upload2(snap, out, presentation):
    u2 = out / 'Upload_2_PPT_and_Report'
    copy(snap / 'report/report.pdf', u2 / 'Team8_Report.pdf')
    tex = (snap / 'report/report.tex').read_text(encoding='utf-8')
    names = sorted(set(re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', tex)))
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / 'Team8_Report_LaTeX_source'
        for f in ('report.tex', 'refs.bib', 'numbers.tex'):
            copy(snap / 'report' / f, src / 'report' / f)
        for n in names:
            found = [snap / 'figures' / f'{n}{ext}' for ext in FIG_EXT if (snap / 'figures' / f'{n}{ext}').exists()]
            if not found:
                raise FileNotFoundError(f'figure {n} not found in figures/')
            for f in found:
                copy(f, src / 'figures' / f.name)
        write(src / 'README.txt', 'Build: cd report, then pdflatex report, bibtex report, pdflatex report (twice).\n'
                                  'Figures are in ../figures (\\graphicspath). numbers.tex holds every number '
                                  '(generated by scripts/write_latex_numbers.py in the repository).\n')
        zip_dir(src, u2 / 'Team8_Report_LaTeX_source.zip', arc_root='Team8_Report_LaTeX_source')
    if presentation:
        for f in ('Team8_Presentation.pptx', 'Team8_Presentation.pdf'):
            if (Path(presentation) / f).exists():
                copy(Path(presentation) / f, u2 / f)
    return u2, names


# ---------------------------------------------------------------------------------------------- submission files
def build_submission_files(snap, out, u1, u2):
    """One folder with everything important, grouped by kind (copies of Upload 1/2 plus the team JC study)."""
    sf = out / 'submission files'
    copy(u2 / 'Team8_Report.pdf', sf / '1_Report' / 'Team8_Report.pdf')
    copy(u2 / 'Team8_Report_LaTeX_source.zip', sf / '1_Report' / 'Team8_Report_LaTeX_source.zip')
    for f in ('Team8_Presentation.pptx', 'Team8_Presentation.pdf'):
        if (u2 / f).exists():
            copy(u2 / f, sf / '2_Presentation' / f)
    fea = sf / '3_FEA_simulations'
    copy(snap / 'presentation/source/Comparison Study - Final.wbpj', fea / 'A_Team_JC_comparison_study' / 'Comparison Study - Final.wbpj')
    copy(snap / 'presentation/source/results', fea / 'A_Team_JC_comparison_study' / 'results')
    copy(u1 / '03_FE_model_ANSYS', fea / 'B_Bracket_FE_model_ANSYS')
    copy(u1 / '04_Results', fea / 'C_Bracket_results_USERMAT_EP_porosity_mesh')
    copy(u1 / '01_USERMAT_ANSYS_UPF', sf / '4_USERMAT_UMAT_code' / 'USERMAT_ANSYS_UPF')
    copy(snap / 'reports/jc_pinn_20261107', sf / '5_ML_model_weights' / 'locked_run_jc_pinn_20261107')
    for f in ('jc_pinn.py', 'jc_pinn.json'):
        copy(u1 / '05_ML_model' / f, sf / '5_ML_model_weights' / f)
    for f in sorted((snap / 'notebooks').glob('*.ipynb')):
        copy(f, sf / '6_Colab_notebook' / f.name)
    write(sf / 'README.md', README_SF)
    return sf


def test_latex_zip(zpath, latex_bin):
    """Unzip into a temp folder and compile there, on its own."""
    env = dict(os.environ, PATH=str(latex_bin) + os.pathsep + os.environ.get('PATH', ''))
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zpath) as z:
            z.extractall(tmp)
        rep = Path(tmp) / 'Team8_Report_LaTeX_source' / 'report'
        for cmd in (['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'report.tex'], ['bibtex', 'report'],
                    ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'report.tex'],
                    ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'report.tex']):
            exe = Path(latex_bin) / (cmd[0] + ('.exe' if os.name == 'nt' else ''))
            r = subprocess.run([str(exe), *cmd[1:]], cwd=rep, env=env, capture_output=True, text=True)
            if r.returncode:
                raise RuntimeError(f'{cmd[0]} failed in the unzipped source: {r.stdout[-800:]}')
        log = (rep / 'report.log').read_text(errors='replace')
        pages = re.search(r'Output written on report\.pdf \((\d+) pages', log)
        return {'pages': int(pages.group(1)) if pages else None,
                'undefined': len(re.findall(r'undefined', log)), 'overfull': len(re.findall(r'Overfull \\[hv]box', log)),
                'qq_in_log': log.count('??')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--commit', default='HEAD')
    ap.add_argument('--out', default=str(Path.home() / 'Documents' / 'Team8_Submission'))
    ap.add_argument('--presentation')
    ap.add_argument('--latex-bin')
    a = ap.parse_args()
    commit = git('rev-parse', a.commit)
    out = Path(a.out).resolve()
    if ROOT.resolve() in out.parents or out == ROOT.resolve():
        sys.exit('build the submission outside the repository')
    for sub in ('Upload_1_UMAT_UPF_and_FE_model', 'Upload_2_PPT_and_Report', 'submission files'):
        if (out / sub).exists():
            shutil.rmtree(out / sub)
    with tempfile.TemporaryDirectory() as tmp:
        snap = Path(tmp) / 'snapshot'
        export(commit, snap)
        N = numbers(snap)
        u1 = build_upload1(snap, out, commit, N)
        u2, figs = build_upload2(snap, out, a.presentation)
        sf = build_submission_files(snap, out, u1, u2)
    n3, s3 = manifest(sf, commit, 'Team 8 - submission files (all important files)')
    n1, s1 = manifest(u1, commit, 'Team 8 - Upload 1: UMAT/UPF code and FE model files')
    zip1 = out / 'Team8_UMAT_UPF_FE_model.zip'
    zip_dir(u1, zip1, arc_root='Team8_UMAT_UPF_FE_model')
    test = test_latex_zip(u2 / 'Team8_Report_LaTeX_source.zip', a.latex_bin) if a.latex_bin else None
    n2, s2 = manifest(u2, commit, 'Team 8 - Upload 2: end-semester PPT and report')
    print(json.dumps({'commit': commit, 'out': str(out),
                      'upload1': {'files': n1, 'bytes': s1, 'zip': str(zip1), 'zip_bytes': zip1.stat().st_size},
                      'upload2': {'files': n2, 'bytes': s2, 'figures_in_latex_zip': figs},
                      'submission_files': {'files': n3, 'bytes': s3},
                      'latex_zip_test': test}, indent=2))


# ---------------------------------------------------------------------------------------------- READMEs
README_TOP = """# Team 8: UMAT/UPF code and FE model files

**Course:** Multiscale Modelling of Materials using Machine Learning, IIITDM Kancheepuram (instructor Prof. Arul Kumar Mariyappan).
**Team 8:** Pranav Parasuram C (ME24B1061), R Saravanan (ME24I1006), Dinesh Y (ME24B1043), Amit Narayan K (ME24I1024).
**Repository:** {repo}, commit `{commit}`. Every file here was copied from that commit, unchanged, except the generated MAPDL decks (see `03_FE_model_ANSYS/README.md`).

## Overview

- **Component:** an additively manufactured (LPBF) AlSi10Mg aircraft wing-rib bracket. It is the team's ANSYS Workbench model: fixed mounting faces, an imposed displacement UX = -2 mm at the bore, and quadratic SOLID186 elements of about 5 mm ({MeshElemCoarse} elements).
- **Material and porosity:**
  - porosity phi = 1 - density/2700 (user decision);
  - study point phi = 4 % (density 2592 kg/m3), 100 degC, strain rate 1e-4 /s;
  - G(phi) = 25300 (1 - phi) MPa, an assumed upper bound (decision D5) that the data's G levels follow exactly.
- **ML model (JC-PINN):** the team's customised Johnson-Cook law (Equation 1) multiplied by exp(delta) from a 5-16-16-1 tanh network ({Params} weights each, five copies).
  - The model was selected on the 36 training simulations, locked, then scored once on 37 test simulations: mean curve RMSE {TestMean} MPa, R^2 = {TestRsq}.
  - The test set is not blind.
- **From model to FE material:** `scripts/write_umat.py` writes the locked weights (`05_ML_model/locked_run/equation.json`) into an ANSYS USERMAT (`01_...`), the only FE solver used.
  - It is J2 plasticity with a radial return and a consistent tangent, and the flow stress is the JC-PINN prediction.
  - Offline it reproduces the model to {VerStressErr} (relative).
  - In MAPDL 2024 R1, a single element matches to {SeMaxDiff} MPa (tolerance {SeTol} MPa): final S11 {SeSFinal} MPa, EQPS {SeEqpsFinal}.
- **Results on the bracket** (`04_Results`):
  - **Peak and softening:** the reaction peaks at {BrUsermatPeakkN} kN at UX = -{BrUsermatPeakUX} mm, then softens to {BrUsermatFinalkN} kN at -2 mm.
  - **Porosity, phi 0 -> 7.85 %:**
    - density alone changes the peak by {PorDensPeakChangePct} %;
    - with G coupled (D5), the peak changes by {GphiPeakChangePct} % and the force at -2 mm by {GphiFinalChangePct} %.
  - **Mesh:** halving the element size changes the peak by {BrMeshPeakChangePct} % and later forces by {MeshForceOneChangePct} %, against at most {MeshEpMaxChangePct} % for a hardening material. The response after yield is therefore mesh dependent.

## Limits (all apply)

- **Not a blind test.** The 37 test cases were explored in earlier project stages.
- **Simulations, not experiments.** The data are simulations, with units (degC, 1/s, MPa, kg/m3) confirmed by the user but no documentation of the generator. Nothing is experimentally validated.
- **Temperature range.** Nothing is validated above 200 degC.
- **Mesh dependence.** Bracket forces after yield are mesh dependent; they are not a converged strength.
- **G(phi).** It is an assumed upper bound, not measured, so porosity effects are a lower estimate.
- **No critical flaw length.** No service load exists, and LEFM is not valid at the yielding peak.
- **Assumptions.** nu = 0.33 is assumed; small strain; one material condition (the study point).

## Folder map

| Folder | Contents |
|---|---|
| `01_USERMAT_ANSYS_UPF/` | The ANSYS USERMAT that was used, its generator, the build script and log, the single-element test (PASS) and the offline verification with its test driver |
| `03_FE_model_ANSYS/` | The Workbench project (solver scratch files removed), CAD (STEP), MAPDL batch decks (5 mm, porosity cases, 2.5 mm refinement), the deck and post-processing scripts, and run commands |
| `04_Results/` | The committed evidence: histories (CSV), summaries (JSON), plots (PNG) and READMEs for every bracket study |
| `05_ML_model/` | The locked equation and its selection lock, the model code, its config and the Colab notebook |
| `MANIFEST.txt` | Every file, its size and SHA-256, and the commit |
"""

README_USERMAT = """# ANSYS USERMAT (UPF) for the JC-PINN

`jc_pinn_usermat3d.F` is the `usermat3d` routine used in every ANSYS run. It is **generated**, not hand written: `generator/write_umat.py` fills `generator/templates/` with the locked weights (`../05_ML_model/locked_run/equation.json`). Do not edit it by hand.

## Build (MAPDL 2024 R1, Windows)

1. Make a build folder. Copy into it ANSYS's `<install>/ansys/customize/user/usermat.F` and `usermatth.F`. In v241, `usermat.F` contains the stock `usermat3d`: delete that block (from `*deck,usermat3d` to its `end`).
2. Copy `jc_pinn_usermat3d.F` in as `usermat3d.F`.
3. Run ANSYS's `ANSUSERSHARED.bat` (`<install>/ansys/custom/user/winx64/`) for `usermat`. The v241 script expects ifort 2023 and VS 2019.
   - The tested library was built with `build/build_ifx.bat`: the same compile and link steps with Intel ifx 2026.2 and VS 2019 Build Tools 16.11.
   - The log is in `build/build_log_tail.txt`.
4. Set `ANS_USER_PATH` to the build folder before starting MAPDL or Workbench.

## Input

```
TB,USER,1,1,7
TBTEMP,0
TBDATA,1,100,1.0E-4,2592,24541,0.33,0      ! T degC, rate 1/s, density kg/m3, G MPa, nu (assumed), ITEMP
TBDATA,7,0                                 ! GEL (0 = use G)
TB,STATE,1,,4
```

- **Constants:** T, strain rate, density, G, nu, ITEMP (0 = use constant 1; 1 = use the analysis temperature), GEL (elastic shear modulus; 0 = G).
- **State variables:** SVAR1 = equivalent plastic strain, SVAR2 = current flow stress, SVAR3 = range flag (1 = EQPS > 0.0999; 2 = input outside the data; 4 = 200-300 degC), SVAR4 = Newton iterations.
- **Range:** outside the data the routine flags; it does not clamp.

## Verification

- **Offline** (`verification/verification.json`; gfortran with a test driver):
  - flow stress at {VerFlowPoints} points to {VerStressErr} (relative);
  - slope to {VerSlopeErr};
  - on the flow curve to {VerCurveErr};
  - increment-size spread {VerIncSpread} MPa;
  - consistent tangent to {VerTangentErr};
  - all {VerFlagChecks} flag cases correct.
- **MAPDL 2024 R1 single element** (`single_element_test/`): one SOLID185 pulled to eps11 = 0.12. S11 matches `expected_single_element.csv` to {SeMaxDiff} MPa at all {SePoints} substeps (tolerance {SeTol} MPa). Final S11 {SeSFinal} MPa, EQPS {SeEqpsFinal}, flag {SeFlagFinal}. **PASS.**

## Limits

- **Strain.** The data's total strain E11 is read as plastic strain.
- **Assumptions.** nu = 0.33 is assumed. Fixed temperature and strain rate per run. Small strain.
- **Elements.** Only `usermat3d` is provided: 3D, plane strain and axisymmetric.
- **Softening.** The material softens, so FE results after yield are mesh dependent.
- **No validation.** Nothing is experimentally validated.
"""

README_FE = """# ANSYS FE model of the wing-rib bracket

- `workbench_project/`: the team's Workbench 2026 R1 project (`Elastic.wbpj` with `Elastic_files/`), as committed.
  - Solver scratch files (`.rst`, `.err`) were left out, so Workbench will ask to re-solve before showing results.
  - Open it in Workbench 2026 R1 or later.
- `workbench_2024R1_USERMAT/`: the bracket with the JC-PINN USERMAT as a Workbench 2024 R1 project (`Bracket_USERMAT_2024R1.wbpj`, added 18 Nov 2026, post-hoc re-run).
  - Same supports, load and material block as the batch decks; swept 5 mm mesh. The material is the `TB,USER` command snippet under the body.
  - Open it with `open_project.bat`, which sets `ANS_USER_PATH`; the result file is left out, so solve once (about two minutes) to see contours. Its README has the settings and the comparison with the batch run.
- `cad/`: `Rib Bracket.STEP` and `Bracket support.STEP`.
- `scripts/`: the deck generator, mesh refinement and post-processing (`make_decks.py`, `refine_mesh.py`, `post_bracket.mac`, plot scripts).
- `mapdl_decks/`: batch decks regenerated from the Workbench solver input, for MAPDL 2024 R1. The 2026 R1 `eblock,COMPACT` element block is rewritten in the standard layout, with the same elements.
  - `5mm/`: `elastic`, `ep_miso` (the Workbench elastic-plastic card) and `usermat` (JC-PINN at the study point).
  - `porosity_density_only/`: phi0, phi4, phi785 (G fixed) and G_lo, G_hi.
  - `porosity_G_coupled_D5/`: gphi0, gphi4, gphi785 (G = 25300 (1 - phi)).
  - `2p5mm/`: `elastic_fine`, `usermat_fine`, `ep_miso_fine`, a uniform 2x2x2 refinement ({MeshElemFine} elements). This is not a Workbench remesh.

## Run (Windows, MAPDL 2024 R1)

For a USERMAT deck, build the USERMAT first (`../01_USERMAT_ANSYS_UPF/README.md`). Then, in the deck's folder:

```bat
set "ANS_USER_PATH=<folder with usermatLib.dll>" && "C:\\Program Files\\ANSYS Inc\\v241\\ansys\\bin\\winx64\\ANSYS241.exe" -b -smp -np 4 -dir . -j bracket -i bracket.dat -o bracket.out
```

- The elastic and ep_miso decks do not need `ANS_USER_PATH`.
- Each deck writes `bracket_history.csv` per substep: reaction at the fixed support, peak element von Mises, EPPL, SVAR1 and flagged elements.
- The 5 mm USERMAT run takes about a minute on 4 cores; the 2.5 mm run took about {MeshFineWallMin} min.
- Expected results are in `../04_Results/`.

## Limits

- **Boundary conditions.** Imposed displacement, as in the Workbench project. No service load magnitude exists.
- **Mesh dependence.** Results after yield depend on the mesh.
- **Material condition.** The EP card is a different material condition (yield 251 MPa, hardening). It is used only as a reference and to test the mesh.
"""

README_RESULTS = """# Results (committed evidence, unchanged)

| Folder | Study |
|---|---|
| `results_2026-11-17/` | Bracket on the 5 mm mesh: elastic, EP (MISO) and the JC-PINN USERMAT |
| `porosity_2026-11-17/` | Porosity, density only (G fixed), plus G sensitivity at phi = 4 % |
| `porosity_gphi_2026-11-17/` | Porosity with density and G coupled by decision D5, G = 25300 (1 - phi) |
| `mesh_2026-11-17/` | Mesh study: 5 mm against the 2x2x2 refinement (JC-PINN) |
| `mesh_ep_2026-11-17/` | The same refinement with the hardening EP material |
| `workbench_usermat_2026-11-18/` | The Workbench 2024 R1 USERMAT project solved (post-hoc): reaction history, summary, contour pictures, solver output |

Each folder has its own README with the run commands, a results table and its limits. Bracket forces after yield are mesh dependent, and nothing is experimentally validated.
"""

README_ML = """# The locked ML model (JC-PINN)

- `locked_run/equation.json`: the locked model, with Equation 1's constants and the five correction networks (5-16-16-1 tanh, {Params} weights each).
- `locked_run/selection_lock.json`: the SHA-256 fingerprint written before the test set was read.
- `jc_pinn.py` (with `jc_pinn.json`) trains, selects, locks and evaluates the model. `equation_predict` evaluates the saved equation with NumPy only.
- `jc_pinn_colab.ipynb` runs on Colab, Kaggle or locally. `MODE = 'PREDICT'` needs no data.

**How the FE material gets its weights:** `../01_USERMAT_ANSYS_UPF/generator/write_umat.py` reads `equation.json` and writes the constants and all network weights into the Fortran core.
- Offline, the routine reproduces `equation_predict` to {VerStressErr} (relative).
- Strain E11 is read as equivalent plastic strain, and the elastic part comes from G and an assumed nu = 0.33.

The instructor's raw data (`TEAM_8_extracted_results_set_1/`) are not included.
"""

README_SF = """# Team 8: submission files

Everything important in one place. The files are copies of the two upload folders plus the team's JC comparison study; nothing was changed.

| Folder | Contents |
|---|---|
| `1_Report/` | `Team8_Report.pdf` and its LaTeX source (zip, compiles on its own) |
| `2_Presentation/` | `Team8_Presentation.pptx` and `.pdf` (exported from Canva; 1 intro, 15 content, 1 outro slide) |
| `3_FEA_simulations/A_Team_JC_comparison_study/` | The team's Workbench comparison project (`Comparison Study - Final.wbpj`, project file only) and its equivalent-stress screenshots: elastic, built-in JC, user-defined JC |
| `3_FEA_simulations/B_Bracket_FE_model_ANSYS/` | The teams bracket Workbench project and the Workbench 2024 R1 USERMAT project (workbench_2024R1_USERMAT/, open with open_project.bat), both without solver scratch; CAD, MAPDL decks (elastic, EP, USERMAT, porosity, 2.5 mm mesh) and scripts |
| `3_FEA_simulations/C_Bracket_results_USERMAT_EP_porosity_mesh/` | Results of every bracket run: histories (CSV), summaries (JSON), plots and READMEs |
| `4_USERMAT_UMAT_code/` | The ANSYS USERMAT (UPF) used in every run, with generator, build log, single-element test and verification |
| `5_ML_model_weights/` | The locked run `jc_pinn_20261107` (`equation.json` holds Equation 1's constants and all network weights; `selection_lock.json` is its fingerprint), with `jc_pinn.py` and `jc_pinn.json` |
| `6_Colab_notebook/` | `jc_pinn_colab.ipynb` (runs on Colab; `MODE = 'PREDICT'` needs no data) and `jc_pinn_explained.ipynb` |
| `MANIFEST.txt` | Every file, its size and SHA-256, and the commit |

Not included: the instructor's raw data (`TEAM_8_extracted_results_set_1/`), solver scratch files, the compiled USERMAT DLL, environments and credentials.

Limits: the test is not blind; the units are user-confirmed; nothing is validated above 200 degC; nothing is experimentally validated; bracket forces after yield are mesh dependent; G(phi) is an assumed upper bound (D5); no critical flaw length is given.
"""


if __name__ == '__main__':
    main()
