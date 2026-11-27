import unittest
from itertools import product
from mathos.research.pnp_overlap_boundary import (
    project, affine_rows, affine_solve, solve, verify, reduce_3sat, audit)

class OverlapTests(unittest.TestCase):
    def test_all_domains(self):
        a=audit()
        self.assertEqual(a["relation_sizes"],{0:49,1:100,2:73,3:18,4:16})
        self.assertEqual(a["triple_missing_output"],{1:9,2:9})
        for l,r in product(range(16),repeat=2):
            rel=project(l,r)
            for v in range(4):
                self.assertEqual(solve([(l,r)],[(1,v&1),(2,v>>1)]) is not None,v in rel)
            if len(rel)!=3:
                rows=affine_rows(rel)
                self.assertEqual({v for v in range(4) if all(
                    (v&m).bit_count()%2==b for m,b in rows)},set(rel))

    def test_affine_elimination(self):
        for rows in product([(m,b) for m in range(8) for b in range(2)],repeat=2):
            expected=any(all((v&m).bit_count()%2==b for m,b in rows) for v in range(8))
            self.assertEqual(affine_solve(3,rows) is not None,expected)

    def test_coupled_components(self):
        ds=[(10,15),(15,10)]
        for rows in product([(m,b) for m in range(16) for b in range(2)],repeat=2):
            expected=any(all(((u|(v<<2))&m).bit_count()%2==b for m,b in rows)
                         for u,v in product(project(*ds[0]),project(*ds[1])))
            w=solve(ds,rows)
            self.assertEqual(w is not None,expected)
            if w is not None:
                self.assertTrue(verify(ds,rows,w))

    def test_reduction(self):
        clauses=list(product((-2,-1,1,2),repeat=3))
        examples=[[],[(1,1,1),(-1,-1,-1)],[(1,-1,2)]]
        examples += [[c] for c in clauses]
        examples += [[c,d] for c,d in zip(clauses,reversed(clauses))]
        for formula in examples:
            expected=any(all(any(bool(bits[abs(l)-1])==(l>0) for l in c)
                             for c in formula) for bits in product(range(2),repeat=2))
            ds,rows=reduce_3sat(formula)
            w=solve(ds,rows)
            self.assertEqual(w is not None,expected)
            if w is not None:
                self.assertTrue(verify(ds,rows,w))

    def test_invalid_and_empty(self):
        self.assertEqual(solve([],[]),())
        self.assertIsNone(solve([],[(0,1)]))
        with self.assertRaises(ValueError):
            reduce_3sat([(0,1,2)])
        with self.assertRaises(ValueError):
            solve([(10,15)],[(4,0)])
