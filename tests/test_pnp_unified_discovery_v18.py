import copy
import unittest
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_adaptive_decision import search
from mathos.research.pnp_unified_discovery_v18 import (
    solve, verify, abstract_verified_tree, check_abstraction, admit_offline)
from mathos.research.pnp_proof_library import Index, reuse

PLAN = ["min_product", 8]
LIB = ({"n": 1, "axioms": ((-1,), (1,)), "steps": ((),), "edges": ()},)


def budget():
    return Budget(seconds=5, max_steps=500_000)


class TestUnifiedDiscovery(unittest.TestCase):
    def test_constructive_first(self):
        f = [(1, 2), (-1, 2)]
        r = solve(2, f, {}, PLAN, LIB)
        self.assertEqual(r["decision"], "sat")
        self.assertEqual([x["route"] for x in r["attempts"]], ["adaptive"])
        self.assertTrue(verify(2, f, {}, PLAN, LIB, r))
        bad = copy.deepcopy(r)
        bad["decision"] = "unsat"
        with self.assertRaises(ValueError):
            verify(2, f, {}, PLAN, LIB, bad)

    def test_large_retrieval_first_and_forged_proof(self):
        f = [(1,), (-1,)] + [(v,) for v in range(2, 21)]
        r = solve(20, f, {}, PLAN, LIB)
        self.assertEqual(r["decision"], "unsat")
        self.assertEqual([x["route"] for x in r["attempts"]], ["library"])
        self.assertTrue(verify(20, f, {}, PLAN, LIB, r))
        bad = copy.deepcopy(r)
        bad["attempts"][0]["payload"]["proof"] = [(1,)]
        with self.assertRaises(ValueError):
            verify(20, f, {}, PLAN, LIB, bad)
        bad = copy.deepcopy(r)
        bad["library_sha256"] = "0"*64
        with self.assertRaises(ValueError):
            verify(20, f, {}, PLAN, LIB, bad)

    def test_retrieval_miss_does_not_claim_unsat(self):
        f = [(v,) for v in range(1, 21)]
        r = solve(20, f, {}, PLAN, LIB)
        self.assertEqual(r["decision"], "sat")
        self.assertEqual([x["route"] for x in r["attempts"]], ["library", "adaptive"])
        self.assertLessEqual(r["work_steps"], r["total_steps"])

    def test_offline_admission(self):
        f = [(1,), (-1, 2), (-2,)]
        raw = search(2, f, budget())
        record = abstract_verified_tree(2, f, raw, budget())
        self.assertTrue(check_abstraction(2, f, record, budget()))
        new = admit_offline((), 2, f, record, budget())
        self.assertEqual(len(new), 1)
        self.assertEqual(len(admit_offline(new, 2, f, record, budget())), 1)
        # Replay on an independently renamed target.
        target = [(3,), (-3, 4), (-4,)]
        self.assertEqual(reuse(4, target, Index(new), budget())["status"], "verified")
        with self.assertRaises(ValueError):
            check_abstraction(2, [(1,)], record, budget())
        with self.assertRaises(ValueError):
            abstract_verified_tree(1, [(1,)], {"decision":"sat", "certificate":[True]}, budget())


if __name__ == "__main__":
    unittest.main()
