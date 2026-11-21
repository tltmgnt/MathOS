"""Regression tests for TECT-X thematic audit scope and provenance checks.

These tests validate repository declarations, not mathematical truth.
"""
from __future__ import annotations

import copy
import json
import unittest

from mathos.research.tect_x_thematic_gate import (
    REGISTER,
    ROOT,
    evaluate_register,
)


class TestTECTXThematicGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.original = json.loads(REGISTER.read_text(encoding="utf-8"))

    def altered(self):
        return copy.deepcopy(self.original)

    def reject(self, payload, fragment: str) -> None:
        result = evaluate_register(payload, ROOT)
        self.assertFalse(result["ok"], result)
        self.assertTrue(
            any(fragment in issue for issue in result["issues"]),
            f"missing expected blocker {fragment!r}: {result['issues']}",
        )

    def test_tracked_register_is_consistent_but_not_certified(self):
        result = evaluate_register(self.original, ROOT)
        self.assertEqual(result["issues"], [])
        self.assertTrue(result["ok"])
        self.assertEqual(result["theme_count"], 6)
        self.assertEqual(result["evidence_count"], 10)
        self.assertEqual(result["assurance_level"], "REPOSITORY_SOURCE_AUDIT_ONLY")

    def test_promoted_rh_flag_rejected(self):
        value = self.altered()
        value["certification_flags"]["riemann_hypothesis_proved"] = True
        self.reject(value, "unsupported certification flag: riemann_hypothesis_proved")

    def test_promoted_external_review_flag_rejected(self):
        value = self.altered()
        value["certification_flags"]["independent_specialist_review_complete"] = True
        self.reject(value, "unsupported certification flag: independent_specialist_review_complete")

    def test_unapproved_assurance_level_rejected(self):
        value = self.altered()
        value["assurance_level"] = "EXTERNALLY_CERTIFIED"
        self.reject(value, "assurance_level cannot assert independent certification")

    def test_missing_evidence_reference_rejected(self):
        value = self.altered()
        value["themes"][0]["evidence_ids"].append("E999")
        self.reject(value, "unknown evidence reference T1: E999")

    def test_duplicate_theme_rejected(self):
        value = self.altered()
        value["themes"][1]["id"] = "T1"
        self.reject(value, "duplicate theme id: T1")

    def test_orphan_evidence_rejected(self):
        value = self.altered()
        for theme in value["themes"]:
            theme["evidence_ids"] = [eid for eid in theme["evidence_ids"] if eid != "E09"]
        self.reject(value, "unlinked evidence record: E09")

    def test_missing_anchor_rejected(self):
        value = self.altered()
        value["evidence"][0]["source_paths"] = ["docs/research/does_not_exist_thematic_file.md"]
        self.reject(value, "missing source file: E01")

    def test_repository_traversal_rejected(self):
        value = self.altered()
        value["evidence"][0]["source_paths"] = ["../../private/document.txt"]
        self.reject(value, "unsafe source path: E01")

    def test_missing_evidence_limitation_rejected(self):
        value = self.altered()
        value["evidence"][0]["limitation"] = ""
        self.reject(value, "missing limitation: E01")

    def test_million_variant_h1_overclaim_rejected(self):
        value = self.altered()
        value["metrics_snapshot"]["million_point_h1_persistence_computed"] = True
        self.reject(value, "experiment metric mismatch: million_point_h1_persistence_computed")

    def test_tda_sample_inflation_rejected(self):
        value = self.altered()
        value["metrics_snapshot"]["rips_h01_sample_size_per_family"] = 1_000_000
        self.reject(value, "experiment metric mismatch: rips_h01_sample_size_per_family")

    def test_evidence_kind_must_be_scoped(self):
        value = self.altered()
        value["evidence"][0]["kind"] = "UNCONDITIONAL_PROOF"
        self.reject(value, "invalid evidence kind: E01")


if __name__ == "__main__":
    unittest.main()
