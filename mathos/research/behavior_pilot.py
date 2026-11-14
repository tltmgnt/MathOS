"""Offline, double-rater SAT1 decision-behavior pilot; no human-study claims.

This script prepares a limited blinding package and checks *supplied* rater
rubric decisions for agreement. It does not conduct recruitment, obtain
consent, independently authenticate people, validate mathematical reasoning,
or prove a Clay Millennium result.

No participant response or rater statement is uploaded to any service.

python -m mathos.research.behavior_pilot --output-dir artifacts/behavior-pilot
python -m mathos.research.behavior_pilot --responses private/answers.json \
    --consent-attested --output-dir private/behavior-pilot
python -m mathos.research.behavior_pilot --responses private/answers.json \
    --consent-attested --rater-a private/a.json --rater-b private/b.json \
    --output-dir private/behavior-pilot
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from mathos.research.behavior_review import (
    CARDS_PATH, KEYS, _read_cases, run_behavior_review,
)
from mathos.research.hypothesis_pipeline import ROOT
from mathos.research.theorem_assurance import SAT_LEAN

PROTOCOL_PATH = ROOT / "docs/research/papers/SAT1_BEHAVIOR_PILOT_PROTOCOL.v1.json"
DIMENSIONS = (
    "observation_one_present", "observation_two_present",
    "source_reference_relevant",
)
POLICY = {
    "study_conducted": "NOT_INDEPENDENTLY_VERIFIED",
    "independence_authenticated": False,
    "human_rater_authenticity": "NOT_AUTHENTICATED",
    "behavioral_validation": "NOT_ESTABLISHED",
    "mathematical_review": "NOT_PERFORMED",
    "clay_solution": "NOT_CERTIFIED",
    "auto_promotion": False,
}
METHOD = {
    "design": "EXPLORATORY_UNVALIDATED_PILOT",
    "sampling": "NOT_RECRUITED",
    "consent": "OPERATOR_ATTESTATION_REQUIRED_NOT_AUTHENTICATED",
    "rater_blinding": (
        "CASE_AND_RESPONSIVE_JUSTIFICATION_VISIBLE_DECISION_LABEL_AND_PARTICIPANT_PSEUDONYM_HIDDEN"
    ),
    "participant_task": (
        "Seven written decision/explanation tasks bound to the exact Lean SHA-256 "
        "and casebook SHA-256"
    ),
    "outcome": (
        "Descriptive double-rater binary rubric agreement; no personal ability inference"
    ),
    "agreement": (
        "Observed percent agreement and Cohen kappa per dimension and pooled; "
        "undefined kappa emitted as null"
    ),
    "adjudication": "NOT_AUTOMATED",
    "preregistration": "IN_REPOSITORY_SPECIFICATION_ONLY_NOT_EXTERNALLY_REGISTERED",
    "controls": "NO_CONTROL_GROUP_NO_VALIDATED_COMPARISON",
}
RATING_FIELDS = {"case_id", "evidence_note_sha256", *DIMENSIONS, "rater_comment"}
RATER_FIELDS = {
    "schema_version", "kind", "protocol_sha256", "casebook_sha256",
    "source_sha256", "response_sha256", "rater_pseudonym",
    "independence_declaration", "conflicts_declaration", "ratings",
}
LABEL_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{1,30}\Z")
HEX_RE = re.compile(r"[a-f0-9]{64}\Z")


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    output = {}
    for k, v in pairs:
        if k in output:
            raise ValueError("duplicate JSON object key")
        output[k] = v
    return output


def _read_json(path: Path, *, limit: int = 65_536) -> tuple[dict, bytes]:
    data = path.read_bytes()
    if len(data) > limit:
        raise ValueError("input exceeds bounded study data limit")
    try:
        result = json.loads(data.decode("utf-8"),
                            object_pairs_hook=_pairs_no_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("invalid UTF-8 JSON") from error
    if type(result) is not dict:
        raise ValueError("expected JSON object")
    return result, data


def _read_protocol(path: Path) -> tuple[dict, bytes]:
    protocol, raw = _read_json(path)
    if set(protocol) != {
        "schema_version", "title", "purpose", "scope", "source_cardbook",
        "case_ids", "rater_count", "dimensions", "rubric", "method", "policy",
    }:
        raise ValueError("invalid pilot protocol fields")
    if (protocol["schema_version"] != "1.0.0" or
        protocol["scope"] != "SAT1_SEVEN_CASES_RESEARCH_DECISION_ONLY" or
        protocol["source_cardbook"] !=
            "docs/research/papers/SAT1_ADVERSARIAL_BEHAVIOR_CARDS.v1.json" or
        protocol["case_ids"] != list(KEYS) or
        type(protocol["rater_count"]) is not int or
        protocol["rater_count"] != 2 or
        protocol["dimensions"] != list(DIMENSIONS) or
        protocol["method"] != METHOD or protocol["policy"] != POLICY):
        raise ValueError("protocol attempts to change preregistered pilot bounds")
    if type(protocol["rubric"]) is not dict or set(protocol["rubric"]) != set(DIMENSIONS):
        raise ValueError("invalid rubric specification")
    if any(type(text) is not str or len(text) < 50
           for text in protocol["rubric"].values()):
        raise ValueError("rubric descriptions are missing")
    if type(protocol["purpose"]) is not str or len(protocol["purpose"]) < 55:
        raise ValueError("the pilot purpose cannot be obscured")
    return protocol, raw


def _rater_template(refs: dict, note_hashes: dict) -> dict:
    return {
        "schema_version": "1.0.0",
        "kind": "SAT1_DOUBLE_RATER_RUBRIC",
        **refs,
        "rater_pseudonym": "Rater_01",
        "independence_declaration": "SELF_DECLARED_NOT_AUTHENTICATED",
        "conflicts_declaration": "",
        "ratings": [
            {
                "case_id": cid,
                "evidence_note_sha256": note_hashes[cid],
                "observation_one_present": None,
                "observation_two_present": None,
                "source_reference_relevant": None,
                "rater_comment": "",
            }
            for cid in KEYS
        ],
    }


def _validate_rater(path: Path, refs: dict,
                    note_hashes: dict) -> tuple[dict, dict]:
    doc, raw = _read_json(path)
    if set(doc) != RATER_FIELDS or doc["schema_version"] != "1.0.0" or (
        doc["kind"] != "SAT1_DOUBLE_RATER_RUBRIC"
    ) or any(doc.get(k) != v for k, v in refs.items()):
        raise ValueError("rater record does not match study sources")
    pseudonym = doc["rater_pseudonym"]
    if type(pseudonym) is not str or not LABEL_RE.fullmatch(pseudonym):
        raise ValueError("rater pseudonym must be an unidentifying label")
    if doc["independence_declaration"] != "SELF_DECLARED_NOT_AUTHENTICATED":
        raise ValueError("unverified raters cannot promote themselves")
    conflicts = doc["conflicts_declaration"]
    if type(conflicts) is not str or not 30 <= len(conflicts.strip()) <= 900:
        raise ValueError("rater conflict declaration required")
    answers = doc["ratings"]
    if type(answers) is not list or len(answers) != len(KEYS):
        raise ValueError("each rater must assess all seven cases")
    indexed = {}
    for row in answers:
        if type(row) is not dict or set(row) != RATING_FIELDS:
            raise ValueError("invalid rater case fields")
        cid = row["case_id"]
        if type(cid) is not str or cid not in KEYS or cid in indexed:
            raise ValueError("duplicate or unknown rater case")
        if row["evidence_note_sha256"] != note_hashes[cid]:
            raise ValueError("rater assessment is not pinned to the response text")
        if any(type(row[k]) is not int or row[k] not in (0, 1)
               for k in DIMENSIONS):
            raise ValueError("rubric ratings must be actual binary decisions")
        comment = row["rater_comment"]
        if type(comment) is not str or not 35 <= len(comment.strip()) <= 1800:
            raise ValueError("rater case rationale cannot be empty")
        indexed[cid] = row
    return indexed, {
        "pseudonym": pseudonym,
        "rater_file_sha256": _digest(raw),
        "declaration_status": "SELF_DECLARED_NOT_AUTHENTICATED",
        "independence_authenticity": "NOT_VERIFIED",
    }


def _agreement(first: list[int], second: list[int]) -> dict:
    if not first or len(first) != len(second) or any(
        type(value) is not int or value not in (0, 1)
        for value in first + second
    ):
        raise ValueError("agreement requires paired binary observations")
    n = len(first)
    same = sum(a == b for a, b in zip(first, second))
    # Exact count-based computation; output rounded only for reporting.
    p_o = same / n
    count_a = sum(first)
    count_b = sum(second)
    p_e = (count_a * count_b + (n - count_a) * (n - count_b)) / (n * n)
    kappa = None if p_e == 1 else round((p_o - p_e) / (1 - p_e), 6)
    return {
        "pair_count": n,
        "agreeing_pairs": same,
        "observed_agreement": round(p_o, 6),
        "expected_chance_agreement": round(p_e, 6),
        "cohen_kappa": kappa,
        "kappa_defined": kappa is not None,
    }


def run_pilot(
    *, protocol_path: Path = PROTOCOL_PATH,
    response_path: Path | None = None,
    rater_a_path: Path | None = None,
    rater_b_path: Path | None = None,
    consent_attested: bool = False,
    output_dir: Path | None = None,
) -> dict:
    _, protocol_raw = _read_protocol(protocol_path)
    cards, cards_raw = _read_cases(CARDS_PATH)
    lean_raw = SAT_LEAN.read_bytes()
    refs = {
        "protocol_sha256": _digest(protocol_raw),
        "casebook_sha256": _digest(cards_raw),
        "source_sha256": _digest(lean_raw),
    }
    if (rater_a_path is None) != (rater_b_path is None):
        raise ValueError("two independently completed rater files are required")
    if response_path is not None:
        # Personal data must not be staged in the tracked repository, even
        # by accident through the default artifacts/ output location.
        root = ROOT.resolve()
        for candidate in (response_path, output_dir):
            if candidate is not None:
                resolved = candidate.resolve()
                if resolved == root or root in resolved.parents:
                    raise ValueError(
                        "participant responses and blinded packets must stay "
                        "outside the MathOS repository"
                    )
    elif output_dir is not None and (
        (output_dir / "private_blinded_rater_packet.json").exists() or
        (output_dir / "private_rater_template.json").exists()
    ):
        raise ValueError("previous private participant data remains in output directory")
    if response_path is None and (rater_a_path is not None or consent_attested):
        raise ValueError("consent/rating cannot occur without participant data")
    report = {
        "schema_version": "1.0.0",
        "pilot_status": "PROTOCOL_ONLY_NO_HUMAN_DATA",
        "research_scope": "EXPLORATORY_UNVALIDATED_PILOT",
        **refs,
        "participant_data_present": False,
        "operator_consent_attestation": False,
        "independent_participants_authenticated": False,
        "independent_raters_authenticated": False,
        "expert_mathematical_review": "NOT_PERFORMED",
        "behavioral_instrument_validated": False,
        "clay_solution": "NOT_CERTIFIED",
        "inter_rater_metrics": None,
        "limitations": (
            "No automated evidence can establish informed consent, external "
            "research independence, reviewer qualifications or mathematical truth. "
            "Without human validation and matched controls, these are at most "
            "exploratory inter-rater agreement calculations."
        ),
    }
    blinded = None
    rater_template = None
    if response_path is not None:
        if consent_attested is not True:
            raise ValueError("operator must attest participant consent before handling response")
        # Reuse the stricter 7-case input validation and the source-linked hash.
        run_behavior_review(response_path=response_path)
        response, response_raw = _read_json(response_path)
        if response["casebook_sha256"] != refs["casebook_sha256"] or (
            response["source_sha256"] != refs["source_sha256"]
        ):
            raise ValueError("participant response does not match the piloted source")
        by_case = {r["case_id"]: r for r in response["responses"]}
        note_hashes = {
            cid: _digest(by_case[cid]["evidence_notes"].encode("utf-8"))
            for cid in KEYS
        }
        response_digest = _digest(response_raw)
        bound = {**refs, "response_sha256": response_digest}
        blinded = {
            "schema_version": "1.0.0",
            "kind": "BLINDED_JUSTIFICATION_RATER_PACKET",
            **bound,
            "blinding_limits": (
                "Participant pseudonym, decision labels and answer keys hidden. "
                "Free-text notes may still disclose choices or identities."
            ),
            "cases": [
                {
                    "case_id": row["case_id"],
                    "scenario": row["scenario"],
                    "claim": row["claim"],
                    "evidence_notes": by_case[row["case_id"]]["evidence_notes"],
                    "source_reference": by_case[row["case_id"]]["source_reference"],
                    "evidence_note_sha256": note_hashes[row["case_id"]],
                    "rubric_observations": row["required_observations"],
                }
                for row in cards["cases"]
            ],
        }
        rater_template = _rater_template(bound, note_hashes)
        report.update({
            "pilot_status": "BLINDED_PACKET_PREPARED_UNAUTHENTICATED",
            "participant_data_present": True,
            "operator_consent_attestation": True,
            "response_sha256": response_digest,
            "response_handling": "LOCAL_PRIVATE_DATA_NOT_FOR_CI_ARTIFACT_UPLOAD",
        })
        if rater_a_path is not None:
            a, a_meta = _validate_rater(rater_a_path, bound, note_hashes)
            b, b_meta = _validate_rater(rater_b_path, bound, note_hashes)
            if a_meta["pseudonym"] == b_meta["pseudonym"] or (
                a_meta["rater_file_sha256"] == b_meta["rater_file_sha256"]
            ):
                raise ValueError("duplicate rater identifier or identical submissions")
            # These are source-pinned supplied ratings, not authenticated people.
            aggregates = {}
            for dim in DIMENSIONS:
                aggregates[dim] = _agreement(
                    [a[cid][dim] for cid in KEYS],
                    [b[cid][dim] for cid in KEYS],
                )
            aggregates["pooled"] = _agreement(
                [a[cid][dim] for cid in KEYS for dim in DIMENSIONS],
                [b[cid][dim] for cid in KEYS for dim in DIMENSIONS],
            )
            report.update({
                "pilot_status": "DOUBLE_RATINGS_RECEIVED_UNAUTHENTICATED",
                "rater_receipts": [a_meta, b_meta],
                "inter_rater_metrics": aggregates,
                "adjudication": "REQUIRES_SEPARATE_HUMAN_REVIEW",
                "mathematical_reasoning_quality": "NOT_AUTOMATICALLY_JUDGED",
                "study_conducted_independently": "NOT_VERIFIED",
            })
    if (protocol_path.read_bytes() != protocol_raw or
        CARDS_PATH.read_bytes() != cards_raw or
        SAT_LEAN.read_bytes() != lean_raw):
        raise RuntimeError("pilot sources changed during evidence generation")
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "pilot_status.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if blinded is not None and rater_template is not None:
            (output_dir / "private_blinded_rater_packet.json").write_text(
                json.dumps(blinded, indent=2, sort_keys=True) + "\n",
                encoding="utf-8")
            (output_dir / "private_rater_template.json").write_text(
                json.dumps(rater_template, indent=2, sort_keys=True) + "\n",
                encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", type=Path)
    parser.add_argument("--rater-a", type=Path)
    parser.add_argument("--rater-b", type=Path)
    parser.add_argument("--consent-attested", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/behavior-pilot"))
    args = parser.parse_args(argv)
    result = run_pilot(
        response_path=args.responses, rater_a_path=args.rater_a,
        rater_b_path=args.rater_b, consent_attested=args.consent_attested,
        output_dir=args.output_dir,
    )
    print(json.dumps({
        "pilot_status": result["pilot_status"],
        "independent_raters_authenticated": False,
        "inter_rater_metrics": result["inter_rater_metrics"],
        "clay_solution": "NOT_CERTIFIED",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
