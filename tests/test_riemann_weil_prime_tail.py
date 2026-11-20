"""Exact rational and adversarial regression for Weil prime-tail estimates."""
import json
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_prime_tail import (
    per_entry_prime_tail_bound, gram_quadratic_tail_bound, report,
)


class WeilPrimeTailTests(unittest.TestCase):
    def test_exact_bound_positive_and_small(self):
        d = per_entry_prime_tail_bound()
        self.assertIsInstance(d, Fraction)
        self.assertGreater(d, 0)
        self.assertLess(d, Fraction(1, 10**17))

    def test_beta_and_exponent_exact_reference(self):
        a = Fraction(1, 50)
        beta = (Fraction(5)-1-a)/(2*a)
        x = (Fraction(5)-1-a)**2/(4*a)
        self.assertEqual(beta, Fraction(199, 2))
        self.assertEqual(x, Fraction(39601, 200))
        self.assertEqual(
            per_entry_prime_tail_bound(),
            10*(Fraction(5)/beta+1/beta**2)/(1+x/16)**16,
        )

    def test_uniform_gram_bound_linear_in_dimension(self):
        for m in [1,2,3,10,100,1000]:
            self.assertEqual(gram_quadratic_tail_bound(m), m*per_entry_prime_tail_bound())

    def test_reject_bad_dimensions(self):
        for m in [0,-1,1.0,True,100001]:
            with self.subTest(m=m), self.assertRaises(ValueError):
                gram_quadratic_tail_bound(m)

    def test_default_basis(self):
        r = report()
        self.assertEqual(r["parameters"]["centers_exact"],["0/1","1/5","1/2"])
        self.assertEqual(r["parameters"]["gaussian_a_exact"],"1/50")
        self.assertEqual(r["parameters"]["cutoff"],256)
        self.assertFalse(any(r["positivity_contract"].values()))

    def test_cutoff_monotonic_uniform_validity(self):
        a = report(prime_cutoff=256)
        b = report(prime_cutoff=10000)
        self.assertEqual(a["analytic_prime_tail"]["per_gram_entry_upper_rational"],
                         b["analytic_prime_tail"]["per_gram_entry_upper_rational"])
        self.assertTrue(b["parameters"]["bound_valid_for_all_larger_cutoffs"])

    def test_invalid_centers_rejected(self):
        examples=[(),(Fraction(-1,100),),(Fraction(3,4),),(0,),tuple([Fraction(0)]*21)]
        for centers in examples:
            with self.subTest(centers=centers),self.assertRaises(ValueError):
                report(centers)

    def test_invalid_cutoffs_rejected(self):
        for n in [0,255,-1,256.0,True,10**9+1]:
            with self.subTest(n=n),self.assertRaises(ValueError):
                report(prime_cutoff=n)

    def test_comparative_basis_dimensions(self):
        small=report((Fraction(0),))
        big=report((Fraction(0),Fraction(1,2)))
        self.assertEqual(
            Fraction(big["analytic_prime_tail"]["quadratic_form_norm_upper_rational"]),
            2*Fraction(small["analytic_prime_tail"]["quadratic_form_norm_upper_rational"])
        )

    def test_does_not_claim_full_arithmetic_certification(self):
        r=report()
        self.assertEqual(len(r["other_unbounded_errors"]),5)
        self.assertFalse(r["positivity_contract"]["finite_matrix_psd_certified"])
        self.assertFalse(r["positivity_contract"]["global_weil_psd_certified"])
        self.assertFalse(r["positivity_contract"]["riemann_hypothesis_proved"])

    def test_cli_generates_machine_readable_rational_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/"tail.json"
            subprocess.run(
                [sys.executable,"-m","mathos.research.riemann_weil_prime_tail",
                 "--centers","0,1/5,1/2","--prime-cutoff","512",
                 "--output",str(target)],
                capture_output=True,text=True,check=True,
            )
            r=json.loads(target.read_text(encoding="utf-8"))
            self.assertGreater(Fraction(r["analytic_prime_tail"]["per_gram_entry_upper_rational"]),0)
            self.assertFalse(any(r["positivity_contract"].values()))

    def test_cli_fails_closed_for_uncovered_basis(self):
        r=subprocess.run(
            [sys.executable,"-m","mathos.research.riemann_weil_prime_tail",
             "--centers","0,3/4"],
            capture_output=True,text=True,
        )
        self.assertNotEqual(r.returncode,0)
        self.assertIn("centers must be",r.stderr)


if __name__=="__main__":
    unittest.main()
