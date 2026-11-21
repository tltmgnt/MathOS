"""Adversarial source audits for typed TECT-X Lean proof certificates.

A mocked subprocess can test failure paths, but cannot itself provide
a trusted kernel certificate. Actual replay occurs in pinned Lean CI.
"""
from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from mathos.research.tect_x_formal_certificates import (
    LEAN_VERSION, MANIFEST_PATH, THEOREMS,
    _extract_axiom_reports, audit, validate_manifest,
)


class TestTECTXFormalCertificates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def modified(self):
        return copy.deepcopy(self.manifest)

    def rejects(self, value, phrase):
        result = validate_manifest(value)
        self.assertFalse(result["source_audit_passed"], result)
        self.assertFalse(result["kernel_checked"])
        self.assertTrue(any(phrase in issue for issue in result["failures"]), result["failures"])

    def test_static_source_audit_never_claims_kernel_validation(self):
        result = validate_manifest(self.manifest)
        self.assertTrue(result["source_audit_passed"], result["failures"])
        self.assertEqual(result["formal_status"], "NOT_RUN")
        self.assertFalse(result["kernel_checked"])
        self.assertFalse(result["semantic_link_to_conjecture_verified"])
        self.assertFalse(result["independent_human_review_completed"])
        self.assertEqual(result["closed_conjecture_obligations"], [])
        for path in ("formal/TECTXFiniteTopology.lean", "formal/TECTXFiniteTopologyContract.lean"):
            self.assertEqual(len(result[path + "_sha256"]), 64)

    def test_cli_static_does_not_invent_formal_success(self):
        result = audit()
        self.assertTrue(result["ok"])
        self.assertEqual(result["formal_status"], "NOT_RUN")
        self.assertFalse(result["kernel_checked"])

    def test_reject_noncanonical_toolchain(self):
        value = self.modified()
        value["backend"]["version"] = "nightly"
        self.rejects(value, "approved pinned Lean")

    def test_reject_removed_theorem_contract(self):
        value = self.modified()
        value["certificate"]["theorem_names"].pop()
        self.rejects(value, "theorem declarations must exactly match")

    def test_reject_made_up_custom_axiom(self):
        value = self.modified()
        value["certificate"]["permitted_transitive_axioms"] = ["sorryAx"]
        self.rejects(value, "transitive axioms are not allowed")

    def test_reject_fabricated_clay_claim(self):
        value = self.modified()
        value["certificate"]["proof_of_rh"] = True
        self.rejects(value, "unsupported conjecture proof claim")

    def test_reject_unreviewed_external_promotion(self):
        value = self.modified()
        value["certificate"]["external_review"] = "COMPLETED"
        self.rejects(value, "external human review must not be self-certified")

    def test_reject_fake_completed_kernel_replay_in_manifest(self):
        value = self.modified()
        value["certificate"]["formal_claim_status"] = "KERNEL_CHECKED"
        self.rejects(value, "static manifest cannot claim")

    def test_reject_mapped_open_obligation_promotion(self):
        value = self.modified()
        value["certificate"]["closes_mathematical_obligation_ids"] = ["RH.zero_identity"]
        self.rejects(value, "cannot close open conjecture")

    def test_exact_clean_axiom_reports_parsed(self):
        output = "\n".join(
            f"/tmp/contract.lean:39:0: information: '{t}' does not depend on any axioms"
            for t in THEOREMS
        )
        self.assertEqual(_extract_axiom_reports(output), {t: [] for t in THEOREMS})

    def test_missing_axiom_report_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
            _extract_axiom_reports("nothing checked")

    def test_duplicate_axiom_report_rejected(self):
        output = "\n".join(f"'{t}' does not depend on any axioms" for t in THEOREMS)
        with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
            _extract_axiom_reports(output + "\n" + output.splitlines()[0])

    def test_sorry_dependency_rejected(self):
        text = "\n".join(
            f"'{t}' depends on axioms: [sorryAx]" if i == 1
            else f"'{t}' does not depend on any axioms"
            for i, t in enumerate(THEOREMS)
        )
        with self.assertRaisesRegex(ValueError, "unapproved transitive axioms"):
            _extract_axiom_reports(text)

    def test_classical_axiom_rejected_for_this_certificate(self):
        text = "\n".join(
            f"'{t}' depends on axioms: [Classical.choice]" if i == 1
            else f"'{t}' does not depend on any axioms"
            for i, t in enumerate(THEOREMS)
        )
        with self.assertRaisesRegex(ValueError, "unapproved transitive axioms"):
            _extract_axiom_reports(text)

    def test_missing_kernel_binary_fails_closed(self):
        with patch("mathos.research.tect_x_formal_certificates.subprocess.run",
                   side_effect=FileNotFoundError("Lean is not installed")):
            result = audit(check_kernel=True)
        self.assertFalse(result["ok"])
        self.assertFalse(result["kernel_checked"])
        self.assertEqual(result["formal_status"], "KERNEL_CHECK_FAILED")

    def test_wrong_pinned_version_fails_closed(self):
        with patch("mathos.research.tect_x_formal_certificates.subprocess.run",
                   return_value=subprocess.CompletedProcess([], 0, "Lean (version 4.13.0, x)", "")):
            result = audit(check_kernel=True)
        self.assertFalse(result["ok"])
        self.assertFalse(result["kernel_checked"])
        self.assertEqual(result["formal_status"], "KERNEL_CHECK_FAILED")

    def test_accepted_version_but_compiler_failure_fails_closed(self):
        def fake_run(args, **kw):
            if "--version" in args:
                return subprocess.CompletedProcess(args, 0, f"Lean (version {LEAN_VERSION}, mocked)", "")
            return subprocess.CompletedProcess(args, 1, "", "incorrect proof")
        with patch("mathos.research.tect_x_formal_certificates.subprocess.run", side_effect=fake_run):
            result = audit(check_kernel=True)
        self.assertFalse(result["ok"])
        self.assertFalse(result["kernel_checked"])
        self.assertEqual(result["formal_status"], "KERNEL_CHECK_FAILED")


if __name__ == "__main__":
    unittest.main()
