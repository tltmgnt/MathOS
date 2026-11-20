"""RH-Omega scoped research and adversarial proof-boundary tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from mathos.research.rh_omega import (
    CHECKS, ROLES, RHOmegaError, audit, digest, provenance, run,
)
from mathos.research.rh_proof_firewall import DEFAULT_REGISTRY


class RHOmegaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = run()

    def mutated(self, edit, *, recalc=False):
        packet = copy.deepcopy(self.packet)
        edit(packet)
        if recalc:
            packet["assurance"]["content_sha256"] = digest(
                {k: v for k, v in packet.items() if k != "assurance"}
            )
        with self.assertRaises(RHOmegaError):
            audit(packet)

    def test_eight_checks_and_ten_roles(self):
        self.assertEqual([c["id"] for c in self.packet["checks"]], list(CHECKS))
        self.assertEqual([a["role"] for a in self.packet["agents"]], list(ROLES))
        result = audit(self.packet)
        self.assertEqual(result["checks"], 8)
        self.assertEqual(result["agents"], 10)
        self.assertEqual(result["decision"], "RESEARCH_ONLY")

    def test_all_rh_proof_promotion_denied(self):
        self.assertEqual(self.packet["global_claim_status"], "OPEN")
        self.assertEqual(self.packet["certification"], "NOT_CERTIFIED")
        self.assertEqual(self.packet["proof_promotion"], "NONE")
        self.assertFalse(self.packet["assurance"]["rh_proved"])
        self.assertTrue(all(c["rh_proved"] is False for c in self.packet["checks"]))

    def test_existing_six_plus_family_wide_gates_preserved(self):
        tect = self.packet["checks"][-1]["evidence"]
        self.assertEqual(tect["unresolved_gates"],
                         ["G1", "G2", "G3", "G4", "G5", "G6"])
        self.assertEqual(tect["family_wide_positivity"], "CONJECTURED")
        self.assertEqual(self.packet["source_sha256"], provenance())

    def test_finite_li_is_synthetic_only(self):
        e = self.packet["checks"][1]["evidence"]
        self.assertTrue(e["synthetic_countermodel"])
        self.assertFalse(e["uses_actual_zeta_zeros"])
        self.assertFalse(e["universal_positive_established"])
        self.assertGreater(e["first_li_closed_form_float"], 0)

    def test_finite_weil_is_not_universal(self):
        e = self.packet["checks"][2]["evidence"]
        self.assertFalse(e["positive_L2_gram_is_weil"])
        self.assertFalse(e["quadrature_and_tails_certified"])
        self.assertFalse(e["full_test_space_positivity"])

    def test_numeric_reflection_not_formal_analytic_continuation(self):
        e = self.packet["checks"][3]["evidence"]
        self.assertLess(e["theta_reflection_residual"], 1e-9)
        self.assertFalse(e["analytical_continuation_formally_checked"])
        self.assertFalse(e["fixed_self_adjoint_zero_operator"])

    def test_adversarial_counterexamples_recorded(self):
        e = self.packet["checks"][5]["evidence"]
        self.assertEqual(len(e["countermodels"]), 4)
        self.assertTrue(all(c["unwarranted_implication_rejected"]
                            for c in e["countermodels"]))

    def test_reject_report_digest_tampering(self):
        self.mutated(lambda p: p["checks"][0]["evidence"].update(
            independent_analytic_proof_performed=True))

    def test_reject_recomputed_digest_on_global_claim(self):
        self.mutated(lambda p: p.update(global_claim_status="PROVED"), recalc=True)

    def test_reject_recomputed_digest_on_li_promotion(self):
        self.mutated(lambda p: p["checks"][1]["evidence"].update(
            universal_positive_established=True), recalc=True)

    def test_reject_recomputed_digest_on_weil_promotion(self):
        self.mutated(lambda p: p["checks"][2]["evidence"].update(
            full_test_space_positivity=True), recalc=True)

    def test_reject_fake_kernel_check_and_expert_consensus(self):
        self.mutated(lambda p: p["checks"][6]["evidence"].update(
            formal_rh_theorem_proved=True), recalc=True)
        self.mutated(lambda p: p["agents"][-1].update(
            consensus_of_independent_experts=True), recalc=True)

    def test_reject_missing_analytical_or_counterexample_stage(self):
        self.mutated(lambda p: p["checks"].pop(3), recalc=True)
        self.mutated(lambda p: p["checks"][5]["evidence"].update(
            countermodels=[]), recalc=True)

    def test_reject_provenance_tampering(self):
        self.mutated(lambda p: p["source_sha256"].update({
            "formal/RHTransferLogic.lean": "0"*64}), recalc=True)

    def test_reject_canonical_registry_promotion(self):
        registry = json.loads(DEFAULT_REGISTRY.read_text(encoding="utf-8"))
        registry["global_claim_status"] = "PROVED"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "register.json"
            path.write_text(json.dumps(registry), encoding="utf-8")
            with self.assertRaises(ValueError):
                run(registry_path=path)

    def test_reject_prefix_limit_abuse(self):
        with self.assertRaises(RHOmegaError):
            run(li_prefix=0)
        with self.assertRaises(RHOmegaError):
            run(li_prefix=13)
        with self.assertRaises(RHOmegaError):
            run(li_prefix=True)

    def test_run_does_not_modify_canonical_register(self):
        before = DEFAULT_REGISTRY.read_bytes()
        audit(self.packet)
        self.assertEqual(DEFAULT_REGISTRY.read_bytes(), before)

    def test_reserialize_auditable_packet(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "rh.json"
            file.write_text(json.dumps(self.packet), encoding="utf-8")
            self.assertEqual(audit(json.loads(file.read_text()))["decision"],
                             "RESEARCH_ONLY")


if __name__ == "__main__":
    unittest.main()
