"""TECT-X RH spectral-route audit: exact fixed-log-interval dilation spectrum.

This module provides an exact counting checker for the *toy* compactification
and reports a known asymptotic obstruction. It does not construct a
Hilbert--Polya operator or establish the Riemann hypothesis.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path


def positive_circle_eigen_count(radius: Fraction, phase: Fraction = Fraction(0)) -> int:
    """Count 0 < n+phase <= radius for integer n, 0 <= phase < 1.

    For H=-i d/dy on [0,L] with g(L)=exp(2πi phase)g(0), the
    eigenvalues are (2π/L)(n+phase), n in Z.
    radius is T*L/(2π), not a physical ordinate or zeta zero.
    The arithmetic is exact; no pi or float approximation occurs.
    """
    if not isinstance(radius, Fraction) or radius < 0:
        raise ValueError("radius must be a nonnegative Fraction")
    if not isinstance(phase, Fraction) or not 0 <= phase < 1:
        raise ValueError("phase must be a Fraction in [0, 1)")
    if phase == 0:
        return radius.numerator // radius.denominator
    if radius < phase:
        return 0
    d = radius - phase
    return 1 + d.numerator // d.denominator


def _fraction(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def build_report(max_radius: int = 12, phase: Fraction = Fraction(0)) -> dict:
    """Report exact finite spectral counting and the *externally known* asymptotic."""
    if type(max_radius) is not int or not 1 <= max_radius <= 2000:
        raise ValueError("max_radius must lie in 1..2000")
    if not isinstance(phase, Fraction) or not 0 <= phase < 1:
        raise ValueError("invalid fractional boundary phase")
    rows = []
    for k in range(1, max_radius + 1):
        radius = Fraction(k)
        count = positive_circle_eigen_count(radius, phase)
        # Exact discrete derivative in normalized energy (unit intervals).
        prior = positive_circle_eigen_count(Fraction(k-1), phase)
        if count-prior != 1:
            raise AssertionError("unexpected fixed-interval spectral spacing")
        rows.append({
            "normalized_radius": k,
            "positive_eigenvalue_count": count,
            "unit_interval_increment": count-prior,
        })
    source = Path(__file__).read_bytes()
    return {
        "schema": "mathos_tectx_rh_spectral_obstruction/1",
        "status": "BOUNDED_TOY_SPECTRAL_AUDIT_NOT_RH_PROOF",
        "candidate": "unmodified_dilation_operator_fixed_log_interval",
        "phase": _fraction(phase),
        "normalization": "radius = T*L/(2*pi) with fixed L > 0",
        "exact_eigenvalues": "lambda_n = 2*pi*(n+phase)/L, n in Z",
        "full_half_line": {
            "unitary_map": "(Uf)(y)=exp(y/2)*f(exp(y)), y in R",
            "conjugated_operator": "-i*d/dy on L2(R,dy), domain H1(R)",
            "point_spectrum": "EMPTY",
            "spectral_type": "purely absolutely continuous, sigma(H)=R",
            "mathematical_basis": "unitary equivalence to momentum operator; requires standard spectral theorem",
        },
        "fixed_log_interval": {
            "boundary_condition": "g(L)=exp(2*pi*i*phase)*g(0)",
            "domain": "H1([0,L]) satisfying stated boundary condition",
            "eigenvalue_growth": "N_H(T)=L*T/(2*pi)+O(1) for T -> infinity",
            "zeta_counting_input": "N_zeta(T)=(T/(2*pi))*log(T/(2*pi))-T/(2*pi)+O(log T)",
            "asymptotic_incompatibility": (
                "For fixed L and phase, N_H(T)/(T*log T)->0, "
                "whereas N_zeta(T)/(T*log T)->1/(2*pi). "
                "Thus the two multisets cannot coincide with multiplicities."
            ),
            "comparison_is_analytic": True,
            "exact_sample_rows": rows,
        },
        "required_missing_bridges": [
            "independently construct an operator from arithmetic data",
            "establish self-adjointness on an explicit, suitable domain",
            "obtain the Riemann-von Mangoldt density, not a fixed-spacing model",
            "prove a noncircular identity covering every nontrivial zero, multiplicities, and off-line alternatives",
        ],
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "external_theorems_assumed": [
            "spectral theorem for the self-adjoint momentum operator",
            "Riemann-von Mangoldt zero counting formula",
        ],
        "assurance": {
            "spectral_route_closed": False,
            "riemann_hypothesis_proved": False,
            "nontrivial_zeta_zero_certified": False,
            "novel_math_claim": False,
            "independent_mathematical_review": False,
        },
        "limitations": [
            "Rules out only the stated free dilation operator and fixed-length quasiperiodic compactification.",
            "Does not exclude arithmetic modifications, energy-dependent geometry, more general boundary conditions, or other Hilbert-Polya programs.",
            "A finite count sample never proves an asymptotic theorem.",
            "Numerical eigenvalue fitting alone cannot certify the location of all zeta zeros.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-radius", type=int, default=12)
    parser.add_argument("--phase-numerator", type=int, default=0)
    parser.add_argument("--phase-denominator", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        phase = Fraction(args.phase_numerator, args.phase_denominator)
        result = build_report(args.max_radius, phase)
    except (ValueError, ZeroDivisionError) as exc:
        parser.error(str(exc))
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
