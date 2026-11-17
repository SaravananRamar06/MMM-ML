"""Single-element expectation for the porosity cases, from the locked JC-PINN (no ANSYS).

Evaluates jc_pinn.equation_predict(load_final_equation(), X) with X rows
[T, log10 rate, density, G, eqps] at eqps = 0.0002, 0.05 and 0.0999 for every case in
make_decks.POROSITY_CASES, and writes expected_flow_stress.csv with the flow stress and its
% change relative to phi0 at the same eqps. (Decision M4: the data strain E11 is read as
plastic strain, so eqps is the model's strain input.)

With --gphi it uses make_decks.GPHI_CASES (density and G coupled by decision D5), relative to gphi0.

Usage: python bracket/ansys_usermat/expected_flow_stress.py [--gphi] OUTPUT_DIR
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402
import jc_pinn  # noqa: E402
from make_decks import GPHI_CASES, POROSITY_CASES  # noqa: E402

T, LOG_RATE = 100.0, -4.0
EQPS = (0.0002, 0.05, 0.0999)


def main():
    args = [a for a in sys.argv[1:] if a != '--gphi']
    cases = GPHI_CASES if '--gphi' in sys.argv[1:] else POROSITY_CASES
    ref = next(iter(cases))  # phi0 or gphi0
    out = Path(args[0])
    out.mkdir(parents=True, exist_ok=True)
    eq = jc_pinn.load_final_equation(ROOT)
    sig = {}
    for case, (rho, g, _) in cases.items():
        X = np.array([[T, LOG_RATE, rho, g, e] for e in EQPS])
        sig[case] = np.asarray(jc_pinn.equation_predict(eq, X), dtype=float).ravel()
    rows = []
    for case, (rho, g, _) in cases.items():
        for k, e in enumerate(EQPS):
            rows.append({'case': case, 'density_kg_m3': rho, 'phi_pct': round(100 * (1 - rho / 2700), 4),
                         'G_MPa': g, 'eqps': e, 'flow_stress_MPa': round(float(sig[case][k]), 6),
                         'change_vs_phi0_pct': round(float(100 * (sig[case][k] / sig[ref][k] - 1)), 4)})
    with open(out / 'expected_flow_stress.csv', 'w', newline='\n') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print('{case:7s} rho {density_kg_m3:8.2f} G {G_MPa:9.2f} eqps {eqps:<7g} sigma {flow_stress_MPa:9.4f} MPa  '
              '{change_vs_phi0_pct:+.3f} %'.format(**r))


if __name__ == '__main__':
    main()
