"""Train and evaluate all models under two protocols, then save everything to runs/.

1. random  : professor's seed-42 36/37 case split (data/split.json).
2. loco    : leave-one-condition-out. Hold out every case of one (T, rate) condition,
             train on the rest. This tests prediction for a condition never seen in
             training, which the random split almost never does.

Usage:  .venv/bin/python src/evaluate.py [--target SCAU11|Svm]
"""
import os

# Tiny matrices: multi-threaded BLAS only adds contention (a full run hung for 20+ min).
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
from datetime import datetime  # noqa: E402
from functools import partial  # noqa: E402

import joblib  # noqa: E402
import matplotlib  # noqa: E402
import numpy as np  # noqa: E402
import sklearn  # noqa: E402

print = partial(print, flush=True)  # progress shows up live in logs

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from data import ROOT, STRAIN_GRID, build, condition_groups  # noqa: E402
from models import MODELS, PcaGP, QueryMLP  # noqa: E402
from split import make_split  # noqa: E402


def per_case(P, Y):
    return np.sqrt(((P - Y) ** 2).mean(1)), np.abs(P - Y).mean(1)


def summarise(rmse):
    return {"mean_rmse": float(rmse.mean()), "median_rmse": float(np.median(rmse)),
            "worst_rmse": float(rmse.max())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="SCAU11", choices=["SCAU11", "Svm"])
    target = ap.parse_args().target
    ids, X, Y, _ = build(target=target)
    groups = condition_groups(X)
    split = make_split()
    tr, te = np.isin(ids, split["train"]), np.isin(ids, split["test"])
    run = ROOT / "runs" / (datetime.now().strftime("%Y%m%d-%H%M%S") + "_" + target)
    (run / "models").mkdir(parents=True)
    fig_dir = ROOT / "figures" / target
    fig_dir.mkdir(parents=True, exist_ok=True)
    metrics = {"random_split": {}, "loco": {}, "ablation": {}}
    rows = []

    # ---- 1. professor's random split
    preds = {}
    for name, cls in MODELS.items():
        model = cls().fit(X[tr], Y[tr])
        P = model.predict(X[te])
        preds[name] = P
        rmse, mae = per_case(P, Y[te])
        metrics["random_split"][name] = summarise(rmse) | {"mean_mae": float(mae.mean())}
        for i, g, r, m in zip(ids[te], groups[te], rmse, mae):
            rows.append(f"random,{name},{i},{g},{r:.4f},{m:.4f}")
        joblib.dump(model, run / "models" / f"{name.replace(' ', '_').replace('+', 'plus')}.joblib")
        print(f"[random] {name:16s} mean RMSE {rmse.mean():6.3f}  worst {rmse.max():6.3f} MPa")

    # Ablation: does density carry any information? (drop column 2)
    rmse, _ = per_case(QueryMLP(features=[0, 1, 3]).fit(X[tr], Y[tr]).predict(X[te]), Y[te])
    metrics["ablation"]["query MLP without density"] = summarise(rmse)
    print(f"[random] query MLP, no density mean RMSE {rmse.mean():6.3f}")

    # Reload check: saved model must reproduce its predictions in this process.
    reloaded = joblib.load(run / "models" / "query_MLP.joblib")
    assert np.allclose(reloaded.predict(X[te]), preds["query MLP"]), "reload mismatch"

    # ---- 2. leave one (T, rate) condition out
    for name, cls in MODELS.items():
        metrics["loco"][name] = {}
        for g in np.unique(groups):
            hold = groups == g
            P = cls().fit(X[~hold], Y[~hold]).predict(X[hold])
            rmse, mae = per_case(P, Y[hold])
            metrics["loco"][name][g] = float(rmse.mean())
            for i, r, m in zip(ids[hold], rmse, mae):
                rows.append(f"loco,{name},{i},{g},{r:.4f},{m:.4f}")
        v = metrics["loco"][name]
        print(f"[loco]   {name:16s} " + " ".join(f"{k}:{x:.1f}" for k, x in v.items()))

    # ---- save
    np.savez_compressed(run / "random_split_predictions.npz", test_ids=ids[te], truth=Y[te],
                        strain=STRAIN_GRID, **{k.replace(" ", "_"): v for k, v in preds.items()})
    (run / "metrics.json").write_text(json.dumps(metrics, indent=1))
    (run / "per_case.csv").write_text("protocol,model,id,condition,rmse,mae\n" + "\n".join(rows) + "\n")
    (run / "config.json").write_text(json.dumps({
        "target": target, "split": split, "strain_grid": [float(STRAIN_GRID[0]), float(STRAIN_GRID[-1]), len(STRAIN_GRID)],
        "query_mlp": {"hidden": [16, 16], "activation": "tanh", "alpha": 1e-4, "n_init": 5},
        "pca_gp": {"n_components": 4, "kernel": "Constant*RBF(ARD)+White"},
        "versions": {"python": platform.python_version(), "numpy": np.__version__,
                     "sklearn": sklearn.__version__}, "argv": sys.argv}, indent=1))

    plot_random(ids[te], Y[te], preds, fig_dir)
    plot_loco(metrics["loco"], fig_dir)
    plot_case60(ids, X, Y, groups, fig_dir)
    print(f"saved run to {run.relative_to(ROOT)} and figures to {fig_dir.relative_to(ROOT)}")


def plot_random(test_ids, Yte, preds, fig_dir):
    rmse, _ = per_case(preds["query MLP"], Yte)
    pick = [int(np.argmin(rmse)), int(np.argsort(rmse)[len(rmse) // 2]), int(np.argmax(rmse))]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    for ax, k, label in zip(axes, pick, ["best", "median", "worst"]):
        ax.plot(STRAIN_GRID, Yte[k], "k", lw=3, alpha=0.35, label="simulation")
        for name, P in preds.items():
            ax.plot(STRAIN_GRID, P[k], lw=1.2, label=name)
        ax.set_title(f"test case {test_ids[k]} ({label} for query MLP)")
        ax.set_xlabel("axial strain E11")
    axes[0].set_ylabel("axial stress (MPa)")
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(fig_dir / "random_split_curves.png", dpi=130)
    plt.close(fig)


def plot_loco(loco, fig_dir):
    conds = list(next(iter(loco.values())).keys())
    w = 0.27
    fig, ax = plt.subplots(figsize=(11, 4))
    for j, (name, v) in enumerate(loco.items()):
        ax.bar(np.arange(len(conds)) + (j - 1) * w, [v[c] for c in conds], w, label=name)
    ax.set_xticks(np.arange(len(conds)), conds)
    ax.set_ylabel("mean per-case RMSE (MPa)")
    ax.set_title("Held-out condition never seen in training")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_dir / "loco_rmse.png", dpi=130)
    plt.close(fig)


def plot_case60(ids, X, Y, groups, fig_dir):
    """Case 60 is the only 200 C / 1e-5 case: show both models extrapolating with GP error bars."""
    hold = ids == 60
    gp = PcaGP().fit(X[~hold], Y[~hold])
    mean, std = gp.predict(X[hold], return_std=True)
    mlp = QueryMLP().fit(X[~hold], Y[~hold]).predict(X[hold])
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(STRAIN_GRID, Y[hold][0], "k", lw=3, alpha=0.35, label="simulation (case 60)")
    # Same colours as the other figures: C1 = query MLP, C2 = PCA + GP.
    ax.plot(STRAIN_GRID, mlp[0], "C1", label="query MLP")
    ax.plot(STRAIN_GRID, mean[0], "C2", label="PCA + GP")
    ax.fill_between(STRAIN_GRID, mean[0] - 2 * std[0], mean[0] + 2 * std[0], color="C2", alpha=0.2,
                    label="GP ±2σ")
    ax.set_xlabel("axial strain E11")
    ax.set_ylabel("axial stress (MPa)")
    ax.set_title("Extrapolation to unseen 200 °C / 1e-5")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_dir / "case60_extrapolation.png", dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
