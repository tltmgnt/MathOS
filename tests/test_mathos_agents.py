"""Tests for MathOS multi-agent coordination."""

import unittest

from mathos.agents import (
    SolverAgent,
    CriticAgent,
    VerifierAgent,
    MultiAgentMathOS,
)


class TestMathOSAgents(unittest.TestCase):

    def test_solver(self):
        result = SolverAgent().run("2x + 5 = 13")
        self.assertEqual(result["answer"], "4")

    def test_critic_accepts_valid_result(self):
        solution = SolverAgent().run("x + 5 = 12")
        report = CriticAgent().run(solution)
        self.assertEqual(report.status, "passed")

    def test_critic_flags_unverified_result(self):
        solution = {
            "answer": "7",
            "details": {
                "verification_status": "unverified"
            },
        }
        report = CriticAgent().run(solution)
        self.assertEqual(report.status, "flagged")

    def test_verifier_accepts_correct_answer(self):
        solution = SolverAgent().run("3x - 6 = 0")
        report = VerifierAgent().run(
            "3x - 6 = 0", solution
        )
        self.assertEqual(report.status, "passed")

    def test_verifier_rejects_wrong_answer(self):
        solution = SolverAgent().run("2x + 5 = 13")
        solution["answer"] = "99"

        report = VerifierAgent().run(
            "2x + 5 = 13", solution
        )
        self.assertEqual(report.status, "failed")

    def test_complete_workflow(self):
        result = MultiAgentMathOS().solve(
            "4x + 1 = 2"
        )

        self.assertEqual(result["answer"], "1/4")
        self.assertEqual(result["status"], "verified")
        self.assertEqual(
            result["critic"]["status"], "passed"
        )
        self.assertEqual(
            result["verifier"]["status"], "passed"
        )

    def test_invalid_equation(self):
        with self.assertRaises(ValueError):
            MultiAgentMathOS().solve("x^2 = 4")


if __name__ == "__main__":
    unittest.main()
