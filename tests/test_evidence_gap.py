"""Adversarial tests for offline research evidence lineage checks."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from mathos.evidence_gap import audit, KINDS, PREDECESSOR


class EvidenceGapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        records = []
        for kind in KINDS:
            path = kind + ".txt"
            data = ("sample-" + kind).encode()
            (self.root / path).write_bytes(data)
            records.append({
                "kind": kind,
                "state": "recorded",
                "path": path,
                "sha256": hashlib.sha256(data).hexdigest(),
                "depends_on": [] if PREDECESSOR[kind] is None else [PREDECESSOR[kind]],
            })
        self.manifest = {
            "schema_version": "research_evidence_manifest/1",
            "claim_id": "test_claim",
            "source_commit": "a" * 40,
            "scope": "Toy evidence packet; no mathematical truth claims",
            "records": records,
        }
        self.write()

    def write(self):
        (self.root / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def check_error(self, expected):
        result = audit(self.root)
        self.assertEqual(result["status"], "incomplete_or_invalid")
        self.assertTrue(any(expected in error for error in result["errors"]), result)
        self.assertFalse(result["external_validation_established"])
        self.assertFalse(result["mathematical_truth_verified"])
        self.assertFalse(result["human_review_authenticated"])

    def test_complete_packet_only_structural(self):
        result = audit(self.root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["status"], "lineage_packet_structurally_complete")
        self.assertTrue(result["structural_lineage_complete"])
        self.assertFalse(result["mathematical_truth_verified"])
        self.assertFalse(result["external_validation_established"])

    def test_pending_review_and_export_are_explicit(self):
        for rec in self.manifest["records"][-2:]:
            rec.update(state="pending", path=None, sha256=None)
        self.write()
        result = audit(self.root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["status"], "lineage_packet_structurally_valid_with_gaps")
        self.assertEqual(result["unresolved_roles"], ["export", "review"])

    def test_tampered_artifact(self):
        (self.root / "analysis.txt").write_text("corrupted")
        self.check_error("digest mismatch")

    def test_missing_predecessor_link(self):
        self.manifest["records"][2]["depends_on"] = []
        self.write()
        self.check_error("predecessor dependency")

    def test_missing_role(self):
        self.manifest["records"] = self.manifest["records"][:-1]
        self.write()
        self.check_error("missing required roles")

    def test_pending_upstream_cannot_promote_downstream(self):
        self.manifest["records"][2].update(state="pending", path=None, sha256=None)
        self.write()
        self.check_error("recorded downstream with pending prerequisite")

    def test_duplicate_kind(self):
        self.manifest["records"].append(copy.deepcopy(self.manifest["records"][0]))
        self.write()
        self.check_error("duplicate kind")

    def test_parent_traversal(self):
        self.manifest["records"][0]["path"] = "../source.txt"
        self.write()
        self.check_error("unsafe artifact path")

    def test_symlink_artifact(self):
        (self.root / "source.txt").unlink()
        (self.root / "source.txt").symlink_to(self.root / "analysis.txt")
        self.check_error("symlinks forbidden")

    def test_bad_commit(self):
        self.manifest["source_commit"] = "main"
        self.write()
        self.check_error("invalid source_commit")

    def test_duplicate_json_field(self):
        (self.root / "manifest.json").write_text('{"schema_version":1,"schema_version":2}')
        self.check_error("duplicate JSON key")

    def test_no_self_attestation_by_extra_fields(self):
        self.manifest["external_validation_established"] = True
        self.write()
        self.check_error("exactly the five contracted fields")


if __name__ == "__main__":
    unittest.main()
