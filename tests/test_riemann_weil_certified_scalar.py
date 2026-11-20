"""Tests for rigorously enclosed one-dimensional Weil-form scalar."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mpmath import iv, mp

from mathos.research.riemann_weil_certified_scalar import (
    _digamma_real_enclosure, _prime_power_base, _rational_bound,
    _outward_decimal, audit,
)


class CertifiedWeilScalarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        iv.dps=45

    def test_prime_power_recognizer(self):
        for n, p in [(2,2),(4,2),(8,2),(9,3),(16,2),(25,5),(49,7),(121,11)]:
            self.assertEqual(_prime_power_base(n),p)
        for n in [0,1,6,10,12,15,18,36,100]:
            self.assertIsNone(_prime_power_base(n))

    def test_endpoint_conversion_exact(self):
        x=iv.mpf([1,2])/4
        self.assertLessEqual(_rational_bound(x,False), Fraction(1,4))
        self.assertGreaterEqual(_rational_bound(x,True), Fraction(1,2))
        a,b=_outward_decimal(x)
        self.assertLessEqual(Fraction(a), Fraction(1,4))
        self.assertGreaterEqual(Fraction(b), Fraction(1,2))

    def test_digamma_quarter_enclosure(self):
        # Existing closed form at 1/4 used only as independent regression:
        # psi(1/4) = -gamma - pi/2 - 3 log(2).
        v=_digamma_real_enclosure(iv.mpf([0,0]))
        with mp.workdps(65):
            x=-mp.euler-mp.pi/2-3*mp.log(2)
            self.assertLess(float(_rational_bound(v,False)),float(x))
            self.assertGreater(float(_rational_bound(v,True)),float(x))

    def test_digamma_encloses_reference_at_high_t(self):
        with mp.workdps(65):
            for t in [0,1,5,25,45]:
                v=_digamma_real_enclosure(iv.mpf(t))
                x=mp.re(mp.digamma(mp.mpf(1)/4+mp.j*t/2))
                self.assertLessEqual(_rational_bound(v,False), Fraction(str(x)))
                self.assertGreaterEqual(_rational_bound(v,True), Fraction(str(x)))

    def test_certified_scalar_contains_strict_positive_interval(self):
        r=audit(2048)
        lo,hi=map(Fraction,r["components_outward_rationals"]["full_G_eigenvalue"])
        self.assertGreater(lo,0)
        self.assertLess(lo,hi)
        self.assertLess(hi,Fraction(1,10))
        self.assertTrue(r["assurance"]["one_test_function_positive_enclosed"])
        self.assertFalse(r["assurance"]["riemann_hypothesis_proved"])

    def test_refinement_increases_information_not_promotion(self):
        lo1,hi1=map(Fraction,audit(2048)["components_outward_rationals"]["full_G_eigenvalue"])
        lo2,hi2=map(Fraction,audit(4096)["components_outward_rationals"]["full_G_eigenvalue"])
        self.assertLessEqual(lo1,lo2)
        self.assertLessEqual(hi2,hi1)

    def test_finite_gram_interval_separate_from_prime_tail(self):
        r=audit(2048)
        a,b=map(Fraction,r["components_outward_rationals"]["finite_G_256_eigenvalue"])
        c,d=map(Fraction,r["components_outward_rationals"]["full_G_eigenvalue"])
        self.assertLessEqual(c,a)
        self.assertGreaterEqual(d,b)
        self.assertEqual(r["parameters"]["prime_cutoff"],256)

    def test_unavailable_higher_dimensional_claims_rejected(self):
        r=audit(2048)
        self.assertFalse(r["assurance"]["all_three_dimensional_Weil_Gram_enclosed"])
        self.assertFalse(r["assurance"]["all_admissible_test_functions_positive"])
        self.assertFalse(r["assurance"]["global_Weil_Hilbert_space_constructed"])

    def test_invalid_panels_rejected(self):
        for panels in [0,1024,2049,65536,2048.0,True]:
            with self.subTest(panels=panels),self.assertRaises(ValueError):
                audit(panels)

    def test_cli_noncertification(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/"certificate.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_certified_scalar",
                "--panels","2048","--output",str(target)
            ],capture_output=True,text=True,check=True)
            report=json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(report["schema"],"mathos_tectx_weil_certified_scalar/1")
            self.assertGreater(Fraction(report["components_outward_rationals"]["full_G_eigenvalue"][0]),0)
            self.assertFalse(report["assurance"]["riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
