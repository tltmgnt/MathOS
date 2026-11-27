import unittest
from itertools import product
from mathos.research.pnp_overlap_boundary import (
    project, affine_rows, affine_solve, solve, verify, reduce_3sat, audit,
    independent_coordinates, solve_ranked, rank_demo,
    minimum_rank_coordinates, graph_rank_instance, optimum_demo,
    independent_forms, minimum_rank_forms, parity_gap_instance, parity_gap_demo)

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

    def test_minimum_rank_exhaustive(self):
        pairs=((0,1),(2,3))
        for rows in product([(m,b) for m in range(16) for b in range(2)],repeat=2):
            opt=minimum_rank_coordinates(4,rows,pairs)
            expected=min(len(independent_coordinates(4,rows,s))
                         for s in product(*pairs))
            self.assertEqual(opt["d"],expected)
            self.assertTrue(all(j in p for j,p in zip(opt["coordinates"],pairs)))
            self.assertEqual(len(independent_coordinates(4,rows,opt["coordinates"])),expected)

    def test_vertex_cover_embedding(self):
        from itertools import combinations
        edges=list(combinations(range(4),2))
        for mask in range(1<<len(edges)):
            es=[e for j,e in enumerate(edges) if (mask>>j)&1]
            ds,rows=graph_rank_instance(es)
            opt=minimum_rank_coordinates(2*len(ds),rows,[(2*i,2*i+1) for i in range(len(ds))])
            expected=min(s.bit_count() for s in range(16)
                         if all((s>>a)&1 or (s>>b)&1 for a,b in es))
            self.assertEqual(opt["d"],expected)

    def test_optimized_solver_against_exhaustive(self):
        for ds in ([(10,15),(15,10)],[(15,15),(10,15)]):
            for rows in product([(m,b) for m in range(16) for b in range(2)],repeat=2):
                expected=any(all(((u|(v<<2))&m).bit_count()%2==b for m,b in rows)
                             for u,v in product(project(*ds[0]),project(*ds[1])))
                w=solve_ranked(ds,rows,optimize=True)
                self.assertEqual(w is not None,expected)
                if w is not None:
                    self.assertTrue(verify(ds,rows,w))

    def test_optimum_demo_and_degenerate(self):
        demo=optimum_demo()
        self.assertEqual((demo["fixed_d"],demo["optimal_d"]),(21,1))
        self.assertEqual((demo["fixed_patterns"],demo["optimal_patterns"]),(2097152,2))
        self.assertEqual(minimum_rank_coordinates(0,[],[])["d"],0)
        self.assertEqual(minimum_rank_coordinates(2,[(1,1)],[(0,1)])["d"],0)
        with self.assertRaises(ValueError):
            minimum_rank_coordinates(2,[],[(0,2)])

    def test_all_linear_slices(self):
        for missing in range(4):
            relation=set(range(4))-{missing}
            for form in (1,2,3):
                for bit in (0,1):
                    sliced={v for v in relation if (v&form).bit_count()%2==bit}
                    self.assertIn(len(sliced),(1,2))
                    rows=affine_rows(sliced)
                    self.assertEqual({v for v in range(4) if all(
                        (v&m).bit_count()%2==b for m,b in rows)},sliced)

    def test_linear_optimum_exhaustive(self):
        groups=((1,2,3),(4,8,12))
        for rows in product([(m,b) for m in range(16) for b in range(2)],repeat=2):
            opt=minimum_rank_forms(4,rows,groups)
            expected=min(len(independent_forms(4,rows,s)) for s in product(*groups))
            self.assertEqual(opt["d"],expected)
            self.assertTrue(all(m in g for m,g in zip(opt["forms"],groups)))
            self.assertEqual(len(independent_forms(4,rows,opt["forms"])),expected)

    def test_linear_vertex_cover_embedding(self):
        from itertools import combinations
        edges=list(combinations(range(4),2))
        for mask in range(1<<len(edges)):
            es=[e for j,e in enumerate(edges) if (mask>>j)&1]
            ds,rows=graph_rank_instance(es)
            opt=minimum_rank_forms(2*len(ds),rows,
                                    [(1<<(2*i),2<<(2*i),3<<(2*i)) for i in range(len(ds))])
            expected=min(s.bit_count() for s in range(16)
                         if all((s>>a)&1 or (s>>b)&1 for a,b in es))
            self.assertEqual(opt["d"],expected)

    def test_linear_solver_against_exhaustive(self):
        for ds in ([(10,15),(15,10)],[(15,15),(10,15)],[(0,15),(10,15)]):
            for rows in product([(m,b) for m in range(16) for b in range(2)],repeat=2):
                expected=any(all(((u|(v<<2))&m).bit_count()%2==b for m,b in rows)
                             for u,v in product(project(*ds[0]),project(*ds[1])))
                w=solve_ranked(ds,rows,linear=True)
                self.assertEqual(w is not None,expected)
                if w is not None:
                    self.assertTrue(verify(ds,rows,w))

    def test_parity_gap(self):
        for k in range(1,7):
            ds,rows=parity_gap_instance(k)
            opt=minimum_rank_coordinates(2*k,rows,[(2*i,2*i+1) for i in range(k)])
            self.assertEqual(opt["d"],k)
            self.assertEqual(parity_gap_demo(k)["linear_d"],1)
        demo=parity_gap_demo()
        self.assertEqual((demo["coordinate_patterns_analytic"],demo["linear_patterns"]),
                         (2097152,2))
        self.assertEqual(solve_ranked([],[],linear=True),())
        self.assertIsNone(solve_ranked([],[(0,1)],linear=True))

    def test_invalid_and_empty(self):
        self.assertEqual(solve([],[]),())
        self.assertIsNone(solve([],[(0,1)]))
        with self.assertRaises(ValueError):
            reduce_3sat([(0,1,2)])
        with self.assertRaises(ValueError):
            solve([(10,15)],[(4,0)])
