"""Charts of the porosity effect on limit load, residual strength and critical flaw length (from fad_cl.py output).

Usage: python plot_cl.py OUT_DIR   (OUT_DIR holds fad_cl.json)
Writes limit_load_phi.png, residual_strength.png, cl_vs_load.png.
The limit loads P_L(phi) are those printed by scripts/check_limit_load.py (step 4).
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

COLORS = {'gphi0': '#1b7837', 'gphi4': '#c2401c', 'gphi785': '#5e3c99'}
LABELS = {'gphi0': 'φ = 0 %', 'gphi4': 'φ = 4 %', 'gphi785': 'φ = 7.85 %'}
P_LIMIT_PHI = {'gphi0': 36.25, 'gphi4': 35.82, 'gphi785': 35.43}   # scripts/check_limit_load.py, step 4
INK, MUTED = '#222222', '#666666'


def style(ax):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.grid(alpha=0.2, lw=0.6)
    ax.tick_params(colors=INK, labelsize=9)


def main():
    out = Path(sys.argv[1])
    d = json.loads((out / 'fad_cl.json').read_text())
    A = sorted(float(a) for a in d['elastic'])
    lim, lim_ff = d['loads_kN']['limit'], d['loads_kN']['limit_x_1.15']

    # 1. limit load against porosity
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    for j, (c, v) in enumerate(P_LIMIT_PHI.items()):
        ax.bar(j, v, width=0.55, color=COLORS[c])
        ax.text(j, v + 0.4, f'{v:.2f} kN', ha='center', va='bottom', fontsize=9, color=INK)
    ax.set_xticks(range(3), [LABELS[c] for c in P_LIMIT_PHI])
    ax.set_ylim(0, 42)
    ax.set_ylabel('limit pin load P_L (kN)', color=INK)
    ax.set_title('First-yield limit load at the R10 fillet\n(G coupled to porosity, D5): −2.3 % from φ 0 to 7.85 %',
                 fontsize=10, color=INK)
    style(ax)
    fig.tight_layout()
    fig.savefig(out / 'limit_load_phi.png', dpi=170)
    plt.close(fig)

    # 2. residual strength against crack length
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    for c, v in d['cases'].items():
        pa = [v['per_a'][f'{a:g}'] for a in A]
        ax.fill_between(A, [p['P_f_first_K36'] for p in pa], [p['P_f_first_K50'] for p in pa],
                        color=COLORS[c], alpha=0.12, lw=0)
        ax.plot(A, [p['P_f_first_K40'] for p in pa], color=COLORS[c], lw=2, marker='o', ms=4,
                label=f'{LABELS[c]}: K_mat 40 (band 36–50 MPa√m)')
    for y, txt in ((lim, f'limit load {lim:g} kN'), (lim_ff, f'limit × 1.15 = {lim_ff:g} kN')):
        ax.axhline(y, color=INK, lw=1.1, ls='--' if y == lim else ':')
        ax.text(0.4, y + 0.8, txt, fontsize=9, color=INK, va='bottom')
    w = d['cases']['gphi785']['per_a']['30']['P_f_first_K36']
    ax.annotate(f'weakest case {w:.1f} kN\n(a 30 mm, φ 7.85 %, K 36)', xy=(30, w), xytext=(21.5, 26),
                fontsize=8.5, color=INK, arrowprops={'arrowstyle': '-', 'color': MUTED, 'lw': 0.8})
    ax.set_xlim(0, 30.5)
    ax.set_ylim(0, 100)
    ax.set_xlabel('crack length a at the R10 fillet (mm)', color=INK)
    ax.set_ylabel('residual strength P_f (kN)', color=INK)
    ax.set_title('Residual strength of the cracked bracket (BS 7910 Option 1 FAD, 2D plane strain)',
                 fontsize=10, color=INK)
    ax.legend(fontsize=8.5, frameon=False, loc='upper right')
    style(ax)
    fig.tight_layout()
    fig.savefig(out / 'residual_strength.png', dpi=170)
    plt.close(fig)

    # 3. CL against load (sensitivity above limit load)
    loads = d['loads_kN']['sensitivity']
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    for c, v in d['cases'].items():
        cl = lambda k: [v['CL_mm'][f'first_K{k}_P{p:g}'] for p in loads]
        mid, lo, hi = cl(40), cl(36), cl(50)
        xs = [p for p, m in zip(loads, mid) if m is not None]
        ax.plot(xs, [m for m in mid if m is not None], color=COLORS[c], lw=2, marker='o', ms=4,
                label=f'{LABELS[c]}: K_mat 40')
        xb = [p for p, a, b in zip(loads, lo, hi) if a is not None]
        ax.fill_between(xb, [a for a in lo if a is not None], [b if b is not None else 30 for a, b in zip(lo, hi)
                                                                if a is not None], color=COLORS[c], alpha=0.10, lw=0)
    ax.axhline(30, color=MUTED, lw=0.8, ls=':')
    ax.text(80, 30.4, 'largest modelled crack, 30 mm', fontsize=8.5, color=MUTED, ha='right', va='bottom')
    ax.set_xlim(44, 81)
    ax.set_ylim(0, 33)
    ax.set_xlabel('applied pin load (kN), all above the 35.9 kN limit load', color=INK)
    ax.set_ylabel('critical flaw length CL (mm)', color=INK)
    ax.set_title('Sensitivity: critical flaw length against load (bands: K_mat 36–50 MPa√m)', fontsize=10, color=INK)
    ax.legend(fontsize=8.5, frameon=False, loc='lower left')
    style(ax)
    fig.tight_layout()
    fig.savefig(out / 'cl_vs_load.png', dpi=170)
    plt.close(fig)
    print('charts written to', out)


if __name__ == '__main__':
    main()
