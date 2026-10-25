"""Read-only verification of raw data, preprocessing and the final local artifact.

Run: .venv/bin/python reports/verify_final_model.py
Writes new audit evidence only; never rebuilds caches, fits, or changes model files.
"""
import csv
import hashlib
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import joblib
import numpy as np
import sklearn


def verify():
    split = json.loads((ROOT / 'data/split.json').read_text())
    manifest = {m['id']: m for m in json.loads((ROOT / 'data/manifest.json').read_text())}
    with np.load(ROOT / 'data/curves_Svm.npz', allow_pickle=False) as z:
        ids, X, Y, grid = (z[k].copy() for k in ('ids', 'X', 'Y', 'strain'))
        assert str(z['target']) == 'Svm'
    assert X.shape == (73, 4) and Y.shape == (73, 120)
    assert np.isfinite(X).all() and np.isfinite(Y).all()
    assert len(set(ids)) == 73
    tr, te = np.isin(ids, split['train']), np.isin(ids, split['test'])
    assert len(set(split['train'])) == 36 and len(set(split['test'])) == 37
    assert not (set(split['train']) & set(split['test']))
    assert set(split['train']) | set(split['test']) == set(ids) == set(manifest)
    permutation = np.random.default_rng(split['seed']).permutation(ids)
    assert set(permutation[:36]) == set(split['train'])
    raw = ROOT / 'TEAM_8_extracted_results_set_1'
    with (raw / 'simulation_matrix.csv').open() as f:
        matrix = {int(r['Simulation_ID']): r for r in csv.DictReader(f)}
    max_cache_error, rows = 0.0, 0
    for i, case in enumerate(ids):
        files = list(raw.glob(f'simulation_{int(case):04d}/STR_STR.OUT'))
        assert len(files) == 1, (int(case), 'source path')
        path = files[0]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest[int(case)]['sha256']
        a = np.loadtxt(path, skiprows=1, usecols=(2, 3))
        stress, strain = a.T
        assert np.isfinite(a).all() and np.all(np.diff(strain) > 0)
        assert strain[0] <= grid[0] < grid[-1] <= strain[-1]
        assert len(a) == manifest[int(case)]['rows']
        expected = np.interp(grid, strain, stress)
        error = float(np.max(np.abs(expected - Y[i])))
        max_cache_error = max(max_cache_error, error)
        np.testing.assert_allclose(Y[i], expected, rtol=0, atol=1e-12)
        r = matrix[int(case)]
        np.testing.assert_allclose(X[i], [float(r['temperature']), np.log10(float(r['strain_rate'])),
                                        float(r['density']), float(r['shear_modulus'])], rtol=0, atol=0)
        rows += len(a)
    folder = ROOT / 'runs/score/final_Svm'
    model = joblib.load(folder / 'model.joblib')
    Z = np.column_stack([np.repeat(X[tr], len(grid), axis=0), np.tile(grid, tr.sum())])
    np.testing.assert_allclose(model.xs.mean_, Z.mean(0), rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(model.xs.var_, Z.var(0), rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose([model.ym, model.ys], [Y[tr].mean(), Y[tr].std()], rtol=1e-12)
    assert model.xs.n_samples_seen_ == 36 * 120
    parameters = [sum(a.size for a in n.coefs_ + n.intercepts_) for n in model.nets]
    assert parameters == [385] * 5
    assert model.alpha == 0.001 and model.hidden == (16, 16)
    assert all(n.activation == 'tanh' and n.out_activation_ == 'identity' for n in model.nets)
    p = model.predict(X[te])
    with np.load(folder / 'test_predictions.npz', allow_pickle=False) as z:
        np.testing.assert_array_equal(z['test_ids'], ids[te])
        np.testing.assert_array_equal(z['truth'], Y[te])
        np.testing.assert_array_equal(z['strain'], grid)
        saved_difference = float(np.max(np.abs(p - z['prediction'])))
        np.testing.assert_allclose(p, z['prediction'], rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(model.predict(X[te][::-1])[::-1], p, rtol=1e-12, atol=1e-12)
    single = np.concatenate([model.predict(x[None]) for x in X[te]])
    np.testing.assert_allclose(single, p, rtol=1e-12, atol=1e-12)
    errors = np.sqrt(np.mean((p - Y[te]) ** 2, axis=1))
    metrics = json.loads((folder / 'metrics.json').read_text())
    assert metrics['train_ids'] == split['train'] and metrics['test_ids'] == split['test']
    for key, value in [('test_mean_rmse', errors.mean()), ('test_median_rmse', np.median(errors)),
                       ('test_worst_rmse', errors.max())]:
        np.testing.assert_allclose(value, metrics[key], rtol=1e-12)
    for case, error in zip(ids[te], errors):
        np.testing.assert_allclose(error, metrics['per_case'][str(case)], rtol=1e-12)
    selection = json.loads((ROOT / 'runs/score/select_mlp_Svm.json').read_text())
    folds = json.loads((ROOT / 'runs/selection_Svm.json').read_text())['folds']
    assert set(map(int, folds)) == set(split['train'])
    cv = selection['per_case']['cv']
    loco = selection['per_case']['loco']
    assert {r['id'] for r in cv} == {r['id'] for r in loco} == set(split['train'])
    assert len(cv) == len(loco) == 36
    np.testing.assert_allclose(np.mean([r['rmse'] for r in cv]), selection['cv_mean_rmse'])
    np.testing.assert_allclose(np.mean(list(selection['loco_by_condition'].values())), selection['loco_mean_rmse'])
    return dict(checked_at=datetime.now(timezone.utc).isoformat(), status='passed', cases=73,
                source_rows=rows, raw_cache_max_abs_difference=max_cache_error,
                final_reload_max_abs_difference=saved_difference, train_cases=36, test_cases=37,
                parameters_per_network=parameters, training_scaler_samples=int(model.xs.n_samples_seen_),
                test_mean_curve_rmse=float(errors.mean()), test_worst_curve_rmse=float(errors.max()),
                test_worst_case=int(ids[te][errors.argmax()]),
                cv_mean_curve_rmse=selection['cv_mean_rmse'],
                condition_holdout_mean_rmse=selection['loco_mean_rmse'],
                condition_holdout_by_condition=selection['loco_by_condition'],
                versions={'numpy': np.__version__, 'sklearn': sklearn.__version__},
                limits=['Source stress units remain inferred.',
                        'Earlier full-data exploration means the test set is not fully blind.',
                        'This verifies artifacts and source processing, not independent training reproduction or physical validity.',
                        'No aerodynamic labels or validated porosity mapping exist.'])


if __name__ == '__main__':
    result = verify()
    path = ROOT / 'reports/model_verification_20261025.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
