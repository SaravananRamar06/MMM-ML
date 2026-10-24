"""Figure of the FINAL model's test-set predictions (best, median and worst test curve).

Usage:  .venv/bin/python src/plot_final.py   ->  figures/final_test_curves.png
"""
import json

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from data import ROOT, read_matrix  # noqa: E402

run = ROOT / "runs" / "score" / "final_Svm"
z = np.load(run / "test_predictions.npz")
metrics = json.loads((run / "metrics.json").read_text())
ids, truth, pred, strain = z["test_ids"], z["truth"], z["prediction"], z["strain"]
err = np.sqrt(((pred - truth) ** 2).mean(1))
order = np.argsort(err)
matrix = read_matrix()

fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
for ax, k, label in zip(axes, [order[0], order[len(order) // 2], order[-1]], ["best", "median", "worst"]):
    r = matrix[int(ids[k])]
    ax.plot(strain, truth[k], color="0.55", lw=4, alpha=0.6, label="simulation")
    ax.plot(strain, pred[k], "C1", lw=1.6, label="final query MLP")
    ax.set_title(f"{label}: case {ids[k]}, {float(r['temperature']):g} °C, {float(r['strain_rate']):g}/s\n"
                 f"RMSE {err[k]:.3f} MPa", fontsize=10)
    ax.set_xlabel("axial strain E11")
axes[0].set_ylabel("von Mises stress Svm (MPa)")
axes[0].legend()
fig.suptitle(f"Final model on the 37 held-out test cases: mean RMSE {metrics['test_mean_rmse']:.3f} MPa", fontsize=11)
fig.tight_layout()
out = ROOT / "figures" / "final_test_curves.png"
fig.savefig(out, dpi=130)
print("saved", out.relative_to(ROOT))
