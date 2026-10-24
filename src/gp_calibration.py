"""Does the PCA + GP's ±2σ band actually contain the truth on conditions it has never seen?

For each leave-one-(T, rate)-condition-out fold, report the fraction of held-out curve
points inside mean ± 2σ (≈95 % if the uncertainty were well calibrated), and the mean σ.
Usage:  .venv/bin/python src/gp_calibration.py [--target SCAU11|Svm]
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse  # noqa: E402
import json  # noqa: E402

import numpy as np  # noqa: E402

from data import ROOT, build, condition_groups  # noqa: E402
from models import PcaGP  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--target", default="SCAU11", choices=["SCAU11", "Svm"])
target = ap.parse_args().target
ids, X, Y, _ = build(target=target)
groups = condition_groups(X)
out = {}
for g in np.unique(groups):
    hold = groups == g
    mean, std = PcaGP().fit(X[~hold], Y[~hold]).predict(X[hold], return_std=True)
    err = np.abs(mean - Y[hold])
    # σ only covers coefficient uncertainty; PCA truncation error is ignored (it is <1 MPa).
    out[g] = {"coverage_2sigma": float((err <= 2 * std).mean()),
              "mean_sigma": float(std.mean()), "mean_abs_err": float(err.mean())}
    print(f"{g:10s} inside ±2σ: {out[g]['coverage_2sigma']:5.1%}   mean σ {std.mean():6.2f}   "
          f"mean |err| {err.mean():6.2f} MPa")
(ROOT / "runs" / f"gp_calibration_{target}.json").write_text(json.dumps(out, indent=1))
