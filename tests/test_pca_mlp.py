"""Focused checks for fold isolation and portable curve inference."""
from pathlib import Path
import sys
import tempfile
import unittest

import joblib
import numpy as np
from sklearn.base import clone
from sklearn.exceptions import NotFittedError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from pca_mlp import PcaMLP


class CurveComponentTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(12)
        self.X = rng.uniform(-1, 1, (32, 2))
        strain = np.linspace(0, 1, 21)
        self.Y = 100 + 6 * self.X[:, :1] * strain + 3 * self.X[:, 1:] * np.sin(np.pi * strain)

    def make(self, **kwargs):
        return PcaMLP(n_components=2, hidden=(8, 8), n_init=1, seed=7, **kwargs)

    def test_fit_is_isolated_and_predict_does_not_refit(self):
        model = self.make().fit(self.X[:24], self.Y[:24])
        np.testing.assert_allclose(model.x_scaler_.mean_, self.X[:24].mean(0))
        np.testing.assert_allclose(model.pca_.mean_, self.Y[:24].mean(0))
        x_mean, y_mean = model.x_scaler_.mean_.copy(), model.pca_.mean_.copy()
        model.predict(np.full((3, 2), 1000.0))
        np.testing.assert_array_equal(model.x_scaler_.mean_, x_mean)
        np.testing.assert_array_equal(model.pca_.mean_, y_mean)
        self.assertEqual(model.n_fit_cases_, 24)

    def test_curve_learning_and_saved_reload(self):
        model = self.make(alpha=1e-5).fit(self.X[:24], self.Y[:24])
        prediction = model.predict(self.X[24:])
        self.assertEqual(prediction.shape, self.Y[24:].shape)
        self.assertLess(float(np.sqrt(np.mean((prediction - self.Y[24:]) ** 2))), 0.5)
        self.assertLess(model.training_reconstruction_rmse_, 1e-10)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'component.joblib'
            joblib.dump(model, path)
            np.testing.assert_array_equal(joblib.load(path).predict(self.X[24:]), prediction)

    def test_rank_one_and_input_validation(self):
        model = PcaMLP(n_components=1, hidden=(4,), n_init=1, seed=3).fit(self.X, self.Y)
        self.assertEqual(model.predict(self.X[:1]).shape, (1, 21))
        with self.assertRaises(ValueError):
            model.predict(np.ones((2, 3)))
        with self.assertRaises(ValueError):
            PcaMLP(n_components=40).fit(self.X, self.Y)
        with self.assertRaises(NotFittedError):
            PcaMLP().predict(self.X)
        self.assertEqual(clone(model).n_components, 1)


if __name__ == '__main__':
    unittest.main()
