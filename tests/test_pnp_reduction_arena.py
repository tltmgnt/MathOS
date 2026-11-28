import random
import unittest
from mathos.research.pnp_structural_kernel import Budget, brute
from mathos.research.pnp_reduction_portfolio import PROFILES, reduce_cnf, verify_reduction
from mathos.research.pnp_reduction_arena import family_evidence, research
from mathos.research.pnp_semantic_escape import propose, verify


class TestReductionArena(unittest.TestCase):
    def test_rule_traces(self):
        cases = [
            ([[1], [-1, 2]], "unit", 4, "unit"),
            ([[1, 2], [1, -2]], "simplify", 4, "pure"),
            ([[1, 2], [1, 2, 3], [-1, -2, -3], [1, -3]], "simplify", 4, "subsumption"),
            ([[1, 2], [-1, 3], [-2, -3]], "bounded_resolution", 4, "resolve"),
        ]
        for f, profile, cap, rule in cases:
            a = reduce_cnf(3, f, Budget(), profile=profile, cap=cap)
            self.assertIn(rule, [x["rule"] for x in a["steps"]])
            self.assertTrue(verify_reduction(3, f, a, Budget()))
            self.assertEqual(brute(3, f, Budget()), brute(a["n"], a["clauses"], Budget()))

    def test_forged_certificates(self):
        f = [[1, 2], [-1, -2]]
        a = reduce_cnf(2, f, Budget())
        for step in ({"rule": "unit", "literal": 1}, {"rule": "pure", "literal": 1},
                     {"rule": "subsumption", "witness": [1,2], "remove": [-1,-2]},
                     {"rule": "resolve", "variable": 3}):
            with self.assertRaises(ValueError):
                verify_reduction(2, f, {**a, "steps": [step]}, Budget())
        with self.assertRaises(ValueError):
            verify_reduction(2, f, {**a, "n": 9}, Budget())
        with self.assertRaises(ValueError):
            verify_reduction(2, f, {**a, "neighbor_cap": 0}, Budget())

    def test_random_reference(self):
        rng = random.Random(882)
        for _ in range(180):
            n = rng.randrange(7)
            lits = [i for i in range(-n, n+1) if i]
            f = [rng.choices(lits, k=rng.randrange(4)) if lits else []
                 for _ in range(rng.randrange(12))]
            expected = brute(n, f, Budget())
            for profile in PROFILES:
                a = reduce_cnf(n, f, Budget(), profile=profile)
                self.assertTrue(verify_reduction(n, f, a, Budget()))
                self.assertEqual(brute(a["n"], a["clauses"], Budget()), expected)

    def test_restricted_obstruction(self):
        result = family_evidence(16, 4, 1, Budget(seconds=20, max_steps=10_000_000))
        self.assertEqual([x["decision"]["sat"] for x in result], [True, False])
        for x in result:
            self.assertTrue(x["all_rules_blocked"])
            self.assertTrue(x["unchanged"])
            self.assertEqual((x["bounds"]["lower"], x["bounds"]["upper"]), (15, 15))
            self.assertTrue(x["bounds"]["obstructed_current_graph"])
            self.assertEqual(x["semantic_escape"]["bounds"]["upper"], 0)
            self.assertTrue(x["semantic_escape"]["certificate_replayed"])

    def test_escape_certificates(self):
        f = [[1, 2], [-1, 2]]
        a = propose(2, f, Budget())
        self.assertTrue(verify(2, f, a, Budget()))
        with self.assertRaises(ValueError):
            verify(2, f, {**a, "assignment": [False, False]}, Budget())
        with self.assertRaises(ValueError):
            verify(2, f, {"kind":"unsat_core", "core": [[1,2]], "n":0,
                          "clauses":[[]]}, Budget())
        self.assertIsNone(propose(2, [[1], [-2]], Budget()))

    def test_end_to_end(self):
        r = research(3, [[1,2], [-1,3], [-2,-3]], Budget(seconds=20, max_steps=10_000_000))
        self.assertEqual(r["completion"], "scoped_research_cycle_completed")
        self.assertEqual(len(r["portfolio"]), 3)
        self.assertTrue(all(h["status"] == "refuted_by_replayed_instance" for h in r["hypotheses"]))
        self.assertEqual(r["universal_obligation"], "unresolved")
        self.assertFalse(r["p_equals_np_established"])
        self.assertFalse(r["p_not_equals_np_established"])

    def test_resource_exhaustion(self):
        r = research(3, [[1,2,3]], Budget(max_steps=1))
        self.assertEqual(r["completion"], "resource_exhausted")
        self.assertEqual(r["hypotheses"], [])


if __name__ == "__main__":
    unittest.main()
