import itertools
import json
from pathlib import Path
import random
import tempfile
import unittest

from mathos.research.pnp_structural_kernel import (
    Budget, Exhausted, analyze, brute, decide, duplication_example, eliminate,
    horn_sat, normalize, primal, truth, two_sat, verify_order,
)
from mathos.research.pnp_outcome_registry import OBJECTIVES, decompose
from mathos.research.pnp_outcome_engine import MathOSResearchEngine, main


class TestOutcomeEngine(unittest.TestCase):
    def test_duplication(self):
        r = duplication_example(Budget())
        self.assertEqual((r["raw_original"]["N"], r["raw_duplicated"]["N"]), (92, 176))
        self.assertEqual((r["raw_original"]["gap"], r["raw_duplicated"]["gap"]), (1, 0))
        self.assertEqual(r["normalized"]["beta1"], 21)

    def test_normalization(self):
        n, f, mapping = normalize(9, [[2, 2, -8], [-8, 2], [4, -4], []])
        self.assertEqual((n, f, mapping), (2, ((), (-2, 1)), (2, 8)))
        self.assertEqual(normalize(n, f)[:2], (n, f))
        for raw in ([[0]], [[True]], [[10]]):
            with self.assertRaises(ValueError):
                normalize(9, raw)

    def test_signed_information(self):
        a = analyze(1, [[1]], 1, Budget())
        b = analyze(1, [[-1]], 1, Budget())
        self.assertEqual(a["normalized"], b["normalized"])
        self.assertNotEqual(a["signed_incidence"], b["signed_incidence"])

    def test_replay_and_order(self):
        g = primal(3, [(1, 2), (2, 3)], Budget())
        self.assertEqual(verify_order(g, (1, 2, 3), Budget()), 1)
        self.assertEqual(verify_order(g, (2, 1, 3), Budget()), 2)
        with self.assertRaises(ValueError):
            verify_order(g, (1, 1, 2), Budget())

    def test_special_cases(self):
        self.assertTrue(two_sat(0, (), Budget()))
        self.assertFalse(two_sat(1, [(1,), (-1,)], Budget()))
        self.assertFalse(horn_sat([(1,), (-1, 2), (-2,)], Budget()))
        self.assertTrue(horn_sat([(-1, 2)], Budget()))
        self.assertFalse(eliminate(0, [()], (), Budget()))
        self.assertTrue(eliminate(0, [], (), Budget()))

    def test_randomized_reference(self):
        rng = random.Random(71203)
        for _ in range(240):
            n = rng.randint(0, 6)
            lits = [s*i for i in range(1, n+1) for s in (-1, 1)]
            f = [tuple(rng.choices(lits, k=rng.randint(0, 4))) if n else ()
                 for _ in range(rng.randint(0, 8))]
            nn, normalized, mapping = normalize(n, f)
            expected = brute(n, f, Budget())
            self.assertEqual(brute(nn, normalized, Budget()), expected)
            for a in itertools.product((False, True), repeat=n):
                self.assertEqual(truth(f, a), truth(normalized, tuple(a[i-1] for i in mapping)))
            analysis = analyze(n, f, 1, Budget())
            self.assertEqual(decide(n, f, analysis, Budget())["sat"], expected)
            self.assertEqual(eliminate(nn, normalized, analysis["normalized"]["order"], Budget()), expected)

    def test_random_specialized(self):
        rng = random.Random(412)
        for _ in range(100):
            n = 5
            f = [tuple(rng.choices([-5,-4,-3,-2,-1,1,2,3,4,5], k=2)) for _ in range(8)]
            self.assertEqual(two_sat(n, f, Budget()), brute(n, f, Budget()))
            h = [tuple(-i for i in rng.sample(range(1, 6), 2)) + (rng.randint(1, 5),)
                 for _ in range(6)] + [(1,), (-5,)]
            self.assertEqual(horn_sat(h, Budget()), brute(n, h, Budget()))

    def test_budget_and_checkpoint(self):
        with self.assertRaises(Exhausted):
            eliminate(3, [(1, 2, 3)], (1, 2, 3), Budget(max_cells=2))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "record.json"
            r = MathOSResearchEngine().execute("E01", Budget(max_steps=1),
                n=3, clauses=[[1, 2, 3]], checkpoint_path=p)
            self.assertEqual(r["completion"], "resource_exhausted")
            self.assertFalse(r["p_equals_np_established"])
            self.assertEqual(json.loads(p.read_text())["restart"]["clauses"], [[1, 2, 3]])

    def test_registry_and_governance(self):
        self.assertEqual(len(OBJECTIVES), 20)
        plan = decompose("E01")
        ids = [o["id"] for o in plan["obligations"]]
        self.assertIn("O10", ids)
        for o in plan["obligations"]:
            self.assertTrue(all(ids.index(d) < ids.index(o["id"]) for d in o["dependencies"]))
        for objective in OBJECTIVES:
            r = MathOSResearchEngine().execute(objective, Budget())
            self.assertFalse(r["novel_theorem_verified"])
            self.assertFalse(r["p_equals_np_established"])
            self.assertFalse(r["p_not_equals_np_established"])
            self.assertTrue(all(o["status"] == "unresolved" for o in r["objective"]["obligations"]))
        r = MathOSResearchEngine().execute("E12", Budget())
        self.assertEqual(r["completion"], "verified_finite_limitation")


if __name__ == "__main__":
    unittest.main()
