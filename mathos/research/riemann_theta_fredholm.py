"""TECT-X global theta/Fredholm family, with a strict spectral trust boundary.

A rank-one holomorphic trace-class operator K_s is defined directly from the
Jacobi theta series, without taking zeta zeros as input. Its Fredholm determinant
is the classical completed Riemann xi function for all complex s.

This is a reformulation of the classical theta-integral representation, NOT
a self-adjoint Hilbert--Polya spectral realization or a proof of RH.
Finite quadratures below are diagnostics, not certified enclosures.
"""
from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path

PI = math.pi
FIRST_ZERO_HEIGHT = 14.134725141734693  # external approximate reference only


def theta_tail(x: float, terms: int = 8) -> float:
    """psi(x)=sum_{n>=1} exp(-pi*n*n*x), evaluated with finite terms on x>=1."""
    if not math.isfinite(x) or x < 1:
        raise ValueError("theta series evaluation requires finite x>=1")
    if type(terms) is not int or not 1 <= terms <= 64:
        raise ValueError("terms must be an integer in 1..64")
    return math.fsum(math.exp(-PI*n*n*x) for n in range(1, terms + 1))


def theta_integrand(s: complex, x: float, terms: int = 8) -> complex:
    """Integrand in the globally convergent classical xi theta representation."""
    a = theta_tail(x, terms)
    lx = math.log(x)
    return a * (cmath.exp((s/2-1)*lx) + cmath.exp(-((s+1)/2)*lx))


def u_kernel(s: complex, x: float, terms: int = 8) -> complex:
    """Rank-one kernel vector u_s(x); v(x)=exp(-(x-1)).

    K_s f = u_s * <v,f> on L2([1,infinity)), with <v,f>=int v(x)f(x) dx.
    """
    v = math.exp(-(x - 1))
    return v - (s*(s-1)/2) * math.exp(x-1) * theta_integrand(s, x, terms)


def determinant_approx(s: complex, xmax: float = 12, panels: int = 4096,
                       terms: int = 8) -> complex:
    """Composite Simpson approximation of det(I-K_s)=xi(s).

    Tr(K_s)=1/2 - (s(s-1)/2) integral_1^infinity psi(x)(...)dx.
    Numerical integration replaces infinity by xmax. No certified interval
    error bound is returned; result cannot independently certify a zero.
    """
    if not isinstance(s, (complex, int, float)):
        raise ValueError("s must be numeric")
    s = complex(s)
    if not (math.isfinite(s.real) and math.isfinite(s.imag)
            and -4 <= s.real <= 5 and abs(s.imag) <= 35):
        raise ValueError("numeric diagnostic s lies outside bounded window")
    if not isinstance(xmax, (int, float)) or not math.isfinite(xmax) or not 4 <= xmax <= 24:
        raise ValueError("xmax must be finite and in [4,24]")
    if type(panels) is not int or panels < 512 or panels > 32768 or panels % 2:
        raise ValueError("panels must be an even integer in 512..32768")
    if type(terms) is not int or not 1 <= terms <= 64:
        raise ValueError("terms must be an integer in 1..64")
    step = (xmax - 1)/panels
    total = 0j
    for i in range(panels + 1):
        x = 1 + i*step
        coeff = 1 if i == 0 or i == panels else (4 if i % 2 else 2)
        total += coeff * theta_integrand(s, x, terms)
    return 0.5 + (s*(s-1)/2) * (step/3) * total


def audit(panels: int = 4096, xmax: float = 12, terms: int = 8) -> dict:
    samples = [0j, 1+0j, .5+0j, 2+0j, .7+2j,
               .5+FIRST_ZERO_HEIGHT*1j, .7+FIRST_ZERO_HEIGHT*1j]
    rows = []
    for s in samples:
        det = determinant_approx(s, xmax, panels, terms)
        reflected = determinant_approx(1-s, xmax, panels, terms)
        # Theta integrand is *pointwise* invariant under reflection.
        if abs(det-reflected) > 1e-9:
            raise AssertionError("theta reflection test failed")
        rows.append({
            "parameter": [s.real, s.imag],
            "determinant_approximation": [det.real, det.imag],
            "abs_determinant": abs(det),
            "reflection_discrepancy": abs(det-reflected),
        })
    return {
        "schema": "mathos_tectx_theta_fredholm_xi/1",
        "status": "GLOBAL_XI_DIVISOR_FROM_CLASSICAL_THETA_IDENTITY_NOT_HILBERT_POLYA",
        "operator": {
            "space": "L2([1,infinity),dx)",
            "v": "v(x)=exp(-(x-1))",
            "u_s": "u_s(x)=exp(-(x-1))-(s(s-1)/2)*exp(x-1)*psi(x)*(x^(s/2-1)+x^(-(s+1)/2))",
            "action": "(K_s f)(x)=u_s(x)*integral_1^infinity v(y)f(y)dy",
            "family": "entire in s with values in rank-one trace-class operators",
            "determinant": "det(I-K_s)=1/2+(s(s-1)/2)*int_1^infinity psi(x)*(x^(s/2-1)+x^(-(s+1)/2))dx=xi(s)",
            "theta_series": "psi(x)=sum_(n>=1) exp(-pi*n*n*x)",
            "derivation": "Jacobi theta modular identity + Mellin representation of completed zeta; no zeta zeros are input",
            "global_divisor": "zeros of det(I-K_s) are precisely all nontrivial zeta zeros, with analytic multiplicities, even if off the critical line",
            "gamma_and_poles": "xi(s)=s(s-1)*pi^(-s/2)*Gamma(s/2)*zeta(s)/2; theta subtraction removes s=0,1 poles and gamma/trivial-zero cancellations",
            "functional_equation": "K_(1-s)=K_s, hence det(I-K_(1-s))=det(I-K_s)",
            "is_fixed_self_adjoint_operator": False,
            "is_hilbert_polya_spectral_realization": False,
            "zero_correspondence_is_from_preexisting_xi_identity": True,
            "spectral_interpretation": "At each zero s, the s-dependent rank-one K_s has eigenvalue 1; this does not prove Re(s)=1/2",
        },
        "computation": {
            "panels": panels, "xmax": xmax, "theta_terms": terms,
            "method": "uncertified composite Simpson with truncated theta sum and integral",
            "samples": rows,
            "numerical_zero_certification": False,
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "remaining_proof_gaps": [
            "Find a fixed self-adjoint arithmetic operator with a real spectral parameter matching ordinates of all nontrivial zeros",
            "Supply a new noncircular spectral mechanism constraining Re(s)=1/2, not just repackaging the known xi function",
            "Independent review of operator-theoretic formulation, novelty and any proposed stronger implication",
        ],
        "assurance": {
            "rh_proved": False,
            "new_math_theorem_claimed": False,
            "fixed_self_adjoint_zero_operator": False,
            "independent_review_completed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panels", type=int, default=4096)
    parser.add_argument("--xmax", type=float, default=12)
    parser.add_argument("--theta-terms", type=int, default=8)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.panels, args.xmax, args.theta_terms)
    except (ValueError, OverflowError) as exc:
        parser.error(str(exc))
    content = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
