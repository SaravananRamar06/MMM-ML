"""Training-case-only qualification of effective scalar response hypotheses.

Svm = R + A exp(-k x**n), x=E11/0.1. These are softening adaptations,
not identified microscopic laws; E11 is an operational loading coordinate.
This module deliberately does not call data.build (which opens all cases).
"""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import argparse
import csv
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares
from scipy.special import expit, logit
from sklearn.model_selection import KFold

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_training(raw, split_path, grid, expected_train=36, expected_test=37):
    """Open only paths explicitly whitelisted by split.train; audit each source."""
    raw = Path(raw)
    split = json.loads(Path(split_path).read_text())
    ids, test = split['train'], split['test']
    if (len(ids) != expected_train or len(test) != expected_test or
            len(set(ids)) != len(ids) or len(set(test)) != len(test) or set(ids) & set(test)):
        raise ValueError('Invalid/disjoint training split')
    with (raw / 'simulation_matrix.csv').open() as f:
        matrix = {int(r['Simulation_ID']): r for r in csv.DictReader(f)}
    X, Y, audits = [], [], []
    for case in ids:
        path = raw / f'simulation_{case:04d}' / 'STR_STR.OUT'
        columns = 'TIME Evm Svm E11 E22 E33 E23 E13 E12 SCAU11 SCAU22 SCAU33 SCAU23 SCAU13 SCAU12 TEMP'.split()
        with path.open() as f:
            if f.readline().split() != columns:
                raise ValueError(f'Unexpected source columns: {case}')
        a = np.loadtxt(path, skiprows=1)
        if a.shape[1] != 16 or not np.isfinite(a).all() or not np.all(np.diff(a[:, 3]) > 0):
            raise ValueError(f'Invalid history: {case}')
        if grid[0] < a[0, 3] or grid[-1] > a[-1, 3]:
            raise ValueError(f'Extrapolation requested: {case}')
        r = matrix[case]
        X.append([float(r['temperature']), np.log10(float(r['strain_rate'])),
                  float(r['density']), float(r['shear_modulus'])])
        Y.append(np.interp(grid, a[:, 3], a[:, 2]))
        e, s = a[:, 3:9], a[:, 9:15]
        vm = np.sqrt(.5 * ((s[:, 0]-s[:, 1])**2 + (s[:, 1]-s[:, 2])**2
                          + (s[:, 2]-s[:, 0])**2) + 3*(s[:, 3:]**2).sum(1))
        de = np.diff(e, axis=0)
        dw = (s[1:, :3]*de[:, :3]).sum(1) + 2*(s[1:, 3:]*de[:, 3:]).sum(1)
        reconstructed = a[0, 1] + np.cumsum(dw/a[1:, 2])
        audits.append(dict(id=case, rows=len(a), sha256=digest(path),
                           svm_relative_error=float(np.max(np.abs(vm-a[:, 2])/a[:, 2])),
                           evm_work_reconstruction_max_error=float(np.max(np.abs(reconstructed-a[1:, 1]))),
                           evm_reversals=int(np.sum(np.diff(a[:, 1]) < 0)),
                           negative_work_increments=int(np.sum(dw < -1e-10)),
                           temperature_offset=float(np.median(a[:, 15])-float(r['temperature']))))
    return np.array(ids), np.array(X), np.array(Y), audits, split


def basis(X, mean, scale):
    z = (np.asarray(X)-mean)/scale
    return np.column_stack([np.ones(len(z)), z, z[:, 0]*z[:, 1]])


def response(beta, B, strain, family, stress_scale=1., reference=.1, jacobian=False):
    """Positive log-linear R,A,k; n in (0.1,8) by logistic mapping."""
    count = 3 if family == 'exponential' else 4
    beta = np.asarray(beta).reshape(count, B.shape[1])
    q = B @ beta.T
    R, A, k = np.exp(q[:, :3]).T
    n = np.ones(len(B)) if count == 3 else .1+7.9*expit(q[:, 3])
    u = np.asarray(strain)/reference
    if np.any(u <= 0):
        raise ValueError('Positive strain required; zero is outside qualified domain')
    power = u[None, :]**n[:, None]
    z = k[:, None]*power
    damp = np.exp(-np.minimum(z, 700.))
    excess = A[:, None]*damp
    pred = (R[:, None]+excess)*stress_scale
    if not jacobian:
        return pred
    dz = np.where(z < 700., z, 0.)
    factors = [np.broadcast_to(R[:, None], z.shape), excess, -excess*dz]
    if count == 4:
        dn = 7.9*expit(q[:, 3])*(1-expit(q[:, 3]))
        factors.append(-excess*dz*np.log(u)[None, :]*dn[:, None])
    J = np.concatenate([(v[:, :, None]*B[:, None, :]).reshape(-1, B.shape[1])
                        for v in factors], axis=1)*stress_scale
    return pred, J


def fit_global(X, Y, strain, family, alpha, config):
    mean, scale = X.mean(0), X.std(0)
    scale = np.where(scale > 0, scale, 1.)
    B = basis(X, mean, scale)
    stress_scale = float(np.sqrt(np.mean(Y**2)))
    yn = Y/stress_scale
    count = 3 if family == 'exponential' else 4
    mask = np.tile([0., 1., 1., 1., 1., 1.], count)
    norm = np.sqrt(Y.size)

    def fun(v):
        p = response(v, B, strain, family, reference=config['strain_reference'])
        return np.r_[(p-yn).ravel()/norm, np.sqrt(alpha)*mask*v]

    def jac(v):
        _, J = response(v, B, strain, family, reference=config['strain_reference'], jacobian=True)
        return np.vstack([J/norm, np.diag(np.sqrt(alpha)*mask)])

    starts, fitted = [], []
    for seed in range(config['starts']):
        b = np.random.default_rng(seed).normal(0, .08, (count, 6))
        b[:3, 0] = [np.log(.2), np.log(.9), np.log([.5, 1., 2.][seed % 3])]
        if count == 4:
            b[3, 0] = logit(([1., 1.5, 2.][seed % 3]-.1)/7.9)
        # Set intercept separately because the flexible family has four rows.
        initial = b.ravel()
        fit = least_squares(fun, initial, jac=jac, bounds=(-8, 8),
                            max_nfev=config['max_nfev'], ftol=1e-10, xtol=1e-10, gtol=1e-9)
        fitted.append(fit)
        starts.append(dict(seed=seed, cost=float(fit.cost), success=bool(fit.success),
                           evaluations=fit.nfev, optimality=float(fit.optimality)))
    best = min(fitted, key=lambda f: f.cost)
    pbest = response(best.x, B, strain, family, reference=config['strain_reference'])
    spread = max(float(np.sqrt(np.mean((response(f.x, B, strain, family,
                 reference=config['strain_reference'])-pbest)**2))) for f in fitted)
    sv = np.linalg.svd(jac(best.x)[:Y.size], compute_uv=False)
    return dict(family=family, alpha=alpha, mean=mean.tolist(), scale=scale.tolist(),
                stress_scale=stress_scale, beta=best.x.reshape(count, 6).tolist(),
                reference=config['strain_reference'], starts=starts,
                success=bool(best.success), initialization_prediction_spread_relative_rms=spread,
                data_jacobian_condition=float(sv[0]/max(sv[-1], 1e-300)))


def predict(model, X, strain):
    return response(model['beta'], basis(X, np.array(model['mean']), np.array(model['scale'])),
                    strain, model['family'], model['stress_scale'], model['reference'])


def metrics(Y, prediction):
    rmse = np.sqrt(np.mean((prediction-Y)**2, axis=1))
    nrmse = rmse/np.sqrt(np.mean(Y**2, axis=1))
    return dict(mean_rmse=float(rmse.mean()), worst_rmse=float(rmse.max()),
                mean_nrmse=float(nrmse.mean()), worst_nrmse=float(nrmse.max()),
                case_rmse=rmse.tolist(), case_nrmse=nrmse.tolist())


def fit_shape(y, strain, family):
    u = strain/.1
    def fun(v, at=u):
        n = 1. if family == 'exponential' else v[3]
        return v[0]+v[1]*np.exp(-v[2]*at**n)
    count = 3 if family == 'exponential' else 4
    fits = []
    for k, n in [(1., 1.), (2., 2.), (5., 3.)]:
        initial = [max(y[-1]*.3, .01), max(y[0]-y[-1]*.3, .01), k]
        if count == 4:
            initial.append(n)
        f = least_squares(lambda v: fun(v)-y, initial,
                          bounds=([0, 0, 1e-6]+([.1] if count == 4 else []),
                                  [1000, 1000, 100]+([8] if count == 4 else [])),
                          x_scale='jac', max_nfev=2500, ftol=1e-10, xtol=1e-10, gtol=1e-10)
        fits.append(f)
    best = min(fits, key=lambda f: np.sum(f.fun**2))
    singular = np.linalg.svd(best.jac, compute_uv=False)
    return dict(parameters=best.x.tolist(), rmse=float(np.sqrt(np.mean(best.fun**2))),
                jacobian_condition=float(singular[0]/max(singular[-1], 1e-300)),
                success=bool(best.success)), fun(best.x)


def numerical_checks():
    strain = np.linspace(.0002, .0999, 120)
    R, A, k, n, ref = 20., 100., 1.3, .7, .1
    exact = lambda e: R+A*np.exp(-k*(np.asarray(e)/ref)**n)
    derivative = lambda e: -k*n/ref*(np.asarray(e)/ref)**(n-1)*(exact(e)-R)
    h = 1e-8
    fd = (exact(strain+h)-exact(strain-h))/(2*h)
    fd_error = float(np.max(np.abs(fd-derivative(strain)))/np.max(np.abs(derivative(strain))))
    sol = solve_ivp(lambda e, s: -k*n/ref*(e/ref)**(n-1)*(s-R),
                    (strain[0], strain[-1]), [exact(strain[0])], t_eval=strain,
                    rtol=1e-10, atol=1e-10)
    ode_error = float(np.max(np.abs(sol.y[0]-exact(strain)))/np.max(exact(strain)))
    return dict(derivative_relative_error=fd_error, ode_relative_error=ode_error,
                passed=bool(sol.success and fd_error < 1e-6 and ode_error < 1e-6))


def run(root, output):
    root, output = Path(root), Path(output)
    if output.exists():
        raise FileExistsError(f'Choose a new output directory: {output}')
    config_path = root/'configs/effective_equation.json'
    config = json.loads(config_path.read_text())
    if config['test_targets_permitted']:
        raise ValueError('Test target access forbidden')
    grid = np.linspace(config['strain_min'], config['strain_max'], config['strain_points'])
    ids, X, Y, audit, split = load_training(root/'TEAM_8_extracted_results_set_1', root/'data/split.json', grid)
    folds = list(KFold(config['folds'], shuffle=True, random_state=config['seed']).split(ids))
    result = dict(config=config, config_sha256=digest(config_path),
                  code_sha256=digest(__file__), split_sha256=digest(root/'data/split.json'),
                  training_ids=ids.tolist(), excluded_test_ids=split['test'], raw_audit=audit,
                  raw_history_ids_opened=[a['id'] for a in audit],
                  versions=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                  numerical_checks=numerical_checks(), families={},
                  evaluation_status='Development CV: used to compare families/alpha; not unbiased final-test performance')
    baseline = np.empty_like(Y)
    fold_manifest = []
    for tr, va in folds:
        baseline[va] = Y[tr].mean(0)
        fold_manifest.append(dict(fit=ids[tr].tolist(), validation=ids[va].tolist()))
    result['folds'] = fold_manifest
    result['mean_curve_baseline'] = metrics(Y, baseline)
    curves = {}
    start = time.perf_counter()
    for family in config['families']:
        shape, sp = [], []
        for i, y in zip(ids, Y):
            m, p = fit_shape(y, grid, family)
            shape.append(dict(id=int(i), **m)); sp.append(p)
        trials = []
        for alpha in config['alphas']:
            oof = np.empty_like(Y); models = []
            for fold, (tr, va) in enumerate(folds):
                model = fit_global(X[tr], Y[tr], grid, family, alpha, config)
                oof[va] = predict(model, X[va], grid); models.append(model)
                print(f'{family} alpha={alpha} fold={fold+1} done', flush=True)
            trials.append(dict(alpha=alpha, metrics=metrics(Y, oof), models=models, predictions=oof))
        selected = min(trials, key=lambda t: t['metrics']['mean_rmse'])
        transfer = []
        for T, lr in sorted(set(map(tuple, X[:, :2]))):
            va = np.where((X[:, 0] == T) & (X[:, 1] == lr))[0]
            tr = np.setdiff1d(np.arange(len(ids)), va)
            model = fit_global(X[tr], Y[tr], grid, family, selected['alpha'], config)
            p = predict(model, X[va], grid)
            transfer.append(dict(temperature=T, log10_rate=lr, fit_ids=ids[tr].tolist(),
                                 validation_ids=ids[va].tolist(), metrics=metrics(Y[va], p)))
            print(f'{family} condition holdout {T}/{lr} done', flush=True)
        model = fit_global(X, Y, grid, family, selected['alpha'], config)
        cv = selected['metrics']
        gate = dict(mean_nrmse=cv['mean_nrmse'] < config['screening_mean_nrmse'],
                    worst_nrmse=cv['worst_nrmse'] < config['screening_worst_nrmse'],
                    beats_mean_curve=cv['mean_rmse'] < result['mean_curve_baseline']['mean_rmse'],
                    selected_fits_converged=all(m['success'] for m in selected['models']) and model['success'],
                    numerics=result['numerical_checks']['passed'])
        result['families'][family] = dict(shape=shape, shape_metrics=metrics(Y, np.array(sp)),
            trials=[{k:v for k,v in t.items() if k != 'predictions'} for t in trials],
            selected_alpha=selected['alpha'], cv=cv, screening=gate, screening_passed=all(gate.values()),
            condition_holdouts=transfer, final_training_model=model,
            final_training_metrics=metrics(Y, predict(model, X, grid)))
        curves[family] = dict(shape=np.array(sp), cv=selected['predictions'], final=predict(model, X, grid))
    result['elapsed_seconds'] = time.perf_counter()-start
    result['qualified_families'] = [f for f,r in result['families'].items() if r['screening_passed']]
    result['decision'] = 'screening_passed_not_physical_validation' if result['qualified_families'] else 'not_qualified_do_not_create_pinn_yet'
    output.mkdir(parents=True)
    (output/'results.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    with (output/'predictions.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['id', 'E11', 'observed_Svm', 'mean_curve_cv']+
                                      [f'{family}_{kind}' for family in curves for kind in curves[family]])
        for i, case in enumerate(ids):
            for j, strain in enumerate(grid):
                w.writerow([case, strain, Y[i,j], baseline[i,j]]+
                           [curves[family][kind][i,j] for family in curves for kind in curves[family]])
    cache = root/'work'/'matplotlib'
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR', str(cache))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
    for ax, case in zip(axes.flat, [2, 18, 40, 52, 60, 64]):
        i = list(ids).index(case)
        ax.plot(grid, Y[i], color='black', label='Supplied curve')
        for family, style in [('exponential', '--'), ('power_exponential', '-')]:
            ax.plot(grid, curves[family]['cv'][i], style, label=f'{family} case-CV')
        ax.set(title=f'Training case {case}; T={X[i,0]:g}, log-rate={X[i,1]:g}',
               xlabel='E11 (source strain coordinate)', ylabel='Svm (source stress units)')
    axes.flat[0].legend(fontsize=7)
    fig.suptitle('Effective-equation predictions: cases held out within the 36 training cases')
    fig.savefig(output/'case_validation.png', dpi=150); plt.close(fig)
    print(json.dumps(dict(decision=result['decision'],
        families={f: dict(mean_rmse=r['cv']['mean_rmse'], mean_nrmse=r['cv']['mean_nrmse'],
                          worst_nrmse=r['cv']['worst_nrmse'], gate=r['screening'])
                  for f,r in result['families'].items()})), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.root, args.output)
