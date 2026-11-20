"""MathOS 007: finite regression for exact mod-20 agreement classes.

This tests a classical consequence of quadratic twisting and rational
two-torsion. It does NOT prove the infinite-prime density statement,
elliptic-curve rank, or the Birch--Swinnerton-Dyer conjecture.
"""
import unittest

from mathos.research.bsd_inert_007 import (
    is_prime,
    legendre_symbol,
    number_of_points_bruteforce,
)


class BSD007PrimeClassChecks(unittest.TestCase):
    def test_exact_residue_classes_up_to_401(self):
        good_primes = 0
        matches = 0
        disagreements = 0
        for p in range(3, 402, 2):
            if p == 5 or not is_prime(p):
                continue
            good_primes += 1
            n1 = number_of_points_bruteforce(1, p)
            n5 = number_of_points_bruteforce(5, p)
            a1 = p + 1 - n1
            a5 = p + 1 - n5

            # Standard quadratic-twist trace identity.
            self.assertEqual(a5, legendre_symbol(5, p) * a1, p)

            # Exact classification derived in the mathematical addendum.
            difference_expected = (p % 20 in (13, 17))
            self.assertEqual(n1 != n5, difference_expected, p)

            if p % 4 == 1:
                self.assertEqual(a1 % 4, 2, p)
            else:
                self.assertEqual(a1, 0, p)

            if difference_expected:
                disagreements += 1
                self.assertEqual((n5 - n1) % 8, 4, p)
            else:
                matches += 1

        # Counts are finite regression metadata, NOT density assertions.
        self.assertEqual(good_primes, 77)
        self.assertEqual(matches, 55)
        self.assertEqual(disagreements, 22)


if __name__ == "__main__":
    unittest.main()
