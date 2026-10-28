"""MathOS Internal Reasoning Laboratory: baseline experiment."""

import json


EXPERIMENTS = [
    {"policy_a": 8, "policy_b": 4, "expected": "A"},
    {"policy_a": 3, "policy_b": 9, "expected": "B"},
    {"policy_a": 6, "policy_b": 6, "expected": "Tie"},
]


def verified_decision(policy_a, policy_b):
    """Independent mathematical reference calculation."""
    if policy_a > policy_b:
        return "A"
    if policy_b > policy_a:
        return "B"
    return "Tie"


def main():
    results = []

    for index, experiment in enumerate(EXPERIMENTS, start=1):
        decision = verified_decision(
            experiment["policy_a"],
            experiment["policy_b"],
        )

        results.append({
            "experiment_id": f"IRL-{index:03d}",
            "input": {
                "policy_a": experiment["policy_a"],
                "policy_b": experiment["policy_b"],
            },
            "expected": experiment["expected"],
            "verified_decision": decision,
            "passed": decision == experiment["expected"],
        })

    print(json.dumps(results, indent=2))

    if not all(result["passed"] for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
