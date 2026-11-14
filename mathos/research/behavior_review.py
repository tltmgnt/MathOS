"""Adversarial *use card* for research review decisions, not a peer-review verdict.

This deterministic, offline evaluator presents scoped challenges without answers
and checks only selected decision labels against preregistered keys. It CANNOT
assess the quality of a mathematical explanation, authenticate the participant,
infer a behavioral trait or create an independent mathematical review.

    python -m mathos.research.behavior_review --output-dir artifacts/behavior
    python -m mathos.research.behavior_review --responses answers.json --output-dir artifacts/behavior
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from mathos.research.hypothesis_pipeline import ROOT
from mathos.research.theorem_assurance import SAT_LEAN

CARDS_PATH = ROOT / "docs/research/papers/SAT1_ADVERSARIAL_BEHAVIOR_CARDS.v1.json"
REGISTRATION_PATH = ROOT / "docs/research/papers/SAT1_INDEPENDENT_REVIEW_REGISTER.v1.json"
EXPECTED_POLICY = {
    "external_reviewer_verification": "NOT_PERFORMED",
    "behavior_study": "NOT_CONDUCTED",
    "human_decision_review": "REQUIRED",
    "auto_mathematical_truth_assessment": False,
    "independent_math_acceptance": "NOT_ESTABLISHED",
    "clay_solution": "NOT_CERTIFIED",
}
DECISIONS = (
    "REJECT_PROMOTION", "REQUEST_SCOPE_PROOF", "REQUEST_AUTHENTICATION",
    "ACCEPT_LIMITED_SCOPE", "INCONCLUSIVE",
)
KEYS = {
    "BHV-01": "REJECT_PROMOTION",
    "BHV-02": "REJECT_PROMOTION",
    "BHV-03": "REQUEST_SCOPE_PROOF",
    "BHV-04": "REQUEST_AUTHENTICATION",
    "BHV-05": "REQUEST_AUTHENTICATION",
    "BHV-06": "REQUEST_SCOPE_PROOF",
    "BHV-07": "ACCEPT_LIMITED_SCOPE",
}
CASE_FIELDS = {
    "case_id", "category", "claim", "scenario", "participant_task",
    "expected_decision", "rationale", "required_observations",
}
RESPONSE_FIELDS = {"case_id", "decision", "evidence_notes", "source_reference"}
SESSION_FIELDS = {"schema_version", "kind", "source_sha256", "casebook_sha256",
                  "participant_label", "responses"}
PSEUDONYM = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,31}\Z")


def _sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _long(value: Any, name: str, low: int = 30, high: int = 1500) -> str:
    if type(value) is not str or not low <= len(value.strip()) <= high:
        raise ValueError(f"invalid or insubstantial {name}")
    return value


def _read_cases(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as error:
        raise ValueError("invalid adversarial casebook") from error
    if type(data) is not dict or set(data) != {
        "schema_version", "title", "scope", "source_theorem",
        "policy", "decisions", "cases",
    }:
        raise ValueError("casebook schema drift")
    if (data["schema_version"] != "1.0.0" or
        data["scope"] != "BOUNDED_REVIEW_DECISION_BEHAVIOR_NOT_CLAY_PROOF" or
        data["source_theorem"] != "MathOS.satSupport_certificate" or
        data["policy"] != EXPECTED_POLICY or
        data["decisions"] != list(DECISIONS)):
        raise ValueError("unsupported behavioral or mathematical status promotion")
    _long(data["title"], "card title", 12)
    rows = data["cases"]
    if type(rows) is not list or len(rows) != len(KEYS):
        raise ValueError("expected exactly seven case cards")
    seen = set()
    for row in rows:
        if type(row) is not dict or set(row) != CASE_FIELDS:
            raise ValueError("invalid adversarial case fields")
        cid = row["case_id"]
        if type(cid) is not str or cid not in KEYS or cid in seen:
            raise ValueError("duplicate or unknown case ID")
        seen.add(cid)
        if row["expected_decision"] != KEYS[cid]:
            raise ValueError("adversarial decision key altered")
        for field in ("category", "claim", "scenario", "participant_task", "rationale"):
            _long(row[field], field, 8 if field == "category" else 30, 1800)
        obs = row["required_observations"]
        if type(obs) is not list or len(obs) != 2 or any(
            type(x) is not str or not 20 <= len(x) <= 300 for x in obs
        ):
            raise ValueError("case is missing behavioral observations")
    if seen != set(KEYS):
        raise ValueError("missing adversarial case")
    return data, raw


def run_behavior_review(
    *, casebook_path: Path = CARDS_PATH,
    response_path: Path | None = None,
    output_dir: Path | None = None,
) -> dict:
    data, cases_raw = _read_cases(casebook_path)
    source = SAT_LEAN.read_bytes()
    registry_before = REGISTRATION_PATH.read_bytes()
    ledger = json.loads(registry_before)
    if (ledger.get("scope") != "SAT1_CHOICE_WORD_SUPPORT_ONLY" or
        ledger.get("policy", {}).get("expert_verdict") !=
            "NOT_INDEPENDENTLY_VALIDATED" or
        ledger.get("policy", {}).get("clay_solution") != "NOT_CERTIFIED"):
        raise ValueError("independent reviewer status drift")
    proof_sha = _sha(source)
    cases_sha = _sha(cases_raw)
    prompts = {
        "schema_version": "1.0.0",
        "kind": "ADVERSARIAL_RESEARCH_USE_CARDS",
        "source_sha256": proof_sha,
        "casebook_sha256": cases_sha,
        "status": "NOT_AN_INDEPENDENT_ASSESSMENT",
        "instructions": (
            "For each scenario select one listed decision, record your reason "
            "and the source you actually inspected. Do not assert independence "
            "or claim to have solved a Millennium problem. Human assessment "
            "of argument quality and reviewer identity is mandatory."
        ),
        "decisions": list(DECISIONS),
        "cards": [
            {k: row[k] for k in (
                "case_id", "category", "claim", "scenario", "participant_task"
            )} for row in data["cases"]
        ],
    }
    blank = {
        "schema_version": "1.0.0",
        "kind": "ADVERSARIAL_RESEARCH_RESPONSE",
        "source_sha256": proof_sha,
        "casebook_sha256": cases_sha,
        "participant_label": "anonymous",
        "responses": [
            {"case_id": row["case_id"], "decision": "INCONCLUSIVE",
             "evidence_notes": "", "source_reference": ""}
            for row in data["cases"]
        ],
    }
    evaluation = None
    if response_path is not None:
        raw = response_path.read_bytes()
        if len(raw) > 40_000:
            raise ValueError("response size exceeds review budget")
        try:
            answers = json.loads(raw)
        except ValueError as error:
            raise ValueError("invalid behavioral response JSON") from error
        if type(answers) is not dict or set(answers) != SESSION_FIELDS:
            raise ValueError("response format does not match the protocol")
        if (answers["schema_version"] != "1.0.0" or
            answers["kind"] != "ADVERSARIAL_RESEARCH_RESPONSE" or
            answers["source_sha256"] != proof_sha or
            answers["casebook_sha256"] != cases_sha):
            raise ValueError("responses are not linked to the exact reviewed sources")
        label = answers["participant_label"]
        if type(label) is not str or not PSEUDONYM.fullmatch(label):
            raise ValueError("participant label must be a local pseudonym")
        rows = answers["responses"]
        if type(rows) is not list or len(rows) != len(KEYS):
            raise ValueError("responses must cover all seven use cases")
        indexed = {}
        for row in rows:
            if type(row) is not dict or set(row) != RESPONSE_FIELDS:
                raise ValueError("invalid response fields")
            cid = row["case_id"]
            if type(cid) is not str or cid not in KEYS or cid in indexed:
                raise ValueError("duplicate or unknown response case")
            if row["decision"] not in DECISIONS:
                raise ValueError("invalid review decision")
            _long(row["evidence_notes"], "mathematical evidence notes", 40, 2500)
            _long(row["source_reference"], "inspected source reference", 10, 500)
            indexed[cid] = row
        if set(indexed) != set(KEYS):
            raise ValueError("response case coverage incomplete")
        grades = []
        for row in data["cases"]:
            cid = row["case_id"]
            answer = indexed[cid]
            grades.append({
                "case_id": cid, "selected_decision": answer["decision"],
                "key_decision": KEYS[cid],
                "decision_key_match": answer["decision"] == KEYS[cid],
                "evidence_note_sha256": _sha(answer["evidence_notes"].encode()),
                "source_reference_sha256": _sha(answer["source_reference"].encode()),
                "human_mathematical_evaluation": "NOT_PERFORMED",
                "required_observations_for_human": row["required_observations"],
                "expert_independence_authenticated": False,
            })
        evaluation = {
            "status": "DECISION_LABEL_COMPARISON_ONLY",
            "decision_key_matches": sum(x["decision_key_match"] for x in grades),
            "total_cases": len(grades),
            "grades": grades,
            "behavioral_competence_verified": False,
            "independent_mathematical_review": "NOT_PERFORMED",
            "clay_solution": "NOT_CERTIFIED",
            "limitations": (
                "Matching a multiple-choice decision does not establish sound "
                "mathematical reasoning, actual reviewer behavior, reviewer "
                "independence, research novelty, or a valid Clay proof. "
                "Humans must inspect arguments and independently verify identity."
            ),
        }
    if (SAT_LEAN.read_bytes() != source or
        REGISTRATION_PATH.read_bytes() != registry_before or
        casebook_path.read_bytes() != cases_raw):
        raise RuntimeError("protected mathematical sources changed during card review")
    report = {
        "schema_version": "1.0.0",
        "card_count": len(KEYS),
        "source_sha256": proof_sha,
        "casebook_sha256": cases_sha,
        "study_status": "NOT_CONDUCTED_EXTERNALLY",
        "actual_independent_review": "NOT_VERIFIED",
        "clay_solution": "NOT_CERTIFIED",
        "evaluation": evaluation,
        "participant_instructions": prompts,
    }
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "participant_cards.json").write_text(
            json.dumps(prompts, indent=2, sort_keys=True) + "\n")
        (output_dir / "blank_responses.json").write_text(
            json.dumps(blank, indent=2, sort_keys=True) + "\n")
        (output_dir / "review_behavior_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/behavior"))
    args = parser.parse_args(argv)
    result = run_behavior_review(response_path=args.responses,
                                 output_dir=args.output_dir)
    print(json.dumps({
        "card_count": result["card_count"],
        "study_status": result["study_status"],
        "actual_independent_review": result["actual_independent_review"],
        "decision_key_matches": (
            result["evaluation"]["decision_key_matches"] if result["evaluation"]
            else None
        ),
        "clay_solution": "NOT_CERTIFIED",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
