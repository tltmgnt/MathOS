import copy
import itertools
import json
import random
import unittest

from mathos.research.pnp_adaptive_decision import search, verify_search, quota, solve, verify_report
from mathos.research.pnp_structural_kernel import Budget, Exhausted
from mathos.research.pnp_evidence_scheduler import _fit
from mathos.research.pnp_unified_portfolio import DEFAULT_PLANS


def budget(steps=100_000):
    return Budget(seconds=5, max_steps=steps)


class AdaptiveDecisionTests(unittest.TestCase):
    def test_exhaustive_two_variables(self):
        clauses = [(), (1,), (-1,), (2,), (-2,), (1, 2), (-1, 2), (1, -2), (-1, -2)]
        for mask in range(1 << len(clauses)):
            f = [c for i, c in enumerate(clauses) if mask & (1 << i)]
            r = search(2, f, budget())
            self.assertTrue(verify_search(2, f, json.loads(json.dumps(r)), budget()))
            expected = any(all(any(a[abs(x)-1] == (x > 0) for x in c) for c in f)
                           for a in itertools.product((False, True), repeat=2))
            self.assertEqual(r["decision"], "sat" if expected else "unsat")

    def test_random_and_signed_redundancy(self):
        rng = random.Random(16029)
        for _ in range(100):
            f = [tuple(rng.choice((-1, 1)) * rng.randint(1, 5) for _ in range(rng.randint(0, 4))) for _ in range(12)]
            r = search(5, f, budget())
            verify_search(5, f, r, budget())
            expected = any(all(any(a[abs(x)-1] == (x > 0) for x in c) for c in f)
                           for a in itertools.product((False, True), repeat=5))
            self.assertEqual(r["decision"], "sat" if expected else "unsat")

    def test_forged_certificates(self):
        for f, result in [
            ([(1,)], {"decision": "sat", "certificate": [False]}),
            ([(1,)], {"decision": "sat", "certificate": [1]}),
            ([(1,)], {"decision": "unsat", "certificate": ["leaf", 0]}),
            ([(1,), (-1,)], {"decision": "unsat", "certificate": ["split", 1, ["leaf", 0], ["leaf", 0]]}),
            ([(1,), (-1,)], {"decision": "unsat", "certificate": ["split", True, ["leaf", 0], ["leaf", 1]]}),
            ([(1,), (-1,)], {"decision": "unsat", "certificate": ["split", 1, ["leaf", 0]]}),
        ]:
            with self.assertRaises(ValueError):
                verify_search(1, f, result, budget())

    def test_budget_and_borrowing(self):
        with self.assertRaises(Exhausted):
            search(2, [(1, 2)], budget(1))
        self.assertEqual(quota("search", 100, 0, (9, True)), 50)
        self.assertEqual(quota("fallback", 100, 5, (9, False)), 95)
        self.assertEqual(quota("resolution", 100, 80, (9, True)), 13)

    def test_end_to_end_and_tampering(self):
        policy = {"order": [{"plan": list(p), "suggested_cap": 100} for p in DEFAULT_PLANS]}
        plan = ["min_product", 8]
        for f in ([(1,), (-1,)], [(1, 2)], [], [()]):
            r = solve(2, f, policy, plan, total=1000)
            self.assertNotEqual(r["decision"], "unknown")
            self.assertTrue(verify_report(2, f, policy, plan, json.loads(json.dumps(r))))
            bad = copy.deepcopy(r)
            bad["work_steps"] += 1
            with self.assertRaises(ValueError):
                verify_report(2, f, policy, plan, bad)
            bad = copy.deepcopy(r)
            bad["decision"] = "unsat" if r["decision"] == "sat" else "sat"
            with self.assertRaises(ValueError):
                verify_report(2, f, policy, plan, bad)
        r = solve(2, [(1, 2)], policy, plan, total=1)
        self.assertEqual(r["decision"], "unknown")
        verify_report(2, [(1, 2)], policy, plan, r)


if __name__ == "__main__":
    unittest.main()
