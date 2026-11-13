"""MathOS EXP-019: Cross-model arithmetic error analysis."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


def load_report(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def analyze(report):
    unique = {}

    for record in report["records"]:
        a = record["first_operand"]
        b = record["second_operand"]

        if a == b:
            continue

        key = tuple(sorted((a, b)))

        if key not in unique:
            unique[key] = record

    if not unique:
        raise ValueError("No unique operand pairs found")

    records = []

    for (a, b), record in unique.items():
        correct = record["correct_answer"]

        original = record["original_prediction"]
        swapped = record["swapped_prediction"]

        original_error = original - correct
        swapped_error = swapped - correct

        records.append({
            "operands": [a, b],
            "correct_answer": correct,
            "original_prediction": original,
            "swapped_prediction": swapped,
            "original_signed_error": original_error,
            "swapped_signed_error": swapped_error,
            "original_absolute_error": abs(original_error),
            "swapped_absolute_error": abs(swapped_error),
            "signed_error_changed": (
                original_error != swapped_error
            ),
        })

    return {
        "source_experiment": report["experiment"],
        "model": report["model"],
        "unique_pair_count": len(records),
        "mean_original_signed_error": mean(
            r["original_signed_error"] for r in records
        ),
        "mean_swapped_signed_error": mean(
            r["swapped_signed_error"] for r in records
        ),
        "mean_original_absolute_error": mean(
            r["original_absolute_error"] for r in records
        ),
        "mean_swapped_absolute_error": mean(
            r["swapped_absolute_error"] for r in records
        ),
        "error_change_count": sum(
            r["signed_error_changed"] for r in records
        ),
        "records": records,
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--distilgpt2", required=True)
    parser.add_argument("--tiny-gpt2", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    distil = load_report(args.distilgpt2)
    tiny = load_report(args.tiny_gpt2)

    if distil["experiment"] != "MathOS-EXP-013":
        raise ValueError("Expected Experiment 013")

    if tiny["experiment"] != "MathOS-EXP-015":
        raise ValueError("Expected Experiment 015")

    distil_result = analyze(distil)
    tiny_result = analyze(tiny)

    if (
        distil_result["unique_pair_count"]
        != tiny_result["unique_pair_count"]
    ):
        raise ValueError("Pair counts differ")

    report = {
        "experiment": "MathOS-EXP-019",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "method": (
            "Deduplicated cross-model arithmetic "
            "prediction-error comparison"
        ),
        "benchmark": "MathOS-Arithmetic-Grid-v1",
        "models": {
            "distilgpt2": distil_result,
            "tiny_gpt2": tiny_result,
        },
        "limitations": [
            "Only 15 unique nonidentical operand pairs",
            "Candidate answers restricted to integers 5-13",
            "Pair orientation follows first occurrence",
            "Error magnitude does not establish reasoning",
            "Results are descriptive, not causal",
        ],
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
