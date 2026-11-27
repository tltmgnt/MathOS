import unittest
from itertools import product
from copy import deepcopy
from mathos.research.pnp_overlap_order import minimum_order,check_minimum
from mathos.research.pnp_overlap_recovery import hierarchy_instance
from mathos.research.pnp_overlap_order_bounds import encode,predict,check_prediction,girth,two_cycles,evidence

class BoundsTests(unittest.TestCase):
    def test_all_two_variable_clause_sets(self):
        edges=list(product((1,-1),(2,-2)))
        for mask in range(1<<len(edges)):
            es=[e for j,e in enumerate(edges) if (mask>>j)&1]
            # Add contraposed alternatives in a second exhaustive family.
            for subset in (es,es+[(2,-1),(-2,1)]):
                cert=predict(subset)
                ds,rs=encode(subset)
                exact=minimum_order(ds,rs)
                self.assertTrue(check_prediction(subset,cert))
                self.assertTrue(check_minimum(ds,rs,exact))
                if cert["kind"]=="sat":
                    self.assertIsNone(exact["minimum"])
                else:
                    self.assertLessEqual(cert["lower"],exact["minimum"])
                    self.assertLessEqual(exact["minimum"],cert["upper"])

    def test_signed_forest(self):
        for signs in product((1,-1),repeat=6):
            es=[(signs[2*i]*(i+1),signs[2*i+1]*(i+2)) for i in range(3)]
            self.assertIsNone(girth(es))
            self.assertEqual(predict(es)["kind"],"sat")
            self.assertTrue(check_prediction(es,predict(es)))

    def test_equal_cycle_hierarchy(self):
        for r in (1,2,3):
            es=two_cycles(r+1,r+1)
            self.assertEqual(encode(es),hierarchy_instance(r))
            cert=predict(es)
            self.assertEqual((cert["lower"],cert["upper"]),(r+1,r+1))
            self.assertTrue(check_prediction(es,cert))

    def test_large_prediction(self):
        es=two_cycles(21,21)
        cert=predict(es)
        self.assertEqual((len(es),cert["lower"],cert["upper"]),(42,21,21))
        self.assertTrue(check_prediction(es,cert))

    def test_mutations(self):
        es=two_cycles(3,3)
        cert=predict(es)
        for mutate in (lambda c:c.update(lower=4),lambda c:c.update(upper=2),
                       lambda c:c["paths"][0][0].__setitem__(2,999),
                       lambda c:c["paths"][1].pop(),lambda c:c.update(variable=999)):
            bad=deepcopy(cert)
            mutate(bad)
            self.assertFalse(check_prediction(es,bad))
        self.assertFalse(check_prediction(es,{"kind":"sat","lower":None,"upper":None}))
        self.assertFalse(check_prediction([],cert))
        with self.assertRaises(ValueError):
            predict([(1,-1)])

    def test_evidence(self):
        data=evidence()
        self.assertEqual(data["large"]["minimum_analytic"],21)
        self.assertEqual(len(data["small_exact_controls"]),4)
