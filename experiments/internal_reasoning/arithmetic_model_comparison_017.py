"""MathOS EXP-017: Cross-model operand-swap comparison."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load_report(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def summarize(report):
    return {
        "experiment": report["experiment"],
        "model": report["model"],
        "unique_pair_count": report[
            "unique_nonidentical_pair_count"
        ],
        "prediction_change_count": report[
            "prediction_change_count"
        ],
        "prediction_change_rate": report[
            "prediction_change_rate"
        ],
        "mean_standardized_distance": report[
            "mean_standardized_distance"
        ],
        "minimum_standardized_distance": report[
            "minimum_standardized_distance"
        ],
        "maximum_standardized_distance": report[
            "maximum_standardized_distance"
        ],
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--distilgpt2", required=True)
    parser.add_argument("--tiny-gpt2", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    distil = load_report(args.distilgpt2)
    tiny = load_report(args.tiny_gpt2)

    if distil["experiment"] != "MathOS-EXP-014":
        raise ValueError("Expected Experiment 014")

    if tiny["experiment"] != "MathOS-EXP-016":
        raise ValueError("Expected Experiment 016")

    distil_summary = summarize(distil)
    tiny_summary = summarize(tiny)

    if (
        distil_summary["unique_pair_count"]
        != tiny_summary["unique_pair_count"]
    ):
        raise ValueError("Pair counts do not match")

    report = {
        "experiment": "MathOS-EXP-017",
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "method": (
            "Descriptive cross-model comparison of "
            "deduplicated operand-swap results"
        ),
        "benchmark": "MathOS-Arithmetic-Grid-v1",
        "models": {
            "distilgpt2": distil_summary,
            "tiny_gpt2": tiny_summary,
        },
        "comparison": {
            "prediction_change_rate_difference": (
                distil_summary["prediction_change_rate"]
                - tiny_summary["prediction_change_rate"]
            ),
            "mean_standardized_distance_difference": (
                distil_summary["mean_standardized_distance"]
                - tiny_summary["mean_standardized_distance"]
            ),
        },
        "limitations": [
            "Only 15 unique nonidentical operand pairs",
            "Candidate answers are restricted",
            "Model-specific scores are not directly comparable",
            "Standardized distances are descriptive",
            "No causal or arithmetic-understanding claims",
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
