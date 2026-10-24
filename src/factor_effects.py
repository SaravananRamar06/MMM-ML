"""How much does each input move the curve? Compare cases that differ in ONE input by one level.

For every pair of cases identical except for one input (one level apart), take the largest
stress difference along the curve; report the mean and maximum per input.
Usage:  .venv/bin/python src/factor_effects.py   ->  runs/factor_effects.json
"""
import json

import numpy as np

from data import FEATURES, ROOT, build

out = {}
for target in ("SCAU11", "Svm"):
    ids, X, Y, _ = build(target=target)
    out[target] = {}
    for col, name in enumerate(FEATURES):
        levels = np.unique(X[:, col])
        diffs = []
        for a in range(len(X)):
            for b in range(len(X)):
                others = np.delete(np.arange(X.shape[1]), col)
                ia, ib = np.searchsorted(levels, X[a, col]), np.searchsorted(levels, X[b, col])
                if np.all(X[a, others] == X[b, others]) and ib - ia == 1:
                    diffs.append(np.abs(Y[a] - Y[b]).max())
        out[target][name] = {"pairs": len(diffs), "mean_max_abs_diff": float(np.mean(diffs)),
                             "largest": float(np.max(diffs))}
        print(f"{target:6s} {name:18s} pairs {len(diffs):3d}  mean {np.mean(diffs):6.2f}  max {np.max(diffs):6.2f} MPa")
(ROOT / "runs" / "factor_effects.json").write_text(json.dumps(out, indent=1))
