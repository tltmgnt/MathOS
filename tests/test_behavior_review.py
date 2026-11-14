"""Adversarial use-card regressions: false promotion, honest scope and provenance."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from mathos.research.behavior_review import (
    CARDS_PATH, DECISIONS, KEYS, REGISTRATION_PATH, run_behavior_review,
)
from mathos.research.theorem_assurance import SAT_LEAN


class BehaviorReviewTests(unittest.TestCase):
    def test_generated_cards_hide_answer_keys_and_do_not_claim_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            report = run_behavior_review(output_dir=out)
            prompts = json.loads((out / "participant_cards.json").read_text())
            self.assertEqual(report["card_count"], 7)
            self.assertEqual(prompts["kind"], "ADVERSARIAL_RESEARCH_USE_CARDS")
            self.assertEqual(len(prompts["cards"]), 7)
            self.assertEqual(set(prompts["decisions"]), set(DECISIONS))
            self.assertTrue(all("expected_decision" not in x
                                and "rationale" not in x
                                and "required_observations" not in x
                                for x in prompts["cards"]))
            self.assertEqual(report["study_status"], "NOT_CONDUCTED_EXTERNALLY")
            self.assertEqual(report["actual_independent_review"], "NOT_VERIFIED")
            self.assertIsNone(report["evaluation"])
            self.assertEqual(report["clay_solution"], "NOT_CERTIFIED")

    def _responses(self, parent: Path, mutate=None):
        output = parent / "cards"
        run_behavior_review(output_dir=output)
        responses = json.loads((output / "blank_responses.json").read_text())
        for row in responses["responses"]:
            row["decision"] = KEYS[row["case_id"]]
            row["evidence_notes"] = (
                "Independent-style fixture only: the word-list theorem cannot "
                "validate full Clay claims or arbitrary algorithmic lower bounds."
            )
            row["source_reference"] = "formal/SATSupport.lean from test fixture"
        if mutate:
            mutate(responses)
        answer_file = parent / "fixture_responses.json"
        answer_file.write_text(json.dumps(responses), encoding="utf-8")
        return answer_file

    def test_key_comparison_is_not_behavioral_or_peer_review_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            path = self._responses(base)
            report = run_behavior_review(response_path=path)
            result = report["evaluation"]
            self.assertEqual(result["decision_key_matches"], 7)
            self.assertEqual(result["total_cases"], 7)
            self.assertFalse(result["behavioral_competence_verified"])
            self.assertEqual(result["independent_mathematical_review"],
                             "NOT_PERFORMED")
            self.assertTrue(all(x["human_mathematical_evaluation"]
                                == "NOT_PERFORMED" for x in result["grades"]))
            self.assertTrue(all(not x["expert_independence_authenticated"]
                                for x in result["grades"]))
            self.assertEqual(result["clay_solution"], "NOT_CERTIFIED")

    def test_wrong_decision_counts_only_labels_not_reason_quality(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            path = self._responses(base, lambda d: d["responses"][0].update({
                "decision": "ACCEPT_LIMITED_SCOPE"
            }))
            r = run_behavior_review(response_path=path)["evaluation"]
            self.assertEqual(r["decision_key_matches"], 6)
            self.assertFalse(r["behavioral_competence_verified"])
            self.assertEqual(r["grades"][0]["key_decision"], "REJECT_PROMOTION")

    def test_tampered_source_and_casebook_digests_rejected(self):
        for field in ("source_sha256", "casebook_sha256"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                answer = self._responses(root, lambda d: d.update({field: "0" * 64}))
                with self.assertRaisesRegex(ValueError, "exact reviewed sources"):
                    run_behavior_review(response_path=answer)

    def test_missing_or_duplicate_cases_rejected(self):
        edits = [
            lambda d: d["responses"].pop(),
            lambda d: d["responses"].append(d["responses"][0]),
            lambda d: d["responses"][1].update({"case_id": "BHV-01"}),
            lambda d: d["responses"][1].update({"case_id": "BHV-99"}),
        ]
        for i, edit in enumerate(edits):
            with self.subTest(i=i), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                answer = self._responses(root, edit)
                with self.assertRaises(ValueError):
                    run_behavior_review(response_path=answer)

    def test_empty_justifications_and_untrusted_markers_rejected(self):
        edits = [
            lambda d: d["responses"][1].update({"evidence_notes": ""}),
            lambda d: d["responses"][1].update({"source_reference": ""}),
            lambda d: d["responses"][1].update({"decision": "CLAY_SOLVED"}),
            lambda d: d.update({"participant_label": "../../escapes"}),
            lambda d: d.update({"independent_expert_approved": True}),
            lambda d: d["responses"][1].update({"peer_reviewed": True}),
        ]
        for i, edit in enumerate(edits):
            with self.subTest(i=i), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                answer = self._responses(root, edit)
                with self.assertRaises(ValueError):
                    run_behavior_review(response_path=answer)

    def test_casebook_status_promotion_and_key_tampering_fails(self):
        edits = [
            lambda d: d["policy"].update({"behavior_study": "COMPLETE"}),
            lambda d: d["policy"].update({"external_reviewer_verification": "VERIFIED"}),
            lambda d: d["policy"].update({"clay_solution": "CERTIFIED"}),
            lambda d: d["policy"].update({"auto_mathematical_truth_assessment": True}),
            lambda d: d["cases"][0].update({"expected_decision": "ACCEPT_LIMITED_SCOPE"}),
            lambda d: d["cases"].pop(),
            lambda d: d["cases"].append(copy.deepcopy(d["cases"][0])),
        ]
        for i, edit in enumerate(edits):
            with self.subTest(i=i), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                cases = json.loads(CARDS_PATH.read_text())
                edit(cases)
                path = root / "cards.json"
                path.write_text(json.dumps(cases))
                with self.assertRaises(ValueError):
                    run_behavior_review(casebook_path=path)

    def test_reproducible_packets_and_protected_sources(self):
        paths = (CARDS_PATH, SAT_LEAN, REGISTRATION_PATH)
        before = [p.read_bytes() for p in paths]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            r1 = run_behavior_review(output_dir=root / "a")
            r2 = run_behavior_review(output_dir=root / "b")
            self.assertEqual(r1, r2)
            self.assertEqual(
                (root / "a" / "participant_cards.json").read_bytes(),
                (root / "b" / "participant_cards.json").read_bytes())
            self.assertEqual(r1["source_sha256"],
                             hashlib.sha256(SAT_LEAN.read_bytes()).hexdigest())
        self.assertEqual(before, [p.read_bytes() for p in paths])


if __name__ == "__main__":
    unittest.main()
