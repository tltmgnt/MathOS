"""Tests for the MathOS Internal Reasoning model adapter."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_DIR = ROOT / "experiments" / "internal_reasoning"
sys.path.insert(0, str(ADAPTER_DIR))

from model_adapter import ask_model
from baseline import EXPERIMENTS, verified_decision


class MockResponse:
    def __init__(self, data):
        self.data = data

    def read(self):
        return json.dumps(self.data).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class TestInternalReasoningAdapter(unittest.TestCase):

    def test_baseline_has_three_experiments(self):
        self.assertEqual(len(EXPERIMENTS), 3)

    def test_verified_decisions(self):
        self.assertEqual(verified_decision(8, 4), "A")
        self.assertEqual(verified_decision(3, 9), "B")
        self.assertEqual(verified_decision(6, 6), "Tie")

    @patch("model_adapter.urllib.request.urlopen")
    def test_model_request(self, mock_urlopen):
        mock_urlopen.return_value = MockResponse({
            "choices": [
                {"message": {"content": "A"}}
            ]
        })

        answer = ask_model(
            "http://localhost:8000/v1/chat/completions",
            "test-model",
            "",
            8,
            4,
        )

        self.assertEqual(answer, "A")

        request = mock_urlopen.call_args.args[0]
        payload = json.loads(request.data)

        self.assertEqual(payload["model"], "test-model")
        self.assertEqual(payload["temperature"], 0)
        self.assertIn("Policy A: 8", payload["messages"][0]["content"])
        self.assertIn("Policy B: 4", payload["messages"][0]["content"])

    @patch("model_adapter.urllib.request.urlopen")
    def test_model_tie_response(self, mock_urlopen):
        mock_urlopen.return_value = MockResponse({
            "choices": [
                {"message": {"content": "Tie\n"}}
            ]
        })

        answer = ask_model(
            "http://localhost:8000/v1/chat/completions",
            "test-model",
            "",
            6,
            6,
        )

        self.assertEqual(answer, "Tie")


if __name__ == "__main__":
    unittest.main()
