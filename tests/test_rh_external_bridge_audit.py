"""Adversarial source-link tests; none of these tests run external Lean."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mathos.research.rh_external_claim_audit import AuditError, git_blob_sha1
from mathos.research import rh_external_bridge_audit as bridge


def fixture():
    sources = {p: "\n".join(parts) for p, parts in bridge.MARKERS.items()}
    sources[bridge.DIRECT] += (
        "\nimport Development.AutomorphicArithmetic.CharacterBoxes.EveryCharacter\n"
    )
    sources[bridge.CRIT] += (
        "\nimport Formalism.GammaFactorNonvanishing.RhOfRight\n"
    )
    sources[bridge.MAIN] += (
        "\nimport Development.AutomorphicArithmetic.CharacterBoxes.RiemannHypothesisOfEveryCharacter\n"
    )
    return sources


class RHBridgeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(bridge.MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_is_pinned_and_read_only(self):
        bridge.validate_manifest(self.manifest)
        self.assertEqual(len(bridge.PINS), 8)
        self.assertEqual(len(set(bridge.PINS.values())), 8)

    def test_safe_offline_report(self):
        result = bridge.make_report()
        self.assertFalse(result["source_fetch_performed"])
        self.assertIsNone(result["source_inspection"])
        self.assertEqual(result["global_rh_status"], "OPEN")
        self.assertEqual(result["mathos_certification"], "NOT_CERTIFIED")
        self.assertFalse(result["full_formal_proof_replayed_by_mathos"])
        self.assertFalse(result["mathematical_truth_established_by_this_audit"])

    def test_source_chain_patterns(self):
        r = bridge.inspect_source_texts(fixture())
        self.assertEqual(r["files_matched"], 8)
        self.assertEqual(len(r["explicit_source_edges"]), 8)
        self.assertFalse(r["deep_automorphic_input_reviewed"])
        self.assertFalse(r["transitive_kernel_proof_verified_by_this_audit"])

    def test_each_file_individually_required(self):
        for path in bridge.PINS:
            sources = fixture()
            del sources[path]
            with self.subTest(file=path), self.assertRaises(AuditError):
                bridge.inspect_source_texts(sources)

    def test_each_marker_is_mandatory(self):
        for path, markers in bridge.MARKERS.items():
            for marker in markers:
                sources = fixture()
                sources[path] = sources[path].replace(marker, "unproven-shortcut")
                with self.subTest(path=path, marker=marker), self.assertRaises(AuditError):
                    bridge.inspect_source_texts(sources)

    def test_direct_and_conditional_imports_required(self):
        for path, import_line in (
            (bridge.MAIN, "import Development.AutomorphicArithmetic.CharacterBoxes.RiemannHypothesisOfEveryCharacter"),
            (bridge.CRIT, "import Formalism.GammaFactorNonvanishing.RhOfRight"),
            (bridge.DIRECT, "import Development.AutomorphicArithmetic.CharacterBoxes.EveryCharacter"),
        ):
            source = fixture()
            source[path] = source[path].replace(import_line, "")
            with self.subTest(path=path), self.assertRaises(AuditError):
                bridge.inspect_source_texts(source)

    def test_stronger_theorem_not_confused_with_rh_equivalence(self):
        sources = fixture()
        sources[bridge.EVERY] = sources[bridge.EVERY].replace(
            "1 / 2 < s.re", "1 < s.re"
        )
        with self.assertRaises(AuditError):
            bridge.inspect_source_texts(sources)

    def test_source_ref_is_fixed_and_no_arbitrary_paths(self):
        for path in bridge.PINS:
            url = bridge.url_for(path)
            self.assertTrue(url.startswith(
                "https://raw.githubusercontent.com/CocoSgt/riemann-hypothesis-lean/"
                + bridge.MIRROR_COMMIT
            ))
        with self.assertRaises(AuditError):
            bridge.url_for("https://attacker.example.com/")
        with self.assertRaises(AuditError):
            bridge.url_for("../../.env")

    def test_forged_status_rejected_even_with_other_fields_unchanged(self):
        for key, val in (
            ("canonical_rh_status", "SOLVED"),
            ("mathos_certification", "CERTIFIED"),
            ("transitive_kernel_replayed_here", True),
            ("deep_automorphic_proof_independently_reviewed", True),
            ("independent_mathematical_acceptance", True),
            ("automatically_update_canonical_register", True),
        ):
            manifest = copy.deepcopy(self.manifest)
            manifest["policy"][key] = val
            with self.subTest(field=key), self.assertRaises(AuditError):
                bridge.validate_manifest(manifest)

    def test_upstream_pin_change_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["pinned_git_blobs"][bridge.MAIN] = "0" * 40
        with self.assertRaises(AuditError):
            bridge.validate_manifest(manifest)

    def test_reject_mismatched_fetched_bytes(self):
        class FakeResp:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self, _):
                return b"not a pinned source"

        def opener(request, timeout):
            self.assertEqual(timeout, 25)
            self.assertTrue(request.full_url.startswith(
                "https://raw.githubusercontent.com/"))
            return FakeResp()

        with self.assertRaisesRegex(AuditError, "exact Git blob fingerprint"):
            bridge.fetch_pinned_files(opener=opener)

    def test_manifest_fingerprint_is_actual_bytes(self):
        data = bridge.MANIFEST.read_bytes()
        report = bridge.make_report()
        self.assertEqual(report["manifest_sha256"],
                         hashlib.sha256(data).hexdigest())

    def test_existing_rh_state_not_modified(self):
        path = bridge.ROOT / "docs/research/rh_proof_obligations.json"
        before = path.read_bytes()
        bridge.make_report()
        bridge.inspect_source_texts(fixture())
        self.assertEqual(before, path.read_bytes())

    def test_invalid_manifest_is_rejected_before_fetch(self):
        changed = copy.deepcopy(self.manifest)
        changed["source_commit"] = "0" * 40
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.json"
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(AuditError):
                bridge.make_report(manifest_path=path, fetch_pinned=True)


if __name__ == "__main__":
    unittest.main()
