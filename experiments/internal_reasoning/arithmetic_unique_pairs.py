import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


def analyze(data, experiment_id="MathOS-EXP-014"):
    records = data["records"]

    unique_pairs = {}
    identical_pairs = []

    for record in records:
        a = record["first_operand"]
        b = record["second_operand"]

        if a == b:
            identical_pairs.append(record)
            continue

        key = tuple(sorted((a, b)))

        if key not in unique_pairs:
            unique_pairs[key] = record

    selected = list(unique_pairs.values())

    changed = sum(
        bool(record["prediction_changed"])
        for record in selected
    )

    distances = [
        float(record["standardized_distance"])
        for record in selected
    ]

    return {
        "experiment": experiment_id,
        "source_experiment": data["experiment"],
        "model": data["model"],
        "benchmark": data["benchmark"],
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "method": "Deduplicated unordered operand-pair analysis of the supplied source experiment",
        ),
        "unique_nonidentical_pair_count": len(selected),
        "identical_operand_case_count": len(identical_pairs),
        "prediction_change_count": changed,
        "prediction_change_rate": (
            changed / len(selected)
            if selected
            else None
        ),
        "mean_standardized_distance": (
            mean(distances)
            if distances
            else None
        ),
        "minimum_standardized_distance": (
            min(distances)
            if distances
            else None
        ),
        "maximum_standardized_distance": (
            max(distances)
            if distances
            else None
        ),
        "unique_pair_records": [
            {
                "first_operand": r["first_operand"],
                "second_operand": r["second_operand"],
                "original_prediction": r["original_prediction"],
                "swapped_prediction": r["swapped_prediction"],
                "prediction_changed": r["prediction_changed"],
                "standardized_distance": r["standardized_distance"],
            }
            for r in selected
        ],
        "limitations": [
            "Pairs are deduplicated by unordered operand values",
            "The selected orientation follows the input record order",
            "Identical-operand cases are excluded from swap metrics",
            "The arithmetic grid is small and fixed",
            "Candidate answers are restricted",
            "Results are descriptive, not causal",
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
        "--experiment-id",
        default="MathOS-EXP-014",
    )
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as file:
        data = json.load(file)

        report = analyze(data, experiment_id=args.experiment_id)

    output_path = Path(args.output)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(report, file, indent=2)

    print(
        json.dumps(
            report,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
