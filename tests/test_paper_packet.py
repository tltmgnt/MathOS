"""Reproducible SAT1 paper/review packets: anti-certification and provenance gates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mathos.research.paper_packet import (
    LEDGER_PATH, PAPER_PATH, REVIEW_PATH, audit_paper_packet,
)
from mathos.research.theorem_assurance import SAT_LEAN, THEOREMS_PATH


class PaperPacketTests(unittest.TestCase):
    def test_review_packet_is_explicitly_not_submission_or_clay_proof(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "research-note"
            report = audit_paper_packet(output_dir=out)
            self.assertEqual(report["packet_classification"],
                             "REVIEW_READY_NOT_SUBMISSION_READY")
            self.assertEqual(report["formal_status"], "NOT_RUN")
            self.assertEqual(report["manuscript_status"],
                             "REVIEW_DRAFT_NOT_SUBMITTED")
            self.assertEqual(report["novelty_assessment"],
                             "NOT_INDEPENDENTLY_ASSESSED")
            self.assertEqual(report["systematic_literature_review"],
                             "NOT_COMPLETED")
            self.assertEqual(report["independent_expert_review"],
                             "NOT_PERFORMED")
            self.assertEqual(report["journal_submission"], "NOT_SUBMITTED")
            self.assertEqual(report["clay_submission"], "NOT_SUBMITTED")
            self.assertFalse(report["clay_problem_solved"])
            self.assertEqual(report["registered_proof_obligations_closed"], 0)
            self.assertEqual(report["canonical_certification"], "NOT_CERTIFIED")
            self.assertEqual(report["independent_review_task_count"], 4)
            for name in ("SAT1_FORMAL_NOTE.md",
                         "SAT1_LITERATURE_LEDGER.v1.json",
                         "SAT1_EXTERNAL_REVIEW.md", "SATSupport.lean",
                         "packet_manifest.json", "review_readme.md"):
                self.assertTrue((out / name).exists(), name)
            self.assertEqual(
                hashlib.sha256((out / "SATSupport.lean").read_bytes()).hexdigest(),
                report["sources_sha256"]["formal_lean_source"],
            )

    def test_reproducible_packets_and_no_source_modifications(self):
        paths = [LEDGER_PATH, PAPER_PATH, REVIEW_PATH, SAT_LEAN, THEOREMS_PATH]
        original = [x.read_bytes() for x in paths]
        with tempfile.TemporaryDirectory() as temp:
            a = audit_paper_packet(output_dir=Path(temp) / "one")
            b = audit_paper_packet(output_dir=Path(temp) / "two")
            self.assertEqual(a, b)
            self.assertEqual(
                (Path(temp) / "one" / "packet_manifest.json").read_bytes(),
                (Path(temp) / "two" / "packet_manifest.json").read_bytes(),
            )
        self.assertEqual(original, [x.read_bytes() for x in paths])

    def test_manuscript_suppressed_caveat_rejected_without_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            document = Path(temp) / "paper.md"
            document.write_text(PAPER_PATH.read_text().replace(
                "No claim of mathematical novelty or a solution to P versus NP.",
                "A mathematical breakthrough is declared.",
            ))
            out = Path(temp) / "out"
            with self.assertRaisesRegex(ValueError, "disclosures"):
                audit_paper_packet(paper_path=document, output_dir=out)
            self.assertFalse(out.exists())

    def test_manuscript_forged_solution_status_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            document = Path(temp) / "paper.md"
            document.write_text(PAPER_PATH.read_text() + "\nResult: SOLVED\n")
            with self.assertRaisesRegex(ValueError, "status promotion"):
                audit_paper_packet(paper_path=document)

    def _bad_ledger(self, edit):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ledger.json"
            ledger = json.loads(LEDGER_PATH.read_text())
            edit(ledger)
            path.write_text(json.dumps(ledger), encoding="utf-8")
            return audit_paper_packet(ledger_path=path)

    def test_forged_novelty_expert_approval_publication_rejected(self):
        changes = [
            lambda d: d["policy"].update({"novelty_determination": "VERIFIED"}),
            lambda d: d["policy"].update({"external_review": "APPROVED"}),
            lambda d: d["policy"].update({"submission": "ACCEPTED"}),
            lambda d: d["policy"].update({"clay_solution": "PROVED"}),
            lambda d: d["policy"].update({"auto_promotion": True}),
            lambda d: d["policy"].update({"systematic_prior_art_search": "COMPLETE"}),
        ]
        for i, change in enumerate(changes):
            with self.subTest(case=i), self.assertRaises(ValueError):
                self._bad_ledger(change)

    def test_reference_metadata_and_urls_cannot_be_ghostwritten(self):
        changes = [
            lambda d: d["references"][0].update({"url": "https://example.test"}),
            lambda d: d["references"][1].update({"id": "R1"}),
            lambda d: d["references"][2].update({
                "independent_full_text_analysis": True}),
            lambda d: d["references"][3].update({
                "proves_specific_sat1_fact": True}),
            lambda d: d["references"].pop(),
            lambda d: d["references"][0].update({"metadata_checked": False}),
        ]
        for i, change in enumerate(changes):
            with self.subTest(case=i), self.assertRaises(ValueError):
                self._bad_ledger(change)

    def test_preliminary_search_cannot_be_laundered_as_complete(self):
        changes = [
            lambda d: d["search_log"][0].update({"completeness": "SYSTEMATIC"}),
            lambda d: d["open_review_tasks"][0].update({"status": "DONE"}),
            lambda d: d["search_log"].pop(),
            lambda d: d["open_review_tasks"].pop(),
            lambda d: d["open_review_tasks"][1].update({"task_id": "LIT01"}),
        ]
        for i, change in enumerate(changes):
            with self.subTest(case=i), self.assertRaises(ValueError):
                self._bad_ledger(change)

    def test_forged_human_review_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            review = Path(temp) / "review.md"
            review.write_text(REVIEW_PATH.read_text().replace(
                "No reviewer has been recruited or contacted",
                "This received independent mathematical acceptance",
            ))
            with self.assertRaisesRegex(ValueError, "unfilled-state"):
                audit_paper_packet(review_path=review)

    def test_missing_citations_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            document = Path(temp) / "paper.md"
            document.write_text(PAPER_PATH.read_text().replace(
                "https://doi.org/10.1145/237814.237860", "unspecified-URL"
            ))
            with self.assertRaisesRegex(ValueError, "background reference"):
                audit_paper_packet(paper_path=document)

    def test_no_subprocess_or_online_calls_by_default(self):
        with patch("mathos.research.theorem_assurance.subprocess.run") as subprocess:
            audit_paper_packet()
        subprocess.assert_not_called()

    def test_explicit_pinned_lean_option_records_only_limited_formal_status(self):
        with patch("mathos.research.theorem_assurance._check_lean",
                   return_value={
                       "status": "LEAN_COMPILED_EXACT_SUBRESULT_ONLY",
                       "lean_version": "Lean (version 4.14.0, mocked)",
                       "source_sha256": hashlib.sha256(SAT_LEAN.read_bytes()).hexdigest(),
                       "scope": "MATHOS_SAT1_TERM_CHOICE_ENCODING",
                       "clay_proof": False,
                   }) as checker:
            report = audit_paper_packet(verify_lean=True)
        checker.assert_called_once()
        self.assertEqual(report["formal_status"], "LEAN_COMPILED_EXACT_SUBRESULT_ONLY")
        self.assertTrue(report["pinned_lean_replay_requested"])
        self.assertFalse(report["clay_problem_solved"])
        self.assertEqual(report["novelty_assessment"], "NOT_INDEPENDENTLY_ASSESSED")

    def test_source_hash_matches_expert_handoff(self):
        report = audit_paper_packet()
        self.assertEqual(report["sources_sha256"]["manuscript"],
                         hashlib.sha256(PAPER_PATH.read_bytes()).hexdigest())
        self.assertEqual(report["sources_sha256"]["literature_ledger"],
                         hashlib.sha256(LEDGER_PATH.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
