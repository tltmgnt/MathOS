"""Validate MathOS TOPO-406 evidence records."""

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/topo406-verification-record.schema.json"
RECORDS = ROOT / "evidence/topo406"


class TestTOPO406Records(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        cls.validator = Draft202012Validator(schema)

    def test_evidence_directory_exists(self):
        self.assertTrue(
            RECORDS.is_dir(),
            "Missing evidence/topo406 directory"
        )

    def test_evidence_records_exist(self):
        records = list(RECORDS.glob("*.json"))

        self.assertGreater(
            len(records),
            0,
            "No TOPO-406 evidence records found"
        )

    def test_all_evidence_records_valid(self):
        records = sorted(RECORDS.glob("*.json"))

        self.assertTrue(records, "No evidence records found")

        for path in records:
            with self.subTest(record=path.name):
                record = json.loads(
                    path.read_text(encoding="utf-8")
                )

                errors = list(
                    self.validator.iter_errors(record)
                )

                self.assertEqual(
                    errors,
                    [],
                    f"Invalid record: {path.name}\n"
                    + "\n".join(str(e) for e in errors)
                )


if __name__ == "__main__":
    unittest.main()
