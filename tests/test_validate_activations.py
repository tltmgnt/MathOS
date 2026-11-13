#!/usr/bin/env python3
"""Regression tests for MathOS neural activation validation."""

import copy
import math
import unittest

from verification.validate_activations import validate_activations


def valid_record():
    return {
        "schema_version": "1.0",
        "experiment": "MathOS internal activation capture",
        "model": "sshleifer/tiny-gpt2",
        "timestamp": "2026-10-28T16:46:47+00:00",
        "prompt": "Policy A has score 8. Policy B has score 4.",
        "token_count": 12,
        "layers": [
            {
                "layer": index,
                "hidden_size": 2,
                "last_token_activation": [0.1, -0.2],
            }
            for index in range(3)
        ],
    }


class TestActivationValidator(unittest.TestCase):

    def setUp(self):
        self.data = valid_record()

    def assertRejected(self, data):
        errors = validate_activations(data)
        self.assertTrue(
            errors,
            "Validator accepted an invalid activation record",
        )

    def test_valid_record_accepted(self):
        self.assertEqual(
            validate_activations(self.data),
            [],
        )

    def test_missing_required_field_rejected(self):
        del self.data["model"]
        self.assertRejected(self.data)

    def test_invalid_token_count_rejected(self):
        self.data["token_count"] = 0
        self.assertRejected(self.data)

    def test_incorrect_hidden_size_rejected(self):
        self.data["layers"][0]["hidden_size"] = 3
        self.assertRejected(self.data)

    def test_missing_activation_values_rejected(self):
        del self.data["layers"][0]["last_token_activation"]
        self.assertRejected(self.data)

    def test_nan_rejected(self):
        self.data["layers"][0]["last_token_activation"][0] = math.nan
        self.assertRejected(self.data)

    def test_infinity_rejected(self):
        self.data["layers"][0]["last_token_activation"][0] = math.inf
        self.assertRejected(self.data)

    def test_malformed_layer_rejected(self):
        self.data["layers"][0] = "invalid layer"
        self.assertRejected(self.data)

    def test_non_object_root_rejected(self):
        self.assertRejected(["invalid root"])

    def test_original_record_not_modified(self):
        original = copy.deepcopy(self.data)
        validate_activations(self.data)
        self.assertEqual(self.data, original)


if __name__ == "__main__":
    unittest.main()
