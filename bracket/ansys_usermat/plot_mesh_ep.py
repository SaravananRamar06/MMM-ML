"""Mesh check with the hardening Workbench EP material, against the USERMAT mesh pair (Q9).

Usage: python bracket/ansys_usermat/plot_mesh_ep.py RESULTS_DIR
RESULTS_DIR holds ep_miso_5mm_history.csv, ep_miso_2p5mm_history.csv and their
*_out_key_lines.txt. The USERMAT pair is read, unchanged, from ../mesh_2026-11-17/.
Writes mesh_ep_force_displacement.png and mesh_ep_summary.json into RESULTS_DIR.
"""
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
USERMAT_DIR = HERE / 'mesh_2026-11-17'
MESHES = [('5mm', 5.0), ('2p5mm', 2.5)]
PROBES = (0.455, 1.0)  # |UX| in mm where RFX is compared


def load(path):
    with open(path) as f:
        return [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(f)]


def run_info(path):
    t = path.read_text()
    m = re.findall(r'Elapsed Time \(sec\) =\s+([\d.]+)', t)
    return {'bisections': len(re.findall(r'BEGIN BISECTION', t)), 'wall_time_s': float(m[-1]) if m else None}


def describe(r, info):
    u = np.array([0.0] + [-x['ux_applied_mm'] for x in r])
    f = np.array([0.0] + [x['RFX_N'] for x in r])
    peak = max(r, key=lambda x: x['RFX_N'])
    out = {'initial_stiffness_N_per_mm': r[0]['RFX_N'] / -r[0]['ux_applied_mm'],
           'peak_RFX_N': peak['RFX_N'], 'peak_at_ux_mm': peak['ux_applied_mm'],
           'RFX_at_final_N': r[-1]['RFX_N']}
    for p in PROBES:
        out[f'RFX_at_ux_{p:g}mm_N'] = float(np.interp(p, u, f))
    out['max_elem_eppl_eqv'] = r[-1]['eppl_eqv_max_elem']
    out['substeps'] = len(r)
    out.update(info)
    return out


def pct(s, ref):
    keys = ['initial_stiffness_N_per_mm', 'peak_RFX_N', 'RFX_at_final_N', 'max_elem_eppl_eqv'] + \
           [f'RFX_at_ux_{p:g}mm_N' for p in PROBES]
    return {k: round(100 * (s[k] / ref[k] - 1), 3) for k in keys}


def main():
    d = Path(sys.argv[1])
    data, summary = {}, {'ep_miso': {}, 'usermat': {}}
    for label, size in MESHES:
        data['ep_miso', label] = load(d / f'ep_miso_{label}_history.csv')
        summary['ep_miso'][label] = {'element_size_mm': size, **describe(data['ep_miso', label],
                                                                         run_info(d / f'ep_miso_{label}_out_key_lines.txt'))}
        data['usermat', label] = load(USERMAT_DIR / f'usermat_{label}_history.csv')
        summary['usermat'][label] = {'element_size_mm': size, **describe(data['usermat', label],
                                                                          run_info(USERMAT_DIR / f'usermat_{label}_out_key_lines.txt'))}
    for mat in summary:
        ref = summary[mat]['5mm']
        for label in summary[mat]:
            summary[mat][label]['pct_vs_5mm'] = pct(summary[mat][label], ref)
    # the USERMAT numbers must agree with the committed mesh_summary.json
    ms = json.loads((USERMAT_DIR / 'mesh_summary.json').read_text())
    for label, _ in MESHES:
        for k in ('initial_stiffness_N_per_mm', 'peak_RFX_N', 'RFX_at_final_N', 'bisections', 'wall_time_s'):
            assert abs(summary['usermat'][label][k] - ms[label][k]) <= 1e-9 * max(1, abs(ms[label][k])), (label, k)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.4))
    style = {('ep_miso', '5mm'): ('#1f6fb4', '-'), ('ep_miso', '2p5mm'): ('#1f6fb4', '--'),
             ('usermat', '5mm'): ('#c2401c', '-'), ('usermat', '2p5mm'): ('#c2401c', '--')}
    names = {'ep_miso': 'Workbench EP (MISO, hardening)', 'usermat': 'JC-PINN USERMAT (softening)'}
    for (mat, label), r in data.items():
        colour, ls = style[mat, label]
        u = [0.0] + [-x['ux_applied_mm'] for x in r]
        size = dict(MESHES)[label]
        a1.plot(u, [0.0] + [x['RFX_N'] / 1e3 for x in r], ls, marker='o', ms=2.5, color=colour,
                label=f'{names[mat]}, {size:g} mm')
        a2.plot(u, [0.0] + [x['eppl_eqv_max_elem'] for x in r], ls, marker='o', ms=2.5, color=colour,
                label=f'{names[mat]}, {size:g} mm')
    for p in PROBES:
        a1.axvline(p, color='k', lw=0.6, ls=':')
    a1.set(xlabel='imposed displacement |UX| (mm)', ylabel='reaction at fixed support, RFX (kN)',
           title='Force-displacement')
    a2.set(xlabel='imposed displacement |UX| (mm)', ylabel='max element EPPL,EQV',
           title='Peak plastic strain')
    for a in (a1, a2):
        a.grid(alpha=0.3)
        a.legend(fontsize=7)
    fig.suptitle('Bracket mesh check: 5 mm (solid) vs uniform 2x2x2 refinement (dashed); EP is a different material '
                 'condition, used only to test the mesh', fontsize=8.5)
    fig.tight_layout()
    fig.savefig(d / 'mesh_ep_force_displacement.png', dpi=150)
    (d / 'mesh_ep_summary.json').write_text(json.dumps(summary, indent=2) + '\n', newline='\n')
    print(json.dumps({m: {l: s['pct_vs_5mm'] for l, s in v.items()} for m, v in summary.items()}, indent=2))


if __name__ == '__main__':
    main()
