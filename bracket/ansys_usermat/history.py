"""Read bracket_history.csv files written by post_bracket.mac, for either load case.

Files from 17 Nov 2026 (load UX = -2 mm on the whole bore) have the columns ux_applied_mm and RFX_N.
Files from 18 Nov 2026 on have load_axis, u_load_mm and F_load_N (the displacement and the reaction along
the load axis, the reaction signed positive against the displacement).
Every row gets two load-neutral keys:
  u_mm  magnitude of the imposed bore displacement (mm)
  F_N   reaction along the load axis, positive (N)
"""
import csv

LOAD_TEXT = {1: 'UX = -2 mm on the whole bore (team Workbench load)',
             2: 'UY = +2 mm on the upper half of the bore (pin load +P_y)'}


def load_history(path):
    with open(path) as f:
        rows = [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(f)]
    for r in rows:
        if 'u_load_mm' not in r:  # 17 Nov 2026 format: load along -x
            r['load_axis'], r['u_load_mm'], r['F_load_N'] = 1.0, r['ux_applied_mm'], r['RFX_N']
        r['u_mm'], r['F_N'] = abs(r['u_load_mm']), r['F_load_N']
    return rows


def load_text(rows):
    axes = {int(r['load_axis']) for r in rows}
    assert len(axes) == 1, axes
    return LOAD_TEXT[axes.pop()]
