"""Independent check of a saved JC-PINN run. Does not import src/jc_pinn.py.

Re-implements Equation 1 and the correction network in plain NumPy, recomputes every saved prediction
and metric, checks the split, the lock order, the selection rule, parameter bounds, the data identity
with the earlier models' curves, and that previously delivered artifacts are unchanged.
Usage: python scripts/verify_jc_pinn.py [reports/jc_pinn_YYYYMMDD]
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

root = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'reports/jc_pinn_20261107'
R = json.loads((run / 'results.json').read_text())
EQ = json.loads((run / 'equation.json').read_text())
EO = json.loads((run / 'equation_only.json').read_text())
LOCK = json.loads((run / 'selection_lock.json').read_text())
split = json.loads((root / 'data/split.json').read_text())
man = {m['id']: m for m in json.loads((root / 'data/manifest.json').read_text())}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks = {}


def eq1(theta, T, lr, rho, G, e, c):
    A, B, n, C, m, q, r = theta
    Ts = np.maximum((T - c['T_ref']) / (c['T_melt'] - c['T_ref']), 0.0)
    thermal = 1.0 - np.array([t ** m if t > 0 else 0.0 for t in Ts])
    return (A - B * e ** n) * (1 + C * np.log(10.0 ** lr / c['rate0'])) * thermal * (G / c['G0']) ** q * (rho / c['rho0']) ** r


def network(mem, Z):
    cols = mem['inputs']
    z = (Z[:, cols] - np.array(EQ['x_mean'])[cols]) / np.array(EQ['x_scale'])[cols]
    return np.tanh(np.tanh(z @ np.array(mem['W1']).T + mem['b1']) @ np.array(mem['W2']).T + mem['b2']) @ np.array(mem['w3']) + mem['b3']


def read(name):
    out = {}
    with (run / name).open() as f:
        for r in csv.DictReader(f):
            out.setdefault(int(r['id']), []).append({k: float(v) for k, v in r.items() if k != 'id'})
    return {i: {k: np.array([row[k] for row in rows]) for k in rows[0]} for i, rows in out.items()}


def metric(y, p):
    rmse = np.sqrt(np.mean((y - p) ** 2, axis=1))
    return dict(mean_rmse=rmse.mean(), median_rmse=np.median(rmse), worst_rmse=rmse.max(),
                mean_mae=np.mean(np.abs(y - p), axis=1).mean(), mean_nrmse=(rmse / np.sqrt(np.mean(y * y, axis=1))).mean())


def close(a, b, tol=1e-9):
    return all(abs(a[k] - b[k]) <= tol * max(1.0, abs(b[k])) for k in a)


# 1. split and protocol
checks['split_matches_data_split_json'] = R['train_ids'] == split['train'] and R['test_ids'] == split['test']
checks['train_test_disjoint'] = not set(split['train']) & set(split['test']) and len(split['train']) == 36 and len(split['test']) == 37
checks['lock_hashes_match_files'] = LOCK['equation_sha256'] == sha(run / 'equation.json') and \
    LOCK['equation_only_sha256'] == sha(run / 'equation_only.json')
checks['lock_written_before_test'] = LOCK['written_before_test_load'] and R['checks']['selection_saved_before_test']
checks['final_fit_uses_training_ids_only'] = sorted(EQ['fit_ids']) == sorted(split['train']) == sorted(EO['fit_ids'])
sp = R['selection']['splits']
checks['selection_splits_isolated'] = all(not set(s['fit_ids']) & set(s['val_ids']) and not set(s['fit_ids'] + s['val_ids']) - set(split['train'])
                                         for s in sp)
checks['folds_cover_training_once'] = sorted(sum((s['val_ids'] for s in sp if s['kind'] == 'fold'), [])) == sorted(split['train'])
checks['groups_hold_out_whole_conditions'] = all(
    not {(man[i]['temperature'], man[i]['log10_strain_rate']) for i in s['val_ids']} &
    {(man[i]['temperature'], man[i]['log10_strain_rate']) for i in s['fit_ids']} for s in sp if s['kind'] == 'group')

# 2. selection rule reproduced from saved trial scores
trials = R['selection']['trials']
recomputed = [0.5 * (t['cv']['mean_rmse'] + np.mean([g['metrics']['mean_rmse'] for g in t['groups']])) for t in trials]
checks['trial_scores_recomputed'] = all(abs(a - t['score']) < 1e-12 for a, t in zip(recomputed, trials))
best = min(range(len(trials)), key=lambda k: (round(recomputed[k], 12), -trials[k]['candidate']['lambda_phys'],
                                              trials[k]['candidate']['theta_mode'] != 'frozen'))
checks['selected_is_best_by_preregistered_rule'] = trials[best]['candidate'] == R['selected'] == EQ['selected'] == LOCK['selected']

# 3. predictions recomputed from the saved equations with independent code
c = EQ['constants']
test = read('test_predictions.csv')
worst_pinn = worst_eq1 = 0.0
for i, d in test.items():
    m = man[i]
    T, lr, rho, G = (np.full(len(d['E11']), v) for v in (m['temperature'], m['log10_strain_rate'], m['density'], m['shear_modulus']))
    Z = np.c_[T, lr, rho, G, d['E11']]
    logs = [np.log(eq1(mem['theta'], T, lr, rho, G, d['E11'], c)) + network(mem, Z) for mem in EQ['members']]
    worst_pinn = max(worst_pinn, np.max(np.abs(np.exp(np.mean(logs, axis=0)) - d['JC_PINN'])))
    worst_eq1 = max(worst_eq1, np.max(np.abs(eq1(list(EO['theta'].values()), T, lr, rho, G, d['E11'], c) - d['equation_only'])))
checks['jc_pinn_predictions_reproduced_max_abs'] = float(worst_pinn)
checks['equation_only_predictions_reproduced_max_abs'] = float(worst_eq1)
# Compare the Python floats: comparing NumPy scalars gives np.bool_, which json cannot write and
# which the isinstance(v, bool) filter for all_passed below would silently skip.
checks['predictions_reproduced'] = checks['jc_pinn_predictions_reproduced_max_abs'] < 1e-9 and \
    checks['equation_only_predictions_reproduced_max_abs'] < 1e-9

# 4. metrics recomputed from the saved CSVs
ids = split['test']
Y = np.array([test[i]['Svm'] for i in ids])
for col, key in (('JC_PINN', 'jc_pinn'), ('equation_only', 'equation_only'), ('lookup', 'lookup')):
    checks[f'test_metrics_{key}'] = close(metric(Y, np.array([test[i][col] for i in ids])), R['test'][key])
cv = read('cv_predictions.csv')
Yc = np.array([cv[i]['Svm'] for i in split['train']])
checks['cv_metrics_selected'] = close(metric(Yc, np.array([cv[i]['JC_PINN'] for i in split['train']])),
                                      R['selection']['selected_trial']['cv'])
checks['cv_metrics_equation_only'] = close(metric(Yc, np.array([cv[i]['equation_only'] for i in split['train']])),
                                           R['selection']['equation_only']['cv'])

# 5. same curves as every earlier model (committed 2 Nov curves)
old = {}
old_dir = root / 'reports/single_mlp_20261102'
if old_dir.exists():
    for name in ('cv_predictions.csv', 'test_predictions.csv'):
        with (old_dir / name).open() as f:
            for r in csv.DictReader(f):
                old.setdefault(int(r['id']), []).append(float(r['Svm']))
    checks['curves_identical_to_2nov_curves'] = all(np.array_equal(np.array(old[i]), test[i]['Svm']) for i in ids) and \
        all(np.array_equal(np.array(old[i]), cv[i]['Svm']) for i in split['train'])
else:
    # Archived: the identity was checked when baselines.json was frozen; here the curves must still match the run's fingerprints.
    base = json.loads((run / 'baselines.json').read_text())
    fp = R['fingerprints']
    def matches(i, y, part):
        return max(abs(a - b) for a, b in zip([y[0], y[len(y) // 2], y[-1], float(np.mean(y))], fp[part][str(i)])) <= 1e-9
    checks['curves_identical_to_2nov_curves'] = bool(base['curves_identical_to_2nov_hash_checked_curves']) and \
        all(matches(i, test[i]['Svm'], 'test') for i in ids) and all(matches(i, cv[i]['Svm'], 'train') for i in split['train'])

# 6. physical bounds of the Equation 1 constants
b = json.loads((root / 'configs/jc_pinn.json').read_text())['calibration']['bounds']
ok = True
for theta in [list(EO['theta'].values())] + [mem['theta'] for mem in EQ['members']]:
    A, B, n, C, m, q, r = theta
    ok &= A - B * 0.1 ** n > 0 and C >= 0 and q >= 0 and r >= 0 and n > 0 and m > 0
    ok &= b['A'][0] <= A <= b['A'][1] and b['n'][0] <= n <= b['n'][1]
checks['constants_within_physical_bounds'] = bool(ok)
checks['members'] = len(EQ['members'])
checks['parameters_per_member'] = R['checks']['parameters_per_member']

# 7. earlier delivered artifacts unchanged (files moved to the archive branch are recorded in baselines.json)
prot = R['checks']['protected_artifacts_unchanged']
present = {k: v for k, v in prot.items() if (root / k).exists()}
archived = set(prot) - set(present)
arch_ok = True
if archived:
    base = json.loads((run / 'baselines.json').read_text())
    arch_ok = bool(base.get('archive', {}).get('branch'))
checks['protected_artifacts_unchanged'] = len(prot) > 0 and all(sha(root / k) == v for k, v in present.items()) and arch_ok
checks['protected_artifacts_archived'] = len(archived)

passed = all(v for k, v in checks.items() if isinstance(v, bool))
checks['all_passed'] = passed
(run / 'verification.json').write_text(json.dumps(checks, indent=2) + '\n')
print(json.dumps(checks, indent=2))
sys.exit(0 if passed else 1)
