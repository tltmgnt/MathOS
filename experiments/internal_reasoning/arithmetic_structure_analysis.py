import argparse
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path


def euclidean_distance(first, second):
    return math.sqrt(
        sum((a - b) ** 2 for a, b in zip(first, second))
    )


def parse_prompt(prompt):
    left, right = prompt.split("=")[0].split("+")
    return int(left.strip()), int(right.strip())


def analyze(data):
    trials = data["results"]
    candidates = [str(x) for x in data["candidate_answers"]]

    records = []

    for trial in trials:
        a, b = parse_prompt(trial["prompt"])

        scores = [
            float(trial["candidate_scores"][candidate])
            for candidate in candidates
        ]

        records.append({
            "a": a,
            "b": b,
            "sum": a + b,
            "scores": scores,
        })

    groups = defaultdict(list)

    for first, second in combinations(records, 2):
        distance = euclidean_distance(
            first["scores"],
            second["scores"],
        )

        same_sum = first["sum"] == second["sum"]
        same_first = first["a"] == second["a"]
        same_second = first["b"] == second["b"]

        if same_sum:
            category = "same_sum"
        elif same_first:
            category = "same_first_operand"
        elif same_second:
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
        "experiment": "MathOS-EXP-009",
        "source_experiment": data["experiment"],
        "model": data["model"],
        "benchmark": data["benchmark"],
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "method": (
            "Euclidean distances between candidate "
            "log-probability vectors grouped by "
            "arithmetic and operand relationships"
        ),
        "problem_count": len(records),
        "summary": summary,
        "limitations": [
            "Pairwise comparisons are not independent observations",
            "Raw score distances can reflect prompt-dependent shifts",
            "Categories are assigned by priority and are not balanced",
            "Same-sum similarity does not prove arithmetic understanding",
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

    print("MathOS Experiment 009 completed")
    print(f"Model: {report['model']}")

    for category, values in report["summary"].items():
        print(
            f"{category}: "
            f"pairs={values['pair_count']}, "
            f"mean={values['mean_distance']:.6f}"
        )


if __name__ == "__main__":
    main()
