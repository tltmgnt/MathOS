"""Adversarial exact finite-prime and verified 3D Weil Gram tests."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_prime_four_five_gram3 import (
    CENTERS, LONG_SPACING, MIN_EIGEN,
    _prime_support_inventory,_rational_log_bounds,audit,
)


class PrimeFourFiveWeilGramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit(256)

    def test_actual_distinct_compact_support_centers(self):
        self.assertEqual(CENTERS,(Fraction(0),Fraction(3,4),Fraction(3,2)))
        self.assertEqual(len(set(CENTERS)),3)
        self.assertTrue(self.report["test_family"]["every_direction_is_compactly_supported"])

    def test_prime_power_support_inventory_is_rigorous(self):
        x=_prime_support_inventory()
        self.assertEqual(x["short_prime_powers"],[2])
        self.assertEqual(x["long_prime_powers"],[4,5])
        self.assertEqual(x["long_support"],["5/4","7/4"])
        for n in range(2,7):
            low,hi=map(Fraction,x["log_intervals"][str(n)])
            self.assertLess(low,hi)
        self.assertFalse(not x["no_nontrivial_zeta_zero_data"])

    def test_four_and_five_are_nonzero_negative_arithmetic_terms(self):
        parts=self.report["arithmetic"]["new_prime_power_components"]
        self.assertEqual(set(parts),{"4","5"})
        self.assertEqual(parts["4"]["von_mangoldt_base"],2)
        self.assertEqual(parts["5"]["von_mangoldt_base"],5)
        for name,datum in parts.items():
            lo,hi=map(Fraction,datum["interval"])
            self.assertLess(lo,hi)
            self.assertLess(hi,0,name)

    def test_long_gamma_cross_negative_and_pole_positive(self):
        a=self.report["arithmetic"]
        self.assertLess(Fraction(a["new_long_archimedean_interval"][1]),0)
        self.assertLess(Fraction(a["new_long_prime_interval"][1]),0)
        self.assertGreater(Fraction(a["new_long_pole_interval"][0]),0)

    def test_full_three_by_three_symmetric_actual_weil_entries(self):
        a=self.report["arithmetic"]
        M=a["complete_real_symmetric_gram"]
        self.assertEqual(len(M),3)
        for i in range(3):
            self.assertEqual(len(M[i]),3)
            for j in range(3):
                self.assertEqual(M[i][j],M[j][i])
                lo,hi=map(Fraction,M[i][j])
                self.assertLess(lo,hi)
        self.assertEqual(M[0][0],M[1][1])
        self.assertEqual(M[0][0],M[2][2])
        self.assertEqual(M[0][1],M[1][2])
        self.assertEqual(M[0][2],a["new_long_weil_entry"])

    def test_gershgorin_gap_strict_and_exact(self):
        a=self.report["arithmetic"]
        self.assertEqual(a["strict_lambda_min_lower"],"1/200")
        self.assertGreater(Fraction(a["gershgorin_rational_lower"]),MIN_EIGEN)

    def test_three_interval_ldl_pivots_strictly_positive(self):
        pivots=self.report["arithmetic"]["interval_LDL_pivots"]
        self.assertEqual(len(pivots),3)
        for lo,hi in pivots:
            self.assertGreater(Fraction(lo),0)
            self.assertGreaterEqual(Fraction(hi),Fraction(lo))

    def test_no_rh_or_infinite_dimensional_promotion(self):
        r=self.report
        self.assertTrue(r["trust_boundary"]["fixed_3D_positive_definite"])
        for name,value in r["trust_boundary"].items():
            if name!="fixed_3D_positive_definite":
                self.assertFalse(value,name)
        self.assertFalse(r["arithmetic"]["uses_zeta_zeros_as_input"])

    def test_logarithmic_interval_invalid_input_rejected(self):
        for n in [-1,0,1,2.0,True]:
            with self.subTest(n=n),self.assertRaises(ValueError):
                _rational_log_bounds(n)

    def test_invalid_panels_rejected(self):
        for n in [0,64,128,257,512.0,True]:
            with self.subTest(n=n),self.assertRaises(ValueError):
                audit(n)

    def test_cli_certificate_rational_endpoints(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"3d.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_prime_four_five_gram3",
                "--panels","256","--output",str(path),
            ],check=True,capture_output=True,text=True)
            r=json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(r["schema"],"mathos_tectx_weil_prime_four_five_gram3/1")
            self.assertGreater(Fraction(r["arithmetic"]["gershgorin_rational_lower"]),Fraction(1,200))
            self.assertFalse(r["trust_boundary"]["Riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
