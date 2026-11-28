"""Bounded cross-checks, certificate tampering, and synthesis coverage controls."""
import itertools
import json
from pathlib import Path
import random
import tempfile
import unittest

from mathos.research.pnp_certificate_routes import ROUTES, propose, verify, execute
from mathos.research.pnp_hypothesis_synthesis import (
    controls, covered, evaluate, minimize, select_program, synthesize,
)
from mathos.research.pnp_structural_kernel import Budget, brute, normalize


class TestCertificateRoutes(unittest.TestCase):
    def test_all_binary_formulas_on_two_variables(self):
        choices = [(1,), (-1,), (2,), (-2,)] + [
            tuple(sorted((a, b))) for a, b in itertools.product((1, -1), (2, -2))]
        for mask in range(1 << len(choices)):
            f = [q for i, q in enumerate(choices) if mask & (1 << i)]
            a = propose(2, f, "two_sat", Budget())
            self.assertTrue(verify(2, f, a, Budget()))
            self.assertEqual(a["kind"] == "sat_witness", brute(2, f, Budget()))
        a = propose(2, [()], "two_sat", Budget())
        self.assertEqual(a["kind"], "empty_clause")
        self.assertTrue(verify(2, [()], a, Budget()))

    def test_randomized_reference_and_renamability(self):
        rng = random.Random(5802)
        for _ in range(180):
            n = rng.randrange(7)
            lits = [x for x in range(-n, n+1) if x]
            f = [rng.choices(lits, k=rng.randrange(5)) if lits else []
                 for _ in range(rng.randrange(12))]
            nn, nf, _ = normalize(n, f)
            decision = brute(nn, nf, Budget())
            renamable = any(
                all(sum((x > 0) != flips[abs(x)-1] for x in c) <= 1 for c in nf)
                for flips in itertools.product((False, True), repeat=nn))
            for route in ROUTES:
                a = propose(n, f, route, Budget())
                if route == "two_sat":
                    self.assertEqual(a is not None, all(len(c) <= 2 for c in nf))
                if route == "horn":
                    self.assertEqual(a is not None,
                                     all(sum(x > 0 for x in c) <= 1 for c in nf))
                if route == "renamable_horn":
                    self.assertEqual(a is not None, renamable)
                if route == "bounded_core" and nn <= 5:
                    self.assertEqual(a is not None, not decision)
                if a is not None:
                    self.assertTrue(verify(n, f, a, Budget()))
                    self.assertEqual(a["kind"] == "sat_witness", decision)

    def test_distinct_grammar_controls(self):
        cases = [evaluate(name, n, f, Budget()) for name, n, f in controls()]
        self.assertEqual([e["covered_routes"] for e in cases],
                         [["constant"], ["two_sat"], ["renamable_horn"],
                          ["bounded_core"], []])
        self.assertEqual([e["sat_reference"] for e in cases],
                         [True, False, True, False, True])
        for case in cases[:-1]:
            proof = execute(case["n"], case["clauses"], ROUTES, Budget())
            self.assertIsNotNone(proof)
        self.assertIsNone(execute(cases[-1]["n"], cases[-1]["clauses"], ROUTES, Budget()))

    def test_tampering_rejected(self):
        _, n, f = controls()[1]
        a = propose(n, f, "two_sat", Budget())
        self.assertEqual(a["kind"], "opposing_paths")
        with self.assertRaises(ValueError):
            verify(n, f, {**a, "positive_to_negative": [a["variable"], -a["variable"]]}, Budget())
        with self.assertRaises(ValueError):
            verify(n, f, {**a, "clauses": []}, Budget())
        h = [[1], [-1, 2], [-2]]
        a = propose(2, h, "horn", Budget())
        self.assertEqual(a["kind"], "unit_conflict")
        self.assertTrue(verify(2, h, a, Budget()))
        with self.assertRaises(ValueError):
            verify(2, h, {**a, "trace": []}, Budget())
        with self.assertRaises(ValueError):
            verify(2, h, {**a, "conflict": a["trace"][0]}, Budget())
        _, n, f = controls()[2]
        a = propose(n, f, "renamable_horn", Budget())
        with self.assertRaises(ValueError):
            verify(n, f, {**a, "renaming": [False]*n}, Budget())
        with self.assertRaises(ValueError):
            verify(n, f, {**a, "assignment": [False]*n}, Budget())
        _, n, f = controls()[3]
        a = propose(n, f, "bounded_core", Budget())
        with self.assertRaises(ValueError):
            verify(n, f, {**a, "core": [a["core"][0]]}, Budget())

    def test_json_roundtrip(self):
        for name, n, f in controls()[:-1]:
            e = evaluate(name, n, f, Budget())
            for a in e["certificates"].values():
                self.assertTrue(verify(n, f, json.loads(json.dumps(a)), Budget()))


class TestSynthesis(unittest.TestCase):
    def test_counterexample_guided_search(self):
        r = synthesize(Budget(seconds=30, max_steps=20_000_000), random_cases=8,
                       target={"n": 2, "clauses": [[1], [-2]]})
        self.assertEqual(r["completion"], "finite_synthesis_cycle_completed")
        self.assertEqual(tuple(r["program"]),
                         ("constant", "two_sat", "renamable_horn", "bounded_core"))
        self.assertGreaterEqual(len(r["refinements"]), 3)
        self.assertEqual(r["statistics"]["challenge_program_covered"],
                         r["statistics"]["challenge_grammar_covered"])
        self.assertTrue(r["heldout"])
        self.assertTrue(r["unresolved_examples"])
        self.assertEqual(r["target_result"]["status"], "certificate_replayed")
        self.assertEqual(r["universal_obligation"], "unresolved")
        self.assertFalse(r["novel_theorem_verified"])
        self.assertFalse(r["p_equals_np_established"])
        self.assertFalse(r["p_not_equals_np_established"])
        self.assertEqual(r["formal_verification"], "not_performed")
        for step in r["refinements"]:
            self.assertFalse(covered(step["previous_program"], step["minimized"]["case"]))
            self.assertTrue(covered(step["new_program"], step["minimized"]["case"]))
        self.assertEqual(tuple(r["program"]), select_program(r["training"], Budget()))

    def test_minimization_contract(self):
        # Constant witnesses cannot satisfy two opposing unit requirements;
        # the two-SAT route can. Removing an unrelated clause is harmless.
        e = evaluate("control", 3, [[1], [-2], [1, 3]], Budget())
        r = minimize(e, ("constant",), Budget())
        self.assertEqual(r["remaining_clause_count"], 2)
        self.assertTrue(r["deletion_minimal"])
        self.assertTrue(r["case"]["sat_reference"])
        self.assertFalse(covered(("constant",), r["case"]))
        f = r["case"]["clauses"]
        for i in range(len(f)):
            trial = evaluate("trial", r["case"]["n"], f[:i]+f[i+1:], Budget())
            self.assertTrue(covered(("constant",), trial) or
                            not trial["covered_routes"] or not trial["sat_reference"])
        truncated = minimize(e, ("constant",), Budget(), max_trials=0)
        self.assertFalse(truncated["deletion_minimal"])

    def test_exhaustion_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checkpoint.json"
            r = synthesize(Budget(max_steps=1), random_cases=0, checkpoint_path=path)
            self.assertEqual(r["completion"], "resource_exhausted")
            self.assertEqual(r["universal_obligation"], "unresolved")
            self.assertEqual(json.loads(path.read_text())["completion"], "resource_exhausted")
            self.assertEqual(r["restart"]["random_cases"], 0)


if __name__ == "__main__":
    unittest.main()
