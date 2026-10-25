"""Refit the frozen final configuration separately; never replace delivered artifacts.

Run with .venv/bin/python reports/reproduce_final_training.py. No architecture,
hyperparameter, split, or seed selection is performed using test predictions.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
import warnings

for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import joblib
import numpy as np
from models import QueryMLP


if __name__ == '__main__':
    with np.load(ROOT / 'data/curves_Svm.npz', allow_pickle=False) as z:
        ids, X, Y = (z[k].copy() for k in ('ids', 'X', 'Y'))
    split = json.loads((ROOT / 'data/split.json').read_text())
    train = np.isin(ids, split['train'])
    original = joblib.load(ROOT / 'runs/score/final_Svm/model.joblib')
    print('Refitting frozen 5 x (5-16-16-1) tanh ensemble on 36 training cases...', flush=True)
    start = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        fitted = QueryMLP(hidden=original.hidden, alpha=original.alpha,
                          n_init=original.n_init, seed=original.seed).fit(X[train], Y[train])
    elapsed = time.perf_counter() - start
    weight_difference = max(float(np.max(np.abs(a - b)))
                            for first, second in zip(original.nets, fitted.nets)
                            for a, b in zip(first.coefs_ + first.intercepts_, second.coefs_ + second.intercepts_))
    prediction_difference = float(np.max(np.abs(original.predict(X) - fitted.predict(X))))
    result = dict(checked_at=datetime.now(timezone.utc).isoformat(), elapsed_seconds=elapsed,
                  train_cases=int(train.sum()), original_seed=int(original.seed),
                  seeds=[int(n.random_state) for n in fitted.nets],
                  max_abs_weight_difference=weight_difference,
                  max_abs_prediction_difference_all_cases=prediction_difference,
                  iterations=[int(n.n_iter_) for n in fitted.nets],
                  losses=[float(n.loss_) for n in fitted.nets],
                  warnings=[f'{type(w.message).__name__}: {w.message}' for w in caught],
                  passed=bool(prediction_difference < 1e-9),
                  limits=['Same local code, numerical libraries and hardware; not cross-platform reproducibility.',
                          'No new model or configuration selection; original artifacts unchanged.',
                          'Does not establish physical correctness or blind evaluation.'])
    (ROOT / 'reports/final_training_reproduction_20261025.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)
    if not result['passed']:
        raise SystemExit('Reproduction differs; inspect evidence before claiming reproducibility.')
