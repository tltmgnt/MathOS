import unittest
from unittest.mock import patch
from itertools import product

from mathos.research import tga_proctor_hybrid_adversary as a
from mathos.research import tga_proctor_hybrid_sat as h
from mathos.research import tga_proctor_dynamic_components as d
from mathos.research import tga_proctor_dynamic_resolution as r
from mathos.research import tga_proctor_xor_cnf as x


class WideAuditTests(unittest.TestCase):
    def test_controls(self):
        report=a.controls()
        self.assertEqual(report["random_cases"],1000)
        self.assertEqual(sum(report["outcomes"].values()),1000)
        self.assertEqual(len(report["php"]),6)
        self.assertEqual(len(report["shared_selector"]),6)

    def test_wide_php_resolution(self):
        n,cs=a.pigeonhole(4)
        self.assertEqual(h.solve(n,cs,1000,10000)["reason"],"UNSUPPORTED_SEARCH_WIDTH")
        out=h.solve(n,cs,1000,10000,allow_wide=True)
        self.assertEqual(out["status"],"UNSAT")
        pre,search=out["proof"]
        p=r.extract(n,cs,search,wide=True)
        with patch.object(d,"verify",side_effect=AssertionError("no dynamic replay")):
            self.assertTrue(r.verify(n,cs,p,wide=True))
            self.assertFalse(r.verify(n,cs,{**p,"conclusion":0},wide=True))
        self.assertFalse(h.verify(n,cs,out))
        self.assertTrue(h.verify(n,cs,out,allow_wide=True))

    def test_php_sat_and_budget(self):
        n,cs=a.pigeonhole(4,4)
        out=h.solve(n,cs,0,10000,allow_wide=True)
        self.assertEqual(out["status"],"SAT")
        self.assertTrue(h.verify(n,cs,out,allow_wide=True))
        n,cs=a.pigeonhole(4)
        out=h.solve(n,cs,0,1,allow_wide=True)
        self.assertEqual(out["status"],"UNKNOWN")
        self.assertEqual(out["search_nodes"],1)

    def test_wide_dynamic_and_tamper(self):
        # Every assignment on four bits is forbidden. Use direct dynamic
        # here so that the algebraic stage cannot shortcut the test.
        cs=tuple(tuple(-i if b else i for i,b in enumerate(bits,1))
                 for bits in product((False,True),repeat=4))
        out=d.solve(4,cs,100,wide=True)
        self.assertEqual(out["status"],"UNSAT")
        self.assertTrue(d.verify(4,cs,out,wide=True))
        self.assertFalse(d.verify(4,cs,{**out,"tree":out["tree"][:-1]},wide=True))
        self.assertTrue(r.verify(4,cs,r.extract(4,cs,out,wide=True),wide=True))
        with self.assertRaises(ValueError):
            d.solve(4,cs)
        with self.assertRaises(ValueError):
            h.solve(4,cs,allow_wide=1)

    def test_sparse_wide(self):
        n=2**200
        cs=((n,1,2,3,4,5),(-n,),(-1,),(-2,),(-3,),(-4,),(-5,))
        out=d.solve(n,cs,10,wide=True)
        self.assertEqual(out["status"],"UNSAT")
        self.assertTrue(d.verify(n,cs,out,wide=True))
        self.assertTrue(r.verify(n,cs,r.extract(n,cs,out,wide=True),wide=True))


if __name__ == "__main__":
    unittest.main()
