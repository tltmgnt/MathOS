"""
MathOS Mathematical Engine.

Solves linear equations of the form:
    ax + b = c

Uses exact rational arithmetic.
"""

import re
from fractions import Fraction


class MathEngine:
    """Deterministic mathematical problem solver."""

    def solve_linear(self, equation: str):
        if not isinstance(equation, str):
            raise ValueError("Equation must be a string.")

        pattern = (
            r"^\s*([+-]?\d*)\s*\*?\s*x"
            r"\s*([+-]\s*\d+)?"
            r"\s*=\s*([+-]?\d+)\s*$"
        )

        match = re.fullmatch(pattern, equation)

        if not match:
            raise ValueError(
                "Unsupported equation. Example: 2x + 5 = 13"
            )

        coefficient, constant, right = match.groups()

        if coefficient in ("", "+"):
            a = 1
        elif coefficient == "-":
            a = -1
        else:
            a = int(coefficient)

        b = int(constant.replace(" ", "")) if constant else 0
        c = int(right)

        if a == 0:
            if b == c:
                return {
                    "answer": "Infinitely many solutions",
                    "verification_status": "verified",
                }

            return {
                "answer": "No solution",
                "verification_status": "verified",
            }

        x = Fraction(c - b, a)

        verified = (a * x + b == c)

        return {
            "equation": equation,
            "answer": str(x),
            "explanation": (
                f"Subtract {b} from both sides, "
                f"then divide by {a}."
            ),
            "verification_status": (
                "verified" if verified else "failed"
            ),
            "verification_method": (
                "Exact substitution using rational arithmetic"
            ),
        }


if __name__ == "__main__":
    engine = MathEngine()

    result = engine.solve_linear("2x + 5 = 13")

    print(result)
