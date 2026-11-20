"""Adversarial regression checks for bounded TECT-X rank certificates.

These tests check exact finite-field calculations, not an infinite
Selmer-3 theorem, analytic rank, Sha finiteness, or BSD.
"""
from contextlib import redirect_stdout
from fractions import Fraction
from io import StringIO
import unittest

from mathos.research import tect_x_rank3_family_certificate as family
from mathos.research import tect_x_rank4_fiber_certificate as fiber


class NonisotrivialRankCertificateTests(unittest.TestCase):
    def test_progression_has_exact_rational_point_identities(self):
        for m in (0, 1, 2, 9):
            n = 5 + 759 * m
            a, b = family.ab(n)
            self.assertEqual(a * a - 3 * b * b, 1)
            for x, y in ((0, b), (a, b), (-1, 2 * b)):
                self.assertEqual(y * y, x * x * x - a * a * x + b * b)
            for p in (3, 11, 23):
                self.assertEqual((family.red(a, p), family.red(b, p)),
                                 (26 % p, 15 % p))

    def test_family_rank_three_reduction_certificate(self):
        with redirect_stdout(StringIO()) as out:
            family.verify()
        self.assertIn("3 independent point classes", out.getvalue())
        self.assertIn("NOT CHECKED: any global 2-Selmer upper bound",
                      out.getvalue())

    def test_first_fiber_has_four_exact_rational_points(self):
        self.assertEqual(fiber.DELTA, 19748739664)
        self.assertEqual(len(fiber.POINTS), 4)
        for x, y in fiber.POINTS:
            self.assertEqual(y * y, x ** 3 + fiber.A * x + fiber.B)
        self.assertEqual([x for x in range(11)
                          if (x ** 3 + fiber.A * x + fiber.B) % 11 == 0], [])

    def test_every_nonzero_binary_relation_obstructed(self):
        survivors = set(range(1, 16))
        for p, expected in ((3, {6, 9, 15}), (5, {6}), (23, set())):
            self.assertNotEqual(fiber.DELTA % p, 0)
            doubles = fiber.twoE(p)
            survivors = {mask for mask in survivors
                         if fiber.binary_combination(mask, p) in doubles}
            self.assertEqual(survivors, expected)
        self.assertEqual(fiber.binary_combination(6, 23), (2, 10))

    def test_first_fiber_certificate_and_scope(self):
        with redirect_stdout(StringIO()) as out:
            fiber.main()
        self.assertIn("rank(E_5(Q)) >= 4", out.getvalue())
        self.assertIn("dim_F2 Sel_2(E_5/Q) >= 4", out.getvalue())

    def test_n_is_not_constant_family(self):
        self.assertNotEqual(family.ab(5)[1], family.ab(5 + 759)[1])
        self.assertEqual(family.ab(5), (Fraction(26), Fraction(15)))


if __name__ == "__main__":
    unittest.main()
