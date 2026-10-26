"""Numerical equivalence, serialization, validation and concurrent inference."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import tempfile
import unittest

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from query_runtime import QueryRuntime


class QueryRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = joblib.load(ROOT / 'runs/score/final_Svm/model.joblib')
        cls.runtime = QueryRuntime.from_model(cls.model)
        manifest = json.loads((ROOT / 'data/manifest.json').read_text())
        cls.X = np.array([[m[k] for k in ('temperature', 'log10_strain_rate', 'density', 'shear_modulus')]
                          for m in manifest])

    def test_all_cases_and_random_conditions_match_existing_model(self):
        rng = np.random.default_rng(271)
        lo, hi = self.X.min(0), self.X.max(0)
        X = np.concatenate([self.X, rng.uniform(lo, hi, (100, 4)),
                            [[300, -6, 2400, 22000]]])
        np.testing.assert_allclose(self.runtime.predict(X), self.model.predict(X), rtol=1e-12, atol=1e-11)

    def test_roundtrip_batch_single_and_concurrent_reads(self):
        X = self.X[:5]
        expected = self.runtime.predict(X)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'runtime.npz'
            self.runtime.save(path)
            restored = QueryRuntime.load(path)
            np.testing.assert_array_equal(restored.predict(X), expected)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(self.runtime.predict, [x[None] for x in X]))
        np.testing.assert_allclose(np.concatenate(results), expected, rtol=1e-12, atol=1e-11)
        self.assertFalse(self.runtime.weights[0].flags.writeable)

    def test_empty_and_invalid_inputs(self):
        self.assertEqual(self.runtime.predict(np.empty((0, 4))).shape, (0, 120))
        for X in ([30, -4, 2700, 25300], [[30, -4, 2700]], [[np.nan, -4, 2700, 25300]],
                  [[30, np.inf, 2700, 25300]]):
            with self.subTest(X=X), self.assertRaises(ValueError):
                self.runtime.predict(X)


if __name__ == '__main__':
    unittest.main()
