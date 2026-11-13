"""Automated tests for the MathOS reasoning core."""

import unittest
from fractions import Fraction

from mathos.core import MathOS
from mathos.math_engine import MathEngine


class TestMathEngine(unittest.TestCase):

    def setUp(self):
        self.engine = MathEngine()

    def test_simple_equation(self):
        result = self.engine.solve_linear("x + 5 = 12")
        self.assertEqual(result["answer"], "7")
        self.assertEqual(result["verification_status"], "verified")

    def test_coefficient_equation(self):
        result = self.engine.solve_linear("2x + 5 = 13")
        self.assertEqual(result["answer"], "4")

    def test_negative_constant(self):
        result = self.engine.solve_linear("3x - 6 = 0")
        self.assertEqual(result["answer"], "2")

    def test_fractional_solution(self):
        result = self.engine.solve_linear("4x + 1 = 2")
        self.assertEqual(
            Fraction(result["answer"]),
            Fraction(1, 4),
        )

    def test_no_solution(self):
        result = self.engine.solve_linear("0x + 5 = 12")
        self.assertEqual(result["answer"], "No solution")

    def test_infinite_solutions(self):
        result = self.engine.solve_linear("0x + 5 = 5")
        self.assertEqual(
            result["answer"],
            "Infinitely many solutions",
        )

    def test_invalid_equation(self):
        with self.assertRaises(ValueError):
            self.engine.solve_linear("x^2 = 4")


class MockAIEngine:

    def solve(self, problem, domain="general"):
        return {
            "problem": problem,
            "domain": domain,
            "answer": "Gravity attracts masses.",
            "model": "mock-model",
            "verification_status": "unverified",
        }


class TestMathOSCore(unittest.TestCase):

    def setUp(self):
        self.system = MathOS(ai_engine=MockAIEngine())

    def test_mathematics_integration(self):
        result = self.system.solve(
            "2x + 5 = 13",
            domain="mathematics",
        )
        self.assertEqual(result.answer, "4")
        self.assertEqual(
            result.verification_status,
            "verified",
        )

    def test_structured_output(self):
        result = self.system.solve(
            "x + 5 = 12",
            domain="mathematics",
        )
        data = result.to_dict()
        self.assertEqual(data["domain"], "mathematics")
        self.assertEqual(data["answer"], "7")
        self.assertIn("evidence", data)

    def test_empty_problem(self):
        with self.assertRaises(ValueError):
            self.system.solve("", domain="mathematics")

    def test_unsupported_domain(self):
        with self.assertRaises(ValueError):
            self.system.solve(
                "Test problem",
                domain="unknown",
            )

    def test_general_reasoning_with_mock_ai(self):
        result = self.system.solve(
            "Explain gravity",
            domain="science",
        )
        self.assertEqual(
            result.answer,
            "Gravity attracts masses.",
        )
        self.assertEqual(
            result.verification_status,
            "unverified",
        )
        self.assertIn(
            "Model: mock-model",
            result.evidence,
        )


if __name__ == "__main__":
    unittest.main()
