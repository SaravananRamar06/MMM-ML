"""Tests for the user materials generated from the locked JC-PINN.

umat/jc_pinn_umat.f (Abaqus UMAT) and umat/jc_pinn_usermat3d.F (ANSYS usermat3d). The generation tests need
only Python. The numerical tests compile each file with an offline driver and are skipped without gfortran.
"""
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'src'))

import jc_pinn as J  # noqa: E402
import verify_umat as V  # noqa: E402
import write_umat  # noqa: E402


class UmatGenerationTests(unittest.TestCase):
    def test_committed_files_match_locked_weights(self):
        for kind, (_, out) in write_umat.TARGETS.items():
            with self.subTest(kind):
                self.assertEqual(out.read_text(), write_umat.render(kind))

    def test_fixed_form_line_lengths(self):
        for _, out in write_umat.TARGETS.values():
            with self.subTest(out.name):
                self.assertTrue(all(len(line) <= 72 for line in out.read_text().splitlines()))


class _Numerics:
    KIND = None

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.exe = V.compile_driver(cls.tmp.name, cls.KIND)
        cls.eq = J.load_final_equation(ROOT)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_flow_stress_matches_python_model(self):
        r = V.check_flow(self.exe, self.eq, n=300)
        self.assertLess(r['max_rel_stress_error'], 1e-12)
        self.assertLess(r['max_rel_slope_error_vs_fd'], 1e-6)

    def test_uniaxial_on_curve_and_increment_independent(self):
        for c in V.check_uniaxial(self.exe, self.eq, plastic_tensor=self.KIND == 'ansys'):
            self.assertLess(c['increment_size_spread_MPa'], 1e-8)
            for run in c['runs'].values():
                self.assertLess(run['on_flow_curve_rel_error'], 1e-9)
                self.assertLess(run['strain_split_error'], 1e-10)
                self.assertLess(run.get('plastic_tensor_error', 0.0), 1e-12)

    def test_consistent_tangent(self):
        for t in V.check_tangent(self.exe):
            self.assertLess(t['rel_error'], 1e-6, t)

    def test_range_flags(self):
        for name, f in V.check_flags(self.exe).items():
            self.assertEqual(f['expected'], f['got'], name)


@unittest.skipUnless(shutil.which('gfortran'), 'gfortran not installed')
class AbaqusUmatTests(_Numerics, unittest.TestCase):
    KIND = 'abaqus'


@unittest.skipUnless(shutil.which('gfortran'), 'gfortran not installed')
class AnsysUsermatTests(_Numerics, unittest.TestCase):
    KIND = 'ansys'


if __name__ == '__main__':
    unittest.main()
