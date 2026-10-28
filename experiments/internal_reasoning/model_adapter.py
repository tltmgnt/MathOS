"""MathOS Internal Reasoning Laboratory: AI model adapter.

Runs baseline questions against a model and records its answers.

Requires an OpenAI-compatible model endpoint.
Uses only Python's standard library.
"""

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

from baseline import EXPERIMENTS, verified_decision


def ask_model(api_url, model, api_key, policy_a, policy_b):
    """Request one decision from an AI model."""

    prompt = (
        "Compare two policy scores.\n"
        f"Policy A: {policy_a}\n"
        f"Policy B: {policy_b}\n"
        "Return exactly one label: A, B, or Tie. "
        "Return no explanation."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
    }

    headers = {
        "Content-Type": "application/json",
    }

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    request = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    with urllib.request.urlopen(
        request, timeout=60
    ) as response:
        data = json.load(response)

    return data["choices"][0]["message"]["content"].strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api-url",
        default=os.getenv(
            "MATHOS_MODEL_API_URL",
            "http://localhost:8000/v1/chat/completions",
        ),
    )
    parser.add_argument(
        "--model",
        default=os.getenv("MATHOS_MODEL_NAME", "local-model"),
    )
    parser.add_argument(
        "--output",
        default="artifacts/internal_reasoning/model_results.json",
    )
    args = parser.parse_args()

    api_key = os.getenv("MATHOS_MODEL_API_KEY", "")
    results = []

    for index, experiment in enumerate(EXPERIMENTS, start=1):
        a = experiment["policy_a"]
        b = experiment["policy_b"]

        expected = verified_decision(a, b)

        try:
            answer = ask_model(
                args.api_url,
                args.model,
                api_key,
                a,
                b,
            )
            error = None
        except (
            urllib.error.URLError,
            TimeoutError,
            KeyError,
            ValueError,
        ) as exc:
            answer = None
            error = str(exc)

        results.append({
            "experiment_id": f"IRL-{index:03d
