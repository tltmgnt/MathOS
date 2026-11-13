import argparse
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path


def parse_prompt(prompt):
    left, right = prompt.split("=")[0].split("+")
    return int(left.strip()), int(right.strip())


def standardize_vector(values):
    mean = statistics.mean(values)

    variance = statistics.mean(
        [(value - mean) ** 2 for value in values]
    )

    standard_deviation = math.sqrt(variance)

    if standard_deviation == 0:
        return [0.0 for _ in values]

    return [
        (value - mean) / standard_deviation
        for value in values
    ]


def euclidean_distance(first, second):
    return math.sqrt(
        sum(
            (a - b) ** 2
            for a, b in zip(first, second)
        )
    )


def analyze(data):
    candidates = [
        str(value)
        for value in data["candidate_answers"]
    ]

    records = []

    for trial in data["results"]:
        a, b = parse_prompt(trial["prompt"])

        scores = [
            float(trial["candidate_scores"][candidate])
            for candidate in candidates
        ]

        records.append({
            "a": a,
            "b": b,
            "sum": a + b,
            "standardized_scores": standardize_vector(scores),
        })

    groups = defaultdict(list)

    for first, second in combinations(records, 2):
        distance = euclidean_distance(
            first["standardized_scores"],
            second["standardized_scores"],
        )

        if first["sum"] == second["sum"]:
            category = "same_sum"
        elif first["a"] == second["a"]:
            category = "same_first_operand"
        elif first["b"] == second["b"]:
            category = "same_second_operand"
        else:
            category = "different_operands_and_sum"

        groups[category].append(distance)

    summary = {}

    for category, values in groups.items():
        summary[category] = {
            "pair_count": len(values),
            "mean_distance": statistics.mean(values),
            "minimum_distance": min(values),
            "maximum_distance": max(values),
        }

    return {
        "experiment": "MathOS-EXP-011",
        "source_experiment": data["experiment"],
        "model": data["model"],
        "benchmark": data["benchmark"],
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "method": (
            "Pairwise Euclidean distances between "
            "z-score-standardized candidate "
            "log-probability vectors"
        ),
        "problem_count": len(records),
        "summary": summary,
        "limitations": [
            "Pairwise observations are not independent",
            "Z-score normalization removes mean and scale",
            "Zero-variance vectors are mapped to zeros",
            "Relationship categories are not balanced",
            "The benchmark uses only 25 addition problems",
            "No causal conclusions can be drawn",
        ],
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    source = Path(args.input)
    destination = Path(args.output)

    data = json.loads(
        source.read_text(encoding="utf-8")
    )

    report = analyze(data)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("MathOS Experiment 011 completed")

    for category, values in report["summary"].items():
        print(
            f"{category}: "
            f"pairs={values['pair_count']}, "
            f"mean={values['mean_distance']:.6f}"
        )


if __name__ == "__main__":
    main()
