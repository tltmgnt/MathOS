"""
MathOS Core — Structured Reasoning Interface.

Provides a consistent format for mathematical,
general-purpose, and multi-agent reasoning.
"""

from dataclasses import asdict, dataclass, field
from typing import List


@dataclass
class ReasoningResult:
    problem: str
    domain: str
    answer: str
    explanation: str
    verification_status: str = "unverified"
    evidence: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


class MathOS:
    """Main entry point for MathOS reasoning."""

    SUPPORTED_DOMAINS = {
        "mathematics",
        "science",
        "coding",
        "research",
        "general",
    }

    def solve(self, problem: str, domain: str = "general"):
        if not isinstance(problem, str) or not problem.strip():
            raise ValueError("Problem must be a nonempty string.")

        if domain not in self.SUPPORTED_DOMAINS:
            raise ValueError(
                f"Unsupported domain: {domain}"
            )

        return ReasoningResult(
            problem=problem.strip(),
            domain=domain,
            answer="No solution generated yet.",
            explanation=(
                "The MathOS reasoning interface is initialized. "
                "An AI model and verification tools must be "
                "connected before solutions can be generated."
            ),
            verification_status="unverified",
        )


if __name__ == "__main__":
    system = MathOS()
    result = system.solve(
        "Solve x + 5 = 12",
        domain="mathematics",
    )

    print(result.to_dict())
"""
MathOS Core — Unified Reasoning Interface.

Connects the mathematical engine to the
structured MathOS reasoning system.
"""

from dataclasses import asdict, dataclass, field
from typing import List

from mathos.math_engine import MathEngine


@dataclass
class ReasoningResult:
    problem: str
    domain: str
    answer: str
    explanation: str
    verification_status: str = "unverified"
    evidence: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


class MathOS:
    """Main entry point for MathOS reasoning."""

    SUPPORTED_DOMAINS = {
        "mathematics",
        "science",
        "coding",
        "research",
        "general",
    }

    def __init__(self):
        self.math_engine = MathEngine()

    def solve(self, problem: str, domain: str = "general"):
        if not isinstance(problem, str) or not problem.strip():
            raise ValueError("Problem must be a nonempty string.")

        if domain not in self.SUPPORTED_DOMAINS:
            raise ValueError(f"Unsupported domain: {domain}")

        problem = problem.strip()

        if domain == "mathematics":
            result = self.math_engine.solve_linear(problem)

            return ReasoningResult(
                problem=problem,
                domain=domain,
                answer=result["answer"],
                explanation=result.get(
                    "explanation",
                    "The equation was analyzed using exact arithmetic."
                ),
                verification_status=result["verification_status"],
                evidence=[
                    result.get(
                        "verification_method",
                        "Deterministic equation analysis"
                    )
                ],
            )

        return ReasoningResult(
            problem=problem,
            domain=domain,
            answer="No solution generated yet.",
            explanation=(
                "General reasoning requires an AI model "
                "that has not yet been connected."
            ),
            verification_status="unverified",
        )


if __name__ == "__main__":
    system = MathOS()

    result = system.solve(
        "2x + 5 = 13",
        domain="mathematics",
    )

    print(result.to_dict())
