"""Explicit live checks; start app/server.py, then discover this exact filename.

python3 -m unittest discover -s tests -p live_model_app_check.py -v
Does not train, modify models, or write to the user's chat.
"""
import json
import os
from pathlib import Path
import unittest
from urllib.request import Request, urlopen

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:' + os.environ.get('MODEL_CHAT_PORT', '8766')


def request(path, text=None):
    if text is None:
        target = BASE + path
    else:
        target = Request(BASE + path, data=json.dumps({'text': text}).encode(),
                         headers={'Content-Type': 'application/json'})
    with urlopen(target, timeout=20) as response:
        assert response.status == 200
        return json.load(response)


class LiveModelAppTests(unittest.TestCase):
    def test_health_identifies_the_final_model(self):
        health = request('/api/health')
        self.assertTrue(health['ok'])
        self.assertEqual(health['primary'], 'mlp')
        self.assertEqual(health['models']['mlp'], 'runs/score/final_Svm/model.joblib')

    def test_user_query_reproduces_a_saved_test_prediction(self):
        with np.load(ROOT / 'runs/score/final_Svm/test_predictions.npz', allow_pickle=False) as saved:
            case_id = int(saved['test_ids'][0])
            expected = saved['prediction'][0].copy()
        manifest = json.loads((ROOT / 'data/manifest.json').read_text())
        case = next(m for m in manifest if m['id'] == case_id)
        temperature, log_rate, density, modulus = (
            case[k] for k in ('temperature', 'log10_strain_rate', 'density', 'shear_modulus'))
        text = f'stress curve at {temperature:g} C, rate {10 ** log_rate:g}, density {density:g}, G {modulus:g}'
        reply = request('/api/chat', text)
        primary = next(curve for curve in reply['curves'] if curve['primary'])
        self.assertEqual(primary['model'], 'mlp')
        self.assertEqual(len(primary['stress']), 120)
        np.testing.assert_allclose(primary['stress'], expected, rtol=0, atol=0.00051)
        self.assertTrue(np.isfinite(primary['stress']).all())

    def test_bad_rate_lift_request_and_extrapolation_are_not_silent(self):
        bad_rate = request('/api/chat', 'stress curve at 100 C, rate 0')
        self.assertIn('positive', bad_rate['reply'].lower())
        lift = request('/api/chat', 'predict coefficient of lift')
        self.assertNotIn('curves', lift)
        self.assertIn('lift', lift['reply'].lower())
        outside = request('/api/chat', 'stress curve at 300 C, rate 1e-5')
        self.assertTrue(outside.get('warnings'))


if __name__ == '__main__':
    unittest.main()
