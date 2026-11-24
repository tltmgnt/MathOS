import unittest
from unittest.mock import patch

from mathos.research import tga_proctor_hybrid_sat as h
from mathos.research import tga_proctor_blind_parity as b
from mathos.research import tga_proctor_xor_cnf as x
from mathos.research import tga_proctor_dynamic_components as d


class HybridTests(unittest.TestCase):
    def test_controls(self):
        r=h.controls()
        self.assertEqual(r["random_formulas"],1400)
        self.assertEqual(r["budgeted_runs"],4200)
        self.assertEqual(sum(r["outcomes"].values()),4200)
        self.assertEqual(len(r["graph_controls"]),6)

    def test_direct_and_bve_routes(self):
        cs=x.encode_parity((1,2,3),0)+x.encode_parity((1,2,3),1)
        r=h.solve(3,cs,0,0)
        self.assertEqual((r["status"],r["route"]),("UNSAT","DIRECT_XOR"))
        n,hidden=b.chain_split(3,cs,11,2)
        n,hidden=b.relabel(n,hidden,47)
        s=h.solve(n,hidden,16,0)
        self.assertEqual((s["status"],s["route"]),("UNSAT","BVE_XOR"))
        self.assertEqual((s["pair_tests"],s["search_nodes"]),(16,0))
        with patch.object(x,"solve",side_effect=AssertionError("no XOR search")), \
             patch.object(b,"solve",side_effect=AssertionError("no BVE search")), \
             patch.object(d,"solve",side_effect=AssertionError("no dynamic search")):
            self.assertTrue(h.verify(3,cs,r))
            self.assertTrue(h.verify(n,hidden,s))
            self.assertFalse(h.verify(n,hidden,{**s,"route":"DIRECT_XOR"}))
            self.assertFalse(h.verify(n,hidden,{**s,"proof":r["proof"]}))

    def test_projected_dynamic_unsat(self):
        cs=((1,),(-1,2),(-2,))
        r=h.solve(2,cs,0,10)
        self.assertEqual((r["status"],r["route"]),("UNSAT","DYNAMIC_PROJECTED"))
        pre,search=r["proof"]
        self.assertTrue(h.verify(2,cs,r))
        self.assertFalse(h.verify(2,cs,{**r,"proof":({**pre,"residual":()},search)}))
        self.assertFalse(h.verify(2,cs,{**r,"proof":(pre,{**search,"status":"SAT"})}))
        self.assertEqual(h.solve(2,cs,0,0)["reason"],"ZERO_SEARCH_BUDGET")

    def test_lift_and_original_fallback(self):
        n=2**200
        cs=((1,2,3,n),(-1,))
        r=h.solve(n,cs,1,100)
        self.assertEqual((r["status"],r["route"]),("SAT","DYNAMIC_PROJECTED"))
        self.assertTrue(h.verify(n,cs,r))
        self.assertFalse(h.verify(n,cs,{**r,"witness":(False,)*4}))
        cs=((1,2,3),(-1,4,5))
        r=h.solve(5,cs,1,100)
        self.assertEqual((r["status"],r["route"]),("SAT","DYNAMIC_ORIGINAL"))
        self.assertTrue(h.verify(5,cs,r))

    def test_width_budget_and_invalid(self):
        self.assertEqual(h.solve(4,((1,2,3,4),),0,100)["reason"],"UNSUPPORTED_SEARCH_WIDTH")
        self.assertEqual(h.solve(0,(),0,0)["status"],"UNKNOWN")
        self.assertTrue(h.verify(0,(),h.solve(0,(),0,1)))
        self.assertTrue(h.verify(0,((),),h.solve(0,((),),0,0)))
        for p,k in ((-1,0),(0,-1),(True,1),(1,True)):
            with self.assertRaises(ValueError):
                h.solve(0,(),p,k)
        with self.assertRaises(ValueError):
            h.solve(1,((0,),))

    def test_nonzero_node_exhaustion(self):
        # SAT nonrenamable-Horn gadget from F030.
        from mathos.research import tga_proctor_adaptive_propagation as a
        n,cs=a.obstruction(4)
        r=h.solve(n,cs,0,1)
        self.assertEqual(r["status"],"UNKNOWN")
        self.assertEqual(r["reason"],"SEARCH_BUDGET")
        self.assertEqual(r["search_nodes"],1)
        self.assertFalse(h.verify(n,cs,r))


if __name__ == "__main__":
    unittest.main()
