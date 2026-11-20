"""Verified L2-relative Weil generalized eigenvalue and nested Schur certificates.

For q_j=exp(-t²/100)cos(c_j t), centers 0, 1/5, 1/2, compute the
previously enclosed actual Weil Gram G and an independently enclosed
ordinary Gaussian L2 Gram L. Verify strict positivity of G-kappa*L by
interval LDL at each nested dimension 1,2,3, using block Schur
complements. Also certify a rational Rayleigh upper bound on the
smallest generalized eigenvalue.

A synthetic 4x4 Schur extension can test the algebra, but NEVER counts
as a new Weil basis vector. An actual fourth direction requires newly
certified Weil and L2 cross-block enclosures.

No global Weil positivity, unconditional Weil Hilbert completion or RH.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from mpmath import iv

from mathos.research.riemann_weil_certified_gram3 import (
    CENTERS, _gram_intervals,
)
from mathos.research.riemann_weil_certified_scalar import (
    _outward_decimal, _rational_bound,
)

LOWER = Fraction(1,50_000_000)
UPPER = Fraction(1,1_000_000)
UPPER_WITNESS = (1000, 1466, 557)


def _point(f: Fraction) -> object:
    if not isinstance(f,Fraction):
        raise TypeError("exact rational input required")
    return iv.mpf(f.numerator)/f.denominator


def _positive_lower(x: object) -> bool:
    return _rational_bound(x,False)>0


def _negative_upper(x: object) -> bool:
    return _rational_bound(x,True)<0


def _ldl_intervals(M: list[list[object]]) -> tuple[list[list[object]],list[object]]:
    """Interval LDL enclosure, strict positivity mandatory for every pivot."""
    n=len(M)
    if not 1<=n<=8 or any(len(row)!=n for row in M):
        raise ValueError("matrix must be square, dimension 1..8")
    # Hermitian/symmetric input must be explicit, not silently symmetrized.
    for i in range(n):
        for j in range(i+1,n):
            if (_rational_bound(M[i][j],False)!=_rational_bound(M[j][i],False)
                or _rational_bound(M[i][j],True)!=_rational_bound(M[j][i],True)):
                raise ValueError("symmetric entry intervals required")
    lower=[[iv.mpf(0) for _ in range(n)] for _ in range(n)]
    diag=[]
    for i in range(n):
        d=M[i][i]
        for k in range(i):
            d-=lower[i][k]*lower[i][k]*diag[k]
        if not _positive_lower(d):
            raise ArithmeticError(f"uncertified/nonpositive LDL pivot {i}")
        diag.append(d)
        lower[i][i]=iv.mpf(1)
        for j in range(i+1,n):
            value=M[j][i]
            for k in range(i):
                value-=lower[j][k]*diag[k]*lower[i][k]
            lower[j][i]=value/d
    return lower,diag


def verified_schur(M: list[list[object]], old_dim: int) -> dict:
    """Prove M>0 through old positive block and interval Schur complement.

    A=L D L^T. Solve L Y=B, then S=C-Y^T D^-1 Y.
    This interval enclosure holds for EVERY symmetric realization of the
    entry intervals. No accidental numeric (unvalidated) inverse is used.
    """
    n=len(M)
    if type(old_dim) is not int or not 1<=old_dim<n:
        raise ValueError("old_dim must be a positive integer smaller than matrix dimension")
    A=[row[:old_dim] for row in M[:old_dim]]
    L,d=_ldl_intervals(A)
    fresh=n-old_dim
    transformed=[[iv.mpf(0) for _ in range(fresh)] for _ in range(old_dim)]
    for i in range(old_dim):
        for j in range(fresh):
            value=M[i][old_dim+j]
            for k in range(i):
                value-=L[i][k]*transformed[k][j]
            transformed[i][j]=value
    S=[[iv.mpf(0) for _ in range(fresh)] for _ in range(fresh)]
    for i in range(fresh):
        for j in range(i,fresh):
            value=M[old_dim+i][old_dim+j]
            for k in range(old_dim):
                value-=transformed[k][i]*transformed[k][j]/d[k]
            S[i][j]=S[j][i]=value
    _,pivots=_ldl_intervals(S)
    return {
        "old_dim":old_dim,"new_dim":fresh,
        "old_pivots":[_outward_decimal(t,10**14) for t in d],
        "schur_entry_intervals":[[_outward_decimal(t,10**14) for t in row] for row in S],
        "schur_pivots":[_outward_decimal(t,10**14) for t in pivots],
        "all_pivots_positive":True,
    }


def l2_gram_intervals() -> list[list[object]]:
    """Exact Gaussian L2 Gram evaluated with directed interval arithmetic."""
    a=iv.mpf(1)/50
    cs=[_point(t) for t in CENTERS]
    result=[[iv.mpf(0) for _ in range(3)] for _ in range(3)]
    for i,c in enumerate(cs):
        for j in range(i,3):
            d=cs[j]
            value=(iv.sqrt(iv.pi/a)/2 *
                   (iv.exp(-(c-d)**2/(4*a))+iv.exp(-(c+d)**2/(4*a))))
            result[i][j]=result[j][i]=value
    return result


def _linear_combination(M: list[list[object]],
                        N: list[list[object]], kappa: Fraction) -> list[list[object]]:
    n=len(M)
    if not n or len(N)!=n or any(len(row)!=n for row in M+N):
        raise ValueError("incompatible matrices")
    return [[M[i][j]-_point(kappa)*N[i][j] for j in range(n)] for i in range(n)]


def _rayleigh(M: list[list[object]], v: tuple[int,...]) -> object:
    n=len(M)
    if len(v)!=n:
        raise ValueError("wrong Rayleigh witness size")
    val=iv.mpf(0)
    for i in range(n):
        for j in range(n):
            val+=v[i]*v[j]*M[i][j]
    return val


def audit(panels: int = 8192) -> dict:
    if type(panels) is not int or panels not in (8192,16384):
        raise ValueError("supported quadrature counts: 8192 or 16384")
    iv.dps=60
    G,parts=_gram_intervals(panels)
    L=l2_gram_intervals()
    # The reference L2 Gram must itself be provably PD on this basis.
    _,l2_pivots=_ldl_intervals(L)
    shifted=_linear_combination(G,L,LOWER)
    _,shifted_pivots=_ldl_intervals(shifted)
    schur=[verified_schur([row[:n] for row in shifted[:n]],n-1)
           for n in (2,3)]
    # Upper bound for lambda_min(G,L): one exact integer witness v.
    upper_residual=_rayleigh(_linear_combination(G,L,UPPER),UPPER_WITNESS)
    if not _negative_upper(upper_residual):
        raise ArithmeticError("no certified generalized eigenvalue upper bound")
    return {
        "schema":"mathos_tectx_weil_generalized_schur/1",
        "status":"VERIFIED_FIXED_3D_GENERALIZED_GAP_AND_NESTED_SCHUR_GLOBAL_OPEN",
        "basis":{
            "a":"1/50","centers":["0/1","1/5","1/2"],
            "q_c":"exp(-t^2/100)cos(c*t)",
            "G":"exact Weil arithmetic Gram (zeros not inputs)",
            "L":"independent ordinary Gaussian L2 Gram of same test functions",
        },
        "certified_generalized_eigenvalue":{
            "strict_lower":f"{LOWER.numerator}/{LOWER.denominator}",
            "strict_upper":f"{UPPER.numerator}/{UPPER.denominator}",
            "inequality":"lambda_min(L^-1/2 G L^-1/2) > lower and < upper; L is PD on the fixed span",
            "L2_pivots":[_outward_decimal(t,10**14) for t in l2_pivots],
            "shifted_G_minus_kappa_L_pivots":[_outward_decimal(t,10**14) for t in shifted_pivots],
            "integer_Rayleigh_upper_witness":list(UPPER_WITNESS),
            "Rayleigh_G_minus_upper_L_interval":[str(x) for x in _outward_decimal(upper_residual,10**8)],
            "verified_upper_witness_strictly_negative":True,
            "matrix_intervals":[[_outward_decimal(t,10**12) for t in row] for row in G],
            "reference_L2_intervals":[[_outward_decimal(t,10**12) for t in row] for row in L],
        },
        "nested_verified_schur":{
            "basis_sequence":["c=0","c=0,1/5","c=0,1/5,1/2"],
            "extension_results":schur,
            "meaning":"positive old block plus positive interval Schur complement certifies newly adjoined block",
            "fourth_or_higher_dimensional_actual_Weil_blocks_certified":False,
            "conditional_extension_gate":"Require rigorous new G and L block enclosures; apply interval old-block LDL and Schur; reject any pivot whose interval includes zero",
        },
        "analytic_input":{
            "panel_count":panels,
            "source":"the certified Weil 3x3 module supplies exact formula with Binet, Simpson and infinite prime/archimedean tail enclosures",
            "computed_from_zeta_zero_table":False,
            "input_error_parts":{k:_outward_decimal(v,10**18) for k,v in parts.items()},
        },
        "assurance":{
            "fixed_three_span_generalized_positivity_certified":True,
            "dimension_independent_L2_coercivity":False,
            "all_admissible_Weil_tests_positive":False,
            "complete_Weil_Hilbert_space_constructed":False,
            "riemann_hypothesis_proved":False,
            "independent_formal_proof_review":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--panels",type=int,default=8192)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        r=audit(args.panels)
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
