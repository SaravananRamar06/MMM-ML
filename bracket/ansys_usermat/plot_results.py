"""Plot the bracket histories written by post_bracket.mac.

Usage: python bracket/ansys_usermat/plot_results.py RESULTS_DIR
RESULTS_DIR holds elastic_history.csv, ep_miso_history.csv and usermat_history.csv.
Writes force_displacement.png and summary.json into RESULTS_DIR.
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RUNS = [('elastic', 'Workbench "AlSi10Mg - E" (elastic)', '#8c8c8c', '--'),
        ('ep_miso', 'Workbench "AlSi10Mg - EP" (TB,PLAS MISO)', '#1f6fb4', '-'),
        ('usermat', 'JC-PINN USERMAT, study point (100 C, 1e-4 /s, phi 4 %)', '#c2401c', '-')]


def load(path):
    with open(path) as f:
        rows = [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(f)]
    return [{'set': 0, 'time': 0.0, 'ux_applied_mm': 0.0, 'RFX_N': 0.0, 'seqv_max_elem_MPa': 0.0,
             'eppl_eqv_max_elem': 0.0, 'svar1_max_elem': 0.0, 'n_elem_flag': 0.0}] + rows


def main():
    d = Path(sys.argv[1])
    data = {k: load(d / f'{k}_history.csv') for k, *_ in RUNS}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
    for k, label, colour, ls in RUNS:
        r = data[k]
        u = [-x['ux_applied_mm'] for x in r]
        a1.plot(u, [x['RFX_N'] / 1e3 for x in r], ls, color=colour, marker='o', ms=3, label=label)
        a2.plot(u, [x['seqv_max_elem_MPa'] for x in r], ls, color=colour, marker='o', ms=3, label=label)
    a1.set(xlabel='imposed displacement |UX| (mm)', ylabel='reaction at fixed support, RFX (kN)',
           title='Force-displacement')
    a2.set(xlabel='imposed displacement |UX| (mm)', ylabel='max element von Mises (MPa)',
           title='Peak centroid stress')
    for a in (a1, a2):
        a.grid(alpha=0.3)
    a1.legend(fontsize=7.5, loc='upper left')
    fig.suptitle('Bracket, same mesh and load, MAPDL 2024 R1 (one mesh only; softening is mesh dependent)', fontsize=9)
    fig.tight_layout()
    fig.savefig(d / 'force_displacement.png', dpi=150)

    summary = {}
    for k, *_ in RUNS:
        r = data[k][1:]
        peak = max(r, key=lambda x: x['RFX_N'])
        summary[k] = {'substeps_saved': len(r),
                      'final_ux_mm': r[-1]['ux_applied_mm'],
                      'final_RFX_N': r[-1]['RFX_N'],
                      'peak_RFX_N': peak['RFX_N'], 'peak_at_ux_mm': peak['ux_applied_mm'],
                      'initial_stiffness_N_per_mm': r[0]['RFX_N'] / -r[0]['ux_applied_mm'],
                      'final_seqv_max_elem_MPa': r[-1]['seqv_max_elem_MPa'],
                      'final_eppl_eqv_max_elem': r[-1]['eppl_eqv_max_elem'],
                      'final_svar1_max_elem': r[-1]['svar1_max_elem'],
                      'final_n_elem_flag': int(r[-1]['n_elem_flag'])}
    (d / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', newline='\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
