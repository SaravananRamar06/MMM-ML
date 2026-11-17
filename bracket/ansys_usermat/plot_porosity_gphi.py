"""Plot and summarise the bracket porosity runs with density and G coupled by decision D5.

Usage: python bracket/ansys_usermat/plot_porosity_gphi.py RESULTS_DIR
RESULTS_DIR holds gphi0_history.csv, gphi4_history.csv and gphi785_history.csv (post_bracket.mac).
For comparison it also reads the density-only runs (G fixed) from ../porosity_2026-11-17/.
Writes porosity_gphi_force_displacement.png and porosity_gphi_summary.json into RESULTS_DIR.
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
from make_decks import GPHI_CASES, POROSITY_CASES  # noqa: E402

COUPLED = [('gphi0', '#1b7837'), ('gphi4', '#c2401c'), ('gphi785', '#5e3c99')]
DENSITY_ONLY = HERE / 'porosity_2026-11-17'


def load(path):
    with open(path) as f:
        return [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(f)]


def summarise(r, rho, g):
    peak = max(r, key=lambda x: x['RFX_N'])
    return {'density_kg_m3': rho, 'phi_pct': round(100 * (1 - rho / 2700), 4), 'G_MPa': g,
            'substeps_saved': len(r), 'final_ux_mm': r[-1]['ux_applied_mm'],
            'initial_stiffness_N_per_mm': r[0]['RFX_N'] / -r[0]['ux_applied_mm'],
            'peak_RFX_N': peak['RFX_N'], 'peak_at_ux_mm': peak['ux_applied_mm'],
            'RFX_at_final_N': r[-1]['RFX_N'], 'max_elem_eqps_svar1': r[-1]['svar1_max_elem'],
            'n_elem_flagged': int(r[-1]['n_elem_flag'])}


def main():
    d = Path(sys.argv[1])
    data = {c: load(d / f'{c}_history.csv') for c in GPHI_CASES}
    summary = {c: summarise(data[c], *GPHI_CASES[c][:2]) for c in GPHI_CASES}
    ref = summary['gphi0']
    for s in summary.values():
        s['pct_vs_gphi0'] = {k: round(100 * (s[k] / ref[k] - 1), 4)
                             for k in ('initial_stiffness_N_per_mm', 'peak_RFX_N', 'RFX_at_final_N')}
    # density-only runs at the same porosities (G = 24541 fixed), for comparison
    dens = {c: summarise(load(DENSITY_ONLY / f'{c}_history.csv'), *POROSITY_CASES[c][:2]) for c in ('phi0', 'phi785')}
    summary['density_only_reference'] = {
        'source': 'bracket/ansys_usermat/porosity_2026-11-17/ (G fixed at 24541 MPa)',
        'peak_RFX_change_phi0_to_phi785_pct': round(100 * (dens['phi785']['peak_RFX_N'] / dens['phi0']['peak_RFX_N'] - 1), 4),
        'RFX_at_final_change_phi0_to_phi785_pct': round(100 * (dens['phi785']['RFX_at_final_N'] / dens['phi0']['RFX_at_final_N'] - 1), 4),
    }

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.4))
    for c, colour in COUPLED:
        rho, g, _ = GPHI_CASES[c]
        r = [{'ux_applied_mm': 0.0, 'RFX_N': 0.0}] + data[c]
        lab = f'{c}: phi {100 * (1 - rho / 2700):.2f} %, rho {rho:.12g}, G {g:.12g}'
        a1.plot([-x['ux_applied_mm'] for x in r], [x['RFX_N'] / 1e3 for x in r], '-o', ms=2.5, color=colour, label=lab)
    ins = a1.inset_axes([0.24, 0.1, 0.3, 0.42])
    for c, colour in COUPLED:
        r = data[c]
        ins.plot([-x['ux_applied_mm'] for x in r], [x['RFX_N'] / 1e3 for x in r], '-o', ms=2.5, color=colour, lw=1)
    pk = [summary[c]['peak_RFX_N'] / 1e3 for c, _ in COUPLED]
    ins.set_xlim(0.3, 0.7)
    ins.set_ylim(min(pk) - 4, max(pk) + 2)
    ins.tick_params(labelsize=6.5)
    ins.set_title('peak region', fontsize=7)
    ins.grid(alpha=0.3)
    a1.set(xlabel='imposed displacement |UX| (mm)', ylabel='reaction at fixed support, RFX (kN)',
           title='Density and G coupled: G = 25300 (1 - phi) (D5)')
    a1.legend(fontsize=7, loc='center right', bbox_to_anchor=(1.0, 0.42))
    names = ['peak force', 'force at -2 mm']
    coupled = [summary['gphi785']['pct_vs_gphi0']['peak_RFX_N'], summary['gphi785']['pct_vs_gphi0']['RFX_at_final_N']]
    donly = [summary['density_only_reference']['peak_RFX_change_phi0_to_phi785_pct'],
             summary['density_only_reference']['RFX_at_final_change_phi0_to_phi785_pct']]
    x = range(len(names))
    a2.bar([i - 0.18 for i in x], donly, width=0.36, color='#9aa6b3', label='density only (G fixed)')
    a2.bar([i + 0.18 for i in x], coupled, width=0.36, color='#5e3c99', label='density and G coupled (D5)')
    for i in x:
        a2.text(i - 0.18, donly[i] - 0.25, f'{donly[i]:.2f} %', ha='center', va='top', fontsize=8)
        a2.text(i + 0.18, coupled[i] - 0.25, f'{coupled[i]:.2f} %', ha='center', va='top', fontsize=8)
    a2.axhline(0, color='k', lw=0.8)
    a2.set_xticks(list(x), names)
    a2.set(ylabel='change from phi 0 to 7.85 % (%)', title='Bracket change, phi 0 -> 7.85 %',
           ylim=(min(coupled + donly) * 1.35, 0.6))
    a2.legend(fontsize=7.5, loc='lower left')
    for a in (a1, a2):
        a.grid(alpha=0.3)
    fig.suptitle('Bracket with the JC-PINN USERMAT, 100 C, 1e-4 /s, nu 0.33; 5 mm mesh, -2 mm load '
                 '(G(phi) is an assumed upper bound; post-peak values are mesh dependent)', fontsize=8.5)
    fig.tight_layout()
    fig.savefig(d / 'porosity_gphi_force_displacement.png', dpi=150)
    (d / 'porosity_gphi_summary.json').write_text(json.dumps(summary, indent=2) + '\n', newline='\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
