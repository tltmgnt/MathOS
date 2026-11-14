"""Regression and adversarial tests for the CMI Poincare external CERTIFIED mirror.

These tests do not certify a new Millennium solution or verify Perelman's proof.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from mathos.research.millennium_certification import (
    EVIDENCE_PATH, OTHER_MODELS, EXPECTED_EXTERNAL_RECORD,
    EXPECTED_POLICY, _canonical, _sha256, main,
    verify_external_millennium_case,
)
from mathos.research.clay_alignment import TARGETS_PATH
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS


class MillenniumExternalCertifiedUseCaseTests(unittest.TestCase):
    def test_only_cmi_awarded_poincare_is_external_certified(self):
        report = verify_external_millennium_case()
        self.assertEqual(report["status"], "CERTIFIED")
        self.assertEqual(report["status_scope"],
                         "EXTERNALLY_RECOGNIZED_MILLENNIUM_RESOLUTION")
        self.assertEqual(report["use_case"], "MILLENNIUM_EXTERNAL_CERTIFIED_POINCARE")
        self.assertEqual(report["recognized_by"], "Clay Mathematics Institute")
        self.assertEqual(report["reported_by"], "MathOS external-recognition mirror")
        self.assertEqual(report["award_recipient"], "Grigori Perelman")
        self.assertEqual(report["award_announcement_date"], "2010-03-18")
        self.assertEqual(report["external_recognized_problems"], 1)
        self.assertEqual(report["unrecognized_problems_not_certified"], 6)
        self.assertEqual(report["certified_new_mathos_millennium_proofs"], 0)
        self.assertEqual(report["mathos_open_work_packages"], 14)
        self.assertEqual(report["mathos_canonical_certification"], "NOT_CERTIFIED")
        self.assertEqual(report["canonical_proof_promotion"], "NONE")
        self.assertFalse(report["external_award_mirror_is_independent_mathos_proof"])
        self.assertEqual(len(report["all_tracks"]), 7)

        solved = [x for x in report["all_tracks"] if x["status"] == "CERTIFIED"]
        self.assertEqual(len(solved), 1)
        self.assertEqual(solved[0]["model_key"], "Poincare")
        self.assertFalse(solved[0]["independently_proved_by_mathos"])
        self.assertEqual(solved[0]["mathos_proof_status"], "NOT_CERTIFIED")
        for item in report["all_tracks"]:
            self.assertFalse(item["official_source_live_checked_by_this_run"])
            self.assertEqual(item["mathos_research_route"], "BLOCKED")

    def test_other_six_millennium_problems_remain_not_certified(self):
        report = verify_external_millennium_case()
        by_name = {x["model_key"]: x for x in report["all_tracks"]}
        self.assertEqual(set(by_name) - {"Poincare"}, set(OTHER_MODELS))
        for key in OTHER_MODELS:
            self.assertEqual(by_name[key]["status"], "NOT_CERTIFIED")
            self.assertEqual(by_name[key]["certification_scope"], "NONE")
            self.assertEqual(by_name[key]["certification_basis"], "NONE")

    def test_source_is_official_cmi_and_not_a_cryptographic_credential(self):
        report = verify_external_millennium_case()
        self.assertEqual(report["source_verification_mode"],
                         "PINNED_OFFICIAL_RECORDS_NOT_LIVE_FETCH")
        self.assertFalse(report["original_cmi_source_live_checked"])
        self.assertTrue(report["human_review_needed_for_new_external_awards"])
        self.assertIn("NOT a CMI-issued digital credential", report["meaning"])
        self.assertEqual(report["official_cmi_sources"]["award_announcement"],
                         "https://www.claymath.org/wp-content/uploads/2022/06/"
                         "Poincare-press-release.pdf")
        self.assertIn("claymath.org", report["official_cmi_sources"]["solved_listing"])

    def test_canonical_register_is_untouched_and_poincare_reconstruction_open(self):
        sources = [EVIDENCE_PATH, OBLIGATIONS, TARGETS_PATH, HYPOTHESES]
        before = [p.read_bytes() for p in sources]
        verify_external_millennium_case()
        self.assertEqual(before, [p.read_bytes() for p in sources])
        obligations = json.loads(OBLIGATIONS.read_text())
        self.assertEqual(obligations["certification"], "NOT_CERTIFIED")
        self.assertEqual(obligations["external_result"]["graph_state"],
                         "established_external")
        self.assertEqual(obligations["external_result"]["verification"],
                         "accepted_external_not_replayed")
        reconstruction = next(x for x in obligations["tracks"]
                              if x["model_key"] == "Poincare")
        self.assertEqual(reconstruction["modeled_target_status"], "BLOCKED")
        self.assertEqual([p["claim_id"] for p in reconstruction["work_packages"]],
                         ["POINCARE.reconstruction"])

    def _tampered(self, *, edit_manifest=None, edit_obligations=None,
                  edit_targets=None):
        with tempfile.TemporaryDirectory() as tmp:
            paths = {
                "manifest": Path(tmp) / "external_manifest.json",
                "obligations": Path(tmp) / "obligations.json",
                "targets": Path(tmp) / "clay_targets.json",
            }
            manifests = {
                "manifest": json.loads(EVIDENCE_PATH.read_text()),
                "obligations": json.loads(OBLIGATIONS.read_text()),
                "targets": json.loads(TARGETS_PATH.read_text()),
            }
            if edit_manifest is not None:
                edit_manifest(manifests["manifest"])
            if edit_obligations is not None:
                edit_obligations(manifests["obligations"])
            if edit_targets is not None:
                edit_targets(manifests["targets"])
            for name, file in paths.items():
                file.write_text(json.dumps(manifests[name]))
            return verify_external_millennium_case(
                evidence_path=paths["manifest"],
                obligations_path=paths["obligations"],
                targets_path=paths["targets"],
            )

    def test_reject_award_attribution_forgery(self):
        for field, value in [
            ("award_recipient", "Anonymous MathOS agent"),
            ("award_year", 2026),
            ("award_announcement_date", "2026-11-13"),
            ("canonical_claim_id", "RH.proved"),
        ]:
            def mutate(data):
                data["allowed_external_record"][field] = value
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "pinned CMI"):
                    self._tampered(edit_manifest=mutate)

    def test_reject_forged_source_domain(self):
        def change(data):
            data["allowed_external_record"]["official_problem_url"] = (
                "https://not-clay.example/poincare"
            )
        with self.assertRaises(ValueError):
            self._tampered(edit_manifest=change)

    def test_reject_added_new_certified_millennium_problem(self):
        def change(data):
            data["other_models_expected_not_certified"].remove("Riemann")
        with self.assertRaisesRegex(ValueError, "additional problem"):
            self._tampered(edit_manifest=change)

    def test_reject_claim_to_certify_new_mathos_proof(self):
        def change(data):
            data["policy"]["auto_certify_new_solutions"] = True
        with self.assertRaisesRegex(ValueError, "promotion policy"):
            self._tampered(edit_manifest=change)

    def test_reject_claim_that_mathos_replayed_perelman(self):
        def change(data):
            data["allowed_external_record"]["independent_mathos_proof_replayed"] = True
        with self.assertRaises(ValueError):
            self._tampered(edit_manifest=change)

    def test_reject_forged_clay_live_source_verification(self):
        def change(data):
            data["policy"]["claim_real_time_external_reverification"] = True
        with self.assertRaises(ValueError):
            self._tampered(edit_manifest=change)

    def test_reject_extra_certified_fields(self):
        def change(data):
            data["CERTIFIED_ALL_7"] = True
        with self.assertRaisesRegex(ValueError, "fields"):
            self._tampered(edit_manifest=change)

    def test_reject_closed_mathos_open_obligation(self):
        def change(data):
            data["tracks"][0]["work_packages"][0]["graph_state"] = "closed"
        with self.assertRaises(ValueError):
            self._tampered(edit_obligations=change)

    def test_reject_poincare_changed_to_new_unsolved_problem(self):
        def change(data):
            entry = next(t for t in data["targets"] if t["model_key"] == "Poincare")
            entry["clay_status"] = "UNSOLVED"
        with self.assertRaises(ValueError):
            self._tampered(edit_targets=change)

    def test_reject_mathos_canonical_global_certification(self):
        def change(data):
            data["certification"] = "CERTIFIED"
        with self.assertRaises(ValueError):
            self._tampered(edit_obligations=change)

    def test_deterministic_replay_and_audit_hash(self):
        first, second = verify_external_millennium_case(), verify_external_millennium_case()
        self.assertEqual(first, second)
        self.assertEqual(first["report_sha256"], _sha256(_canonical({
            k: v for k, v in first.items() if k != "report_sha256"
        })))
        self.assertEqual(first["source_sha256"]["cmi_source_manifest"],
                         _sha256(EVIDENCE_PATH.read_bytes()))
        self.assertEqual(first["source_sha256"]["canonical_obligations"],
                         _sha256(OBLIGATIONS.read_bytes()))

    def test_cli_emits_scoped_certificate_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            main(["--output-dir", tmp])
            output = Path(tmp) / "millennium_certification.json"
            self.assertTrue(output.exists())
            report = json.loads(output.read_text())
            self.assertEqual(report["status"], "CERTIFIED")
            self.assertEqual(report["certified_new_mathos_millennium_proofs"], 0)
            self.assertEqual(report["mathos_canonical_certification"], "NOT_CERTIFIED")

    def test_pinned_manifest_policy_has_no_auto_cmi_endorsement(self):
        data = json.loads(EVIDENCE_PATH.read_text())
        self.assertEqual(data["policy"], EXPECTED_POLICY)
        self.assertEqual(data["allowed_external_record"], EXPECTED_EXTERNAL_RECORD)
        self.assertFalse(data["policy"]["enable_automatic_proof_promotion"])
        self.assertEqual(data["policy"]["certificate_issuer"],
                         "MathOS evidence mirror, NOT the Clay Mathematics Institute")


if __name__ == "__main__":
    unittest.main()
