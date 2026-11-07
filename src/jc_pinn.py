"""Johnson-Cook-governed physics-informed network (JC-PINN) for the AlSi10Mg Svm(E11) curves.

Governing equation (the user's customised Johnson-Cook law, Equation 1, 7 November 2026)::

    sigma_JC = [A - B*eps^n] * [1 + C*ln(rate/rate0)] * [1 - Tstar^m] * [G/G0]^q * [1 - phi]^r

    Tstar = (T - T_ref)/(T_melt - T_ref),  phi = 1 - density/rho0

Model: the equation is the backbone and a small network learns a bounded correction::

    sigma = sigma_JC(theta) * exp(delta(z)),  delta = 5-16-16-1 tanh network, last layer starts at 0

    loss = mean(((sigma - S)/s_y)^2)                 data term, 120 equal-weight points per case
         + lambda_phys * mean_collocation(delta^2)   physics term: delta = ln(sigma) - ln(sigma_JC)
         + (alpha/N) * sum ||W||^2                   weight decay on network weights

delta is exactly the log residual of Equation 1, so the physics term is the PINN residual loss.
Collocation points cover the whole planned design box, including conditions without data.
lambda_phys = 0 gives an unconstrained data fit; a very large lambda_phys returns Equation 1.

The script runs training-only selection, saves and locks the selected model, and only then
loads the 37 test histories. Run ``python src/jc_pinn.py --help``.
"""
import argparse
import csv
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import platform
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PARAMS = ['A', 'B', 'n', 'C', 'm', 'q', 'r']           # physical constants of Equation 1
CAL_VARS = ['A', 'beta', 'n', 'C', 'm', 'q', 'r']      # bounded calibration variables
HEADER = 'TIME Evm Svm E11 E22 E33 E23 E13 E12 SCAU11 SCAU22 SCAU33 SCAU23 SCAU13 SCAU12 TEMP'.split()


# ----------------------------------------------------------------------------- utilities
def json_text(value):
    """Strict JSON (no NaN) that also accepts NumPy scalars and arrays."""
    def convert(v):
        if isinstance(v, np.generic):
            return v.item()
        if isinstance(v, np.ndarray):
            return v.tolist()
        raise TypeError(f'Unsupported JSON value: {type(v).__name__}')
    return json.dumps(value, indent=2, default=convert, allow_nan=False) + '\n'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_config(path=None):
    return json.loads(Path(path or ROOT / 'configs/jc_pinn.json').read_text())


def strain_grid(cfg):
    g = cfg['grid']
    return np.linspace(g['strain_min'], g['strain_max'], g['strain_points'])


def queries(X, grid):
    """Case conditions (n,4) x strain grid -> query rows [T, log10 rate, density, G, E11]."""
    return np.c_[np.repeat(X, len(grid), axis=0), np.tile(grid, len(X))]


# ----------------------------------------------------------------------------- data
def load_cases(raw, ids, grid):
    """Read STR_STR.OUT histories and interpolate Svm onto the common E11 grid.

    Identical to src/single_mlp.py's loader so all project models see the same curves.
    Returns X (n,4) = [T degC, log10 rate, density, G], Y (n, len(grid)) and a hash audit.
    """
    raw = Path(raw)
    with (raw / 'simulation_matrix.csv').open() as f:
        matrix = {int(r['Simulation_ID']): r for r in csv.DictReader(f)}
    X, Y, audit = [], [], []
    for i in ids:
        path = raw / f'simulation_{int(i):04d}' / 'STR_STR.OUT'
        with path.open() as f:
            if f.readline().split() != HEADER:
                raise ValueError(f'Unexpected header in {path}')
        a = np.loadtxt(path, skiprows=1, usecols=(2, 3))
        if not np.isfinite(a).all() or not np.all(np.diff(a[:, 1]) > 0):
            raise ValueError(f'Invalid curve {i}')
        if grid[0] < a[0, 1] or grid[-1] > a[-1, 1]:
            raise ValueError(f'Curve {i} would require extrapolation')
        r = matrix[int(i)]
        X.append([float(r['temperature']), np.log10(float(r['strain_rate'])),
                  float(r['density']), float(r['shear_modulus'])])
        Y.append(np.interp(grid, a[:, 1], a[:, 0]))
        audit.append(dict(id=int(i), sha256=sha(path), rows=len(a)))
    return np.array(X), np.array(Y), audit


def fingerprints(ids, Y):
    """Small per-case summary used to confirm that a new environment reads identical curves."""
    return {str(int(i)): [float(y[0]), float(y[len(y) // 2]), float(y[-1]), float(np.mean(y))] for i, y in zip(ids, Y)}


def check_fingerprints(ids, Y, expected, tol=1e-8):
    if not expected:
        return None
    got = fingerprints(ids, Y)
    worst = max(max(abs(a - b) for a, b in zip(got[k], expected[k])) for k in got)
    if worst > tol:
        raise ValueError(f'Curves differ from the committed curves by {worst:g}; check the data folder')
    return worst


# ----------------------------------------------------------------------------- Equation 1
def _terms_numpy(X5, const):
    T, lograte, rho, G, eps = (X5[:, j] for j in range(5))
    ln_rate = math.log(10.0) * (lograte - math.log10(const['rate0']))
    Ts = np.clip((T - const['T_ref']) / (const['T_melt'] - const['T_ref']), 0.0, None)
    return eps, ln_rate, Ts, G / const['G0'], rho / const['rho0']


def jc_numpy(theta, X5, const):
    """Equation 1 in NumPy. theta = (A, B, n, C, m, q, r); X5 rows = [T, log10 rate, density, G, E11]."""
    A, B, n, C, m, q, r = theta
    eps, ln_rate, Ts, g, om = _terms_numpy(np.asarray(X5, dtype=float), const)
    Tm = np.where(Ts > 0, np.exp(m * np.log(np.maximum(Ts, 1e-300))), 0.0)
    return (A - B * eps ** n) * (1.0 + C * ln_rate) * (1.0 - Tm) * g ** q * om ** r


def theta_from_cal(v, const):
    """Calibration variables (A, beta, n, C, m, q, r) -> physical constants (A, B, n, C, m, q, r)."""
    A, beta, n, C, m, q, r = v
    return np.array([A, A * beta / const['eps_ref'] ** n, n, C, m, q, r])


def cal_from_theta(theta, const):
    A, B, n, C, m, q, r = theta
    return np.array([A, B * const['eps_ref'] ** n / A, n, C, m, q, r])


def calibrate_jc(Xq, yq, cfg, y_scale):
    """Fit the seven constants of Equation 1 alone by bounded least squares (multi-start)."""
    from scipy.optimize import least_squares
    const, cal = cfg['constants'], cfg['calibration']
    lo = np.array([cal['bounds'][k][0] for k in CAL_VARS])
    hi = np.array([cal['bounds'][k][1] for k in CAL_VARS])
    rng = np.random.default_rng(cal['seed'])
    starts = [np.array([float(np.max(yq)), 0.5, 0.8, 0.03, 1.0, 0.5, 0.05])]
    sub_lo = np.array([0.5 * np.max(yq), 0.05, 0.2, 0.0, 0.3, 0.0, 0.0])
    sub_hi = np.array([1.5 * np.max(yq), 0.95, 2.0, 0.2, 4.0, 2.0, 1.0])
    starts += [rng.uniform(sub_lo, sub_hi) for _ in range(cal['starts'] - 1)]
    resid = lambda v: (jc_numpy(theta_from_cal(v, const), Xq, const) - yq) / y_scale
    runs = []
    for v0 in starts:
        res = least_squares(resid, np.clip(v0, lo, hi), bounds=(lo, hi), jac='3-point', method='trf',
                            x_scale='jac', ftol=cal['tol'], xtol=cal['tol'], gtol=cal['tol'], max_nfev=cal['max_nfev'])
        runs.append(dict(start=v0.tolist(), v=res.x.tolist(), cost=float(res.cost), status=int(res.status), nfev=int(res.nfev)))
    best = min(runs, key=lambda r: r['cost'])
    v = np.array(best['v'])
    at_bound = [k for k, x, a, b in zip(CAL_VARS, v, lo, hi) if np.isclose(x, a, atol=1e-9) or np.isclose(x, b, atol=1e-9)]
    theta = theta_from_cal(v, const)
    return v, dict(theta=dict(zip(PARAMS, theta.tolist())), cal_vars=dict(zip(CAL_VARS, v.tolist())),
                   normalised_mse=float(2 * best['cost'] / len(yq)), at_bounds=at_bound,
                   starts=runs, best_start=runs.index(best))


# ----------------------------------------------------------------------------- torch model
def _torch():
    import torch
    torch.set_default_dtype(torch.float64)
    return torch


def jc_torch(theta, X5, const):
    """Equation 1 in torch (same formula as jc_numpy, differentiable in theta and inputs)."""
    torch = _torch()
    A, B, n, C, m, q, r = theta
    T, lograte, rho, G, eps = X5.unbind(1)
    ln_rate = math.log(10.0) * (lograte - math.log10(const['rate0']))
    Ts = ((T - const['T_ref']) / (const['T_melt'] - const['T_ref'])).clamp_min(0.0)
    Tm = torch.where(Ts > 0, torch.exp(m * torch.log(Ts.clamp_min(1e-300))), torch.zeros_like(Ts))
    return (A - B * eps ** n) * (1 + C * ln_rate) * (1 - Tm) * (G / const['G0']) ** q * (rho / const['rho0']) ** r


def torch_log_stress(mem, X5, const, x_mean, x_scale):
    """ln(sigma) of one saved member, evaluated in torch from its exported numbers."""
    torch = _torch()
    t = lambda v: torch.tensor(v, dtype=torch.float64)
    cols = mem.get('inputs', list(range(5)))
    z = (X5[:, cols] - t(x_mean)[cols]) / t(x_scale)[cols]
    h = torch.tanh(torch.tanh(z @ t(mem['W1']).T + t(mem['b1'])) @ t(mem['W2']).T + t(mem['b2']))
    return torch.log(jc_torch(t(mem['theta']), X5, const)) + h @ t(mem['w3']) + mem['b3']


def build_model(v_cal, cfg, x_mean, x_scale, joint, seed):
    """Equation-1 backbone with a zero-initialised 5-16-16-1 tanh correction network."""
    torch = _torch()
    nn = torch.nn
    const, b = cfg['constants'], cfg['calibration']['bounds']
    lo = torch.tensor([b[k][0] for k in CAL_VARS])
    hi = torch.tensor([b[k][1] for k in CAL_VARS])

    class JCPINN(nn.Module):
        def __init__(self):
            super().__init__()
            torch.manual_seed(seed)
            h1, h2 = cfg['network']['hidden']
            self.cols = list(cfg['network'].get('correction_inputs', range(5)))
            self.l1, self.l2, self.l3 = nn.Linear(len(self.cols), h1), nn.Linear(h1, h2), nn.Linear(h2, 1)
            nn.init.zeros_(self.l3.weight)
            nn.init.zeros_(self.l3.bias)
            self.register_buffer('x_mean', torch.tensor(np.asarray(x_mean)[self.cols]))
            self.register_buffer('x_scale', torch.tensor(np.asarray(x_scale)[self.cols]))
            self.register_buffer('lo', lo)
            self.register_buffer('hi', hi)
            frac = ((torch.tensor(np.asarray(v_cal, dtype=float)) - lo) / (hi - lo)).clamp(1e-6, 1 - 1e-6)
            u = torch.log(frac) - torch.log1p(-frac)
            if joint:
                self.u = nn.Parameter(u)
            else:
                self.register_buffer('u', u)

        def cal_vars(self):
            return self.lo + (self.hi - self.lo) * torch.sigmoid(self.u)

        def theta(self):
            A, beta, n, C, m, q, r = self.cal_vars()
            return torch.stack([A, A * beta / const['eps_ref'] ** n, n, C, m, q, r])

        def backbone(self, X5):
            return jc_torch(self.theta(), X5, const)

        def delta(self, X5):
            z = (X5[:, self.cols] - self.x_mean) / self.x_scale
            return self.l3(torch.tanh(self.l2(torch.tanh(self.l1(z))))).squeeze(1)

        def forward(self, X5):
            base, d = self.backbone(X5), self.delta(X5)
            return base * torch.exp(d), base, d

    return JCPINN()


def collocation(cfg):
    """Fixed scrambled-Sobol input locations over the planned design box (no targets)."""
    torch = _torch()
    box = cfg['collocation']['box']
    keys = ['temperature', 'log10_rate', 'density', 'G', 'E11']
    eng = torch.quasirandom.SobolEngine(5, scramble=True, seed=cfg['collocation']['seed'])
    u = eng.draw(cfg['collocation']['points']).double().numpy()
    lo = np.array([box[k][0] for k in keys])
    hi = np.array([box[k][1] for k in keys])
    return lo + (hi - lo) * u


def physics_residual(model, Xc, form):
    """Mean squared residual of Equation 1 at collocation points (no targets involved).

    level: delta = ln(sigma) - ln(sigma_JC), i.e. the model's stress level should follow Equation 1.
    trend: d(delta)/dz_c for the four conditions c = T, log10 rate, density, G, i.e. the model's
           sensitivities d ln(sigma)/dc should equal Equation 1's (derivative form via autograd,
           converted to standardised units with the scaling chain rule). The strain-shape
           correction delta(E11) stays free.
    """
    torch = _torch()
    if form == 'level':
        return torch.mean(model.delta(Xc) ** 2)
    if form == 'trend':
        X = Xc.detach().requires_grad_(True)
        g, = torch.autograd.grad(model.delta(X).sum(), X, create_graph=True)
        scale = torch.ones(5, dtype=X.dtype)
        scale[model.cols] = model.x_scale
        return torch.mean(((g * scale)[:, :4] ** 2).sum(1))
    raise ValueError(form)


def train_member(Xq, yq, Cq, v_cal, cfg, x_mean, x_scale, y_scale, cand, seed):
    """Train one JC-PINN member: Adam warm-up then L-BFGS, full batch, float64, deterministic."""
    torch = _torch()
    torch.set_num_threads(1)
    tr = cfg['training']
    lam, joint, form = cand['lambda_phys'], cand['theta_mode'] == 'joint', cand['physics']
    model = build_model(v_cal, cfg, x_mean, x_scale, joint, seed)
    Xd, yd, Xc = torch.tensor(Xq), torch.tensor(yq), torch.tensor(Cq)
    N = len(yq)
    weights = [model.l1.weight, model.l2.weight, model.l3.weight]

    def parts(report=False):
        s, _, _ = model(Xd)
        data = torch.mean(((s - yd) / y_scale) ** 2)
        need = lam > 0 or report
        phys = physics_residual(model, Xc, 'level' if form == 'none' else form) if need else torch.zeros(())
        reg = tr['alpha'] / N * sum((w ** 2).sum() for w in weights)
        return data + lam * phys + reg, data, phys, reg

    net_params = [p for name, p in model.named_parameters() if name != 'u']
    groups = [dict(params=net_params)]
    if joint:
        groups.append(dict(params=[model.u], lr=tr['adam_lr'] * tr['theta_lr_scale']))
    start = time.perf_counter()
    adam = torch.optim.Adam(groups, lr=tr['adam_lr'])
    for _ in range(tr['adam_steps']):
        adam.zero_grad()
        loss = parts()[0]
        loss.backward()
        adam.step()
    after_adam = parts()[0].item()
    lbfgs = torch.optim.LBFGS([p for g in groups for p in g['params']], lr=1.0, max_iter=tr['lbfgs_max_iter'],
                              max_eval=int(tr['lbfgs_max_iter'] * 1.25), history_size=tr['lbfgs_history'],
                              tolerance_grad=tr['lbfgs_tolerance_grad'], tolerance_change=tr['lbfgs_tolerance_change'],
                              line_search_fn='strong_wolfe')

    def closure():
        lbfgs.zero_grad()
        loss = parts()[0]
        loss.backward()
        return loss
    lbfgs.step(closure)
    state = lbfgs.state[lbfgs._params[0]]
    total, data, phys, reg = (x.item() for x in parts(report=True))
    if not all(np.isfinite([total, data, phys, reg])):
        raise FloatingPointError('Non-finite loss after training')
    info = dict(seed=seed, **cand, loss=total, data_loss=data,
                physics_loss=phys, weight_loss=reg, loss_after_adam=after_adam, lbfgs_iterations=int(state.get('n_iter', 0)),
                lbfgs_evaluations=int(state.get('func_evals', 0)), seconds=time.perf_counter() - start)
    return export_member(model), info


def export_member(model):
    t = lambda p: p.detach().numpy().tolist()
    return dict(inputs=model.cols, W1=t(model.l1.weight), b1=t(model.l1.bias), W2=t(model.l2.weight), b2=t(model.l2.bias),
                w3=t(model.l3.weight)[0], b3=float(model.l3.bias.detach()[0]),
                cal_vars=t(model.cal_vars()), theta=t(model.theta()))


# ----------------------------------------------------------------------------- portable equation
def member_delta(member, X5, x_mean, x_scale):
    cols = member.get('inputs', list(range(5)))
    z = (np.asarray(X5, dtype=float)[:, cols] - np.array(x_mean)[cols]) / np.array(x_scale)[cols]
    h1 = np.tanh(z @ np.array(member['W1']).T + member['b1'])
    h2 = np.tanh(h1 @ np.array(member['W2']).T + member['b2'])
    return h2 @ np.array(member['w3']) + member['b3']


def equation_predict(eq, X5, parts=False):
    """Evaluate a saved equation.json with NumPy only. X5 rows = [T, log10 rate, density, G, E11].

    Ensemble rule: geometric mean of member stresses,
    sigma = exp(mean_k[ln sigma_JC(theta_k) + delta_k]) = sigma_JC(theta)*exp(mean_k delta_k) for one shared theta.
    """
    X5 = np.atleast_2d(np.asarray(X5, dtype=float))
    logs, bases, deltas = [], [], []
    for mem in eq['members']:
        base = jc_numpy(mem['theta'], X5, eq['constants'])
        d = member_delta(mem, X5, eq['x_mean'], eq['x_scale'])
        logs.append(np.log(base) + d)
        bases.append(base)
        deltas.append(d)
    s = np.exp(np.mean(logs, axis=0))
    if parts:
        return s, np.exp(np.mean(np.log(bases), axis=0)), np.mean(deltas, axis=0)
    return s


def make_equation(members, cfg, x_mean, x_scale, y_scale, cand, fit_ids):
    return dict(
        name='JC-PINN: user Equation 1 backbone with neural correction',
        governing_equation=cfg['governing_equation'], model=cfg['model'], constants=cfg['constants'],
        variable_mapping=cfg['variable_mapping'], input_order=cfg['network']['inputs'],
        theta_names=PARAMS, theta=dict(zip(PARAMS, np.mean([m['theta'] for m in members], axis=0).tolist())),
        selected=cand, correction_inputs=members[0]['inputs'], x_mean=list(x_mean), x_scale=list(x_scale), target_scale=y_scale,
        members=members, fit_ids=[int(i) for i in fit_ids],
        ensemble='sigma = exp(mean_k[ln sigma_JC(theta_k) + delta_k(z)]); z = (x - x_mean)/x_scale; '
                 'delta_k = w3.tanh(W2.tanh(W1.z + b1) + b2) + b3',
        validity=dict(temperature_C=[30, 200], temperature_extrapolation_C=[200, 300], log10_rate=[-5, -3],
                      density=[2488.05, 2700], G_MPa=[23313.95, 25300], E11=[0.0002, 0.0999],
                      note=extrapolation_note(cand)))


def extrapolation_note(cand):
    if cand['lambda_phys'] > 0:
        return (f"Data cover 30-200 C; 200-300 C is held to Equation 1 only through the {cand['physics']} physics "
                'residual and is unvalidated.')
    return ('Data cover 30-200 C; with lambda_phys = 0 nothing constrains 200-300 C except the Equation 1 backbone '
            'and the smooth network, so those curves are unvalidated extrapolation.')


# ----------------------------------------------------------------------------- fitting and scoring
def scalers(Xq, Y):
    x_mean, x_scale = Xq.mean(0), Xq.std(0)
    x_scale = np.where(x_scale > 0, x_scale, 1.0)
    return x_mean, x_scale, float(Y.std())


def lookup(X, Y, V):
    """Curve-copy baseline: nearest training curve at the same temperature and rate (src/single_mlp.py)."""
    out = []
    for v in V:
        same = (X[:, 0] == v[0]) & (X[:, 1] == v[1])
        if not same.any():
            same[:] = True
        c = X[same]
        d = np.abs(c[:, 0] - v[0]) / 50 + np.abs(c[:, 1] - v[1]) + np.abs(c[:, 2] - v[2]) / 1000 + np.abs(c[:, 3] - v[3]) / 1000
        out.append(Y[same][d.argmin()])
    return np.array(out)


def scores(y, p):
    rmse = np.sqrt(np.mean((y - p) ** 2, axis=1))
    mae = np.mean(np.abs(y - p), axis=1)
    norm = rmse / np.sqrt(np.mean(y * y, axis=1))
    return dict(mean_rmse=float(rmse.mean()), median_rmse=float(np.median(rmse)), worst_rmse=float(rmse.max()),
                mean_mae=float(mae.mean()), mean_nrmse=float(norm.mean()), worst_nrmse=float(norm.max()),
                case_rmse=rmse.tolist(), case_mae=mae.tolist())


def candidates(cfg):
    sel = cfg['selection']
    return [dict(physics=form, lambda_phys=float(lam), theta_mode=mode)
            for mode in sel['theta_modes'] for form, lams in sel['physics'].items() for lam in lams]


def splits(X, ids, cfg):
    """Three whole-case folds plus nine temperature/rate group holdouts, training cases only."""
    from sklearn.model_selection import KFold
    out = []
    kf = KFold(cfg['selection']['folds'], shuffle=True, random_state=cfg['selection']['fold_seed'])
    for k, (tr, va) in enumerate(kf.split(X)):
        out.append(dict(kind='fold', name=f'fold{k}', fit=tr, val=va))
    for T, rate in sorted(set(map(tuple, X[:, :2]))):
        va = np.flatnonzero((X[:, 0] == T) & (X[:, 1] == rate))
        out.append(dict(kind='group', name=f'T{T:g}_rate{rate:g}', temperature=T, log10_rate=rate,
                        fit=np.setdiff1d(np.arange(len(X)), va), val=va))
    for s in out:
        s['fit_ids'], s['val_ids'] = ids[s['fit']].tolist(), ids[s['val']].tolist()
        assert not set(s['fit_ids']) & set(s['val_ids'])
    return out


def _member_task(args):
    """Worker: train one member on a fitting set and predict its validation queries."""
    key, Xq, yq, Vq, Cq, v_cal, cfg, x_mean, x_scale, y_scale, cand, seed = args
    member, info = train_member(Xq, yq, Cq, v_cal, cfg, x_mean, x_scale, y_scale, cand, seed)
    log_pred = np.log(jc_numpy(member['theta'], Vq, cfg['constants'])) + member_delta(member, Vq, x_mean, x_scale)
    return key, log_pred, member, info


def _pool(workers):
    method = 'fork' if 'fork' in mp.get_all_start_methods() else 'spawn'
    return mp.get_context(method).Pool(workers)


def _run_tasks(tasks, workers, label):
    results, t0 = [], time.perf_counter()
    if workers <= 1:
        it = map(_member_task, tasks)
        pool = None
    else:
        pool = _pool(workers)
        it = pool.imap_unordered(_member_task, tasks)
    for k, r in enumerate(it, 1):
        results.append(r)
        if k % max(1, len(tasks) // 20) == 0 or k == len(tasks):
            print(f'  {label}: {k}/{len(tasks)} fits, {time.perf_counter() - t0:.0f} s', flush=True)
    if pool is not None:
        pool.close()
        pool.join()
    return results


def select(X, Y, ids, grid, cfg, workers, Cq):
    """Training-only selection of (lambda_phys, theta_mode) with the pre-registered balanced score."""
    sp = splits(X, ids, cfg)
    cands = candidates(cfg)
    prep = []
    for s in sp:
        Xq, yq = queries(X[s['fit']], grid), Y[s['fit']].ravel()
        x_mean, x_scale, y_scale = scalers(Xq, Y[s['fit']])
        v, cal = calibrate_jc(Xq, yq, cfg, y_scale)
        Vq = queries(X[s['val']], grid)
        jc_pred = jc_numpy(theta_from_cal(v, cfg['constants']), Vq, cfg['constants']).reshape(len(s['val']), len(grid))
        prep.append(dict(Xq=Xq, yq=yq, Vq=Vq, x_mean=x_mean, x_scale=x_scale, y_scale=y_scale, v=v, cal=cal, jc=jc_pred))
        print(f"  Equation 1 calibrated on {s['name']}: normalised MSE {cal['normalised_mse']:.5f}", flush=True)
    tasks = [((si, ci, seed), p['Xq'], p['yq'], p['Vq'], Cq, p['v'], cfg, p['x_mean'], p['x_scale'], p['y_scale'], c, seed)
             for si, p in enumerate(prep) for ci, c in enumerate(cands) for seed in cfg['selection']['seeds']]
    out = _run_tasks(tasks, workers, 'selection')
    logs, infos = {}, {}
    for (si, ci, seed), lp, _, info in out:
        logs.setdefault((si, ci), []).append((seed, lp))
        infos.setdefault((si, ci), []).append(info)
    n = len(grid)

    def assemble(get):
        """Build CV predictions (36 cases) and per-group predictions from per-split predictions."""
        cv = np.empty_like(Y)
        groups = []
        for si, (s, p) in enumerate(zip(sp, prep)):
            pr = get(si, s, p)
            if s['kind'] == 'fold':
                cv[s['val']] = pr
            else:
                groups.append((s, pr))
        return cv, groups

    def summarise(get):
        cv, groups = assemble(get)
        g = [dict(name=s['name'], temperature=s['temperature'], log10_rate=s['log10_rate'], validation_ids=s['val_ids'],
                  metrics=scores(Y[s['val']], pr)) for s, pr in groups]
        cvm = scores(Y, cv)
        gm = float(np.mean([x['metrics']['mean_rmse'] for x in g]))
        return dict(cv=cvm, groups=g, group_mean_rmse=gm, score=0.5 * (cvm['mean_rmse'] + gm)), cv

    trials = []
    cv_preds = {}
    for ci, c in enumerate(cands):
        def get(si, s, p, ci=ci):
            members = sorted(logs[(si, ci)])
            return np.exp(np.mean([lp for _, lp in members], axis=0)).reshape(len(s['val']), n)
        summ, cv = summarise(get)
        fits = [i for si in range(len(sp)) for i in infos[(si, ci)]]
        summ.update(candidate=c, fits=dict(count=len(fits), max_loss=max(f['loss'] for f in fits),
                                           mean_seconds=float(np.mean([f['seconds'] for f in fits])),
                                           max_lbfgs_iterations=max(f['lbfgs_iterations'] for f in fits)))
        trials.append(summ)
        cv_preds[ci] = cv
        print(f"  candidate {c}: CV {summ['cv']['mean_rmse']:.4f}, groups {summ['group_mean_rmse']:.4f}, "
              f"score {summ['score']:.4f}", flush=True)
    jc_summary, jc_cv = summarise(lambda si, s, p: p['jc'])
    base_summary, base_cv = summarise(lambda si, s, p: lookup(X[s['fit']], Y[s['fit']], X[s['val']]))
    order = sorted(range(len(cands)), key=lambda ci: (round(trials[ci]['score'], 12), -cands[ci]['lambda_phys'],
                                                     cands[ci]['theta_mode'] != 'frozen'))
    best = order[0]
    return dict(splits=[{k: v for k, v in s.items() if k not in ('fit', 'val')} for s in sp],
                calibrations=[dict(split=s['name'], **p['cal']) for s, p in zip(sp, prep)],
                trials=trials, selected=cands[best], selected_index=best, ranking=[cands[i] for i in order],
                equation_only=jc_summary, lookup=base_summary,
                fit_infos={f'{sp[si]["name"]}|{cands[ci]}': v for (si, ci), v in infos.items()}), \
        dict(model=cv_preds[best], equation_only=jc_cv, lookup=base_cv)


def fit_final(X, Y, ids, grid, cfg, cand, workers, Cq):
    Xq, yq = queries(X, grid), Y.ravel()
    x_mean, x_scale, y_scale = scalers(Xq, Y)
    v, cal = calibrate_jc(Xq, yq, cfg, y_scale)
    tasks = [(('final', seed), Xq, yq, Xq, Cq, v, cfg, x_mean, x_scale, y_scale, cand, seed)
             for seed in cfg['final']['seeds']]
    out = sorted(_run_tasks(tasks, workers, 'final fit'), key=lambda r: r[0][1])
    members = [m for _, _, m, _ in out]
    infos = [i for _, _, _, i in out]
    eq = make_equation(members, cfg, x_mean, x_scale, y_scale, cand, ids)
    eq_only = dict(constants=cfg['constants'], theta=dict(zip(PARAMS, theta_from_cal(v, cfg['constants']).tolist())),
                   calibration=cal, fit_ids=[int(i) for i in ids])
    return eq, eq_only, infos


def torch_predict(eq, X5):
    """Reference torch evaluation of a saved equation (checks the NumPy formula)."""
    torch = _torch()
    X = torch.tensor(np.asarray(X5, dtype=float))
    with torch.no_grad():
        logs = [torch_log_stress(m, X, eq['constants'], eq['x_mean'], eq['x_scale']) for m in eq['members']]
    return torch.exp(torch.stack(logs).mean(0)).numpy()


def monotonicity(eq, cfg):
    """Share of collocation points that break the sign rules seen in every training-data pair."""
    torch = _torch()
    X = torch.tensor(collocation(cfg), requires_grad=True)
    logs = [torch_log_stress(m, X, eq['constants'], eq['x_mean'], eq['x_scale']) for m in eq['members']]
    s = torch.exp(torch.stack(logs).mean(0))
    g, = torch.autograd.grad(s.sum(), X)
    g = g.numpy()
    T = X.detach().numpy()[:, 0]
    out = {}
    for label, mask in [('observed_30_200C', T <= 200), ('physics_only_200_300C', T > 200)]:
        out[label] = dict(points=int(mask.sum()),
                          dS_dE11_positive=float(np.mean(g[mask, 4] > 0)),
                          dS_dT_positive=float(np.mean(g[mask, 0] > 0)),
                          dS_dG_negative=float(np.mean(g[mask, 3] < 0)),
                          dS_ddensity_negative=float(np.mean(g[mask, 2] < 0)))
    out['rule'] = ('Training pairs show stress falls with E11 (except case 60), falls with T, rises with G and with density '
                   '(falls with porosity). Strain rate is mixed in the data, so it is not checked.')
    return out


# ----------------------------------------------------------------------------- reporting
def references(root):
    """Earlier models' saved results on the same 36/37 split (read-only)."""
    out = {}
    p = Path(root) / 'reports/single_mlp_20261102/results.json'
    if p.exists():
        r = json.loads(p.read_text())
        out['single_mlp'] = dict(source=str(p.relative_to(root)), sha256=sha(p), test=r['test'], cv=r['cv'],
                                 groups=[dict(temperature=g['temperature'], log10_rate=g['log10_rate'],
                                              mean_rmse=g['mlp']['mean_rmse']) for g in r['condition_holdouts']])
    p = Path(root) / 'runs/score/final_Svm/metrics.json'
    if p.exists():
        out['ensemble_mlp'] = dict(source=str(p.relative_to(root)), sha256=sha(p), metrics=json.loads(p.read_text()))
    if not out:
        # The earlier models were archived; their numbers are frozen with provenance in baselines.json.
        for b in sorted(Path(root).glob('reports/*/baselines.json')):
            B = json.loads(b.read_text())
            s, e = B['single_mlp'], B['ensemble_mlp']
            out['single_mlp'] = dict(source=str(b.relative_to(root)), test=s['test'], cv=dict(mean_rmse=s['cv']), groups=s['groups'])
            out['ensemble_mlp'] = dict(source=str(b.relative_to(root)), metrics=dict(test_mean_rmse=e['test']['mean_rmse'],
                                       test_median_rmse=e['test']['median_rmse'], test_worst_rmse=e['test']['worst_rmse'], per_case=e['test_case_rmse']))
            break
    return out


def write_csv(path, ids, grid, columns):
    with Path(path).open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'E11'] + list(columns))
        for i, case in enumerate(ids):
            for j, e in enumerate(grid):
                w.writerow([int(case), repr(float(e))] + [repr(float(v[i, j])) for v in columns.values()])


def study_curves(eq, cfg, grid, cand=None):
    sp = cfg['study_point']
    rows = []
    for T in (30.0, 100.0, 200.0, 300.0):
        for lr in (-5.0, -4.0, -3.0):
            X5 = np.c_[np.tile([T, lr, sp['density'], sp['G']], (len(grid), 1)), grid]
            s, base, d = equation_predict(eq, X5, parts=True)
            rows.append(dict(temperature=T, log10_rate=lr, stress=s.tolist(), equation_only_backbone=base.tolist(),
                             correction_factor=np.exp(d).tolist(), extrapolated=T > 200))
    return dict(porosity=sp['porosity'], density=sp['density'], G=sp['G'], E11=grid.tolist(), curves=rows,
                note='300 C has no data. ' + extrapolation_note(cand or eq.get('selected', dict(lambda_phys=0.0))))


def plots(output, grid, test, Z, p, p_jc, train, Y, cv, cv_jc, sel, study, refs):
    cache = Path(output) / '.mpl'
    cache.mkdir(exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR', str(cache))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rm = np.sqrt(np.mean((Z - p) ** 2, axis=1))
    order = np.argsort(rm)
    i60 = list(train).index(60) if cv is not None and 60 in list(train) else None
    panels = [(Z[order[-1]], p[order[-1]], p_jc[order[-1]], f'Worst test case {test[order[-1]]}'),
              (Z[order[len(order) // 2]], p[order[len(order) // 2]], p_jc[order[len(order) // 2]],
               f'Median test case {test[order[len(order) // 2]]}')]
    hot = [k for k in range(len(test)) if test[k] >= 64]
    if hot:
        k = hot[int(np.argmax(rm[hot]))]
        panels.append((Z[k], p[k], p_jc[k], f'Hardest 200 °C test case {test[k]}'))
    if i60 is not None:
        panels.append((Y[i60], cv[i60], cv_jc[i60], 'Case 60 (training-side CV, not test)'))
    fig, axes = plt.subplots(1, len(panels), figsize=(4.2 * len(panels), 3.8), constrained_layout=True)
    for ax, (truth, mp_, jc_, title) in zip(np.atleast_1d(axes), panels):
        ax.plot(grid, truth, color='black', lw=2, label='Simulation (Svm)')
        ax.plot(grid, jc_, '--', color='#c0392b', label='Equation 1 only')
        ax.plot(grid, mp_, color='#2471a3', label='JC-PINN')
        ax.set(title=title, xlabel='E11 (axial strain)', ylabel='Svm (MPa, inferred)')
        ax.grid(alpha=.3)
    np.atleast_1d(axes)[0].legend(fontsize=8)
    fig.savefig(Path(output) / 'test_comparison.png', dpi=150)
    plt.close(fig)

    if 'selected_trial' in sel:
        holdout_figure(output, sel, refs, plt)
    study_figure(output, study, plt)


def holdout_figure(output, sel, refs, plt):
    names = [f"{g['temperature']:g} °C\n1e{g['log10_rate']:g}" for g in sel['selected_trial']['groups']]
    series = [('Curve copy', [g['metrics']['mean_rmse'] for g in sel['lookup']['groups']], '#95a5a6'),
              ('Equation 1 only', [g['metrics']['mean_rmse'] for g in sel['equation_only']['groups']], '#c0392b'),
              ('JC-PINN (selected)', [g['metrics']['mean_rmse'] for g in sel['selected_trial']['groups']], '#2471a3')]
    if 'single_mlp' in refs:
        series.append(('Single MLP (2 Nov)', [g['mean_rmse'] for g in refs['single_mlp']['groups']], '#27ae60'))
    fig, ax = plt.subplots(figsize=(10, 4), constrained_layout=True)
    w = 0.8 / len(series)
    for k, (lab, vals, col) in enumerate(series):
        ax.bar(np.arange(len(names)) + (k - (len(series) - 1) / 2) * w, vals, w, label=lab, color=col)
    ax.set_xticks(np.arange(len(names)), names, fontsize=8)
    ax.set(ylabel='Mean curve RMSE (MPa, inferred)', title='Unseen temperature/rate group (training cases only)')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=.3)
    fig.savefig(Path(output) / 'condition_holdouts.png', dpi=150)
    plt.close(fig)


def study_figure(output, study, plt):
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.9), constrained_layout=True, sharey=True)
    colours = {30.0: '#1f77b4', 100.0: '#2ca02c', 200.0: '#d62728', 300.0: '#7f7f7f'}
    for ax, lr in zip(axes, (-5.0, -4.0, -3.0)):
        for c in study['curves']:
            if c['log10_rate'] == lr:
                ax.plot(study['E11'], c['stress'], '--' if c['extrapolated'] else '-', color=colours[c['temperature']],
                        label=f"{c['temperature']:g} °C" + (' (no data: extrapolation)' if c['extrapolated'] else ''))
        ax.set(title=f'φ = {study["porosity"]:.0%}, rate 1e{lr:g} /s', xlabel='E11 (axial strain)')
        ax.grid(alpha=.3)
    axes[0].set_ylabel('Predicted Svm (MPa, inferred)')
    axes[0].legend(fontsize=8)
    fig.savefig(Path(output) / 'study_point_curves.png', dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------------- full experiment
def run(root, raw, output, mode='full', selected=None, workers=None, expected=None, cfg=None):
    """Select (full mode) or reuse (fast mode) settings, lock the model, then score the 37 test cases once."""
    root, output = Path(root), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    cfg = cfg or load_config(root / 'configs/jc_pinn.json')
    split = json.loads((root / 'data/split.json').read_text())
    train, test = np.array(split['train']), np.array(split['test'])
    assert len(set(train)) == 36 and len(set(test)) == 37 and not set(train) & set(test)
    grid = strain_grid(cfg)
    workers = workers or max(1, os.cpu_count() or 1)
    protected = {str(p.relative_to(root)): sha(p) for d in ('runs/score/final_Svm', 'reports/single_mlp_20261102')
                 for p in sorted((root / d).glob('*')) if p.is_file()} if (root / 'runs/score/final_Svm').exists() else {}
    start = time.perf_counter()
    X, Y, audit = load_cases(raw, train, grid)
    fp_train = check_fingerprints(train, Y, (expected or {}).get('train'))
    Cq = collocation(cfg)
    print(f'Loaded {len(train)} training cases ({sum(a["rows"] for a in audit)} rows); {workers} worker(s); mode {mode}', flush=True)
    if mode == 'full':
        sel, cvp = select(X, Y, train, grid, cfg, workers, Cq)
        chosen = sel['selected']
        sel['selected_trial'] = sel['trials'][sel['selected_index']]
    elif mode == 'fast':
        if not selected:
            raise ValueError('fast mode needs the selected settings from a full run')
        chosen, sel, cvp = dict(selected['selected']), selected, None
    else:
        raise ValueError(mode)
    print(f'Selected (training cases only): {chosen}', flush=True)
    eq, eq_only, final_infos = fit_final(X, Y, train, grid, cfg, chosen, workers, Cq)
    (output / 'equation.json').write_text(json_text(eq))
    (output / 'equation_only.json').write_text(json_text(eq_only))
    lock = dict(selected=chosen, mode=mode, config=cfg, fit_ids=train.tolist(), equation_sha256=sha(output / 'equation.json'),
                equation_only_sha256=sha(output / 'equation_only.json'), code_sha256=sha(__file__),
                written_before_test_load=True, utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    (output / 'selection_lock.json').write_text(json_text(lock))
    # ---- the 37 test histories are opened only after the selected model is saved and locked ----
    V, Z, test_audit = load_cases(raw, test, grid)
    fp_test = check_fingerprints(test, Z, (expected or {}).get('test'))
    eq = json.loads((output / 'equation.json').read_text())
    Vq = queries(V, grid)
    p = equation_predict(eq, Vq).reshape(Z.shape)
    p_torch = torch_predict(eq, Vq).reshape(Z.shape)
    p_jc = jc_numpy(list(eq_only['theta'].values()), Vq, cfg['constants']).reshape(Z.shape)
    p_lookup = lookup(X, Y, V)
    p_train = equation_predict(eq, queries(X, grid)).reshape(Y.shape)
    eq_err = float(np.max(np.abs(p - p_torch)))
    assert eq_err <= 1e-10, eq_err
    for rel, h in protected.items():
        assert sha(root / rel) == h, rel
    refs = references(root)
    study = study_curves(eq, cfg, grid, chosen)
    by_cond = []
    for T, rate in sorted(set(map(tuple, V[:, :2]))):
        k = (V[:, 0] == T) & (V[:, 1] == rate)
        by_cond.append(dict(temperature=T, log10_rate=rate, cases=test[k].tolist(), jc_pinn=scores(Z[k], p[k]),
                            equation_only=scores(Z[k], p_jc[k])))
    _, _, d_test = equation_predict(eq, Vq, parts=True)
    result = dict(
        mode=mode, config=cfg, selected=chosen, train_ids=train.tolist(), test_ids=test.tolist(),
        training_audit=audit, test_audit=test_audit, selection=sel if mode == 'full' else dict(reused=True),
        final_fit=final_infos, equation_only_constants=eq_only['theta'], equation_only_at_bounds=eq_only['calibration']['at_bounds'],
        jc_pinn_constants=eq['theta'],
        test=dict(jc_pinn=scores(Z, p), equation_only=scores(Z, p_jc), lookup=scores(Z, p_lookup)),
        train_fit=dict(jc_pinn=scores(Y, p_train)), test_by_condition=by_cond,
        correction=dict(test_mean_abs_delta=float(np.mean(np.abs(d_test))), test_max_abs_delta=float(np.max(np.abs(d_test)))),
        monotonicity=monotonicity(eq, cfg), study_point=study, references=refs,
        checks=dict(numpy_vs_torch_max_error=eq_err, fingerprint_max_error_train=fp_train, fingerprint_max_error_test=fp_test,
                    parameters_per_member=sum(np.size(eq['members'][0][k]) for k in ('W1', 'b1', 'W2', 'b2', 'w3')) + 1,
                    protected_artifacts_unchanged=protected, selection_saved_before_test=True),
        fingerprints=dict(train=fingerprints(train, Y), test=fingerprints(test, Z)),
        versions=versions(), elapsed_seconds=time.perf_counter() - start, code_sha256=sha(__file__),
        split_sha256=sha(root / 'data/split.json'),
        caveat=('The 37 test cases were explored in earlier project stages, so this is not a blind test. Group-holdout '
                'errors were part of the selection score, so the selected model\'s group errors are optimistic. Stress '
                'units are inferred as MPa. No experimental validation; 300 C predictions are unvalidated.'))
    (output / 'results.json').write_text(json_text(result))
    write_csv(output / 'test_predictions.csv', test, grid, dict(Svm=Z, JC_PINN=p, equation_only=p_jc, lookup=p_lookup))
    if cvp is not None:
        write_csv(output / 'cv_predictions.csv', train, grid,
                  dict(Svm=Y, JC_PINN=cvp['model'], equation_only=cvp['equation_only'], lookup=cvp['lookup']))
    plots(output, grid, test, Z, p, p_jc, train, Y, None if cvp is None else cvp['model'],
          None if cvp is None else cvp['equation_only'], sel, study, refs)
    summary = dict(selected=chosen, test={k: {m: v[m] for m in ('mean_rmse', 'median_rmse', 'worst_rmse', 'mean_nrmse')}
                                          for k, v in result['test'].items()},
                   equation_only_constants=eq_only['theta'], numpy_vs_torch=eq_err, seconds=round(result['elapsed_seconds'], 1))
    print(json_text(summary), flush=True)
    return result


def replot(run_dir, root=ROOT):
    """Redraw a saved run's figures from its CSV/JSON files (no refitting, no new test scoring)."""
    run_dir = Path(run_dir)
    R = json.loads((run_dir / 'results.json').read_text())
    eq = json.loads((run_dir / 'equation.json').read_text())
    cfg = R['config']
    grid = strain_grid(cfg)

    def read(name):
        rows = {}
        with (run_dir / name).open() as f:
            for r in csv.DictReader(f):
                rows.setdefault(int(r['id']), []).append(r)
        return rows
    tst = read('test_predictions.csv')
    test, train = R['test_ids'], R['train_ids']
    col = lambda rows, ids, k: np.array([[float(r[k]) for r in rows[i]] for i in ids])
    Z, p, p_jc = (col(tst, test, k) for k in ('Svm', 'JC_PINN', 'equation_only'))
    Y = cv = cv_jc = None
    if (run_dir / 'cv_predictions.csv').exists():
        cvr = read('cv_predictions.csv')
        Y, cv, cv_jc = (col(cvr, train, k) for k in ('Svm', 'JC_PINN', 'equation_only'))
    sel = R['selection'] if 'trials' in R['selection'] else {}
    study = study_curves(eq, cfg, grid, R['selected'])
    plots(run_dir, grid, np.array(test), Z, p, p_jc, np.array(train), Y, cv, cv_jc, sel, study, R['references'])
    return study


# ----------------------------------------------------------------------------- using the delivered model
FINAL_RUN = 'reports/jc_pinn_20261107'
DATA_BOX = dict(temperature=(30.0, 200.0), log10_rate=(-5.0, -3.0), density=(2488.05, 2700.0), G=(23313.95, 25300.0))


def load_final_equation(root=ROOT):
    """The delivered, locked JC-PINN (checked against its selection lock)."""
    run = Path(root) / FINAL_RUN
    lock = json.loads((run / 'selection_lock.json').read_text())
    if sha(run / 'equation.json') != lock['equation_sha256']:
        raise ValueError('equation.json does not match selection_lock.json')
    return json.loads((run / 'equation.json').read_text())


def predict_curves(eq, conditions, grid=None):
    """Predicted Svm (MPa, inferred) on the E11 grid for rows [T degC, strain rate 1/s, density kg/m3, G MPa]."""
    grid = np.linspace(0.0002, 0.0999, 120) if grid is None else np.asarray(grid, dtype=float)
    c = np.atleast_2d(np.asarray(conditions, dtype=float))
    if np.any(c[:, 1] <= 0):
        raise ValueError('Strain rate must be positive.')
    X = np.c_[c[:, 0], np.log10(c[:, 1]), c[:, 2], c[:, 3]]
    return grid, equation_predict(eq, queries(X, grid)).reshape(len(c), len(grid))


def range_warnings(temperature, rate, density, G):
    """Plain-language warnings about where a query sits relative to the simulated data."""
    out = []
    lr = math.log10(rate) if rate > 0 else float('nan')
    for name, v, (lo, hi) in (('temperature', temperature, DATA_BOX['temperature']), ('log10 strain rate', lr, DATA_BOX['log10_rate']),
                              ('density', density, DATA_BOX['density']), ('shear modulus G', G, DATA_BOX['G'])):
        if not (lo - 1e-9 <= v <= hi + 1e-9):
            out.append(f'{name} {v:g} is outside the simulated range {lo:g} to {hi:g}: unvalidated extrapolation.')
    if 200 < temperature <= 300:
        out.append('Above 200 C there is no data and no physics penalty in the selected model; treat the curve as unverified.')
    if temperature not in (30.0, 100.0, 200.0) and 30 <= temperature <= 200:
        out.append('Temperature lies between the simulated levels 30, 100 and 200 C: interpolated.')
    if abs(lr - round(lr)) > 1e-9 and -5 <= lr <= -3:
        out.append('Strain rate lies between the simulated levels 1e-5, 1e-4 and 1e-3 /s: interpolated.')
    if abs(temperature - 200) < 1e-9 and abs(lr + 5) < 1e-9:
        out.append('200 C at 1e-5 /s has a single simulation (case 60, irregular collapse); errors there are largest.')
    return out


def versions():
    out = dict(python=platform.python_version(), numpy=np.__version__)
    for mod in ('torch', 'scipy', 'sklearn', 'matplotlib'):
        try:
            out[mod] = __import__(mod).__version__
        except ImportError:
            pass
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--root', type=Path, default=ROOT)
    ap.add_argument('--raw', type=Path, default=ROOT / 'TEAM_8_extracted_results_set_1',
                    help='folder holding simulation_matrix.csv and simulation_XXXX/STR_STR.OUT')
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--mode', choices=['full', 'fast'], default='full')
    ap.add_argument('--selected-from', type=Path, help='results.json of a full run (fast mode)')
    ap.add_argument('--workers', type=int, default=None)
    ap.add_argument('--fingerprints', type=Path, help='results.json whose curve fingerprints must match')
    a = ap.parse_args()
    selected = expected = None
    if a.selected_from:
        r = json.loads(a.selected_from.read_text())
        selected = dict(selected=r['selected'])
    if a.fingerprints:
        expected = json.loads(a.fingerprints.read_text())['fingerprints']
    run(a.root, a.raw, a.output, a.mode, selected, a.workers, expected)


if __name__ == '__main__':
    main()
