"""Regenerate every figure used by the course report, the paper and the presentation, from the saved run only.

Writes figures/<name>.pdf (vector, for LaTeX) and figures/<name>.png (for slides). No fitting, no test-set choices.
Usage: python scripts/make_figures.py
"""
import csv
import json
import os
from pathlib import Path
import sys

import numpy as np

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
import jc_pinn as J  # noqa: E402

os.environ.setdefault('MPLCONFIGDIR', str(root / 'work/matplotlib'))
import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch  # noqa: E402

RUN = root / 'reports/jc_pinn_20261107'
OUT = root / 'figures'
OUT.mkdir(exist_ok=True)
R = json.loads((RUN / 'results.json').read_text())
EQ = J.load_final_equation(root)
EO = json.loads((RUN / 'equation_only.json').read_text())
CTRL = json.loads((RUN / 'control_no_equation.json').read_text())
BASE = json.loads((RUN / 'baselines.json').read_text())
TS = json.loads((RUN / 'test_report/test_summary.json').read_text())
TRACE = json.loads((RUN / 'training_trace_member0.json').read_text())
man = {m['id']: m for m in json.loads((root / 'data/manifest.json').read_text())}
grid = J.strain_grid(R['config'])

INK, MUTED, MODEL, EQC, HI = '#18212b', '#5b6878', '#1d5ea8', '#a8620e', '#b5481f'
TCOL = {30.0: '#1d5ea8', 100.0: '#2f8a57', 200.0: '#b5481f'}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.titlesize': 9.5, 'axes.labelsize': 9,
                     'axes.edgecolor': '#9aa6b3', 'axes.grid': True, 'grid.color': '#e3e8ee', 'grid.linewidth': .7,
                     'legend.fontsize': 8, 'legend.frameon': False, 'savefig.bbox': 'tight', 'savefig.dpi': 220})


def curves(name, col):
    out = {}
    with (RUN / name).open() as f:
        for r in csv.DictReader(f):
            out.setdefault(int(r['id']), []).append(float(r[col]))
    return {k: np.array(v) for k, v in out.items()}


S_tr, S_te = curves('cv_predictions.csv', 'Svm'), curves('test_predictions.csv', 'Svm')
P_te, E1_te = curves('test_predictions.csv', 'JC_PINN'), curves('test_predictions.csv', 'equation_only')
theta_alone = list(EO['theta'].values())


def cond(i):
    m = man[i]
    return m['temperature'], m['log10_strain_rate'], m['density'], m['shear_modulus']


def save(fig, name):
    fig.savefig(OUT / f'{name}.pdf', metadata={'CreationDate': None})
    fig.savefig(OUT / f'{name}.png', metadata={'Software': None})
    plt.close(fig)
    print('wrote', name)


# 1. data overview -----------------------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5), sharey=True)
for ax, lr in zip(axes, (-5.0, -4.0, -3.0)):
    for i, y in S_tr.items():
        T, l, _, _ = cond(i)
        if l == lr:
            ax.plot(grid, y, color=TCOL[T], lw=1.1, alpha=.9)
    ax.set(title=f'strain rate $10^{{{int(lr)}}}$ s$^{{-1}}$', xlabel='$E_{11}$ (axial strain)', xlim=(0, .1), ylim=(0, 170))
    ax.set_xticks([0, .025, .05, .075, .1], ['0', '0.025', '0.05', '0.075', '0.1'])
axes[0].set_ylabel('$S_{vm}$ (MPa)')
for T, c in TCOL.items():
    axes[0].plot([], [], color=c, label=f'{T:g} °C')
axes[0].legend(loc='lower left')
save(fig, 'fig_data')

# 2. Equation 1 alone fails ---------------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4))
for ax, i in zip(axes, (2, 46, 60)):
    T, lr, rho, G = cond(i)
    X5 = np.c_[np.tile([T, lr, rho, G], (120, 1)), grid]
    p = J.jc_numpy(theta_alone, X5, EQ['constants'])
    ax.plot(grid, S_tr[i], color=INK, lw=1.8, label='simulation')
    ax.plot(grid, p, '--', color=EQC, lw=1.6, label='Equation 1 alone')
    ax.set(title=f'case {i}: {T:g} °C, $10^{{{int(lr)}}}$ s$^{{-1}}$', xlabel='$E_{11}$')
    ax.text(.97, .92, f'Eq. 1 off by {np.sqrt(np.mean((p - S_tr[i]) ** 2)):.1f} MPa', transform=ax.transAxes, ha='right', fontsize=7.5, color=EQC)
axes[0].set_ylabel('$S_{vm}$ (MPa)')
axes[0].legend(loc='lower left')
save(fig, 'fig_eq1_fail')

# 3. architecture ------------------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.2, 2.9))
ax.set_xlim(0, 100)
ax.set_ylim(0, 40)
ax.axis('off')


def box(x, y, w, h, text, ec, fc, size=8.2, weight='normal'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.6,rounding_size=1.2', ec=ec, fc=fc, lw=1.3))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=size, color=INK, weight=weight, linespacing=1.35)


def arrow(a, b, text=None, off=(0, 1.2)):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=9, lw=1.1, color=INK, shrinkA=0, shrinkB=0))
    if text:
        ax.text((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1], text, ha='center', fontsize=7.5, color=MUTED)


box(1, 12, 15, 16, 'Inputs\n$T$ (°C)\n$\\dot\\varepsilon$ (s$^{-1}$)\n$\\rho$ (kg m$^{-3}$)\n$G$ (MPa)\n$\\varepsilon=E_{11}$', '#9aa6b3', '#ffffff', 7.8)
box(24, 25, 38, 12, 'Equation 1 backbone $\\sigma_{JC}$\n$[A-B\\varepsilon^n][1+C\\ln\\dot\\varepsilon^*][1-T^{*m}]$\n$\\times(G/G_0)^q(1-\\phi)^r$   (7 bounded constants)', EQC, '#f8eedf', 7.6)
box(24, 2, 38, 12, 'Correction network $\\delta$\nstandardise $\\rightarrow$ 5$\\rightarrow$16$\\rightarrow$16$\\rightarrow$1, tanh\n385 weights, output layer starts at 0', MODEL, '#e4edf8', 7.6)
box(66, 13, 8, 8, '$\\times$', '#9aa6b3', '#ffffff', 12)
box(80, 10, 19, 14, 'Prediction\n$\\hat\\sigma=\\sigma_{JC}\\,e^{\\delta}$\ngeometric mean of\n5 trained copies', '#9aa6b3', '#ffffff', 7.8)
arrow((17.2, 20), (21, 20))
ax.plot([21, 21], [8, 31], color=INK, lw=1.1)
arrow((21, 31), (23.4, 31))
arrow((21, 8), (23.4, 8))
arrow((62.6, 31), (70, 31))
ax.plot([70, 70], [31, 21.6], color=INK, lw=1.1)
arrow((70, 22.4), (70, 21.7), None)
ax.text(65.2, 32.4, '$\\sigma_{JC}$', fontsize=8, color=EQC)
arrow((62.6, 8), (70, 8))
ax.plot([70, 70], [8, 12.4], color=INK, lw=1.1)
ax.text(65.2, 9.2, '$e^{\\delta}$', fontsize=8, color=MODEL)
arrow((74.6, 17), (79.4, 17))
save(fig, 'fig_architecture')

# 4. training trace ----------------------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.5), gridspec_kw=dict(width_ratios=[1.15, 1]))
h = np.array([[r[0], r[2]] for r in TRACE['hist'] if r[2]])
h = h[np.argsort(h[:, 0])]
ax = axes[0]
ax.axvspan(0, TRACE['adam_steps'], color='#e4edf8')
ax.semilogy(h[:, 0], h[:, 1], color=MODEL, lw=1.2)
ax.text(60, .12, 'Adam', fontsize=8, color=MUTED)
ax.text(TRACE['adam_steps'] + 80, .12, 'L-BFGS', fontsize=8, color=MUTED)
ax.set(xlabel='optimisation step', ylabel='training loss', title='Loss of copy 1 (seed 0)')
ax2 = axes[1]
k = [c['id'] for c in TRACE['cases']].index(64)
E = np.array(TRACE['E11'])
ax2.plot(E, TRACE['truth'][k], color=INK, lw=2, label='simulation')
for snap, ls, lab in ((TRACE['snaps'][0], '--', 'step 0 (Equation 1)'), (next(s for s in TRACE['snaps'] if s['step'] >= 400), ':', 'step 400'),
                      (TRACE['snaps'][-1], '-', f'final ({TRACE["snaps"][-1]["step"]} steps)')):
    ax2.plot(E, snap['curves'][k], ls, color=EQC if ls == '--' else MODEL, lw=1.4, label=lab)
ax2.set(xlabel='$E_{11}$', ylabel='$S_{vm}$ (MPa)', title='Training case 64 (200 °C, $10^{-4}$ s$^{-1}$)')
ax2.legend()
save(fig, 'fig_training')

# 5. selection heatmap -------------------------------------------------------------------------------------
tr = sorted(R['selection']['trials'], key=lambda t: t['score'])
lab = lambda c: ('no physics' if c['physics'] == 'none' else f"{c['physics']} λ={c['lambda_phys']:g}") + f", {c['theta_mode']}"
M = np.array([[t['cv']['mean_rmse']] + [g['metrics']['mean_rmse'] for g in t['groups']] for t in tr])
cols = ['CV'] + [f"{g['temperature']:g}°\n1e{g['log10_rate']:g}" for g in tr[0]['groups']]
fig, ax = plt.subplots(figsize=(7.2, 4.0))
im = ax.imshow(np.log(M), cmap='Blues', aspect='auto', vmin=np.log(.5), vmax=np.log(25))
for r in range(M.shape[0]):
    for c in range(M.shape[1]):
        ax.text(c, r, f'{M[r, c]:.1f}' if M[r, c] >= 10 else f'{M[r, c]:.2f}', ha='center', va='center', fontsize=6.4,
                color='white' if np.log(M[r, c]) > 1.8 else INK)
ax.set_xticks(range(len(cols)), cols, fontsize=7)
ax.set_yticks(range(len(tr)), [lab(t['candidate']) + f"   [{t['score']:.2f}]" for t in tr], fontsize=7)
ax.grid(False)
ax.add_patch(plt.Rectangle((-.5, -.5), M.shape[1], 1, fill=False, ec=HI, lw=1.8))
ax.set_title('Training-only selection: error (MPa) on what was hidden; [score]; row 1 selected')
save(fig, 'fig_selection')

# 6. parity, histogram and error along strain -----------------------------------------------------------------
test = R['test_ids']
Y = np.array([S_te[i] for i in test])
P = np.array([P_te[i] for i in test])
Err = P - Y
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4))
for T, c in TCOL.items():
    k = np.array([cond(i)[0] == T for i in test])
    if k.any():
        axes[0].scatter(Y[k].ravel(), P[k].ravel(), s=1.5, color=c, alpha=.5, label=f'{T:g} °C', rasterized=True)
axes[0].plot([0, 170], [0, 170], 'k--', lw=.8)
axes[0].set(xlim=(0, 170), ylim=(0, 170), xlabel='simulated $S_{vm}$ (MPa)', ylabel='predicted (MPa)',
            title=f"$R^2$ = {TS['summary']['points_summary']['r2']:.4f}")
axes[0].legend(markerscale=4)
axes[1].hist(Err.ravel(), bins=np.linspace(-3, 3, 61), color=MODEL)
axes[1].axvline(0, color='k', lw=.8)
axes[1].set(xlabel='prediction − simulation (MPa)', ylabel='points', title=f"{100 * TS['summary']['points_summary']['within_1']:.1f} % within ±1 MPa")
axes[2].plot(grid, np.abs(Err).mean(0), color=MODEL, label='mean |error|')
axes[2].plot(grid, Err.mean(0), color=EQC, label='mean signed error')
axes[2].axhline(0, color='k', lw=.7)
axes[2].set(xlabel='$E_{11}$', ylabel='MPa', title='Error along the curve')
axes[2].legend()
save(fig, 'fig_test_points')

# 7. best / median / worst test cases, and all 37 ---------------------------------------------------------
rm = np.sqrt(np.mean(Err ** 2, axis=1))
order = np.argsort(rm)
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5))
for ax, k, name in zip(axes, (order[0], order[len(order) // 2], order[-1]), ('best', 'median', 'worst')):
    i = test[k]
    T, lr, _, _ = cond(i)
    ax.plot(grid, Y[k], color=INK, lw=1.8, label='simulation')
    ax.plot(grid, E1_te[i], '--', color=EQC, lw=1.3, label='Equation 1 alone')
    ax.plot(grid, P[k], color=MODEL, lw=1.4, label='JC-PINN')
    ax.set_title(f'{name}: case {i}\n{T:g} °C, $10^{{{int(lr)}}}$ s$^{{-1}}$, RMSE {rm[k]:.2f} MPa', fontsize=8)
    ax.set_xlabel('$E_{11}$')
axes[0].set_ylabel('$S_{vm}$ (MPa)')
axes[0].legend(fontsize=7)
save(fig, 'fig_test_examples')

fig, axes = plt.subplots(7, 6, figsize=(7.2, 9.0), sharex=True, layout='constrained')
for ax in axes.flat[len(test):]:
    ax.axis('off')
for ax, k, i in zip(axes.flat, range(len(test)), test):
    T, lr, rho, _ = cond(i)
    ax.plot(grid, Y[k], color=INK, lw=1.6)
    ax.plot(grid, P[k], '--', color=MODEL, lw=1.2)
    ax.set_title(f'case {i}: {T:g} °C, 1e{int(lr)}', fontsize=6, pad=2)
    ax.text(.96, .9, f'{rm[k]:.2f}', transform=ax.transAxes, ha='right', va='top', fontsize=6.5, color=MODEL)
    ax.tick_params(labelsize=5, pad=1, length=2)
    ax.set_xticks([0, .05, .1], ['0', '.05', '.1'])
axes.flat[len(test)].plot([], [], color=INK, lw=1.6, label='simulation')
axes.flat[len(test)].plot([], [], '--', color=MODEL, lw=1.2, label='JC-PINN')
axes.flat[len(test)].legend(loc='center', fontsize=7, frameon=False)
fig.supxlabel('$E_{11}$', fontsize=8)
fig.supylabel('$S_{vm}$ (MPa)', fontsize=8)
save(fig, 'fig_test_cases')

# 8. unseen temperature/rate groups ------------------------------------------------------------------------
sel = R['selection']['selected_trial']['groups']
names = [f"{g['temperature']:g} °C\n1e{g['log10_rate']:g}" for g in sel]
series = [('Equation 1 alone', [g['metrics']['mean_rmse'] for g in R['selection']['equation_only']['groups']], EQC),
          ('JC-PINN', [g['metrics']['mean_rmse'] for g in sel], MODEL),
          ('same network, Eq. 1 off', [g['mean_rmse'] for g in CTRL['control']['groups']], '#8a96a3'),
          ('single MLP (2 Nov)', [g['mean_rmse'] for g in BASE['single_mlp']['groups']], '#c8d0da')]
fig, ax = plt.subplots(figsize=(7.2, 2.6))
w = .2
for k, (n, v, c) in enumerate(series):
    ax.bar(np.arange(9) + (k - 1.5) * w, v, w, color=c, label=f'{n} (mean {np.mean(v):.2f})')
ax.set_xticks(range(9), names, fontsize=7.5)
ax.set(ylabel='mean curve RMSE (MPa)', title='Hiding a whole temperature/rate group (training cases only)')
ax.set_ylim(0, 62)
ax.legend(ncol=2, loc='upper left')
save(fig, 'fig_groups')

# 9. model comparison on the 37 test cases -----------------------------------------------------------------
C = TS['summary']['comparison']
rows = [('Equation 1 alone', C['equation_only'], EQC), ('curve-copy baseline', C['lookup'], '#8a96a3'), ('JC-PINN (this work)', C['jc_pinn'], MODEL),
        ('same network, Eq. 1 off', C['control_no_equation'], '#8a96a3'), ('single MLP (2 Nov)', C['single_mlp'], '#c8d0da'),
        ('5-network MLP (24 Oct)', C['ensemble_mlp'], '#c8d0da')]
fig, ax = plt.subplots(figsize=(7.2, 2.4))
ax.barh(range(len(rows))[::-1], [r[1] for r in rows], color=[r[2] for r in rows])
for k, r in enumerate(rows):
    ax.text(r[1] * 1.08, len(rows) - 1 - k, f'{r[1]:.3f}', va='center', fontsize=8)
ax.set_yticks(range(len(rows))[::-1], [r[0] for r in rows])
ax.set_xscale('log')
ax.set(xlabel='mean curve RMSE on the 37 test cases (MPa, log scale)', xlim=(.03, 20))
save(fig, 'fig_comparison')

# 10. predictions at the 4 % porosity study point ----------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4), sharey=True)
for ax, rate in zip(axes, (1e-5, 1e-4, 1e-3)):
    for T in (30.0, 100.0, 200.0, 300.0):
        g, s = J.predict_curves(EQ, [[T, rate, 2592.0, 24541.0]])
        ax.plot(g, s[0], '--' if T > 200 else '-', color=TCOL.get(T, '#8a96a3'), lw=1.4, label=f'{T:g} °C' + (' (no data)' if T > 200 else ''))
    ax.set(title=f'φ = 4 %, $\\dot\\varepsilon$ = {rate:g} s$^{{-1}}$', xlabel='$E_{11}$')
axes[0].set_ylabel('predicted $S_{vm}$ (MPa)')
axes[2].legend(loc='lower left')
save(fig, 'fig_study_point')
