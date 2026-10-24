"""Shared scoring so Claude and Codex can check each other's models with identical numbers.

Selection scores use the 36 TRAINING cases only:
  (a) cv   : 3-fold case CV, using the exact fold assignment saved in runs/selection_<target>.json
  (b) loco : leave-one-(T, rate)-condition-out, restricted to the training half

Selection rule, frozen 2026-10-24 14:27 IST before PCA-MLP results were seen:
  1. Primary score: (a) cv mean RMSE. Lowest wins.
  2. A candidate whose (a) is within 10 % of the lowest ties with it. Among tied candidates, one
     whose (b) loco mean is at least 20 % lower than the (a)-winner's is preferred.
  3. (a) and (b) are always reported separately; the best eligible neural network is reported
     separately from any non-NN reference (the course asks for a neural-network type).

Workflow:
  score.py --candidate NAME            selection scores (repeatable, training half only)
  score.py --select NAME               record the ONE agreed configuration (once per target)
  score.py --final                     fit it on all 36, score the 37 test cases ONCE, save everything
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import collections  # noqa: E402
import json  # noqa: E402
import warnings  # noqa: E402
from datetime import datetime, timezone  # noqa: E402

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import sklearn  # noqa: E402
from joblib import Parallel, delayed  # noqa: E402

from data import ROOT, STRAIN_GRID, build, condition_groups  # noqa: E402
from models import CANDIDATES  # noqa: E402
from split import make_split  # noqa: E402

OUT = ROOT / "runs" / "score"


def rmse(P, Y):
    return np.sqrt(((P - Y) ** 2).mean(1))


def _fit_predict(factory, X, Y, fit, val):
    """Return per-case RMSE and a count of warnings raised (recorded, not hidden)."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        e = rmse(factory().fit(X[fit], Y[fit]).predict(X[val]), Y[val])
    counts = collections.Counter(f"{w.category.__name__}: {str(w.message).splitlines()[0][:80]}" for w in caught)
    return e, dict(counts)


def _merge(dicts):
    total = collections.Counter()
    for d in dicts:
        total.update(d)
    return dict(total.most_common())


def selection_scores(name, target):
    factory = CANDIDATES[name]
    ids, X, Y, _ = build(target=target)
    tr = np.isin(ids, make_split()["train"])
    ids, X, Y = ids[tr], X[tr], Y[tr]  # from here on, only training cases exist
    saved = json.loads((ROOT / "runs" / f"selection_{target}.json").read_text())["folds"]
    folds = np.array([saved[str(i)] for i in ids])
    groups = condition_groups(X)
    jobs = [("cv", k, folds != k, folds == k) for k in range(3)]
    jobs += [("loco", g, groups != g, groups == g) for g in np.unique(groups)]
    res = Parallel(n_jobs=min(8, os.cpu_count() or 1))(
        delayed(_fit_predict)(factory, X, Y, fit, val) for _, _, fit, val in jobs)
    per_case = {"cv": [], "loco": []}
    for (kind, label, _, val), (e, _) in zip(jobs, res):
        for i, v in zip(ids[val], e):
            per_case[kind].append({"id": int(i), "fold" if kind == "cv" else "condition": str(label),
                                   "condition_of_case": str(groups[ids == i][0]), "rmse": float(v)})
    cv = np.array([r["rmse"] for r in per_case["cv"]])
    loco = {str(g): float(np.mean([r["rmse"] for r in per_case["loco"] if r["condition"] == str(g)]))
            for g in np.unique(groups)}
    return {"candidate": name, "target": target, "cv_mean_rmse": float(cv.mean()),
            "cv_median_rmse": float(np.median(cv)), "cv_worst_rmse": float(cv.max()),
            "cv_worst_case": per_case["cv"][int(cv.argmax())]["id"],
            "loco_mean_rmse": float(np.mean(list(loco.values()))), "loco_by_condition": loco,
            "per_case": per_case, "warnings": _merge(w for _, w in res)}


def select(name, target):
    path = OUT / f"SELECTED_{target}.json"
    if path.exists():
        raise SystemExit(f"{path.name} already records {json.loads(path.read_text())['candidate']}; "
                         "change it only with agreement in the room.")
    scores = OUT / f"select_{name}_{target}.json"
    if not scores.exists():
        raise SystemExit(f"score it first: src/score.py --candidate {name} --target {target}")
    path.write_text(json.dumps({"candidate": name, "target": target,
                                "selection_scores": json.loads(scores.read_text())["cv_mean_rmse"],
                                "selected_at": datetime.now(timezone.utc).isoformat()}, indent=1))
    return path


def final_score(target):
    sel = OUT / f"SELECTED_{target}.json"
    if not sel.exists():
        raise SystemExit("no agreed configuration: run src/score.py --select NAME first")
    name = json.loads(sel.read_text())["candidate"]
    out = OUT / f"final_{target}"
    if out.exists():
        raise SystemExit(f"{out.relative_to(ROOT)} exists: the test set is scored once. "
                         "Delete it only with agreement in the room.")
    ids, X, Y, _ = build(target=target)
    split = make_split()
    tr, te = np.isin(ids, split["train"]), np.isin(ids, split["test"])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model = CANDIDATES[name]().fit(X[tr], Y[tr])
        P = model.predict(X[te])
    e = rmse(P, Y[te])
    out.mkdir(parents=True)
    joblib.dump(model, out / "model.joblib")
    assert np.allclose(joblib.load(out / "model.joblib").predict(X[te]), P), "reload mismatch"
    np.savez_compressed(out / "test_predictions.npz", test_ids=ids[te], truth=Y[te], prediction=P, strain=STRAIN_GRID)
    result = {"candidate": name, "target": target, "train_ids": split["train"], "test_ids": split["test"],
              "test_mean_rmse": float(e.mean()), "test_median_rmse": float(np.median(e)),
              "test_worst_rmse": float(e.max()), "test_worst_case": int(ids[te][e.argmax()]),
              "per_case": {int(i): float(v) for i, v in zip(ids[te], e)},
              "warnings": _merge([collections.Counter(f"{w.category.__name__}: {str(w.message).splitlines()[0][:80]}"
                                                      for w in caught)]),
              "versions": {"numpy": np.__version__, "sklearn": sklearn.__version__},
              "scored_at": datetime.now(timezone.utc).isoformat()}
    (out / "metrics.json").write_text(json.dumps(result, indent=1))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate")
    ap.add_argument("--select")
    ap.add_argument("--target", default="Svm", choices=["SCAU11", "Svm"])
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.final:
        r = final_score(a.target)
        print(f"FINAL {r['candidate']} {a.target}: test mean {r['test_mean_rmse']:.4f}  "
              f"median {r['test_median_rmse']:.4f}  worst {r['test_worst_rmse']:.4f} (case {r['test_worst_case']})")
    elif a.select:
        print("recorded", select(a.select, a.target).relative_to(ROOT))
    elif a.candidate:
        r = selection_scores(a.candidate, a.target)
        (OUT / f"select_{a.candidate}_{a.target}.json").write_text(json.dumps(r, indent=1))
        nwarn = sum(r["warnings"].values())
        print(f"{a.candidate:14s} {a.target}: cv mean {r['cv_mean_rmse']:.4f} median {r['cv_median_rmse']:.4f} "
              f"worst {r['cv_worst_rmse']:.2f} (case {r['cv_worst_case']}) | train-half loco mean "
              f"{r['loco_mean_rmse']:.2f} | warnings {nwarn}")
    else:
        print("\n".join(CANDIDATES))


if __name__ == "__main__":
    main()
