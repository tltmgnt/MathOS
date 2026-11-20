"""RH-Ω: bounded research evidence and finite-to-global assurance for MathOS.

This integrates existing RH proof-firewall, synthetic Li-prefix, arithmetic Weil
Gram and theta/Fredholm diagnostics. It DOES NOT prove or disprove RH.

Offline, deterministic, standard-library-only. No LLM agents are executed.
Run: python -m mathos.research.rh_omega --output artifacts/rh-omega/report.json
     python -m mathos.research.rh_omega --audit artifacts/rh-omega/report.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from mathos.research import riemann_li_prefix_005, riemann_theta_fredholm
from mathos.research import riemann_weil_gram
from mathos.research.rh_proof_firewall import (
    DEFAULT_REGISTRY, ProofBoundaryError, validate as validate_rh_register,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mathos.rh_omega/1"
CHECKS = (
    "mathematical_foundation",
    "li_universal_positivity",
    "weil_positivity",
    "analytic_continuation",
    "zero_distribution",
    "adversarial_proof_testing",
    "lean_formal_verification",
    "tect_evidence_acceptance",
)
ROLES = (
    "analytic", "zero", "prime", "spectral", "positivity",
    "conjecture", "counterexample", "formal_verification",
    "evidence", "consensus",
)
ROLE_BASIS = {
    "analytic": ("mathematical_foundation", "analytic_continuation"),
    "zero": ("zero_distribution",),
    "prime": ("mathematical_foundation", "weil_positivity"),
    "spectral": ("analytic_continuation", "adversarial_proof_testing"),
    "positivity": ("li_universal_positivity", "weil_positivity"),
    "conjecture": ("li_universal_positivity",),
    "counterexample": ("li_universal_positivity", "adversarial_proof_testing"),
    "formal_verification": ("lean_formal_verification",),
    "evidence": ("tect_evidence_acceptance",),
    "consensus": ("adversarial_proof_testing", "tect_evidence_acceptance"),
}
ROLE_FINDINGS = {
    "analytic": "The known xi functional equation is a source fact; this run checks only a finite theta-reflection sample.",
    "zero": "Riemann-von Mangoldt samples estimate N(T); no nontrivial zero has been located or certified.",
    "prime": "Euler product is scoped to Re(s)>1; finite prime-power cutoffs leave open uniform analytic tails.",
    "spectral": "The theta/Fredholm parameter family is not a fixed self-adjoint Hilbert-Pólya realization.",
    "positivity": "The exact synthetic Li prefix and finite Weil Gram do not establish all-index or all-test positivity.",
    "conjecture": "Candidate: actual Li coefficients are nonnegative for every n>=1; this is unproved.",
    "counterexample": "Finite-prefix and lower-semicontinuity countermodels invalidate two tempting proof shortcuts.",
    "formal_verification": "Lean and Coq cover bounded logical implications; this runner has no RH kernel certificate.",
    "evidence": "Canonical G1-G6 and G5P stay open, with traceable source fingerprints and scoped numerical data.",
    "consensus": "No independent expert review has occurred; ten role records are not an expert consensus.",
}

PROVENANCE_FILES = (
    "docs/research/rh_proof_obligations.json",
    "mathos/research/riemann_li_prefix_005.py",
    "mathos/research/riemann_weil_gram.py",
    "mathos/research/riemann_theta_fredholm.py",
    "formal/RHTransferLogic.lean",
    "formal/coq/RHOmegaFinitePrefix.v",
)
DISCLAIMERS = {
    "mathematical_foundation": "Known identities catalogued; no analytical reconstruction is proved by this runner.",
    "li_universal_positivity": "An exact synthetic finite prefix and a floating lambda_1 check cannot establish positivity for every zeta Li coefficient.",
    "weil_positivity": "Finite, uncertified Weil Gram with finite prime cutoff; neither all-function positivity nor tail bounds are proved.",
    "analytic_continuation": "Finite theta-integral reflection sample; no machine-checked complex-analytic continuation theorem.",
    "zero_distribution": "Riemann-von Mangoldt main-term estimates only; no actual zero enumeration or rigorous root locations.",
    "adversarial_proof_testing": "Logical countermodels expose unsupported inference, not a contradiction in RH.",
    "lean_formal_verification": "Lean/Coq source references only; CI compiles finite logical lemmas, never RH.",
    "tect_evidence_acceptance": "Proof-state and provenance checks only; TECT cannot establish mathematical truth.",
}


class RHOmegaError(ValueError):
    """Reject unsupported inference, mutated evidence and fake certification."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RHOmegaError(message)


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False,
                   separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def provenance(root: Path = ROOT) -> dict[str, str]:
    return {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in PROVENANCE_FILES
    }


def stage(name: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": name,
        "status": "RESEARCH_DIAGNOSTIC_ONLY",
        "explanation": DISCLAIMERS[name],
        "evidence": data,
        "rh_proved": False,
        "global_obligation_discharged": False,
    }


def run(*, registry_path: Path = DEFAULT_REGISTRY, root: Path = ROOT,
        li_prefix: int = 6) -> dict[str, Any]:
    """Execute 8 grounded checks and 10 deterministic role summaries.

    Uses existing MathOS research code; never writes the proof register.
    Avoid treating a proof assistant's source file as a verified compilation.
    """
    require(type(li_prefix) is int and 1 <= li_prefix <= 12,
            "li_prefix must be an integer in 1..12")
    before = registry_path.read_bytes()
    registry_report = validate_rh_register(json.loads(before))
    require(registry_report["global_claim_status"] == "OPEN" and
            registry_report["unresolved_gates"] == ["G1","G2","G3","G4","G5","G6"] and
            registry_report["family_wide_positivity_status"] == "CONJECTURED",
            "RH full proof obligations unexpectedly changed")
    fingerprints = provenance(root)

    synthetic = riemann_li_prefix_005.certificate(li_prefix)
    require(synthetic["status"] == "EXACT_SYNTHETIC_COUNTERMODEL_ONLY"
            and synthetic["all_prefix_coefficients_positive"] is True
            and synthetic["full_rh_proved"] is False
            and synthetic["zeta_zero_claim"] is False,
            "Li-prefix evidence escaped its synthetic scope")
    # Closed-form first Li coefficient; float is NOT a certified enclosure.
    first_li = 1 + 0.5772156649015329 / 2 - math.log(4 * math.pi) / 2
    require(0 < first_li < 1, "Li coefficient numeric sanity check failed")

    gram = riemann_weil_gram.audit(
        centers=(0.0, 0.2), a=0.02, max_t=30.0,
        panels=2048, prime_bound=128,
    )
    require(gram["status"] == "FINITE_UNCERTIFIED_WEIL_FORM_TEST_NOT_RH"
            and gram["numerics"]["can_certify_Weil_psd"] is False
            and gram["finite_Weil_Gram"]["claim_of_global_psd"] is False
            and gram["conditional_Hilbert_space"]["global_positivity_proved"] is False
            and gram["independent_positive_L2_comparison"]["is_the_Weil_form"] is False
            and all(flag is False for flag in gram["assurance"].values()),
            "Weil numeric scope unexpectedly promoted")

    s = 0.7 + 2j
    xi_s = riemann_theta_fredholm.determinant_approx(
        s, xmax=6, panels=512, terms=6
    )
    xi_reflection = riemann_theta_fredholm.determinant_approx(
        1 - s, xmax=6, panels=512, terms=6
    )
    reflection_error = abs(xi_s - xi_reflection)
    require(math.isfinite(reflection_error) and reflection_error < 1e-9,
            "finite theta reflection diagnostic regressed")

    # The terms are asymptotic estimates, not measured zero counts.
    zero_main_terms = [
        {
            "T": t,
            "riemann_von_mangoldt_main_term": (
                t / (2 * math.pi) * math.log(t / (2 * math.pi))
                - t / (2 * math.pi) + 0.875
            ),
        }
        for t in (20, 50, 100)
    ]
    require(all(math.isfinite(x["riemann_von_mangoldt_main_term"])
                for x in zero_main_terms), "zero asymptotic nonfinite")

    # Concrete countermodel: f(0)=-1, f(x)=1 for x !=0.
    # f is lower semicontinuous and positive on dense R\{0}, but negative
    # at 0. Thus l.s.c. + dense positivity does NOT give global positivity.
    adversarial = [
        {
            "attack": "finite_positive_prefix_to_universal",
            "witness": "a_n=1 for n<=K and -1 for n>K",
            "unwarranted_implication_rejected": True,
        },
        {
            "attack": "lower_semicontinuity_plus_dense_positivity",
            "witness": "f(0)=-1 and f(x)=1 for x!=0 on R",
            "unwarranted_implication_rejected": True,
        },
        {
            "attack": "finite_gram_or_l2_positivity_to_weil",
            "witness": "Finite Weil Gram does not exhaust the full test space; L2 Gram is a different form",
            "unwarranted_implication_rejected": True,
        },
        {
            "attack": "s_dependent_determinant_to_hilbert_polya",
            "witness": "A parameter-dependent rank-one determinant is not a fixed self-adjoint zero operator",
            "unwarranted_implication_rejected": True,
        },
    ]

    data = {
        "mathematical_foundation": {
            "zeta_dirichlet_half_plane": "Re(s)>1",
            "xi_definition": "xi(s)=s(s-1)*pi^(-s/2)*Gamma(s/2)*zeta(s)/2",
            "xi_functional_equation_reference": "xi(s)=xi(1-s)",
            "euler_product_half_plane": "Re(s)>1",
            "independent_analytic_proof_performed": False,
        },
        "li_universal_positivity": {
            "first_li_closed_form_float": first_li,
            "first_li_float_is_certified_interval": False,
            "exact_synthetic_prefix": synthetic["tested_positive_prefix_length"],
            "synthetic_countermodel": True,
            "uses_actual_zeta_zeros": False,
            "universal_positive_established": False,
        },
        "weil_positivity": {
            "basis_size": len(gram["basis"]["centers"]),
            "prime_bound": gram["numerics"]["max_prime_power_index"],
            "approx_min_eigenvalue": gram["finite_Weil_Gram"]["approx_min_eigenvalue"],
            "positive_L2_gram_is_weil": False,
            "quadrature_and_tails_certified": False,
            "full_test_space_positivity": False,
        },
        "analytic_continuation": {
            "sample_s": [s.real, s.imag],
            "theta_reflection_residual": reflection_error,
            "numeric_reflection_only": True,
            "analytical_continuation_formally_checked": False,
            "fixed_self_adjoint_zero_operator": False,
        },
        "zero_distribution": {
            "asymptotic_main_term_samples": zero_main_terms,
            "actual_zeros_verified": 0,
            "all_zeros_on_line_established": False,
        },
        "adversarial_proof_testing": {
            "countermodels": adversarial,
            "universal_transfer_justified_by_finite_evidence": False,
        },
        "lean_formal_verification": {
            "lean_source": "formal/RHTransferLogic.lean",
            "coq_source": "formal/coq/RHOmegaFinitePrefix.v",
            "ci_kernel_check_required": True,
            "kernel_was_executed_by_this_runner": False,
            "formal_rh_theorem_proved": False,
        },
        "tect_evidence_acceptance": {
            "canonical_proof_registry": "docs/research/rh_proof_obligations.json",
            "global_status": registry_report["global_claim_status"],
            "unresolved_gates": registry_report["unresolved_gates"],
            "family_wide_positivity": registry_report["family_wide_positivity_status"],
            "finite_probes_are_global_proof": False,
            "external_peer_review_complete": False,
        },
    }
    checks = [stage(name, data[name]) for name in CHECKS]
    agents = [
        {
            "role": role,
            "mode": "DETERMINISTIC_RESEARCH_REVIEW_NOT_LIVE_AI",
            "inputs": list(ROLE_BASIS[role]),
            "finding": ROLE_FINDINGS[role],
            "consensus_of_independent_experts": False,
            "rh_proved": False,
        }
        for role in ROLES
    ]
    require(before == registry_path.read_bytes(),
            "canonical RH proof register changed during research run")
    report = {
        "schema": SCHEMA,
        "target": "Riemann Hypothesis",
        "global_claim_status": "OPEN",
        "certification": "NOT_CERTIFIED",
        "outcome": "SCOPED_RESEARCH_EVIDENCE",
        "checks": checks,
        "agents": agents,
        "canonical_proof_obligation_sha256": hashlib.sha256(before).hexdigest(),
        "source_sha256": fingerprints,
        "proof_promotion": "NONE",
    }
    report["assurance"] = {
        "decision": "RESEARCH_ONLY",
        "rh_proved": False,
        "independent_review_completed": False,
        "content_sha256": digest(report),
    }
    audit(report, root=root)
    return report


def audit(report: dict[str, Any], *, root: Path = ROOT,
          verify_sources: bool = True) -> dict[str, Any]:
    """Fail closed on promotion, missing agents, altered hashes or stage types.

    Even a consistent packet is NOT a theorem verification transcript.
    """
    require(type(report) is dict and set(report) == {
        "schema", "target", "global_claim_status", "certification", "outcome",
        "checks", "agents", "canonical_proof_obligation_sha256",
        "source_sha256", "proof_promotion", "assurance",
    }, "RH-Ω packet schema mismatch")
    require(
        report["schema"] == SCHEMA and report["target"] == "Riemann Hypothesis"
        and report["global_claim_status"] == "OPEN"
        and report["certification"] == "NOT_CERTIFIED"
        and report["outcome"] == "SCOPED_RESEARCH_EVIDENCE"
        and report["proof_promotion"] == "NONE",
        "attempted global RH promotion",
    )
    if verify_sources:
        require(report["source_sha256"] == provenance(root), "source provenance changed")
        registry_bytes = (root / "docs/research/rh_proof_obligations.json").read_bytes()
        require(
            report["canonical_proof_obligation_sha256"] ==
            hashlib.sha256(registry_bytes).hexdigest(),
            "RH obligation register fingerprint mismatch",
        )
        validate_rh_register(json.loads(registry_bytes))
    checks = report["checks"]
    require(type(checks) is list and len(checks) == len(CHECKS),
            "required eight checks missing")
    require(all(
        type(c) is dict and set(c) == {
            "id", "status", "explanation", "evidence",
            "rh_proved", "global_obligation_discharged",
        } and c["id"] == name
        and c["status"] == "RESEARCH_DIAGNOSTIC_ONLY"
        and c["explanation"] == DISCLAIMERS[name]
        and c["rh_proved"] is False
        and c["global_obligation_discharged"] is False
        and type(c["evidence"]) is dict
        for c, name in zip(checks, CHECKS)
    ), "research check or proof state altered")
    evidence = {c["id"]: c["evidence"] for c in checks}
    expected_flags = {
        "mathematical_foundation": {"independent_analytic_proof_performed": False},
        "li_universal_positivity": {
            "first_li_float_is_certified_interval": False,
            "synthetic_countermodel": True,
            "uses_actual_zeta_zeros": False,
            "universal_positive_established": False,
        },
        "weil_positivity": {
            "positive_L2_gram_is_weil": False,
            "quadrature_and_tails_certified": False,
            "full_test_space_positivity": False,
        },
        "analytic_continuation": {
            "numeric_reflection_only": True,
            "analytical_continuation_formally_checked": False,
            "fixed_self_adjoint_zero_operator": False,
        },
        "zero_distribution": {"all_zeros_on_line_established": False},
        "adversarial_proof_testing": {
            "universal_transfer_justified_by_finite_evidence": False,
        },
        "lean_formal_verification": {
            "ci_kernel_check_required": True,
            "kernel_was_executed_by_this_runner": False,
            "formal_rh_theorem_proved": False,
        },
        "tect_evidence_acceptance": {
            "global_status": "OPEN",
            "finite_probes_are_global_proof": False,
            "external_peer_review_complete": False,
        },
    }
    for name, flags in expected_flags.items():
        for field, expected in flags.items():
            require(evidence[name].get(field) is expected
                    if type(expected) is bool else
                    evidence[name].get(field) == expected,
                    f"{name}: {field} violates evidence boundary")
    require(
        evidence["tect_evidence_acceptance"].get("unresolved_gates") ==
        ["G1", "G2", "G3", "G4", "G5", "G6"]
        and evidence["tect_evidence_acceptance"].get("family_wide_positivity")
        == "CONJECTURED",
        "missing canonical RH firewall gates",
    )
    countermodels = evidence["adversarial_proof_testing"].get("countermodels")
    require(type(countermodels) is list and len(countermodels) == 4
            and all(type(x) is dict and x.get("unwarranted_implication_rejected") is True
                    for x in countermodels),
            "adversarial countermodels absent")
    agents = report["agents"]
    require(type(agents) is list and len(agents) == len(ROLES) and all(
        type(a) is dict and set(a) == {
            "role", "mode", "inputs", "finding",
            "consensus_of_independent_experts", "rh_proved",
        } and a["role"] == role
        and a["mode"] == "DETERMINISTIC_RESEARCH_REVIEW_NOT_LIVE_AI"
        and a["inputs"] == list(ROLE_BASIS[role])
        and a["consensus_of_independent_experts"] is False
        and a["rh_proved"] is False
        and a["finding"] == ROLE_FINDINGS[role]
        for a, role in zip(agents, ROLES)
    ), "invalid agents or false consensus")
    assurance = report["assurance"]
    require(type(assurance) is dict and set(assurance) == {
        "decision", "rh_proved", "independent_review_completed", "content_sha256",
    } and assurance["decision"] == "RESEARCH_ONLY"
            and assurance["rh_proved"] is False
            and assurance["independent_review_completed"] is False,
            "TECT acceptance boundary violated")
    unassured = {k: v for k, v in report.items() if k != "assurance"}
    require(assurance["content_sha256"] == digest(unassured),
            "evidence payload changed after fingerprinting")
    return {
        "decision": "RESEARCH_ONLY",
        "global_claim_status": "OPEN",
        "checks": len(checks),
        "agents": len(agents),
        "fingerprints_match": True,
        "this_is_not_mathematical_verification": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--audit", type=Path, help="audit existing JSON packet")
    parser.add_argument("--output", type=Path, help="emit new research packet")
    parser.add_argument("--li-prefix", type=int, default=6)
    args = parser.parse_args()
    try:
        if args.audit:
            packet = json.loads(args.audit.read_text(encoding="utf-8"))
            result = audit(packet)
        else:
            result = run(li_prefix=args.li_prefix)
        out = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(out, encoding="utf-8")
        else:
            print(out, end="")
    except (OSError, ValueError, AssertionError, ProofBoundaryError) as exc:
        parser.exit(1, f"RH-Ω FAILED: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
