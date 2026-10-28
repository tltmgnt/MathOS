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
    ("8 + 4 = 12", "8 + 5 = 12"),
    ("7 + 5 = 12", "7 + 4 = 12"),
    ("6 + 3 = 9", "6 + 4 = 9"),
    ("9 + 2 = 11", "9 + 3 = 11"),
    ("4 + 5 = 9", "4 + 6 = 9"),
]


def capture(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    token_ids = inputs["input_ids"][0].tolist()

    with torch.no_grad():
        outputs = model(
            **inputs,
            output_hidden_states=True,
            return_dict=True,
        )

    layers = [
        {
            "layer": index,
            "values": hidden[0, -1, :].tolist(),
        }
        for index, hidden in enumerate(outputs.hidden_states)
    ]

    return {
        "prompt": prompt,
        "token_count": len(token_ids),
        "token_ids": token_ids,
        "tokens": tokenizer.convert_ids_to_tokens(token_ids),
        "layers": layers,
    }


def euclidean_distance(a, b):
    if len(a) != len(b):
        raise ValueError("Activation dimensions do not match")

    value = math.sqrt(
        sum((x - y) ** 2 for x, y in zip(a, b))
    )

    if not math.isfinite(value):
        raise ValueError("Non-finite activation distance")

    return value


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

        correct_ids = correct_result["token_ids"]
        incorrect_ids = incorrect_result["token_ids"]

        same_token_count = len(correct_ids) == len(incorrect_ids)
        same_final_token = correct_ids[-1] == incorrect_ids[-1]

        if not same_final_token:
            raise ValueError(
                f"Trial {trial_number}: final tokens do not match"
            )

        if not same_token_count:
            raise ValueError(
                f"Trial {trial_number}: token counts do not match"
            )

        layer_distances = []

        for layer_a, layer_b in zip(
            correct_result["layers"],
            incorrect_result["layers"],
        ):
            if layer_a["layer"] != layer_b["layer"]:
                raise ValueError("Layer indices do not match")

            layer_index = layer_a["layer"]

            value = euclidean_distance(
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
            "controls": {
                "same_token_count": same_token_count,
                "same_final_token": same_final_token,
            },
            "distances": layer_distances,
        })

        print(f"Trial {trial_number}: controls passed")

    summary = []

    for layer_index in sorted(distances_by_layer):
        values = distances_by_layer[layer_index]

        summary.append({
            "layer": layer_index,
            "trial_count": len(values),
            "mean_distance": statistics.mean(values),
            "standard_deviation": statistics.stdev(values),
            "minimum_distance": min(values),
            "maximum_distance": max(values),
        })

    report = {
        "experiment": "MathOS-EXP-003",
        "model": MODEL_NAME,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "seed": 406,
        "trial_count": len(TRIALS),
        "method": (
            "Matched-answer arithmetic comparisons; "
            "last-token hidden states; "
            "Euclidean distance by layer"
        ),
        "trials": trial_results,
        "summary": summary,
        "limitations": [
            "Only five fixed arithmetic pairs",
            "Operand changes remain a confounding factor",
            "Matching final tokens does not isolate correctness",
            "Activation distance does not measure mathematical understanding",
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

    print("\nMathOS Experiment 003 completed")
    print(f"Report: {output_path}")

    for item in summary:
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
            "experiment_003.json"
        ),
    )

    args = parser.parse_args()
    run_experiment(Path(args.output))


if __name__ == "__main__":
    main()
