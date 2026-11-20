"""TECT-X: first two ACTUAL normalized LF-dense compact Weil Gram entries.

The first two functions in PR #83's immutable enumeration are b_(1,0)
and b_(1,-1): equal normalized smooth bumps, centers 0 and -1,
supports [-1/2,1/2] and [-3/2,-1/2]. The off-diagonal
convolution is supported [0,2] and samples exactly the prime powers
2,3,4,5,7.

Its full arithmetic Weil entry consists of a pole term, those five
prime terms and the nonsingular-by-flatness archimedean integral
   -int_0^2 K(x) h_0(|x-1|) dx
where h_0 is the same compact-bump autocorrelation as PR #94,
K(x)=exp(x/2)/(exp(x)-exp(-x)).
A global explicit |g''|<300 for g=K*h_0(|x-1|) proves a signed
composite-trapezoid remainder <=200/N^2, despite K's formal
1/x singularity at zero: the smooth bump is flat at its support edge.
All trapezoid nodes use *certified* autocorrelation interval values
from the previous theorem, not ordinary point samples.

We reuse PR #94's rigorously enclosed first diagonal (identical
second diagonal by translation invariance) and positive mass, and
check exact rational 2x2 Schur and normalized eigenvalue bounds.
No zero ordinates or RH are assumed or claimed.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from mpmath import iv
from mathos.research.riemann_weil_all_index_bridge import enumerate_compact_bumps
from mathos.research.riemann_weil_lf_dense_core_workflow import (
    exact_prime_power_inventory,
    support_pair,
)
from mathos.research.riemann_weil_lattice_topology_audit import rational_log_integer
from mathos.research.riemann_weil_lf_core_first_diagonal import (
    audit as first_diagonal_audit,
    covariance_at, pole_moments, gamma_kernel,
    exact_iv, interval, endpoints, outward, q,
)

EXPECTED_PRIME_POWERS=((2,2),(3,3),(4,2),(5,5),(7,7))
CROSS_CENTER_SEPARATION=Fraction(1)
CROSS_SUPPORT=(Fraction(0),Fraction(2))
TRAPEZOID_SECOND_DERIVATIVE_BOUND=300
TRAPEZOID_ERROR_NUMERATOR=200
GAMMA_PANELS=2048
COVARIANCE_PANELS=512
PRIME_PANELS=1024
POLE_PANELS=1024
TARGET_EIGEN_FLOOR=Fraction(1,10000)


def validate_first_two() -> list[dict]:
    actual=enumerate_compact_bumps(2)
    expected=[(1,"0/1","-1/2","1/2"),
              (1,"-1/1","-3/2","-1/2")]
    got=[(b["n"],b["center"],b["support_left"],b["support_right"])
         for b in actual]
    if got!=expected:
        raise ArithmeticError(f"immutable LF core enumeration changed: {got}")
    low,high=support_pair(actual[0],actual[1])
    if (low,high)!=CROSS_SUPPORT:
        raise ArithmeticError("incorrect first off-diagonal convolution support")
    primes=exact_prime_power_inventory(low,high)
    if [(v["n"],v["von_mangoldt_base"]) for v in primes]!=list(EXPECTED_PRIME_POWERS):
        raise ArithmeticError("arithmetic support inventory changed")
    return actual


def covariance_range_at_log(n: int,panels: int=PRIME_PANELS) -> object:
    """Rigorous h0(|log(n)-1|), using monotonic h0 and exact log bracket."""
    lo,hi=rational_log_integer(n,32)
    if not Fraction(0)<lo<hi<Fraction(2):
        raise ArithmeticError("prime logarithm leaves cross support")
    dmax=max(abs(lo-1),abs(hi-1))
    dmin=Fraction(0) if lo<=1<=hi else min(abs(lo-1),abs(hi-1))
    if not Fraction(0)<=dmin<=dmax<Fraction(1):
        raise ArithmeticError("invalid prime convolution shift")
    vlow=covariance_at(dmax,panels)
    vhigh=covariance_at(dmin,panels)
    low=max(Fraction(0),endpoints(vlow)[0])
    high=endpoints(vhigh)[1]
    if low>high:
        raise ArithmeticError("inverted prime convolution enclosure")
    return interval(low,high)


def prime_cross(panels: int=PRIME_PANELS) -> tuple[object,list[dict]]:
    """Complete offdiagonal von Mangoldt prime sum at 2,3,4,5,7."""
    if type(panels) is not int or panels not in (256,512,1024,2048):
        raise ValueError("prime panels must be 256,512,1024,2048")
    total=iv.mpf(0)
    pieces=[]
    for n,p in EXPECTED_PRIME_POWERS:
        sample=covariance_range_at_log(n,panels)
        term=-iv.log(p)/iv.sqrt(n)*sample
        total+=term
        pieces.append({
            "prime_power":n,"von_mangoldt_base":p,
            "positive_convolution_sample":outward(sample,10),
            "arithmetic_term":outward(term,10),
            "strict_nonzero_from_support":True,
        })
    return total,pieces


def gamma_cross(
    panels: int=GAMMA_PANELS,
    cov_panels: int=COVARIANCE_PANELS,
) -> object:
    """Range-enclosed composite trapezoid of K(x)*h0(|x-1|), x in [0,2].

    For 0<x<=1/2, the overlap of shifted compact bump supports has
    length x. |f'|<=8 and support-edge flatness imply
       0<=h0(1-x)<= (32/3)x^3
       |d_x h0(1-x)|<=32*x^2
       |d_x² h0(1-x)|<=64*x.
    For x>=1/2: 0<=h0<=1, |h0'|<=8, |h0''|<=64.

    K<=1/x, |K'|<=2/x², |K''|<=5/x³ on 0<x<=2.
    Therefore |(K*h0(|x-1|))''|<=
       64+128+160/3<246 on x<=1/2,
       128+128+40=296 on x>=1/2.
    The product extends smoothly as 0 at x=0 and is smooth at x=1.
    Hence global |g''|<300. On [0,2], composite trapezoid error
       (2^3)/(12*panels²)*300 = 200/panels².
    For even panels, pair symmetric autocorrelation nodes to reuse
    half the expensive validated covariance calculations.
    """
    if type(panels) is not int or panels not in (1024,2048,4096) or panels%2:
        raise ValueError("gamma panels must be even 1024,2048,4096")
    if type(cov_panels) is not int or cov_panels not in (256,512,1024):
        raise ValueError("covariance panels must be 256,512,1024")
    step=Fraction(2,panels)
    total=iv.mpf(0)
    for j in range(1,panels//2):
        x=j*step
        h=covariance_at(Fraction(1)-x,cov_panels)
        low=max(Fraction(0),endpoints(h)[0])
        high=endpoints(h)[1]
        total+=interval(low,high)*(gamma_kernel(x)+gamma_kernel(2-x))
    total+=covariance_at(Fraction(0),cov_panels)*gamma_kernel(Fraction(1))
    total*=exact_iv(step)
    error=Fraction(TRAPEZOID_ERROR_NUMERATOR,panels*panels)
    return total+interval(-error,error)


def audit(
    gamma_panels: int=GAMMA_PANELS,
    covariance_panels: int=COVARIANCE_PANELS,
    prime_panels: int=PRIME_PANELS,
    pole_panels: int=POLE_PANELS,
) -> dict:
    if (type(gamma_panels) is not int or gamma_panels not in (1024,2048,4096)
        or type(covariance_panels) is not int or covariance_panels not in (256,512,1024)
        or type(prime_panels) is not int or prime_panels not in (256,512,1024,2048)
        or type(pole_panels) is not int or pole_panels not in (256,512,1024)):
        raise ValueError("unsupported validated integration panel combination")
    iv.dps=36
    basis=validate_first_two()
    previous=first_diagonal_audit(256,256)
    diaglo,diaghi=map(Fraction,previous["arithmetic"]["raw_complete_Weil_interval"])
    masslo,masshi=map(Fraction,previous["arithmetic"]["raw_mass_m0_interval"])
    if not (Fraction(0)<diaglo<=diaghi and Fraction(0)<masslo<=masshi):
        raise ArithmeticError("missing certified first diagonal and normalization")
    _,m1=pole_moments(pole_panels)
    pole=2*m1*m1*(iv.exp(exact_iv(Fraction(1,2)))+
                   iv.exp(-exact_iv(Fraction(1,2))))/2
    primes,prime_parts=prime_cross(prime_panels)
    arch=-gamma_cross(gamma_panels,covariance_panels)
    cross=pole+primes+arch
    # All public rational proof margins MUST use precisely the
    # serialized outward endpoints; never test a hidden-precision
    # margin which a third-party checker cannot reproduce.
    serialized_cross=outward(cross)
    clo,chi=map(Fraction,serialized_cross)
    crossabs=max(abs(clo),abs(chi))
    raw_margin=diaglo-crossabs
    normal_margin=raw_margin/(masshi*masshi)
    # For the normalized 2x2 Gram both diag and cross divide by m0^2.
    if not normal_margin>TARGET_EIGEN_FLOOR:
        raise ArithmeticError(
            f"insufficient interval 2x2 PSD margin: normalized={normal_margin}, "
            f"raw_diag_lower={diaglo}, cross_abs_upper={crossabs}")
    schur_margin=diaglo-crossabs*crossabs/diaglo
    if schur_margin<=0:
        raise ArithmeticError("rational second Schur pivot inconclusive")
    return {
        "schema":"mathos_tectx_weil_lf_core_first_2x2/1",
        "status":"FIXED_FIRST_TWO_LF_CORE_WEIL_GRAM_POSITIVE_GLOBAL_RH_OPEN",
        "basis":{
            "first_two_immutable_enumeration":basis,
            "normalized_functions":"b_(1,0),b_(1,-1), equal unit-mass real Cc-infinity bumps",
            "cross_convolution_support":["0/1","2/1"],
            "diagonal_translation_invariance_exact":True,
            "offdiag_reflection_Hermitian_exact":True,
        },
        "arithmetic":{
            "gamma_panels":gamma_panels,
            "covariance_panels":covariance_panels,
            "prime_panels":prime_panels,
            "pole_panels":pole_panels,
            "gamma_global_second_derivative_upper":TRAPEZOID_SECOND_DERIVATIVE_BOUND,
            "gamma_signed_trapezoid_error_exact":q(Fraction(TRAPEZOID_ERROR_NUMERATOR,gamma_panels**2)),
            "prime_power_inventory":[{"n":n,"von_mangoldt_base":p}
                                     for n,p in EXPECTED_PRIME_POWERS],
            "prime_power_parts":prime_parts,
            "offdiagonal_pole_interval":outward(pole),
            "offdiagonal_prime_interval":outward(primes),
            "offdiagonal_archimedean_interval":outward(arch),
            "offdiagonal_full_raw_Weil_interval":serialized_cross,
            "diagonal_full_raw_Weil_interval":previous["arithmetic"]["raw_complete_Weil_interval"],
            "normalizing_mass_interval":previous["arithmetic"]["raw_mass_m0_interval"],
            "full_normalized_Gram_2x2":[
                [previous["arithmetic"]["normalized_complete_Weil_interval"],
                 outward(cross/(interval(masslo,masshi)**2))],
                [outward(cross/(interval(masslo,masshi)**2)),
                 previous["arithmetic"]["normalized_complete_Weil_interval"]],
            ],
            "strict_normalized_lambda_lower":q(TARGET_EIGEN_FLOOR),
            "exact_raw_diagonal_dominance_margin":q(raw_margin),
            "exact_normalized_diagonal_dominance_margin":q(normal_margin),
            "exact_raw_second_Schur_pivot_lower":q(schur_margin),
            "first_diagonal_reused_from":"MathOS PR #94, full pole/prime2/gamma enclosure",
            "cross_archimedean_formula":"-int_0^2 exp(x/2)/(exp(x)-exp(-x)) h0(|x-1|) dx; zero h_cross(0), flat endpoint",
            "uses_any_nontrivial_zeta_zero_locations":False,
        },
        "assurance":{
            "first_2x2_LF_core_Gram_certified":True,
            "all_finite_LF_core_Gram_PSD":False,
            "all_admissible_test_functions_positive":False,
            "Riemann_hypothesis_proved":False,
            "global_positive_Weil_Hilbert_completion":False,
            "independently_peer_or_formally_verified":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gamma-panels",type=int,default=GAMMA_PANELS)
    p.add_argument("--covariance-panels",type=int,default=COVARIANCE_PANELS)
    p.add_argument("--prime-panels",type=int,default=PRIME_PANELS)
    p.add_argument("--pole-panels",type=int,default=POLE_PANELS)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        r=audit(args.gamma_panels,args.covariance_panels,
                args.prime_panels,args.pole_panels)
    except (ValueError,ArithmeticError) as exc:
        p.error(str(exc))
    payload=json.dumps(r,sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
