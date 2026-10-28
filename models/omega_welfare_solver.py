"""Numerical evaluator for the MathOS Omega welfare model."""

from math import exp, isfinite


def evaluate_welfare(
    times,
    utilities,
    weights,
    risks,
    governance,
    rho,
    risk_penalty,
    governance_penalty,
):
    """
    Evaluate discounted welfare using trapezoidal integration.

    utilities[i][j] is participant i's utility at times[j].
    """

    if len(times) < 2:
        raise ValueError("At least two time points are required.")

    if not all(
        times[j] < times[j + 1]
        for j in range(len(times) - 1)
    ):
        raise ValueError("Time points must be strictly increasing.")

    if len(utilities) != len(weights):
        raise ValueError("Each participant needs a weight.")

    if not all(len(row) == len(times) for row in utilities):
        raise ValueError("Utility series must match time points.")

    if len(risks) != len(times):
        raise ValueError("Risk series must match time points.")

    if len(governance) != len(times):
        raise ValueError("Governance series must match time points.")

    values = []

    for j, t in enumerate(times):
        total_utility = sum(
            weights[i] * utilities[i][j]
            for i in range(len(weights))
        )

        net_welfare = (
            total_utility
            - risk_penalty * risks[j]
            - governance_penalty * governance[j]
        )

        values.append(exp(-rho * t) * net_welfare)

    result = sum(
        (times[j + 1] - times[j])
        * (values[j] + values[j + 1])
        / 2
        for j in range(len(times) - 1)
    )

    if not isfinite(result):
        raise ValueError("Welfare result is not finite.")

    return result


def optimize_policies(policies, **parameters):
    """
    Compare a finite set of candidate policies.

    Each policy supplies its own utility, risk,
    and governance time series.
    """

    if not policies:
        raise ValueError("At least one policy is required.")

    scores = {}

    for name, policy in policies.items():
        scores[name] = evaluate_welfare(
            utilities=policy["utilities"],
            risks=policy["risks"],
            governance=policy["governance"],
            **parameters,
        )

    best_policy = max(scores, key=scores.get)

    return {
        "best_policy": best_policy,
        "maximum_welfare": scores[best_policy],
        "policy_scores": scores,
        "verification_status": "numerically_evaluated",
    }
