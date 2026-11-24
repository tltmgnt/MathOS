import unittest
from itertools import product
from unittest.mock import patch

from mathos.research import tga_proctor_dynamic_components as d
from mathos.research import tga_proctor_component_search as root


class DynamicComponentsTests(unittest.TestCase):
    def test_controls(self):
        r = d.controls()
        self.assertEqual(r["cases"], 800)
        self.assertEqual(r["zero_budget"], 800)
        self.assertEqual(r["sat"] + r["unsat"], 800)

    def test_guarded_budget_and_tamper(self):
        n, cs = root.guarded_root_obstruction(4)
        r = d.solve(n, cs, 8)
        self.assertEqual(r["status"], "UNSAT")
        self.assertEqual(r["nodes"], 8)
        self.assertEqual(d.solve(n, cs, 7)["status"], "UNKNOWN")
        tree = r["tree"]
        events, terminal = tree[0]
        self.assertEqual(terminal[0], "subset")
        self.assertEqual(events[0][0], "unit")
        with patch.object(d, "partition", side_effect=AssertionError("no partition")), \
             patch.object(d, "recognize", side_effect=AssertionError("no recognition")):
            self.assertTrue(d.verify(n, cs, r))
            for bad in (tree[:-1], tree+tree,
                        (((("unit", -events[0][1], events[0][2]),), terminal),)+tree[1:],
                        ((events, ("subset", (999999,))),)+tree[1:],
                        ((events, ("subset", ())),)+tree[1:],
                        ((events, ("subset", terminal[1][::-1])),)+tree[1:]):
                self.assertFalse(d.verify(n, cs, {**r, "tree": bad}))

    def test_sat_union_and_sparse(self):
        n = 2**100
        cs = ((n,), (n, 1, 2), (-1, -2), (1, 2), (n, 3, 4), (3, 4), (-3, -4))
        r = d.solve(n, cs, 100)
        self.assertEqual(r["status"], "SAT")
        self.assertGreater(r["decomposition_nodes"], 0)
        self.assertTrue(d.verify(n, cs, r))
        self.assertFalse(d.verify(n, cs, {**r, "witness": (False,)*len(r["ids"])}))

    def test_mixed_connected_decisions(self):
        cs = ((1, 2, 3), (-1, 2, 3), (1, -2, -3), (-1, -2, -3),
              (2, -3, 4), (-2, 3, -4), (4, 5, 6), (-4, -5, -6))
        for cs2 in (cs, cs+((5,), (-5,))):
            r = d.solve(6, cs2, 1000)
            expected = any(root._holds(cs2, dict(zip(range(1, 7), bits)))
                           for bits in product((False, True), repeat=6))
            self.assertEqual(r["status"], "SAT" if expected else "UNSAT")
            self.assertTrue(d.verify(6, cs2, r))

    def test_split_then_decompose(self):
        # Two contradictory cores. Variable 7 has 15 occurrences,
        # each core variable has 13. First branch sets 7 true and
        # removes all cross-core clauses; remaining pairs are local.
        from itertools import combinations
        cs = tuple(tuple(s*v for s, v in zip(signs, block))
                   for block in ((1, 2, 3), (4, 5, 6))
                   for signs in product((-1, 1), repeat=3))
        cs += tuple((7, a, b) for a in (1, 2, 3) for b in (4, 5, 6))
        cs += tuple((-7, a, b) for block in ((1, 2, 3), (4, 5, 6))
                    for a, b in combinations(block, 2))
        r = d.solve(7, cs, 1000)
        self.assertEqual(r["status"], "UNSAT")
        self.assertEqual(r["tree"][0][1], ("split", 7, True))
        self.assertEqual(r["tree"][1][1][0], "subset")
        self.assertGreater(r["decomposition_nodes"], 0)
        self.assertTrue(d.verify(7, cs, r))

    def test_empty_and_invalid(self):
        self.assertTrue(d.verify(0, (), d.solve(0, ())))
        self.assertTrue(d.verify(0, ((),), d.solve(0, ((),))))
        self.assertFalse(d.verify(0, (), d.solve(0, (), 0)))
        for cs in (((0,),), ((True,),), ((1, 1, 1, 1),)):
            with self.assertRaises(ValueError):
                d.solve(1, cs)


if __name__ == "__main__":
    unittest.main()
