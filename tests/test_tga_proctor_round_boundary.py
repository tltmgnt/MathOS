import unittest
from unittest.mock import patch
from itertools import product

from mathos.research import tga_proctor_round_boundary as r
from mathos.research import tga_proctor_mixed_routing as m
from mathos.research import tga_proctor_xor_cnf as x
from mathos.research.tga_proctor_hybrid_adversary import pigeonhole


class RoundBoundaryTests(unittest.TestCase):
    def test_controls(self):
        out=r.controls()
        self.assertEqual(sum(out["outcomes"].values()),3600)
        self.assertEqual(len(out["fixtures"]),16)
        self.assertEqual(out["equal_controls"],4)

    def test_exact_guard_frontiers(self):
        n,cs=r.guarded(3,((1,2,3),),3)
        # A full frontier contains each choice of remaining guard subset
        # and each polarity pattern on that subset.
        expected=(12,6,1)
        for count in expected:
            d=m.derive(n,cs)
            self.assertEqual(len(d["clauses"]),count)
            cs=d["clauses"]
        self.assertEqual(cs,((1,2,3),))

    def test_replay_without_discovery(self):
        n,cs=r.guarded(*pigeonhole(4),2)
        out=r.solve(n,cs,2)
        self.assertEqual(out["status"],"UNSAT")
        batches,tag,p=out["certificate"]
        with patch.object(m,"derive",side_effect=AssertionError("no derivation")), \
             patch.object(m,"_infer",side_effect=AssertionError("no inference")):
            self.assertTrue(r.verify(n,cs,out))
            a,b,v=batches[0][0]
            corrupt=(((a,b,0),)+batches[0][1:],)+batches[1:]
            for bad in (corrupt,batches[:-1],tuple(reversed(batches)),((),)+batches):
                self.assertFalse(r.verify(n,cs,{**out,"certificate":(bad,tag,p)}))
            self.assertFalse(r.verify(n,cs,{**out,"certificate":(batches,"OTHER",p)}))

    def test_budget_prefix_and_validation(self):
        n,cs=r.guarded(*pigeonhole(4),2)
        for rounds,sig,steps in ((0,1000,1000),(2,0,1000),(2,1000,0),(2,5,100),(2,1000,1)):
            out=r.solve(n,cs,rounds,sig,steps)
            self.assertEqual(out["status"],"UNKNOWN")
            self.assertLessEqual(out["rounds"],rounds)
            self.assertLessEqual(out["signature_count"],sig)
            self.assertLessEqual(out["resolution_steps"],steps)
            self.assertFalse(r.verify(n,cs,out))
        for kw in ({"round_limit":True},{"signature_limit":-1},{"step_limit":-1}):
            with self.assertRaises(ValueError):
                r.solve(0,(),**kw)

    def test_pointwise_equivalence(self):
        cs=((1,-2),(2,))
        n,guarded=r.guarded(2,cs,2)
        for bits in product((False,True),repeat=n):
            def holds(rows):
                return all(any(bits[abs(l)-1]==(l>0) for l in c) for c in rows)
            self.assertEqual(holds(cs),holds(guarded))


if __name__=="__main__":
    unittest.main()
