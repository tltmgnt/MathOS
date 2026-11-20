"""Adversarial exact first-two LF core arithmetic Weil Gram checks."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mpmath import iv
from mathos.research.riemann_weil_all_index_bridge import enumerate_compact_bumps
from mathos.research.riemann_weil_lf_core_first_2x2 import (
    CROSS_SUPPORT, EXPECTED_PRIME_POWERS, TARGET_EIGEN_FLOOR,
    TRAPEZOID_SECOND_DERIVATIVE_BOUND, TRAPEZOID_ERROR_NUMERATOR,
    audit, validate_first_two, covariance_range_at_log,
    prime_cross, gamma_cross,
)
from mathos.research.riemann_weil_lf_core_first_diagonal import endpoints


class ActualLFDenseCoreWeilTwoByTwoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        iv.dps=36
        cls.r=audit()

    def test_first_two_are_exact_immutable_lf_core_indices(self):
        b=validate_first_two()
        self.assertEqual(b,enumerate_compact_bumps(2))
        self.assertEqual([(v["n"],v["center"]) for v in b],
                         [(1,"0/1"),(1,"-1/1")])
        self.assertEqual(CROSS_SUPPORT,(Fraction(0),Fraction(2)))

    def test_no_cherry_picked_second_direction(self):
        basis=self.r["basis"]
        self.assertEqual(len(basis["first_two_immutable_enumeration"]),2)
        self.assertTrue(basis["diagonal_translation_invariance_exact"])
        self.assertTrue(basis["offdiag_reflection_Hermitian_exact"])

    def test_all_five_prime_power_terms_present_and_actual(self):
        a=self.r["arithmetic"]
        self.assertEqual(EXPECTED_PRIME_POWERS,
                         ((2,2),(3,3),(4,2),(5,5),(7,7)))
        self.assertEqual([(v["n"],v["von_mangoldt_base"])
                          for v in a["prime_power_inventory"]],
                         list(EXPECTED_PRIME_POWERS))
        self.assertEqual(len(a["prime_power_parts"]),5)
        self.assertTrue(all(p["strict_nonzero_from_support"]
                            for p in a["prime_power_parts"]))

    def test_each_prime_convolution_is_in_support(self):
        for n,p in EXPECTED_PRIME_POWERS:
            v=covariance_range_at_log(n,256)
            lo,hi=endpoints(v)
            self.assertGreaterEqual(lo,0)
            self.assertGreater(hi,0)

    def test_prime_sum_strictly_negative(self):
        a=self.r["arithmetic"]
        self.assertLess(Fraction(a["offdiagonal_prime_interval"][1]),0)
        for p in a["prime_power_parts"][:4]:
            self.assertLess(Fraction(p["arithmetic_term"][1]),0)

    def test_full_archimedean_term_strictly_negative(self):
        a=self.r["arithmetic"]
        low,high=map(Fraction,a["offdiagonal_archimedean_interval"])
        self.assertLess(low,high)
        self.assertLess(high,0)
        self.assertEqual(a["gamma_global_second_derivative_upper"],300)
        self.assertEqual(
            Fraction(a["gamma_signed_trapezoid_error_exact"]),
            Fraction(200,2048**2))

    def test_positive_pole_and_complete_cross_entry(self):
        a=self.r["arithmetic"]
        self.assertGreater(Fraction(a["offdiagonal_pole_interval"][0]),0)
        lo,hi=map(Fraction,a["offdiagonal_full_raw_Weil_interval"])
        self.assertLess(lo,hi)
        self.assertLess(hi,0)

    def test_exact_rational_2x2_diagonal_dominance(self):
        a=self.r["arithmetic"]
        dlow,dhigh=map(Fraction,a["diagonal_full_raw_Weil_interval"])
        clo,chi=map(Fraction,a["offdiagonal_full_raw_Weil_interval"])
        upperabs=max(abs(clo),abs(chi))
        self.assertGreater(dlow,upperabs)
        self.assertEqual(
            Fraction(a["exact_raw_diagonal_dominance_margin"]),
            dlow-upperabs)
        self.assertGreater(
            Fraction(a["exact_normalized_diagonal_dominance_margin"]),
            TARGET_EIGEN_FLOOR)

    def test_independent_schur_pivot_is_strictly_positive(self):
        a=self.r["arithmetic"]
        dlow=Fraction(a["diagonal_full_raw_Weil_interval"][0])
        clo,chi=map(Fraction,a["offdiagonal_full_raw_Weil_interval"])
        c=max(abs(clo),abs(chi))
        self.assertEqual(
            Fraction(a["exact_raw_second_Schur_pivot_lower"]),
            dlow-c*c/dlow)
        self.assertGreater(dlow-c*c/dlow,0)

    def test_normalized_gram_is_Hermitian_two_by_two(self):
        m=self.r["arithmetic"]["full_normalized_Gram_2x2"]
        self.assertEqual(len(m),2)
        self.assertEqual(m[0][0],m[1][1])
        self.assertEqual(m[0][1],m[1][0])
        for row in m:
            for lo,hi in row:
                self.assertLessEqual(Fraction(lo),Fraction(hi))

    def test_no_global_RH_promotion(self):
        evidence=self.r["assurance"]
        self.assertTrue(evidence["first_2x2_LF_core_Gram_certified"])
        self.assertFalse(evidence["all_finite_LF_core_Gram_PSD"])
        self.assertFalse(evidence["all_admissible_test_functions_positive"])
        self.assertFalse(evidence["Riemann_hypothesis_proved"])
        self.assertFalse(evidence["global_positive_Weil_Hilbert_completion"])

    def test_wrong_resolution_is_rejected_without_claim(self):
        with self.assertRaises(ValueError):
            audit(300,512,1024,1024)
        with self.assertRaises(ValueError):
            gamma_cross(200,512)
        with self.assertRaises(ValueError):
            prime_cross(100)

    def test_portable_cli_reproduction(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"weil_core2.json"
            subprocess.run([
                sys.executable,"-m",
                "mathos.research.riemann_weil_lf_core_first_2x2",
                "--output",str(output)
            ],check=True,capture_output=True,text=True)
            data=json.loads(output.read_text(encoding="utf-8"))
            a=data["arithmetic"]
            self.assertEqual(data["schema"],"mathos_tectx_weil_lf_core_first_2x2/1")
            self.assertGreater(
                Fraction(a["exact_normalized_diagonal_dominance_margin"]),
                Fraction(1,10000))
            self.assertFalse(data["assurance"]["Riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
