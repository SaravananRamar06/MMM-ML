"""Explicit live checks; synthetic input is never saved as physical evidence."""
import json
import os
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = 'http://127.0.0.1:' + os.environ.get('MODEL_CHAT_PORT', '8766')


def request(path, payload=None):
    target = BASE + path
    if payload is not None:
        target = Request(target, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    try:
        with urlopen(target, timeout=20) as response:
            return response.status, response.read().decode()
    except HTTPError as error:
        return error.code, error.read().decode()


class LivePorosityWorkflow(unittest.TestCase):
    def test_workflow_page_and_missing_physics_are_visible(self):
        status, page = request('/workflow')
        self.assertEqual(status, 200)
        self.assertIn('not solve the bracket or wing', page)
        status, body = request('/api/workflow')
        data = json.loads(body)
        self.assertEqual(status, 200)
        self.assertFalse(data['physical_completion'])
        self.assertTrue(data['material_model_available'])

    def test_undeclared_porosity_relation_is_rejected(self):
        status, body = request('/api/porosity-study', {'mapping': {'status': 'unconfirmed'},
                                                     'phi_values': [0, .03], 'temperature_C': 100,
                                                     'strain_rate_s': 1e-4})
        self.assertEqual(status, 400)
        self.assertIn('confirmed mapping', json.loads(body)['error'])

    def test_explicit_exploration_is_labelled_and_finite(self):
        status, body = request('/api/porosity-study', {
            'mapping': {'status': 'assumed', 'density_is_bulk_density': True,
                        'reference_density_kg_m3': 2700,
                        'modulus_by_phi': [{'phi': 0, 'G_MPa': 25300}, {'phi': .0785, 'G_MPa': 23313.95}],
                        'evidence': 'SYNTHETIC LIVE TEST — not a confirmed material relation'},
            'phi_values': [0, .03], 'temperature_C': 100, 'strain_rate_s': 1e-4, 'allow_assumed': True})
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data['mapping_status'], 'assumed')
        self.assertEqual(data['kind'], 'conditional_material_response')
        self.assertEqual(len(data['curves'][0]['stress_source_units']), 120)
        self.assertNotIn('CL', data)

    def test_bad_solver_file_and_bad_mapping_shape_return_clear_errors(self):
        for path, payload in [('/api/solver-results', {'csv': 'phi,stress\n0,100\n'}),
                              ('/api/porosity-study', {'mapping': [], 'phi_values': [0],
                                                      'temperature_C': 100, 'strain_rate_s': 1e-4})]:
            with self.subTest(path=path):
                status, body = request(path, payload)
                self.assertEqual(status, 400)
                self.assertIn('error', json.loads(body))


if __name__ == '__main__':
    unittest.main()
