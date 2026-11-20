"""Arithmetic and strict-positive matrix tests for actual compact Weil Gram4."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_prime_eight_nine_eleven_gram4 import (
    NEW_CENTER, CENTERS, SPECTRAL_FLOOR,
    _fourth_prime_support, _rational_log_bounds, audit,
)


class PrimeEightNineElevenGram4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate=audit(256)

    def test_actual_distinct_fourth_compact_direction(self):
        self.assertEqual(NEW_CENTER,Fraction(9,4))
        self.assertEqual(len(set(CENTERS)),4)
        self.assertTrue(self.certificate["basis"]["all_compactly_supported"])

    def test_exact_new_prime_power_inventory(self):
        inv=_fourth_prime_support()
        self.assertEqual(inv["support"],["2/1","5/2"])
        self.assertEqual(inv["actual_prime_powers"],[8,9,11])
        self.assertEqual(inv["vanishing_mangoldt_candidates"],[10,12])
        self.assertEqual(inv["von_mangoldt_bases"],{"8":2,"9":3,"11":11})
        for n in range(7,14):
            lo,hi=map(Fraction,inv["log_rational_intervals"][str(n)])
            self.assertLess(lo,hi)

    def test_all_three_new_prime_terms_strict_negative(self):
        parts=self.certificate["arithmetical_certification"]["new_prime_power_parts"]
        self.assertEqual(set(parts),{"8","9","11"})
        for n,p in ((8,2),(9,3),(11,11)):
            value=parts[str(n)]
            self.assertEqual(value["base_prime"],p)
            lo,hi=map(Fraction,value["interval"])
            self.assertLess(lo,hi)
            self.assertLess(hi,0)

    def test_actual_pole_gamma_and_prime_signs(self):
        a=self.certificate["arithmetical_certification"]
        self.assertGreater(Fraction(a["new_pole_interval"][0]),0)
        self.assertLess(Fraction(a["new_archimedean_interval"][1]),0)
        self.assertLess(Fraction(a["new_prime_total_interval"][1]),0)

    def test_full_actual_Weil_4x4_toeplitz_and_intervals(self):
        a=self.certificate["arithmetical_certification"]
        M=a["full_symmetric_weil_matrix"]
        self.assertEqual(len(M),4)
        for i in range(4):
            for j in range(4):
                self.assertEqual(M[i][j],M[j][i])
                self.assertEqual(M[i][j],M[0][abs(i-j)])
                lo,hi=map(Fraction,M[i][j])
                self.assertLessEqual(lo,hi)
        self.assertEqual(M[0][3],a["new_full_weil_entry"])

    def test_strict_rational_gershgorin_floor(self):
        a=self.certificate["arithmetical_certification"]
        self.assertEqual(a["claimed_strict_lambda_lower"],"1/10000")
        self.assertGreater(Fraction(a["verified_gershgorin_floor_exact"]),SPECTRAL_FLOOR)

    def test_four_shifted_interval_LDL_pivots(self):
        p=self.certificate["arithmetical_certification"]["shifted_G_minus_kappa_I_LDL_pivots"]
        self.assertEqual(len(p),4)
        self.assertTrue(all(Fraction(a)>0 and Fraction(b)>=Fraction(a)
                            for a,b in p))

    def test_no_universal_PSD_or_RH_claims(self):
        f=self.certificate["assurance"]
        self.assertTrue(f["actual_compact_four_dimensional_Weil_PSD"])
        for key in f:
            if key!="actual_compact_four_dimensional_Weil_PSD":
                self.assertFalse(f[key],key)
        self.assertTrue(self.certificate["arithmetical_certification"]["no_zeta_zeros_as_input"])

    def test_invalid_logs_and_panel_counts_fail_closed(self):
        for n in (-1,0,1,True,2.5):
            with self.subTest(n=n),self.assertRaises(ValueError):
                _rational_log_bounds(n)
        for n in (0,64,128,257,256.0,True):
            with self.subTest(n=n),self.assertRaises(ValueError):
                audit(n)

    def test_portable_exact_rational_certificate(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/"weil4.json"
            subprocess.run([
                sys.executable,"-m",
                "mathos.research.riemann_weil_prime_eight_nine_eleven_gram4",
                "--panels","256","--output",str(output)
            ],check=True,capture_output=True,text=True)
            c=json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(c["schema"],"mathos_tectx_weil_prime_8_9_11_gram4/1")
            self.assertGreater(Fraction(c["arithmetical_certification"]["verified_gershgorin_floor_exact"]),SPECTRAL_FLOOR)
            self.assertFalse(c["assurance"]["Riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
