"""Tests that TGA graph-to-Lean translation preserves scoped assurance."""
import copy
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
import subprocess

from mathos.tga_lean_bridge import compile_lean, check_lean


def example():
    return {
        "schema": 1,
        "claims": {
            "a": {"state": "open", "routes": []},
            "b": {"state": "open", "routes": []},
            "route": {"state": "derived", "routes": [["a", "b"], ["a"]]},
            "target": {"state": "derived", "routes": [["route"]]},
        },
        "premises": ["a"],
        "goal": "target",
    }


class TGALeanBridgeTests(TestCase):
    def test_emits_quantified_graph_proposition(self):
        result = compile_lean(example())
        self.assertIn("∀ (v0 : Bool) (v1 : Bool)", result["source"])
        self.assertIn("theorem tga_graph_entailment", result["source"])
        self.assertIn("  decide", result["source"])
        self.assertFalse(result["lean_kernel_checked"])
        self.assertFalse(result["mathematical_statement_verified"])

    def test_deterministic_source_digest(self):
        self.assertEqual(compile_lean(example()), compile_lean(copy.deepcopy(example())))

    def test_unproved_graph_rejected(self):
        case = example()
        case["premises"] = []
        with self.assertRaisesRegex(ValueError, "countermodel"):
            compile_lean(case)

    def test_missing_assumption_rejected(self):
        case = example()
        case["claims"]["route"]["routes"] = [["a", "b"]]
        with self.assertRaisesRegex(ValueError, "countermodel"):
            compile_lean(case)

    def test_invalid_dependency_rejected(self):
        case = example()
        case["claims"]["route"]["routes"] = [["unknown"]]
        with self.assertRaises(ValueError):
            compile_lean(case)

    def test_cycle_rejected(self):
        case = example()
        case["claims"]["route"]["routes"] = [["route"]]
        with self.assertRaisesRegex(ValueError, "cycle"):
            compile_lean(case)

    def test_external_assumption_marked(self):
        case = example()
        case["claims"]["a"] = {"state": "established_external", "routes": []}
        case["premises"] = []
        output = compile_lean(case)
        self.assertEqual(output["external_assumptions"], ["a"])
        self.assertFalse(output["mathematical_statement_verified"])

    def test_reject_large_open_input(self):
        case = example()
        for i in range(7):
            case["claims"][f"extra{i}"] = {"state": "open", "routes": []}
        with self.assertRaisesRegex(ValueError, "at most 6"):
            compile_lean(case)

    def test_wrong_lean_version_rejected(self):
        with patch("mathos.tga_lean_bridge.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, "Lean (version 4.13.0, x)", "")
            with self.assertRaisesRegex(ValueError, "4.14.0"):
                check_lean(example())

    def test_lean_rejection_does_not_promote(self):
        with patch("mathos.tga_lean_bridge.subprocess.run") as run:
            run.side_effect = [
                subprocess.CompletedProcess([], 0, "Lean (version 4.14.0, x)", ""),
                subprocess.CompletedProcess([], 1, "", "invalid proof"),
            ]
            with self.assertRaisesRegex(ValueError, "Lean rejected"):
                check_lean(example())

    def test_missing_axiom_report_is_rejected(self):
        with patch("mathos.tga_lean_bridge.subprocess.run") as run:
            run.side_effect = [
                subprocess.CompletedProcess([], 0, "Lean (version 4.14.0, x)", ""),
                subprocess.CompletedProcess([], 0, "", ""),
            ]
            with self.assertRaisesRegex(ValueError, "axiom policy"):
                check_lean(example())


if __name__ == "__main__":
    import unittest
    unittest.main()
