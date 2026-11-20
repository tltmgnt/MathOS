"""TECT-X: RH-equivalent vanishing lower bound and exact prime-support gates.

A fixed nested Hermitian Gram sequence H_m satisfies H_m >= -eps_m I_m
for ALL m with eps_m>=0 and eps_m->0 IF AND ONLY IF every H_m is PSD.
The forward direction follows from zero-extending any fixed vector;
there is no epsilon_m construction here and no RH proof.

For real compactly supported Weil bumps b_(n,r), convolution
b_i * tilde(b_j) is supported inside
[r_i-r_j-(h_i+h_j), r_i-r_j+(h_i+h_j)].
Its explicit-formula prime terms sample the convolution at +/-log(p^k),
so all possible prime powers satisfy p^k <= exp(B), where B is the
maximum absolute endpoint. Since e<3, the integer cap 3^ceil(B) is
rigorous and requires no floating point.

This bounds the FINITE prime side for each pair; it does not compute
archimedean terms, certify any Weil Gram PSD or prove RH.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from math import isqrt
from pathlib import Path

from mathos.research.riemann_weil_all_index_bridge import enumerate_compact_bumps

MAX_BUMPS = 64
MAX_ENUMERATED_CAP = 200000


def rational_str(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def ceiling(x: Fraction) -> int:
    if not isinstance(x, Fraction):
        raise ValueError("exact rational required")
    return -(-x.numerator // x.denominator)


def support_pair(a: dict, b: dict) -> dict:
    """Exact rational support of h=a*tilde(b), not product a*b."""
    left = Fraction(a["support_left"]) - Fraction(b["support_right"])
    right = Fraction(a["support_right"]) - Fraction(b["support_left"])
    if not left <= right:
        raise AssertionError("reversed convolution support")
    B = max(abs(left),abs(right))
    cap = 3**ceiling(B)
    return {
        "support": [rational_str(left),rational_str(right)],
        "max_abs_log_coordinate": rational_str(B),
        "rigorous_integer_prime_power_cap":cap,
        "derivation":"prime terms evaluate convolution at +/-log(p^k); |log(p^k)|<=B implies p^k<=exp(B)<=3^ceil(B), since e<3",
        "prime_powers_are_finite":True,
        "complete_prime_formula_evaluated":False,
        "archimedean_formula_evaluated":False,
    }


def candidate_prime_powers(cap: int) -> list[tuple[int,int]]:
    if type(cap) is not int or not 1 <= cap <= MAX_ENUMERATED_CAP:
        raise ValueError("cap must be integer 1..200000")
    prime=bytearray(b"\x01")*(cap+1)
    prime[:2]=b"\x00\x00"
    for p in range(2,isqrt(cap)+1):
        if prime[p]:
            prime[p*p:cap+1:p]=b"\x00"*((cap-p*p)//p+1)
    powers=[]
    for p in range(2,cap+1):
        if prime[p]:
            v=p
            while v<=cap:
                powers.append((v,p))
                v*=p
    return sorted(powers)


def vanishing_floor_equivalence() -> dict:
    return {
        "fixed_Gram_sequence":"H_m=(W(b_i * tilde(b_j)))_{0<=i,j<m}, all H_m Hermitian and leading-principal nested",
        "hypothesis":"exists nonnegative real eps_m->0 such that H_m >= -eps_m I_m for EVERY m>=1",
        "conclusion":"H_k >= 0 for EVERY fixed k>=1",
        "proof":"Fix k and v in C^k; zero-extend v to C^m for all m>=k; v*H_k v=v_ext*H_m v_ext >= -eps_m||v||^2; pass to limit m->infty",
        "converse":"if every H_m>=0 choose eps_m=0",
        "note":"If the same statement is made with a fixed positive reference Gram L_m, the implication still holds for each fixed v because v*L_k v is independent of m",
        "RH_equivalent_if_canonical_Weil_test_core":True,
        "all_index_hypothesis_proved":False,
        "is_new_RH_proof":False,
    }


def report(count: int = 8) -> dict:
    if type(count) is not int or not 1 <= count <= MAX_BUMPS:
        raise ValueError("count must be integer 1..64")
    bumps=enumerate_compact_bumps(count)
    pairs=[]
    maximum=1
    for i,a in enumerate(bumps):
        for j in range(i,count):
            item=support_pair(a,bumps[j])
            maximum=max(maximum,item["rigorous_integer_prime_power_cap"])
            pairs.append({"i":i,"j":j,**item})
    return {
        "schema":"mathos_tectx_weil_vanishing_floor_and_prime_support/1",
        "status":"ALL_INDEX_VANISHING_FLOOR_EQUIVALENT_TO_RH_NOT_PROVED",
        "gram_family":"compact-log-coordinate Cc-infinity bump Weil Hermitian Gram, NOT the earlier noncompact Gaussian matrix",
        "dimension":count,
        "vanishing_floor_theorem":vanishing_floor_equivalence(),
        "arithmetic_support":{
            "bump_count":count,
            "pair_count":len(pairs),
            "pair_bounds":pairs,
            "maximum_finite_prime_power_cap":maximum,
            "prime_terms_require_at_most_finite_integers":True,
            "bound_may_be_loose":True,
            "prime_terms_fully_evaluated":False,
            "archimedean_terms_fully_evaluated":False,
            "Gram_eigenvalue_certification_performed":False,
        },
        "required_next_proof":[
            "independently derive and certify each compact-bump archimedean Weil entry using the correct convolution normalization",
            "evaluate the finitely many permitted prime powers with interval arithmetic and certified smooth bump integrals",
            "prove a quantitative all-index PSD theorem, or all-index vanishing negative errors, without assuming RH",
            "verify correct LF-topology continuity and RH criterion normalization independently",
        ],
        "assurance":{
            "positive_semidefinite_every_finite_Gram":False,
            "vanishing_negative_floor_exists_for_all_indices":False,
            "global_Weil_positivity_proved":False,
            "positive_Weil_Hilbert_completion":False,
            "Riemann_hypothesis_proved":False,
            "peer_review_completed":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count",type=int,default=8)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        result=report(args.count)
    except ValueError as e:
        parser.error(str(e))
    payload=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
