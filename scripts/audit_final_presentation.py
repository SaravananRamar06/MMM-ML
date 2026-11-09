"""Read-only numerical audit of the supplied 20-slide deck; never refits a model.

Usage: python scripts/audit_final_presentation.py --pptx PATH [--raw PATH]
Outputs go in reports/presentation_audit_20261109, outside the locked run.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

import numpy as np


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def native(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(type(value).__name__)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--pptx', type=Path, required=True)
    parser.add_argument('--raw', type=Path)
    parser.add_argument('--presentation-ref', default='origin/claude/blissful-knuth-nwvl73')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    run = root / 'reports/jc_pinn_20261107'
    out = root / 'reports/presentation_audit_20261109'
    out.mkdir(exist_ok=True)
    protected = {p.name: sha(p) for p in run.glob('*') if p.is_file()}
    result = {'review_date': '2026-11-09', 'project_commit': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
        'deck_filename': args.pptx.name, 'deck_sha256': sha(args.pptx),
        'method': 'Saved-weight inference and saved-prediction reconstruction; no fitting or selection.'}
    pref = subprocess.check_output(['git', 'rev-parse', args.presentation_ref], cwd=root, text=True).strip()
    def blob(path):
        return subprocess.check_output(['git', 'show', f'{pref}:{path}'], cwd=root)
    github_deck = blob('presentation/Final Presentation - Porosity in an AM Wing Bracket.pptx')
    wb = blob('presentation/source/Comparison Study - Final.wbpj')
    systems = []
    for node in ET.fromstring(wb).iter():
        text = node.text or ''
        if node.tag.endswith('member-data') and '"AnalysisType": "Explicit"' in text:
            systems.append(re.search(r'"DisplayText": "([^"]+)"', text).group(1))
    tree_paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', pref], cwd=root, text=True).splitlines()
    result['presentation_branch'] = dict(commit=pref, ref=args.presentation_ref,
        downloaded_deck_matches_github=hashlib.sha256(github_deck).hexdigest()==result['deck_sha256'],
        companion_pdf_sha256=hashlib.sha256(blob('presentation/Final Presentation - Porosity in an AM Wing Bracket.pdf')).hexdigest(),
        workbench_sha256=hashlib.sha256(wb).hexdigest(), explicit_systems=systems,
        companion_solver_folder_committed=any('Comparison Study - Final_files/' in p for p in tree_paths),
        test_prediction_source_matches_main=blob('presentation/source/model/test_predictions.csv') == (run/'test_predictions.csv').read_bytes(),
        cv_prediction_source_matches_main=blob('presentation/source/model/cv_predictions.csv') == (run/'cv_predictions.csv').read_bytes())
    result['github_sources'] = {p: hashlib.sha256(blob(p)).hexdigest() for p in tree_paths
                                if p.startswith('presentation/source/results/')}
    ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
    with zipfile.ZipFile(args.pptx) as z:
        names = sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)],
                       key=lambda n: int(re.search(r'slide(\d+)', n).group(1)))
        result['slide_count'] = len(names)
        result['slides'] = [{'slide': i, 'text': '\n'.join(t.text or '' for t in
                             ET.fromstring(z.read(n)).findall('.//a:t', ns))}
                            for i, n in enumerate(names, 1)]
        for slide in result['slides']:
            note = f"ppt/notesSlides/notesSlide{slide['slide']}.xml"
            if note in z.namelist():
                slide['speaker_notes'] = '\n'.join(t.text or '' for t in
                    ET.fromstring(z.read(note)).findall('.//a:t', ns))
    # Reuse the independent NumPy verification calculations without executing its
    # final serializer, which fails on np.bool_ under the local NumPy version.
    # No source file or locked verification.json is altered.
    verifier = root / 'scripts/verify_jc_pinn.py'
    source = verifier.read_text().split('\npassed = all(')[0]
    scope = {'__file__': str(verifier), '__name__': '__audit__'}
    argv = sys.argv
    try:
        sys.argv = [str(verifier), str(run)]
        exec(compile(source, str(verifier), 'exec'), scope)
    finally:
        sys.argv = argv
    checks = scope['checks']
    checks['all_boolean_checks_passed'] = all(bool(v) for v in checks.values()
                                             if isinstance(v, (bool, np.bool_)))
    result['independent_numpy_checks'] = checks
    result['verifier_limitation'] = ('Unmodified verifier reaches JSON serialization and fails on np.bool_ '
                                    'with local NumPy. Calculations above evaluated all boolean checks including np.bool_.')
    rows = list(csv.DictReader((run / 'test_predictions.csv').open()))
    y = np.array([float(r['Svm']) for r in rows])
    p = np.array([float(r['JC_PINN']) for r in rows])
    e = p - y
    per_case = {}
    for r in rows:
        per_case.setdefault(int(r['id']), []).append((float(r['JC_PINN']) - float(r['Svm'])) ** 2)
    rm = {i: float(np.sqrt(np.mean(v))) for i, v in per_case.items()}
    result['test_recomputed'] = dict(cases=len(rm), points=len(y), mean_curve_rmse=np.mean(list(rm.values())),
        worst_curve_rmse=max(rm.values()), worst_case=max(rm, key=rm.get),
        pooled_rmse=np.sqrt(np.mean(e**2)), r2=1-np.sum(e**2)/np.sum((y-y.mean())**2),
        within_one_fraction=np.mean(np.abs(e) <= 1), max_absolute_error=np.max(np.abs(e)))
    R = json.loads((run / 'results.json').read_text())
    ctrl = json.loads((run / 'control_no_equation.json').read_text())
    base = json.loads((run / 'baselines.json').read_text())
    result['selected'] = R['selected']
    result['selected_group_mean'] = float(np.mean([g['metrics']['mean_rmse'] for g in
                                                 R['selection']['selected_trial']['groups']]))
    result['control_saved_summary'] = ctrl['control']
    result['baseline_saved_summary'] = {k: base[k] for k in ('single_mlp', 'ensemble_mlp')}
    result['control_verification_scope'] = ('Control summary arithmetic checked; control weights and per-query '
                                          'predictions are not committed, so control inference was not independently reproduced.')
    assert np.isclose(result['selected_group_mean'], ctrl['jc_pinn']['group_mean_rmse'])
    assert np.isclose(np.mean([g['mean_rmse'] for g in ctrl['control']['groups']]),
                      ctrl['control']['group_mean_rmse'])
    eq = json.loads((run / 'equation.json').read_text())
    mem = eq['members'][0]
    network_params = sum(np.asarray(mem[k]).size for k in ('W1', 'b1', 'W2', 'b2', 'w3', 'b3'))
    result['parameters'] = {'network_per_member': network_params, 'joint_constants_per_member': len(mem['theta']),
                            'total_per_member': network_params+len(mem['theta']), 'members': len(eq['members'])}
    manifest = json.loads((root / 'data/manifest.json').read_text())
    result['coverage'] = {str(T): {str(lr): sum(m['temperature'] == T and m['log10_strain_rate'] == lr
                           for m in manifest) for lr in (-5, -4, -3)} for T in (30, 100, 200, 300)}
    result['manifest_rows'] = sum(m['rows'] for m in manifest)
    result['porosity'] = {'case_values': sorted({1-m['density']/2700 for m in manifest}),
                          'study_density_for_phi_0p04': 2700*(1-.04)}
    all_rows = rows + list(csv.DictReader((run / 'cv_predictions.csv').open()))
    saved = {}
    for r in all_rows:
        saved.setdefault(int(r['id']), []).append((float(r['E11']), float(r['Svm'])))
    train_ids = set(R['train_ids'])
    train_queries = np.array([[m['temperature'], m['log10_strain_rate'], m['density'], m['shear_modulus'], strain]
        for m in manifest if m['id'] in train_ids for strain, _ in saved[m['id']]])
    result['final_scalers_match_training_queries'] = bool(
        np.allclose(train_queries.mean(0), eq['x_mean'], rtol=1e-12, atol=1e-12) and
        np.allclose(train_queries.std(0), eq['x_scale'], rtol=1e-12, atol=1e-12))
    assert result['final_scalers_match_training_queries']
    if args.raw:
        mismatches, max_delta, starts, ends = [], 0., [], []
        curves = {}
        for m in manifest:
            f = args.raw / f"simulation_{m['id']:04d}" / 'STR_STR.OUT'
            if sha(f) != m['sha256']:
                mismatches.append(m['id'])
            a = np.loadtxt(f, skiprows=1)
            grid, target = np.array(saved[m['id']]).T
            curve = np.interp(grid, a[:, 3], a[:, 2])
            max_delta = max(max_delta, float(np.max(np.abs(curve-target))))
            curves[m['id']] = curve
            starts.append(a[0, 2]); ends.append(a[-1, 2])
        effects = {}
        keys = ['temperature', 'log10_strain_rate', 'density', 'shear_modulus']
        for k in keys:
            levels = sorted({m[k] for m in manifest}); gaps = []
            for a in manifest:
                if a[k] == levels[-1]: continue
                next_level = levels[levels.index(a[k])+1]
                for b in manifest:
                    if b[k] == next_level and all(a[t] == b[t] for t in keys if t != k):
                        gaps.append(np.max(np.abs(curves[a['id']]-curves[b['id']])))
            effects[k] = dict(pairs=len(gaps), mean_largest_gap=float(np.mean(gaps)))
        result['raw_recheck'] = dict(files=len(manifest), hash_mismatch_ids=mismatches,
            resampled_vs_saved_max_absolute_delta=max_delta, mean_first_stress=np.mean(starts),
            mean_last_stress=np.mean(ends), every_end_below_start=all(b < a for a,b in zip(starts,ends)),
            factor_effects=effects)
        assert not mismatches and max_delta < 1e-9
    geom = json.loads((root / 'bracket/geometry_report/parts_20261026.json').read_text())['parts'][0]
    solid = geom['solids'][0]; box = solid['bounding_box_mm']
    cad = (root/'bracket/cad/Rib Bracket.STEP').read_bytes()
    result['geometry'] = dict(cad_sha_matches=sha(root/'bracket/cad/Rib Bracket.STEP')==geom['sha256'],
        cad_sha_matches_after_CRLF_normalization=hashlib.sha256(cad.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')).hexdigest()==geom['sha256'],
        envelope_mm=[box[i+3]-box[i] for i in range(3)], volume_cm3=solid['volume_mm3']/1000,
        mass_kg_at_2700=solid['volume_mm3']*1e-9*2700,
        semicylinder_area_mm2=np.pi*5*40)
    result['ansys_arithmetic_only'] = dict(elastic_over_builtin=595.27/320.79,
        jc_relative_difference_percent=100*(323.81-320.79)/320.79,
        builtin_reduction_from_elastic_percent=100*(595.27-320.79)/595.27,
        status='Peaks match embedded screenshots and presentation-branch source screenshots; Workbench confirms three explicit systems, but its companion solver folder is not committed.')
    trace = json.loads((run / 'training_trace_member0.json').read_text())
    result['training_trace'] = dict(initial_loss=trace['hist'][0][2], final_loss=trace['hist'][-1][2],
        reduction_factor=trace['hist'][0][2]/trace['hist'][-1][2])
    result['locked_run_files_unchanged'] = protected == {p.name: sha(p) for p in run.glob('*') if p.is_file()}
    assert checks['all_boolean_checks_passed'] and result['locked_run_files_unchanged']
    (out/'verification.json').write_text(json.dumps(result, indent=2, default=native, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in
                      ('slides','baseline_saved_summary','control_saved_summary')}, indent=2, default=native))


if __name__ == '__main__':
    main()
