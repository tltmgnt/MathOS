import unittest
from itertools import product
from copy import deepcopy
from mathos.research.pnp_overlap_boundary import reduce_3sat
from mathos.research.pnp_overlap_recovery import recover, hierarchy_instance
from mathos.research.pnp_overlap_order import recover_fast, minimum_order, check_minimum, evidence
from mathos.research.pnp_overlap_adaptive import _consistent

class MinimumOrderTests(unittest.TestCase):
    def test_fast_closure_equivalence(self):
        for ds in ([(10,15),(15,10)],[(15,15),(10,15)],[(0,15),(10,15)]):
            for rs in product([(m,b) for m in range(16) for b in (0,1)],repeat=2):
                for order in (1,2):
                    a,_,ae=recover(ds,rs,order)
                    b,_,be=recover_fast(ds,rs,order)
                    self.assertEqual(ae is None,be is None)
                    if ae is None:
                        self.assertEqual({v for v in range(16) if all((v&m).bit_count()%2==x for m,x in a)},
                                         {v for v in range(16) if all((v&m).bit_count()%2==x for m,x in b)})

    def test_exact_threshold_small(self):
        for ds in ([(10,15),(15,10)],[(0,15),(10,15)]):
            for rs in product([(m,b) for m in range(16) for b in (0,1)],repeat=2):
                expected=0 if not _consistent(4,rs) else next((r for r in (1,2) if recover(ds,rs,r)[2] is not None),None)
                cert=minimum_order(ds,rs)
                self.assertEqual(cert["minimum"],expected)
                self.assertTrue(check_minimum(ds,rs,cert))

    def test_hierarchy_and_mutations(self):
        for r in (1,2,3):
            ds,rs=hierarchy_instance(r)
            cert=minimum_order(ds,rs)
            self.assertEqual(cert["minimum"],r+1)
            self.assertTrue(check_minimum(ds,rs,cert))
            for mutate in (lambda c:c.update(minimum=1),
                           lambda c:c["lower"].update(order=0),
                           lambda c:c["lower"]["rows"].append([0,1]),
                           lambda c:c["lower"].update(rows=[]),
                           lambda c:c["upper"].update(trace=[])):
                bad=deepcopy(cert)
                mutate(bad)
                self.assertFalse(check_minimum(ds,rs,bad))

    def test_full_order_sat_reduction(self):
        for formula in ([(1,1,1),(-1,-1,-1)],[(1,1,1),(1,-1,2)]):
            ds,rs=reduce_3sat(formula)
            cert=minimum_order(ds,rs)
            self.assertTrue(check_minimum(ds,rs,cert))
            self.assertEqual(cert["minimum"] is not None,formula[1]==(-1,-1,-1))

    def test_degenerate(self):
        for ds,rs,expected in (([],[],None),([],[(0,1)],0),([(0,15)],[],1),
                               ([(10,15)],[],None)):
            cert=minimum_order(ds,rs)
            self.assertEqual(cert["minimum"],expected)
            self.assertTrue(check_minimum(ds,rs,cert))
        self.assertFalse(check_minimum([],[],{"minimum":False,"upper":{},"lower":None}))
        with self.assertRaises(ValueError):
            recover_fast([],[],-1)

    def test_evidence(self):
        self.assertEqual([c["minimum"] for c in evidence()["cases"]],[2,3,4])
