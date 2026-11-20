"""Adversarial reproduction of rigorous prime-active 2x2 Weil PSD certificate."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mpmath import iv

from mathos.research.riemann_weil_prime_two_interval import (
    F,I,H,D,R,ZERO_CUTOFF,POSITIVE_FLOOR,
    phi,Kbox,_moments,_regularizer,_diagonal_differences,
    _prime_cross,_arch_cross,audit,
)


class PrimeTwoIntervalWeilTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        iv.dps=45
        cls.r=audit(256)

    def test_exact_window_and_near_zero_cutoff(self):
        self.assertEqual(H,Fraction(1,8))
        self.assertEqual(D,Fraction(3,4))
        self.assertEqual(R,Fraction(1,4))
        self.assertEqual(ZERO_CUTOFF,Fraction(1,2048))

    def test_interval_bump_support_and_peak(self):
        self.assertEqual(str(phi(Fraction(1),Fraction(2))),"[0.0, 0.0]")
        p=phi(Fraction(-1,16),Fraction(1,16))
        self.assertLessEqual(float(p.a),0.0+1)
        self.assertGreaterEqual(float(p.b),1.0)
        with self.assertRaises(ValueError):
            phi(Fraction(1,4),Fraction(0))

    def test_kernel_enclosure_decreasing(self):
        left=Kbox(Fraction(1,2),Fraction(3,4))
        right=Kbox(Fraction(3,4),Fraction(1))
        self.assertGreater(float(left.b),float(right.a))
        with self.assertRaises(ValueError):
            Kbox(Fraction(0),Fraction(1))

    def test_diagonal_positive_with_strict_margin(self):
        p=self.r["arithmetic"]
        dlo,dhi=map(Fraction,p["diagonal_Weil_entry"])
        clo,chi=map(Fraction,p["cross_Weil_entry"])
        self.assertGreater(dlo,Fraction(44,1000))
        self.assertLess(dhi,Fraction(67,1000))
        self.assertLess(chi,0)
        self.assertLess(clo,chi)
        self.assertGreater(dlo-max(abs(clo),abs(chi)),POSITIVE_FLOOR)

    def test_each_LDL_pivot_positive(self):
        pivots=self.r["arithmetic"]["interval_LDL_pivots"]
        self.assertEqual(len(pivots),2)
        self.assertTrue(all(Fraction(low)>0 for low,high in pivots))

    def test_actual_prime_two_term_nonzero_negative(self):
        low,high=map(Fraction,self.r["arithmetic"]["prime_cross"])
        self.assertLess(low,high)
        self.assertLess(high,-Fraction(4,100))
        self.assertGreater(low,-Fraction(5,100))

    def test_actual_arch_cross_term_nonzero_negative(self):
        low,high=map(Fraction,self.r["arithmetic"]["arch_cross"])
        self.assertLess(low,high)
        self.assertLess(high,-Fraction(19,1000))
        self.assertGreater(low,-Fraction(22,1000))

    def test_pole_cross_positive_and_full_matrix_normalized(self):
        a=self.r["arithmetic"]
        self.assertGreater(Fraction(a["pole_cross"][0]),0)
        self.assertGreater(Fraction(a["pole_diagonal"][0]),0)
        self.assertIn("Suzuki",self.r["normalization"])
        self.assertEqual(a["proved_eigenvalue_floor_rational"],"137/5000")

    def test_explicit_interval_integration_nonempty(self):
        p=self.r["arithmetic"]
        for name in ["pole_cross","pole_diagonal","prime_cross","arch_diagonal",
                     "arch_cross","diagonal_Weil_entry","cross_Weil_entry"]:
            low,high=map(Fraction,p[name])
            self.assertLess(low,high,name)

    def test_near_zero_regularizer_and_diagonal_integral(self):
        # Explicit cancellation is finite, and square-difference J>=0.
        r=_regularizer(64)
        j=_diagonal_differences(32)
        self.assertGreater(float(r.a),0)
        self.assertGreaterEqual(float(j.a),0)

    def test_unrelated_Weil_space_and_RH_not_promoted(self):
        flags=self.r["trust_boundary"]
        self.assertTrue(flags["positive_definite_fixed_2x2"])
        self.assertFalse(flags["positive_all_support_windows"])
        self.assertFalse(flags["all_index_Weil_PSD"])
        self.assertFalse(flags["Riemann_hypothesis_proved"])
        self.assertFalse(flags["full_Weil_Hilbert_space_constructed"])

    def test_reject_invalid_panels(self):
        for n in [0,1,128,257,-256,256.0,True]:
            with self.subTest(n=n),self.assertRaises(ValueError):
                audit(n)

    def test_cli_portable_rational_ldl(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"certified_prime_two.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_prime_two_interval",
                "--panels","256","--output",str(output)
            ],capture_output=True,text=True,check=True)
            r=json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(r["schema"],"mathos_tectx_weil_prime_two_interval_psd/1")
            self.assertEqual(Fraction(r["arithmetic"]["proved_eigenvalue_floor_rational"]),
                             Fraction(137,5000))
            self.assertTrue(all(Fraction(low)>0 for low,high
                                in r["arithmetic"]["interval_LDL_pivots"]))
            self.assertFalse(r["trust_boundary"]["Riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
