"""Adversarial tests: bounded checks are never global mathematical proofs."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from mathos.millennium_omega import (
    ENGINES, STAGES, AssuranceError, audit_packet, run_engine, run_framework,
)
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS


class MillenniumOmegaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = run_framework()

    def test_all_seven_named_engines(self):
        self.assertEqual(
            [e["engine"] for e in self.packet["engines"]], list(ENGINES)
        )
        self.assertEqual(audit_packet(self.packet)["decision"], "RESEARCH_ONLY")

    def test_no_mathematical_promotion(self):
        self.assertEqual(self.packet["certification"], "NOT_CERTIFIED")
        self.assertEqual(self.packet["proof_promotion"], "NONE")
        self.assertFalse(self.packet["assurance"]["global_proof_accepted"])
        for e in self.packet["engines"]:
            self.assertEqual(e["accepted_scope"], "RESEARCH_ONLY")
            self.assertEqual(e["mathos_proof_status"], "BLOCKED")
            self.assertTrue(e["probe_result"]["passed"])
            self.assertEqual([s["stage"] for s in e["agents"]], list(STAGES))
            self.assertTrue(all(s["proof_claim"] is False for s in e["agents"]))

    def test_poincare_external_is_not_mathos_reconstruction(self):
        by_key = {e["engine"]: e for e in self.packet["engines"]}
        self.assertEqual(
            by_key["poincare"]["external_solution"], "ESTABLISHED_EXTERNALLY_ONLY"
        )
        self.assertEqual(by_key["poincare"]["clay_status"], "SOLVED_EXTERNALLY")
        self.assertEqual(by_key["poincare"]["mathos_proof_status"], "BLOCKED")
        for key, e in by_key.items():
            if key != "poincare":
                self.assertEqual(e["external_solution"], "NOT_ESTABLISHED")

    def test_single_engine_entrypoint(self):
        self.assertEqual(run_engine("riemann")["engine"], "riemann")
        with self.assertRaises(AssuranceError):
            run_engine("imaginary")

    def test_digest_tampering_rejected(self):
        packet = copy.deepcopy(self.packet)
        packet["engines"][0]["agents"][4]["lean_global_theorem_checked"] = True
        with self.assertRaises(AssuranceError):
            audit_packet(packet)

    def test_forged_proof_promotion_rejected_even_with_recomputed_digest(self):
        from mathos.millennium_omega.framework import _digest
        for field, value in (
            ("certification", "CERTIFIED"),
            ("proof_promotion", "ALLOW"),
        ):
            packet = copy.deepcopy(self.packet)
            packet[field] = value
            packet["assurance"]["content_sha256"] = _digest(
                {k: v for k, v in packet.items() if k != "assurance"}
            )
            with self.assertRaises(AssuranceError):
                audit_packet(packet)

    def test_agent_proof_claim_rejected(self):
        packet = copy.deepcopy(self.packet)
        packet["engines"][-1]["agents"][0]["proof_claim"] = True
        with self.assertRaises(AssuranceError):
            audit_packet(packet)

    def test_duplicate_engines_rejected(self):
        packet = copy.deepcopy(self.packet)
        packet["engines"][1] = packet["engines"][0]
        with self.assertRaises(AssuranceError):
            audit_packet(packet)

    def test_canonical_register_remains_unchanged(self):
        before = OBLIGATIONS.read_bytes()
        run_framework()
        self.assertEqual(OBLIGATIONS.read_bytes(), before)

    def test_canonical_promotion_tampering_rejected(self):
        source = json.loads(OBLIGATIONS.read_text())
        source["tracks"][0]["work_packages"][0]["formal_check"] = "verified"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "obligations.json"
            path.write_text(json.dumps(source))
            with self.assertRaises((AssuranceError, ValueError)):
                run_framework(register_path=path)

    def test_hypothesis_mapping_tampering_rejected(self):
        program = json.loads(HYPOTHESES.read_text())
        program["experiments"][0]["bounded_probe"] = "nonexistent"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "hypotheses.json"
            path.write_text(json.dumps(program))
            with self.assertRaises((AssuranceError, ValueError)):
                run_framework(hypothesis_path=path)


if __name__ == "__main__":
    unittest.main()
