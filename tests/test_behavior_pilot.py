"""Blinded two-rater SAT1 pilot: provenance, privacy, consent and κ arithmetic."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mathos.research.behavior_review import KEYS, run_behavior_review
from mathos.research.behavior_pilot import (
    PROTOCOL_PATH, _agreement, run_pilot,
)
from mathos.research.theorem_assurance import SAT_LEAN


class BehaviorPilotTests(unittest.TestCase):
    def _response(self, folder: Path) -> Path:
        deck_dir = folder / "deck"
        run_behavior_review(output_dir=deck_dir)
        answers = json.loads((deck_dir / "blank_responses.json").read_text())
        answers["participant_label"] = "Pseudonym_01"
        for row in answers["responses"]:
            row["decision"] = "INCONCLUSIVE"
            row["evidence_notes"] = (
                "SAT1 is a theorem about a choice-word expansion only. A "
                "polynomial ring map and general SAT runtime implications "
                "would need additional independent proofs."
            )
            row["source_reference"] = "formal/SATSupport.lean (read within the test fixture)"
        path = folder / "answers.json"
        path.write_text(json.dumps(answers))
        return path

    def _raters(self, folder: Path, answers: Path, mutate=None):
        out = folder / "private"
        run_pilot(response_path=answers, consent_attested=True, output_dir=out)
        original = json.loads((out / "private_rater_template.json").read_text())
        raters = []
        for side in ("A", "B"):
            rater = copy.deepcopy(original)
            rater["rater_pseudonym"] = "Rater_" + side
            rater["conflicts_declaration"] = (
                "Self-reported rater conflict information, unauthenticated "
                "and purely synthetic in this test."
            )
            for index, row in enumerate(rater["ratings"]):
                value = index % 2
                row["observation_one_present"] = value
                row["observation_two_present"] = 1 - value
                row["source_reference_relevant"] = value
                row["rater_comment"] = (
                    "Synthetic example of a per-card rubric observation "
                    "rather than an actual qualified human review."
                )
            raters.append(rater)
        if mutate:
            mutate(raters)
        files = []
        for side, rater in zip(("A", "B"), raters):
            target = folder / (side + ".json")
            target.write_text(json.dumps(rater))
            files.append(target)
        return files

    def test_protocol_mode_contains_no_participant_data_or_false_study(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            result = run_pilot(output_dir=out)
            self.assertEqual(result["pilot_status"], "PROTOCOL_ONLY_NO_HUMAN_DATA")
            self.assertFalse(result["participant_data_present"])
            self.assertIsNone(result["inter_rater_metrics"])
            self.assertFalse(result["independent_raters_authenticated"])
            self.assertEqual(result["expert_mathematical_review"], "NOT_PERFORMED")
            self.assertEqual(result["clay_solution"], "NOT_CERTIFIED")
            self.assertTrue((out / "pilot_status.json").exists())
            self.assertFalse((out / "private_blinded_rater_packet.json").exists())

    def test_consent_required_before_respondent_data_are_read(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            response = self._response(folder)
            with self.assertRaisesRegex(ValueError, "attest participant consent"):
                run_pilot(response_path=response, output_dir=folder / "out")
            self.assertFalse((folder / "out").exists())

    def test_blinding_removes_decision_and_participant_label(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            response = self._response(folder)
            report = run_pilot(
                response_path=response, consent_attested=True,
                output_dir=folder / "rater_packet",
            )
            blinded = json.loads(
                (folder / "rater_packet" / "private_blinded_rater_packet.json").read_text()
            )
            self.assertEqual(report["pilot_status"],
                             "BLINDED_PACKET_PREPARED_UNAUTHENTICATED")
            self.assertTrue(report["operator_consent_attestation"])
            self.assertEqual(len(blinded["cases"]), 7)
            self.assertTrue(all(
                "selected_decision" not in r and "decision" not in r and
                "key_decision" not in r and "participant_label" not in r
                for r in blinded["cases"]
            ))
            self.assertNotIn("participant_label", blinded)
            self.assertNotIn("decision_key", blinded)
            self.assertIn("evidence_notes", blinded["cases"][0])
            self.assertEqual(report["response_sha256"],
                             hashlib.sha256(response.read_bytes()).hexdigest())
            status = (folder / "rater_packet" / "pilot_status.json").read_text()
            self.assertNotIn("choice-word expansion only", status)
            self.assertNotIn("Pseudonym_01", status)

    def test_two_raters_agree_but_not_independently_authenticated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            response = self._response(root)
            a, b = self._raters(root, response)
            result = run_pilot(
                response_path=response, rater_a_path=a, rater_b_path=b,
                consent_attested=True,
            )
            self.assertEqual(result["pilot_status"],
                             "DOUBLE_RATINGS_RECEIVED_UNAUTHENTICATED")
            self.assertEqual(result["inter_rater_metrics"]["pooled"]["pair_count"], 21)
            self.assertEqual(result["inter_rater_metrics"]["pooled"]["cohen_kappa"], 1.0)
            self.assertEqual(
                result["inter_rater_metrics"]["observation_one_present"]["cohen_kappa"],
                1.0,
            )
            self.assertEqual(result["study_conducted_independently"], "NOT_VERIFIED")
            self.assertFalse(result["behavioral_instrument_validated"])
            self.assertFalse(result["independent_raters_authenticated"])
            self.assertEqual(result["clay_solution"], "NOT_CERTIFIED")
            self.assertEqual(len(result["rater_receipts"]), 2)
            self.assertNotIn("conflicts_declaration", result["rater_receipts"][0])

    def test_no_variance_reports_undefined_kappa_not_1(self):
        metrics = _agreement([1] * 7, [1] * 7)
        self.assertEqual(metrics["observed_agreement"], 1.0)
        self.assertIsNone(metrics["cohen_kappa"])
        self.assertFalse(metrics["kappa_defined"])

    def test_exact_kappa_arithmetic_independent_of_commit_order(self):
        r = _agreement([0, 0, 1, 1], [0, 1, 0, 1])
        self.assertEqual(r["observed_agreement"], .5)
        self.assertEqual(r["expected_chance_agreement"], .5)
        self.assertEqual(r["cohen_kappa"], 0.0)
        self.assertEqual(r["agreeing_pairs"], 2)
        reverse = _agreement([0, 1, 0, 1], [0, 0, 1, 1])
        self.assertEqual(r, reverse)

    def test_partial_double_rater_submission_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            response = self._response(root)
            a, _ = self._raters(root, response)
            with self.assertRaisesRegex(ValueError, "two independently"):
                run_pilot(response_path=response, rater_a_path=a,
                          consent_attested=True)

    def test_reject_stale_and_modified_rater_source_receipts(self):
        edits = [
            lambda d: d[0].update({"protocol_sha256": "0" * 64}),
            lambda d: d[0].update({"source_sha256": "0" * 64}),
            lambda d: d[1].update({"response_sha256": "0" * 64}),
            lambda d: d[1]["ratings"][2].update({
                "evidence_note_sha256": "0" * 64
            }),
        ]
        for i, edit in enumerate(edits):
            with self.subTest(case=i), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                response = self._response(root)
                a, b = self._raters(root, response, edit)
                with self.assertRaises(ValueError):
                    run_pilot(response_path=response, rater_a_path=a,
                              rater_b_path=b, consent_attested=True)

    def test_reject_forged_independence_and_invalid_rubric(self):
        edits = [
            lambda d: d[0].update({"independence_declaration": "VERIFIED"}),
            lambda d: d[0]["ratings"][0].update({"observation_one_present": True}),
            lambda d: d[1]["ratings"][1].update({"observation_two_present": 2}),
            lambda d: d[1]["ratings"][1].update({"source_reference_relevant": None}),
            lambda d: d[1]["ratings"][0].update({"rater_comment": "fine"}),
            lambda d: d[0].update({"conflicts_declaration": ""}),
            lambda d: d[1].update({"peer_review_approved": True}),
        ]
        for i, edit in enumerate(edits):
            with self.subTest(case=i), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                response = self._response(root)
                a, b = self._raters(root, response, edit)
                with self.assertRaises(ValueError):
                    run_pilot(response_path=response, rater_a_path=a,
                              rater_b_path=b, consent_attested=True)

    def test_duplicate_raters_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            response = self._response(root)
            a, b = self._raters(
                root, response,
                lambda rr: rr[1].update({"rater_pseudonym": "Rater_A"})
            )
            with self.assertRaisesRegex(ValueError, "duplicate rater"):
                run_pilot(response_path=response, rater_a_path=a,
                          rater_b_path=b, consent_attested=True)

    def test_protocol_scope_and_promotion_fail_closed(self):
        edits = [
            lambda d: d["policy"].update({"clay_solution": "CERTIFIED"}),
            lambda d: d["policy"].update({"human_rater_authenticity": "VERIFIED"}),
            lambda d: d.update({"rater_count": 1}),
            lambda d: d["method"].update({"controls": "VALIDATED_MATCHED_CONTROLS"}),
            lambda d: d["method"].update({"preregistration": "REGISTRY_VERIFIED"}),
            lambda d: d.update({"dimensions": ["observation_one_present"]}),
        ]
        for i, edit in enumerate(edits):
            with self.subTest(case=i), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                protocol = json.loads(PROTOCOL_PATH.read_text())
                edit(protocol)
                path = root / "protocol.json"
                path.write_text(json.dumps(protocol))
                with self.assertRaises(ValueError):
                    run_pilot(protocol_path=path)

    def test_no_unintended_mutation_and_deterministic_protocol_report(self):
        before = [p.read_bytes() for p in (SAT_LEAN, PROTOCOL_PATH)]
        first = run_pilot()
        second = run_pilot()
        self.assertEqual(first, second)
        self.assertEqual(before, [p.read_bytes() for p in (SAT_LEAN, PROTOCOL_PATH)])
        self.assertEqual(
            first["protocol_sha256"],
            hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
