"""Weil all-index LOWER bounds and the actual C_c^infinity test-domain bridge.

No Riemann hypothesis proof. Two mathematically separate results:

A. For the SIGNED trace-class Weil coefficient operator T of PR #82,
   every finite compression T_m has a proved (negative) rational lower
   bound -M*(1-4^-m)/3, M=10000. Assuming the separately certified
   positive leading 3x3 Weil block from PR #78, every m>=3 has the
   sharper all-index lower bound -3*M/64=-1875/4. More generally,
   each newly certified positive leading k block implies a rigorous
   all-m>=k negative spectral floor from the weighted tail. None of
   these estimates tends to 0 with m for a *fixed* certified k.

B. A genuinely domain-correct COUNTABLE family of real compactly
   supported smooth bumps is dense in the LF topology of
   D(R)=C_c^infinity(R). Weil's distribution W is continuous on D(R),
   and (f,g)->W(f*tilde(g)) is jointly continuous on fixed-support
   Frechet pieces. Thus positivity of every finite Gram of this
   countable bump family would IMPLY Weil positivity on all D(R),
   hence RH by the classical Weil criterion. No such all-index
   positivity is established.

The Gaussian spectral tests of PR #82 have noncompact Gaussian inverse
Fourier transforms and cannot serve as members of this compact-support
test-function space. L2-density cannot substitute for D-density.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from math import gcd
import hashlib
import json
from pathlib import Path

from mathos.research.riemann_weil_dense_limit import WEIL_ENTRY_ABS_BOUND

M = WEIL_ENTRY_ABS_BOUND
CERTIFIED_PREFIX = 3
HEAD_SQUARE_WEIGHT = Fraction(21,64)
TAIL_SQUARE_WEIGHT = Fraction(1,192)
SHARP_TAIL_SQRT_RATIONAL = Fraction(1,24)
PREFIX3_LOWER = -Fraction(3*M,64)
MAX_DIMENSION = 4096


def _q(q: Fraction) -> str:
    return f"{q.numerator}/{q.denominator}"


def all_index_lower(dim: int) -> Fraction:
    """No positivity assumptions: T_m >= -M(1-4^-m)/3 I_m.

    For all vectors x of length m:
    |x^T T_m x| <= M*(sum_{j<m} |x_j|2^(-j-1))^2
       <= M*(sum_{j<m} 4^(-j-1))*||x||_2^2.
    """
    if type(dim) is not int or not 0 <= dim <= MAX_DIMENSION:
        raise ValueError("dim must be an integer from 0 through 4096")
    return -Fraction(M,3)*(1-Fraction(1,4**dim))


def certified_prefix3_all_index_lower(dim: int) -> Fraction:
    """For every m>=3, T_m >= -3M/64 I, GIVEN certified G_3>0.

    Decompose into 3D head and tail; the head has nonnegative quadratic
    value, and entrywise |G_ij|<=M controls both cross and tail terms.
    Bound sqrt(S_head*S_tail)<=1/24 using exact rational squares,
    S_tail<=1/192, then use 2||x|| ||y||<=||x||²+||y||².

    This conditional-on-PR78 theorem has a fixed negative floor and
    does NOT demonstrate asymptotic positivity or a uniform PSD bound.
    """
    if type(dim) is not int or not CERTIFIED_PREFIX <= dim <= MAX_DIMENSION:
        raise ValueError("certified prefix bound applies only to m>=3")
    if HEAD_SQUARE_WEIGHT*TAIL_SQUARE_WEIGHT > SHARP_TAIL_SQRT_RATIONAL**2:
        raise ArithmeticError("head-tail rational square inequality failed")
    return PREFIX3_LOWER


def generic_positive_prefix_tail_bound(prefix: int) -> Fraction:
    """All m>=k floor GIVEN positivity of T_k.

    S_head=(1-4^-k)/3, S_tail=4^-k/3;
    negative floor = -M*(sqrt(S_head*S_tail)+S_tail).
    Avoid square roots with a conservative EXACT rational majorant:
       sqrt(S_head*S_tail) <= 1/(3*2^k)
    since sqrt(1-4^-k)<=1.
    Thus T_m >= -M*(1/(3*2^k)+1/(3*4^k)).
    Goes to zero as k->infty IF an unbounded sequence of positive
    prefixes is independently proved; no such theorem is provided.
    """
    if type(prefix) is not int or not 1 <= prefix <= MAX_DIMENSION:
        raise ValueError("prefix must be an integer in 1..4096")
    return -Fraction(M,3)*(Fraction(1,2**prefix)+Fraction(1,4**prefix))


def enumerate_compact_bumps(count: int) -> list[dict]:
    """Concrete enumeration of b_(n,p/q), normalized compact bumps.

    phi(x)=C^-1 exp(-1/(1-x²)) for |x|<1, else 0.
    b_(n,r)(x)=2^n*phi(2^n*(x-r)).
    Here n>=1, r=p/q reduced, q>=1, p any integer.

    Enumerate increasing finite height H=n+abs(p)+q, tie-break by
    n,q,p. Every permissible (n,r) occurs at finite height.
    """
    if type(count) is not int or not 1 <= count <= 300:
        raise ValueError("count must be an integer in 1..300")
    out=[]
    height=2
    while len(out)<count:
        for n in range(1,height):
            for q in range(1,height-n+1):
                abs_p=height-n-q
                if abs_p<0:
                    continue
                candidates = [0] if abs_p==0 else [-abs_p,abs_p]
                for p in candidates:
                    if gcd(abs(p),q)!=1:
                        continue
                    r=Fraction(p,q)
                    h=Fraction(1,2**n)
                    out.append({
                        "n":n,"center":_q(r),"half_support_width":_q(h),
                        "support_left":_q(r-h),
                        "support_right":_q(r+h),
                    })
                    if len(out)==count:
                        break
                if len(out)==count:
                    break
            if len(out)==count:
                break
        height+=1
    return out


def report(dim: int=32, bump_count: int=24) -> dict:
    floor=all_index_lower(dim)
    bumps=enumerate_compact_bumps(bump_count)
    sharper=certified_prefix3_all_index_lower(dim) if dim>=3 else None
    return {
        "schema":"mathos_tectx_weil_all_index_test_topology_bridge/1",
        "status":"ALL_INDEX_NEGATIVE_FLOORS_AND_CCANONICAL_WEIL_TEST_DENSITY_NO_RH",
        "existing_signed_operator":{
            "origin":"PR #82 fixed signed Weil trace-class matrix T_ij=G_ij/2^(i+j+2)",
            "entry_bound":M,
            "dimension":dim,
            "unconditional_all_index_lower":_q(floor),
            "lower_formula":"T_m >= -(M/3)*(1-4^-m) I_m for every m>=1",
            "trivial_m_zero":True,
            "given_previously_certified_G3_positive_prefix3_all_index_lower":
                _q(sharper) if sharper is not None else None,
            "given_prefix3_bound_for_all_m_ge_3":_q(PREFIX3_LOWER),
            "conditional_prefix_k_bound":
                "-(M/3)*(2^-k+4^-k) I_m for every m>=k, IF T_k>=0 independently proved",
            "general_prefix_bound_at_k_3":_q(generic_positive_prefix_tail_bound(3)),
            "fixed_prefix_bounds_tend_to_zero_as_m_grows":False,
            "nonnegative_floor_for_all_dimensions_proved":False,
            "all_index_lower_is_negatively_valued":dim>0,
        },
        "canonical_weil_domain":{
            "test_space":"D(R)=C_c^infinity(R), additive log-coordinate LF topology",
            "bump":"phi(x)=C^-1 exp(-1/(1-x^2)) if |x|<1 else 0; C=int_-1^1 exp(-1/(1-x^2))dx",
            "basis":"b_(n,r)(x)=2^n phi(2^n(x-r)), n>=1, r in Q",
            "explicit_height_enumeration":"H=n+|p|+q, r=p/q in lowest terms, q>=1",
            "sample_bumps":bumps,
            "basis_countably_infinite":True,
            "span_dense_in_D_LF_topology":True,
            "density_argument":"mollification f*phi_h converges in every C^k with support in a fixed enlarged compact; for fixed h, rational-grid Riemann sums of translates approximate f*phi_h in every C^k; diagonalize over h,k and rational meshes",
            "W_continuous_on_D":True,
            "Weil_Hermitian_form_jointly_continuous_on_each_fixed_support_D_K":True,
            "continuity_reason":"W is a distribution (continuous linear functional on D); convolution and conjugate-reflection map D_K x D_K continuously into D_(K-K)",
            "all_finite_bump_Gram_psd_proved":False,
            "logical_equivalence":"RH iff EVERY finite Hermitian Weil Gram of these compact bump functions is positive semidefinite, by density, continuity, and classical Weil positivity criterion",
            "Weil_RH_equivalence_proved_by_this_software":False,
        },
        "gaussian_vs_compact_bump":{
            "prior_family":"q_c(t)=exp(-t^2/100)cos(c*t) in spectral variable t",
            "inverse_Fourier_transform":"linear combination of translated Gaussians in log coordinate, noncompact support",
            "prior_family_inside_Cc_infinity_log_coordinate":False,
            "prior_L2_density_entails_D_density":False,
            "prior_trace_class_limit_proves_RH":False,
        },
        "remaining_open":[
            "Prove the canonical compact-bump Weil Gram is PSD for EVERY finite index, an RH-equivalent theorem",
            "Or prove a uniform nonnegative lower bound for all prefixes of a canonically domain-dense family, not just negative all-index floors",
            "Construct and independently verify the corresponding positive Weil quotient/completion only after that global positivity theorem",
            "Derive a separate noncircular fixed self-adjoint zero-divisor correspondence if pursuing Hilbert–Pólya",
        ],
        "assurance":{
            "new_Riemann_hypothesis_proof":False,
            "all_index_positive_semidefinite_theorem":False,
            "unconditional_Weil_positive_Hilbert_space":False,
            "full_Weil_positive_operator":False,
            "peer_review_completed":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimension",type=int,default=32)
    parser.add_argument("--bump-count",type=int,default=24)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        data=report(args.dimension,args.bump_count)
    except (ValueError,ArithmeticError) as exc:
        parser.error(str(exc))
    payload=json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
