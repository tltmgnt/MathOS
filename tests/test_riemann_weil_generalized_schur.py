"""Adversarial tests for verified generalized Weil eigenvalues and Schur gates."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mpmath import iv
from mathos.research.riemann_weil_generalized_schur import (
    LOWER, UPPER, UPPER_WITNESS, _ldl_intervals, _linear_combination,
    _rayleigh, audit, verified_schur,
)


class WeilGeneralizedSchurTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        iv.dps = 60
        cls.report = audit(8192)

    def test_reference_gram_is_positive(self):
        pivots=self.report["certified_generalized_eigenvalue"]["L2_pivots"]
        self.assertEqual(len(pivots),3)
        self.assertTrue(all(Fraction(lo)>0 for lo,hi in pivots))

    def test_generalized_lower_bound(self):
        result=self.report["certified_generalized_eigenvalue"]
        self.assertEqual(Fraction(result["strict_lower"]),LOWER)
        self.assertTrue(all(Fraction(lo)>0 for lo,hi
                            in result["shifted_G_minus_kappa_L_pivots"]))

    def test_generalized_upper_bound_witness(self):
        x=self.report["certified_generalized_eigenvalue"]
        self.assertEqual(Fraction(x["strict_upper"]),UPPER)
        self.assertEqual(x["integer_Rayleigh_upper_witness"],list(UPPER_WITNESS))
        lo,hi=map(Fraction,x["Rayleigh_G_minus_upper_L_interval"])
        self.assertLess(hi,0)
        self.assertLess(lo,hi)

    def test_nested_schur_real_weil_growing_1_2_3(self):
        items=self.report["nested_verified_schur"]["extension_results"]
        self.assertEqual([x["old_dim"] for x in items],[1,2])
        self.assertEqual([x["new_dim"] for x in items],[1,1])
        for item in items:
            self.assertTrue(item["all_pivots_positive"])
            self.assertTrue(all(Fraction(lo)>0 for lo,hi in item["old_pivots"]))
            self.assertTrue(all(Fraction(lo)>0 for lo,hi in item["schur_pivots"]))

    def test_three_by_three_ref_intervals_are_symmetric(self):
        p=self.report["certified_generalized_eigenvalue"]
        for key in ["matrix_intervals","reference_L2_intervals"]:
            M=p[key]
            self.assertEqual(len(M),3)
            for i in range(3):
                for j in range(3):
                    self.assertEqual(M[i][j],M[j][i])
                    self.assertLessEqual(Fraction(M[i][j][0]),Fraction(M[i][j][1]))

    def test_synthetic_extension_is_not_weil_certificate(self):
        # Pure algebra: this checks block-Schur correctness, not a new
        # fourth arithmetic Weil test function.
        M=[[iv.mpf(3),iv.mpf(1),iv.mpf(0)],
           [iv.mpf(1),iv.mpf(3),iv.mpf(0)],
           [iv.mpf(0),iv.mpf(0),iv.mpf(2)]]
        r=verified_schur(M,2)
        self.assertTrue(r["all_pivots_positive"])
        self.assertGreater(Fraction(r["schur_pivots"][0][0]),0)
        self.assertFalse(self.report["nested_verified_schur"]["fourth_or_higher_dimensional_actual_Weil_blocks_certified"])

    def test_synthetic_schur_rejects_indefinite_new_direction(self):
        M=[[iv.mpf(1),iv.mpf(2)],
           [iv.mpf(2),iv.mpf(1)]]
        with self.assertRaises(ArithmeticError):
            verified_schur(M,1)

    def test_synthetic_schur_rejects_ambiguous_new_direction(self):
        M=[[iv.mpf(1),iv.mpf(0)],
           [iv.mpf(0),iv.mpf([-1,1])]]
        with self.assertRaises(ArithmeticError):
            verified_schur(M,1)

    def test_reject_non_symmetric_interval_data(self):
        with self.assertRaises(ValueError):
            _ldl_intervals([[iv.mpf(2),iv.mpf(0)],
                            [iv.mpf(1),iv.mpf(2)]])

    def test_invalid_schur_and_matrix_shapes(self):
        with self.assertRaises(ValueError):
            verified_schur([[iv.mpf(1)]],1)
        with self.assertRaises(ValueError):
            verified_schur([[iv.mpf(1),iv.mpf(0)],
                            [iv.mpf(0),iv.mpf(1)]],True)
        with self.assertRaises(ValueError):
            _linear_combination([[iv.mpf(1)]],[[iv.mpf(1),iv.mpf(0)]],Fraction(1))
        with self.assertRaises(ValueError):
            _rayleigh([[iv.mpf(1)]],(1,2))

    def test_no_global_positivity_promotion(self):
        flags=self.report["assurance"]
        self.assertTrue(flags["fixed_three_span_generalized_positivity_certified"])
        for name,value in flags.items():
            if name!="fixed_three_span_generalized_positivity_certified":
                self.assertFalse(value,name)

    def test_outward_rational_certificate_roundtrip(self):
        with tempfile.TemporaryDirectory() as dirname:
            output=Path(dirname)/"generalized.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_generalized_schur",
                "--panels","8192","--output",str(output)
            ],check=True,capture_output=True,text=True)
            r=json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(r["schema"],"mathos_tectx_weil_generalized_schur/1")
            self.assertTrue(all(Fraction(v[0])>0 for v in
                r["certified_generalized_eigenvalue"]["shifted_G_minus_kappa_L_pivots"]))
            self.assertFalse(r["assurance"]["riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
