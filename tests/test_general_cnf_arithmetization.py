"""Adversarial tests for arbitrary finite-CNF Boolean arithmetization.

These tests do not imply a SAT search-complexity bound.
"""
import unittest

from mathos.research.general_cnf_arithmetization import (
    arithmetic_gate_count,
    cnf_arithmetic_circuit,
    cnf_truth,
    validate_assignment,
    validate_cnf,
    verify_bounded,
)


class GeneralCNFArithmetizationTests(unittest.TestCase):
    def test_empty_formula_is_true_and_empty_clause_is_false(self):
        for assign in [(), (0,), (1,), (0, 1)]:
            self.assertTrue(cnf_truth((), assign))
            self.assertEqual(cnf_arithmetic_circuit((), assign), 1)
            self.assertFalse(cnf_truth(((),), assign))
            self.assertEqual(cnf_arithmetic_circuit(((),), assign), 0)

    def test_contradiction_and_tautology(self):
        for assign in ((0,), (1,)):
            contradiction = ((1,), (-1,))
            tautology = ((1, -1),)
            self.assertFalse(cnf_truth(contradiction, assign))
            self.assertEqual(cnf_arithmetic_circuit(contradiction, assign), 0)
            self.assertTrue(cnf_truth(tautology, assign))
            self.assertEqual(cnf_arithmetic_circuit(tautology, assign), 1)

    def test_shared_variable_and_duplicate_literals(self):
        formula = ((1, 2), (-1, 2), (1, 1, 1))
        for assign in ((0, 0), (0, 1), (1, 0), (1, 1)):
            expected = (assign == (1, 1))
            self.assertEqual(cnf_truth(formula, assign), expected)
            self.assertEqual(cnf_arithmetic_circuit(formula, assign), int(expected))
        self.assertEqual(arithmetic_gate_count(formula, 2), 10)

    def test_full_exhaustive_finite_box(self):
        report = verify_bounded(3, 2, 2)
        self.assertEqual(report["status"], "FINITE_REGRESSION_ONLY")
        self.assertEqual(report["total_formula_assignment_pairs"], 17113)
        self.assertEqual(
            [r["formulas_checked"] for r in report["results"]],
            [3, 57, 463, 1893],
        )
        self.assertEqual(
            [r["assignment_evaluations"] for r in report["results"]],
            [3, 114, 1852, 15144],
        )
        self.assertFalse(report["arbitrary_sat_polynomial_time_algorithm"])
        self.assertFalse(report["establishes_p_equals_np"])
        self.assertFalse(report["establishes_p_not_equals_np"])
        self.assertFalse(report["external_independent_review_completed"])

    def test_reject_bad_literals_and_assignments(self):
        invalid_cnf = (
            ((0,),), ((2,),), ((True,),), ((-2,),),
            ((1.0,),), ((None,),), (None,), "not clauses",
        )
        for cnf in invalid_cnf:
            with self.subTest(cnf=cnf):
                with self.assertRaises(ValueError):
                    validate_cnf(cnf, 1)
        for assignment in ((True,), (2,), (-1,), (0, 1), "0", None):
            with self.subTest(assignment=assignment):
                with self.assertRaises((ValueError, TypeError)):
                    validate_assignment(assignment, 1)

    def test_bounded_verifier_rejects_large_or_invalid_requests(self):
        for args in ((4, 2, 2), (3, 3, 2), (3, 2, 3), (True, 2, 2), (-1, 2, 2)):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    verify_bounded(*args)


if __name__ == "__main__":
    unittest.main()
