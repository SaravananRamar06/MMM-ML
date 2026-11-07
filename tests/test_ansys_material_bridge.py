"""Tests for the ANSYS Engineering Data material bridge (bracket/tools), driven by the JC-PINN."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bracket/tools'))
sys.path.insert(0, str(ROOT / 'src'))

import ansys_material_bridge as amb  # noqa: E402
import jc_pinn  # noqa: E402
import numpy as np  # noqa: E402


class AnsysMaterialBridgeTests(unittest.TestCase):
    def test_predict_curve_shape_and_bounds(self):
        strains, stresses = amb.predict_curve(temperature=100.0, rate=1e-4, density=2619.0, G=24541.0)
        _, expected = jc_pinn.predict_curves(jc_pinn.load_final_equation(ROOT), [[100.0, 1e-4, 2619.0, 24541.0]])
        np.testing.assert_allclose(stresses, expected[0], rtol=0, atol=1e-12)
        self.assertEqual(len(strains), 120)
        self.assertEqual(len(stresses), 120)
        # Verify finite and physically positive stresses
        self.assertTrue(np.all(np.isfinite(strains)))
        self.assertTrue(np.all(np.isfinite(stresses)))
        self.assertTrue(np.all(stresses > 0))

    def test_format_tabular_csv_total_and_plastic(self):
        strains = np.array([1e-6, 1e-4, 1e-2])
        stresses = np.array([150.0, 180.0, 250.0])

        # Raw total strain
        csv_total = amb.format_tabular_csv(strains, stresses)
        self.assertIn("Total Strain", csv_total)
        self.assertIn("1.00000000e-06,150.000000", csv_total)

        # Calculated plastic strain with user-supplied E = 70000 MPa
        csv_plastic = amb.format_tabular_csv(strains, stresses, youngs_modulus=70000.0)
        self.assertIn("Plastic Strain", csv_plastic)
        self.assertIn("Young's Modulus E = 70000", csv_plastic)

    def test_format_apdl_snippet(self):
        strains = np.array([1e-6, 1e-4])
        stresses = np.array([150.0, 180.0])

        apdl_raw = amb.format_apdl_snippet(strains, stresses, mat_id=2, temperature=100.0)
        self.assertIn("TB,PLAS,2,1,2,MISO", apdl_raw)
        self.assertIn("TBTEMP,100", apdl_raw)
        self.assertIn("TBPT,DEFI,1.00000000e-06,150.000000", apdl_raw)

        apdl_miso = amb.format_apdl_snippet(strains, stresses, mat_id=1, youngs_modulus=69000.0)
        self.assertIn("MP,EX,1,69000", apdl_miso)
        self.assertIn("TB,MISO,1,1,2", apdl_miso)

    def test_format_xml_snippet(self):
        strains = np.array([1e-6, 1e-4])
        stresses = np.array([150.0, 180.0])

        xml = amb.format_xml_snippet(strains, stresses, mat_name="AlSi10Mg_Test")
        self.assertIn('<Material name="AlSi10Mg_Test">', xml)
        self.assertIn('<Point strain="1.00000000e-06" stress="150.000000" />', xml)


if __name__ == '__main__':
    unittest.main()
