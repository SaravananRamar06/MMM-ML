"""Load the professor's simulation histories and put every curve on one strain grid.

Each STR_STR.OUT is one simulation case (one material condition). Cases have
1,000 / 10,000 / 100,000 rows depending on strain rate, so we resample every
curve onto the same strain grid. That way each case counts equally in training
instead of slow-rate cases dominating by row count.
"""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "TEAM_8_extracted_results_set_1"
DATA = ROOT / "data"

# Common support of all 73 curves is E11 in [1e-4, 0.1]; stay just inside it.
STRAIN_GRID = np.linspace(0.0002, 0.0999, 120)

# Column order in STR_STR.OUT
COLS = ["TIME", "Evm", "Svm", "E11", "E22", "E33", "E23", "E13", "E12",
        "SCAU11", "SCAU22", "SCAU33", "SCAU23", "SCAU13", "SCAU12", "TEMP"]

# Model inputs, in this fixed order everywhere.
FEATURES = ["temperature", "log10_strain_rate", "density", "shear_modulus"]


def read_matrix():
    with open(RAW / "simulation_matrix.csv") as f:
        return {int(r["Simulation_ID"]): r for r in csv.DictReader(f)}


# Target column. SCAU11 = axial Cauchy stress (the usual tensile-curve stress);
# Svm = von Mises equivalent, which also includes the small (~4 MPa) shear components.
TARGETS = ("SCAU11", "Svm")


def build(cache=True, target="SCAU11"):
    """Return (ids, X, Y, manifest). X: (n_cases, 4) conditions; Y: (n_cases, 120) stress."""
    assert target in TARGETS
    out = DATA / f"curves_{target}.npz"
    if cache and out.exists():
        z = np.load(out)
        manifest = json.loads((DATA / "manifest.json").read_text())
        return z["ids"], z["X"], z["Y"], manifest

    matrix = read_matrix()
    ids, X, Y, manifest = [], [], [], []
    for folder in sorted(RAW.glob("simulation_[0-9]*")):
        sim_id = int(folder.name.split("_")[1])
        path = folder / "STR_STR.OUT"
        a = np.loadtxt(path, skiprows=1)
        e11, stress = a[:, COLS.index("E11")], a[:, COLS.index(target)]
        assert np.all(np.diff(e11) > 0), f"E11 not increasing in case {sim_id}"
        r = matrix[sim_id]
        x = [float(r["temperature"]), np.log10(float(r["strain_rate"])),
             float(r["density"]), float(r["shear_modulus"])]
        ids.append(sim_id)
        X.append(x)
        Y.append(np.interp(STRAIN_GRID, e11, stress))
        manifest.append({
            "id": sim_id, **dict(zip(FEATURES, x)), "rows": len(a),
            "e11_min": float(e11[0]), "e11_max": float(e11[-1]),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })

    ids, X, Y = np.array(ids), np.array(X), np.array(Y)
    DATA.mkdir(exist_ok=True)
    np.savez_compressed(out, ids=ids, X=X, Y=Y, strain=STRAIN_GRID, target=target)
    (DATA / "manifest.json").write_text(json.dumps(manifest, indent=1))
    return ids, X, Y, manifest


def condition_groups(X):
    """Label each case by its (temperature, strain rate) condition, e.g. '200C_1e-5'."""
    return np.array([f"{int(t)}C_1e{int(lr)}" for t, lr in X[:, :2]])


if __name__ == "__main__":
    for t in TARGETS:
        ids, X, Y, manifest = build(cache=False, target=t)
    rows = sorted({m["rows"] for m in manifest})
    print(f"{len(ids)} cases, curves on {len(STRAIN_GRID)} strain points, row counts {rows}")
