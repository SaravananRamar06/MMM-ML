"""Re-run the improvement screens (training cases only, no test data) and save them as evidence.

Asked on 7 Nov 2026 whether the model can be improved, these screens decided that the locked JC-PINN is submitted as is:
  1. training recipe: more L-BFGS iterations, weaker weight decay, a wider network (3 training folds, 3 seeds);
  2. curve-family floor: best per-curve fit of A - B*eps^n (and alternatives) to each training curve;
  3. correction forms and backbones: bounded or additive corrections, and an extended Equation 1 whose B and n depend on
     temperature and rate, on all 12 training-side splits (2 seeds), scored with the pre-registered balanced score.
Output: reports/jc_pinn_20261107/improvement_screen.json
Usage: python scripts/screen_improvements.py [raw folder]   (default: work/raw_from_committed_curves)
"""
import copy
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
from scipy.optimize import least_squares

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
import jc_pinn as J  # noqa: E402

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'work/raw_from_committed_curves'
cfg = J.load_config(root / 'configs/jc_pinn.json')
grid = J.strain_grid(cfg)
CONST = cfg['constants']
ids = np.array(json.loads((root / 'data/split.json').read_text())['train'])
X, Y, _ = J.load_cases(RAW, ids, grid)          # the 36 training cases only
SP = J.splits(X, ids, cfg)


# ---------------------------------------------------------------- 1. training recipe (3 folds, current architecture)
def recipe():
    folds = [s for s in SP if s['kind'] == 'fold']
    Cq = J.collocation(cfg)
    cand = dict(physics='none', lambda_phys=0.0, theta_mode='joint')
    variants = {'current (alpha 1, 2500 L-BFGS iterations)': dict(alpha=1.0, it=2500, h=[16, 16]),
                'alpha 1, 8000 iterations': dict(alpha=1.0, it=8000, h=[16, 16]),
                'alpha 0.3, 8000 iterations': dict(alpha=0.3, it=8000, h=[16, 16]),
                '32-32 network, alpha 1, 8000 iterations': dict(alpha=1.0, it=8000, h=[32, 32])}
    tasks = []
    for vn, v in variants.items():
        c = copy.deepcopy(cfg)
        c['training'].update(alpha=v['alpha'], lbfgs_max_iter=v['it'])
        c['network']['hidden'] = v['h']
        for si, s in enumerate(folds):
            Xq, yq = J.queries(X[s['fit']], grid), Y[s['fit']].ravel()
            xm, xs, ys = J.scalers(Xq, Y[s['fit']])
            vc, _ = J.calibrate_jc(Xq, yq, c, ys)
            tasks += [((vn, si, seed), Xq, yq, J.queries(X[s['val']], grid), Cq, vc, c, xm, xs, ys, cand, seed) for seed in (0, 1, 2)]
    res = {}
    for (vn, si, seed), lp, _, _ in J._run_tasks(tasks, 4, 'recipe'):
        res.setdefault((vn, si), []).append(lp)
    out = {}
    for vn in variants:
        cv = np.empty_like(Y)
        for si, s in enumerate(folds):
            cv[s['val']] = np.exp(np.mean(res[(vn, si)], axis=0)).reshape(len(s['val']), -1)
        out[vn] = J.scores(Y, cv)['mean_rmse']
    return out


# ---------------------------------------------------------------- 2. curve-family floor (per-curve free constants)
def floor():
    def fit(y, f, p0, lo, hi):
        p0 = np.clip(p0, np.array(lo) + 1e-9, np.array(hi) - 1e-9)
        return float(np.sqrt(np.mean(least_squares(lambda p: f(p) - y, p0, bounds=(lo, hi), max_nfev=5000).fun ** 2)))
    fam = {'A - B eps^n (3 constants per curve)': [], 'A - B eps^n - D eps^k (5 per curve)': [], 'cubic polynomial (4 per curve)': []}
    for y in Y:
        d = max(y[0] - y[-1], 1)
        fam['A - B eps^n (3 constants per curve)'].append(min(fit(y, lambda p: p[0] - p[1] * grid ** p[2], [y[0], d / .1 ** n0, n0], [0, 0, .05], [500, 1e7, 8]) for n0 in (.6, 1, 1.5, 3)))
        fam['A - B eps^n - D eps^k (5 per curve)'].append(min(fit(y, lambda p: p[0] - p[1] * grid ** p[2] - p[3] * grid ** p[4],
                                                                  [y[0], .7 * d / .1 ** .8, .8, .3 * d / .1 ** k0, k0], [0, 0, .05, 0, 1], [500, 1e7, 8, 1e12, 30]) for k0 in (2, 4, 8)))
        fam['cubic polynomial (4 per curve)'].append(float(np.sqrt(np.mean((np.polyval(np.polyfit(grid, y, 3), grid) - y) ** 2))))
    return {k: dict(mean=float(np.mean(v)), median=float(np.median(v)), worst=float(np.max(v)), worst_case=int(ids[int(np.argmax(v))])) for k, v in fam.items()}


# ---------------------------------------------------------------- 3. correction forms and the extended backbone
def ext_np(p, Xq):
    A, b0, n0, Cc, m, q, r, bT, bL, bTL, nT, nL, nTL = p
    T, lr, rho, G, e = Xq.T
    Ts = np.clip((T - 30) / 570, 0, None)
    Tt, L = Ts / 0.3, np.log(10) * (lr + 5) / np.log(100)
    n = n0 * np.exp(nT * Tt + nL * L + nTL * Tt * L)
    B = A * 0.99 / (1 + np.exp(-(b0 + bT * Tt + bL * L + bTL * Tt * L))) / 0.1 ** n
    Tm = np.where(Ts > 0, np.maximum(Ts, 1e-300) ** m, 0)
    return (A - B * e ** n) * (1 + Cc * np.log(10) * (lr + 5)) * (1 - Tm) * (G / 25300) ** q * (rho / 2700) ** r


ELO, EHI = [1, -10, .05, 0, .05, 0, 0] + [-10] * 6, [2000, 10, 5, 2, 20, 10, 20] + [10] * 6


def ext_cal(Xq, y, ys):
    best, rng = None, np.random.default_rng(0)
    for s in range(5):
        p0 = np.array([150, 0, .8, .03, 1.1, .7, .01] + [0] * 6) + (s > 0) * np.r_[rng.normal(0, [10, .5, .1, .01, .2, .1, .005]), rng.normal(0, .3, 6)]
        r = least_squares(lambda p: (ext_np(p, Xq) - y) / ys, np.clip(p0, ELO, EHI), bounds=(ELO, EHI), max_nfev=3000)
        if best is None or r.cost < best.cost:
            best = r
    return best.x


def form_task(args):
    key, Xq, yq, Vq, v, xm, xs, ys, var, seed = args
    torch = J._torch()
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    nn = torch.nn
    l1, l2, l3 = nn.Linear(5, 16), nn.Linear(16, 16), nn.Linear(16, 1)
    nn.init.zeros_(l3.weight)
    nn.init.zeros_(l3.bias)
    base_f = (lambda Xa: ext_np(v, Xa)) if var['backbone'] == 'ext' else (lambda Xa: J.jc_numpy(J.theta_from_cal(v, CONST), Xa, CONST))
    bd, bv = torch.tensor(base_f(Xq)), torch.tensor(base_f(Vq))
    Xd, yd, Vd = torch.tensor((Xq - xm) / xs), torch.tensor(yq), torch.tensor((Vq - xm) / xs)
    raw = lambda Z: l3(torch.tanh(l2(torch.tanh(l1(Z))))).squeeze(1)

    def out(Z, b):
        r = raw(Z)
        if var['form'] == 'exp':
            return b * torch.exp(r)
        if var['form'] == 'bexp':
            return b * torch.exp(var['c'] * torch.tanh(r / var['c']))
        return b + ys * r
    params = list(l1.parameters()) + list(l2.parameters()) + list(l3.parameters())
    W, N = [l1.weight, l2.weight, l3.weight], len(yq)
    loss = lambda: torch.mean(((out(Xd, bd) - yd) / ys) ** 2) + var['alpha'] / N * sum((w ** 2).sum() for w in W)
    opt = torch.optim.Adam(params, lr=0.005)
    for _ in range(1500):
        opt.zero_grad()
        lv = loss()
        lv.backward()
        opt.step()
    lb = torch.optim.LBFGS(params, lr=1, max_iter=2500, max_eval=3125, history_size=50, tolerance_grad=1e-10,
                           tolerance_change=1e-14, line_search_fn='strong_wolfe')

    def cl():
        lb.zero_grad()
        lv = loss()
        lv.backward()
        return lv
    lb.step(cl)
    with torch.no_grad():
        return key, out(Vd, bv).numpy()


def forms():
    variants = {'bounded exp correction (x1/3..x3), alpha 0.1': dict(backbone='sep', form='bexp', c=math.log(3), alpha=0.1),
                'bounded exp correction, alpha 0.01': dict(backbone='sep', form='bexp', c=math.log(3), alpha=0.01),
                'additive correction, alpha 0.01': dict(backbone='sep', form='add', alpha=0.01),
                'additive correction, alpha 0.1': dict(backbone='sep', form='add', alpha=0.1),
                'extended Equation 1 backbone (B, n depend on T and rate), exp correction, alpha 1': dict(backbone='ext', form='exp', alpha=1.0)}
    tasks, ext_alone = [], {}
    for si, s in enumerate(SP):
        Xq, yq = J.queries(X[s['fit']], grid), Y[s['fit']].ravel()
        xm, xs, ys = J.scalers(Xq, Y[s['fit']])
        Vq = J.queries(X[s['val']], grid)
        vsep, _ = J.calibrate_jc(Xq, yq, cfg, ys)
        vext = ext_cal(Xq, yq, ys)
        ext_alone[si] = ext_np(vext, Vq).reshape(len(s['val']), -1)
        for vn, var in variants.items():
            tasks += [((vn, si, seed), Xq, yq, Vq, vext if var['backbone'] == 'ext' else vsep, xm, xs, ys, var, seed) for seed in (0, 1)]
    pool = J._pool(4)
    out = pool.map(form_task, tasks)
    pool.close()
    R = {}
    for (vn, si, seed), p in out:
        R.setdefault((vn, si), []).append(p)

    def summarise(get):
        cv, gs = np.empty_like(Y), []
        for si, s in enumerate(SP):
            p = get(si, s)
            if s['kind'] == 'fold':
                cv[s['val']] = p
            else:
                gs.append(J.scores(Y[s['val']], p)['mean_rmse'])
        c, g = J.scores(Y, cv)['mean_rmse'], float(np.mean(gs))
        return dict(cv=c, groups=g, score=.5 * (c + g), group_rmse=gs)
    res = {}
    for vn, var in variants.items():
        res[vn] = summarise(lambda si, s, vn=vn, var=var: (np.exp(np.mean(np.log(np.maximum(np.array(R[(vn, si)]), 1e-6)), 0))
                                                            if var['form'] != 'add' else np.mean(R[(vn, si)], 0)).reshape(len(s['val']), -1))
    res['extended Equation 1 alone (13 constants, no network)'] = summarise(lambda si, s: ext_alone[si])
    return res


if __name__ == '__main__':
    t0 = time.time()
    R0 = json.loads((root / 'reports/jc_pinn_20261107/results.json').read_text())
    C0 = json.loads((root / 'reports/jc_pinn_20261107/control_no_equation.json').read_text())
    out = dict(purpose='Improvement screens run after the locked model, on the 36 training cases only. They informed the decision to submit the locked JC-PINN unchanged; no test data were used.',
               reference=dict(current_jc_pinn=dict(cv=R0['selection']['selected_trial']['cv']['mean_rmse'], groups=R0['selection']['selected_trial']['group_mean_rmse'],
                                                   score=R0['selection']['selected_trial']['score']),
                              same_network_equation_off=dict(cv=C0['control']['cv_mean_rmse'], groups=C0['control']['group_mean_rmse'], score=C0['control']['score'])),
               recipe_3fold_cv=recipe(), curve_family_floor=floor(), correction_forms_balanced=forms())
    out['seconds'] = round(time.time() - t0, 1)
    out['versions'] = J.versions()
    (root / 'reports/jc_pinn_20261107/improvement_screen.json').write_text(J.json_text(out), newline='\n')  # LF on every OS: reports/** is byte-checked (.gitattributes)
    print(J.json_text({k: v for k, v in out.items() if k not in ('purpose',)}))
