"""Tests for exact prime-support and all-index/RH-equivalence guard."""
import json
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_vanishing_floor_gate import (
    ceiling, support_pair, candidate_prime_powers, report,
    vanishing_floor_equivalence,
)


class WeilVanishingFloorTests(unittest.TestCase):
    def test_fraction_ceil(self):
        for value,expected in [
            (Fraction(0),0),(Fraction(1,4),1),
            (Fraction(7,4),2),(Fraction(-1,4),0),
            (Fraction(-7,4),-1),(Fraction(2),2),
        ]:
            self.assertEqual(ceiling(value),expected)

    def test_pair_support_exact(self):
        a={"support_left":"0/1","support_right":"1/2"}
        b={"support_left":"1/4","support_right":"3/4"}
        r=support_pair(a,b)
        self.assertEqual(r["support"],["-3/4","1/4"])
        self.assertEqual(r["max_abs_log_coordinate"],"3/4")
        self.assertEqual(r["rigorous_integer_prime_power_cap"],3)

    def test_symmetric_pair_support_reflects(self):
        a={"support_left":"-1/4","support_right":"1/4"}
        b={"support_left":"1/1","support_right":"3/2"}
        x=support_pair(a,b)
        y=support_pair(b,a)
        self.assertEqual(Fraction(x["support"][0]),-Fraction(y["support"][1]))
        self.assertEqual(Fraction(x["support"][1]),-Fraction(y["support"][0]))
        self.assertEqual(x["rigorous_integer_prime_power_cap"],y["rigorous_integer_prime_power_cap"])

    def test_cap_enumeration_includes_prime_powers_and_excludes_composites(self):
        x=candidate_prime_powers(64)
        for pair in [(2,2),(4,2),(8,2),(9,3),(16,2),(25,5),(49,7)]:
            self.assertIn(pair,x)
        self.assertNotIn((6,2),x)
        self.assertNotIn((12,2),x)
        self.assertEqual(len(x),len(set(x)))

    def test_small_cap_has_no_primes(self):
        self.assertEqual(candidate_prime_powers(1),[])

    def test_all_index_principal_submatrix_equivalence_flags(self):
        theorem=vanishing_floor_equivalence()
        self.assertTrue(theorem["RH_equivalent_if_canonical_Weil_test_core"])
        self.assertFalse(theorem["all_index_hypothesis_proved"])
        self.assertFalse(theorem["is_new_RH_proof"])
        self.assertIn("zero-extend",theorem["proof"])

    def test_pair_count_and_bump_enumeration(self):
        for n in [1,2,3,8,16]:
            data=report(n)
            ar=data["arithmetic_support"]
            self.assertEqual(ar["pair_count"],n*(n+1)//2)
            self.assertEqual(len(ar["pair_bounds"]),n*(n+1)//2)
            self.assertGreaterEqual(ar["maximum_finite_prime_power_cap"],1)

    def test_no_rh_or_gram_promotion(self):
        data=report(8)
        self.assertFalse(any(data["assurance"].values()))
        self.assertFalse(data["arithmetic_support"]["prime_terms_fully_evaluated"])
        self.assertFalse(data["arithmetic_support"]["archimedean_terms_fully_evaluated"])
        self.assertFalse(data["arithmetic_support"]["Gram_eigenvalue_certification_performed"])

    def test_invalid_inputs(self):
        for n in [0,-1,65,True,1.5]:
            with self.subTest(n=n),self.assertRaises(ValueError):
                report(n)
        for cap in [0,-1,200001,True,2.0]:
            with self.subTest(cap=cap),self.assertRaises(ValueError):
                candidate_prime_powers(cap)
        with self.assertRaises(ValueError):
            ceiling(0.3)

    def test_cli_machine_readable_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"support.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_vanishing_floor_gate",
                "--count","8","--output",str(output),
            ],check=True,capture_output=True,text=True)
            data=json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"],"mathos_tectx_weil_vanishing_floor_and_prime_support/1")
            self.assertEqual(data["arithmetic_support"]["pair_count"],36)
            self.assertFalse(data["assurance"]["Riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
