"""MathOS TOPO-406 evidence quality assurance tests."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "evidence" / "topo406"

REQUIRED_TEXT = [
    "claim_id",
    "proposition",
    "derivation",
    "explanation",
    "verification_method",
    "results",
    "reviewer",
]

REQUIRED_LISTS = [
    "assumptions",
    "counterexamples",
    "transfer_conditions",
    "limitations",
    "revision_history",
]

VALID_STATUSES = {
    "Verified",
    "Supported",
    "Hypothesis",
    "Untested",
    "Rejected",
    "Contested",
}


class TestTOPO406EvidenceQuality(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.records = []

        if RECORDS.is_dir():
            for path in sorted(RECORDS.glob("*.json")):
                with path.open(encoding="utf-8") as file:
                    cls.records.append((path.name, json.load(file)))

    def test_records_exist(self):
        self.assertGreater(
            len(self.records),
            0,
            "No evidence records found."
        )

    def test_required_text_fields(self):
        for filename, record in self.records:
            with self.subTest(filename=filename):
                for field in REQUIRED_TEXT:
                    value = record.get(field)
                    self.assertIsInstance(value, str)
                    self.assertTrue(
                        value.strip(),
                        f"{filename}: {field} is empty."
                    )

    def test_required_list_fields(self):
        for filename, record in self.records:
            with self.subTest(filename=filename):
                for field in REQUIRED_LISTS:
                    value = record.get(field)
                    self.assertIsInstance(value, list)

                    if field != "counterexamples":
                        self.assertGreater(
                            len(value),
                            0,
                            f"{filename}: {field} is empty."
                        )

    def test_valid_status(self):
        for filename, record in self.records:
            with self.subTest(filename=filename):
                self.assertIn(
                    record.get("status"),
                    VALID_STATUSES
                )

    def test_verified_claims_have_evidence(self):
        for filename, record in self.records:
            if record.get("status") == "Verified":
                with self.subTest(filename=filename):
                    for field in [
                        "derivation",
                        "verification_method",
                        "results",
                    ]:
                        self.assertTrue(
                            str(record.get(field, "")).strip(),
                            f"{filename}: Missing {field}"
                        )

    def test_rejected_claims_have_counterexamples(self):
        for filename, record in self.records:
            if record.get("status") == "Rejected":
                with self.subTest(filename=filename):
                    self.assertTrue(
                        record.get("counterexamples"),
                        f"{filename}: Rejection lacks counterexample."
                    )

    def test_transfer_conditions_present(self):
        for filename, record in self.records:
            with self.subTest(filename=filename):
                self.assertTrue(
                    record.get("transfer_conditions"),
                    f"{filename}: Missing transfer conditions."
                )

    def test_unique_claim_ids(self):
        ids = [
            record.get("claim_id")
            for _, record in self.records
        ]

        self.assertEqual(
            len(ids),
            len(set(ids)),
            "Duplicate claim IDs detected."
        )

    def test_unique_evaluation_ids(self):
        ids = [
            record.get("evaluation_id")
            for _, record in self.records
        ]

        self.assertEqual(
            len(ids),
            len(set(ids)),
            "Duplicate evaluation IDs detected."
        )


if __name__ == "__main__":
    unittest.main()
