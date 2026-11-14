"""Bridge-focused Clay agent regression tests: identity, provenance and no promotion."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mathos.research.agentic_clay import OfflineBackend, main, run_agent
from mathos.research.clay_proof_topology import EXTERNAL_PATH, ROUTES_PATH
from mathos.research.clay_alignment import TARGETS_PATH
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS


class DriftingBackend(OfflineBackend):
    def complete(self, role, context):
        result = super().complete(role, context)
        if role == "proposer":
            result["lemma_statement"] = "A different unrelated lemma"
        return result


class FakeCertifiedBackend(OfflineBackend):
    def complete(self, role, context):
        result = super().complete(role, context)
        if role == "proposer":
            result["clay_bridge_status"] = "PROVED: " + context["focus"]["claim_id"]
        return result


class TrackingBackend(OfflineBackend):
    def __init__(self):
        self.contexts = []

    def complete(self, role, context):
        self.contexts.append((role, context))
        return super().complete(role, context)


class BridgeAgentFocusTests(unittest.TestCase):
    def test_all_seven_have_traced_open_claims_and_no_certification(self):
        report = run_agent(OfflineBackend(), rounds=1, max_model_calls=28)
        self.assertEqual(report["orchestrator"], "MathOS/agentic-clay-v2-bridge-focused")
        self.assertEqual(report["bounded_model_calls"], 28)
        self.assertEqual(report["topology_bridges_still_open"], 10)
        self.assertEqual(report["open_work_packages"], 14)
        self.assertEqual(report["certification"], "NOT_CERTIFIED")
        self.assertEqual(report["proof_topology_route_sufficiency"], "NOT_VALIDATED")
        self.assertEqual(len(report["packets"]), 7)
        for packet in report["packets"]:
            focus = packet["research_focus"]
            self.assertEqual(packet["traceable_claim_id"], focus["claim_id"])
            self.assertIn(focus["claim_id"], packet["iterations"][0]["proposal"]["lemma_statement"])
            self.assertFalse(packet["proof_completed"])
            self.assertFalse(packet["route_sufficiency_validated"])
            self.assertFalse(packet["counterexample_search_completed"])
            self.assertFalse(packet["novelty_checked"])
            self.assertFalse(packet["formal_verification_completed"])
            self.assertFalse(packet["independent_mathematical_review"])
            self.assertEqual(focus["priority_basis"], "AUTHOR_ORDER_NOT_DIFFICULTY_OR_RELEVANCE")
            self.assertTrue(focus["claim_statement"])
            self.assertTrue(focus["quantifiers"])
            self.assertEqual(packet["iterations"][0]["falsification_plan_executed"], False)
        self.assertEqual(
            next(p for p in report["packets"] if p["model_key"] == "Poincare")["traceable_claim_id"],
            "POINCARE.reconstruction",
        )

    def test_explicit_navier_stokes_forced_route_targets_correct_bridge(self):
        backend = TrackingBackend()
        report = run_agent(
            backend, track="Navier-Stokes", route_id="NS.C",
            claim_id="BRIDGE.NS.C_forced_breakdown",
            rounds=1, max_model_calls=4,
        )
        p = report["packets"][0]
        self.assertEqual(p["research_focus"]["alternative"], "C_forced_R3_breakdown")
        self.assertEqual(p["research_focus"]["claim_kind"], "PROPOSED_BRIDGE")
        self.assertEqual(p["research_focus"]["other_open_dependencies"], [])
        self.assertEqual(p["traceable_claim_id"], "BRIDGE.NS.C_forced_breakdown")
        self.assertIn("R3", p["research_focus"]["quantifiers"])
        self.assertIn("BRIDGE.NS.C_forced_breakdown",
                      p["iterations"][0]["proposal"]["clay_bridge_status"])
        self.assertEqual([role for role, _ in backend.contexts],
                         ["planner", "proposer", "skeptic", "reviewer"])
        self.assertTrue(all(ctx["focus"]["route_id"] == "NS.C"
                            for _, ctx in backend.contexts))
        self.assertEqual(p["evidence"]["verification_level"],
                         "FINITE_OR_CONDITIONAL_REGRESSION")

    def test_canonical_obligation_can_be_focused(self):
        packet = run_agent(
            OfflineBackend(), track="P-versus-NP", route_id="PNP.equality",
            claim_id="PNP.sat_runtime", rounds=1, max_model_calls=4,
        )["packets"][0]
        self.assertEqual(packet["research_focus"]["claim_kind"],
                         "CANONICAL_OPEN_OBLIGATION")
        self.assertEqual(packet["traceable_claim_id"], "PNP.sat_runtime")
        self.assertEqual(packet["research_focus"]["other_open_dependencies"],
                         ["PNP.sat_correctness", "BRIDGE.PNP.sat_to_class"])
        self.assertFalse(packet["promoted_to_solution"])

    def test_other_alternative_remains_open(self):
        p = run_agent(
            OfflineBackend(), track="P-versus-NP",
            route_id="PNP.separation", rounds=1, max_model_calls=4,
        )["packets"][0]
        self.assertEqual(p["traceable_claim_id"],
                         "BRIDGE.PNP.unrestricted_lower_bound")
        self.assertEqual(p["research_focus"]["alternative"], "P_not_equals_NP")
        self.assertEqual(len(p["research_focus"]["all_modeled_minimal_completion_sets"]), 2)

    def test_reject_unknown_route_wrong_track_or_wrong_claim(self):
        selections = [
            ("Navier-Stokes", "NS.Z", None),
            ("Hodge", "NS.C", None),
            ("Riemann", "RH.spectral", "BRIDGE.NS.C_forced_breakdown"),
            ("P-versus-NP", "PNP.separation", "PNP.sat_runtime"),
        ]
        for track, route, claim in selections:
            with self.subTest(route=route, claim=claim), self.assertRaises(ValueError):
                run_agent(OfflineBackend(), track=track, route_id=route,
                          claim_id=claim, rounds=1, max_model_calls=4)

    def test_reject_claim_without_route_and_cross_track_all_selection(self):
        with self.assertRaisesRegex(ValueError, "requires --route-id"):
            run_agent(OfflineBackend(), track="Riemann",
                      claim_id="RH.operator", rounds=1, max_model_calls=4)
        with self.assertRaisesRegex(ValueError, "single Clay track"):
            run_agent(OfflineBackend(), route_id="RH.spectral", rounds=1)

    def test_proposer_must_trace_claim_and_never_claim_proved(self):
        for backend in (DriftingBackend(), FakeCertifiedBackend()):
            with self.subTest(backend=type(backend).__name__), self.assertRaisesRegex(
                ValueError, "candidate drift or unsupported proof status"
            ):
                run_agent(backend, track="Riemann", rounds=1, max_model_calls=4)

    def test_source_hashes_unchanged_and_contain_proof_route_ledger(self):
        paths = [TARGETS_PATH, OBLIGATIONS, HYPOTHESES, ROUTES_PATH, EXTERNAL_PATH]
        original = [p.read_bytes() for p in paths]
        report = run_agent(OfflineBackend(), track="Hodge", rounds=1,
                           max_model_calls=4)
        self.assertEqual(original, [p.read_bytes() for p in paths])
        self.assertEqual(set(report["source_sha256"]),
                         {"clay_targets", "obligations", "hypotheses",
                          "routes", "external"})

    def test_invalid_route_manifest_prevents_agent_calls(self):
        with tempfile.TemporaryDirectory() as d:
            manifest = Path(d) / "tampered.json"
            raw = json.loads(ROUTES_PATH.read_text())
            raw["routes"][0]["obligations"] = []
            manifest.write_text(json.dumps(raw))
            backend = TrackingBackend()
            with self.assertRaises(ValueError):
                run_agent(backend, track="Riemann", rounds=1,
                          max_model_calls=4, routes_path=manifest)
            self.assertEqual(backend.contexts, [])

    def test_external_announcement_cannot_be_promoted(self):
        with tempfile.TemporaryDirectory() as d:
            manifest = Path(d) / "external.json"
            raw = json.loads(EXTERNAL_PATH.read_text())
            raw["events"][1]["state"] = "ACCEPTED_EXTERNAL"
            manifest.write_text(json.dumps(raw))
            with self.assertRaises(ValueError):
                run_agent(OfflineBackend(), track="Navier-Stokes",
                          rounds=1, max_model_calls=4, external_path=manifest)

    def test_cli_writes_traceable_unverified_review_packet(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.dict("os.environ", {"OPENAI_API_KEY": ""}):
                main(["--provider", "offline", "--track", "Navier-Stokes",
                      "--route-id", "NS.D",
                      "--claim-id", "BRIDGE.NS.D_forced_breakdown",
                      "--rounds", "1", "--max-model-calls", "4",
                      "--output-dir", d])
            result = json.loads((Path(d) / "agentic_research_report.json").read_text())
            packet = result["packets"][0]
            handoff = (Path(d) / "agentic_research_handoff.md").read_text()
            self.assertEqual(packet["traceable_claim_id"],
                             "BRIDGE.NS.D_forced_breakdown")
            self.assertFalse(packet["novelty_checked"])
            self.assertIn("Candidate route (NOT VALIDATED)", handoff)
            self.assertIn("Counterexample check to attempt (NOT RUN)", handoff)


if __name__ == "__main__":
    unittest.main()
