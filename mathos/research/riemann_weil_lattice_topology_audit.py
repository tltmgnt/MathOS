"""Topological obstruction and exact fifth Weil prime-window arithmetic.

For phi(8(x-3j/4)), the *ordinary L2* Gram is exactly alpha*I
for every dimension, alpha in (1/18,1/4). However all these
functions vanish on the open interval (1/8,5/8); their span is NOT
dense in L2(R) or C_c^infinity(R). A growing number of positive finite
Weil Grams on this lattice cannot prove the RH-equivalent Weil
positivity condition on the full admissible test domain.

The genuine fifth direction at 3 has cross-convolution support
[11/4,13/4]. Its new prime-power inputs are precisely
16,17,19,23,25. Exact rational atanh log bounds prove this and
an explicit interval inside the bump convolution gives
h_{3}(log 19)>1/72, yielding a strictly negative prime-19
Weil arithmetic contribution below -49/6000.

This does NOT compute the complete fifth entry, its archimedean
part, or a fifth-direction PSD/Schur certificate. The positive
four-dimensional result from PR #89 remains separately scoped.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from math import isqrt
import hashlib
import json
from pathlib import Path

WIDTH=Fraction(1,8)
STEP=Fraction(3,4)
FIFTH_INDEX=4
WINDOW_LEFT=Fraction(11,4)
WINDOW_RIGHT=Fraction(13,4)
FIFTH_PRIME_POWERS=(16,17,19,23,25)


def rational_text(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def atanh_positive_bounds(t: Fraction, terms: int=16) -> tuple[Fraction,Fraction]:
    """Outward analytic rational atanh bounds for 0<=t<=1/3."""
    if not isinstance(t,Fraction) or not Fraction(0)<=t<=Fraction(1,3):
        raise ValueError("requires rational t in [0,1/3]")
    if type(terms) is not int or not 1<=terms<=64:
        raise ValueError("terms must be integer 1..64")
    partial=sum((Fraction(2)*t**(2*j+1)/(2*j+1)
                 for j in range(terms)),Fraction(0))
    remainder=Fraction(2)*t**(2*terms+1)/(
        (2*terms+1)*(1-t*t))
    return partial,partial+remainder


def rational_log_integer(n: int, terms: int=16) -> tuple[Fraction,Fraction]:
    """Rigorous all-Fraction ln(n), dyadic range reduction, no libm."""
    if type(n) is not int or n<1:
        raise ValueError("n must be a positive integer")
    if type(terms) is not int or not 1<=terms<=64:
        raise ValueError("terms must be integer 1..64")
    if n==1:
        return Fraction(0),Fraction(0)
    k=n.bit_length()-1
    y=Fraction(n,2**k)
    t=(y-1)/(y+1)
    a,b=atanh_positive_bounds(Fraction(1,3),terms)
    c,d=atanh_positive_bounds(t,terms)
    return k*a+c,k*b+d


def prime_power_base(n: int) -> int | None:
    """Return unique prime base p when n=p^k, else None."""
    if type(n) is not int or n<2:
        return None
    divisor=None
    value=n
    for p in range(2,isqrt(value)+1):
        if value%p==0:
            divisor=p
            while value%p==0:
                value//=p
            return p if value==1 else None
    return n


def translated_support(index: int) -> tuple[Fraction,Fraction]:
    if type(index) is not int or index<0:
        raise ValueError("nonnegative integer index required")
    c=index*STEP
    return c-WIDTH,c+WIDTH


def convolution_support(i: int,j: int) -> tuple[Fraction,Fraction]:
    a,b=translated_support(i)
    c,d=translated_support(j)
    return a-d,b-c


def prime_inventory(i: int,j: int,terms: int=16) -> dict:
    """Exact rational bounds for every possible n with Λ(n) !=0."""
    left,right=convolution_support(i,j)
    maximum=max(abs(left),abs(right))
    # Use integer cap 3^ceil(maximum), since e<3.
    ce=-(-maximum.numerator//maximum.denominator)
    cap=3**ce
    if cap>100000:
        raise ValueError("arithmetic window too large for bounded audit")
    possible=[]
    for n in range(2,cap+1):
        p=prime_power_base(n)
        if p is None:
            continue
        lo,hi=rational_log_integer(n,terms)
        # rigorous disjointness; if log interval touches boundary, fail
        if hi < abs(left) and hi < abs(right) and left*right>=0:
            # optimized exclusion below; keep generic exact logic instead
            pass
        at_positive=(left<hi and lo<right)
        at_negative=(left< -lo and -hi <right)
        if at_positive or at_negative:
            # Include ONLY if entire log bracket lies strictly inside
            # the support; otherwise fail rather than assume inclusion.
            positive_inside=(left<lo and hi<right)
            negative_inside=(left<-hi and -lo<right)
            if not (positive_inside or negative_inside):
                raise ArithmeticError("prime logarithm intersects a support boundary")
            possible.append({"integer":n,"von_mangoldt_base":p,
                             "log_lower":rational_text(lo),
                             "log_upper":rational_text(hi)})
    return {"support":[rational_text(left),rational_text(right)],
            "candidate_prime_powers":possible,
            "uses_exact_fraction_log_bounds":True}


def fifth_prime19_lower() -> dict:
    """h_{3}(log19)>1/72 by an explicit positive rational t interval.

    log19 in (147/50,59/20). Thus delta=3-log19 in (1/20,3/50).
    On t in [-1/32,0], both |8t|<1/2 and
    |8(t+delta)|<1/2, because t+delta in
    [1/20-1/32, 3/50] subset (-1/16,1/16).
    phi(u)>2/3 for |u|<1/2 via e^(1/3)<3/2.
    h(log19)>(1/32)*(2/3)^2=1/72.
    log19>147/50 and sqrt19<5, so
    -(log19)/sqrt19*h(log19)<-49/6000.
    """
    lo,hi=rational_log_integer(19)
    if not (Fraction(147,50)<lo<hi<Fraction(59,20)):
        raise ArithmeticError("insufficient strict log19 enclosure")
    delta_lo=3-hi
    delta_hi=3-lo
    if not (Fraction(1,20)<delta_lo<delta_hi<Fraction(3,50)):
        raise ArithmeticError("convolution plateau outside intended window")
    t_left=-Fraction(1,32)
    if not (-Fraction(1,16)<t_left+delta_lo
            and delta_hi<Fraction(1,16)):
        raise ArithmeticError("not both bumps >2/3 on plateau")
    bound=Fraction(147,50)/5/Fraction(72)
    if bound!=Fraction(49,6000):
        raise ArithmeticError("incorrect exact rational prime-19 bound")
    return {
        "log19_bracket":[rational_text(lo),rational_text(hi)],
        "integration_subinterval":["-1/32","0/1"],
        "convolution_at_log19_strictly_greater":"1/72",
        "prime19_term_strictly_less":rational_text(-bound),
        "prime19_contribution_nonzero":True,
        "prime19_von_mangoldt":"log(19)",
        "normalization":"-log(19)/sqrt(19) * h_3(log19)",
    }


def report() -> dict:
    fifth=prime_inventory(4,0)
    actual=[v["integer"] for v in fifth["candidate_prime_powers"]]
    if actual!=list(FIFTH_PRIME_POWERS):
        raise ArithmeticError(f"unexpected fifth prime-power inventory {actual}")
    l2_lower=Fraction(1,18)
    l2_upper=Fraction(1,4)
    return {
        "schema":"mathos_tectx_weil_lattice_topology_fifth_prime_audit/1",
        "status":"FIFTH_ARITHMETIC_WINDOW_IDENTIFIED_GLOBAL_DENSITY_OBSTRUCTION",
        "lattice":{
            "functions":"f_j(x)=phi(8*(x-3j/4)), j>=0",
            "phi":"exp(1-1/(1-u^2)) for |u|<1 and 0 otherwise",
            "lattice_step":"3/4",
            "support_halfwidth":"1/8",
            "open_gap_between_first_two_supports":["1/8","5/8"],
            "every_f_j_identically_zero_on_gap":True,
            "span_dense_in_L2_R":False,
            "span_dense_in_LF_Cc_infinity_R":False,
            "support_gap_nondensity_proof":"Every span element vanishes on (1/8,5/8); take any nonzero smooth bump supported there. L2 and point evaluation are continuous functionals on the respective relevant spaces.",
            "ordinary_L2_reference_Gram":"alpha * I_m for EVERY m, no off-diagonal overlaps",
            "alpha_definition":"integral_-1/8^1/8 phi(8*x)^2 dx",
            "alpha_strict_lower":rational_text(l2_lower),
            "alpha_strict_upper":rational_text(l2_upper),
            "alpha_proof":"On |x|<1/16, phi(8x)>exp(-1/3)>2/3, so alpha>(1/8)*(4/9)=1/18. Since 0<=phi<=1 and support length is 1/4, alpha<1/4.",
            "all_m_coefficient_to_L2_condition_number":1,
            "reference_norm_conditioning_does_not_prove_Weil_positivity":True,
        },
        "fifth_direction":{
            "index":4,
            "center":"3/1",
            "support":["23/8","25/8"],
            "cross_with_zero":fifth,
            "actual_new_prime_powers":list(FIFTH_PRIME_POWERS),
            "new_prime19_proven_lower":fifth_prime19_lower(),
            "all_pole_arch_prime_terms_fully_enclosed":False,
            "fifth_Weil_Gram_eigenvalues_certified":False,
            "fifth_Schur_complement_certified":False,
        },
        "open_proof_obligations":[
            "Complete certified fifth cross-entry pole, all prime powers and gamma/archimedean integration",
            "Prove or disprove a strictly positive fifth Schur complement using the full actual arithmetic Weil form",
            "Construct a genuinely LF-dense compact test core, not a fixed-width lattice with permanent gaps",
            "Prove a universal Weil positivity inequality on that full dense core; equivalent to RH",
        ],
        "assurance":{
            "new_fifth_positive_Weil_Gram":False,
            "lattice_dense_in_full_Weil_test_domain":False,
            "unconditional_global_Weil_PSD":False,
            "Riemann_hypothesis_proved":False,
            "full_positive_Weil_Hilbert_space":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result=report()
    payload=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
