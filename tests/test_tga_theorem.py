"""Regression and adversarial tests for finite TGA theorem proving."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.tga_theorem import decide, verify


def spec():
    return {
        "schema": 1,
        "claims": {
            "a": {"state": "open", "routes": []},
            "b": {"state": "open", "routes": []},
            "c": {"state": "derived", "routes": [["a", "b"], ["a"]]},
            "goal": {"state": "derived", "routes": [["c"]]},
        },
        "premises": ["a"],
        "goal": "goal",
    }


class FiniteTGATheoremTests(unittest.TestCase):
    def test_valid_entailment(self):
        result = decide(spec())
        self.assertEqual(result["verdict"], "ENTAILED_WITHIN_GRAPH")
        self.assertEqual(result["assignments_checked"], 4)
        self.assertEqual(result["premise_satisfying_assignments_checked"], 2)
        self.assertIsNone(result["countermodel"])
        self.assertFalse(result["mathematical_theorem_certified"])
        self.assertTrue(verify(spec(), result)["verified"])

    def test_countermodel(self):
        case = spec()
        case["premises"] = []
        result = decide(case)
        self.assertEqual(result["verdict"], "COUNTERMODEL_FOUND")
        self.assertEqual(result["countermodel"], {"a": False, "b": False})
        self.assertTrue(verify(case, result)["verified"])

    def test_missing_assumption_not_proof(self):
        case = spec()
        case["claims"]["c"]["routes"] = [["a", "b"]]
        result = decide(case)
        self.assertEqual(result["verdict"], "COUNTERMODEL_FOUND")
        self.assertEqual(result["countermodel"], {"a": True, "b": False})

    def test_derived_premises(self):
        case = spec()
        case["premises"] = ["c"]
        self.assertEqual(decide(case)["verdict"], "ENTAILED_WITHIN_GRAPH")

    def test_unrelated_goal(self):
        case = spec()
        case["goal"] = "b"
        self.assertEqual(decide(case)["verdict"], "COUNTERMODEL_FOUND")

    def test_external_assumption_is_not_math_certification(self):
        case = spec()
        case["claims"]["a"] = {"state": "established_external", "routes": []}
        case["premises"] = []
        result = decide(case)
        self.assertEqual(result["verdict"], "ENTAILED_WITHIN_GRAPH")
        self.assertFalse(result["mathematical_theorem_certified"])

    def test_vacuous_entailment_exposes_zero_models(self):
        case = spec()
        case["premises"] = ["a", "goal"]
        case["goal"] = "a"
        self.assertEqual(decide(case)["verdict"], "ENTAILED_WITHIN_GRAPH")

    def test_forged_result_fails_replay(self):
        result = decide(spec())
        result["kernel_checked"] = True
        with self.assertRaises(ValueError):
            verify(spec(), result)

    def test_wrong_spec_fails_replay(self):
        result = decide(spec())
        case = spec()
        case["premises"] = []
        with self.assertRaises(ValueError):
            verify(case, result)

    def test_cycle_rejected_even_if_unreferenced(self):
        case = spec()
        case["claims"]["loop"] = {"state": "derived", "routes": [["loop"]]}
        with self.assertRaisesRegex(ValueError, "cycle"):
            decide(case)

    def test_missing_dependency_rejected(self):
        case = spec()
        case["claims"]["c"]["routes"] = [["nonexistent"]]
        with self.assertRaisesRegex(ValueError, "dependency"):
            decide(case)

    def test_rejects_oversized_open_domain(self):
        case = spec()
        for k in range(17):
            case["claims"][f"x{k}"] = {"state": "open", "routes": []}
        with self.assertRaisesRegex(ValueError, "too many open"):
            decide(case)

    def test_rejects_duplicate_premise(self):
        case = spec()
        case["premises"] = ["a", "a"]
        with self.assertRaisesRegex(ValueError, "premise"):
            decide(case)

    def test_cli_prove_verify_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.json"
            cert_path = root / "certificate.json"
            source.write_text(json.dumps(spec()), encoding="utf-8")
            run = subprocess.run([sys.executable, "-m", "mathos.tga_theorem", "prove", str(source)],
                                 capture_output=True, text=True, check=True)
            cert_path.write_text(run.stdout, encoding="utf-8")
            replay = subprocess.run([sys.executable, "-m", "mathos.tga_theorem", "verify",
                                     str(source), str(cert_path)], capture_output=True, text=True, check=True)
            self.assertTrue(json.loads(replay.stdout)["verified"])


if __name__ == "__main__":
    unittest.main()
