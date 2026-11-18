"""BSD attack 007 adversarial checks: exact inert-prime counts, not BSD proofs."""
from fractions import Fraction
import unittest

from mathos.research.bsd_inert_007 import (
    audit, cubic_mod_p, curve_point, exact_rational_witness,
    is_prime, legendre_symbol, number_of_points_bruteforce,
    number_of_points_character, pairing_cancellation,
)


class BSDInertPrimeTests(unittest.TestCase):
    def test_prime_and_euler_character(self):
        primes = (3, 5, 7, 11, 13, 17, 19, 23, 29)
        self.assertTrue(all(is_prime(p) for p in primes))
        self.assertFalse(any(is_prime(p) for p in (0, 1, 4, 9, 15, 21, 25, 49)))
        for p in primes:
            for a in range(p):
                expected = 0 if a == 0 else (
                    1 if a in {y * y % p for y in range(1, p)} else -1
                )
                self.assertEqual(legendre_symbol(a, p), expected)
            if p % 4 == 3:
                self.assertEqual(legendre_symbol(-1, p), -1)
            else:
                self.assertEqual(legendre_symbol(-1, p), 1)

    def test_odd_cubic_and_character_pair_cancellation(self):
        for p in (3, 7, 11, 19, 23, 31, 43, 47):
            for d in (1, 5, 6):
                if d % p == 0:
                    continue
                self.assertTrue(pairing_cancellation(d, p))
                for x in range(p):
                    self.assertEqual(
                        (cubic_mod_p(d, x, p) +
                         cubic_mod_p(d, -x, p)) % p,
                        0,
                    )

    def test_inert_primes_have_identical_counts(self):
        for p in (3, 7, 11, 19, 23, 31, 43, 47, 59, 67):
            with self.subTest(prime=p):
                e1 = number_of_points_bruteforce(1, p)
                e5 = number_of_points_bruteforce(5, p)
                self.assertEqual(e1, p + 1)
                self.assertEqual(e5, p + 1)
                self.assertEqual(number_of_points_character(1, p), (p + 1, 0))
                self.assertEqual(number_of_points_character(5, p), (p + 1, 0))

    def test_good_split_primes_can_distinguish_curves(self):
        self.assertEqual(number_of_points_bruteforce(1, 13), 8)
        self.assertEqual(number_of_points_bruteforce(5, 13), 20)
        with self.assertRaises(ValueError):
            pairing_cancellation(1, 13)

    def test_exact_witness_and_two_torsion(self):
        x, y = Fraction(25, 4), Fraction(75, 8)
        self.assertTrue(curve_point(5, x, y))
        self.assertFalse(curve_point(1, x, y))
        self.assertEqual(y*y, Fraction(5625, 64))
        self.assertEqual(x*x*x - 25*x, Fraction(5625, 64))
        self.assertNotEqual(x.denominator, 1)
        self.assertEqual(exact_rational_witness()["x"],
                         {"numerator": 25, "denominator": 4})
        for d in (1, 5):
            for t in (-d, 0, d):
                self.assertTrue(curve_point(d, Fraction(t), Fraction(0)))

    def test_finite_audit_has_unpromotable_research_status(self):
        r = audit(101)
        self.assertEqual(r["status"], "EXACT_BOUNDED_LOCAL_AUDIT_NOT_BSD")
        self.assertGreaterEqual(r["tested_inert_primes"], 10)
        self.assertEqual(
            r["two_curve_inert_factor_coincidences"],
            r["tested_inert_primes"],
        )
        self.assertTrue(any(not row["same_count"] for row in r["point_counts"]))
        for row in r["point_counts"]:
            if row["inert_subsequence"]:
                self.assertEqual(row["E1_ap"], 0)
                self.assertEqual(row["E5_ap"], 0)
            self.assertEqual(row["E1_ap"], row["p"] + 1 - row["E1_points"])
            self.assertEqual(row["E5_ap"], row["p"] + 1 - row["E5_points"])
        for key in (
            "establishes_general_bsd_rank_equality",
            "establishes_analytic_rank_or_l_function",
            "establishes_sha_finiteness",
            "establishes_refined_leading_term",
            "mathematical_novelty_established",
            "independent_external_review_completed",
        ):
            self.assertFalse(r[key], key)
        self.assertIn("rank 0", r["known_rank_input_from_external_literature_only"]["E1"])
        self.assertIn("LMFDB", r["known_rank_input_from_external_literature_only"]["E1"])
        self.assertIn("rank 1", r["known_rank_input_from_external_literature_only"]["E5"])
        self.assertIn("Silverberg", r["known_rank_input_from_external_literature_only"]["E5"])

    def test_invalid_input_and_bad_reduction_rejected(self):
        for bad in (-1, 1, 2, 4, 9, True, "7", 7.0):
            with self.subTest(p=bad):
                with self.assertRaises(ValueError):
                    legendre_symbol(1, bad)
        for d, p in ((0, 7), (5, 5), (1, 2), (1, 9), (True, 11)):
            with self.subTest(d=d, p=p):
                with self.assertRaises(ValueError):
                    number_of_points_bruteforce(d, p)
        for bad in (10, 402, True, "101", None):
            with self.subTest(limit=bad):
                with self.assertRaises(ValueError):
                    audit(bad)
        with self.assertRaises(ValueError):
            curve_point(5, Fraction(25, 4), 75/8)
        with self.assertRaises(ValueError):
            cubic_mod_p(1, True, 11)


if __name__ == "__main__":
    unittest.main()
