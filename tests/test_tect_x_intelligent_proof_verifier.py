"""Adversarial tests for TECT-X topological proof gap analysis.

These tests verify structural diagnostics only, not any theorem proof.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from mathos.research.tect_x_intelligent_proof_verifier import (
    CASES_PATH, ROOT, verify_cases, _topology,
)


class TestTECTXIntelligentProofVerifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = json.loads((ROOT / CASES_PATH).read_text(encoding="utf-8"))

    def mutation(self):
        return copy.deepcopy(self.sample)

    def blocked(self, data, part: str):
        report = verify_cases(data)
        self.assertFalse(report["ok"], report)
        self.assertTrue(
            any(part in issue for issue in report["issues"]),
            f"expected {part!r}; got {report['issues']!r}",
        )

    def test_three_real_case_models_are_valid_and_not_certified(self):
        report = verify_cases(self.sample)
        self.assertTrue(report["ok"], report["issues"])
        self.assertFalse(report["scientific_certification"])
        self.assertEqual(report["summary"]["mathematical_theorems_certified"], 0)
        self.assertEqual({c["case_id"] for c in report["cases"]}, {"RH-TGA", "SELMER-TGA", "ZETA-FINITE"})
        for case in report["cases"]:
            self.assertEqual(case["conclusion"], "BLOCKED_NOT_MATHEMATICALLY_VERIFIED")
            self.assertGreater(len(case["minimal_completion_sets"]), 0)
            self.assertTrue(case["prioritized_unresolved_obligations"])
            self.assertEqual(case["topological_gap_analysis"]["graph_h0_components"], 1)

    def test_minimal_completion_sets_respect_authored_or_paths(self):
        report = verify_cases(self.sample)
        rh = next(c for c in report["cases"] if c["case_id"] == "RH-TGA")
        sets = [set(x) for x in rh["minimal_completion_sets"]]
        self.assertEqual(len(sets), 2)
        self.assertIn({"RH.operator", "RH.zero_identity", "RH.global_bridge"}, sets)
        self.assertIn({"RH.feature_scan", "RH.invariant", "RH.tda_zero_bridge", "RH.uniform_argument", "RH.global_bridge"}, sets)
        self.assertEqual(rh["common_to_all_authored_routes"], ["RH.global_bridge"])
        self.assertEqual(rh["prioritized_unresolved_obligations"][0]["obligation"], "RH.global_bridge")

    def test_topological_h1_is_graph_cycle_rank_not_theorem_homology(self):
        report = verify_cases(self.sample)
        rh = next(c for c in report["cases"] if c["case_id"] == "RH-TGA")
        topo = rh["topological_gap_analysis"]
        self.assertEqual(topo["graph_h1_cycle_rank"], 1)
        self.assertIn("undirected dependency 1-skeleton", topo["meaning"])
        isolated = _topology({
            "target": {"routes": [["a"]]},
            "a": {"routes": []},
            "unrelated": {"routes": []},
        }, "target")
        self.assertEqual(isolated["graph_h0_components"], 2)
        self.assertEqual(isolated["disconnected_from_target"], ["unrelated"])

    def test_finite_computation_flagged_against_universal_target(self):
        report = verify_cases(self.sample)
        rh = next(c for c in report["cases"] if c["case_id"] == "RH-TGA")
        self.assertIn(
            "RH.feature_scan",
            {item["obligation"] for item in rh["scope_transfer_flags"]},
        )

    def test_conditional_selmer_lemma_not_unconditional(self):
        report = verify_cases(self.sample)
        sel = next(c for c in report["cases"] if c["case_id"] == "SELMER-TGA")
        self.assertIn(
            "SEL.conditional_counting",
            {item["obligation"] for item in sel["scope_transfer_flags"]},
        )
        self.assertEqual(sel["conclusion"], "BLOCKED_NOT_MATHEMATICALLY_VERIFIED")

    def test_reject_mathematical_certification_flag(self):
        data = self.mutation()
        data["scientific_status"] = "RH_PROVED"
        self.blocked(data, "scientific_status cannot assert mathematical certification")

    def test_reject_fabricated_proved_node(self):
        data = self.mutation()
        data["cases"][0]["nodes"][3]["kind"] = "PROVED"
        self.blocked(data, "invalid kind or scope")

    def test_reject_hidden_proof_promotion_field(self):
        data = self.mutation()
        data["cases"][0]["nodes"][3]["certified"] = True
        self.blocked(data, "unsupported node fields")

    def test_reject_unknown_evidence_id(self):
        data = self.mutation()
        data["cases"][0]["nodes"][3]["evidence_ids"] = ["E999"]
        self.blocked(data, "missing or invalid evidence links")

    def test_reject_incorrect_mapped_external_claim(self):
        data = self.mutation()
        data["cases"][0]["nodes"][3]["mapped_claim"] = "RH.a_mathematical_proof_is_done"
        self.blocked(data, "mapped claim must match an open existing proof obligation")

    def test_reject_dependency_cycles(self):
        data = self.mutation()
        nodes = {n["id"]: n for n in data["cases"][0]["nodes"]}
        # RH.spectral_route -> RH.operator -> RH.spectral_route
        node = nodes["RH.operator"]
        node["kind"] = "DERIVED"
        node.pop("evidence_ids")
        node.pop("mapped_claim")
        node.pop("next_action")
        node["routes"] = [["RH.spectral_route"]]
        self.blocked(data, "Dependency cycle")

    def test_reject_missing_dependency(self):
        data = self.mutation()
        data["cases"][0]["nodes"][0]["routes"] = [["MISSING_NODE"]]
        self.blocked(data, "unknown or repeated route dependency")

    def test_reject_unconnected_but_locally_valid_node(self):
        data = self.mutation()
        data["cases"][2]["nodes"].append({
            "id": "ORPHAN",
            "kind": "OPEN_OBLIGATION",
            "scope": "FINITE",
            "evidence_ids": ["E01"],
            "next_action": "Review omitted source",
        })
        self.blocked(data, "disconnected nodes not part of target dependency graph")

    def test_reject_missing_one_research_case(self):
        data = self.mutation()
        data["cases"] = data["cases"][:2]
        self.blocked(data, "expected exactly the three anchored research cases")

    def test_cli_json_and_fail_closed_require_proof(self):
        args = [sys.executable, "-m", "mathos.research.tect_x_intelligent_proof_verifier"]
        checked = subprocess.run(args + ["--json"], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        decoded = json.loads(checked.stdout)
        self.assertTrue(decoded["ok"])
        self.assertFalse(decoded["scientific_certification"])
        pending = subprocess.run(args + ["--require-proof"], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(pending.returncode, 2, pending.stderr)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "result.json"
            save = subprocess.run(args + ["--report", str(output)], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(save.returncode, 0, save.stderr)
            self.assertFalse(json.loads(output.read_text(encoding="utf-8"))["scientific_certification"])


if __name__ == "__main__":
    unittest.main()
