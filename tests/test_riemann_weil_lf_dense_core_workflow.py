"""Exact arithmetic support auditing and fail-closed LF-dense Weil routing."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.riemann_weil_lf_dense_core_workflow import (
    MAX_PREFIX, family, support_pair, positive_log_relation,
    includes_prime_log, exact_prime_power_inventory,
    finite_core_report,
)


class WeilLFDenseCoreWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=finite_core_report(8)

    def test_core_is_explicit_and_prefix_nested(self):
        a=family(5)
        b=family(12)
        self.assertEqual(a,b[:5])
        self.assertEqual(len({(v["n"],v["center"]) for v in b}),12)

    def test_enumeration_is_NOT_old_fixed_lattice(self):
        r=self.r
        self.assertEqual(r["core"]["priority"],"PRIMARY_RH_RELEVANT_TEST_FAMILY")
        self.assertEqual(r["comparison_lattice"]["span_LF_dense"],False)
        self.assertFalse(r["comparison_lattice"]["fixed_finite_lattice_PSD_implies_global_Weil_PSD"])
        self.assertEqual(r["comparison_lattice"]["permanent_open_gap"],["1/8","5/8"])

    def test_finite_core_supports_are_exact_rationals(self):
        b=family(8)
        for a in b:
            self.assertEqual(
                Fraction(a["support_right"])-Fraction(a["support_left"]),
                2*Fraction(a["half_support_width"]))
        for a in b:
            for c in b:
                lo,hi=support_pair(a,c)
                o,p=support_pair(c,a)
                self.assertEqual((lo,hi),(-p,-o))

    def test_small_symmetric_support_exact_prime_power_inventory(self):
        assert_inv=exact_prime_power_inventory(Fraction(-1),Fraction(1))
        self.assertEqual([(v["n"],v["von_mangoldt_base"]) for v in assert_inv],[(2,2)])
        wide=exact_prime_power_inventory(Fraction(-2),Fraction(2))
        self.assertEqual([(v["n"],v["von_mangoldt_base"]) for v in wide],
                         [(2,2),(3,3),(4,2),(5,5),(7,7)])

    def test_prime_log_certificates_do_not_use_float(self):
        self.assertEqual(positive_log_relation(2,Fraction(2,3)),1)
        self.assertEqual(positive_log_relation(2,Fraction(7,10)),-1)
        self.assertEqual(positive_log_relation(3,Fraction(1)),1)
        self.assertTrue(includes_prime_log(2,Fraction(-1),Fraction(1)))
        self.assertTrue(includes_prime_log(2,Fraction(-1),Fraction(-1,2)))
        self.assertFalse(includes_prime_log(3,Fraction(-1),Fraction(1)))

    def test_prime_inventory_reflects_support(self):
        a=exact_prime_power_inventory(Fraction(1,2),Fraction(1))
        b=exact_prime_power_inventory(Fraction(-1),-Fraction(1,2))
        self.assertEqual(a,b)
        self.assertEqual(a,[{"n":2,"von_mangoldt_base":2}])

    def test_upper_triangle_has_exact_pair_count(self):
        r=self.r
        self.assertEqual(r["arithmetic"]["complete_support_pair_count"],36)
        self.assertEqual(len(r["arithmetic"]["upper_triangle"]),36)
        self.assertTrue(all(e["all_arithmetic_prime_power_candidates_enumerated"]
                            for e in r["arithmetic"]["upper_triangle"]))

    def test_nesting_preserves_first_pairs(self):
        a=finite_core_report(5)
        b=self.r
        for item in a["arithmetic"]["upper_triangle"]:
            match=next(x for x in b["arithmetic"]["upper_triangle"]
                       if x["i"]==item["i"] and x["j"]==item["j"])
            self.assertEqual(item,match)

    def test_diagonal_support_is_center_independent(self):
        r=self.r
        for e in r["arithmetic"]["upper_triangle"]:
            if e["i"]==e["j"]:
                bump=family(8)[e["i"]]
                h=Fraction(bump["half_support_width"])
                self.assertEqual(e["support"],[str(-2*h),str(2*h)])
                self.assertEqual(e["prime_powers"],
                                 exact_prime_power_inventory(-2*h,2*h))
        # Unlike the old narrow lattice, the widest dense-core bumps
        # already encounter prime 2 even on the diagonal.
        self.assertEqual(next(e["prime_powers"] for e in r["arithmetic"]["upper_triangle"]
                              if e["i"]==0 and e["j"]==0),
                         [{"n":2,"von_mangoldt_base":2}])

    def test_density_is_analytic_not_computer_proved(self):
        a=self.r["core"]
        self.assertTrue(a["infinite_family_countable"])
        self.assertFalse(a["finite_prefix_LF_dense"])
        self.assertFalse(a["infinite_span_LF_dense_automatically_verified"])
        self.assertFalse(a["every_fixed_compact_test_eventually_in_finite_span"])

    def test_no_entry_or_RH_claim_is_promoted(self):
        a=self.r["arithmetic"]
        self.assertFalse(a["full_Gram_PSD_certified"])
        self.assertFalse(a["all_entries_have_full_Weil_interval"])
        self.assertFalse(a["all_index_nonnegative_lower_bound"])
        self.assertTrue(all(not e["actual_Weil_entry_enclosed"] for e in a["upper_triangle"]))
        self.assertFalse(any(self.r["assurance"].values()))

    def test_proof_decision_gate_retains_universal_obstacles(self):
        g=self.r["proof_decision_gate"]
        self.assertIn("G1_FINITE_TO_INFINITE",g["missing_proof_gaps"])
        self.assertIn("G2_SUPPORT_WINDOWS",g["missing_proof_gaps"])
        self.assertIn("G6_LOGICAL_COMPLETION",g["missing_proof_gaps"])
        self.assertFalse(g["global_proof_candidate_declared"])
        self.assertFalse(g["Riemann_hypothesis_proved"])

    def test_strict_invalid_input_rejection(self):
        for n in (0,-1,MAX_PREFIX+1,True,2.5):
            with self.subTest(n=n),self.assertRaises(ValueError):
                family(n)
        with self.assertRaises(ValueError):
            exact_prime_power_inventory(Fraction(1),Fraction(0))
        with self.assertRaises(ValueError):
            exact_prime_power_inventory(Fraction(-10),Fraction(10))
        with self.assertRaises(ValueError):
            positive_log_relation(1,Fraction(0))
        with self.assertRaises(ValueError):
            includes_prime_log(2,Fraction(1),Fraction(0))

    def test_cli_report_rational_and_no_RH(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"core.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.riemann_weil_lf_dense_core_workflow",
                "--prefix","8","--output",str(path)
            ],check=True,capture_output=True,text=True)
            r=json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(r["schema"],"mathos_tectx_weil_lf_dense_core_workflow/1")
            self.assertEqual(r["arithmetic"]["complete_support_pair_count"],36)
            self.assertFalse(r["assurance"]["Riemann_hypothesis_proved"])


if __name__=="__main__":
    unittest.main()
