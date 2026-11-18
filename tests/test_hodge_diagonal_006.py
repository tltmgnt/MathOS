"""Exact matrix and scope regression tests for Hodge research attempt 006."""
import unittest
from fractions import Fraction

from mathos.research.hodge_diagonal_006 import (
    audit, determinant_3x3, diagonal_span_obstruction,
    intersection_signature, matrix, pairing,
)


class HodgeDiagonalIntersectionTests(unittest.TestCase):
    def test_exact_geometric_input_matrix_and_determinant(self):
        self.assertEqual(matrix(0), ((0, 1, 1), (1, 0, 1), (1, 1, 2)))
        self.assertEqual(matrix(1), ((0, 1, 1), (1, 0, 1), (1, 1, 0)))
        self.assertEqual(matrix(2), ((0, 1, 1), (1, 0, 1), (1, 1, -2)))
        for genus in (0, 1, 2, 3, 5, 13, 1000):
            with self.subTest(genus=genus):
                self.assertEqual(determinant_3x3(matrix(genus)), 2 * genus)

    def test_divisor_self_intersections_and_pairwise_values(self):
        f1, f2, diagonal = (1, 0, 0), (0, 1, 0), (0, 0, 1)
        for g in (0, 1, 2, 17):
            with self.subTest(genus=g):
                self.assertEqual(pairing(g, f1, f1), 0)
                self.assertEqual(pairing(g, f2, f2), 0)
                self.assertEqual(pairing(g, diagonal, diagonal), 2-2*g)
                for x, y in ((f1, f2), (f1, diagonal), (f2, diagonal)):
                    self.assertEqual(pairing(g, x, y), 1)
                    self.assertEqual(pairing(g, y, x), 1)

    def test_rational_bilinearity_and_independent_divisor_direction(self):
        g = 3
        x, y = (1, Fraction(2, 3), -2), (3, -1, Fraction(7, 4))
        factor = Fraction(5, 9)
        self.assertEqual(
            pairing(g, tuple(factor*z for z in x), y),
            factor*pairing(g, x, y),
        )
        self.assertEqual(
            pairing(g, x, tuple(factor*z for z in y)),
            factor*pairing(g, x, y),
        )
        self.assertEqual(
            intersection_signature(g, (0, 0, 1)),
            (Fraction(1), Fraction(1), Fraction(-4)),
        )
        self.assertEqual(
            intersection_signature(g, (1, 1, 0)),
            (Fraction(1), Fraction(1), Fraction(2)),
        )

    def test_genus_zero_degeneracy_not_promoted_to_equivalence_proof(self):
        result = diagonal_span_obstruction(0)
        self.assertEqual(result["determinant"], 0)
        self.assertEqual(result["third_pairing_residual"], 0)
        self.assertFalse(result["diagonal_excluded_from_two_fiber_rational_span"])
        self.assertEqual(intersection_signature(0, (1, 1, -1)), (0, 0, 0))

    def test_positive_genus_obstruction_exact(self):
        for g in (1, 2, 3, 4, 6, 19):
            with self.subTest(genus=g):
                result = diagonal_span_obstruction(g)
                self.assertEqual(result["candidate_fiber_coefficients"], [1, 1])
                self.assertEqual(result["target_diagonal_pairings"], [1, 1, 2-2*g])
                self.assertEqual(result["candidate_fiber_pairings"], [1, 1, 2])
                self.assertEqual(result["third_pairing_residual"], 2*g)
                self.assertTrue(result["diagonal_excluded_from_two_fiber_rational_span"])

    def test_research_manifest_never_claims_hodge_prize_solution(self):
        result = audit(8)
        self.assertEqual(result["experiment"], "MathOS-MILLENNIUM-006-HODGE-DIAGONAL-DIVISOR")
        self.assertEqual(result["status"], "ABSTRACT_EXACT_INTERSECTION_AUDIT_ONLY")
        self.assertFalse(result["official_conjecture_proved"])
        self.assertFalse(result["independent_geometry_formalized"])
        self.assertFalse(result["independent_external_review"])
        self.assertEqual(len(result["results"]), 9)
        self.assertEqual(result["formal_lean_theorem"],
                         "MathOS.elliptic_diagonal_not_in_fiber_span")

    def test_bad_inputs_fail_closed(self):
        for bad in (-1, True, 1.5, "2", None):
            with self.subTest(genus=bad):
                with self.assertRaises(ValueError):
                    matrix(bad)
        for bad in (0, 101, True, 1.5, "10"):
            with self.subTest(max_genus=bad):
                with self.assertRaises(ValueError):
                    audit(bad)
        for invalid in ((), ((0,),), [[1, 2, 3]], [[0, 1, 2]] * 2,
                        ((True, 0, 0), (0, 1, 0), (0, 0, 1))):
            with self.subTest(matrix=invalid):
                with self.assertRaises(ValueError):
                    determinant_3x3(invalid)
        for invalid in ((1, 2), (True, 0, 0), ("1", 0, 0)):
            with self.subTest(vector=invalid):
                with self.assertRaises(ValueError):
                    pairing(1, invalid, (0, 0, 1))


if __name__ == "__main__":
    unittest.main()
