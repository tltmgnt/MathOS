import unittest
from itertools import combinations, product
from copy import deepcopy
from mathos.research.pnp_overlap_deterministic import (
    conditions, forbidden_sums, construct, family, evidence, greedy_pairs)
from mathos.research.pnp_overlap_asymptotic import check_obstruction
from mathos.research.pnp_overlap_order import recover_fast
from mathos.research.pnp_overlap_certificates import _rank

class DeterministicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stats={}
        cls.ds,cls.rs,cls.cert=construct(24,8,2,stats=cls.stats)

    def test_family_conditions(self):
        for n in range(1,12):
            self.assertTrue(conditions(64*n,16*n,n))
        self.assertTrue(conditions(64,16,2))
        self.assertFalse(conditions(8,4,2))
        self.assertFalse(conditions(4,8,1))

    def test_grouped_sums_and_independence(self):
        self.assertEqual(set(forbidden_sums([(1,2),(4,8)],2)),{0,1,2,3,4,8,12})
        stats={"column_candidates":0,"sum_terms_checked":0}
        pairs=greedy_pairs(24,8,2,stats)
        self.assertEqual(pairs[:4],[(1,2),(4,8),(16,32),(64,128)])
        for a,b in combinations(pairs,2):
            self.assertEqual(_rank(8,a+b),4)

    def test_reproducibility_and_counts(self):
        stats={}
        self.assertEqual(construct(24,8,2,stats=stats),(self.ds,self.rs,self.cert))
        self.assertEqual(stats,self.stats)
        counts=stats["survivors"]
        self.assertEqual((counts[0],counts[-1],len(counts)),(256,0,25))
        self.assertTrue(all(4*b<=3*a for a,b in zip(counts,counts[1:])))
        self.assertTrue(check_obstruction(self.ds,self.rs,self.cert))

    def test_recovery_stalls_and_mutations(self):
        out,trace,empty=recover_fast(self.ds,self.rs,2)
        self.assertEqual((out,trace,empty),(self.rs,[],None))
        for change in (lambda c:c["directions"].pop(),
                       lambda c:c.update(closed_order=3,minimum_order_lower=4),
                       lambda c:c.update(anchor=1<<48)):
            bad=deepcopy(self.cert)
            change(bad)
            self.assertFalse(check_obstruction(self.ds,self.rs,bad))

    def test_budgets(self):
        with self.assertRaises(ValueError):
            family(2)
        with self.assertRaises(ValueError):
            construct(24,8,2,max_sum_terms=1)
        with self.assertRaises(ValueError):
            construct(4,8,1)

    def test_large_control(self):
        data=evidence()
        self.assertEqual([c["blocks"] for c in data["cases"]],[24,64])
        self.assertTrue(all(c["checker_accepted"] for c in data["cases"]))
        self.assertEqual(data["cases"][1]["projection_subsets"],2016)
