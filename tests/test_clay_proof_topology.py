"""Guard against route/bridge deletion and automatic promotion of Clay claims."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from mathos.research.clay_proof_topology import (
    ROUTES_PATH, EXTERNAL_PATH, EXPECTED_ROUTES, audit_clay_proof_topology,
)
from mathos.research.clay_alignment import TARGETS_PATH
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS


class ClayProofTopologyTests(unittest.TestCase):
    def test_all_alternatives_and_canonical_open_claims_are_visible(self):
        result = audit_clay_proof_topology()
        self.assertEqual(result["certification"], "NOT_CERTIFIED")
        self.assertEqual(result["proof_status"], "NOT_ESTABLISHED")
        self.assertEqual(result["route_sufficiency"], "NOT_VALIDATED")
        self.assertEqual(result["clay_prize_readiness"], "NOT_ELIGIBLE")
        self.assertEqual(result["official_targets"], 7)
        self.assertEqual(result["canonical_open_work_packages"], 14)
        self.assertEqual(result["additional_proposed_bridges"], 10)
        self.assertEqual(result["alternative_routes"], 11)
        self.assertTrue(result["field_coverage_is_not_proof"])
        self.assertEqual({t["model_key"] for t in result["targets"]},
                         set(EXPECTED_ROUTES))
        for track in result["targets"]:
            self.assertEqual(track["mathos_status"], "BLOCKED")
            self.assertTrue(track["minimal_completion_sets"])
            self.assertEqual(track["route_count"],
                             len(EXPECTED_ROUTES[track["model_key"]]))
            self.assertTrue(all(route["status"] == "PROPOSED_NOT_VALIDATED"
                                for route in track["candidate_routes"]))

    def test_pnp_and_ns_use_or_routes_with_and_dependencies(self):
        by_key = {t["model_key"]: t for t in audit_clay_proof_topology()["targets"]}
        pnp = by_key["P-versus-NP"]
        self.assertEqual({r["alternative"] for r in pnp["candidate_routes"]},
                         {"P_equals_NP", "P_not_equals_NP"})
        self.assertEqual(pnp["common_to_all_modeled_routes"], [])
        self.assertEqual(
            {frozenset(x) for x in pnp["minimal_completion_sets"]},
            {frozenset(("PNP.sat_correctness", "PNP.sat_runtime",
                        "BRIDGE.PNP.sat_to_class")),
             frozenset(("BRIDGE.PNP.unrestricted_lower_bound",))},
        )
        ns = by_key["Navier-Stokes"]
        self.assertEqual(ns["route_count"], 4)
        self.assertEqual({r["route_id"] for r in ns["candidate_routes"]},
                         {"NS.A", "NS.B", "NS.C", "NS.D"})
        self.assertEqual(ns["common_to_all_modeled_routes"], [])
        self.assertEqual(len(ns["minimal_completion_sets"]), 4)
        self.assertTrue(any(x == ["BRIDGE.NS.C_forced_breakdown"]
                            for x in ns["minimal_completion_sets"]))
        self.assertTrue(any(set(x) == {"NS.critical_bound", "BRIDGE.NS.B_full_scope"}
                            for x in ns["minimal_completion_sets"]))

    def test_external_poincare_is_not_mathos_reconstruction(self):
        result = audit_clay_proof_topology()
        self.assertTrue(result["poincare_externally_solved"])
        self.assertEqual(result["poincare_mathos_reconstruction"], "BLOCKED")
        p = next(t for t in result["targets"] if t["model_key"] == "Poincare")
        self.assertEqual(p["official_status"], "SOLVED_EXTERNALLY")
        self.assertEqual(p["minimal_completion_sets"],
                         [["POINCARE.reconstruction"]])
        self.assertEqual(p["mathos_status"], "BLOCKED")

    def test_candidate_bridges_remain_open_in_every_unsolved_track(self):
        result = audit_clay_proof_topology()
        for t in result["targets"]:
            if t["model_key"] == "Poincare":
                continue
            for missing in t["minimal_completion_sets"]:
                self.assertTrue(any(x.startswith("BRIDGE.") for x in missing))

    def test_deterministic_and_read_only(self):
        paths = [ROUTES_PATH, TARGETS_PATH, OBLIGATIONS, HYPOTHESES, EXTERNAL_PATH]
        before = [p.read_bytes() for p in paths]
        self.assertEqual(audit_clay_proof_topology(),
                         audit_clay_proof_topology())
        self.assertEqual(before, [p.read_bytes() for p in paths])

    def _tamper(self, mutate, kind="routes"):
        paths = {
            "routes": ROUTES_PATH,
            "targets": TARGETS_PATH,
            "register": OBLIGATIONS,
            "hypotheses": HYPOTHESES,
            "external": EXTERNAL_PATH,
        }
        with tempfile.TemporaryDirectory() as tmp:
            docs = {key: json.loads(path.read_text(encoding="utf-8"))
                    for key, path in paths.items()}
            mutate(docs[kind])
            local = {}
            for key, doc in docs.items():
                local[key] = Path(tmp) / (key + ".json")
                local[key].write_text(json.dumps(doc), encoding="utf-8")
            return audit_clay_proof_topology(
                local["routes"], local["targets"],
                local["register"], local["hypotheses"], local["external"]
            )

    def test_reject_removed_official_alternative(self):
        with self.assertRaises(ValueError):
            self._tamper(lambda obj: obj["routes"].pop(6))

    def test_reject_dropped_canonical_dependency(self):
        with self.assertRaises(ValueError):
            self._tamper(lambda obj: obj["routes"][0]["obligations"].pop(0))

    def test_reject_duplicate_route_or_bridge(self):
        for field in ("routes", "candidate_bridges"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self._tamper(lambda obj: obj[field].append(copy.deepcopy(obj[field][0])))

    def test_reject_cross_track_or_unknown_dependency(self):
        for mutation in ("wrong_model", "unknown_dependency"):
            def change(obj):
                if mutation == "wrong_model":
                    obj["candidate_bridges"][0]["model_key"] = "Hodge"
                else:
                    obj["routes"][0]["obligations"][0] = "RH.unproved_shortcut"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self._tamper(change)

    def test_reject_fake_bridge_evidence_or_proof(self):
        for mutation in ("proved", "reviewed", "artifact"):
            def change(obj):
                bridge = obj["candidate_bridges"][0]
                if mutation == "proved":
                    bridge["status"] = "PROVED"
                elif mutation == "reviewed":
                    bridge["review_verdict"] = "independently_verified"
                else:
                    bridge["evidence_artifacts"] = ["unverified.pdf"]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self._tamper(change)

    def test_reject_fake_route_review_or_alternative(self):
        for mutation in ("reviewed", "invalid_alternative", "proof"):
            def change(obj):
                route = obj["routes"][1]
                if mutation == "reviewed":
                    route["sufficiency_review"] = "approved"
                elif mutation == "invalid_alternative":
                    route["alternative"] = "P_not_equals_NP"
                else:
                    route["evidence_artifacts"] = ["claimed-proof"]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self._tamper(change)

    def test_reject_missing_quantifier_review_metadata(self):
        with self.assertRaises(ValueError):
            self._tamper(lambda obj: obj["candidate_bridges"][2].update(
                {"quantifiers": "a few examples"}))

    def test_external_claims_separate_from_mathos_proofs(self):
        result = audit_clay_proof_topology()
        self.assertEqual(result["external_claims_as_of"], "2026-11-13")
        events = {e["claim_id"]: e for e in result["external_claims"]}
        self.assertEqual(events["POINCARE.published"]["state"], "ACCEPTED_EXTERNAL")
        self.assertEqual(events["NS.2026_openai_claim"]["state"],
                         "ANNOUNCED_UNDER_EXAMINATION")
        self.assertTrue(all(not e["mathos_proof"] for e in events.values()))

    def test_reject_external_claim_promotion(self):
        for key, value in (
            ("state", "ACCEPTED_EXTERNAL"),
            ("official_clay_status", "SOLVED_EXTERNALLY"),
            ("mathos_proof", True),
        ):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self._tamper(lambda obj: obj["events"][1].update(
                    {key: value}), "external")

    def test_reject_existing_canonical_promotion(self):
        def promote(obj):
            obj["tracks"][0]["work_packages"][0]["graph_state"] = "proved"
        with self.assertRaises(ValueError):
            self._tamper(promote, "register")

    def test_reject_changed_clay_status(self):
        def promote(obj):
            next(t for t in obj["targets"]
                 if t["model_key"] == "Navier-Stokes")["clay_status"] = "SOLVED"
        with self.assertRaises(ValueError):
            self._tamper(promote, "targets")


if __name__ == "__main__":
    unittest.main()
