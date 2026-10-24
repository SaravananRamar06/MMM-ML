"""Checks for the chat parser, the split, the out-of-range warnings, and the shared scorer's rules."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "app"), str(ROOT / "src")]

from nlu import parse  # noqa: E402
from predict import warnings_for  # noqa: E402


class ParserTests(unittest.TestCase):
    def test_temperatures_units_and_defaults(self):
        p = parse("compare 30, 100 and 200 °C at 1e-3 /s")
        self.assertEqual([c["temperature"] for c in p["conditions"]], [30, 100, 200])
        self.assertTrue(all(c["rate"] == 1e-3 for c in p["conditions"]))
        self.assertEqual(p["defaults_used"], ["density", "G"])

    def test_kelvin_gpa_and_strain_query(self):
        p = parse("T=373.15 K, strain rate 0.0001, density 2619, G 24.5 GPa, stress at 5% strain")
        c = p["conditions"][0]
        self.assertAlmostEqual(c["temperature"], 100.0)
        self.assertEqual((c["rate"], c["density"], c["G"]), (1e-4, 2619.0, 24500.0))
        self.assertAlmostEqual(p["strain_query"], 0.05)

    def test_intents_and_lift_is_flagged(self):
        self.assertEqual(parse("help")["intent"], "help")
        self.assertEqual(parse("what ranges are valid?")["intent"], "ranges")
        self.assertEqual(parse("how accurate is it?")["intent"], "accuracy")
        self.assertIn("lift", parse("what porosity gives max lift")["notes"])

    def test_bare_scientific_number_is_the_rate(self):
        p = parse("compare 30 and 200 C at 1e-3")
        self.assertEqual([c["rate"] for c in p["conditions"]], [1e-3, 1e-3])
        self.assertNotIn("rate", p["defaults_used"])

    def test_strain_rate_is_not_read_as_strain(self):
        self.assertIsNone(parse("at 100 C, strain rate 1e-4")["strain_query"])


class GuardTests(unittest.TestCase):
    def test_out_of_range_warnings(self):
        self.assertEqual(warnings_for(30, -4, 2700, 25300), [])
        self.assertTrue(any("outside the training range" in w for w in warnings_for(300, -4, 2700, 25300)))
        self.assertTrue(any("case 60" in w for w in warnings_for(200, -5, 2700, 25300)))
        self.assertFalse(any("case 60" in w for w in warnings_for(300, -5, 2700, 25300)))

    def test_saved_split_is_disjoint_and_complete(self):
        split = json.loads((ROOT / "data" / "split.json").read_text())
        manifest = json.loads((ROOT / "data" / "manifest.json").read_text())
        train, test = set(split["train"]), set(split["test"])
        self.assertFalse(train & test)
        self.assertEqual(train | test, {m["id"] for m in manifest})
        self.assertEqual((len(train), len(test)), (36, 37))


if __name__ == "__main__":
    unittest.main()
