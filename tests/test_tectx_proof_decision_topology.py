"""Adversarial tests: TECT-X decision trees cannot promote finite Weil work to RH."""
import json
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.research.tectx_proof_decision_topology import (
    DECISION_FAMILIES, Evidence, ProofEvidence, GAPS,
    prefix_distance, norm_window_assessment, check_vanishing_bridge,
    exact_nonnegative, evaluate, sample_report,
)


class TECTXDecisionTopologyTests(unittest.TestCase):
    def test_ten_overlapping_families_not_false_exhaustive_ontology(self):
        r=sample_report()
        self.assertEqual(len(DECISION_FAMILIES),10)
        self.assertEqual(r["decision_ontology"]["families"],list(DECISION_FAMILIES))
        self.assertTrue(r["decision_ontology"]["ten_families_are_overlapping_attributes"])
        self.assertFalse(r["decision_ontology"]["claim_of_exhaustive_ontology"])

    def test_prefix_ultrametric(self):
        a=("a","b","c")
        b=("a","b","d")
        c=("a","e")
        self.assertEqual(prefix_distance(a,a),0)
        self.assertEqual(prefix_distance(a,b),Fraction(1,4))
        self.assertEqual(prefix_distance(a,c),Fraction(1,2))
        self.assertLessEqual(prefix_distance(a,c),max(prefix_distance(a,b),prefix_distance(b,c)))
        self.assertEqual(prefix_distance(a,b),prefix_distance(b,a))

    def test_evidence_levels_have_strict_order(self):
        self.assertLess(Evidence.EXPERIMENTAL,Evidence.INTERVAL_VERIFIED)
        self.assertLess(Evidence.INTERVAL_VERIFIED,Evidence.FINITE_THEOREM)
        self.assertLess(Evidence.FINITE_THEOREM,Evidence.UNIFORM_THEOREM)
        self.assertLess(Evidence.UNIFORM_THEOREM,Evidence.GLOBAL_WEIL_THEOREM)

    def test_finite_compact_certificates_not_rh(self):
        r=sample_report()
        self.assertEqual(r["highest_evidence_level"],"FINITE_THEOREM")
        self.assertTrue(r["finite_evidence_only"])
        self.assertFalse(r["Riemann_hypothesis_proved"])
        self.assertFalse(r["global_proof_candidate_declared"])
        for gap in ("G1_FINITE_TO_INFINITE","G2_SUPPORT_WINDOWS","G4_SPECTRAL_STABILITY","G6_LOGICAL_COMPLETION"):
            self.assertIn(gap,r["missing_proof_gaps"])
        self.assertNotIn("G3_TOPOLOGY",r["missing_proof_gaps"])

    def test_norms_change_while_epsilon_decreases(self):
        r=check_vanishing_bridge([("1/4","4"),("1/16","8"),("1/64","16")])
        self.assertEqual([Fraction(v["error_times_norm_squared"]) for v in r["windows"]],
                         [Fraction(4),Fraction(4),Fraction(4)])
        self.assertTrue(r["sampled_error_products_decreasing"])
        self.assertFalse(r["finite_sample_proves_limit"])
        self.assertFalse(r["mathematically_verified_limit"])
        self.assertEqual(r["status"],"OPEN_TOPOLOGICAL_LIMIT_PROOF")

    def test_finite_samples_even_with_zero_error_are_not_limit_proof(self):
        r=check_vanishing_bridge([("0","999999"),("0","999999")])
        self.assertFalse(r["mathematically_verified_limit"])
        self.assertFalse(r["finite_sample_proves_limit"])

    def test_external_limit_proof_flags_only_request_review(self):
        r=check_vanishing_bridge([("1/100","1")],
            has_universal_rate_proof=True,fixed_test_eventually_admissible=True,
            reference_norm_compatibility_proved=True)
        self.assertTrue(r["limit_claim_has_external_proof_obligations_declared"])
        self.assertFalse(r["mathematically_verified_limit"])
        self.assertEqual(r["status"],"candidate_requires_independent_mathematical_review")

    def test_reject_float_negative_and_nonfinite_rational_bounds(self):
        for value in ("-1/3","0/0","nan","inf",0.25,True):
            with self.subTest(value=value),self.assertRaises(ValueError):
                exact_nonnegative(value)
        with self.assertRaises(ValueError):
            check_vanishing_bridge([])
        with self.assertRaises(ValueError):
            norm_window_assessment("-1","1")

    def test_fabricated_global_claim_fails_strict_domain_topology(self):
        with self.assertRaises(ValueError):
            evaluate([ProofEvidence("fake",Evidence.GLOBAL_WEIL_THEOREM,
                "fixed_4D_compact","all_admissible_tests","unreviewed claim",
                universal_positivity_proved=True)])

    def test_all_true_global_claim_is_only_unverified_candidate(self):
        e=ProofEvidence("alleged",Evidence.GLOBAL_WEIL_THEOREM,
            "Cc_infinity_log","all_admissible_tests","external mathematical manuscript",
            arithmetic_normalization_audited=True,LF_dense_core_proved=True,
            Weil_continuity_proved=True,universal_positivity_proved=True,
            all_compact_support_windows_covered=True,seminorm_limit_bridge_proved=True)
        r=evaluate([e])
        self.assertTrue(r["global_proof_candidate_declared"])
        self.assertEqual(r["scientific_status"],"CANDIDATE_REQUIRES_INDEPENDENT_MATH_REVIEW")
        self.assertFalse(r["global_proof_externally_verified"])
        self.assertFalse(r["Riemann_hypothesis_proved"])

    def test_uniform_claim_requires_universal_quantifier(self):
        with self.assertRaises(ValueError):
            evaluate([ProofEvidence("bad",Evidence.UNIFORM_THEOREM,
                "Cc_infinity_log","m_is_4","a numerical report")])

    def test_duplicate_evidence_ids_are_rejected(self):
        e=ProofEvidence("id",Evidence.FINITE_THEOREM,"finite_2D","finite","source")
        with self.assertRaises(ValueError):
            evaluate([e,e])
        with self.assertRaises(ValueError):
            evaluate([])

    def test_structured_gaps_include_six_proof_obligations(self):
        self.assertEqual(len(GAPS),6)
        r=evaluate([ProofEvidence("finite",Evidence.INTERVAL_VERIFIED,
                                    "compact_2D","finite","report")])
        self.assertEqual(set(r["missing_proof_gaps"]),set(GAPS))
        self.assertFalse(r["Riemann_hypothesis_proved"])

    def test_no_unjustified_finite_to_infinite_evidence_promotion(self):
        finite=[ProofEvidence(f"finite_{j}",Evidence.FINITE_THEOREM,
                    f"fixed_{j}D","specified_finite_span",f"report {j}")
                for j in range(1,200)]
        r=evaluate(finite)
        self.assertEqual(r["highest_evidence_level"],"FINITE_THEOREM")
        self.assertFalse(r["global_proof_candidate_declared"])
        self.assertIn("G1_FINITE_TO_INFINITE",r["missing_proof_gaps"])

    def test_cli_json_report_and_assurance_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"decision_topology.json"
            subprocess.run([
                sys.executable,"-m","mathos.research.tectx_proof_decision_topology",
                "--output",str(output)
            ],check=True,capture_output=True,text=True)
            result=json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["schema"],"mathos_tectx_proof_decision_topology/1")
            self.assertFalse(result["Riemann_hypothesis_proved"])
            self.assertFalse(result["governance"]["finite_certificates_promoted_to_global"])
            self.assertFalse(result["window_demo"]["finite_sample_proves_limit"])


if __name__=="__main__":
    unittest.main()
