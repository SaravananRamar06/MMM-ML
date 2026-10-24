"""Live demo of the final model on held-out test cases (never used for fitting).

Picks 4 test cases at random (seed from the command line, default 7), predicts their full curves
with the saved final model, compares with the simulations, and saves figures/demo.png.
Point values at strain 0.05 are linearly interpolated from the common 120-point grid.
Test cases were explored earlier; this is not untouched-holdout or physical validation.
Usage:  .venv/bin/python src/demo.py [seed]
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")

import joblib  # noqa: E402
import matplotlib  # noqa: E402
import numpy as np  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from data import ROOT, STRAIN_GRID, build, read_matrix  # noqa: E402
from split import make_split  # noqa: E402

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
model = joblib.load(ROOT / "runs" / "score" / "final_Svm" / "model.joblib")
ids, X, Y, _ = build(target="Svm")
test = make_split()["test"]
pick = sorted(np.random.default_rng(seed).choice(test, 4, replace=False).tolist())
matrix = read_matrix()

fig, axes = plt.subplots(1, 4, figsize=(16, 4), sharey=True)
print(f"{'case':>5} {'T °C':>6} {'rate /s':>8} {'density':>8} {'G':>8} | {'RMSE MPa':>8} {'stress@0.05 sim':>15} {'pred':>7}")
for ax, cid in zip(axes, pick):
    i = list(ids).index(cid)
    pred = model.predict(X[i:i + 1])[0]
    rmse = float(np.sqrt(((pred - Y[i]) ** 2).mean()))
    r = matrix[cid]
    sim_at_005 = float(np.interp(0.05, STRAIN_GRID, Y[i]))
    pred_at_005 = float(np.interp(0.05, STRAIN_GRID, pred))
    print(f"{cid:>5} {float(r['temperature']):>6.0f} {float(r['strain_rate']):>8.0e} {float(r['density']):>8.1f} "
          f"{float(r['shear_modulus']):>8.0f} | {rmse:>8.3f} {sim_at_005:>15.2f} {pred_at_005:>7.2f}")
    ax.plot(STRAIN_GRID, Y[i], color="0.55", lw=4, alpha=.6, label="simulation (held out)")
    ax.plot(STRAIN_GRID, pred, "C1", lw=1.6, label="final model")
    ax.set_title(f"case {cid}: {float(r['temperature']):g} °C, {float(r['strain_rate']):g}/s\nRMSE {rmse:.3f} MPa", fontsize=10)
    ax.set_xlabel("axial strain")
axes[0].set_ylabel("von Mises stress (MPa, inferred)")
axes[0].legend(fontsize=9)
fig.suptitle(f"Demo: final model on 4 randomly chosen held-out test cases (seed {seed})", fontsize=11)
fig.tight_layout()
fig.savefig(ROOT / "figures" / "demo.png", dpi=120)
print("saved figures/demo.png")
