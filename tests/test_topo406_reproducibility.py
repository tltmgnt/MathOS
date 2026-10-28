"""MathOS TOPO-406 reproducible verification tests."""

import json
import random
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RECORD = (
    ROOT / "evidence" / "topo406" / "CASE-001.json"
)


class TestTOPO406Reproducibility(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with RECORD.open(encoding="utf-8") as file:
            cls.record = json.load(file)

    def test_claim_identifier(self):
        self.assertEqual(
            self.record["claim_id"],
            "CASE-001"
        )

    def test_even_integer_property(self):
        """Check parity preservation over sampled integers."""

        rng = random.Random(406)

        for _ in range(10000):
            a = 2 * rng.randint(-100000, 100000)
            b = 2 * rng.randint(-100000, 100000)

            with self.subTest(a=a, b=b):
                self.assertEqual((a + b) % 2, 0)

    def test_boundary_cases(self):
        cases = [
            (0, 0),
            (-2, 2),
            (-100, -200),
            (1000000, 2000000),
        ]

        for a, b in cases:
            with self.subTest(a=a, b=b):
                self.assertEqual((a + b) % 2, 0)

    def test_verification_record(self):
        self.assertEqual(
            self.record["status"],
            "Verified"
        )

        self.assertTrue(
            self.record["derivation"].strip()
        )

        self.assertTrue(
            self.record["verification_method"].strip()
        )


if __name__ == "__main__":
    unittest.main()
