"""Compare the ANSYS single-element result with the offline expectation.

Run in the folder where ANSYS wrote jcpinn_single_element.csv:
    python compare.py [jcpinn_single_element.csv]
Passes if S11 agrees with expected_single_element.csv to within 0.1 MPa at every ANSYS point.
"""
import csv
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def load(path):
    with open(path) as f:
        rows = [r for r in csv.reader(f) if r and not r[0].startswith('eps')]
    return np.array([[float(x) for x in r] for r in rows])


def main():
    got = load(sys.argv[1] if len(sys.argv) > 1 else 'jcpinn_single_element.csv')
    ref = load(HERE / 'expected_single_element.csv')
    want = np.interp(got[:, 0], ref[:, 0], ref[:, 1])
    err = np.abs(got[:, 1] - want)
    i = int(np.argmax(err))
    print(f'points {len(got)}, max |S11 difference| {err.max():.4g} MPa at eps11 = {got[i, 0]:.4g}')
    print(f'final: ANSYS S11 {got[-1, 1]:.4f} MPa, EQPS {got[-1, 2]:.6f}, flag {int(got[-1, 4])}; '
          f'expected {ref[-1, 1]:.4f} MPa, EQPS {ref[-1, 2]:.6f}, flag {int(ref[-1, 4])}')
    ok = err.max() < 0.1
    print('PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
