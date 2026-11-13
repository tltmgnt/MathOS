import argparse
import json
import math
import random
import statistics
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path


def parse_prompt(prompt):
    left, right = prompt.split("=")[0].split("+")
    return int(left.strip()), int(right.strip())


def standardize(values):
    mean = statistics.mean(values)

    variance = statistics.mean(
        (value - mean) ** 2
        for value in values
    )

    scale = math.sqrt(variance)

    if scale == 0:
        return [0.0] * len(values)

    return [
        (value - mean) / scale
        for value in values
    ]


def distance(first, second):
    return math.sqrt(
        sum(
            (a - b) ** 2
            for a, b in zip(first, second)
        )
    )


def calculate_statistic(positions, vectors):
    same_first = []
    same_second = []

    for i, j in combinations(range(len(positions)), 2):
        a1, b1 = positions[i]
        a2, b2 = positions[j]

        d = distance(vectors[i], vectors[j])

        if a1 == a2:
            same_first.append(d)

        if b1 == b2:
            same_second.append(d)

    first_mean = statistics.mean(same_first)
    second_mean = statistics.mean(same_second)

    return {
        "same_first_mean": first_mean,
        "same_second_mean": second_mean,
        "difference": first_mean - second_mean,
    }


def analyze(data, permutations, seed):
    candidates = [
        str(value)
        for value in data["candidate_answers"]
    ]

    positions = []
    vectors = []

    for trial in data["results"]:
        positions.append(
            parse_prompt(trial["prompt"])
        )

        scores = [
            float(trial["candidate_scores"][candidate])
            for candidate in candidates
        ]

        vectors.append(standardize(scores))

    observed = calculate_statistic(
        positions,
        vectors,
    )

    rng = random.Random(seed)

    null_statistics = []

    for _ in range(permutations):
        shuffled = vectors.copy()
        rng.shuffle(shuffled)

        statistic = calculate_statistic(
            positions,
            shuffled,
        )

        null_statistics.append(
            statistic["difference"]
        )

    observed_difference = observed["difference"]

    extreme_count = sum(
        value >= observed_difference
        for value in null_statistics
    )

    p_value = (
        extreme_count + 1
    ) / (
        permutations + 1
    )

    return {
        "experiment": "MathOS-EXP-012",
        "source_experiment": data["experiment"],
        "model": data["model"],
        "benchmark": data["benchmark"],
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "method": (
            "Monte Carlo permutation test of the "
            "difference between same-first-operand "
            "and same-second-operand mean distances "
            "using standardized score vectors"
        ),
        "problem_count": len(positions),
        "seed": seed,
        "permutations": permutations,
        "observed": observed,
        "null_distribution": {
            "mean": statistics.mean(null_statistics),
            "standard_deviation": statistics.pstdev(
                null_statistics
            ),
            "minimum": min(null_statistics),
            "maximum": max(null_statistics),
        },
        "extreme_count": extreme_count,
        "one_sided_p_value": p_value,
        "limitations": [
            "Permutation results depend on the chosen null model",
            "The test assumes exchangeability of score vectors",
            "The 25 prompts are a small fixed arithmetic grid",
            "The statistic was chosen after exploratory analysis",
            "The p-value is exploratory, not confirmatory",
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

    parser.add_argument(
        "--permutations",
        type=int,
        default=1000,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=406,
    )

    args = parser.parse_args()

    if args.permutations < 1:
        parser.error("--permutations must be at least 1")

    source = Path(args.input)
    destination = Path(args.output)

    data = json.loads(
        source.read_text(encoding="utf-8")
    )

    report = analyze(
        data,
        args.permutations,
        args.seed,
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("MathOS Experiment 012 completed")
    print(
        "Observed difference:",
        report["observed"]["difference"],
    )
    print(
        "Exploratory one-sided p-value:",
        report["one_sided_p_value"],
    )


if __name__ == "__main__":
    main()
