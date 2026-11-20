"""Adversarial regression tests for RH proof claims and dependency gates."""
import copy
import json
import unittest

from mathos.research.rh_proof_firewall import (
    DEFAULT_REGISTRY, ProofBoundaryError, validate,
)


class ProofFirewallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(DEFAULT_REGISTRY.read_text(encoding="utf-8"))

    def mutate(self, fn):
        record = copy.deepcopy(self.registry)
        fn(record)
        with self.assertRaises(ProofBoundaryError):
            validate(record)

    def test_original_registry_is_open_and_all_six_gates_unresolved(self):
        report = validate(self.registry)
        self.assertEqual(report["global_claim_status"], "OPEN")
        self.assertEqual(report["unresolved_gates"], ["G1","G2","G3","G4","G5","G6"])
        self.assertFalse(report["finite_baseline_is_global_proof"])
        self.assertTrue(report["checks_only_metadata_not_mathematical_truth"])

    def test_reject_global_RH_promotion(self):
        self.mutate(lambda r: r.update(global_claim_status="PROVED"))

    def test_reject_formal_claim_without_trusted_kernel(self):
        self.mutate(lambda r: r["claims"][1].update(status="FORMALLY_VERIFIED"))
        self.mutate(lambda r: r["claims"][1].update(status="PROVED"))

    def test_reject_missing_gate(self):
        self.mutate(lambda r: r["claims"].pop(2))

    def test_reject_global_transfer_without_continuity(self):
        self.mutate(lambda r: r["claims"][5].update(dependencies=["G1","G2","G4"]))

    def test_reject_baseline_promotion_to_global_bridge(self):
        self.mutate(lambda r: r["claims"][5]["dependencies"].append("BASELINE"))

    def test_reject_unknown_dependency(self):
        self.mutate(lambda r: r["claims"][2].update(dependencies=["UNKNOWN"]))

    def test_reject_cycles(self):
        self.mutate(lambda r: r["claims"][1].update(dependencies=["G2"]))

    def test_reject_missing_assumptions_or_topology(self):
        self.mutate(lambda r: r["claims"][3].update(topology=""))
        self.mutate(lambda r: r["claims"][3].update(assumptions=""))

    def test_reject_duplicate_id(self):
        self.mutate(lambda r: r["claims"][2].update(id="G1"))

    def test_reject_invalid_evidence_reference(self):
        self.mutate(lambda r: r["claims"][2].update(evidence=[{"path":"", "role":"proof"}]))


if __name__ == "__main__":
    unittest.main()
