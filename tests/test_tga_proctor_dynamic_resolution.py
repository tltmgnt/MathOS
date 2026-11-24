import unittest
from itertools import product
from unittest.mock import patch

from mathos.research import tga_proctor_dynamic_resolution as a
from mathos.research import tga_proctor_dynamic_components as d
from mathos.research import tga_proctor_component_search as root


class DynamicResolutionTests(unittest.TestCase):
    def test_controls(self):
        r = a.controls()
        self.assertEqual(r["random_cases"], 600)
        self.assertGreater(r["random_unsat_extracted"], 0)
        self.assertEqual(len(r["cubic_graphs"]), 14)

    def test_subset_and_tamper(self):
        n, cs = root.guarded_root_obstruction(4)
        p = a.extract(n, cs, d.solve(n, cs, 8))
        with patch.object(d, "verify", side_effect=AssertionError("no dynamic replay")):
            self.assertTrue(a.verify(n, cs, p))
            self.assertFalse(a.verify(n, cs, {**p, "conclusion": 0}))
            self.assertFalse(a.verify(n, cs, {**p, "conclusion": True}))
            self.assertFalse(a.verify(n, cs, {**p, "steps": (("resolve", 0, 0, 1),)+p["steps"][1:]}))
            self.assertFalse(a.verify(n, cs, {**p, "steps": (("axiom", len(cs)),)+p["steps"][1:]}))
            j = next(i for i,s in enumerate(p["steps"]) if s[0] == "resolve")
            _, x,y,l = p["steps"][j]
            bad = p["steps"][:j]+(("resolve", x,y,0),)+p["steps"][j+1:]
            self.assertFalse(a.verify(n, cs, {**p, "steps": bad}))

    def test_empty_and_reject_nonproof(self):
        self.assertTrue(a.verify(0, ((),), a.extract(0, ((),), d.solve(0, ((),)))))
        with self.assertRaises(ValueError):
            a.extract(1, ((1,),), d.solve(1, ((1,),)))
        with self.assertRaises(ValueError):
            a.extract(1, ((1,),), d.solve(1, ((1,),), 0))

    def test_parity_encoding(self):
        for charge in (False, True):
            edges = a.cubic_graph(4, 11)
            n, cs = a.tseitin(4, edges, (charge, False, False, False))
            self.assertEqual((n,len(cs)), (6,16))
            for bits in product((False,True), repeat=n):
                parity = [False]*4
                for (u,v), b in zip(edges, bits):
                    parity[u] ^= b
                    parity[v] ^= b
                self.assertEqual(root._holds(cs, dict(zip(range(1,n+1),bits))),
                                 parity == [charge, False, False, False])
            r = d.solve(n, cs, 10000)
            self.assertEqual(r["status"], "UNSAT" if charge else "SAT")
            self.assertTrue(d.verify(n,cs,r))

    def test_sparse_pure_and_units(self):
        n = 2**100
        cs = ((n, 9), (5,), (-5, 7), (-7,), (-n,n))
        r = d.solve(n, cs)
        self.assertEqual(r["status"], "UNSAT")
        self.assertTrue(a.verify(n, cs, a.extract(n, cs, r)))


if __name__ == "__main__":
    unittest.main()
