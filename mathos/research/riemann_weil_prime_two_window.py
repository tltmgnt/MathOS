"""TECT-X: rigorous arithmetic Weil 2x2 compact-bump PRIME-TWO window.

Two real C_c^infinity bumps phi((x-r)/h) of width h=1/8 centered
r0=0 and r1=3/4. With tilde(f)(x)=f(-x), their convolution
h10=f_1*tilde(f_0) is supported in [1/2,1], and the conjugate
h01 in [-1,-1/2]. Exactly prime 2 contributes to the off-diagonal
Weil entry: primes n>=3 lie outside these intervals. Diagonal prime
terms are zero.

The actual Weil arithmetic off-diagonal entry has nonzero pole,
prime-2 and archimedean terms. All three receive exact rational
enclosures, including strict negative bounds for prime and gamma
components. No zero ordinates or RH assumptions are used.

This is a restricted two-direction arithmetic calibration, NOT an
infinite-dimensional PSD theorem, a tight numeric integration,
a new RH proof or a completed Weil Hilbert space.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from mathos.research.riemann_weil_small_support_gram import (
    bump_derivative_upper,
)

WIDTH = Fraction(1,8)
CENTERS = (Fraction(0),Fraction(3,4))
MAX_SUPPORTED_COUNT = 2
L2_MIN_PRIME_CONV = Fraction(2,225)
PRIME2_LOWER_MAGNITUDE = Fraction(23,5625)
ARCH_LOWER_MAGNITUDE = Fraction(1,33750)


def q(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def log2_bounds(terms: int=4) -> tuple[Fraction,Fraction]:
    """Exact rational enclosure via log2=2*atanh(1/3) series.

    Tail for k>=terms bounded by
      (2/(2*terms+1))*3^(-2*terms-1)/(1-1/9).
    """
    if type(terms) is not int or not 1<=terms<=32:
        raise ValueError("terms must be 1..32")
    partial=sum((Fraction(2, (2*k+1)*3**(2*k+1))
                 for k in range(terms)),Fraction(0))
    tail=Fraction(2,2*terms+1)*Fraction(1,3**(2*terms+1))*Fraction(9,8)
    return partial,partial+tail


def support_pair(center_a: Fraction,center_b: Fraction) -> tuple[Fraction,Fraction]:
    if not isinstance(center_a,Fraction) or not isinstance(center_b,Fraction):
        raise ValueError("centers must be rational")
    return center_a-center_b-2*WIDTH,center_a-center_b+2*WIDTH


def prime_power_support_inventory() -> dict:
    low,high=log2_bounds()
    if not (Fraction(69,100)<low<high<Fraction(70,100)):
        raise ArithmeticError("log2 rational enclosure failed")
    # log3 = 2*atanh(1/2)>2*(1/2+1/(3*2^3))=13/12>1.
    log3_lower=Fraction(13,12)
    if log3_lower<=1:
        raise ArithmeticError("log3 rational lower inequality failed")
    spans={}
    for i,c in enumerate(CENTERS):
        for j,d in enumerate(CENTERS):
            left,right=support_pair(c,d)
            spans[f"{i}{j}"]={"support":[q(left),q(right)],
                               "prime2_plus":left<low and right>high,
                               "prime2_minus":left< -high and right>-low,
                               "any_prime_power_ge_3":False}
            if not (max(abs(left),abs(right))<=1):
                raise ArithmeticError("unexpected prime-support enlargement")
    return {
        "log2_lower_rational":q(low),
        "log2_upper_rational":q(high),
        "log3_strict_lower_rational":q(log3_lower),
        "spans":spans,
        "only_possible_prime_power":2,
        "actual_nonzero_prime_pairs":["01","10"],
        "diagonals_prime_free":True,
    }


def off_diagonal_certificate() -> dict:
    """Complete *actual* Weil off-diagonal entry via explicit rational bounds.

    h10 support [1/2,1], h10>=0. On x in [69/100,70/100],
    t in [72/100,74/100], the two bumps have scaled coordinate
    absolute value <1/2, hence phi>=exp(-1/3)>2/3.
    Therefore h10(x)> (2/100)*(2/3)^2 = 2/225.

    Prime contribution is -log2/sqrt2*h10(log2)<-23/5625.
    Archimedean contribution is -int_[1/2,1]
        h10(x)* exp(x/2)/(exp(x)-exp(-x)) dx.
    On x in [.69,.70], kernel>1/3, so arch<-1/33750.

    Polar contribution =int h10(x)(e^(x/2)+e^(-x/2))dx.
    Since h10<=1/4 and supp length<=1/2 and e^(.5)<2,
    0<pole<1/2. The prime magnitude <1/4, arch magnitude
    <= (1/4)*integral_[.5,1] 1/x dx <1/4, so
      -1/2 < total < 1/2-23/5625-1/33750.
    This is not a PSD test; it is an independently bounded
    prime-active arithmetic entry.
    """
    inv=prime_power_support_inventory()
    if not inv["spans"]["10"]["prime2_plus"]:
        raise ArithmeticError("prime 2 missing from intended cross term")
    if bump_derivative_upper(0)!=1:
        raise ArithmeticError("wrong normalization for bump sup")
    if not (bump_derivative_upper(1)>=8):
        raise ArithmeticError("first derivative upper underestimates bump")
    lower=-Fraction(1,2)
    upper=Fraction(1,2)-PRIME2_LOWER_MAGNITUDE-ARCH_LOWER_MAGNITUDE
    return {
        "convolution":"h10=phi((x-3/4)/(1/8))*tilde(phi(x/(1/8)))",
        "support":["1/2","1/1"],
        "convolution_at_all_x_in_69_100_to_70_100_strict_lower":q(L2_MIN_PRIME_CONV),
        "at_log2_strict_lower":q(L2_MIN_PRIME_CONV),
        "pole_lower":"0/1",
        "pole_upper":"1/2",
        "prime2_lower":"-1/4",
        "prime2_strict_upper":q(-PRIME2_LOWER_MAGNITUDE),
        "archimedean_lower":"-1/4",
        "archimedean_strict_upper":q(-ARCH_LOWER_MAGNITUDE),
        "full_Weil_cross_lower":q(lower),
        "full_Weil_cross_strict_upper":q(upper),
        "formula":"pole - log(2)/sqrt(2)*h10(log 2) - integral_(1/2)^1 h10(x)*e^(x/2)/(e^x-e^(-x))dx",
        "arithmetic_cross_term_computed_from_zeros":False,
        "individual_integrals_evaluated_to_high_precision":False,
    }


def diagonal_entry_bound() -> dict:
    """For both translated bumps: h_ii support [-1/4,1/4].

    F0<=1; F1<=8/h=64. H0<=2h=1/4, H1<=2hF1=16.
    R=1/4. Arch bound from regularized W infinity:
      |arch|< (6+R+1/R)*H0 + 2R*H1 =169/16.
    Polar absolute < 2*2*(length 1/2)*H0 =1/2.
    Prime contribution zero. So |W_ii|<177/16.
    """
    F0=bump_derivative_upper(0)
    F1=bump_derivative_upper(1)/WIDTH
    H0=2*WIDTH*F0*F0
    H1=2*WIDTH*F1*F0
    R=2*WIDTH
    arch=(6+R+1/R)*H0+2*R*H1
    if arch!=Fraction(169,16):
        raise ArithmeticError("diagonal arch bound mismatch")
    upper=arch+Fraction(1,2)
    if upper!=Fraction(177,16):
        raise ArithmeticError("diagonal Weil bound mismatch")
    return {
        "prime_power_exact":"0/1",
        "archimedean_abs_upper":q(arch),
        "pole_abs_upper":"1/2",
        "full_diagonal_lower":q(-upper),
        "full_diagonal_upper":q(upper),
        "diagonal_positivity_proved":False,
    }


def report() -> dict:
    inv=prime_power_support_inventory()
    cross=off_diagonal_certificate()
    diag=diagonal_entry_bound()
    matrix=[
        [diag,{"cross":cross}],
        [{"cross":cross},diag],
    ]
    return {
        "schema":"mathos_tectx_weil_prime_two_window/1",
        "status":"PRIME_TWO_ACTUAL_WEIL_CROSS_ENCLOSED_NOT_PSD_RH_OPEN",
        "basis":{
            "bump":"phi(x)=exp(1-1/(1-x^2)), |x|<1; 0 otherwise",
            "functions":["phi(8*x)","phi(8*(x-3/4))"],
            "support_windows":["[-1/8,1/8]","[5/8,7/8]"],
            "support_not_inside_previous_yoshida_small_window":True,
            "uses_zeta_zeros":False,
        },
        "prime_power_support":inv,
        "exact_rational_arithmetic_enclosures":{
            "diagonal":diag,
            "off_diagonal":cross,
            "real_symmetric_two_by_two":True,
            "all_pole_prime_and_archimedean_components_included":True,
            "numerically_tight_archimedean_integral":False,
            "matrix_psd_certified":False,
        },
        "remaining":[
            "Tight certified evaluation of the full archimedean integral and pole moments for prime-active pairs",
            "Narrow independent enclosures of both diagonal terms and cross term",
            "Interval LDL positive/negative test on the actual prime-active two-dimensional Weil Gram",
            "Any all-dimension positivity theorem for a core LF-dense in all Cc-infinity is RH-equivalent and open",
        ],
        "assurance":{
            "matrix_psd_certified":False,
            "global_Weil_positivity":False,
            "full_positive_Weil_Hilbert_completion":False,
            "Riemann_hypothesis_proved":False,
            "independent_formal_proof":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    data=report()
    payload=json.dumps(data,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
