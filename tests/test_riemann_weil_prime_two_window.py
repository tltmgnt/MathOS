"""Exact rational adversarial checks for actual prime-2 Weil compact-bump entry."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_prime_two_window import (
    WIDTH, CENTERS, L2_MIN_PRIME_CONV, PRIME2_LOWER_MAGNITUDE,
    ARCH_LOWER_MAGNITUDE,
    log2_bounds, support_pair, prime_power_support_inventory,
    off_diagonal_certificate, diagonal_entry_bound, report,
)


class PrimeTwoWeilTests(unittest.TestCase):
    def test_log2_enclosed_without_float(self):
        lo,hi=log2_bounds()
        self.assertGreater(lo,Fraction(69,100))
        self.assertLess(hi,Fraction(70,100))
        self.assertLess(lo,hi)
        self.assertLess(log2_bounds(8)[1]-log2_bounds(8)[0],hi-lo)

    def test_prime_windows_are_exact_rationals(self):
        self.assertEqual(WIDTH,Fraction(1,8))
        self.assertEqual(CENTERS,(Fraction(0),Fraction(3,4)))
        self.assertEqual(support_pair(CENTERS[1],CENTERS[0]),
                         (Fraction(1,2),Fraction(1)))
        self.assertEqual(support_pair(CENTERS[0],CENTERS[1]),
                         (Fraction(-1),Fraction(-1,2)))

    def test_only_prime_two_cross_terms(self):
        p=prime_power_support_inventory()
        self.assertEqual(p["only_possible_prime_power"],2)
        self.assertEqual(p["actual_nonzero_prime_pairs"],["01","10"])
        self.assertTrue(p["diagonals_prime_free"])
        self.assertTrue(p["spans"]["10"]["prime2_plus"])
        self.assertTrue(p["spans"]["01"]["prime2_minus"])
        for i in (0,1):
            self.assertFalse(p["spans"][f"{i}{i}"]["prime2_plus"])
            self.assertFalse(p["spans"][f"{i}{i}"]["prime2_minus"])

    def test_offdiag_genuine_nonzero_prime_contribution(self):
        c=off_diagonal_certificate()
        self.assertEqual(Fraction(c["at_log2_strict_lower"]),L2_MIN_PRIME_CONV)
        self.assertEqual(Fraction(c["prime2_strict_upper"]),-PRIME2_LOWER_MAGNITUDE)
        self.assertLess(Fraction(c["prime2_strict_upper"]),0)
        self.assertLess(Fraction(c["prime2_lower"]),
                        Fraction(c["prime2_strict_upper"]))

    def test_offdiag_nonzero_archimedean_contribution(self):
        c=off_diagonal_certificate()
        self.assertEqual(Fraction(c["archimedean_strict_upper"]),
                         -ARCH_LOWER_MAGNITUDE)
        self.assertLess(Fraction(c["archimedean_strict_upper"]),0)
        self.assertLess(Fraction(c["archimedean_lower"]),
                        Fraction(c["archimedean_strict_upper"]))

    def test_complete_cross_Weil_interval(self):
        c=off_diagonal_certificate()
        self.assertEqual(Fraction(c["full_Weil_cross_lower"]),Fraction(-1,2))
        self.assertEqual(
            Fraction(c["full_Weil_cross_strict_upper"]),
            Fraction(1,2)-PRIME2_LOWER_MAGNITUDE-ARCH_LOWER_MAGNITUDE)
        self.assertGreater(Fraction(c["full_Weil_cross_strict_upper"]),0)
        self.assertFalse(c["arithmetic_cross_term_computed_from_zeros"])

    def test_diagonal_prime_free_and_arch_rigorously_enclosed(self):
        c=diagonal_entry_bound()
        self.assertEqual(c["prime_power_exact"],"0/1")
        self.assertEqual(Fraction(c["archimedean_abs_upper"]),Fraction(169,16))
        self.assertEqual(Fraction(c["full_diagonal_upper"]),Fraction(177,16))
        self.assertFalse(c["diagonal_positivity_proved"])

    def test_false_global_certification_and_full_matrix_not_psd_proved(self):
        r=report()
        self.assertEqual(r["status"],"PRIME_TWO_ACTUAL_WEIL_CROSS_ENCLOSED_NOT_PSD_RH_OPEN")
        self.assertTrue(r["exact_rational_arithmetic_enclosures"]["all_pole_prime_and_archimedean_components_included"])
        self.assertFalse(r["exact_rational_arithmetic_enclosures"]["matrix_psd_certified"])
        self.assertFalse(any(r["assurance"].values()))

    def test_width_crosses_small_support_without_claiming_new_positivity(self):
        r=report()
        self.assertTrue(r["basis"]["support_not_inside_previous_yoshida_small_window"])
        self.assertFalse(r["basis"]["uses_zeta_zeros"])
        self.assertFalse(r["exact_rational_arithmetic_enclosures"]["numerically_tight_archimedean_integral"])

    def test_invalid_inputs(self):
        for v in (0,-1,33,True,2.5):
            with self.subTest(v=v),self.assertRaises(ValueError):
                log2_bounds(v)
        with self.assertRaises(ValueError):
            support_pair(0.75,Fraction(0))

    def test_cli_portable_rational_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"prime_two.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_prime_two_window",
                "--output",str(output)
            ],check=True,capture_output=True,text=True)
            r=json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(r["schema"],"mathos_tectx_weil_prime_two_window/1")
            self.assertLess(Fraction(r["exact_rational_arithmetic_enclosures"]["off_diagonal"]["prime2_strict_upper"]),0)
            self.assertFalse(r["assurance"]["Riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
