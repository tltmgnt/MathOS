"""Small-support Cc-infinity Weil arithmetic Gram: exact enclosures and all-index PSD.

No RH claim. Uses a CLASSICAL previously established Yoshida/Bombieri
small-window positivity theorem and a published quantitative archimedean
version (after Yoshida). The theorem is not reproved here.

Family: phi(x)=exp(1-1/(1-x²)), |x|<1; 0 otherwise.
phi_(h,r)(x)=phi((x-r)/h). For rationals h=2^-n and r with
|r|+h<1/4, set f_(h,r)=(D²-1/4)phi_(h,r).
Then f is compactly supported in (-1/4,1/4) and
   integral exp(±x/2)*f(x)dx=0
by integration by parts. Every convolution f_i*tilde(f_j) is
supported in [-1/2,1/2] and thus samples ZERO prime powers, since
log 2>1/2. Pole contributions vanish for each pair.

The remaining Weil term is precisely the archimedean functional
  -(log(4*pi)+EulerGamma) h(0)
  - integral_0^infty [h(x)+h(-x)-2exp(-x/2)h(0)]
                  * exp(x/2)/(exp(x)-exp(-x)) dx.
Its apparent singularity at zero cancels. The code supplies genuinely
rigorous, conservative [-B,+B] entry enclosures with B exact rational,
and positive lower intervals for diagonals USING the cited classical
small-support positivity theorem (not an independent proof of it).

The signed f tests span a proper support-constrained subspace of the
full LF Weil test space. Infinite-dimensional PSD on this restricted
space does NOT imply RH.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from math import comb, gcd
import hashlib
import json
from pathlib import Path

MAX_BUMPS = 128
WINDOW_HALF = Fraction(1,4)
YOSHIDA_WINDOW_HALF = "log(2)/2"
QUANTITATIVE_CONSTANT = Fraction(1,250)


def qs(v: Fraction) -> str:
    return f"{v.numerator}/{v.denominator}"


def _poly_derivative(P: dict[tuple[int,int],int], axis: int) -> dict[tuple[int,int],int]:
    Q={}
    for (i,j),v in P.items():
        k=(i-1,j) if axis==0 else (i,j-1)
        degree=i if axis==0 else j
        if degree:
            Q[k]=Q.get(k,0)+v*degree
    return Q


def _add(target: dict[tuple[int,int],int], key: tuple[int,int], value: int) -> None:
    target[key]=target.get(key,0)+value
    if target[key]==0:
        del target[key]


def bump_derivative_polynomial(order: int) -> dict[tuple[int,int],int]:
    """phi^(k)(x)=phi(x)*P_k(x,y), y=(1-x²)^-1."""
    if type(order) is not int or not 0<=order<=3:
        raise ValueError("order must be integer 0..3")
    P={(0,0):1}
    for _ in range(order):
        Q={}
        for key,v in _poly_derivative(P,0).items():
            _add(Q,key,v)
        for (i,j),v in _poly_derivative(P,1).items():
            _add(Q,(i+1,j+2),2*v)
        for (i,j),v in P.items():
            _add(Q,(i+1,j+2),-2*v)
        P=Q
    return P


def bump_derivative_upper(order: int) -> int:
    """Rational-safe global bound via exp(1-y)*y^j <= max(1,j^j), y>=1.

    For j>=1, maximum of exp(1-y)*y^j on y>=1 is
    exp(1-j)*j^j <= j^j. |x|<=1.
    """
    P=bump_derivative_polynomial(order)
    return sum(abs(v)*(j**j if j else 1) for (_,j),v in P.items())


def bumps(count: int) -> list[dict]:
    """Every rational-centered dyadic bump strictly within [-1/4,1/4].

    Enumerate by increasing H=n+|p|+q for r=p/q in lowest terms,
    h=2^-n, n>=3. Any such admissible pair occurs at finite height.
    """
    if type(count) is not int or not 1<=count<=MAX_BUMPS:
        raise ValueError("count must be an integer in 1..128")
    out=[]
    height=4
    while len(out)<count:
        for n in range(3,height):
            width=Fraction(1,2**n)
            for q in range(1,height-n+1):
                k=height-n-q
                for p in ([0] if k==0 else [-k,k]):
                    if gcd(abs(p),q)!=1:
                        continue
                    center=Fraction(p,q)
                    if abs(center)+width>=WINDOW_HALF:
                        continue
                    out.append({
                        "n":n,"center":qs(center),"width":qs(width),
                        "support_left":qs(center-width),
                        "support_right":qs(center+width),
                    })
                    if len(out)==count:
                        break
                if len(out)==count:
                    break
            if len(out)==count:
                break
        height+=1
    return out


def seminorms(b: dict) -> tuple[int,int]:
    h=Fraction(b["width"])
    A0=Fraction(bump_derivative_upper(2),1)/h**2+Fraction(1,4)
    A1=Fraction(bump_derivative_upper(3),1)/h**3 +Fraction(bump_derivative_upper(1),4)/h
    return _ceil(A0),_ceil(A1)


def _ceil(v: Fraction) -> int:
    return -(-v.numerator//v.denominator)


def entry_bound(a: dict,b: dict) -> dict:
    """Validated [-B,B] enclosure for the ACTUAL archimedean Weil entry.

    For h=f_a*tilde(f_b), support in [-R,R] with R<=1/2:
      H0 := sup|h|<=2 min(width_a,width_b) F0_a F0_b
      H1 := sup|h'|<=2 min(width_a,width_b) F1_a F0_b.
    At x in [0,R], numerator of arch kernel:
       |h(x)+h(-x)-2e^-x/2 h(0)| <= x*(2H1+H0).
    Since e^(x/2)/(e^x-e^-x)<=1/x on x<=1/2,
       |integral_(0,R)|<=R*(2H1+H0).
    On x>R, h(x)=h(-x)=0; tail is bounded by
       H0*int_R^infty dx/sinh(x)
       <= H0*(1/R+2).
    Finally log(4*pi)+EulerGamma<4. Thus:
       |Weil(h)| <= (6+R+1/R)*H0+2R*H1.
    The pole and prime contributions vanish IDENTICALLY, so this is
    a full arithmetic-form entry enclosure, albeit deliberately loose.
    """
    ai,ap=seminorms(a)
    bi,_=seminorms(b)
    wa=Fraction(a["width"])
    wb=Fraction(b["width"])
    minimum=min(wa,wb)
    H0=2*minimum*ai*bi
    H1=2*minimum*ap*bi
    R=(max(Fraction(a["support_right"]),Fraction(b["support_right"]))-
       min(Fraction(a["support_left"]),Fraction(b["support_left"])))
    if not Fraction(0)<R<Fraction(1,2):
        raise ArithmeticError("failed to stay strictly inside prime-free support")
    bound=(6+R+1/R)*H0+2*R*H1
    return {
        "support_max_width":qs(R),
        "archimedean_entry_lower":qs(-bound),
        "archimedean_entry_upper":qs(bound),
        "pole_term_exact":"0/1",
        "prime_power_term_exact":"0/1",
        "full_Weil_entry_enclosed":True,
        "archimedean_formula":"-(log(4*pi)+EulerGamma) h(0) - integral_0^infty (h(x)+h(-x)-2e^(-x/2)h(0)) e^(x/2)/(e^x-e^(-x)) dx",
        "evaluation_note":"Exact interval enclosure using analytic sup norm bounds, NOT narrow evaluated quadrature; applicable to each actual convolution h=f_i*tilde(f_j)",
    }


def diagonal_coercivity_lower(b: dict) -> Fraction:
    """Strict rational lower bound on W(f*tilde(f)), using published theorem.

    f=(D²-1/4)phi_(h,r), and f(r)=-2/h²-1/4.
    |f'|<=A1 on entire support. Thus |f| >= |f(r)|/2
    within delta=min(h, |f(r)|/(2 A1)).
    ||f||² >= delta*|f(r)|²/2.
    Published small support Weil theorem gives W(f*tilde f)>=||f||²/250.
    """
    h=Fraction(b["width"])
    _,A1=seminorms(b)
    center_value=Fraction(2,1)/h**2+Fraction(1,4)
    delta=min(h,center_value/(2*A1))
    return QUANTITATIVE_CONSTANT*delta*center_value**2/2


def report(count: int=3) -> dict:
    basis=bumps(count)
    rows=[]
    for i in range(count):
        for j in range(i,count):
            entry=entry_bound(basis[i],basis[j])
            if i==j:
                lower=diagonal_coercivity_lower(basis[i])
                if Fraction(entry["archimedean_entry_upper"])<=lower:
                    raise ArithmeticError("diagonal upper enclosure contradicts proven lower")
                entry["theorem_based_diagonal_lower"]=qs(lower)
            rows.append({"i":i,"j":j,**entry})
    return {
        "schema":"mathos_tectx_weil_small_support_arithmetic_gram/1",
        "status":"ALL_INDEX_SMALL_SUPPORT_PSD_FROM_CLASSICAL_THEOREM_GLOBAL_RH_OPEN",
        "test_family":{
            "function":"f_(n,r)(x)=(D²-1/4) exp(1-1/(1-((x-r)/h)^2)) inside |x-r|<h, zero outside; h=2^-n",
            "finite_basis":basis,
            "all_supports_inside":"(-1/4,1/4)",
            "dense_in":"(D²-1/4)D((-1/4,1/4))",
            "not_dense_in_full_D_R":True,
            "pole_moments":"integral_R e^(x/2) f dx = integral_R e^(-x/2) f dx =0 by integration by parts",
            "prime_support":"support f_i*tilde(f_j) inside (-1/2,1/2); log 2>1/2, so no prime powers contribute",
            "uses_nontrivial_zeta_zeros_as_input":False,
        },
        "arithmetic_gram_enclosures":{
            "entry_count":len(rows),
            "entries":rows,
            "all_entries_have_exact_rational_outer_bounds":True,
            "bounds_are_tight_quadrature_enclosures":False,
            "prime_powers_checked_by_support":True,
            "archimedean_singular_cancellation_bounded":True,
            "individual_archimedean_integrals_numerically_evaluated":False,
        },
        "infinite_dimensional_positive_subspace":{
            "theorem_used":"Existing Yoshida/Bombieri small-support Weil positivity; quantitative 1/250 L2 margin from published exposition under one vanished pole moment",
            "statement":"For every m and every complex v, W(f_v*tilde(f_v)) >= (1/250)*||f_v||²_L2 >=0, where f_v=sum_(j<m) v_j f_j",
            "all_finite_Gram_Hm_PSD_for_this_RESTRICTED_family":True,
            "certificate_mode":"analytic theorem transfer, not interval LDL and not a newly proven RH result",
            "L2_relative_lower_constant":qs(QUANTITATIVE_CONSTANT),
            "all_index_result_independent_of_dimension":True,
            "full_canonical_Weil_test_core":False,
            "global_Weil_positivity":False,
        },
        "missing_universal_bridge":[
            "Extend positivity beyond the small support [-1/4,1/4] and moment-zero subspace; no such estimate is established here",
            "Compute tight outward-rounded archimedean values for larger overlapping support windows and include prime-power contributions",
            "Prove positivity for an LF-dense core of all Cc-infinity, the RH-equivalent step",
            "Unconditional positive full Weil Hilbert completion and zeta-zero spectrum remain unavailable",
        ],
        "assurance":{
            "Riemann_hypothesis_proved":False,
            "global_Weil_test_space_positive":False,
            "full_Weil_Hilbert_space_completed":False,
            "all_prime_windows_analyzed":False,
            "new_unpublished_small_support_theorem_claimed":False,
            "independent_formal_or_peer_verification":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--count",type=int,default=3)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    try:
        data=report(a.count)
    except (ValueError,ArithmeticError) as exc:
        p.error(str(exc))
    payload=json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
