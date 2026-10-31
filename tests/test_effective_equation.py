"""Scientific numerical checks and training/test isolation for equation screening."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
from scipy.optimize._numdiff import approx_derivative

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from effective_equation import basis, load_training, numerical_checks, predict, response


class EquationTests(unittest.TestCase):
    def test_analytical_parameter_jacobian(self):
        rng = np.random.default_rng(42)
        B = np.c_[np.ones(4), rng.normal(size=(4, 5))]
        strain = np.linspace(.0002, .0999, 17)
        for family, count in [('exponential', 3), ('power_exponential', 4)]:
            beta = rng.normal(0, .2, (count, 6)).ravel()
            _, J = response(beta, B, strain, family, jacobian=True)
            numeric = approx_derivative(lambda b: response(b, B, strain, family).ravel(), beta)
            np.testing.assert_allclose(J, numeric, atol=1e-7, rtol=1e-5)

    def test_strain_scaling_and_ode(self):
        self.assertTrue(numerical_checks()['passed'])

    def test_n_one_reduces_to_simple_equation(self):
        from scipy.special import logit
        b = np.zeros((3, 6)); b[:, 0] = np.log([20, 100, 1.2])
        extended = np.vstack([b, np.zeros(6)])
        extended[3, 0] = logit((1-.1)/7.9)
        B = np.ones((2, 6)); e = np.linspace(.0002, .0999, 11)
        np.testing.assert_allclose(response(b, B, e, 'exponential'),
                                   response(extended, B, e, 'power_exponential'), rtol=1e-14)

    def test_predict_uses_frozen_scalers_and_json_reload(self):
        model = dict(family='exponential', mean=[1,2,3,4], scale=[1,2,3,4],
                     beta=np.zeros((3, 6)).tolist(), stress_scale=100., reference=.1)
        before = json.dumps(model)
        X = np.array([[1,2,3,4], [100,200,300,400]])
        p = predict(model, X, [.01, .05])
        self.assertEqual(before, json.dumps(model))
        np.testing.assert_array_equal(p, predict(json.loads(before), X, [.01, .05]))

    def test_loader_never_opens_test_history(self):
        scratch = Path(__file__).resolve().parents[1]/'work'
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temp:
            root = Path(temp)
            split = root/'split.json'
            split.write_text(json.dumps(dict(train=[2], test=[1])))
            with (root/'simulation_matrix.csv').open('w', newline='') as f:
                w = csv.writer(f)
                w.writerow(['Simulation_ID','temperature','strain_rate','density','shear_modulus'])
                w.writerow([2,30,.001,2700,25300])
            folder = root/'simulation_0002'; folder.mkdir()
            a = np.zeros((3, 16)); a[:,3] = [.001,.05,.1]
            a[:,2] = a[:,9] = 100; a[:,1] = a[:,3]; a[:,15] = 303.15
            header = 'TIME Evm Svm E11 E22 E33 E23 E13 E12 SCAU11 SCAU22 SCAU33 SCAU23 SCAU13 SCAU12 TEMP'
            np.savetxt(folder/'STR_STR.OUT', a, header=header, comments='')
            ids, X, Y, audit, _ = load_training(root, split, np.array([.002,.09]), expected_train=1, expected_test=1)
            self.assertEqual(ids.tolist(), [2])
            self.assertEqual([r['id'] for r in audit], [2])
            self.assertFalse((root/'simulation_0001').exists())
            split.write_text(json.dumps(dict(train=[2], test=[2])))
            with self.assertRaises(ValueError):
                load_training(root, split, np.array([.002,.09]), expected_train=1, expected_test=1)


if __name__ == '__main__':
    unittest.main()
