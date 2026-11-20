"""Adversarial tests for the first *actual* LF-dense Weil core entry."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_all_index_bridge import enumerate_compact_bumps
from mathos.research.riemann_weil_lf_core_first_diagonal import (
    HALF_WIDTH, R, NEAR_ZERO, MIN_NORMALIZED_WEIL_VALUE,
    audit, archimedean_coefficient, covariance_at, dyadic_grid,
    endpoints, gamma_kernel, interval, phi_point, pole_moments,
    positive_gamma_integral,
)


class LFCoreFirstActualWeilDiagonalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=audit(256,256)

    def test_actual_first_LF_core_function_matches_enumeration(self):
        b=enumerate_compact_bumps(1)[0]
        self.assertEqual((b["n"],b["center"],b["half_support_width"]),
                         (1,"0/1","1/2"))
        self.assertEqual(self.r["test_function"]["core_index"],0)
        self.assertEqual(self.r["test_function"]["support"],["-1/2","1/2"])

    def test_exact_derivative_majorants_cover_smooth_bump(self):
        # For y>=1, exp(1-y)*y^j maximizes at y=j.
        # Use e>5/2 to bound all three terms in phi''.
        estimate=4*Fraction(2048,125)+12*Fraction(108,25)+6*Fraction(8,5)
        self.assertLess(estimate,127)
        self.assertEqual(self.r["arithmetic"]["global_trap_derivative_bounds"]["convolution_integrand_second"],1144)

    def test_bump_is_zero_outside_support_positive_at_center(self):
        for t in (Fraction(-1),-HALF_WIDTH,HALF_WIDTH,Fraction(1)):
            self.assertEqual(endpoints(phi_point(t)),(Fraction(0),Fraction(0)))
        lo,hi=endpoints(phi_point(Fraction(0)))
        self.assertLessEqual(lo,1)
        self.assertGreaterEqual(hi,1)

    def test_actual_autocorrelation_interval_is_positive(self):
        near=covariance_at(Fraction(0),256)
        lo,hi=endpoints(near)
        self.assertLess(Fraction(49,100),lo)
        self.assertGreater(hi,lo)
        self.assertLess(hi,Fraction(50,100))
        self.assertEqual(endpoints(covariance_at(R,256)),(Fraction(0),Fraction(0)))

    def test_moments_include_exact_positive_normalization(self):
        mass,pole_moment=pole_moments(256)
        self.assertGreater(endpoints(mass)[0],Fraction(3,5))
        self.assertLess(endpoints(mass)[1],Fraction(61,100))
        self.assertGreater(endpoints(pole_moment)[0],endpoints(mass)[0])
        self.assertTrue(self.r["test_function"]["corresponds_to_PR83_dense_core"])

    def test_dyadic_partition_covers_zero_cutoff_to_one(self):
        g=dyadic_grid(256)
        self.assertEqual(len(g),9*256+1)
        self.assertEqual(g[0],NEAR_ZERO)
        self.assertEqual(g[-1],R)
        self.assertTrue(all(x<y for x,y in zip(g,g[1:])))
        self.assertEqual(self.r["arithmetic"]["near_zero_integral_upper"],
                         str(32*NEAR_ZERO**2))

    def test_no_numeric_gamma_singularity_and_exact_analytic_tail(self):
        c,i1,tail=archimedean_coefficient()
        self.assertLess(endpoints(c)[1],Fraction(-2))
        self.assertGreater(endpoints(i1)[0],Fraction(1,4))
        self.assertLess(endpoints(i1)[1],Fraction(3,10))
        self.assertGreater(endpoints(tail)[0],Fraction(3,4))
        self.assertGreater(endpoints(gamma_kernel(Fraction(1,10)))[0],
                           endpoints(gamma_kernel(Fraction(1,2)))[1])

    def test_prime_inventory_contains_only_2(self):
        a=self.r["arithmetic"]
        self.assertEqual(a["prime_powers"],[{"n":2,"von_mangoldt_base":2}])
        self.assertTrue(Fraction(69,100)<Fraction(a["log2_rational_interval"][0])
                        <Fraction(a["log2_rational_interval"][1])<Fraction(7,10))

    def test_nonzero_prime_2_and_complete_arch_terms(self):
        a=self.r["arithmetic"]
        self.assertLess(Fraction(a["raw_prime2_interval"][1]),0)
        self.assertLess(Fraction(a["raw_archimedean_interval"][1]),0)
        self.assertGreater(Fraction(a["raw_pole_interval"][0]),0)
        self.assertGreater(Fraction(a["raw_positive_regularized_J_interval"][0]),0)

    def test_actual_normalized_weil_entry_has_strict_positive_lower(self):
        a=self.r["arithmetic"]
        lo,hi=map(Fraction,a["normalized_complete_Weil_interval"])
        self.assertGreater(lo,MIN_NORMALIZED_WEIL_VALUE)
        self.assertLess(lo,hi)
        self.assertEqual(a["proved_normalized_strict_lower"],"1/1000")
        self.assertGreater(Fraction(a["raw_complete_Weil_interval"][0]),0)

    def test_finite_one_entry_never_promotes_to_all_index_or_RH(self):
        f=self.r["assurance"]
        self.assertTrue(f["this_one_core_diagonal_positive"])
        for k,v in f.items():
            if k!="this_one_core_diagonal_positive":
                self.assertFalse(v,k)
        self.assertEqual(self.r["status"],
                         "FIRST_CANONICAL_LF_CORE_WEIL_DIAGONAL_POSITIVE_NOT_ALL_INDEX")

    def test_insufficient_resolution_fails_closed(self):
        with self.assertRaises(ArithmeticError):
            audit(128,64)

    def test_invalid_inputs_and_inverted_intervals_rejected(self):
        with self.assertRaises(ValueError):
            covariance_at(Fraction(-1,4),256)
        with self.assertRaises(ValueError):
            covariance_at(Fraction(5,4),256)
        with self.assertRaises(ValueError):
            gamma_kernel(Fraction(0))
        with self.assertRaises(ArithmeticError):
            interval(Fraction(2),Fraction(1))
        for panels in (0,-1,True,200,256.0):
            with self.subTest(panels=panels),self.assertRaises(ValueError):
                audit(panels,256)

    def test_cli_replay_and_serialized_rational_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"first_actual.json"
            subprocess.run([
                sys.executable,"-m",
                "mathos.research.riemann_weil_lf_core_first_diagonal",
                "--half-panels","256","--dyadic-panels","256",
                "--output",str(path)
            ],check=True,capture_output=True,text=True)
            data=json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"],"mathos_tectx_weil_LF_core_first_diagonal/1")
            self.assertGreater(Fraction(data["arithmetic"]["normalized_complete_Weil_interval"][0]),
                               Fraction(1,1000))
            self.assertFalse(data["assurance"]["Riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
