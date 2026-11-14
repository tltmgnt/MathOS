"""Regression tests for private human-only SAT1 rater disagreement adjudication.

All rating content in this test is synthetic; no person is assessed.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from mathos.research.behavior_adjudication import (
    ADJUDICATION_PROTOCOL, run_adjudication,
)
from mathos.research.behavior_pilot import run_pilot
from mathos.research.behavior_review import run_behavior_review
from mathos.research.hypothesis_pipeline import ROOT
from mathos.research.theorem_assurance import SAT_LEAN


class AdjudicationTests(unittest.TestCase):
    def _fixtures(self, root: Path, *, disagreements: bool = True):
        deck_dir = root / "deck"
        run_behavior_review(output_dir=deck_dir)
        answers = json.loads((deck_dir / "blank_responses.json").read_text())
        answers["participant_label"] = "PrivateParticipant"
        for row in answers["responses"]:
            row["decision"] = "INCONCLUSIVE"
            row["evidence_notes"] = (
                "This synthetic research exercise checks the exact Lean "
                "word-list theorem, not Clay certification or the time "
                "complexity of unrestricted SAT algorithms."
            )
            row["source_reference"] = "formal/SATSupport.lean, exact source-hash bound"
        response_path = root / "response.json"
        response_path.write_text(json.dumps(answers), encoding="utf-8")
        preparation = root / "preparation"
        run_pilot(
            response_path=response_path,
            consent_attested=True,
            output_dir=preparation,
        )
        template = json.loads(
            (preparation / "private_rater_template.json").read_text()
        )
        files = []
        for ix, handle in enumerate(("Reader_A", "Reader_B")):
            rater = copy.deepcopy(template)
            rater["rater_pseudonym"] = handle
            rater["conflicts_declaration"] = (
                "Synthetic rater conflict statement, not verified by any "
                "human reviewer or independent research service."
            )
            for r in rater["ratings"]:
                r["observation_one_present"] = 1
                r["observation_two_present"] = 0
                r["source_reference_relevant"] = 1
                r["rater_comment"] = (
                    "Synthetic individual case reasoning only, no verified "
                    "external human expertise or real mathematical assessment."
                )
            if ix == 1 and disagreements:
                rater["ratings"][0]["observation_one_present"] = 0
                rater["ratings"][2]["source_reference_relevant"] = 0
            path = root / (handle + ".json")
            path.write_text(json.dumps(rater), encoding="utf-8")
            files.append(path)
        return response_path, files[0], files[1]

    def _adjudicator(self, root: Path, response: Path, a: Path, b: Path,
                     mutate=None) -> Path:
        run_adjudication(
            response_path=response, rater_a_path=a, rater_b_path=b,
            consent_attested=True, output_dir=root / "dispute",
        )
        file = root / "dispute" / "private_adjudicator_template.json"
        adjudicator = json.loads(file.read_text())
        adjudicator["adjudicator_pseudonym"] = "ThirdReader"
        adjudicator["conflicts_declaration"] = (
            "Self-declared unrelatedness, not independently verified. "
            "No personal identity or private contact details recorded."
        )
        for item in adjudicator["decisions"]:
            item["adjudicated_value"] = 1
            item["explanation"] = (
                "The synthetic reviewer selected a rubric observation, "
                "but no actual mathematical expertise or independent human "
                "evaluation is claimed by this test fixture."
            )
            item["source_reference"] = "formal/SATSupport.lean from synthetic fixture"
        if mutate:
            mutate(adjudicator)
        path = root / "adjudicator.json"
        path.write_text(json.dumps(adjudicator), encoding="utf-8")
        return path

    def test_protocol_mode_has_no_participant_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            report = run_adjudication(output_dir=out)
            self.assertEqual(report["status"], "PROTOCOL_ONLY_NO_HUMAN_DATA")
            self.assertFalse(report["participant_data_present"])
            self.assertFalse(report["independent_humans_authenticated"])
            self.assertFalse(report["study_validated"])
            self.assertEqual(report["clay_solution"], "NOT_CERTIFIED")
            self.assertFalse((out / "private_disagreement_packet.json").exists())

    def test_consent_and_both_raters_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            response, a, b = self._fixtures(root)
            with self.assertRaisesRegex(ValueError, "consent"):
                run_adjudication(response_path=response, rater_a_path=a, rater_b_path=b)
            with self.assertRaisesRegex(ValueError, "two complete"):
                run_adjudication(response_path=response, rater_a_path=a,
                                consent_attested=True)

    def test_disagreement_packet_is_partially_blinded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            response, a, b = self._fixtures(root)
            out = root / "adjudication"
            r = run_adjudication(
                response_path=response, rater_a_path=a, rater_b_path=b,
                consent_attested=True, output_dir=out,
            )
            self.assertEqual(r["status"],
                             "DISAGREEMENTS_REQUIRE_HUMAN_ADJUDICATION")
            self.assertEqual(r["rater_disagreement_count"], 2)
            self.assertFalse(r["human_adjudication_file_supplied"])
            self.assertEqual(r["clay_solution"], "NOT_CERTIFIED")
            packet = json.loads((out / "private_disagreement_packet.json").read_text())
            self.assertEqual(len(packet["disagreements"]), 2)
            self.assertNotIn("participant_label", packet)
            self.assertNotIn("PrivateParticipant",
                             (out / "adjudication_status.json").read_text())
            self.assertNotIn("selected_decision",
                             (out / "private_disagreement_packet.json").read_text())
            self.assertIn("evidence_notes", packet["disagreements"][0])
            self.assertEqual(r["source_sha256"],
                             hashlib.sha256(SAT_LEAN.read_bytes()).hexdigest())

    def test_valid_adjudicator_file_still_does_not_authenticate_human(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            response, a, b = self._fixtures(root)
            adj = self._adjudicator(root, response, a, b)
            report = run_adjudication(
                response_path=response, rater_a_path=a, rater_b_path=b,
                adjudicator_path=adj, consent_attested=True,
            )
            self.assertEqual(report["status"],
                             "ADJUDICATION_SUBMITTED_BUT_NOT_AUTHENTICATED")
            self.assertEqual(report["adjudicated_disagreement_count"], 2)
            self.assertEqual(report["adjudicator_identity_status"], "NOT_VERIFIED")
            self.assertFalse(report["independent_humans_authenticated"])
            self.assertEqual(report["independent_mathematical_peer_review"],
                             "NOT_PERFORMED")
            self.assertEqual(report["clay_solution"], "NOT_CERTIFIED")
            self.assertEqual(report["upstream_agreement"]["pooled"]["pair_count"], 21)

    def test_no_disagreements_not_invented_adjudication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            response, a, b = self._fixtures(root, disagreements=False)
            r = run_adjudication(
                response_path=response, rater_a_path=a, rater_b_path=b,
                consent_attested=True,
            )
            self.assertEqual(r["rater_disagreement_count"], 0)
            self.assertEqual(r["status"], "NO_RATER_DISAGREEMENTS_UNAUTHENTICATED")
            self.assertFalse(r["human_adjudication_file_supplied"])

    def test_forged_adjudicator_or_stale_sources_fail_closed(self):
        edits = [
            lambda d: d.update({"independence_declaration": "VERIFIED"}),
            lambda d: d.update({"adjudicator_pseudonym": "Reader_A"}),
            lambda d: d.update({"rater_a_sha256": "0" * 64}),
            lambda d: d.update({"response_sha256": "0" * 64}),
            lambda d: d.update({"adjudication_protocol_sha256": "0" * 64}),
            lambda d: d.update({"expert_mathematical_acceptance": True}),
            lambda d: d.update({"conflicts_declaration": ""}),
        ]
        for n, change in enumerate(edits):
            with self.subTest(case=n), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                response, a, b = self._fixtures(root)
                adj = self._adjudicator(root, response, a, b, change)
                with self.assertRaises(ValueError):
                    run_adjudication(
                        response_path=response, rater_a_path=a, rater_b_path=b,
                        adjudicator_path=adj, consent_attested=True,
                    )

    def test_incorrect_adjudicated_observations_rejected(self):
        edits = [
            lambda d: d["decisions"].pop(),
            lambda d: d["decisions"].append(copy.deepcopy(d["decisions"][0])),
            lambda d: d["decisions"][1].update({"case_id": "BHV-01"}),
            lambda d: d["decisions"][0].update({"adjudicated_value": True}),
            lambda d: d["decisions"][0].update({"adjudicated_value": None}),
            lambda d: d["decisions"][0].update({"explanation": "ok"}),
            lambda d: d["decisions"][0].update({"source_reference": ""}),
            lambda d: d["decisions"][0].update({"evidence_note_sha256": "0" * 64}),
        ]
        for n, change in enumerate(edits):
            with self.subTest(case=n), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                response, a, b = self._fixtures(root)
                adj = self._adjudicator(root, response, a, b, change)
                with self.assertRaises(ValueError):
                    run_adjudication(
                        response_path=response, rater_a_path=a, rater_b_path=b,
                        adjudicator_path=adj, consent_attested=True,
                    )

    def test_input_and_output_must_stay_outside_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            response, a, b = self._fixtures(root)
            with self.assertRaisesRegex(ValueError, "outside the MathOS repository"):
                run_adjudication(
                    response_path=response, rater_a_path=a, rater_b_path=b,
                    consent_attested=True,
                    output_dir=ROOT / "artifacts" / "private-adjudication"
                )
            with self.assertRaisesRegex(ValueError, "outside the MathOS repository"):
                run_adjudication(
                    response_path=ROOT / "docs" / "uncommitted-response.json",
                    rater_a_path=a, rater_b_path=b, consent_attested=True,
                    output_dir=root / "outside"
                )

    def test_protocol_cannot_promote_clay_peer_review_or_human_study(self):
        edits = [
            lambda d: d["policy"].update({"clay_solution": "CERTIFIED"}),
            lambda d: d["policy"].update({"adjudicator_independence_verified": True}),
            lambda d: d["policy"].update({"study_validated": True}),
            lambda d: d["policy"].update({"mathematical_review_completed": True}),
            lambda d: d.update({"dimensions": ["observation_one_present"]}),
            lambda d: d.update({"adjudication_policy": "AUTO_ACCEPTED"}),
        ]
        for n, change in enumerate(edits):
            with self.subTest(case=n), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                spec = json.loads(ADJUDICATION_PROTOCOL.read_text())
                change(spec)
                file = root / "protocol.json"
                file.write_text(json.dumps(spec))
                with self.assertRaises(ValueError):
                    run_adjudication(protocol_path=file)

    def test_no_rating_or_source_mutation_and_deterministic_report(self):
        sources = [ADJUDICATION_PROTOCOL, SAT_LEAN]
        before = [p.read_bytes() for p in sources]
        r1 = run_adjudication()
        r2 = run_adjudication()
        self.assertEqual(r1, r2)
        self.assertEqual(before, [p.read_bytes() for p in sources])


if __name__ == "__main__":
    unittest.main()
