"""Adversarial checks for actual fourth Weil direction, not a synthetic matrix."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from mpmath import iv

from mathos.research.riemann_weil_certified_fourth import (
    A, FOUR_CENTERS, NEW_CENTER, LOWER, PRIME_CUTOFF,
    _f4_rational, _new_prime_tail, _prime_powers_up_to, audit,
)
from mathos.research.riemann_weil_generalized_schur import verified_schur


class FourthWeilTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        iv.dps=60
        cls.report=audit(65536)

    def test_fourth_center_is_actual_distinct_arithmetic_test(self):
        self.assertEqual(NEW_CENTER,Fraction(21,5))
        self.assertEqual(len(set(FOUR_CENTERS)),4)
        self.assertTrue(self.report["basis"]["all_new_arithmetic_cross_entries_computed"])
        self.assertFalse(self.report["basis"]["nontrivial_zero_locations_used_as_input"])

    def test_prime_power_enumerator_includes_prime_and_powers_not_composites(self):
        rows=_prime_powers_up_to(64)
        self.assertIn((2,2),rows)
        self.assertIn((4,2),rows)
        self.assertIn((8,2),rows)
        self.assertIn((9,3),rows)
        self.assertIn((49,7),rows)
        self.assertNotIn((6,2),rows)
        self.assertNotIn((12,2),rows)
        self.assertEqual(len(rows),len(set(rows)))

    def test_prime_tail_exact_and_fails_outside_window(self):
        d=_new_prime_tail()
        self.assertGreater(d,0)
        self.assertLess(d,Fraction(1,10**8))
        self.assertEqual(self.report["analytic_certification"]["new_prime_power_tail_bound_exact"],
                         f"{d.numerator}/{d.denominator}")
        self.assertEqual(PRIME_CUTOFF,65536)

    def test_fourth_derivative_envelopes_depend_on_center_pair(self):
        envelopes=[_f4_rational(c+NEW_CENTER) for c in FOUR_CENTERS]
        self.assertEqual(len(envelopes),4)
        self.assertEqual(envelopes,sorted(envelopes))
        self.assertGreater(envelopes[-1],envelopes[0])
        with self.assertRaises(ValueError):
            _f4_rational(Fraction(100))

    def test_full_four_by_four_symmetric_Weil_and_l2_intervals(self):
        matrices=self.report["verified_matrix"]
        for key in ["weil_G_intervals","L2_intervals"]:
            entries=matrices[key]
            self.assertEqual(len(entries),4)
            for i in range(4):
                self.assertEqual(len(entries[i]),4)
                for j in range(4):
                    self.assertEqual(entries[i][j],entries[j][i])
                    a,b=map(Fraction,entries[i][j])
                    self.assertLess(a,b)

    def test_all_full_shifted_ldl_pivots_strictly_positive(self):
        x=self.report["verified_matrix"]
        self.assertEqual(len(x["shifted_G_minus_kappa_L_pivots"]),4)
        self.assertEqual(len(x["L2_pivots"]),4)
        for kind in ["L2_pivots","shifted_G_minus_kappa_L_pivots"]:
            for lo,hi in x[kind]:
                self.assertGreater(Fraction(lo),0)
                self.assertGreater(Fraction(hi),Fraction(lo))

    def test_real_fourth_block_schur_strictly_positive(self):
        r=self.report["verified_matrix"]["fourth_direction_schur"]
        self.assertEqual(r["old_dim"],3)
        self.assertEqual(r["new_dim"],1)
        self.assertTrue(r["all_pivots_positive"])
        self.assertGreater(Fraction(r["schur_pivots"][0][0]),0)

    def test_old_generalized_gap_fails_on_real_fourth_direction(self):
        r=self.report["verified_matrix"]
        self.assertEqual(r["previous_3D_bound"],"1/50000000")
        self.assertFalse(r["previous_3D_generalized_lower_bound_survives"])
        low,high=map(Fraction,r["failed_previous_3D_bound_schur_interval"])
        self.assertLess(high,0)
        self.assertLess(low,high)
        self.assertEqual(r["strict_generalized_lambda_lower"],"1/1000000000")

    def test_prime_archimedean_errors_all_bounded(self):
        errors=self.report["analytic_certification"]["new_entry_errors"]
        self.assertEqual(len(errors),4)
        expected={"simpson","digamma","archimedean_infinite_tail",
                  "prime_power_infinite_tail","total"}
        for item in errors:
            self.assertEqual(set(item),expected)
            for key in expected:
                self.assertGreater(Fraction(item[key][1]),0)
                self.assertGreaterEqual(Fraction(item[key][1]),Fraction(item[key][0]))
            self.assertLess(Fraction(item["total"][1]),Fraction(1,1000))

    def test_synthetic_indefinite_new_block_rejected(self):
        M=[[iv.mpf(2),iv.mpf(0)],[iv.mpf(0),iv.mpf(-1)]]
        with self.assertRaises(ArithmeticError):
            verified_schur(M,1)

    def test_no_fifth_or_rh_promotion(self):
        flags=self.report["assurance"]
        self.assertTrue(flags["actual_fourth_direction_cross_terms_enclosed"])
        self.assertTrue(flags["fixed_four_span_generalized_positivity"])
        for k,v in flags.items():
            if k not in {"actual_fourth_direction_cross_terms_enclosed",
                          "fixed_four_span_generalized_positivity"}:
                self.assertFalse(v,k)

    def test_invalid_panels_rejected(self):
        for n in [1,1024,4096,8192,16384,0,65536.0,True]:
            with self.subTest(panels=n),self.assertRaises(ValueError):
                audit(n)

    def test_cli_portable_certificate(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"fourth.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_certified_fourth",
                "--panels","65536","--output",str(path),
            ],capture_output=True,text=True,check=True)
            data=json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"],"mathos_tectx_weil_certified_fourth_direction/1")
            self.assertEqual(len(data["verified_matrix"]["weil_G_intervals"]),4)
            self.assertGreater(Fraction(data["verified_matrix"]["fourth_direction_schur"]["schur_pivots"][0][0]),0)
            self.assertFalse(data["assurance"]["riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
