"""MathOS BSD milestone 05: finite rational arithmetic and epistemic guard.

These tests do NOT independently reprove BBD's rank theorem or establish BSD.
"""
import json
from pathlib import Path
import unittest

from mathos.research.bsd_rank_exact_05 import (
    audit, exact_polynomial_certificates, gcd_modp, divmod_modp,
)


class BSDEffectiveGenericRank05Tests(unittest.TestCase):
    def test_rank_formula_arithmetic(self):
        result=exact_polynomial_certificates()
        self.assertTrue(result["exact_polynomial_factorization"])
        self.assertTrue(result["resultant_factors_verified"])
        self.assertTrue(result["irreducible_quartic_via_mod3"])
        self.assertTrue(result["discriminant_squarefree_via_mod3"])
        self.assertEqual(result["BBD_Theorem_1_degree_A_2_rank"],3)
        self.assertEqual(result["Shioda_Tate_geometric_rank"],5)
        terms=result["rank_formula_terms"]
        self.assertEqual(terms["Omega_M_gcdABstar_C"],4)
        self.assertEqual(terms["Omega_M_Fstar_A"],7)
        self.assertEqual(terms["omega_F"],4)
        self.assertEqual(terms["Upsilon_F_A"],0)
        self.assertEqual(terms["two_degree_gcdABstar"],4)

    def test_mod3_factorization_adversarial(self):
        q=(1,0,23,0,128)
        for factor in ((0,1),(1,1),(2,1),(0,0,1),(1,0,1),(2,2,1)):
            self.assertNotEqual(divmod_modp(q,factor,3)[1],(0,))
        D=(37,60,94,78,65,34,16,4,1)
        dD=tuple(i*D[i] for i in range(1,len(D)))
        self.assertEqual(gcd_modp(D,dD,3),(1,))

    def test_no_claim_promotion(self):
        results=audit()
        self.assertEqual(results["BBD_Theorem_1_degree_A_2_rank"],3)
        for key in (
            "published_theorem_reproved_by_script",
            "outside_review_authenticated",
            "universal_exact_specialization_rank_3_proved",
            "effectively_specified_infinite_exact_rank_3_fibers_proved",
            "infinite_family_exact_analytic_rank_3_proved",
            "independent_novelty_established",
            "canonical_TECT_assurance_promoted",
            "BSD_proved",
        ):
            self.assertIs(results[key],False,key)

    def test_tect5_registry(self):
        root=Path(__file__).resolve().parents[1]
        path=root/"docs/research/papers/BSD_RANK_EXACT_MILESTONE_05_TECT5.json"
        record=json.loads(path.read_text(encoding="utf8"))
        self.assertEqual(record["schema_version"],"mathos-tect5-review-v1")
        self.assertEqual(record["TECT_state"],"UNVERIFIED")
        self.assertIs(record["actual_canonical_runtime_executed"],False)
        self.assertEqual(record["count"],5)
        self.assertEqual(len(record["gates"]),5)
        self.assertEqual([g["number"] for g in record["gates"]],list(range(1,6)))
        self.assertEqual([g["outcome"] for g in record["gates"]],
                         ["SCOPED_PASS"]*4+["UNCERTAIN"])
        self.assertIs(record["independently_reproduced_by_separate_mathematician"],False)
        self.assertTrue(all(v is False for v in record["explicit_nonclaims"].values()))


if __name__=="__main__":
    unittest.main()
