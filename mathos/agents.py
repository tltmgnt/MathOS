"""
MathOS Multi-Agent Reasoning.

Solver -> Critic -> Verifier

Initial implementation uses deterministic mathematical
checks. AI-powered agents will be integrated later.
"""

from dataclasses import dataclass, asdict

from mathos.math_engine import MathEngine


@dataclass
class AgentReport:
    agent: str
    status: str
    message: str

    def to_dict(self):
        return asdict(self)


class SolverAgent:
    """Generates mathematical solutions."""

    def __init__(self):
        self.engine = MathEngine()

    def run(self, problem):
        result = self.engine.solve_linear(problem)

        return {
            "agent": "solver",
            "problem": problem,
            "answer": result["answer"],
            "details": result,
        }


class CriticAgent:
    """Checks solution consistency and completeness."""

    def run(self, solution):
        details = solution["details"]

        if details["verification_status"] != "verified":
            return AgentReport(
                agent="critic",
                status="flagged",
                message="Solver result was not verified.",
            )

        if not solution["answer"]:
            return AgentReport(
                agent="critic",
                status="flagged",
                message="Solver returned an empty answer.",
            )

        return AgentReport(
            agent="critic",
            status="passed",
            message=(
                "Solver output contains an answer and "
                "reports successful verification."
            ),
        )


class VerifierAgent:
    """Independently recomputes the mathematical result."""

    def __init__(self):
        self.engine = MathEngine()

    def run(self, problem, solution):
        try:
            independent = self.engine.solve_linear(problem)
        except ValueError as error:
            return AgentReport(
                agent="verifier",
                status="failed",
                message=str(error),
            )

        if (
            independent["answer"] == solution["answer"]
            and independent["verification_status"] == "verified"
        ):
            return AgentReport(
                agent="verifier",
                status="passed",
                message="Recomputation matches solver output.",
            )

        return AgentReport(
            agent="verifier",
            status="failed",
            message="Independent recomputation disagrees.",
        )


class MultiAgentMathOS:
    """Coordinates the initial three-agent workflow."""

    def __init__(self):
        self.solver = SolverAgent()
        self.critic = CriticAgent()
        self.verifier = VerifierAgent()

    def solve(self, problem):
        solution = self.solver.run(problem)
        critique = self.critic.run(solution)
        verification = self.verifier.run(
            problem,
            solution,
        )

        accepted = (
            critique.status == "passed"
            and verification.status == "passed"
        )

        return {
            "problem": problem,
            "answer": solution["answer"],
            "status": (
                "verified" if accepted else "unverified"
            ),
            "solver": solution,
            "critic": critique.to_dict(),
            "verifier": verification.to_dict(),
        }


if __name__ == "__main__":
    system = MultiAgentMathOS()

    result = system.solve("2x + 5 = 13")

    print(result)
