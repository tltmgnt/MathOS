import unittest
from itertools import product
from unittest.mock import patch

from mathos.research import tga_proctor_blind_parity as b
from mathos.research import tga_proctor_xor_cnf as x
from mathos.research import tga_proctor_xor_bve as v


class BlindParityTests(unittest.TestCase):
    def test_controls(self):
        r=b.controls()
        self.assertEqual(r["random_cases"],1200)
        self.assertEqual(len(r["blind_odd"]),36)
        self.assertEqual(r["even_controls"],36)
        self.assertEqual(r["zero_budget_controls"],36)
        self.assertEqual(len(r["shared_selector_negative"]),12)
        self.assertFalse(r["oracle_auxiliary_ids"])

    def test_chain_projection(self):
        for depth in (1,2):
            n,cs=b.chain_split(3,((1,-2,3),),29,depth)
            for bits in product((False,True),repeat=3):
                expected=bits[0] or not bits[1] or bits[2]
                actual=any(all(any((bits+z)[abs(l)-1]==(l>0) for l in c) for c in cs)
                           for z in product((False,True),repeat=depth))
                self.assertEqual(expected,actual)

    def test_schedule_normalization(self):
        n=2**200
        cs=((1,n,n),(-n,2),(1,n),(n,-n,3),(4,),(4,))
        self.assertEqual(b.schedule(n,cs),(n,))
        out=b.solve(n,cs,pair_limit=1)
        self.assertEqual(out["scheduled"],1)
        self.assertEqual(out["eliminated"],1)
        self.assertIsNotNone(v.replay(n,cs,out["preprocessing"]))

    def test_relabel_and_replay_without_heuristic(self):
        cs=x.encode_parity((1,2,3),0)+x.encode_parity((1,2,3),1)
        n,hidden=b.chain_split(3,cs,11,2)
        sn,shuffled=b.relabel(n,hidden,71)
        self.assertTrue(all(abs(l)>=10**40 for c in shuffled for l in c))
        r=b.solve(sn,shuffled,pair_limit=16)
        self.assertEqual(r["status"],"UNSAT")
        self.assertEqual(r["scheduled"],16)
        with patch.object(b,"schedule",side_effect=AssertionError("no schedule")):
            self.assertTrue(b.verify(sn,shuffled,r))
            p=r["preprocessing"]
            self.assertFalse(b.verify(sn,shuffled,{**r,"preprocessing":{**p,"steps":p["steps"][:-1]}}))

    def test_shared_selector_is_equivalent_but_missed(self):
        cs=x.encode_parity((1,2,3),0)+x.encode_parity((1,2,3),1)
        n,hidden=b.shared_selector(3,cs)
        self.assertFalse(x._brute(hidden))
        # Both parities on one support together give every pattern,
        # so this particular fixture is directly detectable. Use the
        # cubic graph controls for the true negative.
        self.assertEqual(b.schedule(n,hidden),())
        for clause in ((1,2,3),(-1,2,-3)):
            _,h=b.shared_selector(3,(clause,))
            for bits in product((False,True),repeat=4):
                self.assertEqual(all(any(bits[abs(l)-1]==(l>0) for l in c) for c in h),
                                 any(bits[abs(l)-1]==(l>0) for l in clause))

    def test_empty_invalid_budget(self):
        self.assertTrue(b.verify(0,((),),b.solve(0,((),))))
        self.assertEqual(b.solve(0,())["status"],"UNKNOWN")
        with self.assertRaises(ValueError):
            b.solve(1,((1,),),pair_limit=-1)
        with self.assertRaises(ValueError):
            b.chain_split(3,((1,2,3),),11,3)


if __name__ == "__main__":
    unittest.main()
