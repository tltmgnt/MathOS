import unittest
from itertools import combinations, product
from mathos.research import tga_proctor_adaptive_propagation as a
from mathos.research.tga_proctor_affine_backdoor import compress
from mathos.research.tga_proctor_renamable_horn import recognize, obstruction as prior


class AdaptiveTests(unittest.TestCase):
    def test_controls(self):
        report = a.controls()
        self.assertEqual(report["cases"], 4418)
        self.assertGreater(report["unsat"], 0)
        self.assertFalse(report["universal_bound"])

    def test_prior_family_one_node(self):
        n, cs = prior(32)
        r = a.solve(n, cs, 1)
        self.assertEqual((r["status"], r["nodes"], r["splits"]), ("SAT", 1, 0))
        self.assertTrue(a.verify(n, cs, r))

    def test_unit_conflict_and_bad_certificate(self):
        cs = ((1, 1, 1), (-1, -1, -1))
        r = a.solve(1, cs, 1)
        self.assertEqual(r["status"], "UNSAT")
        self.assertTrue(a.verify(1, cs, r))
        self.assertFalse(a.verify(1, cs, {**r, "tree": (((("unit", -1, 0),), ("conflict", 1)),)}))
        self.assertFalse(a.verify(1, cs, {**r, "tree": ()}))
        self.assertFalse(a.verify(1, cs, {**r, "tree": r["tree"] * 2}))

    def test_branch_completeness_and_pure_replay(self):
        core = tuple(tuple(s*(i+1) for i, s in enumerate(signs))
                     for signs in product((-1, 1), repeat=3))
        cs = core + ((4, 5, 5),)
        r = a.solve(5, cs, 31)
        self.assertEqual(r["status"], "UNSAT")
        self.assertTrue(a.verify(5, cs, r))
        events, terminal = r["tree"][0]
        self.assertEqual(events[0], ("pure", 4, None))
        self.assertEqual(terminal[0], "split")
        self.assertFalse(a.verify(5, cs, {**r, "tree": r["tree"][:-1]}))
        wrong = (((("pure", -4, None),), terminal),) + r["tree"][1:]
        self.assertFalse(a.verify(5, cs, {**r, "tree": wrong}))
        short = a.solve(5, cs, 1)
        self.assertEqual(short["status"], "UNKNOWN")
        self.assertFalse(a.verify(5, cs, short))

    def test_static_minimum_small(self):
        for t in (1, 2):
            n, cs = a.obstruction(t)
            _, rows, _ = compress(n, cs)
            k = min(k for k in range(n+1)
                    if any(recognize(n, rows, b)[0] is not None
                           for b in combinations(range(1, n+1), k)))
            self.assertEqual(k, 2*t)

    def test_exponential_search_family(self):
        for t in (1, 2, 3):
            n, cs = a.search_obstruction(t)
            r = a.solve(n, cs, 100000)
            self.assertEqual(r["status"], "UNSAT")
            self.assertGreaterEqual(r["nodes"], 2**t)
            self.assertTrue(a.verify(n, cs, r))
            limited = a.solve(n, cs, 2**t-1)
            self.assertEqual(limited["status"], "UNKNOWN")

    def test_sparse_input_and_budgets(self):
        n = 2**100
        cs = ((n, n, n), (1, -n, 1))
        r = a.solve(n, cs, 1)
        self.assertEqual(r["ids"], (1, n))
        self.assertEqual(r["witness"], (True, True))
        self.assertTrue(a.verify(n, cs, r))
        self.assertFalse(a.verify(n, cs, {**r, "ids": (1, n-1)}))
        self.assertEqual(a.solve(n, (), 0)["status"], "UNKNOWN")
        for b in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                a.solve(0, (), b)


if __name__ == "__main__":
    unittest.main()
