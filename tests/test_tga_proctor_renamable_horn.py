import unittest
from itertools import product, combinations
from mathos.research import tga_proctor_renamable_horn as r
from mathos.research.tga_proctor_affine_backdoor import compress
from mathos.research.tga_proctor_resolution_gates import obstruction as prior
from mathos.research.tga_proctor_unrestricted_scope import evaluate


class RenamableTests(unittest.TestCase):
    def test_controls(self):
        report = r.controls()
        self.assertEqual(report["cases"], 4162)
        self.assertEqual(report["recognition_checks"], 16645)
        self.assertGreater(report["unsat"], 0)

    def test_global_obstruction(self):
        n, cs = prior(6)
        result = r.solve(n, cs, 1)
        self.assertEqual((result["status"], result["cover"]), ("SAT", ()))
        self.assertTrue(r.verify(n, cs, result))

    def test_exact_minimum_small(self):
        for t in range(1, 4):
            n, cs = r.obstruction(t)
            _, rows, _ = compress(n, cs)
            optimum = min(k for k in range(n+1)
                          if any(r.recognize(n, rows, b)[0] is not None
                                 for b in combinations(range(1, n+1), k)))
            self.assertEqual(optimum, t)

    def test_full_sign_unsat_and_replay(self):
        cs = tuple(tuple(s*(i+1) for i, s in enumerate(signs))
                   for signs in product((-1, 1), repeat=3))
        result = r.solve(3, cs, 8)
        self.assertEqual(result["status"], "UNSAT")
        self.assertTrue(r.verify(3, cs, result))
        for bad in ({**result, "traces": result["traces"][:-1]},
                    {**result, "flips": (0,)},
                    {**result, "flips": (1, 1)},
                    {**result, "traces": ((-1,),) + result["traces"][1:]}):
            self.assertFalse(r.verify(3, cs, bad))
        self.assertEqual(r.solve(3, cs, 1)["status"], "UNKNOWN")

    def test_three_variable_recognition(self):
        cs = tuple(tuple(s*(i+1) for i, s in enumerate(signs))
                   for signs in product((-1, 1), repeat=3))
        for mask in range(256):
            _, rows, _ = compress(3, tuple(c for i,c in enumerate(cs) if mask >> i & 1))
            flips, _ = r.recognize(3, rows)
            brute = any(r.valid_plan(rows, (), tuple(v for v in range(1,4)
                        if flags[v-1])) for flags in product((False, True), repeat=3))
            self.assertEqual(flips is not None, brute)

    def test_sparse_and_validation(self):
        n = 2**100
        ids, cs = r.sparse_input(n, ((1, -n, n-1), (-1, -1, -1)))
        self.assertEqual(ids, (1, n-1, n))
        self.assertEqual(cs, ((1, -3, 2), (-1, -1, -1)))
        result = r.solve(len(ids), cs, 8)
        self.assertEqual(result["status"], "SAT")
        self.assertTrue(evaluate(cs, result["witness"]))
        self.assertEqual(r.sparse_input(n, ()), ((), ()))
        for bad in ((n, ((0,1,1),)), (-1, ()), (n, ((True,1,1),))):
            with self.assertRaises(ValueError):
                r.sparse_input(*bad)
        self.assertEqual(r.solve(0, (), 0)["status"], "UNKNOWN")
        self.assertFalse(r.verify(0, (), r.solve(0, (), 0)))


if __name__ == "__main__":
    unittest.main()
