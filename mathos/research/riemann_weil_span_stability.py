"""TECT-X: dimension-stable Weil prime-tail estimate and coercivity no-go.

Builds on a validated fixed 3x3 Weil Gram (PR #78) without mistaking it
for positivity on the whole admissible test-function space.

Two analytic results, with precise norms:
(1) For ANY finite number of Gaussian-cosine centers in [0,1/2],
    omitted prime powers perturb the quadratic form by at most
    delta*||v||_1^2, with exact rational delta independent of dimension.
    This is not a dimension-free ||v||_2 or L2 operator bound.
(2) NO positive uniform lower bound G_m >= kappa I_m can hold for
    ALL selections of centers: duplicates give rank deficiency, and
    distinct centers clustering at zero yield vanishing Rayleigh quotients.

In the already certified 3D span, G > 10^-6 I implies a conditional-on-
PR78 basis-invariant bound G > (1/50,000,000) L2_Gram, as L2_Gram < 45 I.
Nothing here proves global Weil positivity or constructs the Weil Hilbert
space. The abstract quotient-completion is conditional on full PSD.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from mathos.research.riemann_weil_prime_tail import (
    CENTER_UPPER, per_entry_prime_tail_bound,
)

THREE_SPAN_EUCLIDEAN_GAP = Fraction(1, 1_000_000)
L2_GAUSSIAN_ENTRY_UPPER = Fraction(15)
L2_THREE_SPAN_NORM_UPPER = Fraction(45)
THREE_SPAN_L2_GAP = Fraction(1, 50_000_000)


def fraction_string(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _check_centers(centers: tuple[Fraction, ...]) -> None:
    if not isinstance(centers, tuple) or not 1 <= len(centers) <= 500:
        raise ValueError("require a tuple of 1..500 centers")
    if any(not isinstance(c, Fraction) or not Fraction(0) <= c <= CENTER_UPPER
           for c in centers):
        raise ValueError("all centers must be Fractions in [0,1/2]")


def dimension_free_prime_tail(centers: tuple[Fraction, ...],
                              coefficients: tuple[Fraction, ...]) -> Fraction:
    """Uniform *L1 coefficient* error on the actual Weil prime-power tail.

    Bound: |P_full((sum v_j q_j)^2)-P_256((sum v_j q_j)^2)|
      <= delta*(sum |v_j|)^2, with delta exact rational.
    Valid for every finite dimension, regardless of repeated centers.
    """
    _check_centers(centers)
    if not isinstance(coefficients, tuple) or len(coefficients) != len(centers):
        raise ValueError("one coefficient per center required")
    if any(not isinstance(v, Fraction) for v in coefficients):
        raise ValueError("coefficients must be exact Fractions")
    return per_entry_prime_tail_bound() * sum((abs(v) for v in coefficients),
                                               Fraction(0)) ** 2


def clustered_centers(n: int) -> tuple[Fraction, ...]:
    """Distinct centers 1/(j+2) -> 0; all in (0,1/2]."""
    if type(n) is not int or not 2 <= n <= 500:
        raise ValueError("n must be integer in 2..500")
    return tuple(Fraction(1, j+2) for j in range(n))


def adjacent_gap(j: int) -> Fraction:
    """Exact gap |1/(j+2)-1/(j+3)| -> 0 as j -> infinity."""
    if type(j) is not int or j < 0:
        raise ValueError("j must be nonnegative integer")
    return Fraction(1, (j+2)*(j+3))


def conditional_completion_statement() -> dict:
    """Conditional algebraic theorem; does NOT assert the hypothesis."""
    return {
        "hypothesis": "Weil Hermitian form W is positive semidefinite for EVERY pair in the full admissible test-function vector space V",
        "null_space": "N={f in V: W(f,f)=0}; if W is PSD, Cauchy-Schwarz implies W(f,g)=0 for all g when f in N",
        "quotient": "V/N with <[f],[g]>=W(f,g) is an inner-product space",
        "completion": "Hilbert-space completion of V/N exists uniquely up to isometry",
        "hypothesis_proved": False,
        "completion_constructed_unconditionally": False,
        "relation_to_RH": "global Weil positivity is an RH-equivalent obligation, not a consequence of finite Gram certificates",
    }


def report(centers: tuple[Fraction, ...] = (
    Fraction(0), Fraction(1,5), Fraction(1,2)),
    coefficients: tuple[Fraction, ...] = (
    Fraction(1),Fraction(-2),Fraction(3))) -> dict:
    _check_centers(centers)
    tail=dimension_free_prime_tail(centers,coefficients)
    if not (THREE_SPAN_L2_GAP*L2_THREE_SPAN_NORM_UPPER
            < THREE_SPAN_EUCLIDEAN_GAP):
        raise ArithmeticError("3D relative coercivity inference invalid")
    if not (THREE_SPAN_EUCLIDEAN_GAP
            -THREE_SPAN_L2_GAP*L2_THREE_SPAN_NORM_UPPER > 0):
        raise ArithmeticError("loss of strict 3D margin")
    n= len(centers)
    return {
        "schema":"mathos_tectx_weil_growing_span_stability/1",
        "status":"DIMENSION_FREE_L1_TAIL_AND_NO_UNIFORM_EUCLIDEAN_COERCIVITY",
        "test_family":{
            "basis":"q_c(t)=exp(-t*t/100)*cos(c*t)",
            "parameter_interval":"c in [0,1/2]",
            "number_of_centers":n,
            "centers":[fraction_string(c) for c in centers],
            "coefficients":[fraction_string(v) for v in coefficients],
            "nontrivial_zero_locations_used_as_input":False,
        },
        "dimension_free_prime_tail":{
            "bound":fraction_string(tail),
            "constant":fraction_string(per_entry_prime_tail_bound()),
            "norm":"coefficient l1, NOT coefficient l2 and NOT L2 of functions",
            "assertion":"For any m and real coefficients v, |P(q_v^2)-P_256(q_v^2)| <= delta*(sum_j |v_j|)^2",
            "proof":"each of the m^2 Weil-prime tail entries is <=delta, so sum_jk |v_j||v_k| delta=delta||v||_1^2",
            "dimension_independent_constant":True,
            "full_Weil_form_error_controlled":False,
        },
        "no_go_for_uniform_coefficient_gap":{
            "claim_refuted":"exists kappa>0 with G_m >=kappa I_m for EVERY finite center tuple (even all tuples with distinct centers)",
            "exact_duplicate_example":"two identical centers c,c give Gram [[w,w],[w,w]] with Rayleigh zero on (1,-1)/sqrt(2), regardless of w",
            "distinct_cluster_example":"c_j=1/(j+2) -> 0, all distinct; |c_j-c_(j+1)|=1/((j+2)(j+3))",
            "continuity_argument":"q_c-q_d tends to zero in Gaussian-Schwartz test-function topology as c-d tends to zero; Weil distribution is continuous, so W((q_c-q_d)^2)->0; normalized coefficient vector (1,-1)/sqrt(2) always has l2 norm 1",
            "absence_of_uniform_kappa_proved":True,
            "rules_out_global_Weil_positivity":False,
            "rules_out_L2_normalized_or_Sobolev_normalized_coercivity":False,
        },
        "previous_three_dimensional_relative_bound":{
            "centers":["0/1","1/5","1/2"],
            "assumed_prior_certified_bound":"G > (1/1000000) I_3 from PR #78",
            "L2_comparison_Gram_operator_norm_upper":"45",
            "proof":"L_ii = integral_R exp(-t²/50)cos(c_i t)^2 dt < sqrt(pi/(1/50)) < 15; L PSD implies L<=trace(L) I_3 <45 I_3; then G-(1/50000000)L >=(1/1000000-45/50000000)I_3>0",
            "conclusion":"W(q_v²) > (1/50000000)*||q_v||_(L2(R))² for every nonzero v in this exact 3D span",
            "relative_constant":fraction_string(THREE_SPAN_L2_GAP),
            "relative_margin_after_trace_bound":fraction_string(
                THREE_SPAN_EUCLIDEAN_GAP
                -THREE_SPAN_L2_GAP*L2_THREE_SPAN_NORM_UPPER),
            "basis_invariant_within_fixed_three_span":True,
            "all_dimensions":False,
        },
        "conditional_Hilbert_space":conditional_completion_statement(),
        "remaining_bridges":[
            "Find and rigorously justify a natural complete test-function topology and norm that control Weil positivity as the support and dimension grow",
            "Prove full Weil-form PSD for every admissible test, rather than all finite samples in a restricted basis",
            "Derive a Hilbert-space completion and the fixed self-adjoint arithmetic generator without assuming RH-equivalent positivity",
            "Prove noncircular spectral correspondence with all nontrivial zeros, multiplicities and off-critical-line alternatives",
        ],
        "assurance":{
            "global_Weil_positivity":False,
            "global_Weil_Hilbert_space":False,
            "uniform_coercivity_in_natural_function_norm":False,
            "riemann_hypothesis_proved":False,
            "independent_mathematical_review":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--centers",default="0,1/5,1/2")
    p.add_argument("--coefficients",default="1,-2,3")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        centers=tuple(Fraction(x) for x in args.centers.split(","))
        coeffs=tuple(Fraction(x) for x in args.coefficients.split(","))
        result=report(centers,coeffs)
    except (ValueError,ZeroDivisionError) as exc:
        p.error(str(exc))
    payload=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
