import unittest
from itertools import combinations, product
from mathos.research import tga_proctor_resolution_gates as g
from mathos.research import tga_proctor_affine_backdoor as f27


class ResolutionTests(unittest.TestCase):
    def test_exhaustive_controls(self):
        report = g.controls()
        self.assertEqual(report["cases"], 4162)
        self.assertGreater(report["unsat"], 0)
        self.assertEqual(report["sat"] + report["unsat"], report["cases"])
        self.assertFalse(report["universal_bound"])

    def test_dense_positive_is_dual_horn(self):
        cs = tuple(combinations(range(1, 13), 3))
        self.assertEqual(len(f27.plan(12, cs)[2]), 11)
        r = g.solve(12, cs, branch_limit=1)
        self.assertEqual((r["status"], r["cover"], r["polarity"]), ("SAT", (), -1))
        self.assertTrue(g.verify(12, cs, r))

    def test_horn_chain_and_conflict(self):
        cs = ((1, 1, 1), (-1, 2, 2), (-2, 3, 3), (-3, -3, -3))
        r = g.solve(3, cs, branch_limit=1)
        self.assertEqual((r["status"], r["cover"]), ("UNSAT", ()))
        self.assertTrue(g.verify(3, cs, r))
        for traces in ((), ((3,),), ((0, 1, 2),), ((0, 0, 3),), ((0, 1, 2, -1),)):
            self.assertFalse(g.verify(3, cs, {**r, "traces": traces}))

    def test_every_branch_required(self):
        cs = tuple(tuple(s*(i+1) for i, s in enumerate(signs))
                   for signs in product((-1, 1), repeat=3))
        r = g.solve(3, cs, branch_limit=8)
        self.assertEqual(r["status"], "UNSAT")
        self.assertGreater(len(r["traces"]), 1)
        self.assertTrue(g.verify(3, cs, r))
        self.assertFalse(g.verify(3, cs, {**r, "traces": r["traces"][:-1]}))
        short = g.solve(3, cs, branch_limit=1)
        self.assertEqual(short["status"], "UNKNOWN")
        self.assertFalse(g.verify(3, cs, short))

    def test_budget_and_input(self):
        r = g.solve(0, (), branch_limit=0)
        self.assertEqual(r["status"], "UNKNOWN")
        self.assertFalse(g.verify(0, (), r))
        self.assertEqual(g.solve(0, (), branch_limit=1)["status"], "SAT")
        for budget in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                g.solve(0, (), branch_limit=budget)
        with self.assertRaises(ValueError):
            g.solve(1, ((1, 0, 1),))

    def test_both_polarities_obstructed(self):
        n, cs = g.obstruction(6)
        _, rows, cover, _, _ = g.plan(n, cs)
        self.assertGreaterEqual(len(cover), 5)
        self.assertEqual(len(g.polarity_edges(rows, 1)), 15)
        self.assertEqual(len(g.polarity_edges(rows, -1)), 15)
        self.assertEqual(g.solve(n, cs, branch_limit=0)["status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
