"""Tests for MathOS neural activation capture."""

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT / "experiments" / "internal_reasoning"
    / "activation_capture.py"
)


class TestActivationCapture(unittest.TestCase):

    def test_file_exists(self):
        self.assertTrue(MODULE_PATH.is_file())

    def test_module_imports(self):
        spec = importlib.util.spec_from_file_location(
            "activation_capture", MODULE_PATH
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.assertTrue(
            callable(module.capture_activations)
        )

    def test_function_accepts_model_and_prompt(self):
        spec = importlib.util.spec_from_file_location(
            "activation_capture", MODULE_PATH
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        import inspect

        parameters = inspect.signature(
            module.capture_activations
        ).parameters

        self.assertIn("model_name", parameters)
        self.assertIn("prompt", parameters)


if __name__ == "__main__":
    unittest.main()
