"""Recheck the delivered model without replacing any fitted artifact.

Run: .venv/bin/python reports/retest_model.py
Evidence is written to a fresh timestamped directory under reports/retests/.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'

from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import warnings

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'reports')]
import joblib
import numpy as np
from models import QueryMLP
from query_runtime import QueryRuntime
from verify_final_model import verify


def main():
    started = datetime.now(timezone.utc)
    out = ROOT / 'reports/retests' / started.strftime('%Y%m%dT%H%M%SZ')
    out.mkdir(parents=True)
    folder = ROOT / 'runs/score/final_Svm'
    protected = [folder / n for n in ('model.joblib', 'model_numpy.npz', 'test_predictions.npz', 'metrics.json')]
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    audit = verify()
    with np.load(ROOT / 'data/curves_Svm.npz', allow_pickle=False) as z:
        ids, X, Y, grid = [z[k].copy() for k in ('ids', 'X', 'Y', 'strain')]
    split = json.loads((ROOT / 'data/split.json').read_text())
    train, test = np.isin(ids, split['train']), np.isin(ids, split['test'])
    saved = joblib.load(folder / 'model.joblib')
    prediction = saved.predict(X[test])
    residual = prediction - Y[test]
    rmse = np.sqrt(np.mean(residual ** 2, axis=1))
    mae = np.mean(np.abs(residual), axis=1)
    runtime_difference = float(np.max(np.abs(QueryRuntime.load(folder / 'model_numpy.npz').predict(X) - saved.predict(X))))
    np.testing.assert_allclose(runtime_difference, 0, atol=1e-10)
    print('Source audit passed. Refitting the frozen configuration on the original 36 training cases...', flush=True)
    tick = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        refit = QueryMLP(hidden=saved.hidden, alpha=saved.alpha, n_init=saved.n_init, seed=saved.seed).fit(X[train], Y[train])
    seconds = time.perf_counter() - tick
    weight_difference = max(float(np.max(np.abs(a - b))) for first, second in zip(saved.nets, refit.nets)
                            for a, b in zip(first.coefs_ + first.intercepts_, second.coefs_ + second.intercepts_))
    refit_difference = float(np.max(np.abs(refit.predict(X) - saved.predict(X))))
    np.testing.assert_allclose(refit_difference, 0, atol=1e-9)
    suites = {}
    for name, pattern in [('unit', 'test_*.py'), ('live_studio', 'live_model_app_check.py')]:
        command = [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', pattern, '-v']
        run = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out / (name + '.txt')).write_text(run.stdout)
        suites[name] = {'command': command, 'returncode': run.returncode, 'log': name + '.txt'}
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    assert before == after, 'A delivered artifact changed during verification.'
    with (out / 'per_case.csv').open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['simulation_id', 'rmse_source_stress_units', 'mae_source_stress_units', 'max_abs_error_source_stress_units'])
        for case, r, a, e in zip(ids[test], rmse, mae, np.max(np.abs(residual), axis=1)):
            writer.writerow([int(case), float(r), float(a), float(e)])
    result = {'started_at': started.isoformat(), 'completed_at': datetime.now(timezone.utc).isoformat(),
              'source_audit': audit,
              'fresh_test_metrics': {'cases': int(test.sum()), 'points_per_curve': len(grid),
                  'mean_curve_rmse': float(rmse.mean()), 'median_curve_rmse': float(np.median(rmse)),
                  'worst_curve_rmse': float(rmse.max()), 'worst_case': int(ids[test][rmse.argmax()]),
                  'mean_curve_mae': float(mae.mean()), 'pooled_rmse': float(np.sqrt(np.mean(residual ** 2))),
                  'max_abs_point_error': float(np.max(np.abs(residual)))},
              'refit': {'seconds': seconds, 'seeds': [n.random_state for n in refit.nets],
                  'max_abs_weight_difference': weight_difference, 'max_abs_prediction_difference': refit_difference,
                  'warnings': [str(w.message) for w in caught]},
              'numpy_runtime_max_abs_difference': runtime_difference,
              'test_suites': suites, 'delivered_artifacts_unchanged': before == after, 'artifact_sha256': before,
              'limits': ['Same dataset and previously explored holdout; no new independent test data.',
                         'Frozen settings refit in the same local environment; no model selection performed.',
                         'Condition-holdout scores are historical diagnostics, not rerun in this audit.',
                         'Physical units, porosity mapping, ANSYS coupling and lift prediction remain unvalidated.']}
    result['passed'] = all(s['returncode'] == 0 for s in suites.values())
    (out / 'results.json').write_text(json.dumps(result, indent=2) + '\n')

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    cases = [42, int(ids[test][rmse.argmax()])]
    fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharex=True, layout='constrained', gridspec_kw={'height_ratios': [3, 1]})
    for col, case in enumerate(cases):
        index = int(np.flatnonzero(ids[test] == case)[0])
        axes[0, col].plot(grid, Y[test][index], label='Supplied simulation', lw=3, color='#536878')
        axes[0, col].plot(grid, prediction[index], label='Saved MLP prediction', ls='--', color='#b45d38')
        axes[0, col].set_title(f'Case {case}: RMSE {rmse[index]:.6f}')
        axes[0, col].set_ylabel('Svm (source stress units)')
        axes[0, col].legend(fontsize=8)
        axes[1, col].plot(grid, residual[index], color='#b45d38')
        axes[1, col].axhline(0, color='#536878', lw=.7)
        axes[1, col].set_xlabel('Axial strain E11 (dimensionless)')
        axes[1, col].set_ylabel('Prediction − source\n(source stress units)', fontsize=8)
    fig.suptitle('Fresh evaluation on the existing 37-case split\nEarlier holdout exploration disclosed; stress units unconfirmed', fontsize=12)
    fig.savefig(out / 'test_curves.png', dpi=150)
    fig.savefig(out / 'test_curves.svg')
    print(json.dumps(result, indent=2))
    print('Evidence:', out)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
