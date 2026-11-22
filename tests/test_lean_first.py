"""Regression controls for Lean-first metadata and fail-closed kernel replay."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mathos.research import lean_first


def completed(stdout="", returncode=0, stderr=""):
    return SimpleNamespace(stdout=stdout, stderr=stderr, returncode=returncode)


class LeanFirstTests(unittest.TestCase):
    def test_inspect_is_explicitly_not_kernel_checked(self):
        with patch.object(lean_first.subprocess, "run") as run:
            report = lean_first.audit_registry()
        run.assert_not_called()
        self.assertEqual(report["checked_count"], 0)
        self.assertEqual(report["canonical_proof_certification"], "NOT_CERTIFIED")
        self.assertGreaterEqual(len(report["claims"]), 2)
        for claim in report["claims"]:
            self.assertEqual(claim["formal_result"]["status"], "NOT_RUN")
            self.assertEqual(claim["statement_fidelity"], "NOT_INDEPENDENTLY_REVIEWED")
            self.assertFalse(claim["automatic_claim_promotion"])
            self.assertFalse(claim["proves_open_problem"])
            self.assertEqual(
                claim["source_sha256"],
                hashlib.sha256((lean_first.ROOT / claim["source"]).read_bytes()).hexdigest(),
            )

    def test_axiom_audit_uses_last_report_not_forged_earlier_message(self):
        theorem = "MathOS.satSupport_certificate"
        out = (
            f"'{theorem}' does not depend on any axioms\n"
            f"'{theorem}' depends on axioms: [sorryAx]\n"
        )
        with self.assertRaisesRegex(RuntimeError, "unapproved"):
            lean_first._parse_axioms(out, theorem)
        self.assertEqual(
            lean_first._parse_axioms(
                f"'{theorem}' depends on axioms: [Classical.choice, propext]", theorem
            ),
            ["Classical.choice", "propext"],
        )
        self.assertEqual(
            lean_first._parse_axioms(f"'{theorem}' does not depend on any axioms", theorem),
            [],
        )
        with self.assertRaisesRegex(RuntimeError, "omitted"):
            lean_first._parse_axioms("unrelated diagnostic", theorem)

    def test_pinned_replay_checks_proposition_and_axioms(self):
        seen = []

        def run(command, **kwargs):
            seen.append(command)
            if command[1] == "--version":
                return completed("Lean (version 4.14.0, x86_64-unknown-linux-gnu)\n")
            self.assertFalse(kwargs.get("shell", False))
            self.assertNotIn("LEAN_PATH", kwargs["env"])
            generated = Path(command[1]).read_text()
            self.assertIn("set_option warningAsError true", generated)
            if "MathOS.satSupport_certificate" in generated.splitlines()[-1]:
                theorem = "MathOS.satSupport_certificate"
                self.assertIn("example : ∀ m : Nat,", generated)
                self.assertIn("exact MathOS.satSupport_certificate", generated)
            else:
                theorem = "MathOS.satTerms_length"
                self.assertIn("exact MathOS.satTerms_length", generated)
            return completed(f"'{theorem}' does not depend on any axioms")

        with patch.object(lean_first.shutil, "which", return_value="/usr/bin/lean"), patch.object(
            lean_first.subprocess, "run", side_effect=run
        ):
            report = lean_first.audit_registry(verify_lean=True)
        self.assertEqual(len(seen), 3)
        self.assertEqual(report["checked_count"], 2)
        self.assertEqual(report["canonical_proof_certification"], "NOT_CERTIFIED")
        for claim in report["claims"]:
            self.assertEqual(claim["formal_result"]["status"], "KERNEL_CHECKED_SCOPE_ONLY")
            self.assertEqual(claim["formal_result"]["transitive_axioms"], [])
            self.assertFalse(claim["automatic_claim_promotion"])
            self.assertTrue(claim["formal_result"]["audit_source_sha256"])

    def test_no_lean_and_unpinned_lean_fail_closed(self):
        with patch.object(lean_first.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "unavailable"):
                lean_first.audit_registry(verify_lean=True)
        for version in ("Lean (version 4.15.0)", "Lean (version 4.14.0-rc1)"):
            with patch.object(lean_first.shutil, "which", return_value="lean"), patch.object(
                lean_first.subprocess, "run", return_value=completed(version)
            ):
                with self.assertRaisesRegex(RuntimeError, "exact Lean 4.14.0"):
                    lean_first.audit_registry(verify_lean=True)

    def test_compilation_failure_never_reports_success(self):
        with patch.object(lean_first.shutil, "which", return_value="lean"), patch.object(
            lean_first.subprocess, "run", side_effect=[
                completed("Lean (version 4.14.0, Linux)"),
                completed(stderr="type mismatch", returncode=1),
            ]
        ):
            with self.assertRaisesRegex(RuntimeError, "Lean rejected"):
                lean_first.audit_registry(verify_lean=True)

    def test_missing_axiom_report_and_nonstandard_axiom_fail_closed(self):
        for output, error in [
            ("No axiom report", "omitted"),
            ("'MathOS.satSupport_certificate' depends on axioms: [sorryAx]", "unapproved"),
            ("'MathOS.satSupport_certificate' depends on axioms: [Lean.trustCompiler]", "unapproved"),
        ]:
            with self.subTest(output=output), patch.object(
                lean_first.shutil, "which", return_value="lean"
            ), patch.object(lean_first.subprocess, "run", side_effect=[
                completed("Lean (version 4.14.0, Linux)"),
                completed(output),
            ]):
                with self.assertRaisesRegex(RuntimeError, error):
                    lean_first.audit_registry(verify_lean=True)

    def _edit_registry(self, edit):
        data = json.loads(lean_first.DEFAULT_REGISTRY.read_text())
        edit(data)
        with TemporaryDirectory() as directory:
            manifest = Path(directory) / "registry.json"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            return lean_first.audit_registry(registry_path=manifest)

    def test_registry_rejects_promotion_and_path_traversal(self):
        changes = [
            lambda d: d["policy"].update(automatic_claim_promotion=True),
            lambda d: d["claims"][0].update(statement_review="APPROVED"),
            lambda d: d["claims"][0].update(external_review="DONE"),
            lambda d: d["claims"][0].update(proves_open_problem=True),
            lambda d: d["claims"][0].update(source="../outside.lean"),
            lambda d: d["claims"][0].update(theorem="MathOS.false; #eval"),
            lambda d: d["claims"][0].update(expected_type="False\n#eval \"OK\""),
            lambda d: d["claims"].append(d["claims"][0].copy()),
        ]
        for i, change in enumerate(changes):
            with self.subTest(i=i), self.assertRaises(ValueError):
                self._edit_registry(change)

    def test_reject_additional_unpinned_imports(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "formal/SATSupport.lean"
            source.parent.mkdir()
            source.write_text("import Mathlib\n")
            with self.assertRaisesRegex(ValueError, "only the pinned Init"):
                lean_first.audit_registry(root=root)


if __name__ == "__main__":
    unittest.main()
