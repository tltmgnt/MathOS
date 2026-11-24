import unittest
from itertools import product
from unittest.mock import patch

from mathos.research import tga_proctor_component_search as c


class ComponentSearchTests(unittest.TestCase):
    def test_controls(self):
        r = c.controls()
        self.assertEqual(r["cases"], 600)
        self.assertEqual(r["unknown"], 600)
        self.assertEqual(r["sat"] + r["unsat"], 600)
        self.assertFalse(r["original_scratch_port"])

    def test_empty_and_sparse_union(self):
        n = 2**100
        for cs in ((), ((n,), (-1,), (n-1, n-1))):
            r = c.solve(n, cs, 4)
            self.assertEqual(r["status"], "SAT")
            self.assertTrue(c.verify(n, cs, r))
        cs = ((n,), (), (-1,))
        r = c.solve(n, cs, 1)
        self.assertEqual(r["status"], "UNSAT")
        self.assertTrue(c.verify(n, cs, r))
        self.assertFalse(c.verify(n, cs, {**r, "certificate": ("empty", 0)}))
        self.assertFalse(c.verify(n, cs, {**r, "certificate": ("empty", True)}))

    def test_global_budget(self):
        cs = ((1,), (2,), (3,))
        for limit in (0, 1, 2):
            r = c.solve(3, cs, limit)
            self.assertEqual(r["status"], "UNKNOWN")
            self.assertLessEqual(r["nodes"], limit)
            self.assertFalse(c.verify(3, cs, r))
        r = c.solve(3, cs, 3)
        self.assertEqual(r["status"], "SAT")
        self.assertEqual(r["nodes"], 3)
        self.assertTrue(c.verify(3, cs, r))
        self.assertFalse(c.verify(3, cs, {**r, "witness": (True, True, False)}))

    def test_refutation_replay_without_partition(self):
        core = tuple(tuple(s*(i+2) for i, s in enumerate(signs))
                     for signs in product((-1, 1), repeat=3))
        cs = ((1,),) + core
        r = c.solve(4, cs, 64)
        self.assertEqual(r["status"], "UNSAT")
        tag, indices, proof = r["certificate"]
        self.assertEqual(tag, "subset")
        with patch.object(c, "partition", side_effect=AssertionError("no partition")):
            self.assertTrue(c.verify(4, cs, r))
            for changed in (("subset", (), proof), ("subset", indices[::-1], proof),
                            ("subset", indices+(indices[-1],), proof),
                            ("subset", (99,), proof),
                            ("subset", indices, {**proof, "tree": ()}),
                            ("subset", indices, {**proof, "status": "SAT"})):
                self.assertFalse(c.verify(4, cs, {**r, "certificate": changed}))

    def test_guarded_connected_root_obstruction(self):
        for t in (1, 2, 3):
            n, cs = c.guarded_root_obstruction(t)
            self.assertEqual(len(cs), 25*t+9)
            self.assertEqual(n, 4*t+4)
            self.assertTrue(all(not any(-l in row for l in row) for row in cs))
            r = c.solve(n, cs, 2**t-1)
            self.assertEqual(r["components"], 1)
            self.assertEqual(r["status"], "UNKNOWN")
            self.assertFalse(c.verify(n, cs, r))

    def test_invalid_inputs(self):
        for cs in (((0,),), ((True,),), ((1, 1, 1, 1),), ((), (3,))):
            with self.assertRaises(ValueError):
                c.solve(2, cs)
        for limit in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                c.solve(2, (), limit)


if __name__ == "__main__":
    unittest.main()
