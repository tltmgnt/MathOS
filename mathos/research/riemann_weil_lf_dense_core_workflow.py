"""TECT-X: LF-dense Weil core is the PRIMARY target; old lattice is a control.

Build a nested, explicitly enumerated C_c^infinity compact bump *core* from
PR #83, and for each finite prefix compute the EXACT rational convolution
supports and an exhaustive prime-power inventory for the arithmetic Weil
formula. Every prime-log inclusion/exclusion uses rational atanh bounds,
refining ambiguous brackets; never floating point and never zeta zeros.

Important boundary: support and arithmetic inventory are NOT actual Weil
form entries, interval PSD matrices, an all-index theorem or an RH proof.
No finite prefix is LF-dense on its own. LF density of the infinite core
is an ANALYTIC proof obligation inherited from PR #83. The comparison
fixed-width lattice from PR #91 is provably non-dense in the full domain.

The workflow explicitly routes all claims through the proof-decision
topology of PR #90. It refuses promotion of finite certificates to RH.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from mathos.research.riemann_weil_all_index_bridge import enumerate_compact_bumps
from mathos.research.riemann_weil_lattice_topology_audit import (
    rational_log_integer,
    prime_power_base,
)
from mathos.research.tectx_proof_decision_topology import (
    Evidence, ProofEvidence, evaluate,
)

MAX_PREFIX=24
MAX_PRIME_CAP=10000
MAX_LOG_TERMS=64


def Q(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def family(prefix: int) -> list[dict]:
    if type(prefix) is not int or not 1<=prefix<=MAX_PREFIX:
        raise ValueError("prefix must be integer 1..24")
    return enumerate_compact_bumps(prefix)


def support_pair(a: dict,b: dict) -> tuple[Fraction,Fraction]:
    """Exact Minkowski difference for f_a * tilde(f_b)."""
    low=Fraction(a["support_left"])-Fraction(b["support_right"])
    high=Fraction(a["support_right"])-Fraction(b["support_left"])
    if low>=high:
        raise ArithmeticError("compact convolution support empty or inverted")
    return low,high


def positive_log_relation(n: int, bound: Fraction) -> int:
    """Rigorous compare log(n) to rational boundary.

    Return -1 if log(n)<bound, +1 if log(n)>bound.
    Exact equality log(n)=nonzero rational is impossible for n>=2
    (Lindemann-Weierstrass), but this routine never silently invokes
    that theorem. If 64 rational atanh terms remain inconclusive,
    fail closed rather than guessing.
    """
    if type(n) is not int or n<2 or not isinstance(bound,Fraction):
        raise ValueError("integer n>=2 and rational bound required")
    if bound<=0:
        return 1
    for terms in (8,16,32,MAX_LOG_TERMS):
        lo,hi=rational_log_integer(n,terms)
        if hi<bound:
            return -1
        if lo>bound:
            return 1
    raise ArithmeticError("prime logarithm too close to rational support boundary")


def includes_prime_log(n: int, low: Fraction, high: Fraction) -> bool:
    """Whether either of +/-log(n) is inside [low,high], certified."""
    if not low<high:
        raise ValueError("invalid compact support")
    # The endpoints are rational and log n cannot match one.
    pos=(positive_log_relation(n,low)==1 and
         positive_log_relation(n,high)==-1)
    neg=(positive_log_relation(n,-high)==1 and
         positive_log_relation(n,-low)==-1)
    return pos or neg


def exact_prime_power_inventory(low: Fraction,high: Fraction) -> list[dict]:
    """Exhaust all p^k with log(p^k) inside the exact support window.

    Since e<3, p^k<=3^ceil(max(abs(endpoints))) is safe; bounded
    audit fails if this limit exceeds MAX_PRIME_CAP. No sampling.
    """
    if not isinstance(low,Fraction) or not isinstance(high,Fraction) or low>=high:
        raise ValueError("strict exact rational support required")
    maximum=max(abs(low),abs(high))
    ceil=-(-maximum.numerator//maximum.denominator)
    cap=3**ceil
    if cap>MAX_PRIME_CAP:
        raise ValueError("bounded arithmetic audit cap exceeded")
    out=[]
    for n in range(2,cap+1):
        base=prime_power_base(n)
        if base is None:
            continue
        if includes_prime_log(n,low,high):
            out.append({"n":n,"von_mangoldt_base":base})
    return out


def finite_core_report(prefix: int=10) -> dict:
    """Finite exact supports and prime skeleton; never a Gram PSD claim."""
    bumps=family(prefix)
    entries=[]
    for i in range(prefix):
        for j in range(i,prefix):
            lo,hi=support_pair(bumps[i],bumps[j])
            inv=exact_prime_power_inventory(lo,hi)
            entries.append({
                "i":i,"j":j,"support":[Q(lo),Q(hi)],
                "prime_powers":inv,
                "all_arithmetic_prime_power_candidates_enumerated":True,
                "pole_term_evaluated":False,
                "archimedean_term_evaluated":False,
                "prime_convolution_values_evaluated":False,
                "actual_Weil_entry_enclosed":False,
            })
    if len(entries)!=prefix*(prefix+1)//2:
        raise ArithmeticError("incorrect Gram upper triangle size")
    evidence=evaluate([
        ProofEvidence(
            "dense_core_analytic_density_PR83",Evidence.FINITE_THEOREM,
            "Cc_infinity_log","countable_core","MathOS PR #83",
            LF_dense_core_proved=True,Weil_continuity_proved=True,
        ),
        ProofEvidence(
            "arithmetical_support_audit",Evidence.INTERVAL_VERIFIED,
            "finite_prefix_of_dense_core","specified_finite_span",
            "exact rational supports and all prime-power candidates",
            arithmetic_normalization_audited=False,
        ),
    ])
    return {
        "schema":"mathos_tectx_weil_lf_dense_core_workflow/1",
        "status":"LF_DENSE_CORE_SELECTED_FINITE_ARITHMETIC_SUPPORTS_AUDITED_GLOBAL_PSD_OPEN",
        "core":{
            "priority":"PRIMARY_RH_RELEVANT_TEST_FAMILY",
            "domain":"D(R)=C_c^infinity(R) with strict LF topology",
            "function":"b_(n,r)(x)=2^n phi(2^n(x-r)); n>=1, rational r",
            "phi":"normalized C_c^infinity bump supported [-1,1]",
            "enumeration":"increasing n+|p|+q for reduced r=p/q; finite prefix nested",
            "finite_prefix":prefix,
            "finite_prefix_functions":bumps,
            "infinite_family_countable":True,
            "infinite_span_LF_dense_analytic_argument":"PR #83: convolution mollifiers and rational-grid Riemann sums, with diagonal derivative seminorm control and common compact support",
            "infinite_span_LF_dense_automatically_verified":False,
            "finite_prefix_LF_dense":False,
            "every_fixed_compact_test_eventually_in_finite_span":False,
            "topology_continuity_argument":"Weil distribution on D(R); continuity of convolution on compact-support Frechet pieces",
        },
        "arithmetic":{
            "complete_support_pair_count":len(entries),
            "upper_triangle":entries,
            "computed_from_zeta_zeros":False,
            "all_entries_have_full_Weil_interval":False,
            "full_Gram_PSD_certified":False,
            "all_index_nonnegative_lower_bound":False,
            "proper_quantifier":"for all i,j in this SPECIFIED finite prefix",
            "necessary_next_step":"validated pole, prime-convolution and archimedean entry enclosures; interval Gram PSD or explicit obstruction",
        },
        "comparison_lattice":{
            "family":"phi(8*(x-3j/4)), j>=0",
            "status":"FINITE_GRAM_COMPARISON_ONLY_NOT_A_DENSE_CORE",
            "permanent_open_gap":["1/8","5/8"],
            "span_LF_dense":False,
            "lattice_L2_Gram_condition_number_every_m":1,
            "fixed_finite_lattice_PSD_implies_global_Weil_PSD":False,
        },
        "proof_decision_gate":evidence,
        "assurance":{
            "global_Weil_PSD":False,
            "all_index_core_PSD":False,
            "full_positive_Weil_Hilbert_completion":False,
            "Riemann_hypothesis_proved":False,
            "independently_formalized_density_proof":False,
        },
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix",type=int,default=10)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        r=finite_core_report(args.prefix)
    except (ArithmeticError,ValueError) as exc:
        parser.error(str(exc))
    payload=json.dumps(r,indent=2,sort_keys=True)+"\n"
    if args.output is None:
        print(payload,end="")
    else:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
