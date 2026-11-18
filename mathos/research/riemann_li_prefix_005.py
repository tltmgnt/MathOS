"""RH attempt 005: exact finite-Li-prefix obstruction for synthetic symmetric zero sets.

For any positive finite prefix length K, one can construct a FINITE, synthetic
multiset of zeros symmetric under conjugation and reflection rho -> 1-rho,
including a quartet off Re(rho)=1/2, whose first K Li-style coefficients
are strictly positive. This is NOT the zero set of the zeta function, not a
counterexample to Li's criterion, and not a Riemann-hypothesis proof.

The executable certificate uses exact fractions, not floating-point signs.
Only 1<=K<=12 is executed here; the note gives the general all-K argument.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEAN_FILE = ROOT / "formal" / "LiPrefixObstruction.lean"
PAIR = tuple[Fraction, Fraction]
ONE = Fraction(1)
ZERO = Fraction(0)
BASE_Q: PAIR = (Fraction(3, 5), Fraction(4, 5))


def complex_mul(a: PAIR, b: PAIR) -> PAIR:
    return (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])


def complex_pow(base: PAIR, exponent: int) -> PAIR:
    if type(exponent) is not int or exponent < 0:
        raise ValueError("exponent must be a nonnegative integer")
    result: PAIR = (ONE, ZERO)
    while exponent:
        if exponent % 2:
            result = complex_mul(result, base)
        base = complex_mul(base, base)
        exponent //= 2
    return result


def q_of_zero(real: Fraction, imag: Fraction) -> PAIR:
    """q(rho)=1-1/rho, exactly; rho is a nonzero complex rational."""
    denom = real*real + imag*imag
    if denom == 0:
        raise ValueError("rho cannot be zero")
    return (ONE-real/denom, imag/denom)


def base_li(n: int) -> Fraction:
    if type(n) is not int or n < 1:
        raise ValueError("index must be positive")
    return 2 - 2 * complex_pow(BASE_Q, n)[0]


def quartet_li(n: int, height: int) -> Fraction:
    """Off-line quartet rho, conj(rho), 1-rho, 1-conj(rho) with Re(rho)=3/4."""
    if type(n) is not int or n < 1 or type(height) is not int or height < 2:
        raise ValueError("positive Li index and height >= 2 required")
    rho_q = q_of_zero(Fraction(3, 4), Fraction(height))
    reflected_q = q_of_zero(Fraction(1, 4), Fraction(-height))
    return 4 - 2*complex_pow(rho_q, n)[0] - 2*complex_pow(reflected_q, n)[0]


def prefix_bound(prefix_length: int, height: int) -> Fraction:
    """Triangle/binomial bound for the absolute four-zero perturbation."""
    if type(prefix_length) is not int or prefix_length < 1:
        raise ValueError("prefix length must be positive")
    if type(height) is not int or height < 2:
        raise ValueError("height must be at least two")
    return 4 * ((ONE + Fraction(1, height))**prefix_length - 1)


def choose_height(prefix_length: int) -> tuple[int, Fraction, Fraction]:
    """Construct an exact quantitative witness; no model or external library."""
    if type(prefix_length) is not int or not 1 <= prefix_length <= 12:
        raise ValueError("executable prefix must lie in 1..12")
    min_base = min(base_li(n) for n in range(1, prefix_length+1))
    if min_base <= 0:
        raise AssertionError("base pair must have positive finite prefix")
    height = 2
    for _ in range(40):
        bound = prefix_bound(prefix_length, height)
        if bound < min_base:
            return height, min_base, bound
        height *= 2
    raise RuntimeError("did not locate finite height for required positive gap")


def _fraction(f: Fraction) -> dict:
    return {"numerator": f.numerator, "denominator": f.denominator}


def certificate(prefix_length: int = 8) -> dict:
    height, margin, perturbation_bound = choose_height(prefix_length)
    r = Fraction(3, 4)
    t = Fraction(height)
    rho_q = q_of_zero(r, t)
    reflected_q = q_of_zero(ONE-r, -t)
    # Reflection acts as q -> 1/q, checked in rational coordinate arithmetic.
    q_norm = rho_q[0]**2 + rho_q[1]**2
    if complex_mul(rho_q, reflected_q) != (ONE, ZERO):
        raise AssertionError("reflection does not invert q")
    if q_norm == 1 or r == Fraction(1, 2):
        raise AssertionError("off-critical-line quartet required")
    if q_of_zero(Fraction(1, 2), ONE) != BASE_Q:
        raise AssertionError("incorrect critical-line baseline")

    rows = []
    for n in range(1, prefix_length + 1):
        b = base_li(n)
        delta = quartet_li(n, height)
        total = b + delta
        # triangle inequality plus exact strict margin
        if abs(delta) > prefix_bound(n, height):
            raise AssertionError("quartet violates stated analytic upper bound")
        if b <= 0 or total <= 0 or b - abs(delta) <= 0:
            raise AssertionError("finite prefix sign not established")
        rows.append({
            "index": n,
            "baseline": _fraction(b),
            "off_line_quartet_perturbation": _fraction(delta),
            "augmented_li_style_value": _fraction(total),
            "strictly_positive": True,
        })

    return {
        "attempt": "MathOS-MILLENNIUM-005-RH-SYNTHETIC-LI-PREFIX",
        "status": "EXACT_SYNTHETIC_COUNTERMODEL_ONLY",
        "canonical_mathos_certification": "NOT_CERTIFIED",
        "target": "Riemann hypothesis / all-index Li criterion",
        "full_rh_proved": False,
        "rh_disproved": False,
        "zeta_zero_claim": False,
        "mathematical_novelty_established": False,
        "independent_review_completed": False,
        "zero_set_type": "synthetic finite multiset, NOT the zeta zeros",
        "symmetries": ["complex conjugation", "rho -> 1-rho"],
        "critical_line_pair": ["1/2+i", "1/2-i"],
        "off_critical_line_quartet": [
            f"3/4+{height}i",
            f"3/4-{height}i",
            f"1/4+{height}i",
            f"1/4-{height}i",
        ],
        "off_line_height": height,
        "tested_positive_prefix_length": prefix_length,
        "minimum_baseline_coefficient": _fraction(margin),
        "certified_absolute_quartet_bound": _fraction(perturbation_bound),
        "certified_positive_lower_bound": _fraction(margin-perturbation_bound),
        "all_prefix_coefficients_positive": all(row["strictly_positive"] for row in rows),
        "synthetic_li_style_coefficients": rows,
        "formal_congruence_theorem": "MathOS.liBaseNumerator_modFive",
        "lean_source_sha256": hashlib.sha256(LEAN_FILE.read_bytes()).hexdigest(),
        "limitations": [
            "Artificial finite symmetric zero multiset, not zeros of Riemann xi",
            "Demonstrates no implication from a finite Li-style prefix alone in the synthetic class",
            "The all-prefix-length existence proof is a separate analytic argument in the note",
            "Lean formalizes one Gaussian-integer all-n congruence, not the full construction",
            "Numerical probes for actual Riemann zeta cannot prove RH or its negation",
        ],
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prefix", type=int, default=8)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    report = certificate(args.prefix)
    result = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "prefix": report["tested_positive_prefix_length"],
        "height": report["off_line_height"],
        "positive": report["all_prefix_coefficients_positive"],
        "zeta_zero_claim": report["zeta_zero_claim"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
