"""TECT-X actual four-dimensional compact Weil Gram: prime powers 2,4,5,8,9,11.

Four translated Cc-infinity bumps at 0,3/4,3/2,9/4. The new
separation 9/4 produces actual arithmetic prime-power contributions
n=8,9,11; no others in [exp(2),exp(5/2)]. The neighboring 3/4
and intermediate 3/2 entries retain the previously certified n=2
and n=4,5 terms. A real symmetric Toeplitz 4x4 interval Weil Gram
encloses all poles, prime powers, and full archimedean distribution
through validated rational-box integration.

Both a positive interval LDL decomposition and a strictly positive
Gershgorin lower bound are required; every failure is fail-closed.
This is a FIXED finite 4D result; no RH, general positivity, or
full Weil-Hilbert construction.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from mpmath import iv
from mathos.research.riemann_weil_prime_two_interval import (
    H, D, F, I, phi, Kbox, out,
)
from mathos.research.riemann_weil_prime_four_five_gram3 import (
    audit as three_audit, _rational_log_bounds,
)
from mathos.research.riemann_weil_certified_scalar import _rational_bound
from mathos.research.riemann_weil_generalized_schur import _ldl_intervals

NEW_CENTER = Fraction(9,4)
CENTERS=(Fraction(0),D,Fraction(3,2),NEW_CENTER)
SPECTRAL_FLOOR=Fraction(1,10000)
VALID_PANELS=(256,512)
NEW_PRIME_POWERS=((8,2),(9,3),(11,11))


def _fourth_prime_support() -> dict:
    """Exact logarithmic support separation: log7<2<log8,log9,log11<5/2<log13."""
    values={n:_rational_log_bounds(n) for n in (7,8,9,10,11,12,13)}
    if not (
        values[7][1] < 2
        and all(Fraction(2) < values[n][0] <= values[n][1] < Fraction(5,2)
                for n in (8,9,10,11,12))
        and values[13][0] > Fraction(5,2)
    ):
        raise ArithmeticError("incorrect arithmetic prime-power support inventory")
    # n=10 and n=12 are not prime powers; Von Mangoldt Λ(n)=0.
    return {
        "new_long_separation": "9/4",
        "support": ["2/1","5/2"],
        "integer_candidates": [8,9,10,11,12],
        "actual_prime_powers": [8,9,11],
        "vanishing_mangoldt_candidates": [10,12],
        "von_mangoldt_bases": {"8":2,"9":3,"11":11},
        "log_rational_intervals": {str(n):[str(q) for q in values[n]]
                                   for n in values},
        "all_zeros_not_used_as_input":True,
    }


def _prime_convolution(s: Fraction, n: int, panels: int) -> object:
    """Actual convolution h_s(log n) via outward interval range integration."""
    lo,hi=_rational_log_bounds(n)
    step=2*H/panels
    total=iv.mpf(0)
    for j in range(panels):
        left=-H+j*step
        right=left+step
        total+=phi(left,right)*phi(left+s-hi,right+s-lo)*F(step)
    return total


def _prime_cross(panels: int) -> tuple[object,dict]:
    total=iv.mpf(0)
    parts={}
    for n,p in NEW_PRIME_POWERS:
        value=-iv.log(p)/iv.sqrt(n)*_prime_convolution(NEW_CENTER,n,panels)
        if _rational_bound(value,True)>=0:
            raise ArithmeticError(f"missing strictly negative n={n} prime term")
        total+=value
        parts[str(n)]={"base_prime":p,"interval":out(value)}
    return total,parts


def _arch_cross(panels: int) -> object:
    """Entire nonsingular archimedean long-distance integral in rational boxes."""
    step=2*H/panels
    boxes=[(-H+i*step,-H+(i+1)*step,
            phi(-H+i*step,-H+(i+1)*step)) for i in range(panels)]
    total=iv.mpf(0)
    for sl,sr,p in boxes:
        for tl,tr,q in boxes:
            total+=p*q*Kbox(NEW_CENTER+sl-tr,NEW_CENTER+sr-tl)*F(step*step)
    return -total


def _matrix(d: object,c: object,e: object,g: object) -> list[list[object]]:
    return [[d,c,e,g],[c,d,c,e],[e,c,d,c],[g,e,c,d]]


def audit(panels: int=256) -> dict:
    if type(panels) is not int or panels not in VALID_PANELS:
        raise ValueError("panels must be 256 or 512")
    iv.dps=45
    prior=three_audit(panels)
    cert=prior["arithmetic"]
    d=I(*[Fraction(x) for x in cert["diagonal_weil_entry"]])
    c=I(*[Fraction(x) for x in cert["short_weil_cross_entry"]])
    e=I(*[Fraction(x) for x in cert["new_long_weil_entry"]])
    # Use previous truly certified base moment, not a rounded point estimate.
    from mathos.research.riemann_weil_prime_two_interval import audit as two_audit
    prior_two=two_audit(panels)
    base_pole=I(*[Fraction(x) for x in prior_two["arithmetic"]["pole_diagonal"]])
    pole=base_pole*(iv.exp(F(NEW_CENTER)/2)+iv.exp(-F(NEW_CENTER)/2))/2
    gamma=_arch_cross(panels)
    primes,prime_parts=_prime_cross(4*panels)
    g=pole+gamma+primes
    M=_matrix(d,c,e,g)
    def abs_hi(x: object) -> Fraction:
        return max(abs(_rational_bound(x,False)),abs(_rational_bound(x,True)))
    rows=[abs_hi(c)+abs_hi(e)+abs_hi(g),
          2*abs_hi(c)+abs_hi(e),
          2*abs_hi(c)+abs_hi(e),
          abs_hi(c)+abs_hi(e)+abs_hi(g)]
    gersh=_rational_bound(d,False)-max(rows)
    # Independently check the strict shifted G-kappa I>0 via LDL.
    shift=I(SPECTRAL_FLOOR,SPECTRAL_FLOOR)
    shifted=[[M[i][j]-shift if i==j else M[i][j]
              for j in range(4)] for i in range(4)]
    _,pivots=_ldl_intervals(shifted)
    if gersh <= SPECTRAL_FLOOR:
        raise ArithmeticError("rational Gershgorin 4D floor is inconclusive")
    if not all(_rational_bound(v,False)>0 for v in pivots):
        raise ArithmeticError("shifted 4D interval LDL did not certify positive pivots")
    return {
        "schema":"mathos_tectx_weil_prime_8_9_11_gram4/1",
        "status":"FIXED_PRIME_ACTIVE_4D_WEIL_GRAM_CERTIFIED_GLOBAL_RH_OPEN",
        "basis":{
            "functions":[f"phi(8*(x-{p}))" for p in ("0","3/4","3/2","9/4")],
            "centers":["0/1","3/4","3/2","9/4"],
            "all_compactly_supported":True,
        },
        "arithmetical_certification":{
            "box_panels":panels,
            "new_prime_support":_fourth_prime_support(),
            "new_prime_power_parts":prime_parts,
            "new_pole_interval":out(pole),
            "new_archimedean_interval":out(gamma),
            "new_prime_total_interval":out(primes),
            "new_full_weil_entry":out(g),
            "full_symmetric_weil_matrix":[[out(v) for v in row] for row in M],
            "verified_gershgorin_floor_exact":str(gersh),
            "claimed_strict_lambda_lower":"1/10000",
            "shifted_G_minus_kappa_I_LDL_pivots":[out(v) for v in pivots],
            "no_zeta_zeros_as_input":True,
        },
        "assurance":{
            "actual_compact_four_dimensional_Weil_PSD":True,
            "all_dimensional_Weil_PSD":False,
            "full_positive_Weil_Hilbert_space":False,
            "Riemann_hypothesis_proved":False,
            "formally_verified":False,
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
    except (ValueError,ArithmeticError) as exc:
        p.error(str(exc))
    payload=json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
