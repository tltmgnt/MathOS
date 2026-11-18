"""Exact arithmetic and fail-closed regression for RH attempt 005.

Synthetic symmetric zero multisets are not the zero set of zeta.
"""
from fractions import Fraction
import unittest

from mathos.research.riemann_li_prefix_005 import (
    BASE_Q, base_li, certificate, choose_height, complex_mul,
    complex_pow, prefix_bound, q_of_zero, quartet_li,
)


class RiemannLiPrefix005Tests(unittest.TestCase):
    def test_baseline_zero_is_on_critical_line(self):
        self.assertEqual(q_of_zero(Fraction(1, 2), Fraction(1)), BASE_Q)
        self.assertEqual(BASE_Q[0]**2 + BASE_Q[1]**2, 1)
        for n in range(1, 13):
            self.assertGreater(base_li(n), 0)

    def test_reflection_inverts_q_for_off_line_rational_zeros(self):
        for height in (2, 7, 256):
            rho_q = q_of_zero(Fraction(3, 4), Fraction(height))
            reflected_q = q_of_zero(Fraction(1, 4), -Fraction(height))
            self.assertEqual(complex_mul(rho_q, reflected_q), (1, 0))
            self.assertNotEqual(rho_q[0]**2+rho_q[1]**2, 1)

    def test_known_exact_baseline_coefficient(self):
        self.assertEqual(base_li(1), Fraction(4, 5))
        self.assertEqual(base_li(2), Fraction(64, 25))
        self.assertEqual(base_li(7), Fraction(3364, 78125))

    def test_all_finite_prefixes_have_certified_positive_margin(self):
        for N in (1, 2, 3, 4, 7, 8, 12):
            with self.subTest(prefix=N):
                report = certificate(N)
                self.assertEqual(report["tested_positive_prefix_length"], N)
                self.assertTrue(report["all_prefix_coefficients_positive"])
                self.assertEqual(report["status"], "EXACT_SYNTHETIC_COUNTERMODEL_ONLY")
                self.assertEqual(report["canonical_mathos_certification"], "NOT_CERTIFIED")
                self.assertFalse(report["full_rh_proved"])
                self.assertFalse(report["rh_disproved"])
                self.assertFalse(report["zeta_zero_claim"])
                self.assertEqual(len(report["synthetic_li_style_coefficients"]), N)
                height = report["off_line_height"]
                smallest, max_delta = choose_height(N)[1:]
                self.assertLess(prefix_bound(N, height), smallest)
                self.assertEqual(
                    Fraction(**report["certified_positive_lower_bound"]),
                    smallest-max_delta,
                )
                for row in report["synthetic_li_style_coefficients"]:
                    n = row["index"]
                    value = Fraction(**row["augmented_li_style_value"])
                    self.assertEqual(value, base_li(n)+quartet_li(n, height))
                    self.assertGreater(value, 0)

    def test_synthetic_values_do_not_require_real_zeta_or_floating_point(self):
        r = certificate(8)
        self.assertEqual(r["off_line_height"], 1024)
        self.assertIn("NOT the zeta zeros", r["zero_set_type"])
        self.assertEqual(r["minimum_baseline_coefficient"],
                         {"numerator": 3364, "denominator": 78125})
        self.assertGreater(Fraction(**r["certified_positive_lower_bound"]), 0)

    def test_invalid_inputs_fail_closed(self):
        for bad in (0, -1, 13, True, "6", None):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    certificate(bad)
        for bad in (0, -1, 1.5, True):
            with self.subTest(index=bad):
                with self.assertRaises(ValueError):
                    base_li(bad)
        with self.assertRaises(ValueError):
            q_of_zero(Fraction(0), Fraction(0))
        with self.assertRaises(ValueError):
            quartet_li(1, 1)
        with self.assertRaises(ValueError):
            prefix_bound(0, 4)
        with self.assertRaises(ValueError):
            complex_pow(BASE_Q, -1)
        with self.assertRaises(ValueError):
            complex_pow(BASE_Q, True)


if __name__ == "__main__":
    unittest.main()
