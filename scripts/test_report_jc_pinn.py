"""Full test report for the locked JC-PINN on the 37 held-out simulations (no refitting, no new choices).

Checks the saved equation against its selection lock, recomputes predictions from equation.json, and breaks
the test errors down by case, condition, strain range and size; compares with every earlier model on the
same cases; measures the spread of the five members; writes figures, tables, a JSON summary and the data
bundle for the test-results video.
Usage: python scripts/test_report_jc_pinn.py [reports/jc_pinn_YYYYMMDD]
"""
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
import jc_pinn as J  # noqa: E402

run = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'reports/jc_pinn_20261107'
out = run / 'test_report'
out.mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
lock = json.loads((run / 'selection_lock.json').read_text())
assert sha(run / 'equation.json') == lock['equation_sha256'], 'equation.json does not match its lock'
EQ = json.loads((run / 'equation.json').read_text())
EO = json.loads((run / 'equation_only.json').read_text())
R = json.loads((run / 'results.json').read_text())
split = json.loads((root / 'data/split.json').read_text())
man = {m['id']: m for m in json.loads((root / 'data/manifest.json').read_text())}
test = split['test']
grid = J.strain_grid(R['config'])

truth = {}
with (run / 'test_predictions.csv').open() as f:
    for r in csv.DictReader(f):
        truth.setdefault(int(r['id']), []).append(float(r['Svm']))
Y = np.array([truth[i] for i in test])
X = np.array([[man[i]['temperature'], man[i]['log10_strain_rate'], man[i]['density'], man[i]['shear_modulus']] for i in test])
Q = J.queries(X, grid)
P = J.equation_predict(EQ, Q).reshape(Y.shape)
members = np.array([J.equation_predict(dict(EQ, members=[m]), Q) for m in EQ['members']]).reshape(len(EQ['members']), *Y.shape)
P_eq1 = J.jc_numpy(list(EO['theta'].values()), Q, EO['constants']).reshape(Y.shape)
X_train = np.array([[man[i]['temperature'], man[i]['log10_strain_rate'], man[i]['density'], man[i]['shear_modulus']] for i in split['train']])
tr = {}
with (run / 'cv_predictions.csv').open() as f:
    for r in csv.DictReader(f):
        tr.setdefault(int(r['id']), []).append(float(r['Svm']))
P_lookup = J.lookup(X_train, np.array([tr[i] for i in split['train']]), X)
saved = J.scores(Y, P)
assert abs(saved['mean_rmse'] - R['test']['jc_pinn']['mean_rmse']) < 1e-9, 'recomputed test score differs from the locked run'

# other models' per-case test errors on the same 37 cases
single = {}
with (root / 'reports/single_mlp_20261102/test_predictions.csv').open() as f:
    for r in csv.DictReader(f):
        single.setdefault(int(r['id']), []).append(float(r['MLP']))
P_single = np.array([single[i] for i in test])
ens_case = json.loads((root / 'runs/score/final_Svm/metrics.json').read_text())['per_case']
case_rmse = lambda A: np.sqrt(np.mean((A - Y) ** 2, axis=1))

E = P - Y
rel = E / Y
rm, rm_eq1, rm_lookup, rm_single = case_rmse(P), case_rmse(P_eq1), case_rmse(P_lookup), case_rmse(P_single)
rm_ens = np.array([ens_case[str(i)] for i in test])
spread = members.std(0)
ss_res, ss_tot = float(np.sum(E ** 2)), float(np.sum((Y - Y.mean()) ** 2))
cases = []
for k, i in enumerate(test):
    m = man[i]
    cases.append(dict(id=i, T=m['temperature'], log10_rate=m['log10_strain_rate'], density=m['density'], G=m['shear_modulus'],
                      porosity_pct=round(100 * (1 - m['density'] / 2700), 2), rmse=rm[k], mae=float(np.mean(np.abs(E[k]))),
                      max_abs=float(np.max(np.abs(E[k]))), bias=float(E[k].mean()), nrmse_pct=float(100 * rm[k] / np.sqrt(np.mean(Y[k] ** 2))),
                      member_spread=float(spread[k].mean()), rmse_eq1=rm_eq1[k], rmse_lookup=rm_lookup[k], rmse_single_mlp=rm_single[k],
                      rmse_ensemble_mlp=rm_ens[k]))
conds = []
for T, lr in sorted(set(map(tuple, X[:, :2]))):
    k = (X[:, 0] == T) & (X[:, 1] == lr)
    conds.append(dict(T=T, log10_rate=lr, cases=int(k.sum()), rmse=float(rm[k].mean()), eq1=float(rm_eq1[k].mean()), single=float(rm_single[k].mean())))
bands = [(0, 40, '0.0002-0.033'), (40, 80, '0.034-0.067'), (80, 120, '0.068-0.0999')]
summary = dict(
    model='JC-PINN, locked 7 Nov 2026', equation_sha256=lock['equation_sha256'], lock_verified=True, refitted=False,
    cases=len(test), points=int(E.size),
    curve_rmse=dict(mean=float(rm.mean()), median=float(np.median(rm)), worst=float(rm.max()), worst_case=int(test[int(rm.argmax())]),
                    best=float(rm.min()), best_case=int(test[int(rm.argmin())])),
    points_summary=dict(mean_signed=float(E.mean()), mae=float(np.abs(E).mean()), max_abs=float(np.abs(E).max()),
                        mean_abs_pct=float(100 * np.abs(rel).mean()), max_abs_pct=float(100 * np.abs(rel).max()),
                        within_0p5=float(np.mean(np.abs(E) <= 0.5)), within_1=float(np.mean(np.abs(E) <= 1)), within_2=float(np.mean(np.abs(E) <= 2)),
                        r2=1 - ss_res / ss_tot),
    bias=dict(cases_high=int((E.mean(1) > 0).sum()), cases_low=int((E.mean(1) < 0).sum())),
    strain_bands=[dict(band=n, mean_signed=float(E[:, a:b].mean()), mae=float(np.abs(E[:, a:b]).mean())) for a, b, n in bands],
    conditions=conds,
    members=dict(mean_spread=float(spread.mean()), max_spread=float(spread.max()), single_member_rmse=[float(case_rmse(m).mean()) for m in members]),
    comparison=dict(jc_pinn=float(rm.mean()), equation_only=float(rm_eq1.mean()), lookup=float(rm_lookup.mean()), single_mlp=float(rm_single.mean()),
                    ensemble_mlp=float(rm_ens.mean()), control_no_equation=json.loads((run / 'control_no_equation.json').read_text())['control']['test']['mean_rmse'],
                    beats_equation_only=int((rm < rm_eq1).sum()), beats_lookup=int((rm < rm_lookup).sum()), beats_single_mlp=int((rm < rm_single).sum()),
                    beats_ensemble_mlp=int((rm < rm_ens).sum())),
    caveat='The 37 test cases were explored in earlier project stages, so this is not a blind test. Agreement is with simulations, '
           'not experiments; stress units are inferred as MPa. No setting was chosen using these results.')
(out / 'test_summary.json').write_text(J.json_text(dict(summary=summary, cases=cases)))
with (out / 'per_case.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(cases[0]))
    w.writeheader()
    w.writerows([{k: (round(v, 6) if isinstance(v, float) else v) for k, v in c.items()} for c in cases])

# ------------------------------------------------------------------ figures
import os  # noqa: E402
os.environ.setdefault('MPLCONFIGDIR', str(root / 'work/matplotlib'))
import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
colT = {30.0: '#1d5ea8', 100.0: '#2f8a57', 200.0: '#b5481f'}
order = np.argsort(rm)
fig, axes = plt.subplots(5, 8, figsize=(20, 12.5), sharex=True)
for ax in axes.flat[len(test):]:
    ax.axis('off')
for n, k in enumerate(order):
    ax = axes.flat[n]
    ax.plot(grid, Y[k], color='k', lw=1.6)
    ax.plot(grid, P[k], color=colT[X[k, 0]], lw=1.4)
    ax.set_title(f'#{test[k]} {X[k, 0]:g}°C 1e{X[k, 1]:g}: {rm[k]:.2f}', fontsize=9)
    ax.tick_params(labelsize=7)
fig.suptitle('All 37 test cases, best to worst (black = simulation, colour = JC-PINN by temperature; title = curve RMSE, MPa)', fontsize=13)
fig.tight_layout()
fig.savefig(out / 'all_test_cases.png', dpi=110)
plt.close(fig)

fig, axes = plt.subplots(1, 3, figsize=(17, 5))
ax = axes[0]
for T, c in colT.items():
    k = X[:, 0] == T
    ax.scatter(Y[k].ravel(), P[k].ravel(), s=3, color=c, alpha=.5, label=f'{T:g} °C')
lim = [0, 170]
ax.plot(lim, lim, 'k--', lw=1)
ax.set(xlim=lim, ylim=lim, xlabel='Simulated Svm (MPa)', ylabel='Predicted Svm (MPa)', title=f'Parity, 4,440 test points (R² = {summary["points_summary"]["r2"]:.5f})')
ax.legend()
ax = axes[1]
ax.hist(E.ravel(), bins=np.linspace(-3, 3, 61), color='#1d5ea8')
ax.axvline(0, color='k', lw=1)
ax.set(xlabel='Prediction − simulation (MPa)', ylabel='points', title=f'Point errors: {100 * summary["points_summary"]["within_1"]:.1f} % within ±1 MPa')
ax = axes[2]
ax.plot(grid, np.abs(E).mean(0), color='#1d5ea8', label='mean |error|')
ax.plot(grid, E.mean(0), color='#a8620e', label='mean signed error')
ax.fill_between(grid, np.percentile(np.abs(E), 90, axis=0), 0, color='#1d5ea8', alpha=.12, label='90th percentile |error|')
ax.axhline(0, color='k', lw=.8)
ax.set(xlabel='E11', ylabel='MPa', title='Error along the strain axis')
ax.legend()
fig.tight_layout()
fig.savefig(out / 'parity_histogram_strain.png', dpi=130)
plt.close(fig)

fig, ax = plt.subplots(figsize=(11, 4.5))
names = ['Equation 1 alone', 'Curve-copy baseline', 'JC-PINN', 'Same network,\nEq. 1 off', 'Single MLP', '5-net MLP']
vals = [summary['comparison'][k] for k in ('equation_only', 'lookup', 'jc_pinn', 'control_no_equation', 'single_mlp', 'ensemble_mlp')]
ax.bar(names, vals, color=['#a8620e', '#8a96a3', '#1d5ea8', '#8a96a3', '#8a96a3', '#8a96a3'])
ax.set_yscale('log')
for x, v in enumerate(vals):
    ax.text(x, v * 1.08, f'{v:.3f}', ha='center')
ax.set(ylabel='Mean curve RMSE on 37 test cases (MPa, log)', title='Same 37 test cases, every model')
fig.tight_layout()
fig.savefig(out / 'model_comparison.png', dpi=130)
plt.close(fig)

# ------------------------------------------------------------------ video bundle
video = dict(grid=[round(float(g), 6) for g in grid], cases=[dict(c, S=[round(float(v), 3) for v in Y[k]], P=[round(float(v), 3) for v in P[k]],
             EQ1=[round(float(v), 3) for v in P_eq1[k]], spread=[round(float(v), 4) for v in spread[k]],
             M=[[round(float(v), 3) for v in members[j, k]] for j in range(len(members))]) for k, c in enumerate(cases)],
             summary=summary, train_ids=split['train'], test_ids=test, lock_sha=lock['equation_sha256'][:12],
             all_cases={int(i): dict(T=m['temperature'], lr=m['log10_strain_rate']) for i, m in man.items()})
(out / 'video_bundle.json').write_text(json.dumps(video, separators=(',', ':')))
s = summary
print(json.dumps({k: s[k] for k in ('curve_rmse', 'points_summary', 'bias', 'members', 'comparison')}, indent=1))
