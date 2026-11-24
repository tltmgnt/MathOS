import unittest
from unittest.mock import patch
from itertools import product

from mathos.research import tga_proctor_capacity as c
from mathos.research import tga_proctor_hall as h
from mathos.research import tga_proctor_signed_hall as s
from mathos.research import tga_proctor_xor_cnf as x


class CapacityTests(unittest.TestCase):
    def test_controls(self):
        r=c.controls()
        self.assertEqual(r["random_cases"],1600)
        self.assertEqual(sum(r["outcomes"].values()),3200)
        self.assertEqual(len(r["fixtures"]),26)
        self.assertEqual(r["equal_controls"],26)

    def test_capacity_two_truth_table(self):
        n,cs=c.php(2,2)
        self.assertFalse(x._brute(cs))
        r=c.solve(n,cs,2)
        self.assertTrue(c.verify(n,cs,r))
        self.assertEqual(sum(g[1] for g in r["certificate"]["groups"]),4)
        n,cs=c.php(2,2,4)
        self.assertTrue(x._brute(cs))
        self.assertEqual(c.solve(n,cs,2)["status"],"UNKNOWN")

    def test_tamper_without_discovery(self):
        n,cs=c.php(2,2)
        r=c.solve(n,cs,2)
        cert=r["certificate"]
        ds,gs=cert["demands"],cert["groups"]
        vs,cap,refs=gs[0]
        with patch.object(c,"_discover",side_effect=AssertionError("no discovery")), \
             patch.object(h,"_deficiency",side_effect=AssertionError("no matching")):
            self.assertTrue(c.verify(n,cs,r))
            for bad in (
                {**cert,"demands":ds[:-1]},
                {**cert,"demands":ds+(ds[0],)},
                {**cert,"groups":gs[:-1]},
                {**cert,"groups":((vs,1,refs),)+gs[1:]},
                {**cert,"groups":((vs,cap,refs[:-1]),)+gs[1:]},
                {**cert,"groups":((vs,cap,(ds[0],)+refs[1:]),)+gs[1:]},
                {**cert,"groups":(((-vs[0],)+vs[1:],cap,refs),)+gs[1:]},
            ):
                self.assertFalse(c.verify(n,cs,{**r,"certificate":bad}))

    def test_mixed_capacity_certificate(self):
        # Four singleton demands; one capacity-two group plus one singleton.
        cs=((1,),(2,),(3,),(4,),(-1,-2,-3))
        r=dict(status="UNSAT",certificate=dict(demands=(0,1,2,3),
                    groups=(((1,2,3),2,(4,)),((4,),1,()))))
        self.assertTrue(c.verify(4,cs,r))
        self.assertFalse(x._brute(cs))

    def test_missing_edge_and_tie(self):
        n,cs=c.php(2,2)
        # Removing one required triple destroys one complete component.
        self.assertEqual(c.solve(n,cs[:-1],2)["status"],"UNKNOWN")
        self.assertEqual(c.solve(2,((1,2),(-1,-2)),1)["status"],"UNKNOWN")

    def test_hybrid_fallback_and_validation(self):
        r=c.solve_hybrid(1,((1,),),0,10)
        self.assertEqual(r["status"],"SAT")
        self.assertTrue(c.verify_hybrid(1,((1,),),r))
        self.assertFalse(c.verify_hybrid(0,(),c.solve_hybrid(0,(),0,0)))
        for k in (0,3,True):
            with self.assertRaises(ValueError):
                c.solve(0,(),k)
        with self.assertRaises(ValueError):
            c.solve_hybrid(0,(),-1,0)


if __name__=="__main__":
    unittest.main()
