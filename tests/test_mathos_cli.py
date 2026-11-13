"""Tests for the offline MathOS CLI."""

import json
import subprocess
import sys
import unittest


class TestMathOSCLI(unittest.TestCase):

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, "-m", "mathos.cli", *arguments],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_solves_equation(self):
        result = self.run_cli("2x + 5 = 13")

        self.assertEqual(result.returncode, 0)

        data = json.loads(result.stdout)

        self.assertEqual(data["answer"], "4")
        self.assertEqual(
            data["verification_status"],
            "verified",
        )

    def test_fractional_answer(self):
        result = self.run_cli("4x + 1 = 2")

        self.assertEqual(result.returncode, 0)

        data = json.loads(result.stdout)

        self.assertEqual(data["answer"], "1/4")

    def test_invalid_equation(self):
        result = self.run_cli("x^2 = 4")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Unsupported equation",
            result.stderr,
        )

    def test_rejects_general_domain(self):
        result = self.run_cli(
            "Explain gravity",
            "--domain",
            "science",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Offline mode currently supports mathematics only",
            result.stderr,
        )

    def test_missing_problem(self):
        result = self.run_cli()

        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
