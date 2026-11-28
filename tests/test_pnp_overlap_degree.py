import unittest
from copy import deepcopy
from itertools import product
from mathos.research.pnp_overlap_degree import (
    polynomials,checker_polynomials,refute,check_degree,separation,evidence)
from mathos.research.pnp_overlap_boundary import project,solve
from mathos.research.pnp_overlap_algebraic import frame
from mathos.research.pnp_overlap_order_bounds import encode,two_cycles

class DegreeTests(unittest.TestCase):
    def test_indicators(self):
        for d in product(range(16),repeat=2):
            for rows in ([],[(3,0)],[(1,1),(2,0)]):
                a,dirs=frame(2,rows)
                qs=polynomials([d],a,dirs)
                self.assertEqual(qs,checker_polynomials([d],a,dirs))
                for x in range(1<<len(dirs)):
                    v=a
                    for j,z in enumerate(dirs):
                        if x>>j&1:
                            v^=z
                    self.assertEqual(sum(sum((x&m)==m for m in q)%2 for q in qs.values()),
                                     int(v not in project(*d)))

    def test_exhaustive_small_complete(self):
        for ds in ([(10,15),(15,10)],[(0,15),(15,15)],[(15,15),(10,15)]):
            for mask,b in product(range(16),(0,1)):
                rs=[(mask,b)]
                fr=frame(4,rs)
                d=len(fr[1])+2 if fr else 0
                cert=refute(ds,rs,d)
                self.assertTrue(check_degree(ds,rs,cert))
                self.assertEqual(cert["kind"]=="no_refutation",solve(ds,rs) is not None)

    def test_strict_separation(self):
        r=separation()
        self.assertEqual((r["blocks"],r["minimum_static_degree"]),(6,3))
        ds,rs=encode(two_cycles(3,3))
        self.assertEqual(refute(ds,rs,1)["kind"],"no_refutation")
        self.assertTrue(check_degree(ds,rs,r["lower"]))
        self.assertTrue(check_degree(ds,rs,r["upper"]))

    def test_mutations(self):
        ds,rs=encode(two_cycles(3,3))
        r=separation()
        for mutate in (lambda c:c["terms"].pop(),
                       lambda c:c["terms"].append(c["terms"][0]),
                       lambda c:c["terms"][0].__setitem__(2,1<<99),
                       lambda c:c.update(degree=2),
                       lambda c:c["directions"].pop()):
            bad=deepcopy(r["upper"])
            mutate(bad)
            self.assertFalse(check_degree(ds,rs,bad))
        bad=deepcopy(r["lower"])
        bad["functional"].remove(0)
        self.assertFalse(check_degree(ds,rs,bad))
        bad=deepcopy(r["lower"])
        bad["degree"]=3
        self.assertFalse(check_degree(ds,rs,bad))

    def test_degenerate_and_budget(self):
        for ds,rs,d,kind in (([],[],0,"no_refutation"),([],[(0,1)],0,"affine_unsat"),
                             ([(0,15)],[(1,0),(2,0)],0,"refutation")):
            cert=refute(ds,rs,d)
            self.assertEqual(cert["kind"],kind)
            self.assertTrue(check_degree(ds,rs,cert))
        with self.assertRaises(ValueError):
            refute([(10,15)]*30,[],5)
        with self.assertRaises(ValueError):
            refute([],[],-1)

    def test_rm_controls(self):
        out=evidence()
        self.assertEqual([(r["blocks"],r["degree_upper"],r["recovery_order_lower"]) for r in out["rm_cases"]],
                         [(7,2,3),(31,2,7),(127,2,15)])
        self.assertTrue(all(r["checker_accepted"] for r in out["rm_cases"]))
