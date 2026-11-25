import copy
import random
import unittest

from mathos.proof_analysis.gap_analysis import Claim, analyze, analyze_legacy, models
from mathos.proof_analysis.certification_audit import exhaustive_check
from mathos.proof_analysis.tga_engine import Limits, ResourceLimitError, minimal_blockers, solve
from mathos.proof_analysis.tga_level6 import digest, report, replay


class ExactTGATests(unittest.TestCase):
    def test_random_differential_and_truth_table(self):
        rng = random.Random(406)
        for _ in range(250):
            g = {f"x{i}": Claim(f"x{i}", "open") for i in range(rng.randint(1, 6))}
            g["e"] = Claim("e", "established_external")
            for i in range(rng.randint(1, 8)):
                routes = tuple(tuple(rng.choices(list(g), k=rng.randint(1, 4)))
                               for _ in range(rng.randint(1, 4)))
                target = f"d{i}"
                g[target] = Claim(target, "derived", routes)
            r = analyze(g, target)
            self.assertEqual(r, analyze_legacy(g, target))
            exhaustive_check(g, target, r["minimal_completion_sets"])

    def test_deep_chain_and_dominated_routes(self):
        g = {"x": Claim("x", "open")}
        for i in range(2000):
            parent = "x" if i == 0 else f"n{i-1}"
            g[f"n{i}"] = Claim(str(i), "derived", ((parent,),))
        self.assertEqual(analyze(g, "n1999")["minimal_completion_sets"], [["x"]])
        g = {k: Claim(k, "open") for k in ["x"] + [f"y{i}" for i in range(20)]}
        for i in range(20):
            g[f"c{i}"] = Claim(str(i), "derived", (("x",), ("x", f"y{i}")))
        g["t"] = Claim("t", "derived", (tuple(f"c{i}" for i in range(20)),))
        self.assertEqual(analyze(g, "t")["minimal_completion_sets"], [["x"]])

    def test_budget_never_returns_partial(self):
        g = {k: Claim(k, "open") for k in ("a", "b")}
        g["t"] = Claim("t", "derived", (("a",), ("b",)))
        for limits in (Limits(max_frontier=1), Limits(max_work=1),
                       Limits(max_retained_sets=1), Limits(max_nodes=1), Limits(max_edges=1)):
            with self.assertRaises(ResourceLimitError):
                solve(g, "t", limits=limits)
            r = report(g, "t", limits=limits)
            self.assertEqual(r["status"], "RESOURCE_LIMIT")
            self.assertIsNone(r["minimal_completion_sets"])
            self.assertFalse(r["level_6_certified"])

    def test_validation_even_disconnected(self):
        g = {"t": Claim("t", "established_external"), "x": Claim("x", "derived", (("x",),))}
        with self.assertRaisesRegex(ValueError, "cycle"):
            analyze(g, "t")
        g["x"] = Claim("x", "derived", (("missing",),))
        with self.assertRaisesRegex(ValueError, "Missing"):
            analyze(g, "t")

    def test_blockers_and_replay(self):
        g = {k: Claim(k, "open") for k in "abc"}
        g["t"] = Claim("t", "derived", (("a",), ("b", "c")))
        p = report(g, "t")
        self.assertEqual(p["minimal_blocking_sets"], [["a", "b"], ["a", "c"]])
        self.assertEqual(p["finite_oracle"]["status"], "PASS")
        self.assertTrue(replay(p)["reproduced"])
        altered = copy.deepcopy(p)
        altered["minimal_blocking_sets"] = []
        with self.assertRaises(ValueError):
            replay(altered)
        altered["sha256"] = digest({k: v for k, v in altered.items() if k != "sha256"})
        with self.assertRaises(ValueError):
            replay(altered)
        self.assertEqual(minimal_blockers([[]]), [])

    def test_existing_models_and_external_boundary(self):
        for g in models().values():
            p = report(g, "target")
            self.assertEqual(p["status"], "BLOCKED")
            self.assertFalse(p["level_6_certified"])
        p = report(models()["Poincare"], "published")
        self.assertEqual(p["minimal_completion_sets"], [[]])
        self.assertEqual(p["minimal_blocking_sets"], [])
        self.assertEqual(p["mathematical_certification"], "NOT_CERTIFIED")


if __name__ == "__main__":
    unittest.main()
