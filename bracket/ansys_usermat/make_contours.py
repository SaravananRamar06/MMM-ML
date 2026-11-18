"""Make contour pictures of solved bracket runs with MAPDL's post-processor (post_contours.mac).

Usage: python bracket/ansys_usermat/make_contours.py OUT_DIR RUN_DIR[:label] [RUN_DIR[:label] ...]
Each RUN_DIR holds bracket.rst and bracket_history.csv. The peak time is read from the history (largest
reaction along the load). Pictures: OUT_DIR/<label>_<peak|final>_<quantity>.png, plus contours_index.json.
Needs MAPDL 2024 R1 (v241); a USERMAT run also needs ANS_USER_PATH (the routine is not called in POST1,
but MAPDL checks the library at start).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from history import load_history  # noqa: E402

EXE = r'C:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\ANSYS241.exe'
BASE = ['uy', 'von_mises', 'max_principal', 'min_principal', 'eppl']
EXTRA = ['flag_svar3', 'flow_stress_svar2']


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    index = {}
    for arg in sys.argv[2:]:
        run, sep, label = arg.rpartition(':')
        if not sep or '\\' in label or '/' in label:  # no label given (a drive letter's colon is not one)
            run, label = arg, ''
        run = Path(run).resolve()
        label = label or run.name
        rows = load_history(run / 'bracket_history.csv')
        peak = max(rows, key=lambda r: r['F_N'])
        um = 1 if any(r['svar1_max_elem'] > 0 for r in rows) else 0
        pl = 1 if any(r['eppl_eqv_max_elem'] > 0 for r in rows) else 0
        work = run / '_contours'
        if work.exists():
            shutil.rmtree(work)
        work.mkdir()
        shutil.copyfile(run / 'bracket.rst', work / 'bracket.rst')
        mac = (HERE / 'post_contours.mac').read_text()
        (work / 'drive.inp').write_text(f'_TPEAK = {peak["time"]}\n_UM = {um}\n_PL = {pl}\n' + mac)
        r = subprocess.run([EXE, '-b', '-np', '1', '-dir', str(work), '-j', 'bracket', '-i', 'drive.inp', '-o', 'post.out'],
                           cwd=work, capture_output=True, text=True)
        pngs = sorted(work.glob('bracket*.png'))
        base = BASE if pl else [q for q in BASE if q != 'eppl']
        names = [f'{t}_{q}' for t in ('peak', 'final') for q in base + (EXTRA if um else [])]
        assert len(pngs) == len(names), (label, len(pngs), len(names), r.returncode)
        for p, n in zip(pngs, names):
            shutil.copyfile(p, out / f'{label}_{n}.png')
        index[label] = {'run': str(run), 'peak_time': peak['time'], 'peak_u_mm': peak['u_mm'],
                        'peak_F_kN': peak['F_N'] / 1e3, 'final_F_kN': rows[-1]['F_N'] / 1e3,
                        'pictures': [f'{label}_{n}.png' for n in names]}
        print(label, 'peak at t =', peak['time'], '->', len(pngs), 'pictures')
    (out / 'contours_index.json').write_text(json.dumps(index, indent=2) + '\n', newline='\n')


if __name__ == '__main__':
    main()
