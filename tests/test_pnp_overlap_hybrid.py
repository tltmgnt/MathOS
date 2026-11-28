import unittest
from copy import deepcopy
from itertools import product
from mathos.research.pnp_overlap_hybrid import (
    dynamic,check_dynamic,hybrid,check_hybrid,dynamic_only_instance,resistant_instance,evidence)
from mathos.research.pnp_overlap_degree import refute
from mathos.research.pnp_overlap_boundary import solve
from mathos.research.pnp_overlap_algebraic import frame
from mathos.research.pnp_overlap_pebbling import chain

class HybridTests(unittest.TestCase):
    def test_dynamic_small_complete(self):
        for ds in ([(10,15),(15,10)],[(0,15),(15,15)],[(15,15),(10,15)]):
            for m,b in product(range(16),(0,1)):
                rs=[(m,b)]
                fr=frame(4,rs)
                d=len(fr[1])+2 if fr else 0
                p=dynamic(ds,rs,d)
                self.assertTrue(check_dynamic(ds,rs,p))
                self.assertEqual(p["kind"]=="dynamic_closed",solve(ds,rs) is not None)

    def test_static_inclusion_and_chains(self):
        for n in (1,3,7,15):
            ds,rs=chain(n)
            p=dynamic(ds,rs,2)
            self.assertEqual(p["kind"],"dynamic_refutation")
            self.assertTrue(check_dynamic(ds,rs,p))
        ds,rs=chain(7)
        self.assertEqual(refute(ds,rs,2)["kind"],"no_refutation")

    def test_dynamic_only(self):
        ds,rs=dynamic_only_instance()
        p=hybrid(ds,rs)
        self.assertEqual(p["kind"],"dynamic")
        self.assertTrue(check_hybrid(ds,rs,p))
        self.assertEqual(refute(ds,rs,2)["kind"],"no_refutation")

    def test_resistant_and_fallback(self):
        ds,rs=resistant_instance()
        p=hybrid(ds,rs)
        self.assertEqual(p["kind"],"inconclusive")
        self.assertTrue(check_hybrid(ds,rs,p))
        self.assertEqual(p["trace"],[])
        q=hybrid(ds,rs,fallback=True)
        self.assertTrue(check_hybrid(ds,rs,q))
        self.assertEqual(q["kind"],"fallback")
        self.assertNotEqual(q["proof"]["kind"],"sat")

    def test_mutations(self):
        ds,rs=dynamic_only_instance()
        p=hybrid(ds,rs)
        for mutate in (lambda c:c["proof"]["lines"].pop(),
                       lambda c:c["proof"]["lines"].append(["xor",999999,0]),
                       lambda c:c.update(degree=1),
                       lambda c:c["trace"].append({"components":[0],"row":[1,0]})):
            q=deepcopy(p)
            mutate(q)
            self.assertFalse(check_hybrid(ds,rs,q))
        ds,rs=resistant_instance()
        p=hybrid(ds,rs)
        p["dynamic"]["basis"]=[]
        self.assertFalse(check_hybrid(ds,rs,p))

    def test_degenerate_and_evidence(self):
        for ds,rs in (([],[]),([],[(0,1)]),([(0,15)],[]),([(15,15)],[])):
            p=hybrid(ds,rs,fallback=True)
            self.assertTrue(check_hybrid(ds,rs,p))
        with self.assertRaises(ValueError):
            dynamic([(10,15)]*30,[],5)
        self.assertEqual([c["result"] for c in evidence()["cases"]],
                         ["local_unsat","static","dynamic","inconclusive"])
