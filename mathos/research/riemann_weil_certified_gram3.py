"""Validated 3x3 Weil Gram: full arithmetic form with interval LDL certificate.

Fixed basis q_j(t)=exp(-t²/100)*cos(c_j*t), c_j in {0,1/5,1/2}.
The exact 3x3 Weil Gram uses h_jk=q_j*q_k and the standard Weil explicit
formula: poles, log(pi), digamma archimedean integral, all prime powers.

Composite Simpson with an explicit, *global* 4th derivative envelope bounds
the archimedean quadrature. Binet + shifted recurrence bounds digamma.
The analytic Gaussian and prime-power tails bound both infinite sums.
Interval LDL on G-(1/10^6)I then certifies all 3 pivots strictly positive.

No zero ordinates are inputs. This does NOT prove Weil positivity on any
other basis or all admissible functions, and does NOT prove RH.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from math import comb, isqrt
from pathlib import Path

from mpmath import iv

from mathos.research.riemann_weil_prime_tail import per_entry_prime_tail_bound
from mathos.research.riemann_weil_certified_scalar import (
    _prime_power_base, _outward_decimal, _rational_bound,
)

CENTERS = (Fraction(0), Fraction(1,5), Fraction(1,2))
A = Fraction(1,50)
T = 45
SHIFT = 64
PRIME_CUTOFF = 256
MIN_PANELS = 8192
MAX_PANELS = 16384
LAMBDA_LOWER = Fraction(1,10**6)


def _iv_frac(x: Fraction) -> object:
    return iv.mpf(x.numerator)/x.denominator


def _cosh(x: object) -> object:
    return (iv.exp(x)+iv.exp(-x))/2


def _f4_bound() -> Fraction:
    """Explicit |(e^(-t²/50) cos(ct)cos(dt) Re ψ(1/4+it/2))''''| bound.

    t in [0,45], c,d in [0,1/2].
    |g^(k)| <= (16,10,36,208,1632) for k=0..4, via
    the digamma recurrence and the absolutely convergent polygamma series.
    Gaussian derivative bounds use Amax=2*a*45.
    The product of cosines has kth derivative bounded by (c+d)^k <=1.
    """
    a = A
    v = 2*a*T
    gaussian = (
        Fraction(1), v, v*v+2*a, v**3+6*a*v,
        v**4+12*a*v*v+12*a*a,
    )
    h = tuple(
        sum(Fraction(comb(k,j))*gaussian[j] for j in range(k+1))
        for k in range(5)
    )
    g=(16,10,36,208,1632)
    return sum(Fraction(comb(4,j))*h[j]*g[4-j] for j in range(5))


def _digamma_core_at(t: object) -> object:
    """Shifted Re ψ with a certified additive remainder of absolute <= R.

    psi(w)=log w-1/(2w)-1/(12w²)+1/(120w⁴)+remainder.
    Binet expansion gives |remainder| <=1/(252 |w|^4 (Re w)^2),
    hence <=1/(252*(64+1/4)^6) for w=64+1/4+i*t/2.
    """
    r=iv.mpf(SHIFT)+iv.mpf(1)/4
    q=t*t/4
    den=r*r+q
    ans=iv.log(den)/2-r/(2*den)
    ans-=(r*r-q)/(12*den*den)
    ans+=(r**4-6*r*r*q+q*q)/(120*den**4)
    for k in range(SHIFT):
        x=iv.mpf(k)+iv.mpf(1)/4
        ans-=x/(x*x+q)
    return ans


def _arch_quad_matrix(panels: int) -> list[list[object]]:
    """Interval Simpson *sum*; separate rigorous quadrature error below."""
    cs=tuple(_iv_frac(c) for c in CENTERS)
    n=len(cs)
    sums=[[iv.mpf(0) for _ in range(n)] for _ in range(n)]
    for k in range(panels+1):
        t=iv.mpf(T*k)/panels  # exactly representable rational endpoints
        gauss=iv.exp(-_iv_frac(A)*t*t)
        dig=_digamma_core_at(t)
        cosines=tuple(iv.cos(c*t) for c in cs)
        weight=1 if k in (0,panels) else (4 if k%2 else 2)
        for i in range(n):
            for j in range(i,n):
                sums[i][j]+=weight*gauss*cosines[i]*cosines[j]*dig
    width=iv.mpf(T)/panels
    for i in range(n):
        for j in range(i,n):
            sums[i][j]=sums[j][i]=sums[i][j]*width/(3*iv.pi)
    return sums


def _fourier_h(logn: object, c: object, d: object) -> object:
    a=_iv_frac(A)
    result=iv.mpf(0)
    for sc in (-1,1):
        for sd in (-1,1):
            shift=sc*c+sd*d
            result+=iv.exp(-(logn-shift)**2/(4*a))
    return iv.sqrt(iv.pi/a)*result/4


def _full_error(panels: int) -> tuple[object,dict[str,object]]:
    a=_iv_frac(A)
    # Composite Simpson: |error| <= (T/180)*(T/n)^4*max|f^(4)|/pi.
    sim=iv.mpf(T)/180*(iv.mpf(T)/panels)**4*_iv_frac(_f4_bound())/iv.pi
    r=iv.mpf(SHIFT)+iv.mpf(1)/4
    rem=iv.mpf(1)/(252*r**6)
    dig=iv.mpf(T)*rem/iv.pi  # |h_jk(t)|<=1, interval [0,T]
    # Uniform bound |Re psi(1/4+it/2)| <= C+t/(2*SHIFT)
    # follows from the 64-step recurrence and Binet's base bound.
    C=iv.log(SHIFT+1)+4+iv.log(4*SHIFT)+iv.mpf(1)/(2*SHIFT)+iv.mpf(1)/(12*SHIFT*SHIFT)
    tail=iv.exp(-a*T*T)/iv.pi*(C/(2*a*T)+iv.mpf(1)/(4*a*SHIFT))
    delta=per_entry_prime_tail_bound()
    prime=_iv_frac(delta)
    return sim+dig+tail+prime, {
        "simpson_abs_error":sim,
        "digamma_remainder_abs_error":dig,
        "archimedean_infinite_tail_abs_error":tail,
        "prime_power_infinite_tail_abs_error":prime,
    }


def _gram_intervals(panels: int) -> tuple[list[list[object]],dict[str,object]]:
    base=_arch_quad_matrix(panels)
    cs=tuple(_iv_frac(c) for c in CENTERS)
    a=_iv_frac(A)
    scale=iv.sqrt(iv.pi/a)
    primes=[]
    for n in range(2,PRIME_CUTOFF+1):
        p=_prime_power_base(n)
        if p is not None:
            logn=iv.log(n)
            primes.append((iv.log(p)*iv.exp(-logn/2),logn))
    error, parts=_full_error(panels)
    error_interval=iv.mpf([-1,1])*error
    matrix=[[iv.mpf(0) for _ in range(3)] for _ in range(3)]
    for i,c in enumerate(cs):
        for j in range(i,3):
            d=cs[j]
            pole=2*iv.exp(a/4)*_cosh(c/2)*_cosh(d/2)
            logpi=-iv.log(iv.pi)*_fourier_h(iv.mpf(0),c,d)/(2*iv.pi)
            prime=iv.mpf(0)
            for coeff,logn in primes:
                prime+=coeff*_fourier_h(logn,c,d)
            prime=-prime/iv.pi
            x=pole+logpi+base[i][j]+prime+error_interval
            matrix[i][j]=matrix[j][i]=x
    return matrix,parts


def _interval_ldlt(matrix: list[list[object]], subtract: Fraction = Fraction(0)) -> list[object]:
    """Validate strict positive-definiteness of an *interval* symmetric matrix.

    All accepted real matrices lying in the entry intervals have positive
    pivots; fail closed if any interval pivot touches/nonpositive zero.
    """
    n=len(matrix)
    if not 1<=n<=5 or any(len(r)!=n for r in matrix):
        raise ValueError("square 1..5 interval matrix required")
    if not isinstance(subtract,Fraction) or subtract<0:
        raise ValueError("nonnegative rational shift required")
    L=[[iv.mpf(0) for _ in range(n)] for _ in range(n)]
    pivots=[]
    for i in range(n):
        value=matrix[i][i]-_iv_frac(subtract)
        for k in range(i):
            value-=L[i][k]*L[i][k]*pivots[k]
        if _rational_bound(value,False)<=0:
            raise ArithmeticError(f"pivot {i} is not certified strictly positive")
        pivots.append(value)
        for j in range(i+1,n):
            numerator=matrix[j][i]
            for k in range(i):
                numerator-=L[j][k]*pivots[k]*L[i][k]
            L[j][i]=numerator/value
    return pivots


def audit(panels: int = 8192) -> dict:
    if type(panels) is not int or panels not in (8192,16384):
        raise ValueError("supported panel counts: 8192 or 16384")
    iv.dps=50
    matrix,errors=_gram_intervals(panels)
    pivots=_interval_ldlt(matrix)
    shifted=_interval_ldlt(matrix,LAMBDA_LOWER)
    return {
        "schema":"mathos_tectx_weil_certified_gram3/1",
        "status":"FIXED_3X3_WEIL_GRAM_STRICTLY_POSITIVE_GLOBAL_RH_OPEN",
        "basis":{
            "a":"1/50","centers":["0/1","1/5","1/2"],
            "q_j":"exp(-t^2/100)*cos(c_j*t)",
            "h_jk":"q_j*q_k",
            "zero_ordinates_as_input":False,
        },
        "numerical_proof":{
            "backend":"mpmath.iv 1.3.0 outward interval arithmetic (implementation trusted)",
            "panels":panels,"digamma_shift":SHIFT,
            "archimedean_cutoff_T":T,
            "prime_power_cutoff":PRIME_CUTOFF,
            "fourth_derivative_global_envelope_exact":str(_f4_bound()),
            "error_bound_intervals":{k:_outward_decimal(v,10**18) for k,v in errors.items()},
            "matrix_entry_intervals": [
                [_outward_decimal(x,10**12) for x in row] for row in matrix
            ],
            "unshifted_LDL_pivots":[_outward_decimal(p,10**12) for p in pivots],
            "shifted_LDL_pivots":[_outward_decimal(p,10**12) for p in shifted],
            "proved_minimum_eigenvalue_greater_than": "1/1000000",
            "method":"validated composite Simpson global derivative bound + digamma Binet remainder + rigorous infinite archimedean and prime-power tails + interval LDL for G-1e-6 I",
        },
        "scope":{
            "positivity_proved_on_fixed_three_dimensional_span":True,
            "positivity_proved_on_entire_Weil_test_space":False,
            "uniform_positive_lower_bound_independent_of_test_span":False,
            "global_Weil_Hilbert_space_constructed":False,
            "riemann_hypothesis_proved":False,
            "independent_formal_verification":False,
        },
        "assurance_note":"The full analytic error inequalities are documented separately; CI and mpmath.iv are not independent proof-assistant verification.",
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panels",type=int,default=8192)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        r=audit(args.panels)
    except (ValueError,ArithmeticError) as e:
        parser.error(str(e))
    payload=json.dumps(r,sort_keys=True,indent=2,allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
