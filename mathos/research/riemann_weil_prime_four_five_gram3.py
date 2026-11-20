"""TECT-X: actual compact Weil 3x3 with prime powers 2, 4 and 5.

Use three translates phi(8*(x-r)) for r=0, 3/4, 3/2.
The short cross spacing 3/4 (twice) has prime 2, while the new long
cross spacing 3/2 has exactly n=4 and n=5 (Lambda(4)=log 2,
Lambda(5)=log 5). Each matrix entry includes its exact arithmetic
pole, prime-power and archimedean terms. Rational-box mpmath.iv
enclosures and rational Gershgorin/interval LDL check a strict
positive spectral floor on this FIXED three-dimensional test span.

No Riemann hypothesis proof or uniform all-window positivity.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from mpmath import iv
from mathos.research.riemann_weil_prime_two_interval import (
    H, D, F, I, phi, Kbox, out, audit as two_audit,
)
from mathos.research.riemann_weil_certified_scalar import _rational_bound
from mathos.research.riemann_weil_generalized_schur import _ldl_intervals

LONG_SPACING=Fraction(3,2)
CENTERS=(Fraction(0), D, LONG_SPACING)
MIN_EIGEN=Fraction(1,200)
VALID_PANELS=(256,512)


def _rational_log_bounds(n: int) -> tuple[Fraction,Fraction]:
    """Directed interval log with exact rational outward 16-digit bounds."""
    if type(n) is not int or n<2:
        raise ValueError("n>=2 required")
    l,h=out(iv.log(n),16)
    return Fraction(l),Fraction(h)


def _prime_support_inventory() -> dict:
    """Classical log n support gate; rigorously recognize n=2,4,5."""
    # Off-diagonal support positive [spacing-1/4,spacing+1/4].
    # log(2) in (1/2,1), log(3)<5/4, log(6)>7/4:
    boundaries={}
    for n in (2,3,4,5,6):
        boundaries[n]=_rational_log_bounds(n)
    if not (
        Fraction(1,2)<boundaries[2][0] and boundaries[2][1]<1
        and boundaries[3][1]<Fraction(5,4)
        and Fraction(5,4)<boundaries[4][0]<boundaries[4][1]<Fraction(7,4)
        and Fraction(5,4)<boundaries[5][0]<boundaries[5][1]<Fraction(7,4)
        and boundaries[6][0]>Fraction(7,4)
    ):
        raise ArithmeticError("prime-support logarithmic inequalities not certified")
    return {
        "short_spacing":"3/4",
        "short_support":["1/2","1/1"],
        "short_prime_powers":[2],
        "long_spacing":"3/2",
        "long_support":["5/4","7/4"],
        "long_prime_powers":[4,5],
        "log_intervals":{str(n):[str(x) for x in pair]
                         for n,pair in boundaries.items()},
        "no_nontrivial_zeta_zero_data":True,
    }


def _prime_convolution_interval(spacing: Fraction,n: int,panels: int) -> object:
    """Evaluate h_delta(log n) by complete rational-box range integral."""
    loglo,loghi=_rational_log_bounds(n)
    step=2*H/panels
    total=iv.mpf(0)
    for j in range(panels):
        tl=-H+j*step
        tr=tl+step
        # h_delta(log n)=int phi(t)phi(t+spacing-log n)dt
        total+=phi(tl,tr)*phi(tl+spacing-loghi,tr+spacing-loglo)*F(step)
    return total


def _prime_cross_long(panels: int) -> tuple[object,dict]:
    """Only 4 (Lambda=log2) and 5 (Lambda=log5) contribute."""
    inventory=_prime_support_inventory()
    total=iv.mpf(0)
    components={}
    for n,p in ((4,2),(5,5)):
        term=-iv.log(p)/iv.sqrt(n)*_prime_convolution_interval(
            LONG_SPACING,n,panels)
        total+=term
        components[str(n)]={"von_mangoldt_base":p,"interval":out(term)}
    return total,components


def _arch_cross_long(panels: int) -> object:
    """Full nonzero nonsingular gamma cross term as validated 2D integral."""
    step=2*H/panels
    boxes=[]
    for i in range(panels):
        l=-H+i*step
        boxes.append((l,l+step,phi(l,l+step)))
    total=iv.mpf(0)
    for sl,sr,p in boxes:
        for tl,tr,q in boxes:
            total+=p*q*Kbox(LONG_SPACING+sl-tr,LONG_SPACING+sr-tl)*F(step*step)
    return -total


def _symm_matrix(d: object,c: object,e: object) -> list[list[object]]:
    """Symmetric Toeplitz 3x3 entries from arithmetic, not fitted values."""
    return [[d,c,e],[c,d,c],[e,c,d]]


def audit(panels: int=256) -> dict:
    if type(panels) is not int or panels not in VALID_PANELS:
        raise ValueError("panels must be 256 or 512")
    iv.dps=45
    old=two_audit(panels)
    dlow,dhigh=map(Fraction,old["arithmetic"]["diagonal_Weil_entry"])
    clow,chigh=map(Fraction,old["arithmetic"]["cross_Weil_entry"])
    d=I(dlow,dhigh)
    c=I(clow,chigh)
    poldlow,poldhigh=map(Fraction,old["arithmetic"]["pole_diagonal"])
    pold=I(poldlow,poldhigh)
    arch_long=_arch_cross_long(panels)
    prime_long,prime_parts=_prime_cross_long(4*panels)
    pole_long=pold*(iv.exp(F(LONG_SPACING)/2)+iv.exp(-F(LONG_SPACING)/2))/2
    e=pole_long+arch_long+prime_long
    M=_symm_matrix(d,c,e)
    vals=[(dlow, max(abs(clow),abs(chigh))+max(abs(_rational_bound(e,False)),abs(_rational_bound(e,True)))),
          (dlow, 2*max(abs(clow),abs(chigh))),
          (dlow, max(abs(clow),abs(chigh))+max(abs(_rational_bound(e,False)),abs(_rational_bound(e,True))))]
    gersh=min(left-right for left,right in vals)
    if gersh<=MIN_EIGEN:
        raise ArithmeticError("certified three-dimensional Gershgorin floor not positive")
    _,pivots=_ldl_intervals(M)
    if not all(_rational_bound(p,False)>0 for p in pivots):
        raise ArithmeticError("interval LDL did not prove all three pivots positive")
    return {
        "schema":"mathos_tectx_weil_prime_four_five_gram3/1",
        "status":"FIXED_PRIME_2_4_5_3D_WEIL_GRAM_POSITIVE_GLOBAL_RH_OPEN",
        "test_family":{
            "bump":"phi(u)=exp(1-1/(1-u^2)) for |u|<1, else 0",
            "functions":["phi(8*x)","phi(8*(x-3/4))","phi(8*(x-3/2))"],
            "centers":["0/1","3/4","3/2"],
            "every_direction_is_compactly_supported":True,
        },
        "arithmetic":{
            "validated_box_panels":panels,
            "prime_support":_prime_support_inventory(),
            "new_long_pole_interval":out(pole_long),
            "new_long_archimedean_interval":out(arch_long),
            "new_long_prime_interval":out(prime_long),
            "new_prime_power_components":prime_parts,
            "new_long_weil_entry":out(e),
            "diagonal_weil_entry":out(d),
            "short_weil_cross_entry":out(c),
            "complete_real_symmetric_gram":[[out(x) for x in row] for row in M],
            "strict_lambda_min_lower":"1/200",
            "gershgorin_rational_lower":str(gersh),
            "interval_LDL_pivots":[out(p) for p in pivots],
            "prime_power_cross_terms_are_actual_nonzero":True,
            "uses_zeta_zeros_as_input":False,
        },
        "trust_boundary":{
            "fixed_3D_positive_definite":True,
            "all_dimension_compact_bump_Weil_positivity":False,
            "global_Weil_positivity":False,
            "complete_positive_Weil_Hilbert_space":False,
            "Riemann_hypothesis_proved":False,
            "formal_proof_assistant_verified":False,
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
    payload=json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
