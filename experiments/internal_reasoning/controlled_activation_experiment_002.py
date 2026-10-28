import argparse
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_NAME = "sshleifer/tiny-gpt2"

TRIALS = [
    ("8 + 4 = 12", "8 + 4 = 15"),
    ("7 + 5 = 12", "7 + 5 = 14"),
    ("6 + 3 = 9", "6 + 3 = 11"),
    ("9 + 2 = 11", "9 + 2 = 13"),
    ("4 + 5 = 9", "4 + 5 = 12"),
]


def capture(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model(
            **inputs,
            output_hidden_states=True,
            return_dict=True,
        )

    return {
        "prompt": prompt,
        "token_count": int(inputs["input_ids"].shape[1]),
        "layers": [
            {
                "layer": index,
                "values": hidden[0, -1, :].tolist(),
            }
            for index, hidden in enumerate(outputs.hidden_states)
        ],
    }


def distance(a, b):
    if len(a) != len(b):
        raise ValueError("Activation dimensions do not match")

    result = math.sqrt(
        sum((x - y) ** 2 for x, y in zip(a, b))
    )

    if not math.isfinite(result):
        raise ValueError("Non-finite activation distance")

    return result


def run_experiment(output_path):
    torch.manual_seed(406)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.eval()

    trial_results = []
    distances_by_layer = {}

    for trial_number, (correct, incorrect) in enumerate(
        TRIALS, start=1
    ):
        correct_result = capture(model, tokenizer, correct)
        incorrect_result = capture(model, tokenizer, incorrect)

        correct_layers = correct_result["layers"]
        incorrect_layers = incorrect_result["layers"]

        if len(correct_layers) != len(incorrect_layers):
            raise ValueError("Layer counts do not match")

        layer_distances = []

        for layer_a, layer_b in zip(
            correct_layers, incorrect_layers
        ):
            if layer_a["layer"] != layer_b["layer"]:
                raise ValueError("Layer indices do not match")

            layer_index = layer_a["layer"]

            value = distance(
                layer_a["values"],
                layer_b["values"],
            )

            distances_by_layer.setdefault(
                layer_index, []
            ).append(value)

            layer_distances.append({
                "layer": layer_index,
                "euclidean_distance": value,
            })

        trial_results.append({
            "trial": trial_number,
            "correct": correct_result,
            "incorrect": incorrect_result,
            "distances": layer_distances,
        })

        print(f"Trial {trial_number} complete")

    summaries = []

    for layer_index in sorted(distances_by_layer):
        values = distances_by_layer[layer_index]

        summaries.append({
            "layer": layer_index,
            "trial_count": len(values),
            "mean_distance": statistics.mean(values),
            "standard_deviation": (
                statistics.stdev(values)
                if len(values) > 1 else 0.0
            ),
            "minimum_distance": min(values),
            "maximum_distance": max(values),
        })

    report = {
        "experiment": "MathOS-EXP-002",
        "model": MODEL_NAME,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "seed": 406,
        "trial_count": len(TRIALS),
        "method": (
            "Paired arithmetic prompts; "
            "last-token hidden-state activations; "
            "Euclidean distance per layer"
        ),
        "trials": trial_results,
        "summary": summaries,
        "limitations": [
            "Five fixed arithmetic pairs are exploratory",
            "Different answer tokens can influence activations",
            "Token counts and token identities are not controlled",
            "Trials are different prompts, not independent model runs",
            "Distance does not measure correctness recognition",
            "No causal conclusions can be drawn",
        ],
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nMathOS Experiment 002 completed")
    print(f"Report: {output_path}")

    for item in summaries:
        print(
            f"Layer {item['layer']}: "
            f"mean={item['mean_distance']:.6f}, "
            f"std={item['standard_deviation']:.6f}"
        )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        default=(
            "artifacts/internal_reasoning/"
            "experiment_002.json"
        ),
    )

    args = parser.parse_args()

    run_experiment(Path(args.output))


if __name__ == "__main__":
    main()
