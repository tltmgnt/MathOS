import unittest
from unittest.mock import patch

from mathos.research import tga_proctor_combined_boundary as c
from mathos.research import tga_proctor_signed_hall as s
from mathos.research import tga_proctor_capacity as cap
from mathos.research import tga_proctor_xor_cnf as x
from mathos.research import tga_proctor_blind_parity as b


class CombinedBoundaryTests(unittest.TestCase):
    def test_controls(self):
        r=c.controls()
        self.assertEqual(sum(r["outcomes"].values()),1600)
        self.assertEqual(len(r["fixtures"]),12)
        self.assertEqual(r["equal_controls"],6)
        self.assertFalse(r["combined_proof_system_lower_bound"])

    def test_shortcuts_and_zero_budget(self):
        n,cs=c.guarded_php(4)
        n,cs=b.relabel(n,cs,29)
        r=cap.solve_hybrid(n,cs,0,0,allow_wide=True)
        self.assertEqual(r["status"],"UNKNOWN")
        self.assertFalse(cap.verify_hybrid(n,cs,r,allow_wide=True))
        self.assertTrue(c.verify_paired_hall(n,cs,c.solve_paired_hall(n,cs)))

    def test_replay_and_tamper(self):
        n,cs=c.guarded_php(4)
        r=c.solve_paired_hall(n,cs)
        steps,h=r["certificate"]
        a,z,p=steps[0]
        with patch.object(c,"paired_resolvents",side_effect=AssertionError("no discovery")), \
             patch.object(s,"solve",side_effect=AssertionError("no matching")):
            self.assertTrue(c.verify_paired_hall(n,cs,r))
            for bad in (
                ((a,a,p),)+steps[1:],
                ((a,z,0),)+steps[1:],
                ((a,len(cs),p),)+steps[1:],
                ((z,a,p),)+steps[1:],
                ((True,z,p),)+steps[1:],
                (),
            ):
                self.assertFalse(c.verify_paired_hall(n,cs,{**r,"certificate":(bad,h)}))
            self.assertFalse(c.verify_paired_hall(n,cs,{**r,"certificate":(steps,{**h,"status":"UNKNOWN"})}))

    def test_sparse_normalization(self):
        n=2**200
        cs=((1,n,n),(-n,1),(1,-1),(2,3),(-2,4))
        derived,steps,count=c.paired_resolvents(n,cs)
        self.assertEqual(derived,((1,),))
        self.assertEqual(c.replay(n,cs,steps),derived)
        self.assertLessEqual(count,sum(map(len,cs)))
        self.assertIsNone(c.replay(n,cs,((3,4,2),)))

    def test_semantic_small_guard(self):
        n,cs=c.guarded_php(2,2)
        self.assertTrue(x._brute(cs))
        self.assertEqual(c.solve_paired_hall(n,cs)["status"],"UNKNOWN")
        n,cs=c.guarded_php(2)
        self.assertFalse(x._brute(cs))
        self.assertTrue(c.verify_paired_hall(n,cs,c.solve_paired_hall(n,cs)))


if __name__=="__main__":
    unittest.main()
