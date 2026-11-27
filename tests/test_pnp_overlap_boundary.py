import unittest
from itertools import product
from mathos.research.pnp_overlap_boundary import (
    project, affine_rows, affine_solve, solve, verify, reduce_3sat, audit,
    independent_coordinates, solve_ranked, rank_demo)

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

    def test_rank_projection_exact(self):
        for rows in product([(m,b) for m in range(16) for b in range(2)],repeat=2):
            xs=[v for v in range(16) if all((v&m).bit_count()%2==b for m,b in rows)]
            if not xs:
                continue
            coords=(0,2)
            basis=independent_coordinates(4,rows,coords)
            patterns={tuple((v>>j)&1 for j in coords) for v in xs}
            images={tuple((v>>j)&1 for j in basis) for v in xs}
            self.assertEqual(len(patterns),1<<len(basis))
            self.assertEqual(len(images),len(patterns))

    def test_rank_solver_against_exhaustive(self):
        for ds in ([(10,15),(15,10)],[(10,15),(0,15)],[(15,15),(10,15)]):
            for rows in product([(m,b) for m in range(16) for b in range(2)],repeat=2):
                expected=any(all(((u|(v<<2))&m).bit_count()%2==b for m,b in rows)
                             for u,v in product(project(*ds[0]),project(*ds[1])))
                stats={}
                w=solve_ranked(ds,rows,stats=stats)
                self.assertEqual(w is not None,expected)
                if w is not None:
                    self.assertTrue(verify(ds,rows,w))
                else:
                    self.assertEqual(stats["visited"],stats["affine_feasible_patterns"])
                if stats["d"] is not None:
                    self.assertLessEqual(stats["d"],stats["k"])

    def test_rank_demo(self):
        r=rank_demo()
        self.assertEqual((r["k"],r["d"],r["visited"],r["affine_feasible_patterns"]),
                         (21,1,2,2))
        self.assertEqual(r["unfiltered_patterns"],2097152)
        self.assertIsNone(solve_ranked([],[(0,1)]))
        self.assertEqual(solve_ranked([],[]),())

    def test_invalid_and_empty(self):
        self.assertEqual(solve([],[]),())
        self.assertIsNone(solve([],[(0,1)]))
        with self.assertRaises(ValueError):
            reduce_3sat([(0,1,2)])
        with self.assertRaises(ValueError):
            solve([(10,15)],[(4,0)])
