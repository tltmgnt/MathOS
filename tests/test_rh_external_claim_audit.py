"""Offline adversarial tests for the pinned external RH headline review."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mathos.research.rh_external_claim_audit import (
    AuditError, MANIFEST, SHA1, THEOREMS, git_blob_sha1,
    inspect_headlines, make_report, read_pinned_sources,
    url_for, validate_manifest,
)


class ExternalRHClaimAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_snapshot_valid_and_not_certified(self):
        self.assertTrue(validate_manifest(self.snapshot)["snapshot_valid"])
        report = make_report()
        self.assertEqual(report["mathos_certification"], "NOT_CERTIFIED")
        self.assertFalse(report["independent_full_proof_replayed_by_mathos"])
        self.assertFalse(report["pinned_source_fetch_completed"])
        self.assertIsNone(report["source_inspection"])

    def test_report_not_false_replay(self):
        report = make_report()
        e = report["independent_kernel_evidence_snapshot"]
        self.assertEqual(e["leanchecker_all_modules"], "REPORTED_PASS")
        self.assertEqual(e["nanoda_export"], "REPORTED_ACCEPT")
        self.assertFalse(e["this_script_verified_external_kernel_logs"])
        self.assertEqual(report["clay_classification_at_snapshot"], "UNSOLVED")

    def test_immutable_upstream_pins(self):
        self.assertEqual(len(SHA1), 6)
        self.assertEqual(len(THEOREMS), 5)
        for digest in SHA1.values():
            self.assertEqual(len(digest), 40)
        for path in SHA1:
            self.assertTrue(url_for(path).startswith(
                "https://raw.githubusercontent.com/"))
        with self.assertRaises(AuditError):
            url_for("../attacker-site")

    def test_git_object_hash_is_not_plain_sha1(self):
        data = b"hello\n"
        self.assertEqual(git_blob_sha1(data),
                         "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_reject_forged_solved_status(self):
        record = copy.deepcopy(self.snapshot)
        record["policy"]["official_cmi_status"] = "SOLVED"
        with self.assertRaises(AuditError):
            validate_manifest(record)

    def test_reject_false_mathos_replay(self):
        record = copy.deepcopy(self.snapshot)
        record["policy"]["full_proof_replayed_by_this_tool"] = True
        with self.assertRaises(AuditError):
            validate_manifest(record)

    def test_reject_forged_kernel_attestation(self):
        record = copy.deepcopy(self.snapshot)
        record["third_party_report"]["full_lake_comparator"] = "passed"
        with self.assertRaises(AuditError):
            validate_manifest(record)

    def test_reject_source_pin_mismatch(self):
        record = copy.deepcopy(self.snapshot)
        record["pinned_blob_sha1"]["src/Main.lean"] = "0" * 40
        with self.assertRaises(AuditError):
            validate_manifest(record)

    def test_no_unpinned_network_fetch(self):
        class FakeResp:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self, _):
                return b"malicious source bytes"

        def fake_open(request, timeout):
            self.assertTrue(request.full_url.startswith(
                "https://raw.githubusercontent.com/"))
            self.assertEqual(timeout, 25)
            return FakeResp()

        with self.assertRaisesRegex(AuditError, "upstream bytes mismatch"):
            read_pinned_sources(opener=fake_open)

    def test_structural_headline_inspection_bounded(self):
        texts = {
            "src/Main.lean": (
                "import Statements\n"
                "theorem riemannHypothesis : RiemannHypothesis := rhOfAll\n"
                "theorem riemannZeta_eq_zero_re : RiemannZetaZerosOnLine := rhOfAll\n"
                "theorem LFunction_ne_zero_of_half_lt_re : DirichletLNonvanishingRightOfHalf := allChi\n"
                "theorem LFunction_eq_zero_re : DirichletLZerosOnLine := claimAll.2.1\n"
                "theorem LFunction_eq_zero_re_of_isPrimitive : PrimitiveDirichletLZerosOnLine := critAll\n"
            ),
            "src/Statements.lean": (
                "import Mathlib\n"
                "def RiemannZetaZerosOnLine : Prop := True\n"
                "def DirichletLNonvanishingRightOfHalf : Prop := True\n"
                "def DirichletLZerosOnLine : Prop := True\n"
                "def PrimitiveDirichletLZerosOnLine : Prop := True\n"
            ),
            "src/Supplements/Kernels/MainTheorems.lean": (
                "theorem allChi : UpperTheory.EveryCharacter := UpperTheory.FinalTheorems.everyCharacter\n"
                "theorem rhOfAll : RiemannHypothesis := Formalism.VW.rh_of_every allChi\n"
            ),
            "Mathlib/NumberTheory/LSeries/RiemannZeta.lean": (
                "def RiemannHypothesis : Prop :=\n"
                "  ∀ (s : ℂ) (_ : riemannZeta s = 0) (_ : ¬∃ n : ℕ, s = -2 * (n + 1)) "
                "(_ : s ≠ 1), s.re = 1 / 2\n"
            ),
            "lean-toolchain": "leanprover/lean4:v4.33.1\n",
            "lakefile.toml": (
                'name = "tree"\n[[require]]\nname = "mathlib"\n'
                'rev = "0df444a360eaa60ab8c11dca51a86af692955474"\n'
            ),
        }
        result = inspect_headlines(texts)
        self.assertTrue(result["riemann_target_is_mathlib_definition"])
        self.assertFalse(result["transitive_proof_checked_by_this_tool"])
        altered = dict(texts)
        altered["src/Main.lean"] = altered["src/Main.lean"].replace(
            "theorem riemannHypothesis : RiemannHypothesis",
            "theorem riemannHypothesis : True"
        )
        with self.assertRaises(AuditError):
            inspect_headlines(altered)

    def test_generated_report_does_not_edit_canonical_RH_register(self):
        path = Path(__file__).resolve().parents[1] / "docs/research/rh_proof_obligations.json"
        before = path.read_bytes()
        make_report()
        self.assertEqual(before, path.read_bytes())

    def test_snapshot_tampering_on_disk_rejected(self):
        changed = copy.deepcopy(self.snapshot)
        changed["policy"]["automatic_promotion"] = True
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.json"
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(AuditError):
                make_report(manifest_path=path)


if __name__ == "__main__":
    unittest.main()
