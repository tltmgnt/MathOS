"""Adversarial tests for finite graph F2 cycle-space proof certificates.

Passing tests checks only Python preflight; actual mathematical proof
requires pinned Lean replay in the dedicated GitHub Actions job.
"""
from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mathos.research.tect_x_general_graph_certificates import (
    MANIFEST, analyze_manifest, emit_lean, replay, _parse_axiom_reports
)


class TestGeneralFiniteGraphCertificates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def mutated(self):
        return copy.deepcopy(self.raw)

    def rejects(self, data, phrase):
        with self.assertRaises(ValueError) as cm:
            analyze_manifest(data)
        self.assertIn(phrase, str(cm.exception))

    def test_five_distinct_graphs_and_expected_betti_numbers(self):
        result = analyze_manifest(self.raw)
        self.assertTrue(result["source_audit_passed"])
        self.assertFalse(result["mathematical_theorem_certification"])
        observed = {c["id"]: (c["h0_components"], c["h1_cycle_dimension"])
                    for c in result["cases"]}
        self.assertEqual(observed, {
            "path4": (1, 0),
            "square4": (1, 1),
            "diamond4": (1, 2),
            "disconnected6": (3, 1),
            "k4": (1, 3),
        })
        for case in result["cases"]:
            self.assertEqual(case["number_of_1cycles"], 2 ** case["h1_cycle_dimension"])

    def test_generates_exactly_ten_kernel_theorems(self):
        analysis = analyze_manifest(self.raw)
        lean, theorem_names = emit_lean(analysis)
        self.assertEqual(len(theorem_names), 10)
        self.assertIn("set_option warningAsError true", lean)
        self.assertEqual(lean.count("#print axioms "), 10)
        self.assertIn("theorem k4_cycles_exact", lean)
        self.assertIn("theorem k4_basis_independent", lean)
        self.assertIn("cases e0", lean)
        self.assertNotIn("sorry", lean)
        self.assertNotIn("native_decide", lean)
        self.assertNotIn("axiom ", lean)

    def test_static_report_never_invents_kernel_pass(self):
        report = replay(self.raw)
        self.assertTrue(report["ok"])
        self.assertFalse(report["kernel_checked"])
        self.assertEqual(report["formal_status"], "NOT_RUN")
        self.assertEqual(report["formal_theorem_count"], 0)
        self.assertEqual(report["closed_conjecture_obligations"], [])
        self.assertEqual(len(report["generated_lean_sha256"]), 64)

    def test_corrupt_h1_rejected(self):
        value = self.mutated()
        value["cases"][2]["expected_h1"] = 3
        self.rejects(value, "claimed H0/H1 contradict")

    def test_corrupt_h0_rejected(self):
        value = self.mutated()
        value["cases"][3]["expected_h0"] = 1
        self.rejects(value, "claimed H0/H1 contradict")

    def test_tampered_mathematical_certification_rejected(self):
        value = self.mutated()
        value["mathematical_theorem_certification"] = True
        self.rejects(value, "illegal research-status promotion")

    def test_reject_open_conjecture_promotion(self):
        value = self.mutated()
        value["closed_conjecture_obligations"] = ["RH.zero_identity"]
        self.rejects(value, "illegal research-status promotion")

    def test_reject_code_injection_into_lean_name(self):
        value = self.mutated()
        value["cases"][0]["id"] = "path4; axiom RH : False"
        self.rejects(value, "safe Lean identifier")

    def test_duplicate_graph_case_id_rejected(self):
        value = self.mutated()
        value["cases"][2]["id"] = "square4"
        self.rejects(value, "safe Lean identifier")

    def test_duplicate_edge_rejected(self):
        value = self.mutated()
        value["cases"][0]["edges"].append([0, 1])
        self.rejects(value, "duplicate edge")

    def test_loop_and_noncanonical_edge_rejected(self):
        value = self.mutated()
        value["cases"][0]["edges"][0] = [1, 1]
        self.rejects(value, "u < v")

    def test_out_of_range_vertex_rejected(self):
        value = self.mutated()
        value["cases"][0]["edges"][0] = [0, 8]
        self.rejects(value, "valid endpoints")

    def test_false_boolean_as_vertex_count_rejected(self):
        value = self.mutated()
        value["cases"][0]["vertices"] = True
        self.rejects(value, "number of vertices is out of bounds")

    def test_oversized_graph_rejected(self):
        value = self.mutated()
        value["cases"][0]["vertices"] = 8
        self.rejects(value, "number of vertices is out of bounds")

    def test_edge_free_graph_is_valid(self):
        value = self.mutated()
        value["cases"] = [{
            "id": "isolated3",
            "vertices": 3,
            "edges": [],
            "expected_h0": 3,
            "expected_h1": 0,
        }]
        result = analyze_manifest(value)
        lean, names = emit_lean(result)
        self.assertEqual(result["cases"][0]["number_of_1cycles"], 1)
        self.assertEqual(len(names), 2)
        self.assertIn("theorem isolated3_cycles_exact", lean)

    def test_reject_missing_axiom_reports(self):
        with self.assertRaisesRegex(ValueError, "missing/ambiguous"):
            _parse_axiom_reports("", ["MathOS.TECTX.GraphCertificates.square4_cycles_exact"])

    def test_reject_sorry_ax(self):
        name = "MathOS.TECTX.GraphCertificates.square4_cycles_exact"
        with self.assertRaisesRegex(ValueError, "missing/ambiguous/nonempty"):
            _parse_axiom_reports(f"'{name}' depends on axioms: [sorryAx]", [name])

    def test_reject_duplicate_axiom_report(self):
        name = "MathOS.TECTX.GraphCertificates.square4_cycles_exact"
        line = f"'{name}' does not depend on any axioms"
        with self.assertRaisesRegex(ValueError, "missing/ambiguous"):
            _parse_axiom_reports(line + "\n" + line, [name])

    def test_reject_wrong_lean_version_and_do_not_write_theorem_source(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch(
                "mathos.research.tect_x_general_graph_certificates.subprocess.run",
                return_value=subprocess.CompletedProcess([], 0,
                    "Lean (version 4.13.0, wrong version)", "")
            ):
                result = replay(self.raw, run_lean=True, output_dir=Path(temp))
            self.assertFalse(result["ok"])
            self.assertFalse(result["kernel_checked"])
            self.assertEqual(result["formal_status"], "KERNEL_CHECK_FAILED")
            self.assertFalse((Path(temp) / "TECTXGeneralFiniteGraph.lean").exists())

    def test_missing_lean_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch(
                "mathos.research.tect_x_general_graph_certificates.subprocess.run",
                side_effect=FileNotFoundError("no Lean")
            ):
                result = replay(self.raw, run_lean=True, output_dir=Path(temp))
            self.assertFalse(result["ok"])
            self.assertFalse(result["kernel_checked"])
            self.assertEqual(result["formal_status"], "KERNEL_CHECK_FAILED")


if __name__ == "__main__":
    unittest.main()
