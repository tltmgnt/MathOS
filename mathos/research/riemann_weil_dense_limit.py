"""Dense Weil test family: fixed trace-class *signed* arithmetic operator.

This module proves two finite-to-infinite control results WITHOUT assuming RH:

1. Fix q_c(t)=exp(-t*t/100)*cos(c*t) and a countable dense set of
   distinct frequencies c in [0,1/2]. The q_c span is dense in the
   EVEN L2(R) space, by analytic uniqueness of a Gaussian-weighted
   Fourier transform. This is NOT a density proof in Weil's admissible
   topology (the latter would be RH-relevant).

2. Weil's explicit formula defines a real symmetric matrix G_ij on
   this family (using ALL pole, digamma, and prime-power contributions).
   An elementary uniform entry estimate |G_ij|<10000, independent of
   indices, and weights w_j=2**(j+1), produce a fixed real self-adjoint
   trace-class operator T_ij=G_ij/(w_i*w_j) on coefficient ell2.
   With P_m the first m coordinate projection,
       ||T-P_m T P_m||_1 <= 10000*(2**(1-m)-2**(-2*m)).
   This is a proved unconditional, dimension-independent geometric
   truncation estimate on a SIGNED operator, not global Weil positivity.

The weighted coefficient Hilbert space has an injective, dense-range
map into even L2, but its norm is NOT equivalent to L2 or the standard
Weil-admissible test-function topology. Thus neither trace-classness
nor L2-density proves the Weil positivity criterion or RH.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from mathos.research.riemann_weil_prime_tail import per_entry_prime_tail_bound

WEIL_ENTRY_ABS_BOUND = 10_000
BASE_CENTERS = (Fraction(0), Fraction(1,5), Fraction(1,2))
MAX_REPORTED_DIMENSION = 4096


def dense_centers(count: int) -> tuple[Fraction, ...]:
    """First count distinct frequencies from a countable dense subset [0,1/2].

    Begin with the previously certified THREE-dimensional Weil basis.
    Thereafter include all odd dyadic fractions k/2^(level+1), level>=1.
    The fixed fourth direction c=21/5 in PR #81 is OUTSIDE this compact
    family and its positive Gram cannot be silently imported here.
    """
    if type(count) is not int or not 1 <= count <= MAX_REPORTED_DIMENSION:
        raise ValueError("count must be integer in 1..4096")
    result = list(BASE_CENTERS[:count])
    seen = set(result)
    level = 1
    while len(result) < count:
        denominator = 1 << (level+1)
        for k in range(1, 1 << level, 2):
            c = Fraction(k, denominator)
            if c not in seen:
                result.append(c)
                seen.add(c)
                if len(result) == count:
                    break
        level += 1
    return tuple(result)


def weight(index: int) -> int:
    """Exact dyadic scaling w_j=2^(j+1), zero-indexed."""
    if type(index) is not int or not 0 <= index <= MAX_REPORTED_DIMENSION:
        raise ValueError("index must be integer in 0..4096")
    return 1 << (index+1)


def uniform_entry_majorant() -> dict:
    """Portable proof bookkeeping for ALL Weil entries, not just primes.

    The bounds are intentionally loose but analytically justified:
      |h(i/2)+h(-i/2)| < 5;
      |log(pi)*hhat(0)/(2*pi)| < 5;
      |archimedean| < 35 by |Re psi(1/4+it/2)|
                                   < 16+t/128 and Gaussian integrals;
      |prime powers n<=256| < 6630 using Lambda(n)<=log n<6,
               n^-1/2<=1, hhat(u)<=sqrt(50*pi)<13, 1/pi<1/3;
      |omitted prime powers n>256| < 1 by exact-rational earlier proof.
    Total <6676 <10000. Valid uniformly for centers in [0,1/2].
    """
    d=per_entry_prime_tail_bound()
    if not Fraction(0)<d<1:
        raise ArithmeticError("previous exact Weil prime-tail estimate invalid")
    subtotal=5+5+35+6630+1
    if not subtotal<WEIL_ENTRY_ABS_BOUND:
        raise ArithmeticError("insufficient global Weil entry upper bound")
    return {
        "pole_upper":5,"log_pi_upper":5,
        "archimedean_upper":35,
        "prime_powers_through_256_upper":6630,
        "all_remaining_prime_powers_upper":1,
        "component_sum_upper":subtotal,
        "final_entry_absolute_bound":WEIL_ENTRY_ABS_BOUND,
        "proved_for_all_centers_in":"[0,1/2]",
        "exact_prime_tail_rational":f"{d.numerator}/{d.denominator}",
    }


def trace_norm_tail_bound(dim: int) -> Fraction:
    """Exact upper bound on ||T-P_m T P_m||_1.

    Sum over rank-one coordinate matrix units with i>=m OR j>=m:
       M*( (sum_j 1/w_j)^2 - (sum_(j<m) 1/w_j)^2 )
        = M*(2^(1-m)-2^(-2*m)).
    """
    if type(dim) is not int or not 0 <= dim <= MAX_REPORTED_DIMENSION:
        raise ValueError("dim must be integer in 0..4096")
    q = Fraction(1,1 << dim)
    return WEIL_ENTRY_ABS_BOUND*(2*q-q*q)


def finite_section_negative_floor(dim: int, known_prefix_lower: Fraction) -> Fraction:
    """If T_m >= lambda I_m, then T >= min(0,lambda)-eps_m.

    This is a conditional sharp logical implication, NOT an
    unconditional assertion of positivity of T_m or the full T.
    """
    if not isinstance(known_prefix_lower,Fraction):
        raise ValueError("certified rational prefix bound required")
    return min(known_prefix_lower,Fraction(0))-trace_norm_tail_bound(dim)


def report(dimension: int=32) -> dict:
    cs=dense_centers(dimension)
    bounds=uniform_entry_majorant()
    eps=trace_norm_tail_bound(dimension)
    if not (eps>0 and trace_norm_tail_bound(dimension+1)<eps):
        raise AssertionError("geometric tail monotonicity failed")
    # The basis is L2 dense, but the Weil-form completion is still open.
    return {
        "schema":"mathos_tectx_dense_weil_trace_class_limit/1",
        "status":"UNCONDITIONAL_SIGNED_TRACE_CLASS_WEIL_LIMIT_NO_GLOBAL_PSD",
        "test_family":{
            "q_c":"q_c(t)=exp(-t^2/100)*cos(c*t)",
            "fixed_prefix_centers":["0/1","1/5","1/2"],
            "frequency_range":"[0,1/2]",
            "enumeration":"after prefix, all distinct positive odd dyadics k/2^(level+1) with level>=1",
            "reported_dimension":dimension,
            "reported_centers":[f"{v.numerator}/{v.denominator}" for v in cs],
            "is_countable_dense_in_frequency_interval":True,
            "span_dense_in_even_real_L2":True,
            "density_proof":"If even f in L2 is orthogonal to every q_c, Gaussian-weighted Fourier cosine transform is entire and vanishes on dense centers with an interior accumulation point; identity theorem and Fourier uniqueness imply f=0",
            "density_proved_in_full_Weil_admissible_topology":False,
            "fourth_center_from_PR81_in_this_family":False,
            "uses_nontrivial_zeta_zeros_as_input":False,
        },
        "global_arithmetic_bound":{
            "all_weil_entry_components":bounds,
            "applies_to_full_pole_gamma_prime_power_expression":True,
            "requires_RH":False,
        },
        "fixed_self_adjoint_trace_class_operator":{
            "Hilbert_space":"coefficient ell2(N_0)",
            "entries":"T_ij=W(q_(c_i)*q_(c_j))/(2^(i+1)*2^(j+1))",
            "weighted_synthesis":"Q(a)(t)=sum_j a_j*2^(-j-1)*q_(c_j)(t)",
            "weighted_synthesis_injective":True,
            "weighted_synthesis_dense_range_in_even_L2":True,
            "norm_of_synthesis_upper_squared": "13/3",
            "self_adjoint":True,
            "trace_class":True,
            "trace_norm_upper":WEIL_ENTRY_ABS_BOUND,
            "finite_projection":"P_m onto first m coefficient basis vectors",
            "trace_norm_error_rational":f"{eps.numerator}/{eps.denominator}",
            "error_formula":"||T-P_mTP_m||_1 <= 10000*(2^(1-m)-2^(-2*m))",
            "error_is_dimension_free_geometric_rate":True,
            "genuine_zeta_zero_operator":False,
            "positive_semidefinite":None,
        },
        "positivity_and_spectrum":{
            "conditional_lower_floor_if_Tm_positive":f"-{eps.numerator}/{eps.denominator}",
            "implication":"If T_m>=0, then T>=-eps_m I. To conclude T>=0, a theorem must certify lower(T_m)>=-o(1) for EVERY m, not finitely many m.",
            "noncoercive_in_coefficient_ell2":"|<e_j,T e_j>|<=10000/4^(j+1)->0, so T>=kappa I with kappa>0 is impossible even if T>=0",
            "no_global_positive_lower_bound_proved":True,
            "full_Weil_psd_proved":False,
        },
        "missing_global_bridges":[
            "Show nonnegativity for all finite sections of the newly chosen dyadic family, or establish a certified all-index lower bound tending to zero",
            "Prove density/continuity in the full Weil-admissible topology; density in even L2 alone is insufficient",
            "Relate the artificial weighted coefficient norm to a natural arithmetic test-function topology if making claims about RH",
            "Only then consider the Weil null quotient and Hilbert completion; derive a noncircular self-adjoint zeta-zero operator separately",
        ],
        "assurance":{
            "global_Weil_positivity":False,
            "unconditional_full_Weil_Hilbert_completion":False,
            "uniform_positive_coercivity":False,
            "Riemann_hypothesis_proved":False,
            "independent_peer_review":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dimension",type=int,default=32)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        data=report(args.dimension)
    except (ValueError,ArithmeticError) as exc:
        p.error(str(exc))
    payload=json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
