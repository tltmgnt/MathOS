"""BSD research attack 007: exact inert-prime local point-count blind spot.

For E_d: y^2 = x^3 - d^2*x, p a good prime with p=3 (mod 4),
the elementary quadratic-character pairing implies #E_d(F_p)=p+1.
This holds for d=1 and d=5 at every such prime, even though their
rational ranks are known externally to be 0 and 1, respectively.

This executable checker enumerates only finitely many small primes.
It cannot prove the global all-prime theorem, the rational ranks,
an analytic rank, Sha finiteness, or any BSD Millennium assertion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEAN_FILE = ROOT / "formal" / "BSDInertPrimeBlindspot.lean"


def _require_int(value: object, name: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{name} must be an exact integer")
    return value


def is_prime(p: int) -> bool:
    _require_int(p, "p")
    if p < 2:
        return False
    if p == 2:
        return True
    if p % 2 == 0:
        return False
    trial = 3
    while trial * trial <= p:
        if p % trial == 0:
            return False
        trial += 2
    return True


def validate_good_prime(d: int, p: int) -> None:
    _require_int(d, "d")
    _require_int(p, "p")
    if d == 0 or p < 3 or p % 2 == 0 or not is_prime(p) or d % p == 0:
        raise ValueError("require nonzero d and odd prime p not dividing d")


def cubic_mod_p(d: int, x: int, p: int) -> int:
    validate_good_prime(d, p)
    _require_int(x, "x")
    return (x * x * x - d * d * x) % p


def legendre_symbol(value: int, p: int) -> int:
    """Quadratic character, with chi(0)=0; validated Euler criterion."""
    _require_int(value, "value")
    _require_int(p, "p")
    if p < 3 or p % 2 == 0 or not is_prime(p):
        raise ValueError("Legendre symbol requires an odd prime")
    a = value % p
    if a == 0:
        return 0
    out = pow(a, (p - 1) // 2, p)
    if out == 1:
        return 1
    if out == p - 1:
        return -1
    raise AssertionError("Euler's criterion returned an impossible residue")


def curve_point(d: int, x: Fraction, y: Fraction) -> bool:
    _require_int(d, "d")
    if d == 0 or type(x) is not Fraction or type(y) is not Fraction:
        raise ValueError("nonzero integer d and exact rational coordinates required")
    return y * y == x * x * x - d * d * x


def number_of_points_bruteforce(d: int, p: int) -> int:
    """Independent y-enumeration, including the elliptic point at infinity."""
    validate_good_prime(d, p)
    y_squares = [0] * p
    for y in range(p):
        y_squares[(y * y) % p] += 1
    return 1 + sum(y_squares[cubic_mod_p(d, x, p)] for x in range(p))


def number_of_points_character(d: int, p: int) -> tuple[int, int]:
    """Independent character sum: p + 1 + sum_x chi(f(x))."""
    validate_good_prime(d, p)
    character_sum = sum(
        legendre_symbol(cubic_mod_p(d, x, p), p) for x in range(p)
    )
    return p + 1 + character_sum, character_sum


def pairing_cancellation(d: int, p: int) -> bool:
    """Test x <-> -x pairing when -1 is nonsquare at p=3 mod 4."""
    validate_good_prime(d, p)
    if p % 4 != 3:
        raise ValueError("pairwise cancellation assertion requires p=3 mod 4")
    if legendre_symbol(-1, p) != -1:
        raise AssertionError("-1 should be a nonsquare at primes p=3 mod 4")
    if legendre_symbol(cubic_mod_p(d, 0, p), p) != 0:
        raise AssertionError("fixed point must have zero contribution")
    for x in range(1, (p + 1) // 2):
        y = (-x) % p
        if (x * x * x - d * d * x +
                (y * y * y - d * d * y)) % p != 0:
            raise AssertionError("cubic oddness failed modulo p")
        a = legendre_symbol(cubic_mod_p(d, x, p), p)
        b = legendre_symbol(cubic_mod_p(d, y, p), p)
        if a + b != 0:
            raise AssertionError("nonzero pair character sum")
    return True


def exact_rational_witness() -> dict:
    x, y = Fraction(25, 4), Fraction(75, 8)
    if not curve_point(5, x, y):
        raise AssertionError("rational witness is not on E5")
    if x.denominator != 4 or y == 0:
        raise AssertionError("unexpected point denominators")
    for d in (1, 5):
        for t in (-d, 0, d):
            if not curve_point(d, Fraction(t), Fraction(0)):
                raise AssertionError("expected rational two-torsion point absent")
    return {
        "curve": "E5: y^2=x^3-25x",
        "x": {"numerator": x.numerator, "denominator": x.denominator},
        "y": {"numerator": y.numerator, "denominator": y.denominator},
        "y_squared": {"numerator": (y*y).numerator, "denominator": (y*y).denominator},
        "x_cubed_minus_25x": {
            "numerator": (x*x*x-25*x).numerator,
            "denominator": (x*x*x-25*x).denominator,
        },
        "point_on_curve_verified_exactly": True,
        "x_nonintegral": True,
        "non_torsion_conclusion_uses_external_nagell_lutz_theorem": True,
        "rank_one_or_higher_not_independently_proved_by_software": True,
    }


def audit(prime_limit: int = 101) -> dict:
    _require_int(prime_limit, "prime_limit")
    if not 11 <= prime_limit <= 401:
        raise ValueError("finite prime limit is restricted to 11..401")
    rows = []
    for p in range(3, prime_limit + 1, 2):
        if not is_prime(p):
            continue
        if p in (2, 5):
            continue
        n1 = number_of_points_bruteforce(1, p)
        n5 = number_of_points_bruteforce(5, p)
        alt1, sum1 = number_of_points_character(1, p)
        alt5, sum5 = number_of_points_character(5, p)
        if n1 != alt1 or n5 != alt5:
            raise AssertionError(f"point counting methods disagree at {p}")
        inert = p % 4 == 3
        if inert:
            if not pairing_cancellation(1, p) or not pairing_cancellation(5, p):
                raise AssertionError("inert prime pairing failure")
            if n1 != p + 1 or n5 != p + 1:
                raise AssertionError("expected exact inert-prime coincidence")
            if sum1 != 0 or sum5 != 0:
                raise AssertionError("inert-prime a_p nonzero")
        rows.append({
            "p": p,
            "p_mod_4": p % 4,
            "good_for_both": True,
            "inert_subsequence": inert,
            "E1_points": n1,
            "E5_points": n5,
            "E1_ap": p + 1 - n1,
            "E5_ap": p + 1 - n5,
            "same_count": n1 == n5,
            "pairing_verified_if_inert": inert,
        })
    inert = [r for r in rows if r["inert_subsequence"]]
    split = [r for r in rows if not r["inert_subsequence"]]
    if len(inert) < 3 or not split:
        raise AssertionError("audit must test inert and split primes")
    if not any(r["E1_points"] != r["E5_points"] for r in split):
        raise AssertionError("should observe a difference outside inert primes")
    return {
        "attempt": "MATHOS-MILLENNIUM-007-BSD-INERT-LOCAL-FACTORS",
        "status": "EXACT_BOUNDED_LOCAL_AUDIT_NOT_BSD",
        "target": "Birch and Swinnerton-Dyer conjecture over Q",
        "general_all_prime_claim": (
            "For every odd prime p=3 mod 4 and any nonzero integer d with p not dividing d,"
            " #E_d(F_p)=p+1; proof in the research note using character pairing."
        ),
        "finite_prime_limit": prime_limit,
        "tested_good_primes": len(rows),
        "tested_inert_primes": len(inert),
        "two_curve_inert_factor_coincidences": len(inert),
        "E1": "y^2=x^3-x",
        "E5": "y^2=x^3-25x",
        "known_rank_input_from_external_literature_only": {
            "E1": "rank 0; LMFDB 32.a3 and Alice Silverberg ECC2001",
            "E5": "rank 1; Alice Silverberg ECC2001 descent",
        },
        "rational_point_certificate": exact_rational_witness(),
        "point_counts": rows,
        "formal_lean_theorem": "MathOS.bsdCharacter_pair_cancel",
        "formal_lean_scope": "odd cubic plus cancellation conditional on character negation; no finite fields, ranks or L-functions formalized",
        "lean_source_sha256": hashlib.sha256(LEAN_FILE.read_bytes()).hexdigest(),
        "establishes_general_bsd_rank_equality": False,
        "establishes_analytic_rank_or_l_function": False,
        "establishes_sha_finiteness": False,
        "establishes_refined_leading_term": False,
        "mathematical_novelty_established": False,
        "independent_external_review_completed": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime-limit", type=int, default=101)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = audit(args.prime_limit)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "status": result["status"],
        "tested_good_primes": result["tested_good_primes"],
        "tested_inert_primes": result["tested_inert_primes"],
        "two_curve_inert_factor_coincidences": result["two_curve_inert_factor_coincidences"],
        "bsd_proved": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
