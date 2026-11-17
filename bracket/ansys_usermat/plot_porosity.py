"""Plot and summarise the bracket porosity runs written by post_bracket.mac.

Usage: python bracket/ansys_usermat/plot_porosity.py RESULTS_DIR
RESULTS_DIR holds <case>_history.csv for phi0, phi4, phi785, G_lo and G_hi.
Writes porosity_force_displacement.png and porosity_summary.json into RESULTS_DIR.
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from make_decks import POROSITY_CASES  # noqa: E402

MAIN = [('phi0', '#1b7837'), ('phi4', '#c2401c'), ('phi785', '#5e3c99')]
GSET = [('G_lo', '#2166ac'), ('phi4', '#c2401c'), ('G_hi', '#b2182b')]


def load(path):
    with open(path) as f:
        return [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(f)]


def label(case):
    rho, g, _ = POROSITY_CASES[case]
    return f'{case}: rho {rho:.12g}, phi {100 * (1 - rho / 2700):.2f} %, G {g:.12g}'


def main():
    d = Path(sys.argv[1])
    data = {c: load(d / f'{c}_history.csv') for c in POROSITY_CASES}

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    for ax, cases, title in ((axes[0], MAIN, 'Main set: density only, G = 24541 MPa'),
                             (axes[1], GSET, 'Secondary set: G sensitivity at phi = 4 %\n'
                                             '(G also changes the elastic stiffness)')):
        for c, colour in cases:
            r = [{'ux_applied_mm': 0.0, 'RFX_N': 0.0}] + data[c]
            ax.plot([-x['ux_applied_mm'] for x in r], [x['RFX_N'] / 1e3 for x in r], '-o', ms=2.5,
                    color=colour, lw=1.2, label=label(c))
        ax.set(xlabel='imposed displacement |UX| (mm)', ylabel='reaction at fixed support, RFX (kN)', title=title)
        ax.title.set_fontsize(9.5)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7, loc='center right', bbox_to_anchor=(1.0, 0.42))
        # inset: zoom on the peak, where the cases differ by well under 1 %
        ins = ax.inset_axes([0.24, 0.1, 0.3, 0.42])
        for c, colour in cases:
            r = data[c]
            ins.plot([-x['ux_applied_mm'] for x in r], [x['RFX_N'] / 1e3 for x in r], '-o', ms=2.5,
                     color=colour, lw=1.0)
        peaks = [max(x['RFX_N'] for x in data[c]) / 1e3 for c, _ in cases]
        ins.set_xlim(0.3, 0.7)
        ins.set_ylim(min(peaks) - 4, max(peaks) + 2)
        ins.tick_params(labelsize=6.5)
        ins.set_title('peak region', fontsize=7)
        ins.grid(alpha=0.3)
    fig.suptitle('Bracket with the JC-PINN USERMAT, 100 C, 1e-4 /s, nu 0.33; same 5 mm mesh and -2 mm load '
                 '(post-peak values are mesh dependent)', fontsize=9)
    fig.tight_layout()
    fig.savefig(d / 'porosity_force_displacement.png', dpi=150)

    summary = {}
    for c, (rho, g, note) in POROSITY_CASES.items():
        r = data[c]
        peak = max(r, key=lambda x: x['RFX_N'])
        summary[c] = {'density_kg_m3': rho, 'phi_pct': round(100 * (1 - rho / 2700), 4), 'G_MPa': g, 'note': note,
                      'substeps_saved': len(r), 'final_ux_mm': r[-1]['ux_applied_mm'],
                      'peak_RFX_N': peak['RFX_N'], 'peak_at_ux_mm': peak['ux_applied_mm'],
                      'RFX_at_final_N': r[-1]['RFX_N'],
                      'max_elem_eqps_svar1': r[-1]['svar1_max_elem'],
                      'n_elem_flagged': int(r[-1]['n_elem_flag'])}
    ref = summary['phi0']
    for c in summary:
        s = summary[c]
        s['peak_RFX_change_vs_phi0_pct'] = round(100 * (s['peak_RFX_N'] / ref['peak_RFX_N'] - 1), 4)
        s['RFX_at_final_change_vs_phi0_pct'] = round(100 * (s['RFX_at_final_N'] / ref['RFX_at_final_N'] - 1), 4)
    (d / 'porosity_summary.json').write_text(json.dumps(summary, indent=2) + '\n', newline='\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
