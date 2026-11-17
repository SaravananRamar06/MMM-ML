"""Compare the bracket USERMAT runs on the 5 mm and refined meshes (open question Q9).

Usage: python bracket/ansys_usermat/plot_mesh.py RESULTS_DIR
RESULTS_DIR holds, for each mesh label in MESHES:
  usermat_<label>_history.csv, usermat_<label>_out_key_lines.txt
and optionally elastic_<label>_history.csv (drawn as a dashed reference).
Writes mesh_force_displacement.png and mesh_summary.json into RESULTS_DIR.
"""
import csv
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# label, nominal element size (mm), colour
MESHES = [('5mm', 5.0, '#c2401c'), ('2p5mm', 2.5, '#1f6fb4')]
EQPS_LIMIT = 0.0999


def load(path):
    with open(path) as f:
        return [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(f)]


def run_info(path):
    """Elements, nodes, bisections and wall time from an *_out_key_lines.txt file."""
    t = path.read_text()
    def grab(pattern, cast=float):
        m = re.findall(pattern, t)
        return cast(m[-1]) if m else None
    return {'elements': grab(r'Total number of elements = (\d+)', int),
            'nodes': grab(r'Total number of nodes = (\d+)', int),
            'bisections': len(re.findall(r'BEGIN BISECTION', t)),
            'wall_time_s': grab(r'Elapsed Time \(sec\) =\s+([\d.]+)')}


def main():
    d = Path(sys.argv[1])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.4))
    summary = {}
    for label, size, colour in MESHES:
        r = load(d / f'usermat_{label}_history.csv')
        info = run_info(d / f'usermat_{label}_out_key_lines.txt')
        u = [0.0] + [-x['ux_applied_mm'] for x in r]
        a1.plot(u, [0.0] + [x['RFX_N'] / 1e3 for x in r], '-o', ms=3, color=colour,
                label=f'USERMAT, {size:g} mm ({info["elements"]:,} elements)')
        a2.plot(u, [0.0] + [x['svar1_max_elem'] for x in r], '-o', ms=3, color=colour, label=f'{size:g} mm')
        el = d / f'elastic_{label}_history.csv'
        if el.exists():
            e = load(el)
            a1.plot([0.0] + [-x['ux_applied_mm'] for x in e], [0.0] + [x['RFX_N'] / 1e3 for x in e], '--',
                    color=colour, lw=0.8, alpha=0.6, label=f'elastic, {size:g} mm')
        peak = max(r, key=lambda x: x['RFX_N'])
        summary[label] = {'element_size_mm': size, 'elements': info['elements'], 'nodes': info['nodes'],
                          'initial_stiffness_N_per_mm': r[0]['RFX_N'] / -r[0]['ux_applied_mm'],
                          'peak_RFX_N': peak['RFX_N'], 'peak_at_ux_mm': peak['ux_applied_mm'],
                          'RFX_at_final_N': r[-1]['RFX_N'], 'final_ux_mm': r[-1]['ux_applied_mm'],
                          'max_elem_eqps_svar1': r[-1]['svar1_max_elem'],
                          'n_elem_flagged': int(r[-1]['n_elem_flag']),
                          'flagged_volume_note': 'element count, not volume: a finer mesh has smaller elements',
                          'substeps': len(r), 'bisections': info['bisections'], 'wall_time_s': info['wall_time_s']}
    ref = summary[MESHES[0][0]]
    for label in summary:
        s = summary[label]
        s['pct_vs_5mm'] = {k: round(100 * (s[k] / ref[k] - 1), 3) for k in
                           ('initial_stiffness_N_per_mm', 'peak_RFX_N', 'RFX_at_final_N', 'max_elem_eqps_svar1')}
    a1.set(xlabel='imposed displacement |UX| (mm)', ylabel='reaction at fixed support, RFX (kN)',
           title='Force-displacement', ylim=(0, 1.25 * max(s['peak_RFX_N'] for s in summary.values()) / 1e3))
    a2.axhline(EQPS_LIMIT, color='k', lw=0.8, ls=':')
    a2.text(0.02, EQPS_LIMIT, ' data limit EQPS 0.0999', va='bottom', fontsize=7)
    a2.set(xlabel='imposed displacement |UX| (mm)', ylabel='max element EQPS (SVAR1)',
           title='Peak plastic strain (localisation)')
    for a in (a1, a2):
        a.grid(alpha=0.3)
        a.legend(fontsize=7.5)
    fig.suptitle('Bracket with the JC-PINN USERMAT at the study point: 5 mm mesh vs uniform 2x2x2 refinement',
                 fontsize=9)
    fig.tight_layout()
    fig.savefig(d / 'mesh_force_displacement.png', dpi=150)
    (d / 'mesh_summary.json').write_text(json.dumps(summary, indent=2) + '\n', newline='\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
