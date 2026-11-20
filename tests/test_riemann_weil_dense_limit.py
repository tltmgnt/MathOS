"""Exact-rational adversarial tests for dense signed Weil trace-class limit."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_dense_limit import (
    WEIL_ENTRY_ABS_BOUND,
    dense_centers, weight, uniform_entry_majorant,
    trace_norm_tail_bound, finite_section_negative_floor, report,
)


class DenseWeilLimitTests(unittest.TestCase):
    def test_first_three_certified_frequencies_retained(self):
        self.assertEqual(dense_centers(3),
            (Fraction(0),Fraction(1,5),Fraction(1,2)))
        self.assertEqual(dense_centers(4)[-1],Fraction(1,4))
        self.assertNotIn(Fraction(21,5),dense_centers(32))

    def test_dyadic_centers_are_distinct_and_bounded(self):
        for n in (4,8,16,64,512,1024):
            centers=dense_centers(n)
            self.assertEqual(len(centers),len(set(centers)))
            self.assertTrue(all(Fraction(0)<=c<=Fraction(1,2)
                                for c in centers))
        centers=dense_centers(32)
        self.assertIn(Fraction(1,8),centers)
        self.assertIn(Fraction(3,8),centers)

    def test_weight_geometric_exact(self):
        for i in (0,1,2,10,100):
            self.assertEqual(weight(i),2**(i+1))

    def test_full_weil_entry_bound_includes_all_components(self):
        r=uniform_entry_majorant()
        self.assertEqual(r["final_entry_absolute_bound"],10000)
        self.assertEqual(r["component_sum_upper"],6676)
        self.assertLess(Fraction(r["exact_prime_tail_rational"]),1)
        self.assertEqual(set(["pole_upper","log_pi_upper",
            "archimedean_upper","prime_powers_through_256_upper",
            "all_remaining_prime_powers_upper"]).issubset(r),True)

    def test_trace_norm_tail_closed_form(self):
        for m in (0,1,2,3,4,8,16,32,64):
            q=Fraction(1,2**m)
            self.assertEqual(trace_norm_tail_bound(m),
                             WEIL_ENTRY_ABS_BOUND*(2*q-q*q))

    def test_tail_strict_decrease_and_quantitative_limits(self):
        for m in (0,1,2,3,8,16,32,64):
            self.assertGreater(trace_norm_tail_bound(m),
                               trace_norm_tail_bound(m+1))
        self.assertLess(trace_norm_tail_bound(32),Fraction(1,100000))
        self.assertLess(trace_norm_tail_bound(64),Fraction(1,10**14))

    def test_conditional_floor_and_negative_control(self):
        eps=trace_norm_tail_bound(10)
        self.assertEqual(finite_section_negative_floor(10,Fraction(1,100)),
                         -eps)
        self.assertEqual(finite_section_negative_floor(10,Fraction(-1,4)),
                         -Fraction(1,4)-eps)

    def test_bounds_reject_bad_indices(self):
        for value in (0.0,True,-1,4097):
            with self.subTest(value=value),self.assertRaises(ValueError):
                dense_centers(value)
        for value in (-1,4097,True):
            with self.subTest(value=value),self.assertRaises(ValueError):
                trace_norm_tail_bound(value)
        with self.assertRaises(ValueError):
            weight(-1)
        with self.assertRaises(ValueError):
            finite_section_negative_floor(10,0.1)

    def test_boundary_report_4096(self):
        r=report(4096)
        self.assertEqual(r["test_family"]["reported_dimension"],4096)
        self.assertFalse(any(r["assurance"].values()))

    def test_no_l2_to_weil_density_promotion(self):
        r=report(64)
        self.assertTrue(r["test_family"]["span_dense_in_even_real_L2"])
        self.assertFalse(r["test_family"]["density_proved_in_full_Weil_admissible_topology"])
        self.assertIsNone(r["fixed_self_adjoint_trace_class_operator"]["positive_semidefinite"])
        self.assertFalse(r["assurance"]["global_Weil_positivity"])

    def test_trace_class_not_RH_hilbert_polya(self):
        r=report(32)
        op=r["fixed_self_adjoint_trace_class_operator"]
        self.assertTrue(op["self_adjoint"])
        self.assertTrue(op["trace_class"])
        self.assertFalse(op["genuine_zeta_zero_operator"])
        self.assertFalse(r["assurance"]["Riemann_hypothesis_proved"])

    def test_cli_report_with_rational_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/"dense_limit.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_dense_limit",
                "--dimension","32","--output",str(output)
            ],capture_output=True,text=True,check=True)
            r=json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(r["schema"],"mathos_tectx_dense_weil_trace_class_limit/1")
            self.assertEqual(Fraction(r["fixed_self_adjoint_trace_class_operator"]["trace_norm_error_rational"]),
                             trace_norm_tail_bound(32))
            self.assertFalse(any(r["assurance"].values()))


if __name__=="__main__":
    unittest.main()
