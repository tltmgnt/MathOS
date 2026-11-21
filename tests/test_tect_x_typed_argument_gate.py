"""Adversarial, fail-closed tests for typed mathematical argument contracts.

Mocked compiler outputs prove only that the status gate works. Actual Lean
kernel verification occurs separately in the pinned CI workflow.
"""
from __future__ import annotations

import copy
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from mathos.research.tect_x_typed_argument_gate import (
    MANIFEST, _axiom_report, main, replay, validate_manifest,
)


class TestTECTXTypedArgumentGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def modified(self):
        return copy.deepcopy(self.raw)

    def rejects(self, sample, text):
        with self.assertRaises(ValueError) as cm:
            validate_manifest(sample)
        self.assertIn(text, str(cm.exception))

    def test_two_independent_typed_reference_propositions(self):
        result = validate_manifest(self.raw)
        self.assertTrue(result["ok"])
        self.assertFalse(result["kernel_checked"])
        self.assertFalse(result["semantic_faithfulness_certified"])
        self.assertEqual(result["closed_research_obligations"], [])
        self.assertEqual({b["id"] for b in result["bundles"]},
                         {"proposition-chain", "natural-right-unit"})
        self.assertEqual(len(result["gaps"]), 3)
        for item in result["bundles"]:
            self.assertEqual(item["mathematical_verification"], "NOT_RUN")
            self.assertEqual(item["statement_faithfulness"], "UNREVIEWED")
            self.assertEqual(len(item["source_sha256"]), 64)
            self.assertEqual(len(item["contract_sha256"]), 64)

    def test_static_cli_does_not_claim_kernel_check(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main([])
        self.assertEqual(code, 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["formal_status"], "SOURCE_CONTRACT_VALIDATED_KERNEL_NOT_RUN")
        self.assertFalse(result["kernel_checked"])

    def test_reject_fake_english_faithfulness_certification(self):
        data = self.modified()
        data["language_to_formal_statement_review"] = "PROVEN"
        self.rejects(data, "unreviewed mathematical claims")

    def test_reject_self_certified_external_review(self):
        data = self.modified()
        data["independent_expert_review"] = "CERTIFIED"
        self.rejects(data, "unreviewed mathematical claims")

    def test_reject_closing_riemann_obligation(self):
        data = self.modified()
        data["closed_research_obligations"] = ["RH.zero_identity"]
        self.rejects(data, "unreviewed mathematical claims")

    def test_reject_wrong_lean_version_in_manifest(self):
        data = self.modified()
        data["backend"]["version"] = "4.99.0"
        self.rejects(data, "unsupported schema")

    def test_reject_unsupported_extra_status_field(self):
        data = self.modified()
        data["proof_of_rh"] = True
        self.rejects(data, "top-level proof registry schema")

    def test_reject_duplicate_argument_id(self):
        data = self.modified()
        data["bundles"][1]["id"] = data["bundles"][0]["id"]
        self.rejects(data, "duplicate bundle")

    def test_reject_unsafe_path_traversal(self):
        data = self.modified()
        data["bundles"][0]["source"] = "formal/tectx_arguments/../Other.lean"
        self.rejects(data, "safe paths")

    def test_reject_path_injection(self):
        data = self.modified()
        data["bundles"][0]["source"] = "formal/tectx_arguments/A.lean;echo hacked"
        self.rejects(data, "safe paths")

    def test_reject_unexpected_proof_assumption(self):
        data = self.modified()
        data["bundles"][0]["conjecture_implication"] = "RIEMANN_HYPOTHESIS"
        self.rejects(data, "cannot self-certify")

    def test_reject_synthetic_theorem_name(self):
        data = self.modified()
        data["bundles"][0]["candidate_theorem"] = "MathOS.TECTX.Arguments.bad; #eval"
        self.rejects(data, "Lean theorem name")

    def test_reject_missing_formal_hypotheses(self):
        data = self.modified()
        data["bundles"][1]["explicit_hypotheses"] = []
        self.rejects(data, "hypotheses")

    def test_missing_lean_binary_fails_closed(self):
        with patch(
            "mathos.research.tect_x_typed_argument_gate.subprocess.run",
            side_effect=FileNotFoundError("Lean missing"),
        ):
            result = replay(self.raw, check_lean=True)
        self.assertFalse(result["ok"])
        self.assertFalse(result["kernel_checked"])
        self.assertEqual(result["formal_status"], "KERNEL_CHECK_FAILED")
        self.assertFalse(result["semantic_faithfulness_certified"])

    def test_wrong_lean_version_fails_closed(self):
        with patch(
            "mathos.research.tect_x_typed_argument_gate.subprocess.run",
            return_value=subprocess.CompletedProcess([], 0,
                                                     "Lean (version 4.13.0, mocked)", ""),
        ):
            result = replay(self.raw, check_lean=True)
        self.assertFalse(result["ok"])
        self.assertEqual(result["formal_status"], "KERNEL_CHECK_FAILED")

    def test_kernel_check_still_keeps_english_semantic_bridge_open(self):
        good = {"contract_kernel_checked": True, "transitive_axioms": {
            "MathOS.TECTX.Arguments.implication_chain": [],
            "MathOS.TECTX.Contracts.implication_chain_matches_reference": [],
        }}
        with patch(
            "mathos.research.tect_x_typed_argument_gate.subprocess.run",
            return_value=subprocess.CompletedProcess([], 0,
                                                     "Lean (version 4.14.0, mocked)", ""),
        ), patch(
            "mathos.research.tect_x_typed_argument_gate._replay_one",
            return_value=good,
        ):
            result = replay(self.raw, check_lean=True)
        self.assertTrue(result["ok"])
        self.assertTrue(result["kernel_checked"])
        self.assertEqual(result["formal_status"], "LEAN_KERNEL_CHECKED_TYPED_DEDUCTIONS_ONLY")
        self.assertFalse(result["semantic_faithfulness_certified"])
        self.assertFalse(result["scientific_claim_certification"])
        self.assertEqual(result["closed_research_obligations"], [])

    def test_axiom_output_must_be_exact_and_axiom_free(self):
        name = "MathOS.TECTX.Arguments.implication_chain"
        self.assertEqual(
            _axiom_report(f"file:22:0: information: '{name}' does not depend on any axioms", name), [],
        )
        for output in ("", f"'{name}' depends on axioms: [sorryAx]",
                       f"'{name}' does not depend on any axioms\n'{name}' does not depend on any axioms"):
            with self.assertRaises(ValueError):
                _axiom_report(output, name)

    def test_generic_registry_accepts_new_checked_goal_types(self):
        # The accepted theorem IDs are NOT hard-coded: any reviewed core
        # Lean theorem can be added with its distinct independent contract.
        data = self.modified()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = root / "formal/tectx_arguments/ConjunctionSwap.lean"
            b = root / "formal/tectx_contracts/ConjunctionSwapContract.lean"
            a.parent.mkdir(parents=True)
            b.parent.mkdir(parents=True)
            a.write_text(
                "import Init\nset_option warningAsError true\n" +
                "namespace MathOS.TECTX.Arguments\n" +
                "theorem swap (P Q : Prop) : P ∧ Q → Q ∧ P := by\n" +
                "  intro h\n  exact ⟨h.right, h.left⟩\n" +
                "end MathOS.TECTX.Arguments\n", encoding="utf-8")
            b.write_text(
                "import Init\nset_option warningAsError true\n" +
                "namespace MathOS.TECTX.Contracts\n" +
                "def swapped : Prop := ∀ P Q : Prop, P ∧ Q → Q ∧ P\n" +
                "end MathOS.TECTX.Contracts\n", encoding="utf-8")
            data["bundles"] = [{
                "id": "conjunction-swap",
                "source": "formal/tectx_arguments/ConjunctionSwap.lean",
                "contract": "formal/tectx_contracts/ConjunctionSwapContract.lean",
                "candidate_theorem": "MathOS.TECTX.Arguments.swap",
                "contract_theorem": "MathOS.TECTX.Contracts.matches",
                "reference_proposition": "MathOS.TECTX.Contracts.swapped",
                "informal_claim": "A conjunction can be reordered.",
                "explicit_hypotheses": ["P,Q are Lean propositions."],
                "formal_scope": "All Lean propositions",
                "semantic_gap": "Informal meaning has not been independently reviewed.",
                "review_status": "NOT_REVIEWED",
                "conjecture_implication": "NONE",
            }]
            report = validate_manifest(data, root)
            self.assertEqual(report["bundles"][0]["id"], "conjunction-swap")
            self.assertFalse(report["kernel_checked"])

    def test_reference_contract_must_not_import_candidate(self):
        data = self.modified()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / data["bundles"][0]["source"]
            contract = root / data["bundles"][0]["contract"]
            source.parent.mkdir(parents=True)
            contract.parent.mkdir(parents=True)
            original = MANIFEST.parent.parent.parent / data["bundles"][0]["source"]
            source.write_bytes(original.read_bytes())
            contract.write_text(
                "import PropositionChain\nset_option warningAsError true\n" +
                "namespace MathOS.TECTX.Contracts\n" +
                "def implicationChainReference : Prop := True\n" +
                "end MathOS.TECTX.Contracts\n", encoding="utf-8")
            data["bundles"] = data["bundles"][:1]
            with self.assertRaisesRegex(ValueError, "import Init independently"):
                validate_manifest(data, root)

    def test_reference_proposition_name_must_be_valid(self):
        data = self.modified()
        data["bundles"][0]["reference_proposition"] = "MathOS.TECTX.Contracts.True; axiom false"
        self.rejects(data, "reference proposition")

    def test_tga_integration_keeps_research_claims_blocked(self):
        from mathos.research.tect_x_intelligent_proof_verifier import main as tga_main
        tested = validate_manifest(self.raw)
        for item in tested["bundles"]:
            item["kernel_checked"] = True
        tested.update({"kernel_checked": True, "formal_status": "LEAN_KERNEL_CHECKED_TYPED_DEDUCTIONS_ONLY"})
        out = StringIO()
        with patch("mathos.research.tect_x_typed_argument_gate.replay", return_value=tested), redirect_stdout(out):
            code = tga_main(["--verify-typed-arguments", "--json"])
        self.assertEqual(code, 0)
        graph = json.loads(out.getvalue())
        self.assertFalse(graph["scientific_certification"])
        self.assertEqual(graph["summary"]["mathematical_theorems_certified"], 0)
        self.assertTrue(graph["typed_argument_certificates"]["kernel_checked"])
        self.assertFalse(graph["typed_argument_certificates"]["semantic_faithfulness_certified"])
        self.assertTrue(all(c["conclusion"] == "BLOCKED_NOT_MATHEMATICALLY_VERIFIED" for c in graph["cases"]))


if __name__ == "__main__":
    unittest.main()
