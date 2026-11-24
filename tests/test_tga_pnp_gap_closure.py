import unittest
from itertools import combinations, product
from mathos.research import tga_pnp_gap_closure as g
from mathos.research.tga_proctor_tree_decomposition import prepare


class TGAGapTests(unittest.TestCase):
    def test_controls(self):
        report = g.controls()
        self.assertEqual(report["cases"], 4418)
        self.assertEqual(report["resolution_status"], "OPEN")
        self.assertEqual(report["proof_obligations"]["status"], "BLOCKED")

    def test_gap_exact_on_small_scope_families(self):
        scopes = tuple(c for k in (1,2,3) for c in combinations(range(1,4), k))
        for mask in range(1, 1 << len(scopes)):
            bags = tuple(b for i, b in enumerate(scopes) if mask >> i & 1)
            edges = tuple(combinations(range(len(bags)), 2))
            best = None
            for candidate in combinations(edges, len(bags)-1):
                # Connected with t-1 distinct edges iff a tree.
                reached = {0}
                while True:
                    enlarged = reached | {v for a,b in candidate
                                           for u,v in ((a,b),(b,a)) if u in reached}
                    if reached == enlarged:
                        break
                    reached = enlarged
                if len(reached) != len(bags):
                    continue
                w = sum(len(set(bags[a]) & set(bags[b])) for a,b in candidate)
                best = w if best is None else max(w,best)
            r = g.topology(bags)
            self.assertEqual(r["overlap_weight"], best)
            try:
                prepare(3, (), bags, r["edges"])
                valid = True
            except ValueError:
                valid = False
            self.assertEqual(valid, r["gap"] == 0)

    def test_same_topology_opposite_decisions(self):
        even, odd = g.parity_cycle(5, False), g.parity_cycle(5, True)
        a, b = g.solve(5, even, 20), g.solve(5, odd, 20)
        self.assertEqual(a["topology"], b["topology"])
        self.assertEqual((a["status"], b["status"]), ("SAT","UNSAT"))
        self.assertTrue(g.verify(5, odd, b))
        self.assertFalse(g.verify(5, even, b))
        self.assertEqual(g.solve(5, odd, 0)["status"], "UNKNOWN")
        self.assertFalse(g.verify(5, odd, g.solve(5, odd, 0)))

    def test_tree_and_tampering(self):
        cs = ((1,1,1),(-1,2,2),(-2,-2,-2),(3,-3,4))
        r = g.solve(4, cs, 0)
        self.assertEqual((r["status"], r["method"]), ("UNSAT","JOIN_TREE"))
        self.assertTrue(g.verify(4, cs, r))
        self.assertFalse(g.verify(4, cs, {**r,"topology":{**r["topology"],"gap":1}}))
        self.assertFalse(g.verify(4, cs, {**r,"evidence":{**r["evidence"],"tables":()}}))

    def test_sparse_and_empty(self):
        n = 2**100
        for cs in ((), ((n,-n,1),), ((n,n,n),(-n,1,1))):
            r = g.solve(n, cs, 0)
            self.assertEqual(r["status"], "SAT")
            self.assertTrue(g.verify(n, cs, r))
        with self.assertRaises(ValueError):
            g.solve(1, ((1,2,1),))
        with self.assertRaises(ValueError):
            g.solve(1, (), -1)


if __name__ == "__main__":
    unittest.main()
