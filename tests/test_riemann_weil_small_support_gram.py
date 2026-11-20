"""Adversarial tests for exact compact-bump Weil archimedean enclosures."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_small_support_gram import (
    WINDOW_HALF, QUANTITATIVE_CONSTANT,
    bump_derivative_polynomial, bump_derivative_upper,
    bumps, seminorms, entry_bound, diagonal_coercivity_lower, report,
)


class SmallSupportWeilTests(unittest.TestCase):
    def test_normalized_bump_derivative_polynomial_at_orders_zero_one_two(self):
        self.assertEqual(bump_derivative_polynomial(0),{(0,0):1})
        self.assertEqual(bump_derivative_polynomial(1),{(1,2):-2})
        self.assertEqual(bump_derivative_polynomial(2).get((0,2)), -2)

    def test_derivative_bounds_are_positive_integers(self):
        C=[bump_derivative_upper(j) for j in range(4)]
        self.assertEqual(C[0],1)
        self.assertGreater(C[1],0)
        self.assertGreater(C[2],0)
        self.assertGreater(C[3],0)

    def test_all_bumps_stay_strictly_inside_prime_free_window(self):
        for n in [1,2,3,12,64,128]:
            b=bumps(n)
            self.assertEqual(len(b),len({(x["n"],x["center"]) for x in b}))
            for item in b:
                self.assertGreater(Fraction(item["support_left"]),-WINDOW_HALF)
                self.assertLess(Fraction(item["support_right"]),WINDOW_HALF)
                self.assertGreater(Fraction(item["width"]),0)

    def test_first_bump_has_expected_support(self):
        b=bumps(1)[0]
        self.assertEqual(b["n"],3)
        self.assertEqual(b["center"],"0/1")
        self.assertEqual(b["support_left"],"-1/8")
        self.assertEqual(b["support_right"],"1/8")

    def test_exact_rational_archimedean_entry_enclosure(self):
        b=bumps(3)
        for a in b:
            for c in b:
                r=entry_bound(a,c)
                self.assertEqual(r["pole_term_exact"],"0/1")
                self.assertEqual(r["prime_power_term_exact"],"0/1")
                lo=Fraction(r["archimedean_entry_lower"])
                hi=Fraction(r["archimedean_entry_upper"])
                self.assertLess(lo,0)
                self.assertEqual(-lo,hi)
                self.assertLess(Fraction(r["support_max_width"]),Fraction(1,2))
                self.assertTrue(r["full_Weil_entry_enclosed"])

    def test_hermitian_entry_enclosures_symmetric_in_real_tests(self):
        b=bumps(4)
        for i in range(4):
            for j in range(4):
                x=entry_bound(b[i],b[j])
                y=entry_bound(b[j],b[i])
                # Derivative orientation causes nonidentical but both valid intervals.
                self.assertGreater(Fraction(x["archimedean_entry_upper"]),0)
                self.assertGreater(Fraction(y["archimedean_entry_upper"]),0)

    def test_diagonal_lower_is_exact_rational_and_positive(self):
        for b in bumps(5):
            lo=diagonal_coercivity_lower(b)
            hi=Fraction(entry_bound(b,b)["archimedean_entry_upper"])
            self.assertIsInstance(lo,Fraction)
            self.assertGreater(lo,0)
            self.assertLess(lo,hi)

    def test_operator_norm_bounds_are_well_defined(self):
        b=bumps(8)
        for item in b:
            F0,F1=seminorms(item)
            self.assertIsInstance(F0,int)
            self.assertIsInstance(F1,int)
            self.assertGreater(F0,0)
            self.assertGreater(F1,0)

    def test_restricted_all_index_positivity_does_not_promote_RH(self):
        r=report(3)
        theorem=r["infinite_dimensional_positive_subspace"]
        self.assertTrue(theorem["all_finite_Gram_Hm_PSD_for_this_RESTRICTED_family"])
        self.assertEqual(theorem["L2_relative_lower_constant"],"1/250")
        self.assertFalse(theorem["full_canonical_Weil_test_core"])
        self.assertFalse(theorem["global_Weil_positivity"])
        self.assertFalse(any(r["assurance"].values()))

    def test_no_false_integral_numerical_certification(self):
        r=report(3)
        evidence=r["arithmetic_gram_enclosures"]
        self.assertEqual(evidence["entry_count"],6)
        self.assertFalse(evidence["bounds_are_tight_quadrature_enclosures"])
        self.assertFalse(evidence["individual_archimedean_integrals_numerically_evaluated"])
        self.assertTrue(evidence["archimedean_singular_cancellation_bounded"])

    def test_invalid_counts_and_orders_rejected(self):
        for count in [0,129,-1,True,3.5]:
            with self.subTest(count=count),self.assertRaises(ValueError):
                bumps(count)
        for order in [-1,4,1.0,True]:
            with self.subTest(order=order),self.assertRaises(ValueError):
                bump_derivative_polynomial(order)

    def test_cli_json_report(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"small_support.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_small_support_gram",
                "--count","3","--output",str(p)
            ],capture_output=True,text=True,check=True)
            data=json.loads(p.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"],"mathos_tectx_weil_small_support_arithmetic_gram/1")
            self.assertEqual(data["arithmetic_gram_enclosures"]["entry_count"],6)
            self.assertFalse(data["assurance"]["Riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
