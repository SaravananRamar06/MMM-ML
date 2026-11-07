"""Post-hoc control: the same network and training with Equation 1 switched off.

Answers "does the Johnson-Cook backbone help?" without changing the locked JC-PINN. The backbone is made
constant (B, C, q, r at their lower bounds, m at its upper bound, so every Equation 1 term is 1 within
1e-5 relative), and A is set to the fitting cases' mean stress: sigma = A * exp(delta). Everything else
(splits, 3 selection seeds, 5 final seeds, alpha, optimiser, lambda_phys = 0) matches the selected run.
This control was not part of the selection and cannot change the delivered model.
Usage: python scripts/control_no_equation.py [reports/jc_pinn_YYYYMMDD] [raw folder]
"""
import json
from pathlib import Path
import sys

import numpy as np

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
import jc_pinn as J  # noqa: E402

run = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'reports/jc_pinn_20261107'
raw = Path(sys.argv[2]) if len(sys.argv) > 2 else root / 'work/raw_from_committed_curves'
R = json.loads((run / 'results.json').read_text())
cfg = R['config']
grid = J.strain_grid(cfg)
split = json.loads((root / 'data/split.json').read_text())
train, test = np.array(split['train']), np.array(split['test'])
cand = dict(physics='none', lambda_phys=0.0, theta_mode='frozen')
b = cfg['calibration']['bounds']


def constant_backbone(mean_stress):
    v = np.array([mean_stress, b['beta'][0], 1.0, b['C'][0], b['m'][1], b['q'][0], b['r'][0]])
    return np.clip(v, [b[k][0] for k in J.CAL_VARS], [b[k][1] for k in J.CAL_VARS])


X, Y, _ = J.load_cases(raw, train, grid)
Cq = J.collocation(cfg)
sp = J.splits(X, train, cfg)
tasks = []
for si, s in enumerate(sp):
    Xq, yq = J.queries(X[s['fit']], grid), Y[s['fit']].ravel()
    xm, xs, ys = J.scalers(Xq, Y[s['fit']])
    tasks += [((si, seed), Xq, yq, J.queries(X[s['val']], grid), Cq, constant_backbone(yq.mean()), cfg, xm, xs, ys, cand, seed)
              for seed in cfg['selection']['seeds']]
out = J._run_tasks(tasks, 4, 'control selection splits')
logs = {}
for (si, seed), lp, _, _ in out:
    logs.setdefault(si, []).append(lp)
cv = np.empty_like(Y)
groups = []
for si, s in enumerate(sp):
    pr = np.exp(np.mean(logs[si], axis=0)).reshape(len(s['val']), len(grid))
    if s['kind'] == 'fold':
        cv[s['val']] = pr
    else:
        groups.append(dict(name=s['name'], temperature=s['temperature'], log10_rate=s['log10_rate'],
                           mean_rmse=J.scores(Y[s['val']], pr)['mean_rmse']))
cvm = J.scores(Y, cv)['mean_rmse']
gm = float(np.mean([g['mean_rmse'] for g in groups]))

Xq, yq = J.queries(X, grid), Y.ravel()
xm, xs, ys = J.scalers(Xq, Y)
final = J._run_tasks([(('final', seed), Xq, yq, Xq, Cq, constant_backbone(yq.mean()), cfg, xm, xs, ys, cand, seed)
                      for seed in cfg['final']['seeds']], 4, 'control final fit')
eq = dict(constants=cfg['constants'], x_mean=list(xm), x_scale=list(xs), members=[m for _, _, m, _ in sorted(final, key=lambda r: r[0][1])])
V, Z, _ = J.load_cases(raw, test, grid)
p = J.equation_predict(eq, J.queries(V, grid)).reshape(Z.shape)
test_scores = J.scores(Z, p)
backbone_spread = float(np.max(np.abs(J.jc_numpy(eq['members'][0]['theta'], Cq, cfg['constants']) / eq['members'][0]['theta'][0] - 1)))
sel = R['selection']['selected_trial']
result = dict(
    purpose='Post-hoc control: identical network and training with Equation 1 switched off (constant backbone). '
            'Not used for selection; the locked JC-PINN is unchanged.',
    backbone_max_relative_deviation_from_constant=backbone_spread,
    control=dict(cv_mean_rmse=cvm, group_mean_rmse=gm, score=0.5 * (cvm + gm), groups=groups,
                  test={k: test_scores[k] for k in ('mean_rmse', 'median_rmse', 'worst_rmse', 'mean_mae', 'mean_nrmse')}),
    jc_pinn=dict(cv_mean_rmse=sel['cv']['mean_rmse'], group_mean_rmse=sel['group_mean_rmse'], score=sel['score'],
                 test={k: R['test']['jc_pinn'][k] for k in ('mean_rmse', 'median_rmse', 'worst_rmse', 'mean_mae', 'mean_nrmse')}),
    caveat='The JC-PINN figures include selection among 14 settings using these same splits; the control had no selection.')
(run / 'control_no_equation.json').write_text(J.json_text(result))
print(J.json_text({k: v for k, v in result.items() if k != 'purpose'}))
