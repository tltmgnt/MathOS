"""Adversarial checks for infinite-span Weil positivity inference boundary."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_prime_tail import per_entry_prime_tail_bound
from mathos.research.riemann_weil_span_stability import (
    THREE_SPAN_EUCLIDEAN_GAP, THREE_SPAN_L2_GAP,
    THREE_SPAN_L2_GAP, L2_THREE_SPAN_NORM_UPPER,
    adjacent_gap, clustered_centers,
    conditional_completion_statement, dimension_free_prime_tail,
    report,
)


class GrowingSpanWeilTests(unittest.TestCase):
    def test_uniform_prime_tail_one_basis(self):
        delta=per_entry_prime_tail_bound()
        self.assertEqual(
            dimension_free_prime_tail((Fraction(0),),(Fraction(3,2),)),
            delta*Fraction(9,4))

    def test_many_dimensions_same_l1_mass(self):
        delta=per_entry_prime_tail_bound()
        for n in [2,3,7,11,100,500]:
            c=tuple(Fraction(k,2*n) for k in range(n))
            v=tuple(Fraction(1,n) for _ in range(n))
            self.assertEqual(dimension_free_prime_tail(c,v),delta)

    def test_equal_and_opposing_coefficients(self):
        c=(Fraction(0),Fraction(0))
        v=(Fraction(1),Fraction(-1))
        # Deliberately an upper bound, not the exact zero tail of q_0-q_0.
        self.assertEqual(dimension_free_prime_tail(c,v),
                         4*per_entry_prime_tail_bound())

    def test_invalid_centers_and_coefficients(self):
        for centers,coeffs in [
            ((),()),((Fraction(-1),),(Fraction(1),)),
            ((Fraction(3,4),),(Fraction(1),)),
            ((Fraction(0),),(1,)),
            ((Fraction(0),),(Fraction(1),Fraction(2))),
            ((Fraction(0),),None),
            (tuple(Fraction(0) for _ in range(501)),tuple(Fraction(1) for _ in range(501))),
        ]:
            with self.subTest(centers=centers), self.assertRaises(ValueError):
                dimension_free_prime_tail(centers,coeffs)

    def test_clustered_distinct_centers(self):
        centers=clustered_centers(200)
        self.assertEqual(len(centers),len(set(centers)))
        self.assertEqual(centers[0],Fraction(1,2))
        self.assertEqual(centers[1],Fraction(1,3))
        self.assertTrue(all(Fraction(0)<x<=Fraction(1,2) for x in centers))

    def test_gaps_tend_to_zero_analytically(self):
        for j in [0,1,2,10,100,1000]:
            self.assertEqual(adjacent_gap(j),
                             Fraction(1,j+2)-Fraction(1,j+3))
        self.assertLess(adjacent_gap(10000),Fraction(1,10**8))

    def test_no_uniform_euclidean_coercivity(self):
        r=report()
        no_go=r["no_go_for_uniform_coefficient_gap"]
        self.assertTrue(no_go["absence_of_uniform_kappa_proved"])
        self.assertFalse(no_go["rules_out_global_Weil_positivity"])
        self.assertIn("Gram [[w,w],[w,w]]",no_go["exact_duplicate_example"])
        self.assertFalse(no_go["rules_out_L2_normalized_or_Sobolev_normalized_coercivity"])

    def test_three_dimensional_relative_bound_exact(self):
        self.assertGreater(
            THREE_SPAN_EUCLIDEAN_GAP-THREE_SPAN_L2_GAP*L2_THREE_SPAN_NORM_UPPER,
            0)
        self.assertEqual(
            THREE_SPAN_EUCLIDEAN_GAP-THREE_SPAN_L2_GAP*L2_THREE_SPAN_NORM_UPPER,
            Fraction(1,10_000_000))
        r=report()
        self.assertTrue(
            r["previous_three_dimensional_relative_bound"]["basis_invariant_within_fixed_three_span"])
        self.assertFalse(r["previous_three_dimensional_relative_bound"]["all_dimensions"])

    def test_conditional_hilbert_completion_is_not_claimed(self):
        c=conditional_completion_statement()
        self.assertFalse(c["hypothesis_proved"])
        self.assertFalse(c["completion_constructed_unconditionally"])

    def test_no_RH_proof_claim(self):
        r=report()
        self.assertEqual(
            r["status"],
            "DIMENSION_FREE_L1_TAIL_AND_NO_UNIFORM_EUCLIDEAN_COERCIVITY")
        self.assertFalse(any(r["assurance"].values()))
        self.assertTrue(r["dimension_free_prime_tail"]["dimension_independent_constant"])

    def test_cli_report(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"stability.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_span_stability",
                "--output",str(p),
            ],check=True,text=True,capture_output=True)
            r=json.loads(p.read_text(encoding="utf-8"))
            self.assertFalse(r["assurance"]["riemann_hypothesis_proved"])
            self.assertEqual(
                Fraction(r["dimension_free_prime_tail"]["bound"]),
                per_entry_prime_tail_bound()*36)

    def test_cli_reject_invalid_dimension(self):
        x=subprocess.run([
            sys.executable,"-m","mathos.research.riemann_weil_span_stability",
            "--centers","0,1/5","--coefficients","1",
        ],capture_output=True,text=True)
        self.assertNotEqual(x.returncode,0)
        self.assertIn("coefficient",x.stderr)


if __name__=="__main__":
    unittest.main()
