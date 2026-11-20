"""Guard theorem scope and truth-table logic; not a BSD or analytic solver."""
import unittest

from mathos.research.bsd_analytic_milestone_02 import (
    analytic_order_floor,
    possible_under_external_low_rank_theorem,
    audit,
)


class BSDAnalyticMilestone02Tests(unittest.TestCase):
    def test_classical_contrapositive_and_signed_parity(self):
        self.assertEqual(analytic_order_floor(2), 2)
        self.assertEqual(analytic_order_floor(3), 2)
        self.assertEqual(analytic_order_floor(2, 1), 2)
        self.assertEqual(analytic_order_floor(2, -1), 3)
        self.assertEqual(analytic_order_floor(1), 1)
        self.assertEqual(analytic_order_floor(1, 1), 2)
        self.assertEqual(analytic_order_floor(0, -1), 1)
        self.assertFalse(possible_under_external_low_rank_theorem(2, 0))
        self.assertFalse(possible_under_external_low_rank_theorem(2, 1))
        self.assertTrue(possible_under_external_low_rank_theorem(2, 2))
        # Nothing in low-rank theorem forces equality in the high-rank regime.
        self.assertTrue(possible_under_external_low_rank_theorem(2, 4))
        self.assertTrue(possible_under_external_low_rank_theorem(7, 2))

    def test_invalid_inputs(self):
        for invalid in (-1, 2.0, True, "2"):
            with self.assertRaises(ValueError):
                analytic_order_floor(invalid)
        for sign in (0, 2, 1.0, False):
            with self.assertRaises(ValueError):
                analytic_order_floor(2, sign)

    def test_nonpromotion_guard(self):
        result = audit()
        self.assertTrue(result["cofinite_family_analytic_order_at_least_2_is_theorem_corollary"])
        for key in (
            "explicit_specialization_exception_set_computed",
            "analytic_L_function_evaluated",
            "exact_analytic_rank_for_generic_fiber_computed",
            "rank_equality_for_infinite_family_proved",
            "mathematical_novelty_established",
            "BSD_proved",
        ):
            self.assertIs(result[key], False)


if __name__ == "__main__":
    unittest.main()
