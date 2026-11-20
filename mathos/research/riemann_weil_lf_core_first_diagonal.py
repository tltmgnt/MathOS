"""First ACTUAL normalized LF-dense-core Weil Gram diagonal, with prime 2.

Rigorous signed arithmetic Weil formula W(b_0 * tilde(b_0)) for the
FIRST function b_(1,0) of the rational-center, dyadic-scale countable
LF-dense compact core from PR #83/#92. b_0 is exactly the unit-mass
smooth bump with support [-1/2,1/2].

Derive fully outward interval bounds on pole, nonzero prime-2 and
complete regularized archimedean terms. The Gamma integrand's
singularity is cancelled using the exact autocorrelation identity.
All numerical integration uses interval-valued point trapezoid sums
with EXPLICIT global C2 derivative error, plus monotone Darboux
bounds on the remaining one-dimensional positive integral.

The certificate is for ONE entry, not the entire dense-core Gram,
all-index PSD, a full positive Weil Hilbert space or RH.
No nontrivial zeros are input.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from mpmath import iv
from mathos.research.riemann_weil_all_index_bridge import enumerate_compact_bumps
from mathos.research.riemann_weil_lattice_topology_audit import rational_log_integer
from mathos.research.riemann_weil_certified_scalar import _rational_bound
from mathos.research.riemann_weil_lf_dense_core_workflow import (
    exact_prime_power_inventory,
)

HALF_WIDTH=Fraction(1,2)
R=Fraction(1)
NEAR_ZERO=Fraction(1,512)
HALF_PANELS=256
DYADIC_PANELS=256
MIN_NORMALIZED_WEIL_VALUE=Fraction(1,1000)


def q(v: Fraction) -> str:
    return f"{v.numerator}/{v.denominator}"


def exact_iv(value: Fraction) -> object:
    if not isinstance(value,Fraction):
        raise TypeError("exact Fraction required")
    return iv.mpf(value.numerator)/value.denominator


def interval(lo: Fraction,hi: Fraction) -> object:
    if lo>hi:
        raise ArithmeticError("reversed rational interval")
    return iv.mpf([exact_iv(lo).a,exact_iv(hi).b])


def endpoints(x: object) -> tuple[Fraction,Fraction]:
    return _rational_bound(x,False),_rational_bound(x,True)


def outward(x: object,places: int=9) -> list[str]:
    lo,hi=endpoints(x)
    mult=10**places
    a=lo*mult
    b=hi*mult
    return [q(Fraction(a.numerator//a.denominator,mult)),
            q(Fraction(-(-b.numerator//b.denominator),mult))]


def phi_point(x: Fraction) -> object:
    """unnormalized phi_old(2x)=exp(1-1/(1-4x²)), |x|<1/2."""
    if abs(x)>=HALF_WIDTH:
        return iv.mpf(0)
    u=exact_iv(x/HALF_WIDTH)
    return iv.exp(1-1/(1-u*u))


def covariance_at(x: Fraction, panels: int=HALF_PANELS) -> object:
    """Trap rule + absolute 2nd-derivative error encloses h(x)=f*tilde f.

    h(x)=2 integral_0^(1/2-x/2) f(u+x/2)f(u-x/2)du.
    f is even, nonnegative, Cc-infinity. From elementary y=1/(1-u²)
    inequalities: |phi_old'|<=4 and |phi_old''|<=127.
    Thus |f'|<=8, |f''|<=508, and
    |(f(u+x/2)f(u-x/2))''|<=2*508+2*8^2=1144.
    The composite trap error, after factor 2, is bounded by
    2*L^3*1144/(12*panels^2), L=(1-x)/2.
    """
    if type(panels) is not int or panels<=0:
        raise ValueError("positive integer panels required")
    if not isinstance(x,Fraction) or not Fraction(0)<=x<=R:
        raise ValueError("rational x in [0,1] required")
    if x==R:
        return iv.mpf(0)
    length=HALF_WIDTH-x/2
    step=length/panels
    total=iv.mpf(0)
    for j in range(panels+1):
        u=j*step
        val=phi_point(u+x/2)*phi_point(u-x/2)
        if j in (0,panels):
            val/=2
        total+=val
    estimate=2*exact_iv(step)*total
    error=2*length**3*1144/(12*panels**2)
    return estimate+interval(-error,error)


def pole_moments(panels: int=HALF_PANELS) -> tuple[object,object]:
    """Validated f mass m0 and pole moment m1=integral f e^(x/2).

    By evenness, integrate 2*f(x) and 2*f(x)*cosh(x/2) on [0,1/2].
    Their global second derivative bounds are 508 and 690:
    e^(1/4)<4/3 and (4/3)*(508+8+1/4)<690.
    """
    if type(panels) is not int or panels<=0:
        raise ValueError("positive integer panels required")
    step=HALF_WIDTH/panels
    plain=iv.mpf(0)
    tilted=iv.mpf(0)
    for j in range(panels+1):
        x=j*step
        value=phi_point(x)
        z=exact_iv(x)/2
        weighted=value*(iv.exp(z)+iv.exp(-z))/2
        if j in (0,panels):
            value/=2
            weighted/=2
        plain+=value
        tilted+=weighted
    m0=2*exact_iv(step)*plain
    m1=2*exact_iv(step)*tilted
    error0=2*HALF_WIDTH**3*508/(12*panels**2)
    error1=2*HALF_WIDTH**3*690/(12*panels**2)
    return (m0+interval(-error0,error0),
            m1+interval(-error1,error1))


def gamma_kernel(x: Fraction) -> object:
    """K(x)=e^(x/2)/(e^x-e^(-x)) >0, strictly decreasing for x>0."""
    if not isinstance(x,Fraction) or x<=0:
        raise ValueError("gamma kernel needs rational x>0")
    z=exact_iv(x)
    return iv.exp(-z/2)/(1-iv.exp(-2*z))


def archimedean_coefficient() -> tuple[object,object,object]:
    """Exact closed regularizer plus infinite tail, no singular numerics.

    I1=int_0^1 [(e^(x/2)-1)/(e^x-e^(-x))]dx.
    Put y=e^(1/2), z=(y-1)/(y+1) in (0,1/4).
    Then I1=atan(z)+1/2 log((e+1)/2)-log((y+1)/2).
    Alternating arctan series has remainder < z^41/41 after 20 terms.
    Tail=2 int_1^infinity e^(-x/2)K(x)dx
        =log((e+1)/(e-1)).
    h0 coefficient equals -log(4*pi)-EulerGamma-2*I1+Tail.
    """
    y=iv.exp(iv.mpf(1)/2)
    z=(y-1)/(y+1)
    s=iv.mpf(0)
    for j in range(20):
        term=z**(2*j+1)/(2*j+1)
        s+=term if j%2==0 else -term
    rem=z**41/41
    r=_rational_bound(rem,True)
    atan=s+interval(-r,r)
    e=iv.exp(1)
    i1=atan+iv.log((e+1)/2)/2-iv.log((y+1)/2)
    tail=iv.log((e+1)/(e-1))
    coeff=-(iv.log(4*iv.pi)+iv.euler)-2*i1+tail
    return coeff,i1,tail


def dyadic_grid(panels: int=DYADIC_PANELS) -> list[Fraction]:
    """Exact rational partition [1/512,1] by 9 dyadic bands."""
    if type(panels) is not int or not 1<=panels<=1024:
        raise ValueError("panels must be integer 1..1024")
    out=[]
    for k in range(8,-1,-1):
        a=Fraction(1,2**(k+1))
        b=Fraction(1,2**k)
        out.extend(a+(b-a)*j/panels for j in range(panels))
    out.append(R)
    if out[0]!=NEAR_ZERO or out[-1]!=R:
        raise ArithmeticError("incorrect dyadic integration partition")
    return out


def positive_gamma_integral(
    h0: object,half_panels: int=HALF_PANELS,
    dyadic_panels: int=DYADIC_PANELS,
) -> object:
    """Entire J=int_0^1 K(x)*D(x)dx with D(x)=2(h0-h(x))>=0.

    For even nonnegative monotone f, its autocorrelation h is decreasing
    on x>=0 (layer cake of symmetric interval indicators). Thus D
    increases and K decreases. In each [a,b], use D(a)K(b) and
    D(b)K(a) for pointwise lower/upper enclosure. h(x) point
    intervals come from certified trap second-derivative bounds.
    On [0,1/512], D(x)<=x²||f'||_2²<=64*x² and K(x)<=1/x,
    giving 0<=J_near<=32*(1/512)².
    """
    grid=dyadic_grid(dyadic_panels)
    total=iv.mpf(0)
    hprev=covariance_at(grid[0],half_panels)
    h0lo,h0hi=endpoints(h0)
    for i in range(len(grid)-1):
        a,b=grid[i],grid[i+1]
        hnext=covariance_at(b,half_panels)
        prevlo,prevhi=endpoints(hprev)
        nextlo,nexthi=endpoints(hnext)
        dl=max(Fraction(0),2*(h0lo-prevhi))
        du=max(Fraction(0),2*(h0hi-nextlo))
        klo=_rational_bound(gamma_kernel(b),False)
        khi=_rational_bound(gamma_kernel(a),True)
        step=b-a
        total+=interval(step*dl*klo,step*du*khi)
        hprev=hnext
    return total+interval(Fraction(0),32*NEAR_ZERO**2)


def audit(
    half_panels: int=HALF_PANELS,dyadic_panels: int=DYADIC_PANELS,
) -> dict:
    """Certify actual first normalized Weil core diagonal > 1/1000."""
    if type(half_panels) is not int or half_panels not in (128,256,512):
        raise ValueError("half_panels must be 128,256,512")
    if type(dyadic_panels) is not int or dyadic_panels not in (64,128,256,512):
        raise ValueError("dyadic_panels must be 64,128,256,512")
    iv.dps=36
    first=enumerate_compact_bumps(1)[0]
    if (first["n"]!=1 or first["center"]!="0/1" or
        Fraction(first["half_support_width"])!=HALF_WIDTH):
        raise ArithmeticError("incorrect canonical dense-core first direction")
    primes=exact_prime_power_inventory(-R,R)
    if primes!=[{"n":2,"von_mangoldt_base":2}]:
        raise ArithmeticError("unexpected arithmetic prime inventory")
    h0=covariance_at(Fraction(0),half_panels)
    mass,m1=pole_moments(half_panels)
    if _rational_bound(mass,False)<=0:
        raise ArithmeticError("bump normalization integral not positive")
    J=positive_gamma_integral(h0,half_panels,dyadic_panels)
    coefficient,i1,tail=archimedean_coefficient()
    arch=coefficient*h0+J
    pole=2*m1*m1
    loglo,loghi=rational_log_integer(2,32)
    if not (Fraction(69,100)<loglo<loghi<Fraction(70,100)):
        raise ArithmeticError("exact prime 2 logarithm not enclosed")
    hlower=covariance_at(loghi,half_panels)
    hupper=covariance_at(loglo,half_panels)
    prime_sample=interval(
        max(Fraction(0),_rational_bound(hlower,False)),
        _rational_bound(hupper,True),
    )
    prime=-iv.sqrt(2)*iv.log(2)*prime_sample
    total=pole+prime+arch
    normalized=total/(mass*mass)
    if _rational_bound(prime,True)>=0:
        raise ArithmeticError("prime 2 did not contribute strictly negatively")
    if _rational_bound(normalized,False)<=MIN_NORMALIZED_WEIL_VALUE:
        raise ArithmeticError("normalized canonical Weil diagonal not strictly certified")
    return {
        "schema":"mathos_tectx_weil_LF_core_first_diagonal/1",
        "status":"FIRST_CANONICAL_LF_CORE_WEIL_DIAGONAL_POSITIVE_NOT_ALL_INDEX",
        "test_function":{
            "core_index":0,"n":1,"center":"0/1",
            "support":["-1/2","1/2"],
            "actual_b0":"normalized unit-mass b_0(x)=f(x)/m0, f(x)=exp(1-1/(1-4x^2)) on |x|<1/2, else 0",
            "normalization":"m0=int_-1/2^1/2 f(x)dx, so b0(x)=2*phi_normalized(2x)",
            "corresponds_to_PR83_dense_core":True,
        },
        "arithmetic":{
            "half_panels":half_panels,
            "dyadic_band_panels":dyadic_panels,
            "dyadic_bands":9,
            "interval_precision_dps":36,
            "prime_powers":primes,
            "log2_rational_interval":[q(loglo),q(loghi)],
            "raw_mass_m0_interval":outward(mass),
            "raw_autocorrelation_h0_interval":outward(h0),
            "raw_exponential_pole_moment_m1_interval":outward(m1),
            "raw_pole_interval":outward(pole),
            "raw_prime2_interval":outward(prime),
            "raw_archimedean_interval":outward(arch),
            "raw_positive_regularized_J_interval":outward(J),
            "closed_regularizer_I1_interval":outward(i1,12),
            "closed_infinite_gamma_tail_interval":outward(tail,12),
            "raw_complete_Weil_interval":outward(total),
            "normalized_complete_Weil_interval":outward(normalized),
            "proved_normalized_strict_lower":"1/1000",
            "proof_scope":"one exact normalized LF-dense-core test; full pole, prime 2, regularized archimedean distribution and infinite tail",
            "gamma_identity":"D(x)=int_R |f(t)-f(t-x)|²dt=2[h(0)-h(x)], gamma arch = h0*(-log(4*pi)-EulerGamma-2*I1+Tail)+int_0^1 K(x)D(x)dx",
            "global_trap_derivative_bounds":{"f_prime":8,"f_second":508,
                "convolution_integrand_second":1144,
                "plain_moment_second":508,
                "pole_moment_second":690},
            "near_zero_integral_upper":q(32*NEAR_ZERO**2),
            "uses_nontrivial_zero_locations":False,
        },
        "assurance":{
            "this_one_core_diagonal_positive":True,
            "all_first_prefix_gram_entries_evaluated":False,
            "every_finite_LF_core_Gram_psd":False,
            "global_Weil_positivity":False,
            "full_positive_Weil_Hilbert_completion":False,
            "Riemann_hypothesis_proved":False,
            "independently_formally_verified":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--half-panels",type=int,default=HALF_PANELS)
    p.add_argument("--dyadic-panels",type=int,default=DYADIC_PANELS)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        r=audit(args.half_panels,args.dyadic_panels)
    except (ArithmeticError,ValueError) as exc:
        p.error(str(exc))
    payload=json.dumps(r,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
