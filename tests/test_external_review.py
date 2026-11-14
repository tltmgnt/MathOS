"""External SAT1 review intake and exact Lean axiom-gate regression tests."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mathos.research.external_review import (
    LEDGER_PATH, audit_external_reviews,
)
from mathos.research.lean_axiom_audit import (
    audit_axioms, parse_axiom_output,
)
from mathos.research.theorem_assurance import SAT_LEAN


def synthetic_review() -> dict:
    return {
        "review_id": "EXTREV-0001",
        "reviewer_github_handle": "external-math-reviewer",
        "external_review_url":
            "https://github.com/tltmgnt/MathOS/issues/25#issuecomment-12345",
        "reviewer_affiliation_or_background":
            "Reviewer self-description, not authenticated by any software or maintainer.",
        "reviewer_self_declares_independence": True,
        "conflicts_of_interest":
            "Self-attestation of no known conflict, requiring independent human confirmation.",
        "review_date_utc": "2026-11-13",
        "source_sha256": hashlib.sha256(SAT_LEAN.read_bytes()).hexdigest(),
        "lean_replay_description":
            "The claimed reviewer describes replaying Lean 4.14.0; code has not authenticated that event.",
        "formal_statement_assessment":
            "The SAT word-list definitions encode indexed choices and assert length, unique words and unit coefficients.",
        "mathematical_criticism":
            "No transfer from choice words to the standard polynomial ring is formally represented.",
        "prior_art_findings":
            "Classical elementary expansion counting should be compared against textbook sources by a real reader.",
        "sat_complexity_assessment":
            "An O(m) compact circuit means that a 3^m expanded monomial list is not a general SAT lower bound.",
        "recommendation": "INCONCLUSIVE",
    }


class ExternalReviewTests(unittest.TestCase):
    def _check_edited(self, edit):
        with tempfile.TemporaryDirectory() as tmp:
            content = json.loads(LEDGER_PATH.read_text())
            edit(content)
            source = Path(tmp) / "test_review_ledger.json"
            source.write_text(json.dumps(content))
            return audit_external_reviews(ledger_path=source)

    def test_empty_registered_assessment_is_not_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = audit_external_reviews(output_dir=Path(tmp))
            self.assertEqual(result["submitted_external_review_count"], 0)
            self.assertEqual(result["authenticated_independent_expert_review_count"], 0)
            self.assertEqual(result["independent_mathematical_assessment"],
                             "NOT_VERIFIED")
            self.assertEqual(result["clay_solution"], "NOT_CERTIFIED")
            self.assertTrue((Path(tmp) / "external_review_status.json").exists())
            self.assertEqual(result["proof_source_sha256"],
                             hashlib.sha256(SAT_LEAN.read_bytes()).hexdigest())

    def test_syntactically_valid_review_is_still_unverified(self):
        result = self._check_edited(
            lambda doc: doc["reviews"].append(synthetic_review()))
        self.assertEqual(result["submitted_external_review_count"], 1)
        self.assertEqual(result["authenticated_independent_expert_review_count"], 0)
        self.assertEqual(result["reviews"][0]["review_authenticity"],
                         "REQUIRES_HUMAN_VERIFICATION")
        self.assertFalse(result["reviews"][0]["expert_acceptance_recorded"])
        self.assertEqual(result["independent_mathematical_assessment"],
                         "NOT_VERIFIED")

    def test_forged_expert_acceptance_and_clay_promotion_rejected(self):
        mutations = [
            lambda d: d["policy"].update({"expert_verdict": "PEER_REVIEWED"}),
            lambda d: d["policy"].update({"independent_reviewer_verified": True}),
            lambda d: d["policy"].update({"mathematical_novelty": "ESTABLISHED"}),
            lambda d: d["policy"].update({"clay_solution": "CERTIFIED"}),
            lambda d: d["policy"].update({"theorem_claim_promotion": True}),
            lambda d: d["policy"].update({"journal_submission": "ACCEPTED"}),
            lambda d: d.update({"schema_version": "2.0.0"}),
        ]
        for i, mutate in enumerate(mutations):
            with self.subTest(i=i), self.assertRaises(ValueError):
                self._check_edited(mutate)

    def test_forged_identity_and_incomplete_evidence_rejected(self):
        changes = [
            lambda r: r.update({"reviewer_github_handle": "tltmgnt"}),
            lambda r: r.update({"reviewer_github_handle": "github-actions"}),
            lambda r: r.update({"reviewer_self_declares_independence": False}),
            lambda r: r.update({"external_review_url": "https://evil.test"}),
            lambda r: r.update({"review_date_utc": "not-a-date"}),
            lambda r: r.update({"source_sha256": "0"}),
            lambda r: r.update({"mathematical_criticism": "looks good"}),
            lambda r: r.update({"recommendation": "CLAY_SOLVED"}),
            lambda r: r.pop("conflicts_of_interest"),
        ]
        for i, change in enumerate(changes):
            with self.subTest(i=i), self.assertRaises(ValueError):
                self._check_edited(lambda d: (
                    d["reviews"].append(synthetic_review()),
                    change(d["reviews"][0]),
                ))

    def test_duplicate_submissions_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self._check_edited(lambda d: d["reviews"].extend(
                [synthetic_review(), synthetic_review()]))

    def test_immutable_sources(self):
        before = LEDGER_PATH.read_bytes()
        lean = SAT_LEAN.read_bytes()
        a = audit_external_reviews()
        b = audit_external_reviews()
        self.assertEqual(a, b)
        self.assertEqual(before, LEDGER_PATH.read_bytes())
        self.assertEqual(lean, SAT_LEAN.read_bytes())

    def test_public_issue_link_not_review_evidence(self):
        result = self._check_edited(
            lambda d: d.update({
                "review_request_url":
                    "https://github.com/tltmgnt/MathOS/issues/25",
            }))
        self.assertEqual(result["review_request_status"],
                         "PUBLIC_INVITATION_POSTED_NOT_REVIEWED")
        self.assertEqual(result["submitted_external_review_count"], 0)
        self.assertEqual(result["independent_mathematical_assessment"],
                         "NOT_VERIFIED")

    def test_axiom_parser_accepts_only_standard_logic(self):
        self.assertEqual(
            parse_axiom_output(
                "'MathOS.satSupport_certificate' does not depend on any axioms"),
            (),
        )
        self.assertEqual(
            parse_axiom_output(
                "'MathOS.satSupport_certificate' depends on axioms: "
                "[Quot.sound, propext, Classical.choice]"),
            ("Classical.choice", "Quot.sound", "propext"),
        )

    def test_axiom_parser_rejects_sorry_custom_native_and_missing(self):
        cases = [
            "'MathOS.satSupport_certificate' depends on axioms: [sorryAx]",
            "'MathOS.satSupport_certificate' depends on axioms: [Lean.trustCompiler]",
            "'MathOS.satSupport_certificate' depends on axioms: [customAx]",
            "'MathOS.satSupport_certificate' depends on axioms: [propext, sorryAx]",
            "Lean elaboration completed successfully",
            "'MathOS.satSupport_certificate' depends on axioms: [propext, propext]",
        ]
        for t in cases:
            with self.subTest(output=t), self.assertRaises(ValueError):
                parse_axiom_output(t)

    def test_axiom_replay_pinned_source_accepted_with_mocked_lean(self):
        with tempfile.TemporaryDirectory() as tmp, patch(
            "mathos.research.lean_axiom_audit.shutil.which",
            return_value="/usr/bin/lean",
        ), patch("mathos.research.lean_axiom_audit.subprocess.run") as run:
            run.side_effect = [
                SimpleNamespace(returncode=0,
                                stdout="Lean (version 4.14.0, x86_64)\n"),
                SimpleNamespace(
                    returncode=0,
                    stdout="'MathOS.satSupport_certificate' "
                           "does not depend on any axioms\n",
                ),
            ]
            result = audit_axioms(output_dir=Path(tmp))
            self.assertEqual(result["transitive_axioms"], [])
            self.assertFalse(result["proves_clay_problem"])
            self.assertEqual(result["formal_axiom_audit"],
                             "PASSED_WITH_ONLY_STANDARD_LEAN_AXIOMS")
            self.assertTrue((Path(tmp) / "sat1_axiom_audit.json").exists())
            self.assertEqual(run.call_count, 2)
            self.assertFalse(run.call_args.kwargs.get("shell", False))

    def test_axiom_replay_fails_without_pinned_lean(self):
        with patch("mathos.research.lean_axiom_audit.shutil.which",
                   return_value=None):
            with self.assertRaises(RuntimeError):
                audit_axioms()


if __name__ == "__main__":
    unittest.main()
