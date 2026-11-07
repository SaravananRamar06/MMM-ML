"""Porosity workflow (bracket/workflow): numerical contracts, evidence gates and comparable solver-result groups.

All assumed mappings and solver records below are synthetic test fixtures.
They are not professor-confirmed definitions or bracket simulation results.
"""
import csv
import io
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'bracket/workflow'))
import porosity_workflow as pw  # noqa: E402
import jc_pinn  # noqa: E402


def mapping():
    return {'status': 'assumed', 'reference_density_kg_m3': 2700., 'density_is_bulk_density': True,
            'modulus_by_phi': [{'phi': 0., 'G_MPa': 25300.}, {'phi': .0785, 'G_MPa': 23313.95}],
            'evidence': 'SYNTHETIC TEST FIXTURE — not a confirmed material relation.'}


def row(case='fixture-0', phi=0, **overrides):
    data = dict(case_id=case, independent_group_id=case, geometry_sha256='a' * 64,
                material_definition_id='synthetic-fixture', load_case_id='fixture-load',
                source_reference='synthetic test fixture, not a simulation', comparison_group_id='fixture-study',
                porosity_fraction=phi, temperature_C=100, force_x_N=0, force_y_N=1000, force_z_N=0,
                max_displacement_mm=1, max_von_mises_MPa=50)
    data.update(overrides)
    return data


def as_csv(rows):
    f = io.StringIO()
    writer = csv.DictWriter(f, fieldnames=pw.STRUCTURAL_FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return f.getvalue()


class PorosityPhysicsContracts(unittest.TestCase):
    def test_density_conversion_roundtrip_and_domains(self):
        self.assertAlmostEqual(pw.bulk_density(.03, 2700), 2619)
        self.assertAlmostEqual(pw.porosity_from_density(2488.05, 2700), .0785)
        for phi in (0., .03, .0785):
            self.assertAlmostEqual(pw.porosity_from_density(pw.bulk_density(phi, 2700), 2700), phi)
        for value in (True, -1, 1, 3, np.nan, np.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                pw.bulk_density(value, 2700)
        with self.assertRaises(ValueError):
            pw.porosity_from_density(2800, 2700)

    def test_unconfirmed_and_unaccepted_assumptions_cannot_predict(self):
        for status in ('unconfirmed', 'assumed'):
            m = mapping(); m['status'] = status
            with self.subTest(status=status), self.assertRaises(ValueError):
                pw.material_study(m, [0, .03], 100, 1e-4)
        m = mapping(); m['evidence'] = ''
        with self.assertRaises(ValueError):
            pw.material_study(m, [0], 100, 1e-4, allow_assumed=True)

    def test_explicit_assumed_study_matches_the_locked_jc_pinn(self):
        study = pw.material_study(mapping(), [0, .03, .0785], 100, 1e-4, allow_assumed=True)
        self.assertEqual(study['mapping_status'], 'assumed')
        self.assertEqual(study['kind'], 'conditional_material_response')
        self.assertIn('not a bracket', study['limitations'][0])
        eq = jc_pinn.load_final_equation(ROOT)
        grid = np.linspace(0.0002, 0.0999, 120)
        for curve in study['curves']:
            X5 = np.c_[np.tile([100, -4, curve['density_kg_m3'], curve['G_MPa']], (120, 1)), grid]
            np.testing.assert_allclose(curve['stress_MPa'], jc_pinn.equation_predict(eq, X5), rtol=0, atol=1e-12)
        self.assertAlmostEqual(study['curves'][1]['density_kg_m3'], 2619)

    def test_mapping_needs_unique_points_and_physical_density(self):
        for change in ({'density_is_bulk_density': False}, {'modulus_by_phi': []},
                       {'modulus_by_phi': [{'phi': 0, 'G_MPa': 25000}, {'phi': 0, 'G_MPa': 24000}]}):
            m = mapping(); m.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                pw.validated_mapping(m, allow_assumed=True)

    def test_mapping_and_material_extrapolation_are_rejected(self):
        for phi, temp, rate in (([.09], 100, 1e-4), ([0], 300, 1e-4), ([0], 100, 0),
                                ([0], 100, float('nan')), ([0], 100, 1e-6)):
            with self.subTest(values=(phi, temp, rate)), self.assertRaises(ValueError):
                pw.material_study(mapping(), phi, temp, rate, allow_assumed=True)


class SolverEvidenceContracts(unittest.TestCase):
    def test_paired_results_calculate_real_changes(self):
        result = pw.compare_solver_results(as_csv([row(), row('fixture-1', .03, max_displacement_mm=1.2, max_von_mises_MPa=55)]))
        r = result['rows'][1]
        self.assertEqual(r['baseline_case_id'], 'fixture-0')
        self.assertAlmostEqual(r['change_from_zero_porosity']['max_displacement_mm']['percent'], 20)
        self.assertAlmostEqual(r['change_from_zero_porosity']['max_von_mises_MPa']['difference'], 5)

    def test_changed_load_temperature_geometry_or_comparison_is_not_paired(self):
        for change in ({'force_y_N': 1100}, {'temperature_C': 200}, {'geometry_sha256': 'b' * 64},
                       {'comparison_group_id': 'different-study'}):
            with self.subTest(change=change):
                r = pw.compare_solver_results(as_csv([row(), row('fixture-1', .03, **change)]))['rows'][1]
                self.assertIsNone(r['baseline_case_id'])
                self.assertEqual(r['change_from_zero_porosity'], {})

    def test_bad_provenance_and_nonfinite_values_are_rejected(self):
        for change in ({'source_reference': ''}, {'geometry_sha256': 'unknown'}, {'porosity_fraction': 3},
                       {'max_displacement_mm': -1}, {'max_von_mises_MPa': 'nan'}, {'force_x_N': 'inf'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                pw.read_solver_results(as_csv([row(**change)]))

    def test_duplicate_cases_and_empty_files_are_rejected(self):
        for text in (as_csv([]), as_csv([row(), row()]), 'phi,stress\n0,1\n'):
            with self.assertRaises(ValueError):
                pw.read_solver_results(text)

    def test_ambiguous_zero_baselines_are_not_silently_selected(self):
        r = pw.compare_solver_results(as_csv([row(), row('fixture-2'), row('fixture-1', .03)]))['rows'][2]
        self.assertIsNone(r['baseline_case_id'])

    def test_zero_baseline_does_not_make_infinite_percent_changes(self):
        r = pw.compare_solver_results(as_csv([row(max_displacement_mm=0), row('fixture-1', .03)]))['rows'][1]
        self.assertIsNone(r['change_from_zero_porosity']['max_displacement_mm']['percent'])


if __name__ == '__main__':
    unittest.main()
