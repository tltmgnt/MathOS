import unittest
from itertools import product
from copy import deepcopy
from mathos.research.pnp_overlap_boundary import project,reduce_3sat
from mathos.research.pnp_overlap_order import minimum_order
from mathos.research.pnp_overlap_algebraic import (
    frame,points,bounds,check_bounds,projective_instance,pencil_proof,evidence)
from mathos.research.pnp_overlap_recovery import check_recovered

class AlgebraicTests(unittest.TestCase):
    def test_frames_exhaustive(self):
        for rs in product([(m,b) for m in range(16) for b in (0,1)],repeat=2):
            expected={x for x in range(16) if all((x&m).bit_count()%2==b for m,b in rs)}
            fr=frame(4,rs)
            self.assertEqual(set() if fr is None else set(points(*fr)),expected)

    def test_bounds_exhaustive(self):
        for ds in ([(10,15),(15,10)],[(15,15),(10,15)],[(0,15),(10,15)]):
            for rs in product([(m,b) for m in range(16) for b in (0,1)],repeat=2):
                cert=bounds(ds,rs)
                exact=minimum_order(ds,rs)["minimum"]
                self.assertTrue(check_bounds(ds,rs,cert))
                if cert["kind"]=="bounds":
                    self.assertLessEqual(cert["lower"],exact)
                    self.assertLessEqual(exact,cert["upper"])
                elif cert["kind"]=="sat":
                    self.assertIsNone(exact)
                else:
                    self.assertEqual(exact,0)

    def test_pencil_small(self):
        ds,rs,vs=projective_instance(2)
        cert=bounds(ds,rs,3)
        self.assertEqual(cert["lower"],4)
        self.assertTrue(check_bounds(ds,rs,cert))
        upper=pencil_proof(ds,rs,vs)
        self.assertTrue(check_recovered(ds,rs,upper))
        self.assertEqual(minimum_order(ds,rs)["minimum"],4)

    def test_large_algebraic_control(self):
        r=evidence()
        self.assertEqual((r["blocks"],r["affine_dimension"],r["affine_points"],r["exact_minimum"]),(21,6,64,4))

    def test_mutations(self):
        ds,rs,vs=projective_instance(2)
        cert=bounds(ds,rs,3)
        for mutate in (lambda c:c.update(anchor=c["anchor"]^1),
                       lambda c:c["directions"].pop(),
                       lambda c:c["directions"].append(c["directions"][0]),
                       lambda c:c.update(lower=5),
                       lambda c:c["core"].pop(),
                       lambda c:c["core"].reverse()):
            bad=deepcopy(cert)
            mutate(bad)
            self.assertFalse(check_bounds(ds,rs,bad))

    def test_np_complete_encoding_and_budget(self):
        for formula in ([(1,1,1),(-1,-1,-1)],[(1,2,3)]):
            ds,rs=reduce_3sat(formula)
            cert=bounds(ds,rs,2)
            self.assertTrue(check_bounds(ds,rs,cert))
            self.assertEqual(cert["kind"]=="sat",len(formula)==1)
        with self.assertRaises(ValueError):
            bounds([(10,15)]*9,[],max_dimension=16)
        self.assertTrue(check_bounds([],[],bounds([],[])))
