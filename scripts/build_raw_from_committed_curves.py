"""Rebuild a stand-in raw folder from the committed 120-point curves (local verification only).

The professor's raw histories are excluded from Git. Every project model reads them through the
same interpolation onto 120 E11 points, and those interpolated curves for all 73 cases are
committed in reports/jc_pinn_20261107/{cv,test}_predictions.csv (column Svm, written with full float
precision; identical to the 2 Nov hash-checked curves, see baselines.json). This script writes one 120-row STR_STR.OUT per case plus a simulation_matrix.csv so the
JC-PINN pipeline can run its exact raw-file loading path in an environment without the raw data.
np.interp at the identical grid points returns the stored values exactly, so models see the same
curves as from the real histories. Unused columns are zero. Output goes to the ignored work/ folder.
"""
import csv
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'work/raw_from_committed_curves'
manifest = {m['id']: m for m in json.loads((root / 'data/manifest.json').read_text())}
curves = {}
for name in ('cv_predictions.csv', 'test_predictions.csv'):
    with (root / 'reports/jc_pinn_20261107' / name).open() as f:
        for r in csv.DictReader(f):
            curves.setdefault(int(r['id']), []).append((r['E11'], r['Svm']))
assert sorted(curves) == sorted(manifest), 'committed curves must cover all 73 manifest cases'
out.mkdir(parents=True, exist_ok=True)
with (out / 'simulation_matrix.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Simulation_ID', 'temperature', 'strain_rate', 'density', 'shear_modulus'])
    for i in sorted(manifest):
        m = manifest[i]
        w.writerow([i, m['temperature'], repr(10.0 ** m['log10_strain_rate']), m['density'], m['shear_modulus']])
header = 'TIME Evm Svm E11 E22 E33 E23 E13 E12 SCAU11 SCAU22 SCAU33 SCAU23 SCAU13 SCAU12 TEMP'
for i, rows in curves.items():
    m = manifest[i]
    rate = 10.0 ** m['log10_strain_rate']
    d = out / f'simulation_{i:04d}'
    d.mkdir(exist_ok=True)
    lines = [header] + [' '.join([repr(float(e) / rate), '0', s, e] + ['0'] * 11 + [repr(m['temperature'] + 273.15)])
                        for e, s in rows]
    (d / 'STR_STR.OUT').write_text('\n'.join(lines) + '\n')
print(out, len(curves), 'cases')
