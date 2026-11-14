"""Exact polynomial-lemma verifier: counterexamples, provenance and Lean boundaries."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from mathos.research.agentic_clay import OfflineBackend, _write_packet, run_agent
from mathos.research.lemma_verification import (
    MANIFEST_PATH, MAX_TEST_POINTS, _parse_expr, _formal_replay,
    verify_lemmas,
)
from mathos.research.clay_proof_topology import ROUTES_PATH, EXTERNAL_PATH
from mathos.research.clay_alignment import TARGETS_PATH
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS


class LemmaVerificationTests(unittest.TestCase):
    def _copy_manifest(self, folder, change):
        source = json.loads(MANIFEST_PATH.read_text())
        change(source)
        target = Path(folder) / "edited_manifest.json"
        target.write_text(json.dumps(source), encoding="utf-8")
        return target

    def test_real_exact_counterexample_and_symbolic_normalization(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "results"
            report = verify_lemmas(output_dir=out)
            self.assertEqual(report["certification"], "NOT_CERTIFIED")
            self.assertFalse(report["formal_proof_of_clay_target"])
            self.assertEqual(report["proof_route_sufficiency"], "NOT_VALIDATED")
            self.assertEqual(len(report["results"]), 2)
            good, bad = report["results"]
            self.assertEqual(good["status"],
                             "EXACT_POLYNOMIAL_IDENTITY_BY_PYTHON_NORMALIZATION")
            self.assertEqual(good["symbolic_difference"], [])
            self.assertIsNone(good["witness"])
            self.assertEqual(good["evaluations"], 625)
            self.assertEqual(bad["status"], "CONCRETE_COUNTEREXAMPLE_FOUND")
            self.assertEqual(bad["witness"]["assignment"], {"x": 1, "y": 1})
            self.assertEqual(bad["witness"]["left_value"], "4")
            self.assertEqual(bad["witness"]["right_value"], "2")
            self.assertFalse(bad["clay_problem_solved"])
            self.assertEqual(bad["lean_certificate"], "NOT_RUN")
            self.assertFalse(bad["complete_proof_of_registered_claim"])
            self.assertFalse(bad["research_claim_promoted"])
            self.assertTrue((out / "lemma_verification_report.json").exists())
            counter = (out / bad["lean_handoff_file"]).read_text()
            self.assertIn("theorem mathos_witness_", counter)
            self.assertIn("  decide", counter)
            self.assertIn("import Init", counter)
            self.assertNotIn("sorry", counter)
            self.assertNotIn("axiom", counter)
            positive = (out / good["lean_handoff_file"]).read_text()
            self.assertIn("-- theorem mathos_candidate_", positive)
            self.assertNotIn("\n theorem ", positive)
            self.assertNotIn("\nsorry", positive)

    def test_reproducible_bytes_and_immutable_sources(self):
        source_paths = [MANIFEST_PATH, TARGETS_PATH, ROUTES_PATH,
                        EXTERNAL_PATH, OBLIGATIONS, HYPOTHESES]
        originals = [p.read_bytes() for p in source_paths]
        with tempfile.TemporaryDirectory() as tmp:
            a = verify_lemmas(output_dir=Path(tmp) / "a")
            b = verify_lemmas(output_dir=Path(tmp) / "b")
            self.assertEqual(a, b)
            for item in a["results"]:
                handoff = (Path(tmp) / "a" / item["lean_handoff_file"]).read_bytes()
                self.assertEqual(hashlib.sha256(handoff).hexdigest(),
                                 item["lean_handoff_sha256"])
            self.assertEqual(source_paths[0].read_bytes(), originals[0])
        self.assertEqual(originals, [p.read_bytes() for p in source_paths])

    def test_tampered_scope_or_forged_proof_fails_closed(self):
        changes = (
            lambda m: m["policy"].update({"certification": "CERTIFIED"}),
            lambda m: m["policy"].update({"automatic_claim_promotion": True}),
            lambda m: m["candidates"][0].update({"route_id": "PNP.separation"}),
            lambda m: m["candidates"][0].update({"claim_id": "BRIDGE.NS.A_full_scope"}),
            lambda m: m["candidates"][0].update({"model_key": "Riemann"}),
            lambda m: m["candidates"][0].update({"variables": ["x", "x"]}),
            lambda m: m["candidates"][0].update({"variables": ["x; import Evil", "y"]}),
        )
        for i, change in enumerate(changes):
            with self.subTest(i=i), tempfile.TemporaryDirectory() as tmp:
                source = self._copy_manifest(tmp, change)
                out = Path(tmp) / "out"
                with self.assertRaises(ValueError):
                    verify_lemmas(source, output_dir=out)
                self.assertFalse((out / "lemma_verification_report.json").exists())

    def test_reject_python_code_strings_and_unsafe_ast(self):
        changes = [
            lambda m: m["candidates"][0].update({
                "left": {"op": "__import__", "name": "os"}
            }),
            lambda m: m["candidates"][0].update({
                "left": {"op": "const", "value": "1+__import__('os').system('id')"}
            }),
            lambda m: m["candidates"][0].update({
                "left": {"op": "const", "value": True}
            }),
            lambda m: m["candidates"][0].update({
                "left": {"op": "pow", "base": {"op": "var", "name": "a"},
                         "exponent": 1000000}
            }),
            lambda m: m["candidates"][0].update({
                "left": {"op": "mul", "args": [{"op": "var", "name": "a"}]}
            }),
            lambda m: m["candidates"][0].update({
                "left": {"op": "var", "name": "undeclared"}
            }),
            lambda m: m["candidates"][0].update({
                "left": {"op": "const", "value": 1, "command": "exit"}
            }),
            lambda m: m["candidates"][0].update({
                "search": {"min": -4, "max": 4}
            }),
        ]
        for i, change in enumerate(changes):
            with self.subTest(i=i), tempfile.TemporaryDirectory() as tmp:
                source = self._copy_manifest(tmp, change)
                with self.assertRaises(ValueError):
                    verify_lemmas(source, output_dir=Path(tmp) / "out")

    def test_reject_large_depth_and_ast_node_limits(self):
        for kind in ("depth", "nodes"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                def mutate(doc):
                    expr = {"op": "var", "name": "a"}
                    for _ in range(20 if kind == "depth" else 110):
                        expr = {"op": "neg", "arg": expr}
                    doc["candidates"][0]["left"] = expr
                source = self._copy_manifest(tmp, mutate)
                with self.assertRaisesRegex(ValueError, "resource limit"):
                    verify_lemmas(source, output_dir=Path(tmp) / "out")

    def test_counterexample_free_finite_search_is_inconclusive(self):
        # x^2=x at 0 and 1 only, false at x=2. This cannot be
        # promoted to universal truth just because the window passes.
        with tempfile.TemporaryDirectory() as tmp:
            def mutate(doc):
                c = doc["candidates"][0]
                c["variables"] = ["x"]
                c["left"] = {"op": "pow", "base": {"op": "var", "name": "x"},
                             "exponent": 2}
                c["right"] = {"op": "var", "name": "x"}
                c["search"] = {"min": 0, "max": 1}
                doc["candidates"] = [c]
            source = self._copy_manifest(tmp, mutate)
            r = verify_lemmas(source, output_dir=Path(tmp) / "out")["results"][0]
            self.assertEqual(r["status"], "FINITE_SEARCH_INCONCLUSIVE")
            self.assertEqual(r["evaluations"], 2)
            self.assertTrue(r["symbolic_difference"])
            self.assertIsNone(r["witness"])
            self.assertFalse(r["complete_proof_of_registered_claim"])

    def test_agent_report_is_linked_only_by_exact_source_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = run_agent(
                OfflineBackend(), track="P-versus-NP",
                route_id="PNP.equality", claim_id="PNP.sat_runtime",
                rounds=1, max_model_calls=4,
            )
            _write_packet(Path(tmp) / "agent", agent)
            file = Path(tmp) / "agent" / "agentic_research_report.json"
            result = verify_lemmas(output_dir=Path(tmp) / "result",
                                   agent_report_path=file)
            self.assertTrue(result["agent_report_linked"])
            self.assertTrue(all(x["agent_report_linked_by_digest"]
                                for x in result["results"]))
            tampered = json.loads(file.read_text())
            tampered["source_sha256"]["routes"] = "0" * 64
            file.write_text(json.dumps(tampered), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source bytes"):
                verify_lemmas(output_dir=Path(tmp) / "invalid",
                              agent_report_path=file)

    def test_agent_forged_certification_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = run_agent(
                OfflineBackend(), track="P-versus-NP",
                route_id="PNP.equality", claim_id="PNP.sat_runtime",
                rounds=1, max_model_calls=4,
            )
            agent["packets"][0]["formal_verification_completed"] = True
            # Top-level flags cannot imply verified proof; status fields are checked.
            agent["packets"][0]["promoted_to_solution"] = True
            path = Path(tmp) / "agent.json"
            path.write_text(json.dumps(agent))
            with self.assertRaisesRegex(ValueError, "unearned"):
                verify_lemmas(output_dir=Path(tmp) / "result",
                              agent_report_path=path)

    def test_generated_lean_name_collisions_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            def mutate(doc):
                second = copy.deepcopy(doc["candidates"][0])
                second["candidate_id"] = "ALG_PNP_distributivity"
                doc["candidates"].append(second)
            path = self._copy_manifest(tmp, mutate)
            with self.assertRaisesRegex(ValueError, "Lean filename"):
                verify_lemmas(path, output_dir=Path(tmp) / "result")

    def test_pinned_lean_gate_requires_pinned_version_and_no_shell(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = Path(tmp) / "witness.lean"
            c.write_text("import Init\nexample : 1 ≠ 2 := by decide\n")
            with patch("mathos.research.lemma_verification.shutil.which",
                       return_value="/usr/bin/lean"), patch(
                       "mathos.research.lemma_verification.subprocess.run"
                       ) as mocked:
                mocked.side_effect = [
                    SimpleNamespace(returncode=0,
                                    stdout="Lean (version 4.14.0, x86_64)",
                                    stderr=""),
                    SimpleNamespace(returncode=0, stdout="", stderr=""),
                ]
                result = _formal_replay(c)
            self.assertEqual(result["status"],
                             "LEAN_KERNEL_CHECKED_CONCRETE_COUNTEREXAMPLE")
            self.assertEqual(mocked.call_count, 2)
            self.assertEqual(mocked.call_args.args[0],
                             ["/usr/bin/lean", str(c)])
            self.assertFalse(mocked.call_args.kwargs.get("shell", False))
            with patch("mathos.research.lemma_verification.shutil.which",
                       return_value=None):
                with self.assertRaisesRegex(RuntimeError, "Lean unavailable"):
                    _formal_replay(c)

    def test_result_never_calls_subprocess_without_explicit_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("mathos.research.lemma_verification.subprocess.run") as run:
                verify_lemmas(output_dir=Path(tmp) / "out")
            run.assert_not_called()

    def test_poincare_or_clay_scope_cannot_be_silently_substituted(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self._copy_manifest(tmp, lambda m: m["candidates"][0].update({
                "model_key": "Poincare",
                "route_id": "POINCARE.replay",
                "claim_id": "POINCARE.published",
            }))
            with self.assertRaises(ValueError):
                verify_lemmas(source, output_dir=Path(tmp) / "out")


if __name__ == "__main__":
    unittest.main()
