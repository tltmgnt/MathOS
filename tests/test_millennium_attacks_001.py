"""Reproducible, bounded checks for the first mathematical attack notes."""
from fractions import Fraction
import unittest

from mathos.research.millennium_attacks_001 import (
    brute_force_satisfiable,
    experiment_report,
    parity_cycle_2cnf,
    stokes_initial_l2_scale_exponent,
    stokes_lower_bound_fourth_power,
    stokes_mixed_l4_l6_scale_exponent,
    stokes_normalized_l4l6_fourth_power,
    two_sat_satisfiable,
    unit_pure_status,
)


class StokesEnergyBarrierTests(unittest.TestCase):
    def test_exact_l2_invariance_and_mixed_norm_exponent(self):
        self.assertEqual(stokes_initial_l2_scale_exponent(), Fraction(0))
        self.assertEqual(stokes_mixed_l4_l6_scale_exponent(), Fraction(1, 2))

    def test_exact_integral_at_unit_viscosity_and_horizon(self):
        # Integral: lambda^2/(24 nu) * [1-(1+4 nu lambda^2 T)^(-6)].
        expected = Fraction(1, 24) * (1 - Fraction(1, 5**6))
        self.assertEqual(stokes_normalized_l4l6_fourth_power(1), expected)

    def test_quartic_norm_lower_bound_grows_with_scale_squared(self):
        for nu, duration in ((1, 1), (Fraction(3, 2), Fraction(2, 5))):
            unit = stokes_lower_bound_fourth_power(
                1, viscosity=nu, horizon=duration)
            for scale in (1, 2, 4, 8, 16, 32):
                with self.subTest(nu=nu, T=duration, scale=scale):
                    actual = stokes_normalized_l4l6_fourth_power(
                        scale, viscosity=nu, horizon=duration)
                    lower = stokes_lower_bound_fourth_power(
                        scale, viscosity=nu, horizon=duration)
                    self.assertGreaterEqual(actual, lower)
                    self.assertEqual(lower, scale * scale * unit)

    def test_exact_formula_at_large_scale(self):
        self.assertGreater(
            stokes_normalized_l4l6_fourth_power(32),
            256 * stokes_normalized_l4l6_fourth_power(1))

    def test_invalid_parameters_rejected(self):
        for n in (0, -1, True, 0.5):
            with self.subTest(scale=n):
                with self.assertRaises(ValueError):
                    stokes_normalized_l4l6_fourth_power(n)
        with self.assertRaises(ValueError):
            stokes_normalized_l4l6_fourth_power(1, viscosity=0)
        with self.assertRaises(ValueError):
            stokes_normalized_l4l6_fourth_power(1, horizon=-1)
        with self.assertRaises(TypeError):
            stokes_normalized_l4l6_fourth_power(1, viscosity=1.0)


class SatLocalRuleBarrierTests(unittest.TestCase):
    def test_parity_cycles_have_no_initial_unit_or_pure_literals(self):
        for n in (3, 4, 6, 8, 10, 32):
            with self.subTest(n=n):
                formula = parity_cycle_2cnf(n)
                self.assertEqual(len(formula), 2 * n)
                self.assertTrue(all(len(clause) == 2 for clause in formula))
                appearances = {literal for clause in formula for literal in clause}
                self.assertEqual(appearances, {
                    literal for i in range(1, n + 1) for literal in (i, -i)
                })
                self.assertEqual(unit_pure_status(formula, n), "stalled")
                self.assertFalse(two_sat_satisfiable(formula, n))

    def test_independent_truth_table_rejects_each_small_cycle(self):
        for n in (3, 4, 5, 6, 8, 10):
            with self.subTest(n=n):
                self.assertFalse(brute_force_satisfiable(parity_cycle_2cnf(n), n))

    def test_implication_solver_matches_exhaustive_baseline(self):
        # Covers satisfiable and unsatisfiable small 2-CNF cases.
        samples = [
            (((1, 2), (-1, 2)), 2),
            (((1, 2), (-1, -2)), 2),
            (((1, 1), (-1, -1)), 1),
            (((1, 2), (-1, 2), (1, -2), (-1, -2)), 2),
            (((1, -1), (2, -2)), 2),
            ((), 3),
        ]
        for clauses, n in samples:
            with self.subTest(clauses=clauses):
                self.assertEqual(two_sat_satisfiable(clauses, n),
                                 brute_force_satisfiable(clauses, n))

    def test_pure_literal_elimination_not_exaggerated_as_sat_algorithm(self):
        self.assertEqual(unit_pure_status(((1, 2), (1, -2)), 2), "sat")
        self.assertEqual(unit_pure_status(parity_cycle_2cnf(3), 3), "stalled")

    def test_invalid_cnf_rejected(self):
        for invalid in (0, 1, 2):
            with self.assertRaises(ValueError):
                parity_cycle_2cnf(invalid)
        with self.assertRaises(ValueError):
            two_sat_satisfiable(((1, 0),), 1)
        with self.assertRaises(ValueError):
            brute_force_satisfiable((), 15)


class ResearchStatusTests(unittest.TestCase):
    def test_no_millennium_result_is_certified(self):
        report = experiment_report()
        self.assertEqual(report["certification"], "NOT_CERTIFIED")
        self.assertIn("NOT", report["certification"])
        self.assertIn("not_proved", report["navier_stokes"])
        self.assertIn("not_proved", report["p_vs_np"])
        for case in report["p_vs_np"]["cases"]:
            self.assertEqual(case["unit_pure"], "stalled")
            self.assertFalse(case["two_sat_satisfiable"])
            self.assertFalse(case["brute_force_satisfiable"])


if __name__ == "__main__":
    unittest.main()
