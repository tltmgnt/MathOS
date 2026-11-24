import unittest
from unittest.mock import patch
from itertools import product

from mathos.research import tga_proctor_signed_hall as s
from mathos.research import tga_proctor_hall as h
from mathos.research import tga_proctor_hybrid_adversary as a
from mathos.research import tga_proctor_xor_cnf as x


class SignedHallTests(unittest.TestCase):
    def test_controls(self):
        r=s.controls()
        self.assertEqual(r["random_cases"],1600)
        self.assertEqual(r["paired_polarity_runs"],3200)
        self.assertEqual(len(r["signed_php"]),18)
        self.assertEqual(r["equal_size_controls"],18)
        self.assertEqual(len(r["noisy_negative"]),6)

    def test_every_polarity_on_php2(self):
        n,cs=a.pigeonhole(2)
        for bits in product((False,True),repeat=n):
            flips=tuple(i for i,b in enumerate(bits,1) if b)
            changed=s._flip(cs,flips)
            r=s.solve(n,changed)
            self.assertEqual(r["status"],"UNSAT")
            self.assertEqual(r["flips"],flips)
            self.assertTrue(s.verify(n,changed,r))

    def test_original_indices_and_tamper(self):
        n,cs=a.pigeonhole(3)
        cs=((1,-1),(n+1,n+2))+s._flip(cs,(1,2,3))
        n+=2
        r=s.solve(n,cs)
        self.assertEqual(r["status"],"UNSAT")
        self.assertEqual(r["flips"],(1,2,3))
        c=r["certificate"]
        self.assertTrue(all(i>=2 for i in c["demands"]))
        with patch.object(s,"orientation",side_effect=AssertionError("no orientation")), \
             patch.object(h,"_discover",side_effect=AssertionError("no discovery")), \
             patch.object(h,"_deficiency",side_effect=AssertionError("no matching")):
            self.assertTrue(s.verify(n,cs,r))
            for flips in ((),(1,2),(1,2,3,3),(3,2,1),(True,2,3),(1,2,n+1_000)):
                self.assertFalse(s.verify(n,cs,{**r,"flips":flips}))
            self.assertFalse(s.verify(n,cs,{**r,"certificate":{**c,"demands":(0,)+c["demands"][1:]}}))

    def test_orientation_normalization(self):
        n=2**200
        cs=((n,n),(-n,2),(-n,2),(-n,3),(n,-n),(4,))
        self.assertEqual(s.orientation(n,cs),(2,3,4,n))
        self.assertEqual(s.orientation(n,s._flip(cs,(4,n))),(2,3,-4,-n))

    def test_noisy_negative_and_fallback(self):
        n,cs=s.noisy_php(2)
        self.assertFalse(x._brute(cs))
        self.assertEqual(s.solve(n,cs)["status"],"UNKNOWN")
        r=s.solve_hybrid(n,cs,0,0)
        self.assertEqual(r["route"],"HALL")
        self.assertTrue(s.verify_hybrid(n,cs,r))
        r=s.solve_hybrid(1,((1,),),0,10)
        self.assertEqual(r["status"],"SAT")
        self.assertTrue(s.verify_hybrid(1,((1,),),r))

    def test_invalid_and_unknown(self):
        self.assertEqual(s.solve(0,())["status"],"UNKNOWN")
        self.assertFalse(s.verify(0,(),s.solve(0,())))
        for p,k in ((-1,0),(0,-1),(True,1)):
            with self.assertRaises(ValueError):
                s.solve_hybrid(0,(),p,k)
        with self.assertRaises(ValueError):
            s.solve(1,((True,),))


if __name__ == "__main__":
    unittest.main()
