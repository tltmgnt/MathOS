"""TECT-X prime-diagonal Fredholm determinant in Re(s)>1.

Constructs a bona fide trace-class arithmetic operator A_s on l2(primes),
checks finite Euler products / trace identities, and provides rigorous
real-axis error bounds. No continuation to nontrivial zeta zeros is claimed.
"""
from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path

MAX_PRIME_BOUND = 100_000


def primes_up_to(bound: int) -> list[int]:
    if type(bound) is not int or not 2 <= bound <= MAX_PRIME_BOUND:
        raise ValueError("prime bound must be an integer in 2..100000")
    sieve = bytearray(b"\x01") * (bound + 1)
    sieve[0:2] = b"\x00\x00"
    for n in range(2, math.isqrt(bound) + 1):
        if sieve[n]:
            sieve[n * n:bound + 1:n] = b"\x00" * ((bound - n * n) // n + 1)
    return [i for i in range(2, bound + 1) if sieve[i]]


def prime_spectral_data(sigma: float, height: float, prime_bound: int, depth: int = 5) -> dict:
    """Return finite principal log determinant and traced prime powers.

    A_s e_p = p^(-s)e_p on l2(P), s=sigma+i*height. The infinite A_s
    is trace class for sigma>1. Finite results are NOT its full determinant.
    """
    if not (isinstance(sigma, (float, int)) and math.isfinite(sigma) and sigma > 1):
        raise ValueError("sigma must be finite and >1")
    if not (isinstance(height, (float, int)) and math.isfinite(height)):
        raise ValueError("height must be finite")
    if type(depth) is not int or not 1 <= depth <= 50:
        raise ValueError("depth must lie in 1..50")
    primes = primes_up_to(prime_bound)
    s = complex(sigma, height)
    values = [cmath.exp(-s * math.log(p)) for p in primes]
    logdet = sum((cmath.log(1 - z) for z in values), 0j)
    # Exact algebraic identity for each finite block:
    # -(d/ds) log det(I-A_s) = sum_p (log p)*p^-s/(1-p^-s).
    # On the real axis, -zeta'/zeta is the same positive prime-power sum,
    # while d/ds log det(I-A_s) is positive.
    derivative_logdet = sum((math.log(p) * z / (1 - z) for p, z in zip(primes, values)), 0j)
    traced_powers = [
        sum((z ** k for z in values), 0j) for k in range(1, depth + 1)
    ]
    # Euler tail bound for real sigma>1, P=prime_bound:
    # 0 <= log ζ(sigma)-log ζ_P(sigma) <=
    # P^(1-sigma)/((sigma-1)*(1-(P+1)^(-sigma))).
    tail_bound = prime_bound ** (1 - sigma) / ((sigma - 1) * (1 - (prime_bound + 1) ** (-sigma)))
    trace_norm_bound = 1 + 1 / (sigma - 1)
    return {
        "prime_count": len(primes),
        "finite_log_determinant": [logdet.real, logdet.imag],
        "finite_determinant": [cmath.exp(logdet).real, cmath.exp(logdet).imag],
        "logarithmic_derivative": [derivative_logdet.real, derivative_logdet.imag],
        "finite_power_traces": [[x.real, x.imag] for x in traced_powers],
        "finite_prime_power_derivative": [
            sum((math.log(p) * z * (1 - z ** depth) / (1 - z)
                 for p, z in zip(primes, values)), 0j).real,
            sum((math.log(p) * z * (1 - z ** depth) / (1 - z)
                 for p, z in zip(primes, values)), 0j).imag,
        ],
        "finite_log_zeta_real_axis_error_bound": tail_bound,
        "trace_norm_upper_bound": trace_norm_bound,
        "tail_bound_scope": "only real sigma>1, not complex error bound for determinant value",
        "prime_bound": prime_bound,
        "depth": depth,
    }


def build_report(sigma: float = 2.0, height: float = 0.0, bound: int = 1000, depth: int = 5) -> dict:
    data = prime_spectral_data(sigma, height, bound, depth)
    return {
        "schema": "tectx_prime_fredholm/1",
        "status": "PROVED_HALF_PLANE_ONLY_GLOBAL_ZERO_CORRESPONDENCE_OPEN",
        "operator": "A_s e_p = p^(-s)e_p on ell2(primes)",
        "operator_domain": "all ell2(primes), bounded diagonal for Re(s)>1",
        "operator_theorem": {
            "trace_class": "sum_p |p^-s| = sum_p p^-Re(s) < infinity for Re(s)>1",
            "fredholm_determinant": "det(I-A_s)=prod_p(1-p^-s)=1/zeta(s), Re(s)>1",
            "log_derivative": "d/ds log det(I-A_s)=sum_(p,k>=1) log(p)*p^(-ks) = -zeta'(s)/zeta(s), Re(s)>1",
            "power_traces": "Tr(A_s^k)=sum_p p^(-ks), k>=1",
            "nonvanishing": "det(I-A_s) != 0 for Re(s)>1, since |p^-s|<1 and the infinite product converges absolutely",
            "trace_class_boundary": "the unregularized prime diagonal is not trace class for 0<Re(s)<=1, since sum_p p^-sigma diverges",
            "self_adjointness": "A_s is self-adjoint for real s>1, NOT for nonreal s",
            "global_identity": "NOT_DERIVED",
            "nontrivial_zero_correspondence": "NOT_DERIVED",
            "analytic_continuation": "zeta continues meromorphically by external theorems; this does not extend A_s as a trace-class family into the critical strip",
        },
        "inputs": {"sigma": sigma, "height": height, "max_prime": bound, "trace_depth": depth},
        "finite_checks": data,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "unresolved_gaps": [
            "Construct an independently defined trace or regularized determinant valid across 0<Re(s)<1",
            "Prove analytic continuation of that operator/determinant with fixed domain, admissible test functions and controlled regularization",
            "Establish a noncircular identity with completed xi(s) including gamma factors and the pole/trivial-zero cancellations",
            "Establish exact zero correspondence with all multiplicities and off-line alternatives, then derive location using a genuine self-adjoint operator",
        ],
        "assurance": {
            "rh_proved": False,
            "global_fredholm_identity": False,
            "critical_strip_trace_class": False,
            "zeta_zero_spectral_correspondence": False,
            "external_review": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sigma", type=float, default=2.0)
    parser.add_argument("--height", type=float, default=0.0)
    parser.add_argument("--prime-bound", type=int, default=1000)
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = build_report(args.sigma, args.height, args.prime_bound, args.depth)
    except (ValueError, OverflowError) as exc:
        parser.error(str(exc))
    payload = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
