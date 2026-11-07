"""Checks for the Johnson-Cook-governed physics-informed model (src/jc_pinn.py)."""
import copy
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import jc_pinn as J  # noqa: E402

CFG = J.load_config(ROOT / 'configs/jc_pinn.json')
CONST = CFG['constants']
THETA = np.array([150.0, 400.0, 0.8, 0.03, 1.1, 0.7, 0.05])     # A, B, n, C, m, q, r
X5 = np.array([[30.0, -5.0, 2700.0, 25300.0, 0.0002],
               [100.0, -4.0, 2619.0, 24541.0, 0.05],
               [200.0, -3.0, 2488.05, 23313.95, 0.0999],
               [300.0, -3.5, 2592.0, 24000.0, 0.03]])


def hand_jc(theta, row):
    A, B, n, C, m, q, r = theta
    T, lr, rho, G, e = row
    rate = 10 ** lr
    Ts = (T - 30.0) / (600.0 - 30.0)
    phi = 1 - rho / 2700.0
    return (A - B * e ** n) * (1 + C * math.log(rate / 1e-5)) * (1 - Ts ** m) * (G / 25300.0) ** q * (1 - phi) ** r


def tiny_cfg():
    c = copy.deepcopy(CFG)
    c['training'].update(adam_steps=30, lbfgs_max_iter=30)
    c['collocation']['points'] = 256
    c['calibration']['starts'] = 2
    return c


def synthetic(n=12, seed=0):
    rng = np.random.default_rng(seed)
    T = rng.choice([30.0, 100.0, 200.0], n)
    lr = rng.choice([-5.0, -4.0, -3.0], n)
    rho = rng.choice([2700.0, 2619.0, 2488.05], n)
    G = rng.choice([25300.0, 24541.0, 23313.95], n)
    X = np.c_[T, lr, rho, G]
    grid = np.linspace(0.0002, 0.0999, 15)
    Y = J.jc_numpy(THETA, J.queries(X, grid), CONST).reshape(n, -1) * (1 - 0.3 * (T[:, None] / 200) * grid / 0.1)
    return X, Y, grid


class EquationTests(unittest.TestCase):
    def test_equation_matches_hand_calculation(self):
        got = J.jc_numpy(THETA, X5, CONST)
        np.testing.assert_allclose(got, [hand_jc(THETA, r) for r in X5], rtol=1e-13)
        self.assertAlmostEqual(J.jc_numpy(THETA, X5[:1], CONST)[0], 150 - 400 * 0.0002 ** 0.8, places=10)

    def test_torch_equation_matches_numpy(self):
        torch = J._torch()
        got = J.jc_torch(torch.tensor(THETA), torch.tensor(X5), CONST).numpy()
        np.testing.assert_allclose(got, J.jc_numpy(THETA, X5, CONST), rtol=1e-14)

    def test_calibration_variables_round_trip_and_keep_stress_positive(self):
        v = J.cal_from_theta(THETA, CONST)
        np.testing.assert_allclose(J.theta_from_cal(v, CONST), THETA, rtol=1e-14)
        b = CFG['calibration']['bounds']
        rng = np.random.default_rng(1)
        for _ in range(200):
            v = np.array([rng.uniform(*b[k]) for k in J.CAL_VARS])
            A, B, n = J.theta_from_cal(v, CONST)[:3]
            self.assertGreater(A - B * 0.1 ** n, 0)

    def test_gradients_are_finite_at_reference_temperature(self):
        torch = J._torch()
        m = J.build_model(J.cal_from_theta(THETA, CONST), CFG, np.zeros(5), np.ones(5), True, 0)
        X = torch.tensor(X5[:1], requires_grad=True)       # T = T_ref, so T* = 0
        s, _, _ = m(X)
        s.sum().backward()
        self.assertTrue(torch.isfinite(m.u.grad).all())
        self.assertTrue(torch.isfinite(X.grad).all())
        lo, hi = m.lo.numpy(), m.hi.numpy()
        cv = m.cal_vars().detach().numpy()
        self.assertTrue(np.all(cv >= lo) and np.all(cv <= hi))


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.X, self.Y, self.grid = synthetic()
        self.Xq = J.queries(self.X, self.grid)
        self.xm, self.xs, self.ys = J.scalers(self.Xq, self.Y)

    def test_untrained_model_is_exactly_equation_one(self):
        torch = J._torch()
        m = J.build_model(J.cal_from_theta(THETA, CONST), CFG, self.xm, self.xs, False, 3)
        with torch.no_grad():
            s, base, d = m(torch.tensor(self.Xq))
        self.assertEqual(float(d.abs().max()), 0.0)
        np.testing.assert_allclose(s.numpy(), J.jc_numpy(THETA, self.Xq, CONST), rtol=1e-13)

    def test_exported_equation_matches_model_torch_and_json_reload(self):
        torch = J._torch()
        cand = dict(physics='trend', lambda_phys=0.001, theta_mode='joint')
        mem, info = J.train_member(self.Xq, self.Y.ravel(), J.collocation(tiny_cfg()), J.cal_from_theta(THETA, CONST),
                                   tiny_cfg(), self.xm, self.xs, self.ys, cand, 0)
        eq = json.loads(J.json_text(J.make_equation([mem, mem], CFG, self.xm, self.xs, self.ys, cand, [1, 2])))
        p = J.equation_predict(eq, self.Xq)
        np.testing.assert_allclose(J.torch_predict(eq, self.Xq), p, rtol=0, atol=1e-10)
        m = J.build_model(mem['cal_vars'], CFG, self.xm, self.xs, True, 0)
        with torch.no_grad():
            for name in ('W1', 'b1', 'W2', 'b2'):
                layer = {'W': 'weight', 'b': 'bias'}[name[0]]
                getattr(m, f'l{name[1]}').__getattr__(layer).copy_(torch.tensor(mem[name]))
            m.l3.weight.copy_(torch.tensor([mem['w3']]))
            m.l3.bias.copy_(torch.tensor([mem['b3']]))
            np.testing.assert_allclose(m(torch.tensor(self.Xq))[0].numpy(), p, rtol=1e-12)
        self.assertEqual(sum(np.size(mem[k]) for k in ('W1', 'b1', 'W2', 'b2', 'w3')) + 1, 385)
        self.assertTrue(np.isfinite(info['loss']))

    def test_physics_limits(self):
        """lambda=0 fits the data better than Eq. 1; a huge level penalty keeps the model at Eq. 1."""
        cfg = tiny_cfg()
        Cq = J.collocation(cfg)
        v = J.cal_from_theta(THETA, CONST)
        eq1 = J.jc_numpy(THETA, self.Xq, CONST)
        err = lambda p: np.sqrt(np.mean((p - self.Y.ravel()) ** 2))
        out = {}
        for lam, form in [(0.0, 'none'), (1e6, 'level')]:
            mem, _ = J.train_member(self.Xq, self.Y.ravel(), Cq, v, cfg, self.xm, self.xs, self.ys,
                                    dict(physics=form, lambda_phys=lam, theta_mode='frozen'), 0)
            out[form] = J.equation_predict(dict(constants=CONST, x_mean=list(self.xm), x_scale=list(self.xs),
                                                members=[mem]), self.Xq)
        self.assertLess(err(out['none']), 0.5 * err(eq1))
        self.assertLess(np.max(np.abs(out['level'] / eq1 - 1)), 1e-3)

    def test_trend_residual_uses_chain_rule_and_ignores_strain_shape(self):
        torch = J._torch()
        m = J.build_model(J.cal_from_theta(THETA, CONST), CFG, self.xm, self.xs, False, 0)
        Xc = torch.tensor(J.collocation(tiny_cfg()))
        with torch.no_grad():
            m.l3.weight.normal_()
            m.l1.weight[:, :4] = 0.0                       # correction depends on E11 only
        self.assertLess(float(J.physics_residual(m, Xc, 'trend')), 1e-28)
        with torch.no_grad():
            m.l1.weight.normal_()
        X = Xc[:64].clone().requires_grad_(True)
        g, = torch.autograd.grad(m.delta(X).sum(), X)
        h = 1e-6
        k = 0                                               # temperature column, raw units
        Xp, Xm = Xc[:64].clone(), Xc[:64].clone()
        Xp[:, k] += h
        Xm[:, k] -= h
        fd = ((m.delta(Xp) - m.delta(Xm)) / (2 * h)).detach()
        np.testing.assert_allclose(g[:, k].numpy(), fd.numpy(), rtol=1e-5, atol=1e-9)
        expect = float(((g * torch.tensor(self.xs))[:, :4] ** 2).sum(1).mean())
        self.assertAlmostEqual(float(J.physics_residual(m, Xc[:64], 'trend')), expect, places=12)


class ProtocolTests(unittest.TestCase):
    def test_splits_keep_cases_and_groups_disjoint(self):
        split = json.loads((ROOT / 'data/split.json').read_text())
        man = {m['id']: m for m in json.loads((ROOT / 'data/manifest.json').read_text())}
        ids = np.array(split['train'])
        X = np.array([[man[i]['temperature'], man[i]['log10_strain_rate'], man[i]['density'], man[i]['shear_modulus']]
                      for i in ids])
        sp = J.splits(X, ids, CFG)
        folds = [s for s in sp if s['kind'] == 'fold']
        groups = [s for s in sp if s['kind'] == 'group']
        self.assertEqual(len(folds), 3)
        self.assertEqual(len(groups), 9)
        self.assertEqual(sorted(sum((s['val_ids'] for s in folds), [])), sorted(ids.tolist()))
        for s in groups:
            held = {(man[i]['temperature'], man[i]['log10_strain_rate']) for i in s['val_ids']}
            fit = {(man[i]['temperature'], man[i]['log10_strain_rate']) for i in s['fit_ids']}
            self.assertEqual(len(held), 1)
            self.assertFalse(held & fit)
        self.assertFalse(set(ids.tolist()) & set(split['test']))

    def test_collocation_is_fixed_inside_box_and_target_free(self):
        a, b = J.collocation(CFG), J.collocation(CFG)
        np.testing.assert_array_equal(a, b)
        self.assertEqual(a.shape, (CFG['collocation']['points'], 5))
        box = CFG['collocation']['box']
        for j, k in enumerate(['temperature', 'log10_rate', 'density', 'G', 'E11']):
            self.assertTrue(np.all(a[:, j] >= box[k][0]) and np.all(a[:, j] <= box[k][1]))

    def test_raw_loader_interpolates_and_rejects_extrapolation(self):
        scratch = ROOT / 'work'
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as d:
            raw = Path(d)
            (raw / 'simulation_matrix.csv').write_text('Simulation_ID,temperature,strain_rate,density,shear_modulus\n'
                                                      '7,100,0.0001,2619,24541\n')
            (raw / 'simulation_0007').mkdir()
            e = np.linspace(0.0001, 0.1, 50)
            rows = [' '.join(['0', '0', repr(float(200 - 300 * x)), repr(float(x))] + ['0'] * 12) for x in e]
            (raw / 'simulation_0007/STR_STR.OUT').write_text(' '.join(J.HEADER) + '\n' + '\n'.join(rows) + '\n')
            grid = np.linspace(0.0002, 0.0999, 120)
            X, Y, audit = J.load_cases(raw, [7], grid)
            np.testing.assert_allclose(X, [[100, -4, 2619, 24541]])
            np.testing.assert_allclose(Y[0], 200 - 300 * grid, rtol=1e-12)
            self.assertEqual(audit[0]['rows'], 50)
            with self.assertRaises(ValueError):
                J.load_cases(raw, [7], np.linspace(0.00001, 0.0999, 5))

    @unittest.skipUnless((ROOT / 'work/raw_from_committed_curves/simulation_matrix.csv').exists(),
                         'run scripts/build_raw_from_committed_curves.py first')
    def test_lock_is_written_before_any_test_history_is_read(self):
        cfg = tiny_cfg()
        cfg['final']['seeds'] = [0]
        split = json.loads((ROOT / 'data/split.json').read_text())
        calls = []
        real = J.load_cases

        def spy(raw, ids, grid):
            is_test = set(map(int, ids)) == set(split['test'])
            calls.append((is_test, (out / 'selection_lock.json').exists()))
            return real(raw, ids, grid)
        with tempfile.TemporaryDirectory(dir=ROOT / 'work') as d:
            out = Path(d) / 'run'
            with patch.object(J, 'load_cases', side_effect=spy), patch.object(J, 'plots'), patch('builtins.print'):
                r = J.run(ROOT, ROOT / 'work/raw_from_committed_curves', out, mode='fast', workers=1, cfg=cfg,
                          selected=dict(selected=dict(physics='trend', lambda_phys=0.001, theta_mode='frozen')))
            self.assertEqual(calls, [(False, False), (True, True)])
            lock = json.loads((out / 'selection_lock.json').read_text())
            self.assertEqual(lock['equation_sha256'], J.sha(out / 'equation.json'))
            self.assertLessEqual(r['checks']['numpy_vs_torch_max_error'], 1e-10)
            self.assertEqual(len(r['test']['jc_pinn']['case_rmse']), 37)


if __name__ == '__main__':
    unittest.main()
