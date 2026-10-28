"""MathOS EXP-018: Operand-swap correctness comparison."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load_report(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def analyze(report):
    records = report["records"]

    # Deduplicate by unordered operands.
    # Exclude identical-operand cases.
    unique = {}

    for record in records:
        a = record["first_operand"]
        b = record["second_operand"]

        if a == b:
            continue

        key = tuple(sorted((a, b)))

        if key not in unique:
            unique[key] = record

    transitions = {
        "correct_to_correct": 0,
        "correct_to_incorrect": 0,
        "incorrect_to_correct": 0,
        "incorrect_to_incorrect": 0,
    }

    original_correct = 0
    swapped_correct = 0

    for record in unique.values():
        answer = record["correct_answer"]

        before = record["original_prediction"] == answer
        after = record["swapped_prediction"] == answer

        original_correct += int(before)
        swapped_correct += int(after)

        if before and after:
            transitions["correct_to_correct"] += 1
        elif before and not after:
            transitions["correct_to_incorrect"] += 1
        elif not before and after:
            transitions["incorrect_to_correct"] += 1
        else:
            transitions["incorrect_to_incorrect"] += 1

    count = len(unique)

    if count == 0:
        raise ValueError("No nonidentical operand pairs found")

    return {
        "source_experiment": report["experiment"],
        "model": report["model"],
        "unique_pair_count": count,
        "original_correct_count": original_correct,
        "swapped_correct_count": swapped_correct,
        "original_accuracy": original_correct / count,
        "swapped_accuracy": swapped_correct / count,
        "transitions": transitions,
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
        raise ValueError("Model pair counts differ")

    report = {
        "experiment": "MathOS-EXP-018",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "method": (
            "Deduplicated operand-swap correctness "
            "transition comparison"
        ),
        "models": {
            "distilgpt2": distil_result,
            "tiny_gpt2": tiny_result,
        },
        "limitations": [
            "Only 15 unique nonidentical operand pairs",
            "Candidate answers restricted to integers 5-13",
            "Selected pair orientation follows input order",
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
