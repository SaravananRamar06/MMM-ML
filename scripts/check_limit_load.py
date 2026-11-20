"""Check the capability-based limit pin load P_L = 35.9 kN against the committed bracket runs.

Reads only committed CSV/JSON files under bracket/ansys_usermat/. Prints every quantity used in
docs/proposals/limit-load-check-2026-11-20.md. Post-hoc; the locked model is not touched.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'bracket' / 'ansys_usermat'


def rows(rel):
    with open(ROOT / rel, newline='') as f:
        return [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(f)]


def per_kn(rel, key):
    r = rows(rel)[0]                       # first substep: fully elastic in every run
    return r[key] / (r['F_load_N'] / 1e3)


def first_yield_bracket(rel):
    """Last saved load with zero plastic strain and first saved load with plastic strain (kN)."""
    h = rows(rel)
    for a, b in zip(h, h[1:]):
        if a['svar1_max_elem'] == 0 and b['svar1_max_elem'] > 0:
            return a['F_load_N'] / 1e3, b['F_load_N'] / 1e3
    return None


SY = 136.06          # JC-PINN initial flow stress at the study point (umat/README.md), MPa
PEAK_3D = 100.5      # USERMAT 5 mm peak reaction, kN
FACTOR = 1.5 * 1.15  # 14 CFR 25.303 x 25.625 fitting factor

zones = json.load(open(ROOT / 'zones_uy_2026-11-18' / 'zones.json'))['elastic']['sets'][0]
f0 = zones['F_kN']
fil_vm, fil_s1 = zones['zones']['fillet']['SEQV_max'] / f0, zones['zones']['fillet']['S1_max'] / f0
print(f'1. Elastic 5 mm, R10 fillet: von Mises {fil_vm:.3f} MPa/kN, S1 {fil_s1:.3f} MPa/kN '
      f'(support corner {zones["zones"]["support"]["SEQV_max"] / f0:.3f}, singular)')
print(f'2. First yield  P = {SY} / {fil_vm:.3f} = {SY / fil_vm:.2f} kN')
print(f'   Capability   P = {PEAK_3D} / {FACTOR:.3f} = {PEAK_3D / FACTOR:.2f} kN  -> P_L,max = '
      f'{min(SY / fil_vm, PEAK_3D / FACTOR):.2f} kN')
print(f'   Tension-based LEFM limit {SY} / {fil_s1:.3f} = {SY / fil_s1:.2f} kN')

print('3. Mesh check (first substep, MPa/kN; node = surface nodal maximum, elem = element maximum):')
for m in ('5mm', '2p5mm'):
    for kind in ('elastic', 'usermat'):
        rel = f'mesh_uy_2026-11-18/{kind}_{m}_history.csv'
        n, e = per_kn(rel, 'seqv_max_node_MPa'), per_kn(rel, 'seqv_max_elem_MPa')
        print(f'   {kind:8s} {m:6s} node {n:.3f}  elem {e:.3f}  -> {SY}/node = {SY / n:.1f} kN')
for m in ('5mm', '2p5mm'):
    lo, hi = first_yield_bracket(f'mesh_uy_2026-11-18/usermat_{m}_history.csv')
    print(f'   USERMAT {m}: no plastic strain at {lo:.1f} kN, plastic strain at {hi:.1f} kN')

print('4. Porosity (G coupled, D5): first-yield limit load = flow stress / fillet von Mises per kN')
for c, phi in (('gphi0', 0.0), ('gphi4', 4.0), ('gphi785', 7.85)):
    sy = max(r['seqv_max_node_MPa'] for r in rows(f'porosity_gphi_uy_2026-11-18/{c}_history.csv'))
    print(f'   phi {phi:5.2f} %: flow stress {sy:.2f} MPa -> P_L {sy / fil_vm:.2f} kN')

print('5. Loads for a crack check:')
print(f'   limit (25.571(b) residual strength)  {SY / fil_vm:.1f} kN')
print(f'   limit x 1.15 fitting factor           {SY / fil_vm * 1.15:.1f} kN')
print(f'   ultimate = 1.5 x limit (25.303)       {SY / fil_vm * 1.5:.1f} kN')
