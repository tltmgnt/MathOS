"""Rigorously enclosed one-dimensional Weil-form computation.

For h(t)=exp(-t^2/50), use mpmath.iv outward interval arithmetic, an
explicit Binet-digamma remainder, range-enclosed real integration on
[0,45], an analytic Gaussian/digamma tail, and the exact-rational
prime-power tail bound from riemann_weil_prime_tail.py.

This certifies only the 1x1 Weil Gram, not the 3x3 numerical Gram,
full Weil positivity, or RH. It is not an independently checked formal proof.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

from mpmath import iv
from mathos.research.riemann_weil_prime_tail import per_entry_prime_tail_bound

A_RATIONAL = Fraction(1,50)
T = 45
DIGAMMA_SHIFT = 64
PRIME_CUTOFF = 256
MIN_PANELS = 2048
MAX_PANELS = 32768


def _rational_bound(y: object, upper: bool) -> Fraction:
    """Read mpmath.iv's binary endpoint as an EXACT rational."""
    point = y._mpi_[1 if upper else 0]  # type: ignore[attr-defined]
    sign, mantissa, exponent, _bc = point
    numerator = -mantissa if sign else mantissa
    return Fraction(numerator*(1<<exponent),1) if exponent >= 0 else Fraction(numerator,1<<(-exponent))


def _rational_string(f: Fraction) -> str:
    return f"{f.numerator}/{f.denominator}"


def _outward_decimal(y: object, scale: int = 10**6) -> list[str]:
    """Outward rational decimal values suitable as a portable certificate."""
    lower = _rational_bound(y, False)
    upper = _rational_bound(y, True)
    lower_scaled = lower*scale
    upper_scaled = upper*scale
    lower_int = lower_scaled.numerator // lower_scaled.denominator
    upper_int = -((-upper_scaled.numerator)//upper_scaled.denominator)
    return [_rational_string(Fraction(lower_int,scale)),
            _rational_string(Fraction(upper_int,scale))]


def _prime_power_base(n: int) -> int | None:
    """Smallest p for which n=p^k, and None for non-prime powers."""
    if type(n) is not int or n < 2:
        return None
    p = next((d for d in range(2,math.isqrt(n)+1) if n%d==0),n)
    v = n
    while v % p == 0:
        v //= p
    return p if v == 1 else None


def _digamma_real_enclosure(t: object, shift: int = DIGAMMA_SHIFT) -> object:
    """Enclose Re psi(1/4+i*t/2), uniformly on an interval of t>=0.

    Binet's 2nd formula gives:
    psi(w)=log w - 1/(2w) -
      2*int_0^infinity u/(w^2+u^2)/(exp(2*pi*u)-1)du.

    For Re(w)=x>0, |w^2+u^2|=|w+iu||w-iu| >= x^2, so the
    remainder magnitude is at most 1/(12*x^2).
    The recurrence psi(z)=psi(z+shift)-sum_(k<shift)1/(z+k)
    then yields the real interval formula below.
    """
    if type(shift) is not int or shift < 1:
        raise ValueError("positive integer digamma shift required")
    z = iv.mpf(shift) + iv.mpf(1)/4
    t2 = t*t/4
    val = iv.log(z*z+t2)/2 - z/(2*(z*z+t2))
    for k in range(shift):
        r = iv.mpf(4*k+1)/4
        val -= r/(r*r+t2)
    remainder = iv.mpf(1)/(12*z*z)
    return val + iv.mpf([-1,1])*remainder


def _archimedean_integral_enclosure(panels: int) -> tuple[object, object]:
    """Outward interval enclosure of (1/pi)*integral_0^infinity
    exp(-t*t/50)*Re psi(1/4+i*t/2)dt.

    Range enclosure on each subinterval bounds the integral directly,
    without an unproved Simpson/finite-difference derivative estimate.
    """
    if type(panels) is not int or not MIN_PANELS <= panels <= MAX_PANELS or panels & (panels-1):
        raise ValueError("panels must be power of 2 in 2048..32768")
    a = iv.mpf(1)/50
    total = iv.mpf(0)
    width = iv.mpf(T)/panels
    for j in range(panels):
        # All endpoints are exactly representable binary fractions.
        t = iv.mpf([j*T/panels, (j+1)*T/panels])
        integrand = iv.exp(-a*t*t)*_digamma_real_enclosure(t)
        total += integrand*width/iv.pi

    # For t>=T, bound |Re psi| by C+t/(2*shift).
    # 1/(z+k) recurrence and harmonic integral yield:
    # C=log(shift+1)+4+log(4*shift)+1/(2*shift)+1/(12*shift^2).
    m = DIGAMMA_SHIFT
    C = (iv.log(m+1)+4+iv.log(4*m)
         +iv.mpf(1)/(2*m)+iv.mpf(1)/(12*m*m))
    tail = (iv.exp(-a*T*T)/iv.pi *
            (C/(2*a*T) + iv.mpf(1)/(2*m)/(2*a)))
    return total, tail


def _finite_prime_enclosure(cutoff: int = PRIME_CUTOFF) -> object:
    if cutoff != PRIME_CUTOFF:
        raise ValueError("only cutoff=256 has the adopted proved tail guarantee")
    a = iv.mpf(1)/50
    s = iv.mpf(0)
    scale = iv.sqrt(iv.pi/a)
    for n in range(2,cutoff+1):
        p = _prime_power_base(n)
        if p is None:
            continue
        lnn = iv.log(n)
        lam = iv.log(p)
        hhat = scale*iv.exp(-(lnn*lnn)/(4*a))
        s += lam*iv.exp(-lnn/2)*hhat
    return -s/iv.pi


def audit(panels: int = 4096) -> dict:
    # No independent float result can promote the proof state.
    iv.dps = 45
    arch, tail = _archimedean_integral_enclosure(panels)
    a = iv.mpf(1)/50
    pole = 2*iv.exp(a/4)
    logpi = -iv.log(iv.pi)*iv.sqrt(iv.pi/a)/(2*iv.pi)
    prime = _finite_prime_enclosure()
    finite = pole+logpi+arch+prime
    delta = per_entry_prime_tail_bound()
    prime_remainder = iv.mpf(delta.numerator)/delta.denominator
    full = finite + iv.mpf([-1,1])*(tail+prime_remainder)

    lo = _rational_bound(full,False)
    hi = _rational_bound(full,True)
    if not (lo > 0 and hi >= lo):
        raise ArithmeticError("no certified strictly positive Weil scalar bound")
    return {
        "schema":"mathos_tectx_weil_certified_scalar/1",
        "status":"ONE_DIMENSIONAL_WEIL_POSITIVITY_CERTIFIED_GLOBAL_RH_OPEN",
        "test_function":"h(t)=exp(-t^2/50), Gaussian-cosine center 0",
        "proof_scope":"actual Weil explicit-formula scalar with all pole/gamma/prime-power terms; one fixed test function, not a whole function space",
        "backend":"mpmath.iv==1.3.0; outward binary interval arithmetic; non-formal implementation",
        "parameters":{"digamma_shift":DIGAMMA_SHIFT,"panels":panels,
                      "integral_T":T,"prime_cutoff":PRIME_CUTOFF,
                      "arithmetic_precision_dps":45},
        "components_outward_rationals":{
            "pole":_outward_decimal(pole),
            "log_pi":_outward_decimal(logpi),
            "archimedean_integral_up_to_45":_outward_decimal(arch),
            "archimedean_abs_tail":_outward_decimal(tail,10**20),
            "finite_prime_power_sum":_outward_decimal(prime),
            "prime_power_abs_tail":_rational_string(delta),
            "finite_G_256_eigenvalue":_outward_decimal(finite),
            "full_G_eigenvalue":_outward_decimal(full),
        },
        "proof":{
            "digamma_remainder":"Binet ψ(w)=log w-1/(2w)-2 integral_0^infty u/((w^2+u^2)(exp(2*pi*u)-1))du. For Re(w)>0 absolute remainder <=1/(12*(Re w)^2)",
            "recurrence":"ψ(z)=ψ(z+64)-sum_(k=0)^63 1/(z+k), z=1/4+i*t/2",
            "integration":"each entire interval value encloses the integrand on its dyadic subinterval; multiply by exact width and sum; finite-interval integral is contained",
            "archimedean_infinite_tail":"|Re ψ(1/4+i*t/2)| <= C + t/(2*64), t>=45; Gaussian integral tail bounded by e^(-aT²)*(C/(2aT)+1/(4a*64))/pi",
            "prime_tail":"exact rational analytic bound from riemann_weil_prime_tail.py, which covers all prime powers n>256",
            "scalar_positivity_certificate":"full_G_eigenvalue rational lower endpoint is strictly greater than zero",
            "certification_method":"conditional on correctness of mpmath.iv binary directed rounding and source implementations; audit is not Lean or independent formal proof",
        },
        "assurance":{
            "one_test_function_positive_enclosed":True,
            "all_three_dimensional_Weil_Gram_enclosed":False,
            "all_admissible_test_functions_positive":False,
            "global_Weil_Hilbert_space_constructed":False,
            "riemann_hypothesis_proved":False,
            "independent_mathematical_review_completed":False,
        },
        "limitations":[
            "Does not enclose the earlier 3-by-3 Gram eigenvalues; only the exact 1-by-1 matrix",
            "Cannot certify RH-equivalent all-functions positivity from this single analytic test",
            "Uses interval library rather than independently verified proof assistant or Arb",
            "No new arithmetic or spectral theorem beyond a concrete bounded test-function inequality is claimed",
        ],
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--panels",type=int,default=4096)
    p.add_argument("--output",type=Path)
    x=p.parse_args()
    try:
        result=audit(x.panels)
    except (ValueError,ArithmeticError) as e:
        p.error(str(e))
    payload=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if x.output:
        x.output.parent.mkdir(parents=True,exist_ok=True)
        x.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
