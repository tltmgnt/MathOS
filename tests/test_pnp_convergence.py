import itertools
import random
import unittest

from mathos.research.pnp_structural_kernel import Budget, Exhausted, brute, primal, verify_order
from mathos.research.pnp_dual_bounds import converge, verify_bounds, verify_lower, threshold_search
from mathos.research.pnp_transformation_agent import unit_transform, verify_transform
from mathos.research.pnp_convergence import research, adversarial_arena
from mathos.research.pnp_convergence_dashboard import render_report


def graph(n, edges):
    g = {i: set() for i in range(1, n+1)}
    for u, v in edges:
        g[u].add(v)
        g[v].add(u)
    return g


class TestConvergence(unittest.TestCase):
    def test_known_graphs(self):
        cases = [(graph(0, []), 0), (graph(5, []), 0),
                 (graph(5, [(1, i) for i in range(2, 6)]), 1),
                 (graph(5, [(i, i+1) for i in range(1, 5)] + [(1, 5)]), 2),
                 (graph(5, itertools.combinations(range(1, 6), 2)), 4),
                 (graph(6, itertools.product(range(1, 4), range(4, 7))), 3)]
        for g, expected in cases:
            r = converge(g, Budget())
            self.assertTrue(r["exact"])
            self.assertEqual(r["lower"], expected)
            self.assertTrue(verify_bounds(g, r, Budget()))

    def test_minor_replay(self):
        g = graph(4, [(1, 2), (2, 3), (3, 4), (4, 1)])
        cert = {"kind": "clique_minor", "branches": [[1, 2], [3], [4]]}
        self.assertEqual(verify_lower(g, cert, Budget()), 2)
        for branches in ([[1, 3], [2], [4]], [[1, 2], [2], [4]], [[1], [3]]):
            with self.assertRaises(ValueError):
                verify_lower(g, {"kind": "clique_minor", "branches": branches}, Budget())

    def test_frontier_replay(self):
        g = graph(4, [(1, 2), (2, 3), (3, 1), (3, 4)])
        cert = threshold_search(g, 1, Budget())
        self.assertEqual(cert["kind"], "closed_frontier")
        self.assertEqual(verify_lower(g, cert, Budget()), 2)
        cert["states"] = [0]
        with self.assertRaises(ValueError):
            verify_lower(g, cert, Budget())
        found = threshold_search(g, 2, Budget())
        self.assertLessEqual(verify_order(g, found["order"], Budget()), 2)

    def test_random_graphs_against_all_orders(self):
        rng = random.Random(712)
        for n in range(1, 7):
            for _ in range(8):
                g = graph(n, [e for e in itertools.combinations(range(1, n+1), 2) if rng.random() < .45])
                b = Budget(max_steps=10_000_000)
                true = min(verify_order(g, order, b) for order in itertools.permutations(g))
                r = converge(g, Budget())
                self.assertEqual((r["lower"], r["upper"]), (true, true))
                self.assertTrue(verify_bounds(g, r, Budget()))
                for k in range(n):
                    cert = threshold_search(g, k, Budget())
                    if true <= k:
                        self.assertEqual(cert["kind"], "order")
                        self.assertLessEqual(verify_order(g, cert["order"], Budget()), k)
                    else:
                        self.assertEqual(verify_lower(g, cert, Budget()), k+1)

    def test_resource_safety(self):
        g = graph(5, itertools.combinations(range(1, 6), 2))
        r = converge(g, Budget(max_steps=1))
        self.assertIsNone(r["upper"])
        self.assertFalse(r["exact"])
        with self.assertRaises(Exhausted):
            threshold_search(g, 2, Budget(max_cells=1))

    def test_unit_transform(self):
        f = [[1], [-1, 2], [-2, 3, 4], [3, -4]]
        r = unit_transform(4, f, Budget())
        self.assertTrue(verify_transform(4, f, r, Budget()))
        self.assertEqual(r["forced_original_literals"], (1, 2))
        self.assertEqual(r["new_to_old"], (3, 4))
        with self.assertRaises(ValueError):
            verify_transform(4, f, {**r, "units": [2, 1]}, Budget())
        with self.assertRaises(ValueError):
            verify_transform(4, f, {**r, "clauses": []}, Budget())

    def test_random_transformations(self):
        rng = random.Random(42)
        for _ in range(100):
            n = 5
            f = [rng.choices([-5,-4,-3,-2,-1,1,2,3,4,5], k=rng.randrange(4))
                 for _ in range(rng.randrange(8))]
            r = unit_transform(n, f, Budget())
            self.assertTrue(verify_transform(n, f, r, Budget()))
            self.assertEqual(brute(n, f, Budget()), brute(r["n"], r["clauses"], Budget()))

    def test_arena_and_governance(self):
        a = adversarial_arena(Budget())
        self.assertEqual(a["sat"], [True, False])
        self.assertEqual(a["bounds"]["gap"], 0)
        r = research(3, [[1], [-1, 2, 3]], Budget(), arena=True)
        self.assertEqual(r["completion"], "scoped_structural_convergence")
        self.assertEqual(r["universal_obligation"], "unresolved")
        self.assertFalse(r["p_equals_np_established"])
        self.assertFalse(r["p_not_equals_np_established"])
        self.assertTrue(all(o["status"] == "unresolved" for p in r["plans"] for o in p["obligations"]))
        self.assertEqual(r["formal_verification"], "not_performed")

    def test_dashboard(self):
        r = research(2, [[1, 2]], Budget())
        r["completion"] = "<script>alert(1)</script>"
        html = render_report(r)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertIn("Universal P versus NP obligation remains unresolved", html)

    def test_interrupted_research(self):
        r = research(3, [[1, 2, 3]], Budget(max_steps=1))
        self.assertEqual(r["completion"], "resource_exhausted")
        self.assertFalse(r["p_equals_np_established"])
        self.assertEqual(r["universal_obligation"], "unresolved")


if __name__ == "__main__":
    unittest.main()
