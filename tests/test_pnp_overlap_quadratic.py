import unittest
from copy import deepcopy
from itertools import product
from mathos.research.pnp_overlap_quadratic import (
    rm_basis,transform,check_quadratic,rm_instance,check_rm,violation_parity,evidence)
from mathos.research.pnp_overlap_algebraic import points
from mathos.research.pnp_overlap_order import recover_fast
from mathos.research.pnp_overlap_certificates import _rank

class QuadraticTests(unittest.TestCase):
    def test_small_rm_exhaustive(self):
        ds,rs,cert=rm_instance(3)
        q=cert["quadratic"]
        self.assertTrue(check_rm(ds,rs,cert))
        self.assertEqual(len(q["directions"]),6)
        self.assertTrue(all(violation_parity(x,7)==1 for x in points(q["anchor"],q["directions"])))
        rows,trace,empty=recover_fast(ds,rs,2)
        self.assertEqual((rows,trace,empty),(rs,[],None))

    def test_generic_transform(self):
        ds,rs,cert=transform(4,[15])
        self.assertTrue(check_quadratic(ds,rs,cert))
        self.assertEqual(len(cert["directions"]),2)
        self.assertTrue(all(violation_parity(x,3)==1 for x in points(cert["anchor"],cert["directions"])))
        with self.assertRaises(ValueError):
            transform(4,[8])
        with self.assertRaises(ValueError):
            transform(4,[15,15])

    def test_exact_small_distance(self):
        ds,rs,cert=rm_instance(3)
        masks=[m for m,b in rs]
        self.assertEqual(len(masks),8)
        weights=[]
        for bits in product((0,1),repeat=len(masks)):
            v=0
            for m,b in zip(masks,bits):
                if b:
                    v^=m
            if v:
                weights.append(sum(bool(v&(3<<(2*i))) for i in range(7)))
        self.assertEqual(min(weights),cert["minimum_order_lower"])

    def test_mutations(self):
        ds,rs,cert=rm_instance(3)
        for mutate in (lambda c:c.update(minimum_order_lower=4),
                       lambda c:c["quadratic"]["directions"].pop(),
                       lambda c:c["quadratic"].update(anchor=1<<14),
                       lambda c:c["quadratic"]["directions"].append(c["quadratic"]["directions"][0])):
            bad=deepcopy(cert)
            mutate(bad)
            self.assertFalse(check_rm(ds,rs,bad))
        self.assertFalse(check_rm([(15,15)]*7,rs,cert))
        self.assertFalse(check_rm(ds,rs[:-1],cert))

    def test_quadratic_identity_needs_pairs(self):
        # For one block, violation is zero at 00, 01, 11 but one at 10.
        # Anchor 10 is a violation; any nonzero direction changes it.
        self.assertTrue(check_quadratic([(10,15)],[(1,0),(2,1)],{"anchor":2,"directions":[]}))
        self.assertFalse(check_quadratic([(10,15)],[],{"anchor":2,"directions":[1,2]}))
        # In two blocks, anchor has odd violation, and both single steps
        # preserve it, but the mixed step does not.
        self.assertEqual([violation_parity(x,2) for x in (2,2^4,2^8,2^4^8)],[1,1,0,1])
        # A genuine mixed-term example: first block always violates; vary both
        # bits in the second around 01 (integer 1), with directions 01 and 11.
        a=2|(1<<2)
        self.assertEqual([violation_parity(x,2) for x in (a,a^4,a^8,a^4^8)],[1,1,1,0])
        self.assertFalse(check_quadratic([(10,15)]*2,[(1,0),(2,1)],{"anchor":a,"directions":[4,8]}))

    def test_large_controls(self):
        out=evidence()
        self.assertEqual([(x["blocks"],x["minimum_order_lower"]) for x in out["cases"]],[(7,3),(31,7),(127,15)])
        self.assertFalse(out["ag_family"]["supplier_implemented"])
