"""Validated actual prime-active 2x2 Weil Gram with rational interval boxes.

Smooth compact tests phi(8*x), phi(8*(x-3/4)). The exact additive-log
arithmetic Weil formula has one prime power (2) in the cross entry.
Pole moments, prime term and full regularized archimedean terms are
enclosed with mpmath.iv on RATIONAL integration boxes. A reformulation
of the diagonal gamma integral removes its x=0 singularity.

Strict interval diagonal dominance AND interval LDL prove the fixed
2x2 Weil matrix positive with lambda_min > 137/5000 = 0.0274.

No claim of positivity in other windows, full Weil Hilbert space or RH.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from mpmath import iv

H=Fraction(1,8)
D=Fraction(3,4)
R=2*H
ZERO_CUTOFF=Fraction(1,2048)
VALID_PANELS=(256,512)
POSITIVE_FLOOR=Fraction(137,5000)


def F(v: Fraction) -> object:
    if not isinstance(v,Fraction):
        raise TypeError("rational argument required")
    return iv.mpf(v.numerator)/v.denominator


def I(lo: Fraction,hi: Fraction) -> object:
    if lo>hi:
        raise ValueError("interval endpoints reversed")
    return iv.mpf([F(lo).a,F(hi).b])


def phi(lo: Fraction,hi: Fraction) -> object:
    """Interval envelope for phi(x/H)=exp(1-1/(1-(x/H)^2)) on a box."""
    if lo>hi:
        raise ValueError("reversed bump interval")
    if lo>=H or hi<=-H:
        return iv.mpf(0)
    amin=min(abs(lo),abs(hi)) if lo*hi>0 else Fraction(0)
    amax=min(max(abs(lo),abs(hi)),H)
    def value(absolute: Fraction):
        z=F(absolute/H)
        return iv.exp(1-1/(1-z*z))
    if amax==H:
        return iv.mpf([0,value(amin).b])
    return iv.mpf([value(amax).a,value(amin).b])


def Kpoint(x: Fraction) -> object:
    """The positive decreasing kernel K(x)=e^(x/2)/(e^x-e^(-x))."""
    z=F(x)
    return iv.exp(z/2)/(iv.exp(z)-iv.exp(-z))


def Kbox(left: Fraction,right: Fraction) -> object:
    if not Fraction(0)<left<=right:
        raise ValueError("positive kernel interval required")
    # K'/K=1/2-coth(x)<0. Monotone endpoints avoid dependency blowup.
    return iv.mpf([Kpoint(right).a,Kpoint(left).b])


def out(x: object, decimals: int=8) -> list[str]:
    """Outward EXACT rational decimals for portable, independent checks."""
    from mathos.research.riemann_weil_certified_scalar import _rational_bound
    scale=10**decimals
    l=_rational_bound(x,False)*scale
    r=_rational_bound(x,True)*scale
    low=l.numerator//l.denominator
    high=-((-r.numerator)//r.denominator)
    return [str(Fraction(low,scale)),str(Fraction(high,scale))]


def _moments(n: int) -> tuple[object,object]:
    """Validated h(0)=integral phi^2 and moment integral phi*exp(x/2)."""
    step=2*H/n
    h0=iv.mpf(0)
    moment=iv.mpf(0)
    for j in range(n):
        left=-H+j*step
        right=left+step
        p=phi(left,right)
        h0+=p*p*F(step)
        moment+=p*iv.exp(I(left,right)/2)*F(step)
    return h0,moment


def _diagonal_differences(n: int) -> object:
    """J=int_0^R K(x)int_R (phi(t)-phi(t-x))^2 dt dx.

    h(x)-h(0)=-(1/2)*int(phi(t)-phi(t-x))^2dt by
    translation invariance of the L2 norm. The integrand is nonnegative.
    For 0<x<eps, |phi'|<64 and union-support length <1/2;
    K(x)<1/x. Therefore 0<=J_near<=1024*eps^2.
    All remaining boxes have dyadic EXACT rational endpoints.
    """
    dx=(R-ZERO_CUTOFF)/n
    dt=Fraction(1,2)/n
    total=iv.mpf(0)
    boxes=[]
    for j in range(n):
        left=-H+j*dt
        boxes.append((left,left+dt,phi(left,left+dt)))
    for i in range(n):
        xl=ZERO_CUTOFF+i*dx
        xr=xl+dx
        summed=iv.mpf(0)
        for tl,tr,p in boxes:
            diff=p-phi(tl-xr,tr-xl)
            summed+=diff**2*F(dt)
        total+=Kbox(xl,xr)*summed*F(dx)
    return total+iv.mpf([0,F(1024*ZERO_CUTOFF**2).b])


def _regularizer(n: int) -> object:
    """I1=int_0^R (exp(x/2)-1)/(exp(x)-exp(-x)) dx.

    On the first interval (0,dx), the integrand is between
    exp(-dx/2)*(1/4-dx/16) and exp(dx/2)/4.
    """
    dx=R/n
    low=F(Fraction(1,4)-dx/16)*iv.exp(-F(dx)/2)*F(dx)
    high=iv.exp(F(dx)/2)*F(dx)/4
    result=iv.mpf([low.a,high.b])
    for i in range(1,n):
        xl=i*dx
        xr=xl+dx
        x=I(xl,xr)
        result+=(iv.exp(x/2)-1)/(iv.exp(x)-iv.exp(-x))*F(dx)
    return result


def _arch_cross(n: int) -> object:
    """Exactly -int phi(s)*phi(t)*K(3/4+s-t) ds dt."""
    dt=2*H/n
    boxes=[]
    for i in range(n):
        left=-H+i*dt
        boxes.append((left,left+dt,phi(left,left+dt)))
    total=iv.mpf(0)
    for sl,sr,p in boxes:
        for tl,tr,q in boxes:
            total+=p*q*Kbox(D+sl-tr,D+sr-tl)*F(dt*dt)
    return -total


def _prime_cross(n: int) -> object:
    """Exactly -log(2)/sqrt(2)*integral phi(t)phi(t+3/4-log2)dt."""
    from mathos.research.riemann_weil_prime_two_window import log2_bounds
    loglo,loghi=log2_bounds(24)
    dt=2*H/n
    total=iv.mpf(0)
    for j in range(n):
        tl=-H+j*dt
        tr=tl+dt
        total+=phi(tl,tr)*phi(tl-loghi+D,tr-loglo+D)*F(dt)
    return -I(loglo,loghi)/iv.sqrt(2)*total


def audit(panels: int=256) -> dict:
    if type(panels) is not int or panels not in VALID_PANELS:
        raise ValueError("panels must be 256 or 512")
    iv.dps=45
    h0,m=_moments(2*panels)
    J=_diagonal_differences(panels)
    I1=_regularizer(2*panels)
    E=iv.exp(F(R))
    # 2*integral_R^infty exp(-x/2)*K(x)dx
    # = integral_R^infty dx/sinh(x) = -log(tanh(R/2)).
    tail=-iv.log((E-1)/(E+1))
    arch_diag=-(iv.log(4*iv.pi)+iv.euler)*h0+J-2*h0*I1+h0*tail
    pole_diag=2*m*m
    diag=arch_diag+pole_diag
    arch_cross=_arch_cross(panels)
    prime_cross=_prime_cross(4*panels)
    pole_cross=pole_diag*(iv.exp(F(D)/2)+iv.exp(-F(D)/2))/2
    cross=pole_cross+prime_cross+arch_cross
    from mathos.research.riemann_weil_certified_scalar import _rational_bound
    dlow=_rational_bound(diag,False)
    cross_abs=max(abs(_rational_bound(cross,False)),abs(_rational_bound(cross,True)))
    gap=dlow-cross_abs
    if gap<=POSITIVE_FLOOR:
        raise ArithmeticError("strict rational diagonal-dominance eigenvalue floor not certified")
    pivot2=diag-cross**2/diag
    if _rational_bound(pivot2,False)<=0:
        raise ArithmeticError("interval LDL second pivot is not strictly positive")
    return {
        "schema":"mathos_tectx_weil_prime_two_interval_psd/1",
        "status":"FIXED_PRIME_TWO_2X2_WEIL_POSITIVE_GLOBAL_RH_OPEN",
        "basis":["phi(8*x)","phi(8*(x-3/4))"],
        "normalization":"Suzuki additive-log Weil explicit formula; full pole, actual prime 2, and regularized archimedean distribution",
        "arithmetic":{
            "panels":panels,
            "rational_interval_nodes":True,
            "near_zero_cutoff":"1/2048",
            "pole_diagonal":out(pole_diag),
            "pole_cross":out(pole_cross),
            "prime_cross":out(prime_cross),
            "arch_diagonal":out(arch_diag),
            "arch_cross":out(arch_cross),
            "diagonal_Weil_entry":out(diag),
            "cross_Weil_entry":out(cross),
            "proved_eigenvalue_floor_rational":"137/5000",
            "actual_diagonal_dominance_margin_binary_rational":str(gap),
            "interval_LDL_pivots":[out(diag),out(pivot2)],
            "proof":"same exact diagonal by translation invariance; d_low>abs(c)_high+137/5000, and interval LDL pivots both positive",
        },
        "trust_boundary":{
            "interval_library":"mpmath.iv 1.3.0; directed rounding and source implementation trusted; no independent proof assistant verification",
            "positive_definite_fixed_2x2":True,
            "positive_all_support_windows":False,
            "all_index_Weil_PSD":False,
            "Riemann_hypothesis_proved":False,
            "full_Weil_Hilbert_space_constructed":False,
            "independent_formal_review":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--panels",type=int,default=256)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        r=audit(args.panels)
    except (ArithmeticError,ValueError) as e:
        p.error(str(e))
    payload=json.dumps(r,sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
