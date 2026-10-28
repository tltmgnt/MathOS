"""TOPO-406 evidence integrity validation tests.

Checks record traceability, completeness, reproducibility
metadata, status consistency, and optional SHA-256 digests.

These tests do not establish mathematical truth or
authenticate reviewer identities.
"""

import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "topo406"

VALID_STATUSES = {
    "Verified",
    "Supported",
    "Hypothesis",
    "Untested",
    "Rejected",
    "Contested",
}

REQUIRED_FIELDS = (
    "evaluation_id",
    "claim_id",
    "proposition",
    "assumptions",
    "derivation",
    "explanation",
    "verification_method",
    "results",
    "counterexamples",
    "transfer_conditions",
    "limitations",
    "status",
    "reviewer",
    "revision_history",
)


def load_records():
    """Load evidence records without silently skipping errors."""
    if not EVIDENCE.is_dir():
        raise AssertionError(
            f"Evidence directory does not exist: {EVIDENCE}"
        )

    paths = sorted(EVIDENCE.glob("*.json"))

    if not paths:
        raise AssertionError("No evidence records found.")

    records = []

    for path in paths:
        with path.open(encoding="utf-8") as file:
            record = json.load(file)

        if not isinstance(record, dict):
            raise AssertionError(
                f"{path.name}: Expected a JSON object."
            )

        records.append((path, record))

    return records


def canonical_digest(record):
    """Compute SHA-256 over canonical JSON, excluding its digest."""
    payload = {
        key: value
        for key, value in record.items()
        if key != "sha256"
    }

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


class TestTOPO406Integrity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.records = load_records()

    def test_required_fields(self):
        for path, record in self.records:
            with self.subTest(file=path.name):
                missing = [
                    field
                    for field in REQUIRED_FIELDS
                    if field not in record
                ]

                self.assertFalse(
                    missing,
                    f"Missing fields: {missing}",
                )

    def test_claim_traceability(self):
        for path, record in self.records:
            with self.subTest(file=path.name):
                for field in (
                    "evaluation_id",
                    "claim_id",
                    "proposition",
                ):
                    value = record.get(field)

                    self.assertIsInstance(value, str)
                    self.assertTrue(value.strip())

    def test_verification_metadata(self):
        for path, record in self.records:
            with self.subTest(file=path.name):
                if record.get("status") == "Verified":
                    for field in (
                        "derivation",
                        "verification_method",
                        "results",
                    ):
                        value = record.get(field)

                        self.assertIsInstance(value, str)
                        self.assertTrue(value.strip())

    def test_status_consistency(self):
        for path, record in self.records:
            with self.subTest(file=path.name):
                status = record.get("status")

                self.assertIn(status, VALID_STATUSES)

                if status == "Rejected":
                    self.assertTrue(
                        record.get("counterexamples"),
                        "Rejected claim lacks a counterexample.",
                    )

    def test_reviewer_accountability(self):
        for path, record in self.records:
            with self.subTest(file=path.name):
                reviewer = record.get("reviewer")

                self.assertIsInstance(reviewer, str)
                self.assertTrue(reviewer.strip())

                history = record.get("revision_history")

                self.assertIsInstance(history, list)
                self.assertGreater(len(history), 0)

    def test_reproducibility_metadata(self):
        for path, record in self.records:
            with self.subTest(file=path.name):
                method = record.get(
                    "verification_method", ""
                )

                self.assertIsInstance(method, str)
                self.assertTrue(method.strip())

                # A described method is not proof that
                # the procedure was independently reproduced.

    def test_unique_identifiers(self):
        for field in ("evaluation_id", "claim_id"):
            values = [
                record.get(field)
                for _, record in self.records
            ]

            self.assertEqual(
                len(values),
                len(set(values)),
                f"Duplicate {field} detected.",
            )

    def test_optional_sha256_integrity(self):
        for path, record in self.records:
            with self.subTest(file=path.name):
                stored = record.get("sha256")

                if stored is None:
                    continue

                self.assertIsInstance(stored, str)

                self.assertRegex(
                    stored,
                    r"^[0-9a-f]{64}$",
                )

                expected = canonical_digest(record)

                self.assertEqual(
                    stored,
                    expected,
                    f"{path.name}: SHA-256 mismatch.",
                )


if __name__ == "__main__":
    unittest.main()
