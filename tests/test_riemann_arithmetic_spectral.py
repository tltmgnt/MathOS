"""Independent checks of TECT-X arithmetic spectral candidate and proof limits."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_arithmetic_spectral import (
    FIRST_ZETA_ZERO_REFERENCE, TAU, arithmetic_shift, build_report,
    eigenvalue, inverse_main_term, main_term, von_mangoldt,
)


class ArithmeticSpectralTests(unittest.TestCase):
    def test_prime_powers_only(self):
        for n, p in [(2, 2), (4, 2), (8, 2), (9, 3), (25, 5), (27, 3),
                     (49, 7), (121, 11)]:
            self.assertAlmostEqual(von_mangoldt(n), math.log(p), places=13)
        for n in [1, 6, 10, 12, 15, 18, 30, 36, 72]:
            self.assertEqual(von_mangoldt(n), 0.0)

    def test_inverse_count_main_term(self):
        for n in [1, 2, 3, 8, 30, 50, 100, 256, 1024, 2048]:
            with self.subTest(n=n):
                self.assertAlmostEqual(main_term(inverse_main_term(n)), n, delta=1e-9*max(1, n))

    def test_unperturbed_eigenvalues_increasing(self):
        values = [eigenvalue(n, 0.0) for n in range(1, 128)]
        self.assertEqual(values, sorted(values))
        self.assertGreater(values[0], TAU * math.e)

    def test_arithmetic_shift_bounded_and_nontrivial(self):
        self.assertEqual(arithmetic_shift(1), 0)
        self.assertEqual(arithmetic_shift(6), 0)
        self.assertGreater(arithmetic_shift(2), 0)
        for n in range(1, 200):
            self.assertLess(arithmetic_shift(n), 1)
            self.assertGreaterEqual(arithmetic_shift(n), 0)

    def test_first_zeta_zero_is_below_spectrum(self):
        self.assertLess(FIRST_ZETA_ZERO_REFERENCE, TAU * math.e)
        self.assertLess(TAU * math.e, eigenvalue(1))

    def test_perturbation_distinguishes_trace(self):
        report = build_report(1024, 1.0)
        heat = report["spectrum_and_trace"]
        self.assertLess(heat["finite_heat_trace_arithmetic"],
                        heat["finite_heat_trace_unperturbed"])
        self.assertTrue(heat["first_ordinate_mismatch"])
        self.assertEqual(heat["trace_identity_status"], "NOT_DERIVED")

    def test_both_variants_match_count_bracket(self):
        for epsilon in [0.0, 0.25, 1.0]:
            report = build_report(1024, epsilon)
            for row in report["zero_count_comparison"]["rows"]:
                self.assertLessEqual(row["count_bracket_lower"], row["arithmetic_count"])
                self.assertLessEqual(row["arithmetic_count"], row["count_bracket_upper"])
            self.assertFalse(any(report["assurance"].values()))

    def test_all_required_obligations_remain_open(self):
        report = build_report(1024)
        self.assertEqual(len(report["missing_bridges"]), 4)
        self.assertIn("NOT_DERIVED", report["spectrum_and_trace"]["prime_explicit_formula_status"])
        self.assertFalse(report["assurance"]["spectral_zero_identity_established"])

    def test_input_rejections(self):
        for bad in [0, -1, 1.0, True, 5000]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                inverse_main_term(bad)
        for bad in [float("nan"), -0.1, 1.1, float("inf")]:
            with self.subTest(epsilon=bad), self.assertRaises(ValueError):
                eigenvalue(1, bad)
        with self.assertRaises(ValueError):
            build_report(256)
        with self.assertRaises(ValueError):
            main_term(0)

    def test_cli_produces_noncertifying_report(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "candidate.json"
            subprocess.run(
                [sys.executable, "-m", "mathos.research.riemann_arithmetic_spectral",
                 "--max-index", "1024", "--epsilon", "1", "--output", str(output)],
                check=True, capture_output=True, text=True,
            )
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(any(result["assurance"].values()))
            self.assertEqual(result["schema"], "mathos_tectx_rh_arithmetic_spectral/1")


if __name__ == "__main__":
    unittest.main()
