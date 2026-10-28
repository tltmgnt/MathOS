import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_NAME = "sshleifer/tiny-gpt2"

PROMPTS = {
    "correct": "8 + 4 = 12",
    "incorrect": "8 + 4 = 15",
    "neutral": "The sky is blue.",
}


def capture_activations(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model(
            **inputs,
            output_hidden_states=True,
            return_dict=True,
        )

    activations = []

    for layer_index, hidden_state in enumerate(
        outputs.hidden_states
    ):
        vector = hidden_state[0, -1, :].tolist()

        activations.append({
            "layer": layer_index,
            "values": vector,
        })

    return {
        "prompt": prompt,
        "token_count": int(inputs["input_ids"].shape[1]),
        "activations": activations,
    }


def euclidean_distance(vector_a, vector_b):
    if len(vector_a) != len(vector_b):
        raise ValueError("Activation dimensions do not match")

    return math.sqrt(
        sum(
            (a - b) ** 2
            for a, b in zip(vector_a, vector_b)
        )
    )


def compare_results(results):
    comparisons = {}

    pairs = [
        ("correct", "incorrect"),
        ("correct", "neutral"),
        ("incorrect", "neutral"),
    ]

    for first, second in pairs:
        first_layers = results[first]["activations"]
        second_layers = results[second]["activations"]

        if len(first_layers) != len(second_layers):
            raise ValueError("Layer counts do not match")

        distances = []

        for layer_a, layer_b in zip(
            first_layers, second_layers
        ):
            if layer_a["layer"] != layer_b["layer"]:
                raise ValueError("Layer indices do not match")

            distance = euclidean_distance(
                layer_a["values"],
                layer_b["values"],
            )

            distances.append({
                "layer": layer_a["layer"],
                "euclidean_distance": distance,
            })

        comparisons[f"{first}_vs_{second}"] = distances

    return comparisons


def run_experiment(output_path):
    torch.manual_seed(406)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME
    )

    model.eval()

    results = {}

    for category, prompt in PROMPTS.items():
        results[category] = capture_activations(
            model,
            tokenizer,
            prompt,
        )

    report = {
        "experiment": "MathOS-EXP-001",
        "model": MODEL_NAME,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "method": (
            "Last-token hidden-state activations; "
            "Euclidean distance by layer"
        ),
        "results": results,
        "comparisons": compare_results(results),
        "limitations": [
            "Single observation per prompt",
            "Prompt content and tokenization are not controlled",
            "Activation differences do not establish correctness recognition",
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

    print("MathOS Experiment 001 completed")
    print(f"Model: {MODEL_NAME}")
    print(f"Report: {output_path}")

    for pair, distances in report["comparisons"].items():
        print(f"\n{pair}")

        for item in distances:
            print(
                f"  Layer {item['layer']}: "
                f"{item['euclidean_distance']:.6f}"
            )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        default=(
            "artifacts/internal_reasoning/"
            "experiment_001.json"
        ),
    )

    args = parser.parse_args()

    run_experiment(Path(args.output))


if __name__ == "__main__":
    main()
