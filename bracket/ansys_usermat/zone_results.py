"""Zone-by-zone stresses and plastic strain of a solved bracket run, from dump_nodes.mac output.

Usage: python bracket/ansys_usermat/zone_results.py OUT_JSON RUN_LABEL=DUMP_DIR [RUN_LABEL=DUMP_DIR ...]
Each DUMP_DIR holds nodes_xyz.csv, sets.csv and ns<N>.csv (node, S1, S3, SEQV, EPPL) from dump_nodes.mac, and
sits inside a run folder whose bracket_history.csv gives the reaction per set.

Zones (mm, from the STEP: bore r = 5 at the origin, R10 crotch fillet axis at (36.15, 23)); every zone stops
5 mm short of the mounting faces (x = 210), where the fixed support makes stresses singular:
  bore_upper    bore surface (r 4.8-5.2), y >= 0: the half the pin bears on
  bore_sides    bore surface, |y| < 1.5 (left and right of the bore: hoop tension)
  ligament      within 4 mm of the line from the upper-left of the bore (-2.5, 5.5) to the fillet (28, 17)
  fillet        R10 crotch fillet surface: |distance to (36.15, 23) - 10| < 0.8
  lower_root    lower arm, top edge near the crotch: 40 <= x <= 90, 8 <= y <= 14
  lower_bottom  lower arm, bottom edge near the support: 150 <= x <= 205, y <= -25
  upper_arm     upper arm away from both ends: y >= 35, 60 <= x <= 180
  support       mounting-face corners region: x >= 205 (singular; for reference only)
"""
import csv
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from history import load_history  # noqa: E402

FX, FY, FR = 36.15, 23.0, 10.0


def zone_of(x, y):
    z = []
    r = math.hypot(x, y)
    if x < 205:
        if 4.8 <= r <= 5.2 and y >= 0:
            z.append('bore_upper')
        if 4.8 <= r <= 5.2 and abs(y) < 1.5:
            z.append('bore_sides')
        ax, ay, bx, by = -2.5, 5.5, 28.0, 17.0
        t = max(0.0, min(1.0, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
        if math.hypot(x - ax - t * (bx - ax), y - ay - t * (by - ay)) < 4.0 and r > 5.2:
            z.append('ligament')
        if abs(math.hypot(x - FX, y - FY) - FR) < 0.8:
            z.append('fillet')
        if 40 <= x <= 90 and 8 <= y <= 14:
            z.append('lower_root')
        if 150 <= x <= 205 and y <= -25:
            z.append('lower_bottom')
        if y >= 35 and 60 <= x <= 180:
            z.append('upper_arm')
    else:
        z.append('support')
    return z


def read_rows(p):
    with open(p) as f:
        return [[float(v) for v in line.split(',')] for line in f if line.strip()]


def main():
    out = Path(sys.argv[1])
    result = {}
    for arg in sys.argv[2:]:
        label, _, d = arg.partition('=')
        d = Path(d)
        hist = load_history(d.parent / 'bracket_history.csv')
        zones = {}
        for n, x, y, z in read_rows(d / 'nodes_xyz.csv'):
            for name in zone_of(x, y):
                zones.setdefault(name, set()).add(int(n))
        sets = read_rows(d / 'sets.csv')
        per_set = []
        for (i, t), h in zip(sets, hist):
            data = {int(r[0]): r[1:] for r in read_rows(d / f'ns{int(i)}.csv')}
            row = {'set': int(i), 'time': t, 'u_mm': h['u_mm'], 'F_kN': h['F_N'] / 1e3, 'zones': {}}
            for name, nodes in zones.items():
                v = [data[k] for k in nodes if k in data]
                row['zones'][name] = {'S1_max': max(a[0] for a in v), 'S3_min': min(a[1] for a in v),
                                      'SEQV_max': max(a[2] for a in v), 'EPPL_max': max(a[3] for a in v)}
            per_set.append(row)
        result[label] = {'zone_node_counts': {k: len(v) for k, v in zones.items()}, 'sets': per_set}
        print(label, {k: len(v) for k, v in zones.items()})
    out.write_text(json.dumps(result, indent=1) + '\n', newline='\n')


if __name__ == '__main__':
    main()
