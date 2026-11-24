import unittest
from unittest.mock import patch

from mathos.research import tga_proctor_xor_bve as b
from mathos.research import tga_proctor_xor_cnf as x


class BVETests(unittest.TestCase):
    def test_controls(self):
        r=b.controls()
        self.assertEqual(r["random_cases"],1500)
        self.assertEqual(r["certified_unsat"]+r["unknown"],1500)
        self.assertEqual(len(r["fixtures"]),12)

    def test_local_obfuscation(self):
        from itertools import product
        n,cs=b.obfuscate(3,((1,-2,3),),29)
        for bits in product((False,True),repeat=3):
            expected=bits[0] or not bits[1] or bits[2]
            actual=any(all(any((bits+(z,))[abs(l)-1]==(l>0) for l in c)
                           for c in cs) for z in (False,True))
            self.assertEqual(expected,actual)
        r=b.eliminate(n,cs,order=(4,),pair_limit=1)
        self.assertEqual(b.replay(n,cs,r),((-2,1,3),))

    def test_growth_width_and_budget(self):
        cs=((1,2),(1,3),(1,4),(-1,5),(-1,6),(-1,7))
        r=b.eliminate(7,cs,order=(1,))
        self.assertEqual(r["eliminated"],0)
        self.assertEqual(r["pair_tests"],9)
        self.assertEqual(len(b.replay(7,cs,r)),6)
        r=b.eliminate(4,((1,2,3),(-1,4)),order=(1,),max_width=2)
        self.assertEqual(r["eliminated"],0)
        r=b.eliminate(2,((1,2),(-1,2)),order=(1,),pair_limit=0)
        self.assertEqual(r["pair_tests"],0)
        self.assertEqual(r["eliminated"],0)

    def test_pure_taut_and_duplicates(self):
        cs=((1,2),(-1,-2),(3,),(3,),(4,-4))
        r=b.eliminate(4,cs,order=(1,3))
        self.assertEqual(b.replay(4,cs,r),())
        self.assertEqual(r["eliminated"],2)

    def test_tamper(self):
        cs=x.encode_parity((1,2,3),0)+x.encode_parity((1,2,3),1)
        n,hidden=b.obfuscate(3,cs,11)
        r=b.solve(n,hidden,order=range(4,n+1))
        self.assertEqual(r["status"],"UNSAT")
        p=r["preprocessing"]
        a,c,v=p["steps"][0]
        e=p["eliminations"][0]
        with patch.object(b,"eliminate",side_effect=AssertionError("no solver")), \
             patch.object(x,"solve",side_effect=AssertionError("no XOR solver")):
            self.assertTrue(b.verify(n,hidden,r))
            mutations=(
                {**p,"steps":((a,c,-v),)+p["steps"][1:]},
                {**p,"steps":((a,999,v),)+p["steps"][1:]},
                {**p,"eliminations":((e[0],e[1],e[2],()),)+p["eliminations"][1:]},
                {**p,"residual":p["residual"][:-1]},
                {**p,"steps":p["steps"]+p["steps"]},
                {**p,"eliminations":p["eliminations"][:-1]},
            )
            for bad in mutations:
                self.assertFalse(b.verify(n,hidden,{**r,"preprocessing":bad}))
            self.assertFalse(b.verify(n,hidden,{**r,"parity":{"status":"UNKNOWN"}}))

    def test_sparse_invalid_and_empty(self):
        n=2**100
        cs=((n,),(-n,))
        r=b.solve(n,cs)
        self.assertTrue(b.verify(n,cs,r))
        self.assertTrue(b.verify(0,((),),b.solve(0,((),))))
        self.assertEqual(b.solve(0,())["status"],"UNKNOWN")
        for order in ((True,),(1,),(n,n)):
            with self.assertRaises(ValueError):
                b.eliminate(n,cs,order=order)
        with self.assertRaises(ValueError):
            b.eliminate(n,cs,pair_limit=-1)


if __name__ == "__main__":
    unittest.main()
