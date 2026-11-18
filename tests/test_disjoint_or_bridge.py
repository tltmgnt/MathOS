"""Exact finite regression for restricted CNF versus OR-polynomial semantics."""
import copy
import unittest
from mathos.research.disjoint_or_bridge import (
    canonical_witness, evaluate_cnf, evaluate_product, verify_finite,
)


class DisjointORBridgeTests(unittest.TestCase):
    def test_empty_product_and_empty_conjunction(self):
        self.assertEqual(evaluate_product([]), 1)
        self.assertTrue(evaluate_cnf([]))

    def test_full_boolean_truth_table(self):
        truth = [
            ((0, 0), 0), ((0, 1), 1),
            ((1, 0), 1), ((1, 1), 1),
        ]
        for pair, expected in truth:
            with self.subTest(pair=pair):
                self.assertEqual(evaluate_product([pair]), expected)
                self.assertEqual(evaluate_cnf([pair]), bool(expected))

    def test_canonical_witness_every_sampled_length(self):
        for n in range(18):
            witness = canonical_witness(n)
            self.assertEqual(len(witness), n)
            self.assertTrue(evaluate_cnf(witness))
            self.assertEqual(evaluate_product(witness), 1)

    def test_exhaustive_finite_counts_are_not_certificate_of_p_vs_np(self):
        report = verify_finite(6)
        self.assertEqual(report["status"], "FINITE_REGRESSION_ONLY")
        self.assertFalse(report["establishes_p_vs_np"])
        self.assertFalse(report["novelty_established"])
        self.assertFalse(report["independent_review_completed"])
        self.assertEqual(report["max_n"], 6)
        self.assertEqual(report["formal_theorem"], "MathOS.satDisjointProduct_indicator")
        for n, row in enumerate(report["counts"]):
            self.assertEqual(row["clauses"], n)
            self.assertEqual(row["assignments_checked"], 4**n)
            self.assertEqual(row["satisfying_assignments"], 3**n)
        self.assertEqual(report["counts"][-1]["satisfying_assignments"], 729)

    def test_invalid_boolean_inputs_fail_closed(self):
        invalid = [
            [(2, 1)], [(True, 1)], [(-1, 0)], [(0, 0, 0)],
            [0], "not an assignment", [(1, 0), [1]], None,
        ]
        for assignment in invalid:
            with self.subTest(assignment=assignment):
                with self.assertRaises(ValueError):
                    evaluate_cnf(assignment)
                with self.assertRaises(ValueError):
                    evaluate_product(assignment)

    def test_unbounded_audit_is_rejected(self):
        for bad in (-1, 8, "6", True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    verify_finite(bad)
        for bad in (-1, True, "2"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    canonical_witness(bad)

if __name__ == "__main__":
    unittest.main()
