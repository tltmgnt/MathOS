"""Exact-rational regression tests for the uniform Hilbert--Polya no-go family."""
import json
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_uniform_hp_barrier import (
    BUDGET, E_LOWER, FIRST_ZERO_UPPER, PI_LOWER, audit, lower_spectral_margin,
)


class UniformHPBarrierTests(unittest.TestCase):
    def test_default_margin_positive_exact(self):
        expected = Fraction(2) * Fraction(157, 50) * Fraction(271, 100) - Fraction(14, 5) - Fraction(707, 50)
        self.assertEqual(lower_spectral_margin(BUDGET), expected)
        self.assertGreater(expected, 0)

    def test_simple_budget_increase_decreases_margin(self):
        a = lower_spectral_margin(Fraction(1))
        b = lower_spectral_margin(Fraction(2))
        self.assertEqual(a - b, 1)

    def test_external_gamma_upper_is_below_pi_e_lower_budget(self):
        self.assertGreater(2 * PI_LOWER * E_LOWER - BUDGET, FIRST_ZERO_UPPER)

    def test_report_rejects_hilbert_polya_claim(self):
        result = audit()
        self.assertFalse(any(result["assurance"].values()))
        self.assertFalse(result["obstruction"]["zero_free_factor_identity_possible"])
        self.assertEqual(result["status"], "UNIFORM_BOUNDED_PERTURBATION_FAMILY_REFUTED_AS_HILBERT_POLYA")

    def test_covers_all_bounded_selfadjoint_not_only_jacobi(self):
        result = audit()
        self.assertIn("all B", result["candidate_family"]["universality"])
        self.assertTrue(result["candidate_family"]["compact_resolvent"])
        self.assertTrue(result["candidate_family"]["no_zero_inputs_in_operator"])

    def test_cannot_promote_outside_valid_budget(self):
        with self.assertRaisesRegex(ValueError, "does not apply"):
            audit(Fraction(3))

    def test_invalid_norm_bounds(self):
        for norm in [Fraction(-1), 1.0, None]:
            with self.subTest(norm=norm), self.assertRaises(ValueError):
                lower_spectral_margin(norm)

    def test_rejects_invalid_sample_sizes(self):
        for size in [15, 4097, True, 12.0]:
            with self.subTest(size=size), self.assertRaises(ValueError):
                audit(BUDGET, size)

    def test_boundaries_without_numeric_zero_fitting(self):
        r = audit(Fraction(0), 16)
        self.assertGreater(Fraction(r["strict_certified_rational_inputs"]["margin_strictly_greater_than"]), 0)
        self.assertTrue(r["finite_regression"]["finite_numbers_do_not_prove_global_result"])

    def test_alternate_valid_budget(self):
        r = audit(Fraction(5, 2), 32)
        self.assertEqual(r["strict_certified_rational_inputs"]["norm_budget"], "5/2")
        self.assertFalse(r["assurance"]["riemann_hypothesis_proved"])

    def test_cli_and_noncertification(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "barrier.json"
            subprocess.run(
                [sys.executable, "-m", "mathos.research.riemann_uniform_hp_barrier",
                 "--sample-size", "32", "--output", str(target)],
                check=True, text=True, capture_output=True,
            )
            r = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(r["schema"], "mathos_tectx_uniform_hp_perturbation_barrier/1")
            self.assertFalse(any(r["assurance"].values()))

    def test_cli_invalid_norm_fails(self):
        run = subprocess.run(
            [sys.executable, "-m", "mathos.research.riemann_uniform_hp_barrier",
             "--budget-numerator", "3", "--budget-denominator", "1"],
            text=True, capture_output=True,
        )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("does not apply", run.stderr)


if __name__ == "__main__":
    unittest.main()
