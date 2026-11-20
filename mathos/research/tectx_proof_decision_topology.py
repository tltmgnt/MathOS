"""TECT-X proof-decision topology and nonpromotion gate.

A *research control system*, not a theorem prover. Models ten possibly
overlapping decision attributes on a labeled rooted proof tree. Its
prefix ultrametric records the earliest differing decision level.

Evidence levels are strictly separated:
EXPERIMENTAL < INTERVAL_VERIFIED < FINITE_THEOREM <
UNIFORM_THEOREM < GLOBAL_WEIL_THEOREM.

Only genuine user-supplied universal proof evidence with explicit
test domain, quantifiers, norm-compatibility and Weil-continuity
obligations may pass the *logical* final gate. That gate reports
"candidate_requires_independent_mathematical_review", NEVER "RH proved".

Finite interval certificates (including MathOS PR #89) cannot
automatically discharge infinite-dimensional or LF-topology claims.
All arithmetic and limit claims remain in a fail-closed status ledger.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import IntEnum
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


class Evidence(IntEnum):
    EXPERIMENTAL = 0
    INTERVAL_VERIFIED = 1
    FINITE_THEOREM = 2
    UNIFORM_THEOREM = 3
    GLOBAL_WEIL_THEOREM = 4


DECISION_FAMILIES = (
    "axiomatic", "probabilistic", "game_theoretic", "reinforcement_learning",
    "counterfactual", "regime_switching", "behavioral", "information_theoretic",
    "topological", "meta_decision",
)

GAPS = {
    "G1_FINITE_TO_INFINITE": "An all-index theorem with explicit quantifiers is missing",
    "G2_SUPPORT_WINDOWS": "An arithmetic bound applying to arbitrary compact support is missing",
    "G3_TOPOLOGY": "Positivity on a domain-dense core and continuity are not both proved",
    "G4_SPECTRAL_STABILITY": "Comparison norms and extending Schur margins need uniform control",
    "G5_NORMALIZATION": "Domain, involution, pole moments and Weil sign convention need a consistent audit",
    "G6_LOGICAL_COMPLETION": "A noncircular all-admissible-test positivity proof is missing",
}


def exact_nonnegative(value: str) -> Fraction:
    """Reject float, boolean, NaN and negative error claims."""
    if not isinstance(value,str):
        raise ValueError("bounds must be exact rational strings")
    try:
        parsed=Fraction(value)
    except (ValueError,ZeroDivisionError) as exc:
        raise ValueError("invalid rational bound") from exc
    if parsed<0:
        raise ValueError("norm and error bounds must be nonnegative")
    return parsed


def prefix_distance(a: tuple[str,...], b: tuple[str,...]) -> Fraction:
    """Ultrametric on infinite continuations of finite labels (prefix metric).

    If equal finite sequences, distance=0 (identical represented trees).
    If distinct, let k=the zero-indexed first difference, or first
    exhausted index; distance=2^(-k). This is a metric on finite
    sequences and an ultrametric on infinite paths.
    """
    if a==b:
        return Fraction(0)
    if not all(isinstance(v,str) for v in a+b):
        raise ValueError("labels must be strings")
    k=0
    while k<min(len(a),len(b)) and a[k]==b[k]:
        k+=1
    return Fraction(1,2**k)


@dataclass(frozen=True)
class ProofEvidence:
    identifier: str
    level: Evidence
    domain: str
    quantifier: str
    source: str
    arithmetic_normalization_audited: bool = False
    LF_dense_core_proved: bool = False
    Weil_continuity_proved: bool = False
    universal_positivity_proved: bool = False
    all_compact_support_windows_covered: bool = False
    seminorm_limit_bridge_proved: bool = False

    def validate(self) -> None:
        if not (self.identifier and self.domain and self.quantifier and self.source):
            raise ValueError("evidence needs ID, domain, quantifier and source")
        if self.level>=Evidence.UNIFORM_THEOREM:
            if self.quantifier not in ("all_m", "all_admissible_tests", "every_support_window"):
                raise ValueError("uniform theorem requires explicitly universal quantifier")
        if self.level==Evidence.GLOBAL_WEIL_THEOREM:
            required=(
                self.domain=="Cc_infinity_log",
                self.quantifier=="all_admissible_tests",
                self.arithmetic_normalization_audited,
                self.LF_dense_core_proved,
                self.Weil_continuity_proved,
                self.universal_positivity_proved,
                self.all_compact_support_windows_covered,
                self.seminorm_limit_bridge_proved,
            )
            if not all(required):
                raise ValueError("global Weil claim fails domain, topology or universal proof gate")


def norm_window_assessment(error: str, reference_norm_upper: str) -> dict[str, Any]:
    """Local exact inequality eps*N(f)^2; finite bounds do NOT prove its limit."""
    eps=exact_nonnegative(error)
    norm=exact_nonnegative(reference_norm_upper)
    value=eps*norm*norm
    return {
        "epsilon":str(eps),
        "reference_norm_upper":str(norm),
        "error_times_norm_squared":str(value),
        "valid_at_this_window":True,
        "vanishing_limit_proved":False,
    }


def check_vanishing_bridge(
    windows: list[tuple[str,str]],
    *,
    has_universal_rate_proof: bool = False,
    fixed_test_eventually_admissible: bool = False,
    reference_norm_compatibility_proved: bool = False,
) -> dict[str, Any]:
    """Check finite samples but never infer n->infinity from finite data.

    Explicit proof flags are *declarations* about external proofs. The
    gate returns a review-required candidate, never certifies their
    mathematical correctness.
    """
    if not windows:
        raise ValueError("at least one finite window needed")
    checks=[norm_window_assessment(e,n) for e,n in windows]
    purported_limit=all((
        has_universal_rate_proof,
        fixed_test_eventually_admissible,
        reference_norm_compatibility_proved,
    ))
    return {
        "windows":checks,
        "sampled_error_products_decreasing":all(
            Fraction(checks[i+1]["error_times_norm_squared"])
            <= Fraction(checks[i]["error_times_norm_squared"])
            for i in range(len(checks)-1)
        ),
        "finite_sample_proves_limit":False,
        "limit_claim_has_external_proof_obligations_declared":purported_limit,
        "mathematically_verified_limit":False,
        "status":"candidate_requires_independent_mathematical_review"
             if purported_limit else "OPEN_TOPOLOGICAL_LIMIT_PROOF",
    }


def evaluate(evidence: list[ProofEvidence]) -> dict[str, Any]:
    if not evidence:
        raise ValueError("at least one evidence record is required")
    identifiers=set()
    for item in evidence:
        item.validate()
        if item.identifier in identifiers:
            raise ValueError("duplicate evidence IDs")
        identifiers.add(item.identifier)
    levels={x.level.name for x in evidence}
    finite_only=all(x.level<=Evidence.FINITE_THEOREM for x in evidence)
    uniform=[x for x in evidence if x.level>=Evidence.UNIFORM_THEOREM]
    candidates=[x for x in evidence if x.level==Evidence.GLOBAL_WEIL_THEOREM]
    missing=[]
    if not any(x.arithmetic_normalization_audited for x in evidence):
        missing.append("G5_NORMALIZATION")
    if not any(x.LF_dense_core_proved and x.Weil_continuity_proved for x in evidence):
        missing.append("G3_TOPOLOGY")
    if not uniform:
        missing.append("G1_FINITE_TO_INFINITE")
    if not any(x.all_compact_support_windows_covered for x in evidence):
        missing.append("G2_SUPPORT_WINDOWS")
    if not any(x.seminorm_limit_bridge_proved for x in evidence):
        missing.append("G4_SPECTRAL_STABILITY")
    if not candidates:
        missing.append("G6_LOGICAL_COMPLETION")
    return {
        "schema":"mathos_tectx_proof_decision_topology/1",
        "levels_observed":sorted(levels,key=lambda k:Evidence[k]),
        "finite_evidence_only":finite_only,
        "highest_evidence_level":max(evidence,key=lambda x:x.level).level.name,
        "global_proof_candidate_declared":bool(candidates),
        "global_proof_externally_verified":False,
        "Riemann_hypothesis_proved":False,
        "missing_proof_gaps":missing,
        "missing_gap_descriptions":{k:GAPS[k] for k in missing},
        "evidence_records":[{
            "id":e.identifier,"level":e.level.name,
            "domain":e.domain,"quantifier":e.quantifier,"source":e.source
        } for e in evidence],
        "scientific_status":"CANDIDATE_REQUIRES_INDEPENDENT_MATH_REVIEW"
            if candidates else "PROOF_INCOMPLETE",
    }


def sample_report() -> dict[str, Any]:
    """Known historical certificates are facts about FIXED finite spans."""
    events=[
        ProofEvidence(
            "TECTX_GAUSSIAN_GRAM3",Evidence.FINITE_THEOREM,
            "fixed_3D_gaussian", "specified_finite_span","MathOS PR #78",
            arithmetic_normalization_audited=True,
        ),
        ProofEvidence(
            "TECTX_COMPACT_PRIME_TWO_GRAM2",Evidence.FINITE_THEOREM,
            "fixed_2D_compact", "specified_finite_span","MathOS PR #87",
            arithmetic_normalization_audited=True,
        ),
        ProofEvidence(
            "TECTX_COMPACT_PRIME_8_9_11_GRAM4",Evidence.FINITE_THEOREM,
            "fixed_4D_compact", "specified_finite_span","MathOS PR #89",
            arithmetic_normalization_audited=True,
        ),
        ProofEvidence(
            "TECTX_COMPACT_BUMP_LF_DENSITY",Evidence.FINITE_THEOREM,
            "Cc_infinity_log", "countable_core","MathOS PR #83",
            LF_dense_core_proved=True,Weil_continuity_proved=True,
        ),
    ]
    report=evaluate(events)
    report["decision_ontology"]={
        "ten_families_are_overlapping_attributes":True,
        "families":list(DECISION_FAMILIES),
        "claim_of_exhaustive_ontology":False,
        "prefix_topology":"ultrametric distance 2^-k at first differing zero-based label position",
        "root":["proposed Weil theorem","actual arithmetic formula",
                "all terms validated","finite or universal",
                "domain and topology","all admissible test functions"],
    }
    report["window_demo"]=check_vanishing_bridge([
        ("1/4","4"),("1/16","8"),("1/64","16"),
    ])
    report["governance"]={
        "finite_certificates_promoted_to_global":False,
        "assurance_flags_fail_closed":True,
        "global_claim_requires_independent_mathematical_verification":True,
        "automatic_RH_solution_declaration":False,
    }
    report["source_sha256"]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return report


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    output=json.dumps(sample_report(),indent=2,sort_keys=True)+"\n"
    if args.output is None:
        print(output,end="")
    else:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(output,encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
