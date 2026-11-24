import unittest
from unittest.mock import patch

from mathos.research import tga_proctor_hall as h
from mathos.research import tga_proctor_hybrid_adversary as a
from mathos.research import tga_proctor_xor_cnf as x


class HallTests(unittest.TestCase):
    def test_controls(self):
        r=h.controls()
        self.assertEqual(sum(r["random_outcomes"].values()),1500)
        self.assertEqual(sum(r["matching_outcomes"].values()),600)
        self.assertEqual(len(r["php"]),9)

    def test_proper_subset_deficiency(self):
        n,cs=h.matching_cnf(((0,1),(0,1),(0,1),(2,3,4)))
        r=h.solve(n,cs)
        self.assertEqual(r["status"],"UNSAT")
        cert=r["certificate"]
        self.assertEqual(len(cert["demands"]),3)
        self.assertEqual(len(cert["groups"]),2)
        self.assertTrue(h.verify(n,cs,r))

    def test_replay_tamper(self):
        n,cs=a.pigeonhole(3)
        r=h.solve(n,cs)
        c=r["certificate"]
        ds,gs=c["demands"],c["groups"]
        vs,refs=gs[0]
        with patch.object(h,"_discover",side_effect=AssertionError("no discovery")), \
             patch.object(h,"_deficiency",side_effect=AssertionError("no matching")):
            self.assertTrue(h.verify(n,cs,r))
            mutations=(
                {**c,"demands":ds[:-1]},
                {**c,"demands":ds+(ds[0],)},
                {**c,"demands":ds[:-1]+(len(cs),)},
                {**c,"groups":gs[:-1]},
                {**c,"groups":((vs,refs[:-1]),)+gs[1:]},
                {**c,"groups":((vs,(ds[0],)+refs[1:]),)+gs[1:]},
                {**c,"groups":((vs+(gs[1][0][0],),refs),)+gs[1:]},
            )
            for bad in mutations:
                self.assertFalse(h.verify(n,cs,{**r,"certificate":bad}))

    def test_nonclique_overlap_and_polarity_negative(self):
        # Three true units with a noncomplete conflict component: missed.
        cs=((1,),(2,),(3,),(-1,-2),(-2,-3))
        self.assertFalse(x._brute(cs))
        self.assertEqual(h.solve(3,cs)["status"],"UNKNOWN")
        # Shared variable can satisfy both demands; a naive count is unsound.
        cs=((1,2),(1,3),(-1,-2),(-1,-3),(-2,-3))
        self.assertTrue(x._brute(cs))
        self.assertEqual(h.solve(3,cs)["status"],"UNKNOWN")
        n,cs=a.pigeonhole(3)
        complemented=tuple(tuple(-l for l in c) for c in cs)
        self.assertEqual(h.solve(n,complemented)["status"],"UNKNOWN")

    def test_hybrid_routes_and_validation(self):
        n,cs=a.pigeonhole(4)
        r=h.solve_hybrid(n,cs,0,0)
        self.assertEqual((r["route"],r["search_nodes"],r["pair_tests"]),("HALL",0,0))
        self.assertTrue(h.verify_hybrid(n,cs,r))
        self.assertFalse(h.verify_hybrid(n,cs,{**r,"status":"SAT"}))
        self.assertFalse(h.verify_hybrid(n,cs,{**r,"route":"DIRECT_XOR"}))
        parity=x.encode_parity((1,2,3),0)+x.encode_parity((1,2,3),1)
        out=h.solve_hybrid(3,parity,0,0)
        self.assertEqual(out["route"],"DIRECT_XOR")
        self.assertTrue(h.verify_hybrid(3,parity,out))
        out=h.solve_hybrid(1,((1,),),0,10)
        self.assertEqual(out["status"],"SAT")
        self.assertTrue(h.verify_hybrid(1,((1,),),out))
        self.assertFalse(h.verify_hybrid(0,(),h.solve_hybrid(0,(),0,0)))
        for p,k in ((-1,0),(0,-1),(True,1)):
            with self.assertRaises(ValueError):
                h.solve_hybrid(n,cs,p,k)

    def test_duplicates_sparse_empty(self):
        n=2**200
        cs=((n,n),(7,),(7,),(-n,-7,-7),(3,-3))
        out=h.solve(n,cs)
        self.assertEqual(out["status"],"UNSAT")
        self.assertTrue(h.verify(n,cs,out))
        self.assertEqual(h.solve(0,((),))["status"],"UNKNOWN")
        with self.assertRaises(ValueError):
            h.solve(1,((True,),))


if __name__ == "__main__":
    unittest.main()
