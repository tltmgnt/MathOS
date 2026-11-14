"""Auditable bounded SAT1 formal proof, novelty triage and Clay implication gate.

This links the exact local SAT1 subresult to a pinned Lean source and
explicitly records that literature novelty, external mathematical review,
and the implication to P vs NP remain unestablished.

Run: python -m mathos.research.theorem_assurance --output-dir artifacts/theorems
     python -m mathos.research.theorem_assurance --output-dir artifacts/theorems --verify-lean
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from mathos.research.clay_alignment import TARGETS_PATH
from mathos.research.clay_proof_topology import (
    EXTERNAL_PATH, ROUTES_PATH, audit_clay_proof_topology,
)
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS, ROOT

THEOREMS_PATH = ROOT / "docs/research/THEOREM_ASSURANCE.v1.json"
SAT_LEAN = ROOT / "formal/SATSupport.lean"
EXPECTED = {
    "schema_version": "1.0.0",
    "policy": {
        "canonical_certification": "NOT_CERTIFIED",
        "mathematical_novelty": "NOT_INDEPENDENTLY_ASSESSED",
        "peer_review": "NOT_PERFORMED",
        "clay_implication": "NOT_ESTABLISHED",
        "auto_promotion": False,
    },
}
EXPECTED_CLAIM = {
    "theorem_id": "SAT1",
    "model_key": "P-versus-NP",
    "route_id": "PNP.equality",
    "open_claim_id": "PNP.sat_runtime",
    "lean_file": "formal/SATSupport.lean",
    "lean_theorem": "MathOS.satSupport_certificate",
    "model_semantics": "DISJOINT_VARIABLE_PAIR_CHOICE_WORDS",
    "proof_goal": "FINITE_SUPPORT_COUNTS_ONLY",
    "originality_status": "ELEMENTARY_KNOWN_STYLE_NOT_CLAIMED_NEW",
    "literature_search": "NOT_COMPLETED",
    "independent_mathematical_review": "NOT_PERFORMED",
    "bridge_to_registered_obligation": "NOT_PROVEN",
    "bridge_to_clay_target": "NOT_PROVEN",
    "publication": "NOT_SUBMITTED",
    "scope_complete_for_clay": False,
}
REQUIRED_AUDIT_FIELDS = (
    "statement", "mathematical_scope", "relevance",
    "limitations", "literature_review_plan", "external_review_plan",
    "route_implication_gap", "counterexample_limitations",
)


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not 40 <= len(value.strip()) <= 4000:
        raise ValueError(f"missing substantial theorem assurance field: {field}")
    return value


def _check_lean(src: Path) -> dict:
    lean = shutil.which("lean")
    if lean is None:
        raise RuntimeError("Lean is unavailable; verification requires pinned 4.14.0")
    ver = subprocess.run([lean, "--version"], timeout=15, capture_output=True,
                         text=True, check=False)
    if ver.returncode != 0 or not ver.stdout.startswith("Lean (version 4.14.0"):
        raise RuntimeError("this assurance gate requires Lean 4.14.0")
    replay = subprocess.run([lean, str(src)], timeout=90, capture_output=True,
                            text=True, check=False)
    if replay.returncode != 0:
        raise RuntimeError("SAT1 formal source did not compile under pinned Lean")
    return {
        "status": "LEAN_COMPILED_EXACT_SUBRESULT_ONLY",
        "lean_version": ver.stdout.strip().splitlines()[0],
        "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        "scope": "MATHOS_SAT1_TERM_CHOICE_ENCODING",
        "clay_proof": False,
    }


def audit_theorem_assurance(
    assurance_path: Path = THEOREMS_PATH, *,
    output_dir: Path | None = None,
    verify_lean: bool = False,
    lean_path: Path = SAT_LEAN,
    register_path: Path = OBLIGATIONS,
    targets_path: Path = TARGETS_PATH,
    routes_path: Path = ROUTES_PATH,
    hypotheses_path: Path = HYPOTHESES,
    external_path: Path = EXTERNAL_PATH,
) -> dict:
    paths = {
        "assurance": assurance_path, "lean": lean_path,
        "register": register_path, "targets": targets_path,
        "routes": routes_path, "hypotheses": hypotheses_path,
        "external": external_path,
    }
    original = {key: path.read_bytes() for key, path in paths.items()}
    topo = audit_clay_proof_topology(
        routes_path=routes_path, targets_path=targets_path,
        register_path=register_path, hypotheses_path=hypotheses_path,
        external_path=external_path,
    )
    manifest = json.loads(original["assurance"])
    if type(manifest) is not dict or set(manifest) != {
        "schema_version", "policy", "subresults",
    }:
        raise ValueError("unsupported theorem assurance registry")
    for field in ("schema_version", "policy"):
        if manifest[field] != EXPECTED[field]:
            raise ValueError("theorem assurance cannot promote proof/review status")
    results = manifest["subresults"]
    if type(results) is not list or len(results) != 1 or type(results[0]) is not dict:
        raise ValueError("exactly one declared SAT1 subresult is required in v1")
    claim = results[0]
    if set(claim) != set(EXPECTED_CLAIM) | set(REQUIRED_AUDIT_FIELDS):
        raise ValueError("missing or extraneous theorem evidence fields")
    for key, value in EXPECTED_CLAIM.items():
        if claim[key] != value:
            raise ValueError(f"unsupported or promoted theorem claim: {key}")
    for key in REQUIRED_AUDIT_FIELDS:
        _text(claim[key], key)

    register = json.loads(original["register"])
    if register.get("certification") != "NOT_CERTIFIED":
        raise ValueError("canonical certification unexpectedly changed")
    sat1 = register.get("sat_subresult", {})
    if sat1.get("claim_id") != "SAT1" or sat1.get("status") != "informal_proof_in_repository":
        raise ValueError("SAT1 source identity or canonical status changed")
    if sat1.get("formal_check") != "not_performed":
        raise ValueError("canonical register promotion requires separate independent review")
    track = next((x for x in register["tracks"]
                  if x["model_key"] == claim["model_key"]), None)
    if track is None or track.get("modeled_target_status") != "BLOCKED":
        raise ValueError("P vs NP target is not canonically blocked")
    if not any(x["claim_id"] == claim["open_claim_id"] and
               x["graph_state"] == "open" for x in track["work_packages"]):
        raise ValueError("incorrect or prematurely closed SAT runtime obligation")
    route = next((r for t in topo["targets"] if t["model_key"] == claim["model_key"]
                  for r in t["candidate_routes"]
                  if r["route_id"] == claim["route_id"]), None)
    if route is None or claim["open_claim_id"] not in route["obligations"]:
        raise ValueError("SAT1 has no registered, still-open Clay route connection")
    if topo.get("certification") != "NOT_CERTIFIED":
        raise ValueError("topology incorrectly reports a certified solution")

    lean_text = original["lean"].decode("utf-8")
    if (lean_text.count("theorem satSupport_certificate ") != 1 or
        "theorem satTerms_length " not in lean_text or
        "theorem satTerms_nodup " not in lean_text or
        "theorem satCoefficient_ne_zero " not in lean_text or
        "namespace MathOS" not in lean_text or
        any(token in lean_text for token in (
            "sorry", "admit", "unsafe def", "axiom ", "opaque ",
            "run_tac", "native_decide",
        ))):
        raise ValueError("formal source contains unsupported proof shortcuts or missing claims")

    lean_check = _check_lean(lean_path) if verify_lean else {
        "status": "NOT_RUN",
        "source_sha256": hashlib.sha256(original["lean"]).hexdigest(),
        "clay_proof": False,
    }
    if any(path.read_bytes() != original[key] for key, path in paths.items()):
        raise RuntimeError("mathematical sources changed during assurance evaluation")

    report = {
        "schema_version": "1.0.0",
        "certification": "NOT_CERTIFIED",
        "formal_result": lean_check,
        "subresult_id": "SAT1",
        "formal_scope": "DISJOINT_FACTOR_CHOICE_WORDS_FOR_ALL_M",
        "mathematical_novelty": "NOT_INDEPENDENTLY_ASSESSED",
        "external_expert_review": "NOT_PERFORMED",
        "clay_route_implication": "NOT_PROVEN",
        "registered_open_obligations_remaining": topo["canonical_open_work_packages"],
        "additional_open_proof_bridges": topo["additional_proposed_bridges"],
        "proof_route_sufficiency": "NOT_VALIDATED",
        "research_priority": "NO_AUTOMATED_PRIORITY_SCORE",
        "sources_sha256": {
            key: hashlib.sha256(value).hexdigest()
            for key, value in original.items()
        },
        "review_queue": {
            "literature_review": claim["literature_review_plan"],
            "independent_review": claim["external_review_plan"],
            "missing_mathos_implication": claim["route_implication_gap"],
            "qualification": claim["limitations"],
        },
        "mathematical_scope_justification": claim["mathematical_scope"],
        "clay_solution": False,
        "canonical_claim_promotion": False,
    }
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "theorem_assurance.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        lines = [
            "# SAT1: independent mathematical review handoff",
            "",
            "**Current status: NOT_CERTIFIED; no independent novelty assessment "
            "or expert review has been completed.**",
            "",
            "## Exact theorem statement",
            "",
            claim["statement"],
            "",
            "## Verified-language scope",
            "",
            claim["mathematical_scope"],
            "",
            "## Known limits and non-implication to the Clay problem",
            "",
            claim["route_implication_gap"],
            "",
            claim["limitations"],
            "",
            "## Formal proof audit",
            "",
            "Lean source: `formal/SATSupport.lean`",
            "",
            "Source SHA-256: `" + report["sources_sha256"]["lean"] + "`",
            "",
            "Lean result: **" + lean_check["status"] + "**",
            "",
            "## Pending independent novelty assessment",
            "",
            claim["literature_review_plan"],
            "",
            "## Pending independent mathematical review",
            "",
            claim["external_review_plan"],
            "",
            "## Reviewer checklist (not automated acceptance)",
            "",
            "- [ ] Verify theorem statement and correct source correspondence",
            "- [ ] Check proof and trusted Lean imports separately",
            "- [ ] Search the literature; cite primary references and dates",
            "- [ ] Evaluate whether any novelty claim is defensible",
            "- [ ] Establish or reject any implication to SAT runtime",
            "- [ ] Document limitations, counterexamples, reviewer identity and date",
            "",
            "Unchecked items are real, outstanding mathematical work, not "
            "a substitute for expert approval.",
        ]
        (output_dir / "sat1_review_handoff.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--verify-lean", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(audit_theorem_assurance(
        output_dir=args.output_dir, verify_lean=args.verify_lean),
        sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
