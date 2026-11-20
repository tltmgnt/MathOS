"""TECT-X numerical Weil-explicit-formula Gram-matrix investigation.

Uses zero-free-input Gaussian-cosine test functions h_jk(t)=
exp(-a*t*t)*cos(c_j*t)*cos(c_k*t), and the classical explicit formula:
 W(h) = h(i/2)+h(-i/2) - log(pi)/(2*pi)*hhat(0)
        + 1/(2*pi)*int_R h(t)*Re digamma(1/4+i*t/2) dt
        - 1/pi*sum_(n>=2) Lambda(n)/sqrt(n)*hhat(log n).
Fourier convention hhat(u)=int_R h(t)exp(-i*u*t)dt.

Finite quadratures and prime cutoffs are approximate and DO NOT certify
nonnegativity of Weil's form, which would imply RH on the complete test space.
The independently positive Gaussian L2 Gram is a DIFFERENT quadratic form.
"""
from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path

from mathos.research.riemann_arithmetic_spectral import von_mangoldt

PI = math.pi
DEFAULT_CENTERS = (0.0, 0.2, 0.5)


def digamma_real(t: float) -> float:
    """Numerical Re psi(1/4+i*t/2), via recurrence + Bernoulli expansion."""
    if not math.isfinite(t):
        raise ValueError("finite real argument required")
    z = complex(0.25, t/2)
    value = 0j
    for k in range(24):
        value -= 1/(z+k)
    z += 24
    w = 1/z
    value += (cmath.log(z) - w/2 - w**2/12 + w**4/120
              - w**6/252 + w**8/240 - 5*w**10/660)
    return value.real


def fourier_h(u: float, c: float, d: float, a: float) -> float:
    """Exact analytic Fourier transform of the even Gaussian-cosine product."""
    if not all(math.isfinite(v) for v in (u, c, d, a)) or a <= 0:
        raise ValueError("finite parameters with positive a required")
    return math.sqrt(PI/a)/4 * math.fsum(
        math.exp(-(u-e*c-f*d)**2/(4*a))
        for e in (-1, 1) for f in (-1, 1)
    )


def l2_entry(c: float, d: float, a: float) -> float:
    """Provably PSD comparison kernel, NOT Weil's form."""
    return math.sqrt(PI/a)/2 * (
        math.exp(-(c-d)**2/(4*a)) + math.exp(-(c+d)**2/(4*a))
    )


def _validate(centers: tuple[float, ...], a: float, max_t: float,
              panels: int, prime_bound: int) -> None:
    if not isinstance(centers, tuple) or not 1 <= len(centers) <= 6 or not all(
        isinstance(c, (int, float)) and math.isfinite(c) and 0 <= c <= 1.5
        for c in centers
    ):
        raise ValueError("centers: tuple of 1..6 finite reals in [0,1.5]")
    if not math.isfinite(a) or not 0.01 <= a <= 0.1:
        raise ValueError("Gaussian coefficient a must lie in [0.01,0.1]")
    if not math.isfinite(max_t) or not 30 <= max_t <= 80:
        raise ValueError("max_t must lie in [30,80]")
    if type(panels) is not int or not 2048 <= panels <= 32768 or panels % 2:
        raise ValueError("panels must be even in 2048..32768")
    if type(prime_bound) is not int or not 100 <= prime_bound <= 10000:
        raise ValueError("prime_bound must lie in 100..10000")


def weil_entry(c: float, d: float, a: float, max_t: float,
               panels: int, prime_bound: int) -> dict:
    """Compute separately labeled pole, archimedean and finite-prime terms."""
    delta = max_t/panels
    arch_sum = 0.0
    for i in range(panels + 1):
        t = i*delta
        factor = 1 if i in (0, panels) else (4 if i%2 else 2)
        arch_sum += (factor*math.exp(-a*t*t)*math.cos(c*t)*math.cos(d*t)
                     *digamma_real(t))
    arch = arch_sum*delta/(3*PI)  # 2-sided real integral: 1/(2pi)*2
    pole = 2*math.exp(a/4)*math.cosh(c/2)*math.cosh(d/2)
    logpi = -math.log(PI)*fourier_h(0, c, d, a)/(2*PI)
    prime_sum = math.fsum(
        von_mangoldt(n)/math.sqrt(n)*fourier_h(math.log(n), c, d, a)
        for n in range(2, prime_bound+1)
    )
    prime = -prime_sum/PI
    return {
        "pole": pole,
        "archimedean_approx": arch,
        "log_pi_term": logpi,
        "finite_prime_power_term": prime,
        "total_approx": pole+arch+logpi+prime,
    }


def symmetric_eigenvalues(matrix: list[list[float]]) -> list[float]:
    """Jacobi rotations for small real symmetric matrices; floating only."""
    n = len(matrix)
    if not 1 <= n <= 6 or any(len(row) != n for row in matrix):
        raise ValueError("1..6 square matrix required")
    if any(not math.isfinite(v) for row in matrix for v in row):
        raise ValueError("finite matrix entries required")
    if any(abs(matrix[i][j]-matrix[j][i]) > 1e-10
           for i in range(n) for j in range(n)):
        raise ValueError("symmetric matrix required")
    a = [row[:] for row in matrix]
    for _ in range(200*n*n):
        p,q = max(((i,j) for i in range(n) for j in range(i+1,n)),
                  key=lambda pair: abs(a[pair[0]][pair[1]]), default=(0,0))
        if p == q or abs(a[p][q]) < 1e-13:
            break
        t = (a[q][q]-a[p][p])/(2*a[p][q])
        tangent = (1 if t>=0 else -1)/(abs(t)+math.sqrt(1+t*t))
        cosv = 1/math.sqrt(1+tangent*tangent)
        sinv = tangent*cosv
        app,aqq,apq = a[p][p],a[q][q],a[p][q]
        a[p][p] = app-tangent*apq
        a[q][q] = aqq+tangent*apq
        a[p][q]=a[q][p]=0.0
        for k in range(n):
            if k == p or k == q:
                continue
            akp,akq=a[k][p],a[k][q]
            a[k][p]=a[p][k]=cosv*akp-sinv*akq
            a[k][q]=a[q][k]=sinv*akp+cosv*akq
    return sorted(a[i][i] for i in range(n))


def audit(centers: tuple[float, ...] = DEFAULT_CENTERS, a: float = 0.02,
          max_t: float = 45.0, panels: int = 4096,
          prime_bound: int = 512) -> dict:
    _validate(centers, a, max_t, panels, prime_bound)
    dimensions = len(centers)
    matrix = [[0.0]*dimensions for _ in range(dimensions)]
    l2 = [[l2_entry(c,d,a) for d in centers] for c in centers]
    components = []
    for i,c in enumerate(centers):
        for j in range(i, dimensions):
            item = weil_entry(c, centers[j], a, max_t, panels, prime_bound)
            matrix[i][j]=matrix[j][i]=item["total_approx"]
            components.append({"i":i, "j":j, **item})
    eigs = symmetric_eigenvalues(matrix)
    l2eigs = symmetric_eigenvalues(l2)
    if min(l2eigs) < -1e-8:
        raise AssertionError("the independent analytic L2 PSD kernel failed a numerical regression")
    return {
        "schema": "mathos_tectx_weil_gram/1",
        "status": "FINITE_UNCERTIFIED_WEIL_FORM_TEST_NOT_RH",
        "basis": {
            "spectral_test": "h_jk(t)=exp(-a*t^2)*cos(c_j*t)*cos(c_k*t)",
            "Fourier": "hhat(u)=integral_R h(t)*exp(-i*u*t) dt",
            "a":a, "centers": list(centers),
            "admissibility": "even entire Gaussian-Schwartz tests, with analytic continuation and rapid decay in horizontal strips",
        },
        "explicit_formula": {
            "pole": "h(i/2)+h(-i/2)",
            "log_pi": "-log(pi)*hhat(0)/(2*pi)",
            "archimedean": "integral_R h(t)*Re digamma(1/4+i*t/2)dt/(2*pi)",
            "prime_powers": "-sum_(n>=2) Lambda(n)*hhat(log n)/(pi*sqrt(n))",
            "zero_side": "sum_(nontrivial rho) h((rho-1/2)/i), with justified symmetric counting and multiplicity",
            "zero_locations_used_as_input": False,
        },
        "numerics": {
            "max_t":max_t, "Simpson_panels":panels,
            "max_prime_power_index":prime_bound,
            "digamma_method":"shifted recurrence and finite Bernoulli asymptotic",
            "all_tail_and_roundoff_errors_rigorously_enclosed": False,
            "can_certify_Weil_psd": False,
        },
        "finite_Weil_Gram": {
            "matrix": matrix, "entry_components": components,
            "approx_eigenvalues":eigs,
            "approx_min_eigenvalue":eigs[0],
            "numerically_nonnegative_with_tol_1e_8":eigs[0]>=-1e-8,
            "claim_of_global_psd":False,
        },
        "independent_positive_L2_comparison": {
            "matrix":l2,"approx_eigenvalues":l2eigs,
            "analytic_proof": "Gram of exp(-a*t*t/2)*cos(c_j*t) in L2(R,dt)",
            "is_the_Weil_form":False,
        },
        "conditional_Hilbert_space": {
            "GNS_quotient_completion": "If (and only if) the full Weil form is PSD on the specified admissible test space, quotient its null space and complete to obtain a Hilbert space",
            "global_positivity_proved":False,
            "self_adjoint_zeta_operator_constructed":False,
        },
        "missing_bridges": [
            "certified arithmetic-side quadrature and infinite-prime error bounds for each finite Gram",
            "positivity for all admissible test functions, not merely this finite basis",
            "a global positive Hilbert completion with specified dense domain and suitable operator",
            "noncircular spectral theorem accounting for every nontrivial zero and multiplicity",
        ],
        "assurance": {
            "riemann_hypothesis_proved":False,
            "Weil_criterion_fully_verified":False,
            "infinite_Weil_Hilbert_space_constructed":False,
            "new_mathematical_theorem_claimed":False,
            "independent_review_completed":False,
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a",type=float,default=0.02)
    parser.add_argument("--centers",type=str,default="0,0.2,0.5")
    parser.add_argument("--max-t",type=float,default=45.0)
    parser.add_argument("--panels",type=int,default=4096)
    parser.add_argument("--prime-bound",type=int,default=512)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        centers=tuple(float(x) for x in args.centers.split(","))
        result=audit(centers,args.a,args.max_t,args.panels,args.prime_bound)
    except (ValueError, OverflowError) as exc:
        parser.error(str(exc))
    payload=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
