#!/usr/bin/env python3
"""Validate MathOS neural activation capture artifacts."""

import argparse
import json
import math
import sys
from pathlib import Path


def validate_activations(data):
    """Return a list of validation errors."""
    errors = []

    if not isinstance(data, dict):
        return ["Root JSON value must be an object"]

    for field in (
        "schema_version",
        "experiment",
        "model",
        "timestamp",
        "prompt",
    ):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a nonempty string")

    token_count = data.get("token_count")
    if type(token_count) is not int or token_count < 1:
        errors.append("token_count must be a positive integer")

    layers = data.get("layers")
    if not isinstance(layers, list) or not layers:
        errors.append("layers must be a nonempty list")
        return errors

    for position, layer in enumerate(layers):
        label = f"layers[{position}]"

        if not isinstance(layer, dict):
            errors.append(f"{label} must be an object")
            continue

        index = layer.get("layer")
        if type(index) is not int or index != position:
            errors.append(
                f"{label}.layer must equal {position}"
            )

        size = layer.get("hidden_size")
        if type(size) is not int or size < 1:
            errors.append(
                f"{label}.hidden_size must be positive"
            )
            size = None

        values = layer.get("last_token_activation")
        if not isinstance(values, list):
            errors.append(
                f"{label}.last_token_activation must be a list"
            )
            continue

        if size is not None and len(values) != size:
            errors.append(
                f"{label}: expected {size} values, "
                f"found {len(values)}"
            )

        for i, value in enumerate(values):
            if (
                type(value) not in (int, float)
                or not math.isfinite(value)
            ):
                errors.append(
                    f"{label}: invalid activation at index {i}"
                )

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate MathOS neural activations"
    )
    parser.add_argument(
        "--input",
        default="artifacts/internal_reasoning/activations.json",
        help="Path to the activation JSON file",
    )
    args = parser.parse_args()

    path = Path(args.input)

    try:
        with path.open(encoding="utf-8") as stream:
            data = json.load(
                stream,
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError(f"Invalid JSON constant: {value}")
                ),
            )
    except (OSError, ValueError) as exc:
        print(f"FAIL: Cannot read activation artifact: {exc}")
        return 1

    errors = validate_activations(data)

    if errors:
        print("FAIL: Neural activation validation")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("PASS: Neural activation validation")
    print(f"Model: {data['model']}")
    print(f"Tokens: {data['token_count']}")
    print(f"Hidden-state tensors: {len(data['layers'])}")
    print("All activation values are finite.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
