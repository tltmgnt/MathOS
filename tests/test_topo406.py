"""Structural verification tests for MathOS TOPO-406."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "curriculum"

REQUIRED_FILES = [
    ROOT / "docs/reasoning-standard.md",
    CURRICULUM / "TOPO-406-proof-explanation-transfer.md",
    CURRICULUM / "TOPO-406-acceptance-tests.md",
    CURRICULUM / "TOPO-406-traceability-matrix.md",
]

TEST_IDS = {
    *(f"TEST-P{i:02d}" for i in range(1, 6)),
    *(f"TEST-E{i:02d}" for i in range(1, 5)),
    *(f"TEST-T{i:02d}" for i in range(1, 6)),
    *(f"TEST-C{i:02d}" for i in range(1, 3)),
}

STATUSES = {
    "Verified",
    "Supported",
    "Hypothesis",
    "Untested",
    "Rejected",
    "Contested",
}

OUTCOMES = {
    "PASS",
    "FAIL",
    "UNRESOLVED",
    "NOT APPLICABLE",
}


class TestTOPO406(unittest.TestCase):

    def test_required_files_exist(self):
        for path in REQUIRED_FILES:
            with self.subTest(path=path):
                self.assertTrue(
                    path.is_file(),
                    f"Missing required file: {path}",
                )

    def test_required_files_not_empty(self):
        for path in REQUIRED_FILES:
            with self.subTest(path=path):
                self.assertTrue(path.is_file())
                self.assertTrue(path.read_text().strip())

    def test_acceptance_identifiers(self):
        path = CURRICULUM / "TOPO-406-acceptance-tests.md"
        content = path.read_text()

        found = set(re.findall(r"TEST-[A-Z]\d{2}", content))

        self.assertEqual(
            TEST_IDS,
            found,
            f"Missing: {TEST_IDS - found}; "
            f"Unexpected: {found - TEST_IDS}",
        )

    def test_traceability_identifiers(self):
        path = CURRICULUM / "TOPO-406-traceability-matrix.md"
        content = path.read_text()

        for test_id in TEST_IDS:
            with self.subTest(test_id=test_id):
                self.assertIn(test_id, content)

    def test_evidence_status_definitions(self):
        content = (
            CURRICULUM / "TOPO-406-acceptance-tests.md"
        ).read_text()

        for status in STATUSES:
            with self.subTest(status=status):
                self.assertIn(status, content)

    def test_outcome_definitions(self):
        content = (
            CURRICULUM / "TOPO-406-acceptance-tests.md"
        ).read_text()

        for outcome in OUTCOMES:
            with self.subTest(outcome=outcome):
                self.assertIn(outcome, content)

    def test_source_reference(self):
        content = (
            CURRICULUM / "TOPO-406-traceability-matrix.md"
        ).read_text()

        self.assertIn(
            "docs/reasoning-standard.md",
            content,
        )

    def test_no_missing_source_documents(self):
        for path in REQUIRED_FILES:
            with self.subTest(path=path):
                self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
