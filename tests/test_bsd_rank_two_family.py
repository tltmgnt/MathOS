"""Structural scope and Z[T] audit only. Does not certify the rank theorem."""
import unittest
from mathos.research.bsd_rank_two_family import audit, invariants, evalp
class BSDRankTwoFamilyTests(unittest.TestCase):
    def test_exact_symbolic_invariants_and_nonpromotion(self):
        c4,d=invariants()
        self.assertEqual(c4,(112,80,16))
        self.assertEqual(d,(389,696,472,144,16))
        self.assertEqual(evalp(d,0),389)
        self.assertEqual(evalp(d,2),5077)
        report=audit()
        self.assertEqual(report["result"],"EXACT_POLYNOMIAL_AUDIT_PASSED")
        for key in ("BSD_proved","novelty_established",
                    "analytic_rank_for_family_proved",
                    "rank_source_independently_verified_by_script",
                    "specialization_theorem_proved_by_script"):
            self.assertIs(report[key],False)
if __name__=="__main__": unittest.main()
