"""Hodge attack 006: exact intersection-matrix audit for C x C divisors.

For a smooth projective complex curve C of genus g, geometric inputs
(under classical intersection theory):
  F1^2 = F2^2 = 0; F1.F2 = F1.Delta = F2.Delta = 1;
  Delta^2 = 2 - 2*g.
Python audits consequences of this asserted matrix, not complex geometry.
Proof of intersection inputs is supplied separately in the research note.
A check of abstract matrices is NOT a solution of the Hodge conjecture.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEAN_SOURCE = ROOT / "formal" / "HodgeDiagonalIntersections.lean"


def matrix(genus: int) -> tuple[tuple[int, int, int], ...]:
    if type(genus) is not int or genus < 0:
        raise ValueError("genus must be a nonnegative integer")
    return ((0, 1, 1), (1, 0, 1), (1, 1, 2 - 2 * genus))


def determinant_3x3(m: tuple[tuple[int, int, int], ...]) -> int:
    if not isinstance(m, (tuple, list)) or len(m) != 3 or any(
        not isinstance(r, (tuple, list)) or len(r) != 3
        or any(type(x) is not int for x in r) for r in m
    ):
        raise ValueError("expected an exact 3 by 3 integer matrix")
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def pairing(genus: int, x, y) -> Fraction:
    """Bilinear pairing on a FORMAL three-generator divisor lattice."""
    m = matrix(genus)
    if not isinstance(x, (tuple, list)) or not isinstance(y, (tuple, list)):
        raise ValueError("coefficient vectors must be 3-tuples")
    if len(x) != 3 or len(y) != 3:
        raise ValueError("coefficient vectors must be 3-tuples")
    if any(type(v) not in (int, Fraction) for v in (*x, *y)):
        raise ValueError("coefficients must be exact rational numbers")
    return sum(
        (Fraction(x[i]) * m[i][j] * Fraction(y[j])
         for i in range(3) for j in range(3)),
        Fraction(0),
    )


def intersection_signature(genus: int, coefficients) -> tuple[Fraction, Fraction, Fraction]:
    basis = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    return tuple(pairing(genus, coefficients, b) for b in basis)


def diagonal_span_obstruction(genus: int) -> dict:
    """Compare the pairings of Delta with a F1+b F2.

    Pairing with F1 and F2 forces b=1, a=1. The third test then
    gives a residual 2*g, so no rational a,b exist if genus > 0.
    """
    m = matrix(genus)
    delta = (0, 0, 1)
    # Solve pairings with F1 and F2 by exact rational arithmetic.
    # (aF1+bF2).F1=b, and (aF1+bF2).F2=a.
    f1 = (1, 0, 0)
    f2 = (0, 1, 0)
    a = pairing(genus, delta, f2)
    b = pairing(genus, delta, f1)
    candidate = (a, b, 0)
    target_signature = intersection_signature(genus, delta)
    candidate_signature = intersection_signature(genus, candidate)
    residual = candidate_signature[2] - target_signature[2]
    if residual != 2 * genus:
        raise AssertionError("diagonal residual disagrees with geometric matrix")
    det = determinant_3x3(m)
    if det != 2 * genus:
        raise AssertionError("general-genus intersection determinant must be 2*g")
    return {
        "genus": genus,
        "intersection_matrix": [list(row) for row in m],
        "determinant": det,
        "candidate_fiber_coefficients": [int(a), int(b)],
        "target_diagonal_pairings": [int(x) for x in target_signature],
        "candidate_fiber_pairings": [int(x) for x in candidate_signature],
        "third_pairing_residual": int(residual),
        "diagonal_excluded_from_two_fiber_rational_span": genus > 0,
        "positive_genus_independence_if_geometric_inputs_hold": genus > 0,
    }


def audit(max_genus: int = 10) -> dict:
    if type(max_genus) is not int or not 1 <= max_genus <= 100:
        raise ValueError("max_genus must be an integer in 1..100")
    results = [diagonal_span_obstruction(g) for g in range(max_genus + 1)]
    if results[0]["determinant"] != 0 or results[0]["third_pairing_residual"] != 0:
        raise AssertionError("genus-zero degeneracy not recovered")
    if not all(r["diagonal_excluded_from_two_fiber_rational_span"]
               for r in results[1:]):
        raise AssertionError("positive-genus obstruction missing")
    return {
        "experiment": "MathOS-MILLENNIUM-006-HODGE-DIAGONAL-DIVISOR",
        "status": "ABSTRACT_EXACT_INTERSECTION_AUDIT_ONLY",
        "official_conjecture_proved": False,
        "mathematical_novelty_established": False,
        "independent_geometry_formalized": False,
        "independent_external_review": False,
        "assumed_geometric_inputs": {
            "F1_squared": 0,
            "F2_squared": 0,
            "F1_F2": 1,
            "F1_Delta": 1,
            "F2_Delta": 1,
            "Delta_squared": "2-2g",
        },
        "general_genus_paper_derivation": "det(M_g)=2*g; match F1,F2 forces a=b=1, mismatch on Delta=2*g",
        "formal_lean_scope": "linear-algebra consequence for genus-one abstract intersection matrix; not a geometry theorem",
        "formal_lean_theorem": "MathOS.elliptic_diagonal_not_in_fiber_span",
        "formal_source_sha256": hashlib.sha256(LEAN_SOURCE.read_bytes()).hexdigest(),
        "results": results,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--max-genus", type=int, default=10)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    report = audit(args.max_genus)
    data = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "max_genus": args.max_genus,
        "positive_genus_cases_confirmed": args.max_genus,
        "full_hodge_claim": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
