"""Certified actual fourth Weil Gaussian direction via interval block Schur.

Extend the previously certified c=(0,1/5,1/2) family by an actual distinct
c_4=21/5 test q_4(t)=exp(-t^2/100) cos(21*t/5). Compute ALL four new Weil
cross entries from poles, archimedean digamma, and prime powers through 65536;
bound the omitted prime powers with an independently derived rational majorant
valid for |c_i|+|c_j|<=42/5. The archimedean Simpson and Binet digamma
errors are rigorously enclosed with center-dependent rational derivative
bounds. Check the new Schur complement for G-kappa L, relative to L2.

This certifies a fixed 4D family ONLY, subject to the analytic assumptions
and correctness of interval implementation. It is NOT RH or global Weil PSD.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from math import comb, isqrt
from pathlib import Path

from mpmath import iv

from mathos.research.riemann_weil_certified_gram3 import (
    CENTERS, SHIFT, T, _digamma_core_at, _fourier_h, _gram_intervals,
)
from mathos.research.riemann_weil_certified_scalar import (
    _outward_decimal, _rational_bound,
)
from mathos.research.riemann_weil_generalized_schur import (
    _ldl_intervals, verified_schur,
)

NEW_CENTER = Fraction(21, 5)
FOUR_CENTERS = CENTERS + (NEW_CENTER,)
A = Fraction(1, 50)
PRIME_CUTOFF = 65536
PRIME_LOG_FLOOR = 10
MAX_FOURIER_SHIFT = 2 * NEW_CENTER
EXP_POWER = 128
VALID_PANELS = (65536,)
LOWER = Fraction(1,1_000_000_000)  # Reduced certified 4D generalized gap.
PREVIOUS_THREE_DIMENSIONAL_LOWER = Fraction(1,50_000_000)


def _frac(x: Fraction) -> object:
    return iv.mpf(x.numerator)/x.denominator


def _fraction_string(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def _f4_rational(shift: Fraction) -> Fraction:
    """Center-specific global bound on |(Gaussian*cos*cos*Re digamma)''''|."""
    if not isinstance(shift, Fraction) or shift < 0 or shift > MAX_FOURIER_SHIFT:
        raise ValueError("invalid cosine derivative shift")
    v = 2*A*T
    gauss = (
        Fraction(1), v, v*v+2*A,
        v**3+6*A*v,
        v**4+12*A*v*v+12*A*A,
    )
    h = [
        sum(Fraction(comb(k,j))*gauss[j]*shift**(k-j)
            for j in range(k+1))
        for k in range(5)
    ]
    digamma_derivatives = (16, 10, 36, 208, 1632)
    return sum(Fraction(comb(4,j))*h[j]*digamma_derivatives[4-j]
               for j in range(5))


def _new_prime_tail() -> Fraction:
    """Rigorous prime-power tail with all Fourier shifts |epsilon*c+eta*d|<=8.4.

    N=65536>3^10>e^10 and on u>=10 the Gaussian majorant decreases.
    Complete the square with C=42/5. The exponential prefactor is
    <5*256=1280 using pi>3, exp(C/2+A/4)<exp(5)<3^5<256.
    exp(-X)<=(1+X/128)^(-128) follows from exp(x)>= (1+x/128)^128.
    """
    if not (3**PRIME_LOG_FLOOR < PRIME_CUTOFF):
        raise AssertionError("prime cutoff doesn't exceed proved log floor")
    beta=(Fraction(PRIME_LOG_FLOOR)-MAX_FOURIER_SHIFT-A)/(2*A)
    X=(Fraction(PRIME_LOG_FLOOR)-MAX_FOURIER_SHIFT-A)**2/(4*A)
    if beta <= 0:
        raise ArithmeticError("prime-tail majorant not decreasing")
    return 1280*(Fraction(PRIME_LOG_FLOOR)/beta+1/(beta*beta))/(1+X/EXP_POWER)**EXP_POWER


def _prime_powers_up_to(bound: int) -> list[tuple[int,int]]:
    """All prime powers p^k<=bound, each exactly once, with its base prime."""
    if type(bound) is not int or not 2<=bound<=PRIME_CUTOFF:
        raise ValueError("bound must lie in 2..65536")
    sieve=bytearray(b"\x01")*(bound+1)
    sieve[0:2]=b"\x00\x00"
    for p in range(2,isqrt(bound)+1):
        if sieve[p]:
            sieve[p*p:bound+1:p]=b"\x00"*((bound-p*p)//p+1)
    result=[]
    for p in range(2,bound+1):
        if sieve[p]:
            n=p
            while n<=bound:
                result.append((n,p))
                n*=p
    result.sort()
    return result


def _error_budget(shift: Fraction, panels: int) -> dict[str,object]:
    a=_frac(A)
    r=iv.mpf(SHIFT)+iv.mpf(1)/4
    sim=iv.mpf(T)/180*(iv.mpf(T)/panels)**4*_frac(_f4_rational(shift))/iv.pi
    dig=iv.mpf(T)/(iv.pi*252*r**6)
    C=(iv.log(SHIFT+1)+4+iv.log(4*SHIFT)
       +iv.mpf(1)/(2*SHIFT)+iv.mpf(1)/(12*SHIFT*SHIFT))
    tail=iv.exp(-a*T*T)/iv.pi*(C/(2*a*T)+iv.mpf(1)/(4*a*SHIFT))
    delta=_new_prime_tail()
    prime=_frac(delta)
    return {
        "simpson":sim,"digamma":dig,
        "archimedean_infinite_tail":tail,
        "prime_power_infinite_tail":prime,
        "total":sim+dig+tail+prime,
    }


def _new_weil_row(panels: int) -> tuple[list[object],list[dict]]:
    """Exactly four independent arithmetic entries G_(i,3), i=0..3."""
    cs=[_frac(c) for c in FOUR_CENTERS]
    a=_frac(A)
    accumulated=[iv.mpf(0) for _ in range(4)]
    for k in range(panels+1):
        t=iv.mpf(T*k)/panels
        base=iv.exp(-a*t*t)*_digamma_core_at(t)*iv.cos(cs[3]*t)
        weight=1 if k in (0,panels) else (4 if k%2 else 2)
        for j in range(4):
            accumulated[j]+=weight*base*iv.cos(cs[j]*t)
    scale=iv.mpf(T)/(panels*3*iv.pi)
    accumulated=[x*scale for x in accumulated]

    sumprime=[iv.mpf(0) for _ in range(4)]
    for n,p in _prime_powers_up_to(PRIME_CUTOFF):
        u=iv.log(n)
        factor=iv.log(p)*iv.exp(-u/2)
        for j in range(4):
            sumprime[j]+=factor*_fourier_h(u,cs[j],cs[3])
    rows=[]
    errors=[]
    for j,c in enumerate(cs):
        pole=2*iv.exp(a/4)*(
            (iv.exp(c/2)+iv.exp(-c/2))/2)*(
            (iv.exp(cs[3]/2)+iv.exp(-cs[3]/2))/2)
        logpi=-iv.log(iv.pi)*_fourier_h(iv.mpf(0),c,cs[3])/(2*iv.pi)
        prime=-sumprime[j]/iv.pi
        parts=_error_budget(FOUR_CENTERS[j]+NEW_CENTER,panels)
        x=pole+logpi+prime+accumulated[j]+iv.mpf([-1,1])*parts["total"]
        rows.append(x)
        errors.append(parts)
    return rows,errors


def _l2_entry(c: Fraction,d: Fraction) -> object:
    a=_frac(A)
    c,d=_frac(c),_frac(d)
    return (iv.sqrt(iv.pi/a)/2 *
            (iv.exp(-(c-d)**2/(4*a))+iv.exp(-(c+d)**2/(4*a))))


def _scalar_schur_interval(M: list[list[object]]) -> object:
    """Enclose the scalar Schur of a verified-positive leading 3x3 block.

    Unlike verified_schur(), this returns negative values too; use to
    rigorously REJECT carrying an old coercivity constant forward.
    """
    if len(M)!=4 or any(len(row)!=4 for row in M):
        raise ValueError("expected a 4x4 interval matrix")
    A=[row[:3] for row in M[:3]]
    low,pivots=_ldl_intervals(A)
    y=[iv.mpf(0) for _ in range(3)]
    for i in range(3):
        v=M[i][3]
        for k in range(i):
            v-=low[i][k]*y[k]
        y[i]=v
    value=M[3][3]
    for i in range(3):
        value-=y[i]*y[i]/pivots[i]
    return value


def audit(panels: int=65536) -> dict:
    if type(panels) is not int or panels not in VALID_PANELS:
        raise ValueError("panels must be 65536")
    iv.dps=60
    old,_=_gram_intervals(panels)
    new,errors=_new_weil_row(panels)
    G=[[old[i][j] if i<3 and j<3
        else new[i] if j==3
        else new[j]
        for j in range(4)] for i in range(4)]
    # The previous triple is *unchanged*; every new cross term is computed.
    L=[[_l2_entry(c,d) for d in FOUR_CENTERS] for c in FOUR_CENTERS]
    _,l2_pivots=_ldl_intervals(L)
    M=[[G[i][j]-_frac(LOWER)*L[i][j] for j in range(4)]
       for i in range(4)]
    check=verified_schur(M,3)
    _,pivots=_ldl_intervals(M)
    # The old 3D lower constant is NOT preserved; certify the negative Schur.
    old_M=[[G[i][j]-_frac(PREVIOUS_THREE_DIMENSIONAL_LOWER)*L[i][j]
             for j in range(4)] for i in range(4)]
    old_schur=_scalar_schur_interval(old_M)
    if _rational_bound(old_schur,True)>=0:
        raise ArithmeticError("the old 3D lower constant was not refuted by a negative fourth Schur interval")
    if not all(_rational_bound(v,False)>0 for v in pivots):
        raise ArithmeticError("full generalized Weil matrix is not certified positive")
    return {
        "schema":"mathos_tectx_weil_certified_fourth_direction/1",
        "status":"FIXED_4D_ACTUAL_WEIL_GENERALIZED_SCHUR_CERTIFIED_GLOBAL_OPEN",
        "basis":{
            "a":"1/50",
            "centers":[_fraction_string(c) for c in FOUR_CENTERS],
            "new_center":_fraction_string(NEW_CENTER),
            "all_new_arithmetic_cross_entries_computed":True,
            "nontrivial_zero_locations_used_as_input":False,
        },
        "analytic_certification":{
            "prime_power_cutoff":PRIME_CUTOFF,
            "new_prime_power_tail_bound_exact":_fraction_string(_new_prime_tail()),
            "prime_power_log_floor":PRIME_LOG_FLOOR,
            "max_Fourier_shift":_fraction_string(MAX_FOURIER_SHIFT),
            "panels":panels,
            "fourth_derivative_envelopes_exact":[
                _fraction_string(_f4_rational(c+NEW_CENTER)) for c in FOUR_CENTERS
            ],
            "new_entry_errors":[
                {key:_outward_decimal(value,10**18)
                 for key,value in parts.items()} for parts in errors
            ],
            "method":"validated Simpson derivative bounds, shifted Binet digamma, analytic Gaussian and prime tails, directed interval Schur complement",
        },
        "verified_matrix":{
            "weil_G_intervals":[[_outward_decimal(v,10**12) for v in row] for row in G],
            "L2_intervals":[[_outward_decimal(v,10**12) for v in row] for row in L],
            "L2_pivots":[_outward_decimal(v,10**12) for v in l2_pivots],
            "shifted_G_minus_kappa_L_pivots":[_outward_decimal(v,10**12) for v in pivots],
            "fourth_direction_schur":check,
            "failed_previous_3D_bound_schur_interval":_outward_decimal(old_schur,10**12),
            "previous_3D_bound":_fraction_string(PREVIOUS_THREE_DIMENSIONAL_LOWER),
            "previous_3D_generalized_lower_bound_survives":False,
            "strict_generalized_lambda_lower":_fraction_string(LOWER),
            "claim":"W(q_v^2) > (1/50000000)*||q_v||_L2^2 for all nonzero v in the fixed 4D span",
        },
        "assurance":{
            "actual_fourth_direction_cross_terms_enclosed":True,
            "fixed_four_span_generalized_positivity":True,
            "fifth_or_higher_actual_Weil_directions_certified":False,
            "uniform_dimension_independent_global_L2_coercivity":False,
            "full_Weil_positivity_proved":False,
            "Weil_Hilbert_completion_constructed":False,
            "riemann_hypothesis_proved":False,
            "independent_formal_verification":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panels",type=int,default=65536)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        data=audit(args.panels)
    except (ValueError,ArithmeticError) as exc:
        parser.error(str(exc))
    payload=json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
