"""Regression checks for Clay full-target alignment and blocked-proof guardrails."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from mathos.research.clay_alignment import (
    EXPECTED_CLAY_URLS, EXPECTED_STATUS, TARGETS_PATH, audit_clay_alignment,
)
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS


class ClayOfficialTargetAlignmentTests(unittest.TestCase):
    def test_full_traceability_is_not_scientific_certification(self):
        report = audit_clay_alignment()
        self.assertEqual(report["certification"], "NOT_CERTIFIED")
        self.assertEqual(report["open_work_packages"], 14)
        self.assertEqual(report["proof_readiness"],
                         "NO_COMPLETE_SOLUTION_SUBMITTED_OR_VERIFIED")
        self.assertEqual(report["clay_prize_readiness"], "NOT_ELIGIBLE")
        self.assertIn("NOT CLAY RELEVANCE", report["coverage_score"])
        self.assertEqual(report["coverage_dimension_count"], 10)
        self.assertTrue(report["all_seven_targets_structurally_complete"])
        self.assertEqual(len(report["targets"]), 7)
        for item in report["targets"]:
            self.assertEqual(item["field_coverage"]["completed"], 10)
            self.assertEqual(item["field_coverage"]["total"], 10)
            self.assertEqual(item["mathos_status"], "BLOCKED")
            self.assertEqual(item["mathos_certification"], "NOT_CERTIFIED")
            self.assertFalse(item["current_probe_proves_full_target"])
            self.assertFalse(item["proof_completed"])
            self.assertFalse(item["independent_review_completed"])
            self.assertTrue(item["required_missing_bridge"])

    def test_all_official_problem_sources_and_statuses(self):
        report = audit_clay_alignment()
        self.assertEqual({t["model_key"] for t in report["targets"]},
                         set(EXPECTED_CLAY_URLS))
        for t in report["targets"]:
            self.assertEqual(t["official_source"],
                             EXPECTED_CLAY_URLS[t["model_key"]])
            self.assertEqual(t["official_status"],
                             EXPECTED_STATUS[t["model_key"]])
        poincare = next(t for t in report["targets"] if t["model_key"] == "Poincare")
        self.assertEqual(poincare["official_status"], "SOLVED_EXTERNALLY")
        self.assertEqual(report["certification"], "NOT_CERTIFIED")

    def test_hypotheses_and_canonical_register_not_mutated(self):
        old = [path.read_bytes() for path in (TARGETS_PATH, OBLIGATIONS, HYPOTHESES)]
        audit_clay_alignment()
        self.assertEqual(old, [path.read_bytes() for path in
                               (TARGETS_PATH, OBLIGATIONS, HYPOTHESES)])

    def test_official_target_statements_include_full_quantifiers(self):
        obj = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))
        keyed = {t["model_key"]: t for t in obj["targets"]}
        self.assertEqual(len(keyed), 7)
        self.assertIn("every nontrivial zero", keyed["Riemann"]["official_target"])
        self.assertIn("NP", keyed["P-versus-NP"]["official_target"])
        self.assertIn("four", keyed["Navier-Stokes"]["permitted_solution_type"])
        self.assertIn("every compact simple gauge group",
                      keyed["Yang-Mills"]["official_target"])
        self.assertIn("every smooth complex projective variety",
                      keyed["Hodge"]["official_target"])
        self.assertIn("every elliptic curve E over Q",
                      keyed["Birch-Swinnerton-Dyer"]["official_target"])
        self.assertIn("already solved", keyed["Poincare"]["permitted_solution_type"])
        self.assertIn("not a non-Abelian gauge field",
                      keyed["Yang-Mills"]["probe_limit"])

    def _tamper_and_run(self, change, file_kind="targets"):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = {
                "targets": root / "targets.json",
                "register": root / "register.json",
                "hypotheses": root / "hypotheses.json",
            }
            originals = {
                "targets": json.loads(TARGETS_PATH.read_text()),
                "register": json.loads(OBLIGATIONS.read_text()),
                "hypotheses": json.loads(HYPOTHESES.read_text()),
            }
            change(originals[file_kind])
            for name, path in paths.items():
                path.write_text(json.dumps(originals[name]), encoding="utf-8")
            return audit_clay_alignment(paths["targets"], paths["register"],
                                        paths["hypotheses"])

    def test_reject_omitted_quantifier_and_source(self):
        for kind in ("quantifier", "wrong_url", "missing_bridge"):
            def mutation(doc):
                first = doc["targets"][0]
                if kind == "quantifier":
                    first["official_target"] = "a simple statement"
                elif kind == "wrong_url":
                    first["clay_problem_page"] = "https://example.com/fake-clay"
                else:
                    first["missing_bridge"] = ""
            with self.subTest(kind=kind):
                with self.assertRaises(ValueError):
                    self._tamper_and_run(mutation)

    def test_reject_fake_clay_prize_eligibility(self):
        def mutation(doc):
            doc["cmi_gate"]["qualifying_publication"] = True
        with self.assertRaises(ValueError):
            self._tamper_and_run(mutation)

    def test_reject_mathos_certificate_promotion(self):
        def mutation(doc):
            doc["policy"]["proof_status"] = "PROVED"
        with self.assertRaises(ValueError):
            self._tamper_and_run(mutation)

    def test_reject_canonical_closed_obligation(self):
        def mutation(register):
            register["tracks"][0]["work_packages"][0]["graph_state"] = "closed"
        with self.assertRaises(ValueError):
            self._tamper_and_run(mutation, "register")

    def test_reject_poincare_misrepresented_as_unsolved(self):
        def mutation(doc):
            next(t for t in doc["targets"] if t["model_key"] == "Poincare")["clay_status"] = "UNSOLVED"
        with self.assertRaises(ValueError):
            self._tamper_and_run(mutation)

    def test_reject_changed_legacy_probe(self):
        def mutation(doc):
            next(t for t in doc["targets"] if t["model_key"] == "P-versus-NP")["current_probe"] = "unrestricted_sat_solver"
        with self.assertRaises(ValueError):
            self._tamper_and_run(mutation)

    def test_reject_duplicate_target(self):
        def mutation(doc):
            doc["targets"][0]["model_key"] = doc["targets"][1]["model_key"]
        with self.assertRaises(ValueError):
            self._tamper_and_run(mutation)


if __name__ == "__main__":
    unittest.main()
