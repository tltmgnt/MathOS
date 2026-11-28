import copy
import itertools
import json
import random
import unittest

from mathos.research import pnp_adaptive_decision as adaptive
from mathos.research.pnp_v16_stress import bitset_reference, manifest, reference, chain, limits
from mathos.research.pnp_structural_kernel import Budget, Exhausted
from mathos.research.pnp_unified_portfolio import DEFAULT_PLANS
from mathos.research.pnp_certified_learning import verify_lemma


def budget(steps=100_000):
    return Budget(seconds=5, max_steps=steps, max_cells=200_000)


class StressTests(unittest.TestCase):
    def test_independent_reference(self):
        rng = random.Random(161703)
        for n in range(1, 7):
            for _ in range(30):
                f = [[rng.choice((-1, 1)) * rng.randint(1, n)
                      for _ in range(rng.randrange(5))] for _ in range(rng.randrange(12))]
                expected = any(all(any(a[abs(x)-1] == (x > 0) for x in c) for c in f)
                               for a in itertools.product((False, True), repeat=n))
                self.assertIs(bitset_reference(n, f), expected)
        self.assertTrue(bitset_reference(0, []))
        self.assertFalse(bitset_reference(0, [[]]))

    def test_manifest(self):
        cases = manifest()
        self.assertEqual(len(cases), 54)
        self.assertEqual(len({c["id"] for c in cases}), 54)
        self.assertEqual(manifest(), cases)
        for case in cases:
            self.assertIs(type(reference(case)), bool)
        bad = copy.deepcopy(next(c for c in cases if c["kind"] == "pigeon"))
        bad["clauses"].pop()
        with self.assertRaises(ValueError):
            reference(bad)

    def test_budget_ablation(self):
        self.assertEqual(limits("v12_third", []), (33333, 5/3))
        self.assertEqual(limits("search_initial", []), (50000, 2.5))
        self.assertEqual(limits("search_initial", chain(65, False)), (5000, .25))
        self.assertEqual(limits("search_full", []), (100000, 5))

    def test_real_fallback_after_search_exhaustion(self):
        # Real certified two-SAT route, not a mocked decision. This policy
        # is intentionally a test fixture, not a fitted benchmark policy.
        plans = [("none", "two_sat")] + [p for p in DEFAULT_PLANS if p != ("none", "two_sat")]
        policy = {"order": [{"plan": list(p), "suggested_cap": 50000} for p in plans]}
        plan = ["min_product", 8]
        for bad in (False, True):
            f = chain(65, bad)
            r = adaptive.solve(65, f, policy, plan)
            self.assertEqual(r["attempts"][0]["status"], "resource_exhausted")
            self.assertEqual(r["attempts"][1]["stage"], "fallback")
            self.assertEqual(r["attempts"][1]["status"], "replayed")
            self.assertEqual(r["decision"], "unsat" if bad else "sat")
            adaptive.verify_report(65, f, policy, plan, json.loads(json.dumps(r)))
            forged = copy.deepcopy(r)
            forged["attempts"][1]["payload"]["decision"] = "unknown"
            with self.assertRaises(ValueError):
                adaptive.verify_report(65, f, policy, plan, forged)

    def test_real_learning_and_compact_resolution(self):
        f = [(1, 2), (1, -2)]
        plan = ["min_product", 8]
        p = adaptive._learn_attempt(2, f, plan, budget())
        self.assertEqual(p["lemma"]["clause"], [1])
        self.assertEqual(verify_lemma(2, f, p["lemma"], budget()), (1,))
        bad = copy.deepcopy(p["lemma"])
        bad["clause"] = [-1]
        with self.assertRaises(ValueError):
            verify_lemma(2, f, bad, budget())
        g = [(1,), (-1,)]
        q = adaptive._resolution_attempt(1, g, plan, budget())
        self.assertEqual(q["decision"], "unsat")
        self.assertIsNotNone(q["compact"])
        c = q["compact"]
        adaptive.abstraction.verify_embedding(1, g, c["template"], c["source_embedding"], budget())
        with self.assertRaises(ValueError):
            adaptive.abstraction.verify_embedding(1, [(1,)], c["template"], c["source_embedding"], budget())


if __name__ == "__main__":
    unittest.main()
