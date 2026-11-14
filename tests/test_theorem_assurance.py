"""SAT1 formal-support assurance, novelty-review and Clay implication gates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from mathos.research.theorem_assurance import (
    THEOREMS_PATH, SAT_LEAN, _check_lean, audit_theorem_assurance,
)
from mathos.research.clay_alignment import TARGETS_PATH
from mathos.research.clay_proof_topology import ROUTES_PATH, EXTERNAL_PATH
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS


class TheoremAssuranceTests(unittest.TestCase):
    def test_true_scope_and_open_mathematical_boundaries(self):
        result = audit_theorem_assurance()
        self.assertEqual(result["subresult_id"], "SAT1")
        self.assertEqual(result["certification"], "NOT_CERTIFIED")
        self.assertEqual(result["formal_result"]["status"], "NOT_RUN")
        self.assertEqual(result["formal_scope"], "DISJOINT_FACTOR_CHOICE_WORDS_FOR_ALL_M")
        self.assertEqual(result["mathematical_novelty"], "NOT_INDEPENDENTLY_ASSESSED")
        self.assertEqual(result["external_expert_review"], "NOT_PERFORMED")
        self.assertEqual(result["clay_route_implication"], "NOT_PROVEN")
        self.assertEqual(result["registered_open_obligations_remaining"], 14)
        self.assertEqual(result["additional_open_proof_bridges"], 10)
        self.assertFalse(result["clay_solution"])
        self.assertFalse(result["canonical_claim_promotion"])
        self.assertTrue(result["review_queue"]["missing_mathos_implication"])

    def test_deterministic_output_and_source_integrity(self):
        paths = [THEOREMS_PATH, SAT_LEAN, TARGETS_PATH, ROUTES_PATH,
                 EXTERNAL_PATH, HYPOTHESES, OBLIGATIONS]
        originals = [p.read_bytes() for p in paths]
        with tempfile.TemporaryDirectory() as d:
            a = audit_theorem_assurance(output_dir=Path(d))
            b = audit_theorem_assurance(output_dir=Path(d))
            self.assertEqual(a, b)
            report = json.loads((Path(d) / "theorem_assurance.json").read_text())
            self.assertEqual(report, a)
            self.assertEqual(report["sources_sha256"]["lean"],
                             hashlib.sha256(SAT_LEAN.read_bytes()).hexdigest())
        self.assertEqual(originals, [p.read_bytes() for p in paths])

    def _mutate_manifest(self, edit):
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / "assurance.json"
            document = json.loads(THEOREMS_PATH.read_text())
            edit(document)
            file.write_text(json.dumps(document))
            return audit_theorem_assurance(assurance_path=file)

    def test_reject_novelty_and_expert_review_promotion(self):
        cases = [
            lambda m: m["policy"].update({"mathematical_novelty": "NEW_THEOREM"}),
            lambda m: m["policy"].update({"peer_review": "APPROVED"}),
            lambda m: m["policy"].update({"clay_implication": "VALIDATED"}),
            lambda m: m["policy"].update({"auto_promotion": True}),
            lambda m: m["subresults"][0].update({"publication": "PUBLISHED"}),
            lambda m: m["subresults"][0].update({
                "independent_mathematical_review": "ACCEPTED"}),
            lambda m: m["subresults"][0].update({
                "literature_search": "NOVELTY_VERIFIED"}),
            lambda m: m["subresults"][0].update({
                "bridge_to_clay_target": "PROVEN"}),
            lambda m: m["subresults"][0].update({"scope_complete_for_clay": True}),
        ]
        for idx, change in enumerate(cases):
            with self.subTest(case=idx), self.assertRaises(ValueError):
                self._mutate_manifest(change)

    def test_reject_misleading_quantifiers_or_deleted_review_plan(self):
        for mutation in (
            lambda m: m["subresults"][0].update({"statement": "3^m"}),
            lambda m: m["subresults"][0].update({"limitations": ""}),
            lambda m: m["subresults"][0].update({"literature_review_plan": ""}),
            lambda m: m["subresults"][0].update({"external_review_plan": ""}),
            lambda m: m["subresults"][0].update({"route_implication_gap": ""}),
        ):
            with self.assertRaises(ValueError):
                self._mutate_manifest(mutation)

    def test_reject_forged_source_identity_or_cross_track_status(self):
        changes = [
            lambda m: m["subresults"][0].update({"theorem_id": "RH"}),
            lambda m: m["subresults"][0].update({"model_key": "Riemann"}),
            lambda m: m["subresults"][0].update({"open_claim_id": "PNP.sat_correctness"}),
            lambda m: m["subresults"][0].update({"route_id": "PNP.separation"}),
            lambda m: m["subresults"].append(m["subresults"][0].copy()),
        ]
        for change in changes:
            with self.assertRaises(ValueError):
                self._mutate_manifest(change)

    def test_reject_gapped_lean_source_and_fake_shortcuts(self):
        for mutation in (
            lambda content: content.replace(
                "theorem satTerms_length", "theorem removed_satTerms_length"
            ),
            lambda content: content + "\naxiom fake (P : Prop) : P\n",
            lambda content: content + "\n-- sorry is forbidden\n",
            lambda content: content.replace(
                "theorem satSupport_certificate", "theorem renamed_certificate"
            ),
        ):
            with self.subTest(mutation=repr(mutation)):
                with tempfile.TemporaryDirectory() as d:
                    path = Path(d) / "unsafe.lean"
                    path.write_text(mutation(SAT_LEAN.read_text()))
                    with self.assertRaisesRegex(ValueError, "formal source"):
                        audit_theorem_assurance(lean_path=path)

    def test_no_compiler_invocation_without_explicit_request(self):
        with patch("mathos.research.theorem_assurance.subprocess.run") as mocked:
            audit_theorem_assurance()
        mocked.assert_not_called()

    def test_replay_is_bounded_and_pinned_and_has_no_shell(self):
        with patch("mathos.research.theorem_assurance.shutil.which",
                   return_value="/opt/lean/bin/lean"), patch(
                   "mathos.research.theorem_assurance.subprocess.run") as run:
            run.side_effect = [
                SimpleNamespace(returncode=0, stdout="Lean (version 4.14.0, Linux)\n"),
                SimpleNamespace(returncode=0, stdout=""),
            ]
            result = _check_lean(SAT_LEAN)
        self.assertEqual(result["status"], "LEAN_COMPILED_EXACT_SUBRESULT_ONLY")
        self.assertFalse(result["clay_proof"])
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args.args[0],
                         ["/opt/lean/bin/lean", str(SAT_LEAN)])
        self.assertFalse(run.call_args.kwargs.get("shell", False))

    def test_wrong_or_missing_lean_toolchain_rejected(self):
        with patch("mathos.research.theorem_assurance.shutil.which",
                   return_value=None):
            with self.assertRaisesRegex(RuntimeError, "Lean is unavailable"):
                _check_lean(SAT_LEAN)
        with patch("mathos.research.theorem_assurance.shutil.which",
                   return_value="lean"), patch(
                   "mathos.research.theorem_assurance.subprocess.run",
                   return_value=SimpleNamespace(returncode=0, stdout="Lean (version 4.15.0)")):
            with self.assertRaisesRegex(RuntimeError, "4.14.0"):
                _check_lean(SAT_LEAN)

    def test_mathos_canonical_sat1_status_never_mutates(self):
        before = OBLIGATIONS.read_bytes()
        audit_theorem_assurance()
        after = json.loads(OBLIGATIONS.read_text())
        self.assertEqual(after["sat_subresult"]["formal_check"], "not_performed")
        self.assertEqual(after["sat_subresult"]["status"],
                         "informal_proof_in_repository")
        self.assertEqual(before, OBLIGATIONS.read_bytes())

    def test_tampered_canonical_register_cannot_be_promoted(self):
        with tempfile.TemporaryDirectory() as d:
            reg = json.loads(OBLIGATIONS.read_text())
            reg["sat_subresult"]["formal_check"] = "verified"
            file = Path(d) / "register.json"
            file.write_text(json.dumps(reg))
            with self.assertRaises(ValueError):
                audit_theorem_assurance(register_path=file)


if __name__ == "__main__":
    unittest.main()
