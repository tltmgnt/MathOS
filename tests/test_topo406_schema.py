"""JSON Schema validation tests for MathOS TOPO-406."""

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT / "schemas"
    / "topo406-verification-record.schema.json"
)


class TestTOPO406Schema(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            SCHEMA_PATH.read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def valid_record(self):
        return {
            "evaluation_id": "EVAL-001",
            "claim_id": "CLAIM-001",
            "proposition": "The sum of two even integers is even.",
            "assumptions": [
                "Both inputs are integers.",
                "Both inputs are even."
            ],
            "derivation": (
                "Let a=2m and b=2n. "
                "Then a+b=2(m+n), which is even."
            ),
            "explanation": (
                "The sum retains a factor of two."
            ),
            "verification_method": "Deductive proof",
            "results": "The proposition follows.",
            "counterexamples": [],
            "transfer_conditions": [
                "Inputs must be even integers."
            ],
            "limitations": [],
            "status": "Verified",
            "reviewer": "MathOS test fixture",
            "revision_history": []
        }

    def test_schema_is_valid(self):
        Draft202012Validator.check_schema(self.schema)

    def test_valid_record_passes(self):
        record = self.valid_record()
        self.validator.validate(record)

    def test_missing_required_field_fails(self):
        record = self.valid_record()
        del record["claim_id"]

        self.assertFalse(
            self.validator.is_valid(record)
        )

    def test_invalid_status_fails(self):
        record = self.valid_record()
        record["status"] = "DefinitelyCorrect"

        self.assertFalse(
            self.validator.is_valid(record)
        )

    def test_empty_proposition_fails(self):
        record = self.valid_record()
        record["proposition"] = ""

        self.assertFalse(
            self.validator.is_valid(record)
        )

    def test_invalid_assumptions_type_fails(self):
        record = self.valid_record()
        record["assumptions"] = "Assumptions"

        self.assertFalse(
            self.validator.is_valid(record)
        )

    def test_unknown_property_fails(self):
        record = self.valid_record()
        record["unsupported_field"] = True

        self.assertFalse(
            self.validator.is_valid(record)
        )


if __name__ == "__main__":
    unittest.main()
