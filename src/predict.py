"""Predict a stress–strain curve for a material condition, using the saved selected models.

Example:
  .venv/bin/python src/predict.py --temperature 100 --rate 1e-4 --density 2619 --G 24541
  .venv/bin/python src/predict.py --temperature 150 --rate 3e-4 --density 2700 --G 25300 --plot curve.png

The MLP is the final scored model (runs/score/final_Svm/model.joblib); the GP reference is the one
chosen by training-side cross-validation (src/select_settings.py). Both are fitted on the 36 training cases. They were trained only on 30/100/200 C, rates 1e-5..1e-3,
density 2488..2700 and G 23314..25300; anything outside that is extrapolation.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse  # noqa: E402
import sys  # noqa: E402

import joblib  # noqa: E402
import numpy as np  # noqa: E402

from data import ROOT, STRAIN_GRID  # noqa: E402

# Training ranges seen by the models (all 73 cases share these levels).
RANGES = {"temperature": (30, 200), "log10_rate": (-5, -3), "density": (2488.05, 2700),
          "G": (23313.95, 25300)}
MODEL_FILES = {"mlp": "query_MLP.joblib", "gp": "PCA_plus_GP.joblib"}


def model_path(name, target):
    """The final scored model when one exists for this target (src/score.py --final), else the CV-selected one."""
    final = ROOT / "runs" / "score" / f"final_{target}" / "model.joblib"
    if name == "mlp" and final.exists():
        return final
    return ROOT / "runs" / f"selected_{target}" / MODEL_FILES[name]


def warnings_for(t, log_rate, rho, g):
    out = []
    for name, v in [("temperature", t), ("log10_rate", log_rate), ("density", rho), ("G", g)]:
        lo, hi = RANGES[name]
        if not lo - 1e-9 <= v <= hi + 1e-9:
            out.append(f"{name}={v:g} is outside the training range [{lo:g}, {hi:g}]: extrapolation, do not trust.")
    if 100 < t <= 200 and log_rate < -4:
        out.append("Hot and slow (200 C / 1e-5 region) has only one training-set case (case 60, an "
                   "irregular collapse); leave-one-condition-out error there is about 23.5 (inferred stress units).")
    elif 100 < t <= 200:
        out.append("Above 100 C, leave-one-condition-out errors at 200 C were about 8-9 (inferred stress units).")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--temperature", type=float, required=True, help="matrix temperature, presumably °C")
    ap.add_argument("--rate", type=float, required=True, help="strain rate, presumably 1/s")
    ap.add_argument("--density", type=float, default=2700.0)
    ap.add_argument("--G", type=float, default=25300.0, help="shear modulus, presumably MPa")
    ap.add_argument("--target", default="Svm", choices=["SCAU11", "Svm"])
    ap.add_argument("--model", default="both", choices=["mlp", "gp", "both"])
    ap.add_argument("--plot", help="save a PNG of the predicted curve(s) here")
    ap.add_argument("--csv", help="save strain and predicted stress as CSV here")
    a = ap.parse_args(argv)
    if a.rate <= 0:
        ap.error("--rate must be positive")

    x = np.array([[a.temperature, np.log10(a.rate), a.density, a.G]])
    names = ["mlp", "gp"] if a.model == "both" else [a.model]
    preds = {}
    for n in names:
        path = model_path(n, a.target)
        if not path.exists():
            sys.exit(f"missing {path}; run: .venv/bin/python src/select_settings.py --target {a.target}")
        preds[n] = joblib.load(path).predict(x)[0]

    for w in warnings_for(a.temperature, np.log10(a.rate), a.density, a.G):
        print("WARNING:", w)
    print(f"{a.target} stress prediction (source units, presumably MPa) at "
          f"T={a.temperature:g}, rate={a.rate:g}, density={a.density:g}, G={a.G:g}")
    print("  strain   " + "  ".join(f"{n:>8s}" for n in preds))
    for k in range(0, len(STRAIN_GRID), 17):
        print(f"  {STRAIN_GRID[k]:.4f}   " + "  ".join(f"{p[k]:8.2f}" for p in preds.values()))
    if a.csv:
        cols = np.column_stack([STRAIN_GRID] + list(preds.values()))
        np.savetxt(a.csv, cols, delimiter=",", header="strain," + ",".join(preds), comments="", fmt="%.6g")
        print("saved", a.csv)
    if a.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 4))
        labels = {"mlp": "query MLP", "gp": "PCA + GP"}
        for n, p in preds.items():
            ax.plot(STRAIN_GRID, p, "C1" if n == "mlp" else "C2", label=labels[n])
        ax.set_xlabel("axial strain E11")
        ax.set_ylabel(f"{a.target} (MPa, provisional)")
        ax.set_title(f"T={a.temperature:g}, rate={a.rate:g}, ρ={a.density:g}, G={a.G:g}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(a.plot, dpi=130)
        print("saved", a.plot)
    return preds


if __name__ == "__main__":
    main()
