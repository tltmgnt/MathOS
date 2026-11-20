"""TECT-X Hilbert--Polya trace/determinant identity gate for a fixed Jacobi operator.

Builds finite-section symmetric spectral determinants for the separately defined
fixed self-adjoint prime-power Jacobi candidate. The infinite determinant is
analytically defined as det(I-z*z*H^-2), since H^-2 is trace class. It has
real zeros only, but provably cannot equal xi(1/2+i*z) up to a zero-free
entire prefactor: its lowest eigenvalue misses the first zeta ordinate.

No RH proof, zero correspondence, or independent prime trace formula is claimed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from mathos.research.riemann_arithmetic_spectral import (
    FIRST_ZETA_ZERO_REFERENCE, TAU, inverse_main_term, von_mangoldt,
)
from mathos.research.riemann_fixed_jacobi import (
    PERTURBATION_NORM_UPPER, jacobi_coefficients,
)

MAX_SIZE = 4096


def logdet_positive_jacobi(diagonal: list[float], off: list[float], shift: float) -> float:
    """Log det(H_N+shift I) via positive LDL pivots.

    Only the provably positive-definite regime is supported; it never
    attempts a branch-sensitive complex logarithm or analytic continuation.
    """
    if not math.isfinite(shift) or not diagonal or len(off) != len(diagonal)-1:
        raise ValueError("invalid finite Jacobi parameters")
    pivot = diagonal[0] + shift
    if pivot <= 0:
        raise ValueError("matrix is not positive definite")
    result = math.log(pivot)
    for j in range(1, len(diagonal)):
        pivot = diagonal[j] + shift - off[j-1]*off[j-1]/pivot
        if not math.isfinite(pivot) or pivot <= 0:
            raise ValueError("matrix not positive definite")
        result += math.log(pivot)
    return result


def finite_symmetric_determinant(z: float, diagonal: list[float],
                                 off: list[float]) -> float:
    """D_N(z)=det(H_N-zI)det(H_N+zI)/det(H_N)^2, real |z| below floor."""
    if not isinstance(z, (int, float)) or not math.isfinite(z):
        raise ValueError("finite real z required")
    if abs(z) >= diagonal[0]-PERTURBATION_NORM_UPPER:
        raise ValueError("z must lie strictly below certified spectral floor")
    ld = (logdet_positive_jacobi(diagonal, off, -z) +
          logdet_positive_jacobi(diagonal, off, z) -
          2*logdet_positive_jacobi(diagonal, off, 0))
    return math.exp(ld)


def prime_power_dirichlet_prefix(sigma: float, length: int) -> float:
    """Finite (not certified infinite) sum of Lambda(n)*n^-sigma."""
    if not isinstance(sigma, (int, float)) or not math.isfinite(sigma) or sigma <= 1:
        raise ValueError("Euler prime-side check requires real sigma > 1")
    if type(length) is not int or not 2 <= length <= 10000:
        raise ValueError("Dirichlet prefix length must lie in 2..10000")
    return math.fsum(von_mangoldt(n)*n**(-sigma) for n in range(2, length+1))


def report(size: int = 256) -> dict:
    if type(size) is not int or not 32 <= size <= MAX_SIZE:
        raise ValueError("matrix size must lie in 32..4096")
    diag, off = jacobi_coefficients(size)
    floor = diag[0] - PERTURBATION_NORM_UPPER
    if not floor > FIRST_ZETA_ZERO_REFERENCE:
        raise AssertionError("first-zero obstruction must have strict margin")
    sample = (0.0, 5.0, 10.0, FIRST_ZETA_ZERO_REFERENCE, 15.0)
    rows = [
        {
            "real_spectral_parameter": z,
            "finite_symmetric_determinant": finite_symmetric_determinant(z, diag, off),
            "is_below_proved_spectral_floor": abs(z) < floor,
        }
        for z in sample
    ]
    if not all(r["finite_symmetric_determinant"] > 0 for r in rows):
        raise AssertionError("determinant must be positive below spectral floor")
    arithmetic_sample = prime_power_dirichlet_prefix(2.0, 4096)
    return {
        "schema": "mathos_tectx_fixed_operator_trace_identity_gate/1",
        "status": "GLOBAL_ZERO_FREE_FACTOR_IDENTITY_REFUTED_FOR_FIXED_JACOBI",
        "candidate": "fixed prime-power Jacobi self-adjoint operator from riemann_fixed_jacobi.py",
        "infinite_regularized_determinant": {
            "definition": "D_H(z)=det(I-z^2 H^(-2))=product_n(1-z^2/mu_n^2)",
            "trace_class_reason": "H^(-2) trace class since mu_n=a_n+O(1), a_n asymptotic to 2*pi*n/log(n), and sum(log n)^2/n^2 converges",
            "entire_even": True,
            "zeros": "exactly the real points +/- mu_n, with spectral multiplicities",
            "log_derivative": "D_H'(z)/D_H(z)=-2*z*Tr((H^2-z^2 I)^(-1)), off its zeros",
            "spectral_floor_lower": floor,
            "known_zeta_ordinate_reference": FIRST_ZETA_ZERO_REFERENCE,
            "determinant_nonzero_at_first_zeta_ordinate": True,
            "zero_free_entire_multiplier_exists": False,
            "zero_free_multiplier_refutation": "xi(1/2+i*gamma1)=0 but D_H(gamma1)>0 from the min-max floor; E(gamma1)D_H(gamma1) cannot vanish if E is entire and nowhere zero",
        },
        "arithmetic_trace_obligation": {
            "coordinate": "s=1/2+i*z; Re(s)>1 exactly when Im(z)<-1/2",
            "xi_log_derivative": "xi'(s)/xi(s)=1/s+1/(s-1)-(log pi)/2+digamma(s/2)/2 - sum_(n>=1) Lambda(n)*n^(-s), Re(s)>1",
            "required_identity": "i*xi'(s)/xi(s)=E'(z)/E(z)-2*z*Tr((H^2-z^2 I)^(-1)); s=1/2+i*z",
            "external_prime_gamma_requirements": [
                "full von Mangoldt prime-power series in the Euler half-plane",
                "archimedean digamma and log pi terms",
                "polar terms 1/s+1/(s-1)",
                "global holomorphic zero-free extension of E, not a definition E=xi/D_H with unchecked zeros",
            ],
            "real_sigma_example": 2.0,
            "finite_prime_power_prefix_length": 4096,
            "finite_prime_power_dirichlet_prefix": arithmetic_sample,
            "finite_prefix_is_full_prime_trace": False,
            "global_identity_proved": False,
        },
        "finite_diagnostic": {
            "matrix_size": size,
            "stability": "real LDL for positive-definite finite Jacobi blocks, not certified interval arithmetic",
            "rows": rows,
            "finite_determinants_do_not_certify_infinite_zeros": True,
        },
        "proof_obligations": {
            "RH.operator": "OPEN: fixed operator exists but has wrong spectrum",
            "RH.zero_identity": "OPEN: required zero-free multiplier identity explicitly refuted for this operator",
            "BRIDGE.RH.spectral": "OPEN: no critical-line theorem follows",
        },
        "assurance": {
            "riemann_hypothesis_proved": False,
            "global_spectral_identity_established": False,
            "fixed_operator_matches_zeta_zeros": False,
            "independent_review": False,
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        data = report(args.size)
    except ValueError as exc:
        parser.error(str(exc))
    payload = json.dumps(data, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
