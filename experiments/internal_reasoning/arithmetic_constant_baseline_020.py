"""MathOS EXP-020: Constant-answer baseline comparison."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


CANDIDATES = list(range(5, 14))


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_predictions(records, predictions):
    answers = [record["correct_answer"] for record in records]

    return {
        "correct_count": sum(
            prediction == answer
            for prediction, answer in zip(predictions, answers)
        ),
        "accuracy": mean(
            prediction == answer
            for prediction, answer in zip(predictions, answers)
        ),
        "mean_signed_error": mean(
            prediction - answer
            for prediction, answer in zip(predictions, answers)
        ),
        "mean_absolute_error": mean(
            abs(prediction - answer)
            for prediction, answer in zip(predictions, answers)
        ),
    }


def analyze_model(data):
    records = data["records"]

    original_predictions = [
        record["original_prediction"] for record in records
    ]

    swapped_predictions = [
        record["swapped_prediction"] for record in records
    ]

    baseline_results = {}

    for candidate in CANDIDATES:
        predictions = [candidate] * len(records)

        baseline_results[str(candidate)] = evaluate_predictions(
            records,
            predictions,
        )

    best_baseline = min(
        CANDIDATES,
        key=lambda candidate: (
            baseline_results[str(candidate)]["mean_absolute_error"],
            candidate,
        ),
    )

    return {
        "model": data["model"],
        "source_experiment": data["experiment"],
        "problem_count": len(records),
        "original_predictions": evaluate_predictions(
            records,
            original_predictions,
        ),
        "swapped_predictions": evaluate_predictions(
            records,
            swapped_predictions,
        ),
        "constant_baselines": baseline_results,
        "best_constant_by_mae": best_baseline,
        "best_constant_mae": baseline_results[
            str(best_baseline)
        ]["mean_absolute_error"],
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--distilgpt2", required=True)
    parser.add_argument("--tiny-gpt2", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    distil_data = load_json(args.distilgpt2)
    tiny_data = load_json(args.tiny_gpt2)

    report = {
        "experiment": "MathOS-EXP-020",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "method": "Constant-answer baseline comparison",
        "benchmark": "MathOS-Arithmetic-Grid-v1",
        "candidate_answers": CANDIDATES,
        "models": {
            "distilgpt2": analyze_model(distil_data),
            "tiny_gpt2": analyze_model(tiny_data),
        },
        "limitations": [
            "Only 25 addition problems per model",
            "Candidate answers restricted to integers 5-13",
            "Constant baselines are evaluated on the same grid",
            "The best baseline is selected in-sample",
            "Results do not establish arithmetic reasoning",
        ],
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
