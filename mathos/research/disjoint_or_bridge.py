"""Finite regression for the restricted SAT1 Boolean-semantic bridge.

The ALL-n result is in formal/DisjointORSemantics.lean. Finite checking
does not prove arbitrary SAT is tractable, P=NP, P!=NP, or mathematical novelty.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEAN_SOURCE = ROOT / "formal" / "DisjointORSemantics.lean"
PAIR_VALUES = ((0, 0), (0, 1), (1, 0), (1, 1))


def _validate_pairs(pairs):
    if not isinstance(pairs, (tuple, list)):
        raise ValueError("assignment must be a list or tuple of 0/1 pairs")
    for pair in pairs:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError("each assignment element must be a pair")
        if any(type(v) is not int or v not in (0, 1) for v in pair):
            raise ValueError("pair entries must be exact integers 0 or 1")


def evaluate_product(pairs):
    """Integer product: ∏(x_i+y_i-x_i y_i) on explicit Boolean 0/1 data."""
    _validate_pairs(pairs)
    result = 1
    for x, y in pairs:
        result *= (x + y - x * y)
    return result


def evaluate_cnf(pairs):
    """Truth value: ∧(x_i ∨ y_i), with empty conjunction true."""
    _validate_pairs(pairs)
    return all(bool(x or y) for x, y in pairs)


def canonical_witness(n):
    """Linear-length satisfying assignment for this *restricted* family."""
    if type(n) is not int or n < 0:
        raise ValueError("n must be a nonnegative integer")
    return ((1, 0),) * n


def verify_finite(max_n=6):
    if type(max_n) is not int or not 0 <= max_n <= 7:
        raise ValueError("finite audit is bounded to 0 <= max_n <= 7")
    counts = []
    for n in range(max_n + 1):
        examined = 0
        satisfying = 0
        for assignment in itertools.product(PAIR_VALUES, repeat=n):
            examined += 1
            truth = evaluate_cnf(assignment)
            indicator = evaluate_product(assignment)
            if indicator not in (0, 1) or bool(indicator) != truth:
                raise AssertionError(f"indicator mismatch at n={n}: {assignment!r}")
            satisfying += int(truth)
        if examined != 4**n or satisfying != 3**n:
            raise AssertionError(f"count mismatch at n={n}")
        witness = canonical_witness(n)
        if len(witness) != n or not evaluate_cnf(witness) or evaluate_product(witness) != 1:
            raise AssertionError(f"canonical witness invalid at n={n}")
        counts.append({
            "clauses": n,
            "assignments_checked": examined,
            "satisfying_assignments": satisfying,
            "expected_all_assignments": 4**n,
            "expected_satisfying_assignments": 3**n,
        })
    return {
        "attempt": "MathOS-MILLENNIUM-003-SAT1-BOOLEAN-BRIDGE",
        "status": "FINITE_REGRESSION_ONLY",
        "formal_theorem": "MathOS.satDisjointProduct_indicator",
        "formal_replay": "lean formal/DisjointORSemantics.lean",
        "formal_source_sha256": hashlib.sha256(LEAN_SOURCE.read_bytes()).hexdigest(),
        "counting_formula": "3^n (a separate elementary induction, not supplied by this Lean theorem)",
        "max_n": max_n,
        "counts": counts,
        "establishes_p_vs_np": False,
        "novelty_established": False,
        "independent_review_completed": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=6)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = verify_finite(args.max_n)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
