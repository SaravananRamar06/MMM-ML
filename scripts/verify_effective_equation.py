"""Independently verify saved metrics, fold scaling, predictions and source hashes."""
import csv
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from effective_equation import digest, metrics, predict

folder = ROOT/'reports/effective_equation_20261031'
r = json.loads((folder/'results.json').read_text())
assert r['code_sha256'] == digest(ROOT/'src/effective_equation.py')
assert r['config_sha256'] == digest(ROOT/'configs/effective_equation.json')
assert r['split_sha256'] == digest(ROOT/'data/split.json')
split = json.loads((ROOT/'data/split.json').read_text())
assert r['raw_history_ids_opened'] == split['train']
assert not set(r['raw_history_ids_opened']) & set(split['test'])
with (folder/'predictions.csv').open() as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 36*120
assert {int(v['id']) for v in rows} == set(split['train'])
with (ROOT/'TEAM_8_extracted_results_set_1/simulation_matrix.csv').open() as f:
    matrix = {int(v['Simulation_ID']):v for v in csv.DictReader(f)}
ids = r['training_ids']
X = np.array([[float(matrix[i]['temperature']),np.log10(float(matrix[i]['strain_rate'])),
               float(matrix[i]['density']),float(matrix[i]['shear_modulus'])] for i in ids])
grid = np.array([float(v['E11']) for v in rows[:120]])
Y = np.array([float(v['observed_Svm']) for v in rows]).reshape(36,120)
baseline = np.array([float(v['mean_curve_cv']) for v in rows]).reshape(36,120)
checks = []
for family, rec in r['families'].items():
    cv = np.array([float(v[f'{family}_cv']) for v in rows]).reshape(36,120)
    for key, value in metrics(Y, cv).items():
        np.testing.assert_allclose(value, rec['cv'][key], rtol=1e-12, atol=1e-12)
    trial = next(t for t in rec['trials'] if t['alpha'] == rec['selected_alpha'])
    assert trial['metrics']['mean_rmse'] == min(t['metrics']['mean_rmse'] for t in rec['trials'])
    for fold, model in zip(r['folds'], trial['models']):
        tr = [ids.index(i) for i in fold['fit']]; va = [ids.index(i) for i in fold['validation']]
        assert not set(tr) & set(va) and sorted(tr+va) == list(range(36))
        np.testing.assert_allclose(model['mean'], X[tr].mean(0), rtol=1e-14)
        expected_scale = np.where(X[tr].std(0)>0, X[tr].std(0), 1.)
        np.testing.assert_allclose(model['scale'], expected_scale, rtol=1e-14)
        np.testing.assert_allclose(model['stress_scale'], np.sqrt(np.mean(Y[tr]**2)), rtol=1e-14)
        np.testing.assert_allclose(predict(model, X[va], grid), cv[va], rtol=1e-12, atol=1e-10)
        np.testing.assert_allclose(baseline[va], np.tile(Y[tr].mean(0),(len(va),1)), rtol=1e-12)
    final = np.array([float(v[f'{family}_final']) for v in rows]).reshape(36,120)
    np.testing.assert_allclose(predict(rec['final_training_model'], X, grid), final, rtol=1e-12, atol=1e-10)
    checks.append(f'{family}: metrics, fold scalers, baseline and reloaded predictions agree')
for a in r['raw_audit']:
    assert a['sha256'] == digest(ROOT/f"TEAM_8_extracted_results_set_1/simulation_{a['id']:04d}/STR_STR.OUT")
notebook = json.loads((ROOT/'notebooks/effective_equation_check.ipynb').read_text())
assert notebook['metadata']['equation_source_sha256'] == __import__('hashlib').sha256((ROOT/'src/effective_equation.py').read_text().encode()).hexdigest()
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        text = ''.join(cell['source'])
        if not text.startswith('%'):
            compile(text, '<notebook cell>', 'exec')
checks += ['36 training source hashes unchanged; no test target in predictions',
           'Notebook source matches checker; all Python cells compile']
smoke_path = ROOT/'work/notebook_equation_results/results.json'
smoke_passed = False
if smoke_path.exists():
    smoke = json.loads(smoke_path.read_text())
    assert smoke['raw_history_ids_opened'] == r['raw_history_ids_opened']
    for family in r['families']:
        for metric, value in r['families'][family]['cv'].items():
            np.testing.assert_allclose(smoke['families'][family]['cv'][metric], value, rtol=1e-12, atol=1e-12)
    smoke_passed = True
    checks.append('Notebook bootstrap, whitelist ZIP extraction and full computation executed locally; metrics match CLI')
evidence = dict(passed=True, checks=checks, unit_test_command='.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_effective_equation.py -v',
                notebook_computation_verified_locally=smoke_passed,
                hosted_colab_execution_verified=False,
                protected_artifact_hashes={p.name:digest(p) for p in (ROOT/'runs/score/final_Svm').iterdir() if p.is_file()})
(folder/'verification.json').write_text(json.dumps(evidence, indent=2)+'\n')
print(json.dumps(evidence, indent=2))
