"""Agentic Clay orchestration: strict budgets, model isolation and no proof promotion."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mathos.research.agentic_clay import (
    ROLE_FIELDS, OfflineBackend, OpenAIResponsesBackend, _validate,
    _write_packet, main, run_agent,
)
from mathos.research.clay_alignment import TARGETS_PATH
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS


class CountingOfflineBackend(OfflineBackend):
    def __init__(self):
        self.calls: list[tuple[str, int | None]] = []

    def complete(self, role, context):
        self.calls.append((role, context.get("iteration")))
        return super().complete(role, context)


class RevisingBackend(CountingOfflineBackend):
    def complete(self, role, context):
        answer = super().complete(role, context)
        if role == "skeptic" and context.get("iteration") == 2:
            answer["verdict"] = "NO_OBVIOUS_FLAW"
        if role == "reviewer" and context.get("iteration") == 2:
            answer["verdict"] = "HUMAN_REVIEW_REQUIRED"
        return answer


class RejectingBackend(CountingOfflineBackend):
    def complete(self, role, context):
        answer = super().complete(role, context)
        if role == "skeptic":
            answer["verdict"] = "REJECT"
        return answer


class ForgedVerdictBackend(OfflineBackend):
    def complete(self, role, context):
        answer = super().complete(role, context)
        if role == "reviewer":
            answer["verdict"] = "PROVED_CLAY"
        return answer


class OmittedFieldBackend(OfflineBackend):
    def complete(self, role, context):
        answer = super().complete(role, context)
        if role == "proposer":
            del answer["clay_bridge_status"]
        return answer


class AgenticClayResearchTests(unittest.TestCase):
    def test_all_seven_tracks_run_as_explicit_offline_simulation(self):
        backend = CountingOfflineBackend()
        report = run_agent(backend, rounds=2)
        self.assertEqual(report["provider"], "offline_simulation")
        self.assertFalse(report["ai_generated"])
        self.assertEqual(len(report["packets"]), 7)
        self.assertEqual(len(report["selected_tracks"]), 7)
        self.assertEqual(report["bounded_model_calls"], 49)
        self.assertEqual(len(backend.calls), 49)
        self.assertEqual(report["certification"], "NOT_CERTIFIED")
        self.assertEqual(report["clay_prize_readiness"], "NOT_ELIGIBLE")
        self.assertEqual(report["open_work_packages"], 14)
        self.assertEqual(report["proof_promotion"], "NONE")
        self.assertTrue(report["human_review_required"])
        self.assertFalse(report["automatic_merge_or_claim_promotion"])
        for packet in report["packets"]:
            self.assertEqual(packet["agent_state"], "OFFLINE_TEMPLATE_ONLY")
            self.assertEqual(packet["certification"], "NOT_CERTIFIED")
            self.assertFalse(packet["proof_completed"])
            self.assertFalse(packet["promoted_to_solution"])
            self.assertFalse(packet["clay_prize_eligible"])
            self.assertEqual(len(packet["iterations"]), 2)
            self.assertTrue(packet["evidence"]["bounded_result"]["passed"])
            self.assertFalse(packet["evidence"]["proves_clay_target"])
            self.assertIn("UNPROVEN", packet["iterations"][-1]
                          ["proposal"]["clay_bridge_status"])

    def test_one_track_exact_role_handoff_and_revision(self):
        backend = RevisingBackend()
        result = run_agent(backend, track="Navier-Stokes", rounds=3,
                           max_model_calls=10)
        self.assertEqual(result["bounded_model_calls"], 7)
        self.assertEqual(
            backend.calls,
            [("planner", None), ("proposer", 1), ("skeptic", 1),
             ("reviewer", 1), ("proposer", 2), ("skeptic", 2), ("reviewer", 2)]
        )
        packet = result["packets"][0]
        self.assertEqual(len(packet["iterations"]), 2)
        self.assertEqual(packet["iterations"][0]["reviewer"]["verdict"], "REVISE")
        self.assertEqual(packet["iterations"][1]["reviewer"]["verdict"],
                         "HUMAN_REVIEW_REQUIRED")
        self.assertFalse(packet["promoted_to_solution"])

    def test_skeptic_can_stop_bad_candidate(self):
        backend = RejectingBackend()
        packet = run_agent(backend, track="Riemann", rounds=3,
                           max_model_calls=10)["packets"][0]
        self.assertEqual(len(packet["iterations"]), 1)
        self.assertEqual(backend.calls[-1][0], "reviewer")
        self.assertEqual(packet["iterations"][0]["skeptic"]["verdict"], "REJECT")
        self.assertFalse(packet["proof_completed"])

    def test_reject_forged_model_certification(self):
        with self.assertRaisesRegex(ValueError, "non-certification verdict"):
            run_agent(ForgedVerdictBackend(), track="Riemann", rounds=1,
                      max_model_calls=4)

    def test_reject_malformed_structured_model_response(self):
        with self.assertRaisesRegex(ValueError, "fields differ"):
            run_agent(OmittedFieldBackend(), track="Riemann", rounds=1,
                      max_model_calls=4)
        self.assertEqual(len(ROLE_FIELDS), 4)
        with self.assertRaises(ValueError):
            _validate("skeptic", {"verdict": "SOLVED"})

    def test_budget_rounds_and_unknown_tracks_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "budget too small"):
            run_agent(OfflineBackend(), rounds=2, max_model_calls=48)
        with self.assertRaisesRegex(ValueError, "rounds"):
            run_agent(OfflineBackend(), rounds=0)
        with self.assertRaisesRegex(ValueError, "rounds"):
            run_agent(OfflineBackend(), rounds=4)
        with self.assertRaisesRegex(ValueError, "unknown Clay track"):
            run_agent(OfflineBackend(), track="Goldbach", rounds=1)
        with self.assertRaisesRegex(ValueError, "max_model_calls"):
            run_agent(OfflineBackend(), track="Hodge", max_model_calls=0)

    def test_original_canonical_register_unchanged(self):
        targets = TARGETS_PATH.read_bytes()
        obligations = OBLIGATIONS.read_bytes()
        hypotheses = HYPOTHESES.read_bytes()
        run_agent(OfflineBackend(), track="Poincare", rounds=2)
        self.assertEqual(TARGETS_PATH.read_bytes(), targets)
        self.assertEqual(OBLIGATIONS.read_bytes(), obligations)
        self.assertEqual(HYPOTHESES.read_bytes(), hypotheses)

    def test_tampered_proof_register_blocks_agent(self):
        with tempfile.TemporaryDirectory() as d:
            r = Path(d) / "register.json"
            x = json.loads(OBLIGATIONS.read_text())
            x["tracks"][0]["work_packages"][0]["graph_state"] = "closed"
            r.write_text(json.dumps(x))
            with self.assertRaisesRegex(ValueError, "promoted"):
                run_agent(OfflineBackend(), track="Hodge", rounds=1,
                          obligations_path=r, max_model_calls=4)

    def test_agent_reports_are_readable_and_inert(self):
        packet = run_agent(OfflineBackend(), track="Yang-Mills", rounds=1,
                           max_model_calls=4)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "evidence"
            _write_packet(output, packet)
            data = json.loads((output / "agentic_research_report.json").read_text())
            note = (output / "agentic_research_handoff.md").read_text()
            self.assertEqual(data["certification"], "NOT_CERTIFIED")
            self.assertEqual(data["proof_promotion"], "NONE")
            self.assertIn("Human mathematical review required", note)
            self.assertIn("Yang-Mills", note)
            self.assertIn("No theorem is derived", note)

    def test_cli_offline_without_secrets(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.dict("os.environ", {"OPENAI_API_KEY": ""}):
                main(["--provider", "offline", "--track", "Hodge", "--rounds",
                      "1", "--max-model-calls", "4", "--output-dir", d])
            self.assertTrue((Path(d) / "agentic_research_report.json").exists())

    def test_live_mode_requires_explicit_credentials_and_model(self):
        with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
            OpenAIResponsesBackend(model="example-model", api_key="")
        with self.assertRaisesRegex(ValueError, "model"):
            OpenAIResponsesBackend(model="", api_key="dummy-secret")

    def test_responses_api_payload_is_bounded_no_tools_no_storage(self):
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def read(self, count=-1):
                sample = {
                    "status": "completed", "output": [{
                        "type": "message", "content": [{
                            "type": "output_text",
                            "text": json.dumps({
                                "research_question": "Can a conditional bound be proved?",
                                "scope": "All admissible data with explicit assumptions.",
                                "attack_plan": "Try a counterexample first.",
                                "success_criterion": "Expert-reviewed complete proof.",
                            }),
                        }]
                    }]
                }
                return json.dumps(sample).encode()

        backend = OpenAIResponsesBackend(model="example-model", api_key="dummy")
        context = {"target": {"direct_research_test": "bounded test"}}
        with patch("mathos.research.agentic_clay.urlopen",
                   return_value=FakeResponse()) as mocked:
            answer = backend.complete("planner", context)
        self.assertIn("research_question", answer)
        request = mocked.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(payload["model"], "example-model")
        self.assertEqual(payload["store"], False)
        self.assertLessEqual(payload["max_output_tokens"], 1800)
        self.assertNotIn("tools", payload)
        self.assertIn("only", payload["instructions"].lower())
        self.assertEqual(request.full_url, "https://api.openai.com/v1/responses")

    def test_live_api_output_cannot_claim_theorem_via_verdict(self):
        fake = {
            "status": "completed", "output": [{
                "type": "message", "content": [{
                    "type": "output_text",
                    "text": json.dumps({
                        "verdict": "CERTIFIED",
                        "reason": "proof!",
                        "next_action": "publish",
                        "evidence_assessment": "all done",
                    })
                }]
            }]
        }
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def read(self, n=-1):
                return json.dumps(fake).encode()
        backend = OpenAIResponsesBackend(model="example-model", api_key="dummy")
        with patch("mathos.research.agentic_clay.urlopen",
                   return_value=FakeResponse()):
            with self.assertRaisesRegex(ValueError, "non-certification verdict"):
                backend.complete("reviewer", {"target": "stub"})


if __name__ == "__main__":
    unittest.main()
