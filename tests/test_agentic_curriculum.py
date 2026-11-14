"""Curriculum progression is a verified plan, never a self-issued mathematical grade."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from mathos.research.agentic_curriculum import (
    EXPECTED_COMPLETION_POLICY, SYLLABUS,
    build_curriculum_plan, main, rehearse_plan,
)
from mathos.research.clay_alignment import TARGETS_PATH
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS


class AgenticCurriculumTests(unittest.TestCase):
    def test_full_six_module_24_week_plan(self):
        plan = build_curriculum_plan()
        self.assertEqual(plan["duration_weeks"], 24)
        self.assertEqual(plan["workload_hours_per_week"], [8, 12])
        self.assertEqual(plan["weeks_covered"], list(range(1, 25)))
        self.assertEqual(len(plan["modules"]), 6)
        self.assertEqual(len(plan["selected_tracks"]), 7)
        self.assertEqual(plan["open_work_packages"], 14)
        self.assertEqual(plan["certification"], "NOT_CERTIFIED")
        self.assertEqual(plan["mathematical_claim_promotion"], "NONE")
        self.assertFalse(plan["rubric_assessed"])
        self.assertTrue(plan["human_assessment_required"])
        self.assertFalse(plan["clay_prize_eligibility"])
        self.assertEqual(sum(plan["rubric_points"].values()), 100)
        for module in plan["modules"]:
            self.assertFalse(module["gate_assessed"])
            self.assertEqual(len(module["weekly"]), 4)

    def test_all_seven_canonical_problem_tracks(self):
        plan = build_curriculum_plan()
        registry = json.loads(OBLIGATIONS.read_text())
        expected = {t["model_key"] for t in registry["tracks"]}
        self.assertEqual({t["model_key"] for t in plan["selected_tracks"]}, expected)
        for entry in plan["selected_tracks"]:
            self.assertEqual(entry["learning_state"], "CURRICULUM_PLAN_ONLY")
            self.assertEqual(entry["mathematical_state"], "BLOCKED")
            self.assertFalse(entry["completion_awarded"])
            self.assertTrue(entry["missing_global_proof"])
            self.assertTrue(entry["first_probe_id"])
            self.assertTrue(entry["official_problem_source"].startswith(
                "https://www.claymath.org/"
            ))
            self.assertGreaterEqual(len(entry["prerequisites"]), 3)

    def test_select_one_problem_keeps_common_study_plan(self):
        single = build_curriculum_plan(track="Navier-Stokes")
        self.assertEqual(len(single["selected_tracks"]), 1)
        self.assertEqual(single["selected_tracks"][0]["model_key"], "Navier-Stokes")
        self.assertEqual(single["selected_tracks"][0]["first_probe_id"],
                         "abc_perturbation_bound")
        self.assertEqual(len(single["modules"]), 6)

    def test_unknown_track_is_not_silently_selected(self):
        with self.assertRaisesRegex(ValueError, "unknown curriculum track"):
            build_curriculum_plan(track="Poincare-Extra")

    def test_source_inputs_are_not_modified(self):
        sources = (SYLLABUS, TARGETS_PATH, OBLIGATIONS, HYPOTHESES)
        before = [p.read_bytes() for p in sources]
        build_curriculum_plan()
        self.assertEqual(before, [p.read_bytes() for p in sources])

    def test_offline_agent_rehearsal_not_model_generated_or_verified(self):
        plan, report = rehearse_plan("Hodge")
        self.assertEqual(plan["rehearsal_status"],
                         "OFFLINE_SCRIPTED_SIMULATION_COMPLETED")
        self.assertFalse(plan["rehearsal_is_ai_research"])
        self.assertEqual(plan["rehearsal_model_calls"], 4)
        self.assertFalse(report["ai_generated"])
        self.assertEqual(report["provider"], "offline_simulation")
        self.assertEqual(report["certification"], "NOT_CERTIFIED")
        self.assertEqual(report["proof_promotion"], "NONE")
        self.assertEqual(len(report["packets"]), 1)
        self.assertFalse(report["packets"][0]["promoted_to_solution"])

    def test_generate_machine_readable_plan_files(self):
        with tempfile.TemporaryDirectory() as temp:
            main(["--track", "Riemann", "--output-dir", temp])
            payload = json.loads((Path(temp) / "curriculum_plan.json").read_text())
            self.assertEqual(payload["selected_tracks"][0]["model_key"], "Riemann")
            self.assertEqual(payload["rehearsal_status"], "NOT_RUN")
            self.assertFalse((Path(temp) / "offline_rehearsal").exists())

    def test_generate_rehearsal_evidence_files(self):
        with tempfile.TemporaryDirectory() as temp:
            main(["--track", "Poincare", "--rehearsal", "--output-dir", temp])
            path = Path(temp) / "offline_rehearsal"
            report = json.loads((path / "agentic_research_report.json").read_text())
            self.assertFalse(report["ai_generated"])
            self.assertEqual(report["certification"], "NOT_CERTIFIED")
            self.assertTrue((path / "agentic_research_handoff.md").exists())

    def _mutate_and_check(self, mutate_syllabus=None, mutate_register=None):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            syllabus_path = p / "syllabus.json"
            register_path = p / "obligations.json"
            syllabus = json.loads(SYLLABUS.read_text())
            register = json.loads(OBLIGATIONS.read_text())
            if mutate_syllabus:
                mutate_syllabus(syllabus)
            if mutate_register:
                mutate_register(register)
            syllabus_path.write_text(json.dumps(syllabus))
            register_path.write_text(json.dumps(register))
            return build_curriculum_plan(
                syllabus_path=syllabus_path, obligations_path=register_path
            )

    def test_reject_auto_graduation_or_proof_claim(self):
        def change(x):
            x["completion_policy"]["automatic_certification"] = True
        with self.assertRaisesRegex(ValueError, "automatic academic"):
            self._mutate_and_check(mutate_syllabus=change)

    def test_reject_inflated_learner_grade(self):
        def change(x):
            x["evaluation"]["claimed_passes_without_human_review"] = True
        with self.assertRaisesRegex(ValueError, "rubric"):
            self._mutate_and_check(mutate_syllabus=change)

    def test_reject_changed_or_duplicated_week(self):
        def change(x):
            x["modules"][0]["weekly"][3]["week"] = 3
        with self.assertRaisesRegex(ValueError, "week"):
            self._mutate_and_check(mutate_syllabus=change)

    def test_reject_wrong_first_probe_and_claims(self):
        for action in ("wrong_probe", "wrong_claims"):
            def change(x):
                if action == "wrong_probe":
                    x["tracks"][0]["first_probe"] = "made_up_experiment"
                else:
                    x["tracks"][0]["obligations"] = ["RH.missing_fake_proof"]
            with self.subTest(action=action):
                with self.assertRaises(ValueError):
                    self._mutate_and_check(mutate_syllabus=change)

    def test_reject_closed_canonical_proof_obligation(self):
        def change(x):
            x["tracks"][0]["work_packages"][0]["graph_state"] = "closed"
        with self.assertRaises(ValueError):
            self._mutate_and_check(mutate_register=change)

    def test_reject_missing_specialist_track(self):
        def change(x):
            x["tracks"].pop()
        with self.assertRaises(ValueError):
            self._mutate_and_check(mutate_syllabus=change)

    def test_reject_duplicate_deliverable(self):
        def change(x):
            x["modules"][0]["weekly"][1]["artifact"] = (
                x["modules"][0]["weekly"][0]["artifact"]
            )
        with self.assertRaisesRegex(ValueError, "unique"):
            self._mutate_and_check(mutate_syllabus=change)


if __name__ == "__main__":
    unittest.main()
