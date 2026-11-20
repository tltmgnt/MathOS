"""Milestone 04: exact arithmetic and non-promotion tests, not a BSD proof."""
import unittest
from mathos.research.bsd_prime_discriminant_04 import (
    is_prime_trial_division, elliptic_invariants, root_number_certificate, audit,
)


class BSDPrimeDiscriminantMilestone04Test(unittest.TestCase):
    def test_exact_primality(self):
        for p in (37, 389, 5077, 43669, 11700677):
            self.assertTrue(is_prime_trial_division(p))
        for n in (0, 1, 25, 45, 5077*7, 43669*3):
            self.assertFalse(is_prime_trial_division(n))

    def test_rank_three_external_benchmarks(self):
        for u,p,c4,c6,label in (
            (2,5077,336,-5400,"5077.a1"),
            (-3,5077,336,-5400,"5077.a1"),
            (3,43669,912,-26136,"43669.a1"),
            (-4,43669,912,-26136,"43669.a1"),
        ):
            rec=root_number_certificate(u)
            self.assertEqual(rec["discriminant"],p)
            self.assertEqual(rec["c4"],c4)
            self.assertEqual(rec["c6"],c6)
            self.assertEqual(rec["root_number"],-1)
            self.assertEqual(rec["Euler_criterion_residue"],p-1)
            self.assertEqual(rec["source_rank_record"]["label"],label)
            self.assertIs(rec["independent_rank_certificate_produced"],False)

    def test_low_rank_sanity_examples(self):
        for u in (1,-2):
            rec=root_number_certificate(u)
            self.assertEqual(rec["root_number"],1)
            self.assertEqual(rec["source_rank_record"]["rank"],2)
        for u in (0,-1):
            rec=root_number_certificate(u)
            self.assertEqual(rec["root_number"],-1)
            self.assertEqual(rec["source_rank_record"]["rank"],1)

    def test_involution_exact(self):
        for u in range(-8,8):
            a=elliptic_invariants(u)
            b=elliptic_invariants(-u-1)
            self.assertEqual(a["delta"],b["delta"])
            self.assertEqual(a["c6"],b["c6"])

    def test_no_promoted_proof_claims(self):
        result=audit()
        self.assertEqual(result["prime_discriminant_case_count"],10)
        for k in (
            "non_prime_discriminant_root_numbers_computed",
            "all_fibers_analytic_rank_three_proved",
            "infinite_prime_discriminant_subfamily_proved",
            "infinite_exact_rank_equality_proved",
            "mathematical_novelty_established", "BSD_proved",
        ):
            self.assertIs(result[k],False)
        with self.assertRaises(ValueError):
            audit(-20,20)


if __name__=="__main__":
    unittest.main()
