"""YM research attack 008: finite 2D Z2 lattice gauge strip, exact arithmetic.

For a 1 x n rectangular strip with FREE boundary, there are n top links,
n bottom links, and n+1 vertical links. A link spin is (-1)^b, b in {0,1}.
Each plaquette Wilson sign is the product of its four link spins.
Assign relative Boltzmann weight t>0 to each positive plaquette and 1 to
each negative plaquette. This matches exp(beta*W) up to an overall constant
when t=exp(2 beta).

For every n>=0 the edge configurations map onto all n plaquette parities,
each with exactly 2^(2n+1) preimages. Hence
  Z_n(t) = 2^(2n+1) * (t+1)^n,
  <W_boundary> = ((t-1)/(t+1))^n.
These are 2D FINITE ABELIAN Z2 gauge-model statements.
No non-Abelian 4D continuum QFT, spectral operator or mass gap follows.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEAN_SOURCE = ROOT / "formal" / "YMZ2Strip.lean"


def _require_int(x, name, minimum=0, maximum=None):
    if type(x) is not int or x < minimum or (maximum is not None and x > maximum):
        raise ValueError(f"{name} must be an integer in the required range")
    return x


def edge_count(n: int) -> int:
    _require_int(n, "n")
    return 3 * n + 1


def validate_edges(n: int, bits):
    _require_int(n, "n")
    if not isinstance(bits, (tuple, list)) or len(bits) != edge_count(n):
        raise ValueError("expected precisely n top + n bottom + (n+1) vertical links")
    if any(type(v) is not int or v not in (0, 1) for v in bits):
        raise ValueError("links must be exact integer bits 0 or 1")


def plaquette_parities(n: int, bits) -> tuple[int, ...]:
    validate_edges(n, bits)
    return tuple(
        bits[i] ^ bits[n + i] ^ bits[2 * n + i] ^ bits[2 * n + i + 1]
        for i in range(n)
    )


def boundary_parity(n: int, bits) -> int:
    validate_edges(n, bits)
    return (
        (sum(bits[:n]) + sum(bits[n:2*n])
         + bits[2*n] + bits[3*n]) % 2
    )


def gauge_transform(n: int, bits, row: int, column: int) -> tuple[int, ...]:
    """Flip every incident link at one vertex (row: 0 top, 1 bottom)."""
    validate_edges(n, bits)
    _require_int(row, "row", maximum=1)
    _require_int(column, "column", maximum=n)
    out = list(bits)
    affected = [2 * n + column]
    offset = 0 if row == 0 else n
    if column > 0:
        affected.append(offset + column - 1)
    if column < n:
        affected.append(offset + column)
    for idx in affected:
        out[idx] ^= 1
    return tuple(out)


def closed_form(n: int, t: int) -> dict:
    _require_int(n, "n")
    _require_int(t, "t", minimum=1)
    fiber = 2 ** (2*n + 1)
    partition = fiber * (t + 1) ** n
    wilson_numerator = fiber * (t - 1) ** n
    expectation = Fraction(wilson_numerator, partition)
    return {
        "n": n,
        "t": t,
        "edges": edge_count(n),
        "plaquette_count": n,
        "per_parity_fiber": fiber,
        "partition": partition,
        "boundary_wilson_numerator": wilson_numerator,
        "boundary_wilson_expectation": {
            "numerator": expectation.numerator,
            "denominator": expectation.denominator,
        },
    }


def exhaustive_strip(n: int, t: int, verify_gauge=False) -> dict:
    """Enumerate only tiny strips, independent of formula closed_form."""
    _require_int(n, "n", maximum=5)
    _require_int(t, "t", minimum=1, maximum=9)
    partition = 0
    numerator = 0
    by_parity: dict[tuple[int, ...], int] = {}
    for bits in itertools.product((0, 1), repeat=edge_count(n)):
        p = plaquette_parities(n, bits)
        by_parity[p] = by_parity.get(p, 0) + 1
        b = boundary_parity(n, bits)
        if b != sum(p) % 2:
            raise AssertionError("interior link cancellation / Stokes identity failed")
        weight = t ** sum(1 for sign_bit in p if sign_bit == 0)
        partition += weight
        numerator += (-weight if b else weight)
        if verify_gauge:
            for j in range(n + 1):
                for row in (0, 1):
                    changed = gauge_transform(n, bits, row, j)
                    if plaquette_parities(n, changed) != p:
                        raise AssertionError("plaquette is not gauge invariant")
                    if boundary_parity(n, changed) != b:
                        raise AssertionError("Wilson perimeter is not gauge invariant")
    expectation = Fraction(numerator, partition)
    expected = closed_form(n, t)
    if partition != expected["partition"] or numerator != expected["boundary_wilson_numerator"]:
        raise AssertionError("edge enumeration differs from independent parity formula")
    if len(by_parity) != 2**n:
        raise AssertionError("not all plaquette parity words are attainable")
    if set(by_parity.values()) != {expected["per_parity_fiber"]}:
        raise AssertionError("not every parity word has same fiber size")
    return {
        "n": n,
        "t": t,
        "configurations_checked": 2**edge_count(n),
        "gauge_check_each_vertex": verify_gauge,
        "distinct_plaquette_parity_words": len(by_parity),
        "per_parity_fiber": min(by_parity.values()),
        "partition": partition,
        "wilson_numerator": numerator,
        "expectation": {"numerator": expectation.numerator, "denominator": expectation.denominator},
    }


def scaling_row(k: int) -> dict:
    """Choose a=1/k, t=k*k+1, q=k^2/(k^2+2), no transcendental signs."""
    _require_int(k, "k", minimum=1)
    t = k*k + 1
    q = Fraction(k*k, k*k + 2)
    defect = 1-q
    distance_one_correlator = q**k
    one_minus = 1-distance_one_correlator
    bound = Fraction(2, k)
    if not 0 < q < 1 or not 0 <= one_minus <= k * defect <= bound:
        raise AssertionError("exact rational scaling bound fails")
    return {
        "k": k,
        "spacing": {"numerator": 1, "denominator": k},
        "relative_positive_weight_t": t,
        "single_step_q": {"numerator": q.numerator, "denominator": q.denominator},
        "unit_distance_wilson_factor": {
            "numerator": distance_one_correlator.numerator,
            "denominator": distance_one_correlator.denominator,
        },
        "unit_distance_defect": {"numerator": one_minus.numerator, "denominator": one_minus.denominator},
        "upper_bound_2_over_k": {"numerator": bound.numerator, "denominator": bound.denominator},
        "rational_inequality_verified": True,
    }


def audit(max_width: int = 5, scaling_max_k: int = 16) -> dict:
    _require_int(max_width, "max_width", maximum=5)
    _require_int(scaling_max_k, "scaling_max_k", minimum=2, maximum=64)
    cases = [
        exhaustive_strip(n, t, verify_gauge=n <= 3)
        for n in range(max_width + 1) for t in (1, 2, 5)
    ]
    scaling = [scaling_row(k) for k in range(2, scaling_max_k+1)]
    return {
        "attempt": "MATHOS-MILLENNIUM-008-YM-Z2-STRIP",
        "status": "EXACT_TWO_DIMENSIONAL_Z2_TOY_AUDIT_ONLY",
        "description": "2D single-row Z2 lattice gauge strip with open boundary",
        "finite_abelian_not_compact_simple": True,
        "formal_lean_theorem": "MathOS.ymGaugeFlipAB",
        "formal_lean_scope": "four-link Boolean gauge-invariance and independent-parity polynomial recurrences only",
        "formal_source_sha256": hashlib.sha256(LEAN_SOURCE.read_bytes()).hexdigest(),
        "all_n_paper_theorem": "Z_n=2^(2n+1)(t+1)^n; <W_boundary>=((t-1)/(t+1))^n, t>=1",
        "physical_scaling_example": (
            "a=1/k; t=k^2+1; q=k^2/(k^2+2); "
            "formal perimeter-decay rate m_eff=k*log(1+2/k^2)<=2/k -> 0"
        ),
        "cases": cases,
        "total_link_configurations_checked": sum(c["configurations_checked"] for c in cases),
        "scaling_rows": scaling,
        "proves_4d_yang_mills_exists": False,
        "constructs_continuum_qft": False,
        "constructs_physical_hilbert_space": False,
        "establishes_positive_physical_spectral_gap": False,
        "independent_external_review_completed": False,
        "novel_mathematics_claimed": False,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--max-width", type=int, default=5)
    p.add_argument("--scaling-max-k", type=int, default=16)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    report = audit(args.max_width, args.scaling_max_k)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "cases": len(report["cases"]),
        "total_link_configurations_checked": report["total_link_configurations_checked"],
        "physical_spectral_gap_proved": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
