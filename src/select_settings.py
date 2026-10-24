"""Choose model settings using ONLY the 36 training cases, then test once on the 37 test cases.

Inside the training half, cases are split into 3 folds (whole cases, never rows). Each
candidate setting is trained on 2 folds and scored on the third; the setting with the
lowest average per-case RMSE wins. Only then is the winner refitted on all 36 training
cases and scored on the held-out 37. The test half plays no part in choosing.

Usage:  .venv/bin/python src/select_settings.py [--target SCAU11|Svm]
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
from functools import partial  # noqa: E402

import joblib  # noqa: E402
import numpy as np  # noqa: E402
from joblib import Parallel, delayed  # noqa: E402

from data import ROOT, build  # noqa: E402
from models import PcaGP, QueryMLP  # noqa: E402
from split import make_split  # noqa: E402

print = partial(print, flush=True)
FOLD_SEED = 42
CANDIDATES = (
    [("query MLP", {"hidden": h, "alpha": a})
     for h, a in itertools.product([(8, 8), (16, 16), (32, 32)], [1e-5, 1e-4, 1e-3])]
    + [("PCA + GP", {"n_components": k}) for k in (3, 4, 5, 6)]
)


def make(name, params):
    if name == "query MLP":
        return QueryMLP(hidden=tuple(params["hidden"]), alpha=params["alpha"])
    return PcaGP(**params)


def rmse(P, Y):
    return np.sqrt(((P - Y) ** 2).mean(1))


def cv_score(name, params, X, Y, folds):
    per_case = []
    for k in range(folds.max() + 1):
        fit, val = folds != k, folds == k
        per_case.extend(rmse(make(name, params).fit(X[fit], Y[fit]).predict(X[val]), Y[val]))
    return float(np.mean(per_case))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="SCAU11", choices=["SCAU11", "Svm"])
    target = ap.parse_args().target
    ids, X, Y, _ = build(target=target)
    split = make_split()
    tr, te = np.isin(ids, split["train"]), np.isin(ids, split["test"])
    Xtr, Ytr = X[tr], Y[tr]
    # 3 case-level folds inside the training half: 12 cases each.
    folds = np.random.default_rng(FOLD_SEED).permutation(np.arange(len(Xtr)) % 3)

    scores = Parallel(n_jobs=min(8, os.cpu_count() or 1))(
        delayed(cv_score)(n, p, Xtr, Ytr, folds) for n, p in CANDIDATES)
    history = [{"model": n, "params": p, "cv_mean_rmse": s} for (n, p), s in zip(CANDIDATES, scores)]
    for h in sorted(history, key=lambda h: h["cv_mean_rmse"]):
        print(f"  cv {h['cv_mean_rmse']:7.3f} MPa  {h['model']:10s} {h['params']}")

    result = {"target": target, "fold_seed": FOLD_SEED, "train_ids": split["train"],
              "folds": {int(i): int(f) for i, f in zip(ids[tr], folds)}, "history": history, "chosen": {}}
    out_dir = ROOT / "runs" / f"selected_{target}"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("query MLP", "PCA + GP"):
        best = min((h for h in history if h["model"] == name), key=lambda h: h["cv_mean_rmse"])
        model = make(name, best["params"]).fit(Xtr, Ytr)
        P = model.predict(X[te])
        e = rmse(P, Y[te])
        # Save the exact fitted model that produced these test numbers, and verify reload.
        path = out_dir / (name.replace(" ", "_").replace("+", "plus") + ".joblib")
        joblib.dump(model, path)
        assert np.allclose(joblib.load(path).predict(X[te]), P), "reload mismatch"
        np.save(out_dir / (path.stem + "_test_predictions.npy"), P)
        result["chosen"][name] = {**best, "artifact": str(path.relative_to(ROOT)), "test_mean_rmse": float(e.mean()),
                                  "test_median_rmse": float(np.median(e)), "test_worst_rmse": float(e.max())}
        print(f"chosen {name:10s} {best['params']}  -> test mean {e.mean():.3f}  worst {e.max():.3f} MPa")
    np.save(out_dir / "test_ids.npy", ids[te])
    (ROOT / "runs" / f"selection_{target}.json").write_text(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
