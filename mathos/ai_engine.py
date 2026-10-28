"""
MathOS AI Reasoning Engine.

Provides an interface to an external AI model.
Requires the openai package and OPENAI_API_KEY.
"""

import os


class AIEngine:
    """Generate reasoning responses using an AI model."""

    def __init__(self, model=None):
        self.model = model or os.getenv(
            "MATHOS_AI_MODEL", "gpt-4.1-mini"
        )

    def solve(self, problem, domain="general"):
        if not isinstance(problem, str) or not problem.strip():
            raise ValueError("Problem must be a nonempty string.")

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError(
                "Install the openai package to enable AI reasoning."
            ) from error

        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model=self.model,
            instructions=(
                "You are the MathOS reasoning assistant. "
                "Provide clear, logically structured answers. "
                "Explain important assumptions and limitations. "
                "Do not claim mathematical proof or independent "
                "verification unless it has actually occurred. "
                "If uncertain, state the uncertainty."
            ),
            input=(
                f"Domain: {domain}\n"
                f"Problem: {problem}"
            ),
        )

        answer = response.output_text

        if not answer or not answer.strip():
            raise RuntimeError(
                "AI model returned an empty response."
            )

        return {
            "problem": problem,
            "domain": domain,
            "answer": answer.strip(),
            "model": self.model,
            "verification_status": "unverified",
            "verification_method": "AI-generated response only",
        }
