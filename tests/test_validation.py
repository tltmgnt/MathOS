import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from mathos.validation import audit


class PackageAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = {key: "synthetic test fixture" for key in (
            "claim", "scope", "operator", "independence_disclosure", "comparator",
            "primary_metric", "acceptance_rule", "sample_size_rationale", "assignment",
            "missing_data_policy", "limitations")}
        self.manifest.update(schema_version=1, domain="mathematics", source_commit="a" * 40,
                             data_origin="external_observations", artifacts=[])
        for role in ("preregistration", "reference", "observations", "analysis", "replication_report"):
            name = role + ".txt"
            (self.root / name).write_bytes(b"synthetic fixture, not external evidence")
            self.manifest["artifacts"].append(dict(role=role, path=name,
                sha256=hashlib.sha256((self.root / name).read_bytes()).hexdigest()))

    def run_audit(self):
        (self.root / "manifest.json").write_text(json.dumps(self.manifest))
        return audit(self.root)

    def test_complete_package_never_establishes_external_validation(self):
        result = self.run_audit()
        self.assertEqual(result["errors"], [])
        self.assertFalse(result["external_validation_established"])
        self.assertEqual(result["status"], "package_complete_pending_external_review")

    def test_tampering_and_missing_artifacts(self):
        (self.root / "analysis.txt").write_text("changed")
        (self.root / "reference.txt").unlink()
        errors = self.run_audit()["errors"]
        self.assertIn("digest mismatch: analysis.txt", errors)
        self.assertIn("missing artifact: reference.txt", errors)

    def test_traversal_and_symlink_escape(self):
        self.manifest["artifacts"][0]["path"] = "../outside.txt"
        self.assertTrue(any("escapes" in e for e in self.run_audit()["errors"]))
        (self.root / "escape").symlink_to(self.root.parent)
        self.manifest["artifacts"][0]["path"] = "escape/outside.txt"
        self.assertTrue(any("escapes" in e for e in self.run_audit()["errors"]))

    def test_synthetic_missing_fields_and_duplicate_paths(self):
        self.manifest["data_origin"] = "synthetic"
        self.manifest["operator"] = " "
        self.manifest["artifacts"].append(self.manifest["artifacts"][0].copy())
        errors = self.run_audit()["errors"]
        self.assertIn("external observations required", errors)
        self.assertIn("missing operator", errors)
        self.assertTrue(any("duplicate" in e for e in errors))

    def test_domains_do_not_change_validation_authority(self):
        for domain in ("mathematics", "computational", "experimental", "operations"):
            self.manifest["domain"] = domain
            self.assertEqual(self.run_audit()["errors"], [])
        self.manifest["domain"] = "unbounded"
        self.assertIn("unsupported domain", self.run_audit()["errors"])

    def test_malformed_manifests_return_structured_failures(self):
        for value in ([], None, "text", 42):
            self.manifest = value
            self.assertEqual(self.run_audit()["status"], "incomplete_or_invalid")
        (self.root / "manifest.json").write_text('{"domain":"mathematics","domain":"operations"}')
        self.assertIn("duplicate JSON key", audit(self.root)["errors"][0])
        (self.root / "manifest.json").write_text('{broken')
        self.assertEqual(audit(self.root)["status"], "incomplete_or_invalid")

    def test_invalid_field_types_do_not_crash(self):
        self.manifest["domain"] = []
        self.manifest["schema_version"] = True
        self.manifest["artifacts"][0]["sha256"] = "invalid"
        errors = self.run_audit()["errors"]
        self.assertIn("unsupported domain", errors)
        self.assertIn("unsupported schema_version", errors)
        self.assertTrue(any("invalid sha256" in e for e in errors))

    def test_large_artifact_streaming_hash(self):
        data = b"a" * (3 * 1024 * 1024 + 17)
        (self.root / "analysis.txt").write_bytes(data)
        self.manifest["artifacts"][3]["sha256"] = hashlib.sha256(data).hexdigest()
        self.assertEqual(self.run_audit()["errors"], [])

    def test_missing_manifest_and_manifest_escape(self):
        self.assertEqual(audit(self.root)["status"], "incomplete_or_invalid")
        (self.root / "manifest.json").symlink_to(self.root.parent / "outside.json")
        self.assertIn("manifest escapes", audit(self.root)["errors"][0])


if __name__ == "__main__":
    unittest.main()
