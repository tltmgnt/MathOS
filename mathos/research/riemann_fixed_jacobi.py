"""Fixed self-adjoint arithmetic Jacobi candidate for the Hilbert-Pólya route.

An independently defined, non-diagonal prime-power-coupled operator on ℓ²(N).
It has compact resolvent, the Riemann-von Mangoldt counting asymptotic, and
an explicit spectral *mismatch* with the first zeta zero. NOT an RH proof.

Finite Sturm-count experiments are diagnostics, not computer-assisted proofs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from mathos.research.riemann_arithmetic_spectral import (
    TAU, FIRST_ZETA_ZERO_REFERENCE, MAX_INDEX, inverse_main_term, main_term,
    von_mangoldt,
)

COUPLING_SCALE = 0.2
PERTURBATION_NORM_UPPER = 2 * COUPLING_SCALE


def coupling(n: int) -> float:
    """Off-diagonal <e_n, B e_(n+1)> from a shifted prime-power index."""
    if type(n) is not int or not 1 <= n < MAX_INDEX:
        raise ValueError("invalid coupling index")
    return COUPLING_SCALE * von_mangoldt(n + 1) / (1 + math.log(n + 2))


def jacobi_coefficients(count: int) -> tuple[list[float], list[float]]:
    if type(count) is not int or not 2 <= count <= MAX_INDEX:
        raise ValueError("count must be an integer in 2..4096")
    return (
        [inverse_main_term(n) for n in range(1, count + 1)],
        [coupling(n) for n in range(1, count)],
    )


def sturm_count_below(t: float, diagonal: list[float], off_diagonal: list[float]) -> int:
    """Count finite Jacobi-matrix eigenvalues strictly below t via LDL pivots.

    This numerical routine uses a protective pivot when close to zero and is
    not a rigorous interval-certified eigenvalue counter. Generic thresholds
    far from eigenvalues are appropriate for regression diagnostics.
    """
    if not math.isfinite(t):
        raise ValueError("finite threshold required")
    if not diagonal or len(off_diagonal) != len(diagonal) - 1:
        raise ValueError("incompatible Jacobi coefficients")
    if any(not math.isfinite(x) for x in diagonal + off_diagonal):
        raise ValueError("nonfinite Jacobi coefficient")
    pivot = diagonal[0] - t
    negative = 0
    for j in range(len(diagonal)):
        if j:
            pivot = diagonal[j] - t - off_diagonal[j - 1] ** 2 / pivot
        if abs(pivot) < 1e-12:
            pivot = -1e-12  # approximate tie convention, never a proof
        negative += pivot < 0
    return negative


def report(count: int = 256) -> dict:
    diagonal, off_diagonal = jacobi_coefficients(count)
    norm_upper = PERTURBATION_NORM_UPPER
    if not (diagonal[0] - norm_upper > TAU * math.e - norm_upper > FIRST_ZETA_ZERO_REFERENCE):
        raise AssertionError("first zero obstruction was not verified")
    if not any(x > 0 for x in off_diagonal):
        raise AssertionError("candidate should be genuinely non-diagonal")
    thresholds = [25., 50., 100., 200.]
    if diagonal[-1] - norm_upper <= max(thresholds):
        raise ValueError("finite truncation too short to guarantee counting window")
    rows = []
    for t in thresholds:
        observed = sturm_count_below(t, diagonal, off_diagonal)
        lower = sum(v < t - norm_upper for v in diagonal)
        upper = sum(v < t + norm_upper for v in diagonal)
        if not lower <= observed <= upper:
            raise AssertionError("Sturm diagnostic violates minmax perturbation bracket")
        rows.append({
            "height": t, "jacobi_count_below": observed,
            "unperturbed_lower": lower, "unperturbed_upper": upper,
            "rv_mangoldt_main_term": main_term(t),
        })
    return {
        "schema": "mathos_tectx_fixed_jacobi_hilbert_polya_gate/1",
        "status": "FIXED_SELF_ADJOINT_ARITHMETIC_OPERATOR_ZERO_IDENTITY_REFUTED",
        "operator": {
            "space": "ell2(N positive)",
            "domain": "{x: sum_n a_n^2*abs(x_n)^2 finite}",
            "action": "(Hx)_n = a_n*x_n + b_(n-1)*x_(n-1) + b_n*x_(n+1), b_0=0",
            "diagonal": "a_n=unique T>2*pi*e with F(T)=n; F(T)=T/(2*pi)*(log(T/(2*pi))-1)",
            "off_diagonal": "b_n=0.2*Lambda(n+1)/(1+log(n+2)), n>=1",
            "independence_from_zero_table": True,
            "self_adjointness": "diagonal maximal self-adjoint operator plus bounded symmetric Jacobi perturbation",
            "bounded_perturbation_norm_upper": norm_upper,
            "compact_resolvent": True,
            "eigenvalue_minmax": "abs(lambda_n(H)-a_n)<=0.4 for eigenvalues in nondecreasing order with multiplicity",
            "counting": "N_H(T)=F(T)+O(log T), via minmax and mean-value theorem",
            "smallest_spectral_point_lower": diagonal[0] - norm_upper,
            "first_zeta_ordinate_external_reference": FIRST_ZETA_ZERO_REFERENCE,
            "first_ordinate_spectral_mismatch": True,
            "is_parameter_dependent": False,
            "is_fixed_self_adjoint": True,
            "is_hilbert_polya_realization": False,
        },
        "finite_diagnostic": {
            "matrix_size": count,
            "couplings_nonzero": sum(w > 0 for w in off_diagonal),
            "counting_rows": rows,
            "arithmetic_type": "floating-point Sturm LDL, not a formal zero certificate",
        },
        "missing_beyond_self_adjointness": [
            "independently derive a global determinant or trace identity with completed xi",
            "demonstrate actual spectral correspondence for every zero including multiplicities and possible off-line zeros",
            "avoid engineering the counting law from known Riemann-von Mangoldt asymptotics",
            "obtain independent mathematical and kernel-level verification of any proposed new relation",
        ],
        "assurance": {
            "rh_proved": False,
            "spectral_zero_correspondence": False,
            "new_theorem_claimed": False,
            "independent_external_review": False,
            "clay_route_completed": False,
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--count", type=int, default=256)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        value = report(args.count)
    except ValueError as exc:
        p.error(str(exc))
    payload = json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
