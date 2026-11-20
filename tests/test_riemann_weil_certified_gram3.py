"""Adversarial verified LDL checks for fixed three-function Weil form."""
import json
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mpmath import iv

from mathos.research.riemann_weil_certified_gram3 import (
    _f4_bound,_interval_ldlt,audit,
)

class WeilCertifiedGram3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        iv.dps=50
        cls.report=audit(8192)

    def test_exact_global_fourth_derivative_envelope(self):
        self.assertEqual(_f4_bound(),Fraction(946104,125))
        self.assertLess(_f4_bound(),8000)

    def test_full_symmetric_interval_matrix(self):
        matrix=self.report["numerical_proof"]["matrix_entry_intervals"]
        self.assertEqual(len(matrix),3)
        for i in range(3):
            for j in range(3):
                self.assertEqual(matrix[i][j],matrix[j][i])
                lo,hi=map(Fraction,matrix[i][j])
                self.assertLess(lo,hi)

    def test_each_ldlt_pivot_is_certified_positive(self):
        for key in ["unshifted_LDL_pivots","shifted_LDL_pivots"]:
            pivots=self.report["numerical_proof"][key]
            self.assertEqual(len(pivots),3)
            for lo,hi in pivots:
                self.assertGreater(Fraction(lo),0)
                self.assertGreaterEqual(Fraction(hi),Fraction(lo))

    def test_global_real_eigenvalue_lower_bound(self):
        self.assertEqual(
            self.report["numerical_proof"]["proved_minimum_eigenvalue_greater_than"],
            "1/1000000")
        self.assertTrue(self.report["scope"]["positivity_proved_on_fixed_three_dimensional_span"])
        self.assertFalse(self.report["scope"]["riemann_hypothesis_proved"])

    def test_elliptic_invalid_matrix_is_rejected(self):
        with self.assertRaises(ArithmeticError):
            _interval_ldlt([[iv.mpf(1),iv.mpf(2)],
                            [iv.mpf(2),iv.mpf(1)]])
        with self.assertRaises(ArithmeticError):
            _interval_ldlt([[iv.mpf([-1,1])]])

    def test_reject_bad_matrix_shapes_and_shifts(self):
        with self.assertRaises(ValueError):
            _interval_ldlt([[iv.mpf(1),iv.mpf(0)]])
        with self.assertRaises(ValueError):
            _interval_ldlt([[iv.mpf(1)]],Fraction(-1))

    def test_prime_power_and_archimedean_error_components_present(self):
        e=self.report["numerical_proof"]["error_bound_intervals"]
        self.assertEqual(set(e),{
            "simpson_abs_error","digamma_remainder_abs_error",
            "archimedean_infinite_tail_abs_error",
            "prime_power_infinite_tail_abs_error"})
        for name,interval in e.items():
            self.assertGreater(Fraction(interval[0]),0,name)
            self.assertGreaterEqual(Fraction(interval[1]),Fraction(interval[0]),name)

    def test_archimedean_simpson_error_dominates(self):
        e=self.report["numerical_proof"]["error_bound_intervals"]
        self.assertGreater(Fraction(e["simpson_abs_error"][0]),
                           Fraction(e["digamma_remainder_abs_error"][1]))

    def test_values_match_independent_high_precision_reference(self):
        m=self.report["numerical_proof"]["matrix_entry_intervals"]
        expected={
            (0,0):Fraction("0.03708258346264"),
            (0,1):Fraction("-0.03511814137211"),
            (0,2):Fraction("0.02591496599955"),
            (1,1):Fraction("0.03333113683154"),
            (1,2):Fraction("-0.02469637709159"),
            (2,2):Fraction("0.01850777088056"),
        }
        for (i,j),v in expected.items():
            lo,hi=map(Fraction,m[i][j])
            self.assertLess(lo,v)
            self.assertGreater(hi,v)

    def test_no_global_weil_or_rh_promotion(self):
        s=self.report["scope"]
        self.assertFalse(s["positivity_proved_on_entire_Weil_test_space"])
        self.assertFalse(s["uniform_positive_lower_bound_independent_of_test_span"])
        self.assertFalse(s["global_Weil_Hilbert_space_constructed"])
        self.assertFalse(s["independent_formal_verification"])

    def test_invalid_quadrature_counts_rejected(self):
        for count in [4096,8193,0,32.0,True]:
            with self.subTest(count=count),self.assertRaises(ValueError):
                audit(count)

    def test_cli_portable_certificate(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/"weil_gram3.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_certified_gram3",
                "--panels","8192","--output",str(target)
            ],check=True,capture_output=True,text=True)
            output=json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(output["status"],"FIXED_3X3_WEIL_GRAM_STRICTLY_POSITIVE_GLOBAL_RH_OPEN")
            self.assertTrue(output["scope"]["positivity_proved_on_fixed_three_dimensional_span"])
            self.assertFalse(output["scope"]["riemann_hypothesis_proved"])

if __name__ == "__main__":
    unittest.main()
