"""Independent exact-arithmetic checks for a published comparison family (not BSD)."""
import json
from fractions import Fraction as Q
from pathlib import Path
import unittest

from mathos.research.bsd_rank3_infinite_tectx import (
    audit, exact_source_identities, model, evaluate, source_squareclass_dimensions,
    prime_parity, rational_squareclass, span_rank
)


class RankThreePublishedBenchmark06(unittest.TestCase):
    def test_source_polynomial_and_point_identity(self):
        report=exact_source_identities()
        self.assertTrue(report["model_polynomial_identity"])
        self.assertTrue(report["dual_isogeny_coefficients_identity"])
        self.assertTrue(report["source_discriminant_factorization_identity"])
        self.assertTrue(report["five_published_point_equations"])
        self.assertTrue(report["original_mathos_u2_has_no_rational_two_torsion"])
        self.assertEqual(report["source_model_discriminant_degree"],10)
        _, a, b, ap, bp, _, _=model()
        self.assertEqual(evaluate(a,0),Q(9725))
        self.assertEqual(evaluate(ap,0),Q(-19450))
        self.assertEqual(evaluate(bp,0),Q(9*3161**2))

    def test_exact_squareclasses(self):
        self.assertEqual(prime_parity(-560),{-1,5,7})
        self.assertEqual(rational_squareclass(Q(1,4)),set())
        self.assertEqual(rational_squareclass(Q(-12,5)),{-1,3,5})
        self.assertEqual(span_rank([{2,3},{3,5},{2,5}]),2)
        report=source_squareclass_dimensions(Q(3))
        self.assertEqual(report["independent_source_E_images"],3)
        self.assertEqual(report["independent_source_Eprime_images"],2)
        self.assertEqual(report["two_isogeny_descent_rank_lower_bound"],3)
        self.assertEqual(report["source_E_classes"],["-560","5","14"])
        self.assertEqual(report["source_Eprime_classes"],["83576889","36009"])
        self.assertIs(report["exact_rank_three_certified_by_this_program"],False)

    def test_bad_fibers_and_nontrivial_rank_drop_candidates(self):
        for t in (-11,-2,2,11,Q(-3161,280),Q(3161,280)):
            with self.assertRaises(ValueError):
                source_squareclass_dimensions(t)
        self.assertLess(
            source_squareclass_dimensions(Q(0))["two_isogeny_descent_rank_lower_bound"],3
        )

    def test_canonical_assurance_remains_unverified(self):
        result=audit(Q(3))
        self.assertTrue(result["source_proves_infinite_rank_three_for_ITS_FAMILY"])
        for k in (
            "source_family_is_original_MathOS_family",
            "source_theorem_independently_reproved_by_this_program",
            "infinite_parameter_set_enumerated_by_this_program",
            "MathOS_family_infinite_exact_rank_three_proved",
            "exact_analytic_rank_three_infinite_proved",
            "independent_novelty_review_completed",
            "canonical_TECT_runtime_executed",
            "BSD_proved",
        ):
            self.assertIs(result[k],False,k)
        self.assertEqual(result["canonical_assurance_state"],"UNVERIFIED")

    def test_tect_x_evidence_scope(self):
        path=Path(__file__).resolve().parents[1]/"docs/research/papers/BSD_RANK3_INFINITE_TECTX.v1.json"
        evidence=json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["canonical_assurance_state"],"UNVERIFIED")
        self.assertEqual(len(evidence["gates"]),5)
        self.assertEqual([g["gate"] for g in evidence["gates"]],[1,2,3,4,5])
        self.assertEqual([g["status"] for g in evidence["gates"]],
             ["SOURCE_CONFIRMED","EXACT_IDENTITY","BOUNDED_LOWER",
              "EXTERNAL_THEOREM_ONLY","BLOCKED"])
        for k in ("original_family_exact_rank_infinite_set_proved","new_ranks_certified_by_code",
                  "exact_analytic_rank_infinite_set_proved","independent_novelty_established","bsd_proved"):
            self.assertIs(evidence[k],False,k)
        self.assertIs(evidence["published_source_family_exact_rank_infinite_set_proved_by_source"],True)


if __name__=="__main__":
    unittest.main()
