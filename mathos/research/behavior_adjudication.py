"""Human-only disagreement adjudication for the SAT1 two-rater behavioral pilot.

No data are recruited, sampled, certified, or submitted automatically.
The program cannot authenticate participant consent, rater identities, expert
credentials or the mathematical content of their judgments.

Protocol-only CI (no participant data):
  python -m mathos.research.behavior_adjudication --output-dir artifacts/adjudication

Private, consent-attested rater disagreement handoff (outside repository):
  python -m mathos.research.behavior_adjudication --responses /private/answers.json \
      --rater-a /private/a.json --rater-b /private/b.json --consent-attested \
      --output-dir /private/adjudication

Once an actual outside adjudicator has independently authored a verdict file:
  ... --adjudicator /private/adjudicator.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from mathos.research.behavior_pilot import (
    DIMENSIONS, PROTOCOL_PATH, _read_json, _read_protocol, _validate_rater,
    run_pilot,
)
from mathos.research.behavior_review import CARDS_PATH, KEYS, _read_cases
from mathos.research.hypothesis_pipeline import ROOT
from mathos.research.theorem_assurance import SAT_LEAN

ADJUDICATION_PROTOCOL = ROOT / (
    "docs/research/papers/SAT1_BEHAVIOR_ADJUDICATION_PROTOCOL.v1.json"
)
ADJUDICATION_POLICY = {
    "human_consent_verified": False,
    "rater_independence_verified": False,
    "adjudicator_independence_verified": False,
    "study_validated": False,
    "mathematical_review_completed": False,
    "clay_solution": "NOT_CERTIFIED",
    "auto_certification": False,
}
REQUIRED_FIELDS = {
    "schema_version", "kind", "protocol_sha256", "casebook_sha256",
    "source_sha256", "response_sha256", "rater_a_sha256", "rater_b_sha256",
    "adjudication_protocol_sha256", "adjudicator_pseudonym",
    "independence_declaration", "conflicts_declaration", "decisions",
}
DECISION_FIELDS = {
    "case_id", "dimension", "evidence_note_sha256",
    "adjudicated_value", "explanation", "source_reference",
}
LABEL = re.compile(r"[A-Za-z][A-Za-z0-9_-]{1,30}\Z")


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _check_private(path: Path) -> None:
    resolved = path.resolve()
    root = ROOT.resolve()
    if resolved == root or root in resolved.parents:
        raise ValueError(
            "participant, rater and adjudication records must stay "
            "outside the MathOS repository"
        )


def _read_adjudication_protocol(path: Path) -> tuple[dict, bytes]:
    spec, raw = _read_json(path)
    if set(spec) != {
        "schema_version", "scope", "source_pilot_protocol",
        "case_ids", "dimensions", "adjudication_policy",
        "method", "policy",
    }:
        raise ValueError("adjudication protocol schema drift")
    if (spec["schema_version"] != "1.0.0" or
        spec["scope"] != "SAT1_PILOT_DISAGREEMENT_ONLY" or
        spec["source_pilot_protocol"] !=
            "docs/research/papers/SAT1_BEHAVIOR_PILOT_PROTOCOL.v1.json" or
        spec["case_ids"] != list(KEYS) or
        spec["dimensions"] != list(DIMENSIONS) or
        spec["adjudication_policy"] != "HUMAN_EXPLICIT_DECISIONS_NO_AUTO_RESOLUTION" or
        spec["policy"] != ADJUDICATION_POLICY):
        raise ValueError("adjudication protocol may not promote peer review or Clay proof")
    if type(spec["method"]) is not dict or set(spec["method"]) != {
        "disagreement_identification", "adjudicator_inputs",
        "analysis", "privacy", "limitations",
    } or any(
        type(value) is not str or len(value.strip()) < 55
        for value in spec["method"].values()
    ):
        raise ValueError("adjudication methodology incomplete")
    return spec, raw


def run_adjudication(
    *, response_path: Path | None = None,
    rater_a_path: Path | None = None,
    rater_b_path: Path | None = None,
    adjudicator_path: Path | None = None,
    consent_attested: bool = False,
    output_dir: Path | None = None,
    protocol_path: Path = ADJUDICATION_PROTOCOL,
) -> dict:
    _, spec_raw = _read_adjudication_protocol(protocol_path)
    _, pilot_protocol_raw = _read_protocol(PROTOCOL_PATH)
    cards, cards_raw = _read_cases(CARDS_PATH)
    lean_raw = SAT_LEAN.read_bytes()
    sources = {
        "adjudication_protocol_sha256": _hash(spec_raw),
        "protocol_sha256": _hash(pilot_protocol_raw),
        "casebook_sha256": _hash(cards_raw),
        "source_sha256": _hash(lean_raw),
    }
    provided = (response_path, rater_a_path, rater_b_path)
    if any(p is not None for p in provided) and not all(
        p is not None for p in provided
    ):
        raise ValueError("a response and two complete rater records are required")
    if adjudicator_path is not None and response_path is None:
        raise ValueError("adjudicator input requires two prior ratings")
    if response_path is not None and not consent_attested:
        raise ValueError("operator consent attestation is required before reading responses")
    for path in (response_path, rater_a_path, rater_b_path, adjudicator_path):
        if path is not None:
            _check_private(path)
    if response_path is not None and output_dir is not None:
        _check_private(output_dir)

    report = {
        "schema_version": "1.0.0",
        "status": "PROTOCOL_ONLY_NO_HUMAN_DATA",
        "scope": "EXPLORATORY_DISAGREEMENT_ADJUDICATION",
        **sources,
        "participant_data_present": False,
        "rater_disagreement_count": 0,
        "human_adjudication_file_supplied": False,
        "independent_humans_authenticated": False,
        "human_consent_authenticated": False,
        "study_validated": False,
        "independent_mathematical_peer_review": "NOT_PERFORMED",
        "clay_solution": "NOT_CERTIFIED",
        "limitations": (
            "The script only validates supplied files and tracks rater disagreements. "
            "It cannot authenticate informed consent, human identity, mathematical "
            "expertise or scholarly independence; it is not a Clay proof audit."
        ),
    }
    disagreement_packet = None
    blank_decisions = None
    if response_path is not None:
        upstream = run_pilot(
            response_path=response_path,
            rater_a_path=rater_a_path,
            rater_b_path=rater_b_path,
            consent_attested=True,
        )
        if upstream["pilot_status"] != "DOUBLE_RATINGS_RECEIVED_UNAUTHENTICATED":
            raise ValueError("cannot adjudicate incomplete pilot rating evidence")
        answer, response_raw = _read_json(response_path)
        original_a, a_raw = _read_json(rater_a_path)
        original_b, b_raw = _read_json(rater_b_path)
        receipt = {
            "protocol_sha256": sources["protocol_sha256"],
            "casebook_sha256": sources["casebook_sha256"],
            "source_sha256": sources["source_sha256"],
            "response_sha256": _hash(response_raw),
        }
        by_case = {item["case_id"]: item for item in answer["responses"]}
        note_hashes = {
            cid: _hash(by_case[cid]["evidence_notes"].encode("utf-8"))
            for cid in KEYS
        }
        a, a_meta = _validate_rater(rater_a_path, receipt, note_hashes)
        b, b_meta = _validate_rater(rater_b_path, receipt, note_hashes)
        if a_meta["pseudonym"] == b_meta["pseudonym"]:
            raise ValueError("cannot adjudicate duplicate rater identities")
        receipt.update({
            "rater_a_sha256": _hash(a_raw),
            "rater_b_sha256": _hash(b_raw),
            "adjudication_protocol_sha256": sources["adjudication_protocol_sha256"],
        })
        by_card = {card["case_id"]: card for card in cards["cases"]}
        disagreements = []
        for cid in KEYS:
            for dim in DIMENSIONS:
                if a[cid][dim] != b[cid][dim]:
                    disagreements.append({
                        "case_id": cid,
                        "dimension": dim,
                        "claim": by_card[cid]["claim"],
                        "scenario": by_card[cid]["scenario"],
                        "required_observations": by_card[cid]["required_observations"],
                        "evidence_notes": by_case[cid]["evidence_notes"],
                        "source_reference": by_case[cid]["source_reference"],
                        "evidence_note_sha256": note_hashes[cid],
                        "rater_one_value": a[cid][dim],
                        "rater_two_value": b[cid][dim],
                        "rater_one_reason": a[cid]["rater_comment"],
                        "rater_two_reason": b[cid]["rater_comment"],
                    })
        disagreement_packet = {
            "schema_version": "1.0.0",
            "kind": "PRIVATE_HUMAN_ADJUDICATION_HANDOFF",
            **receipt,
            "warning": (
                "Contains actual participant response text and rater reasons. "
                "Do not publish; partial blinding cannot remove identifying "
                "information embedded in free text."
            ),
            "disagreements": disagreements,
        }
        blank_decisions = {
            "schema_version": "1.0.0",
            "kind": "SAT1_HUMAN_ADJUDICATION_RECORD",
            **receipt,
            "adjudicator_pseudonym": "Adjudicator_01",
            "independence_declaration": "SELF_DECLARED_NOT_AUTHENTICATED",
            "conflicts_declaration": "",
            "decisions": [{
                "case_id": row["case_id"],
                "dimension": row["dimension"],
                "evidence_note_sha256": row["evidence_note_sha256"],
                "adjudicated_value": None,
                "explanation": "",
                "source_reference": "",
            } for row in disagreements],
        }
        report.update({
            "participant_data_present": True,
            "response_sha256": receipt["response_sha256"],
            "rater_a_sha256": receipt["rater_a_sha256"],
            "rater_b_sha256": receipt["rater_b_sha256"],
            "operator_consent_attested": True,
            "rater_disagreement_count": len(disagreements),
            "status": (
                "DISAGREEMENTS_REQUIRE_HUMAN_ADJUDICATION"
                if disagreements else "NO_RATER_DISAGREEMENTS_UNAUTHENTICATED"
            ),
            "upstream_agreement": upstream["inter_rater_metrics"],
        })
        if adjudicator_path is not None:
            if not disagreements:
                raise ValueError("no disagreements to adjudicate")
            decision, decision_raw = _read_json(adjudicator_path)
            if set(decision) != REQUIRED_FIELDS or (
                decision["schema_version"] != "1.0.0" or
                decision["kind"] != "SAT1_HUMAN_ADJUDICATION_RECORD"
            ) or any(decision.get(k) != value for k, value in receipt.items()):
                raise ValueError("adjudicator record is not pinned to exact evidence")
            label = decision["adjudicator_pseudonym"]
            if (type(label) is not str or not LABEL.fullmatch(label) or
                label in (a_meta["pseudonym"], b_meta["pseudonym"])):
                raise ValueError("adjudicator pseudonym must differ from rater labels")
            if decision["independence_declaration"] != (
                "SELF_DECLARED_NOT_AUTHENTICATED"
            ):
                raise ValueError("independence cannot be self-certified")
            conflict = decision["conflicts_declaration"]
            if type(conflict) is not str or not 35 <= len(conflict.strip()) <= 900:
                raise ValueError("adjudicator conflict disclosure required")
            expected = {
                (d["case_id"], d["dimension"]): d["evidence_note_sha256"]
                for d in disagreements
            }
            got = set()
            rows = decision["decisions"]
            if type(rows) is not list or len(rows) != len(expected):
                raise ValueError("adjudication must cover all and only disputed judgments")
            for row in rows:
                if type(row) is not dict or set(row) != DECISION_FIELDS:
                    raise ValueError("adjudication row schema violation")
                key = (row["case_id"], row["dimension"])
                if key not in expected or key in got:
                    raise ValueError("duplicated or invented adjudication decision")
                got.add(key)
                if row["evidence_note_sha256"] != expected[key]:
                    raise ValueError("disputed text was changed")
                if type(row["adjudicated_value"]) is not int or (
                    row["adjudicated_value"] not in (0, 1)
                ):
                    raise ValueError("adjudication requires an explicit 0/1 judgment")
                for field, low, high in (
                    ("explanation", 45, 2500), ("source_reference", 10, 700)
                ):
                    value = row[field]
                    if type(value) is not str or not low <= len(value.strip()) <= high:
                        raise ValueError("missing meaningful adjudication rationale or source")
            if got != set(expected):
                raise ValueError("incomplete adjudication")
            report.update({
                "status": "ADJUDICATION_SUBMITTED_BUT_NOT_AUTHENTICATED",
                "human_adjudication_file_supplied": True,
                "adjudicator_file_sha256": _hash(decision_raw),
                "adjudicated_disagreement_count": len(got),
                "adjudicator_identity_status": "NOT_VERIFIED",
                "rater_independence_status": "NOT_VERIFIED",
                "mathematical_soundness_of_adjudication": "NOT_AUTOMATICALLY_JUDGED",
            })
        if (response_path.read_bytes() != response_raw or
            rater_a_path.read_bytes() != a_raw or
            rater_b_path.read_bytes() != b_raw):
            raise RuntimeError("private evidence changed during adjudication")
    if (protocol_path.read_bytes() != spec_raw or
        PROTOCOL_PATH.read_bytes() != pilot_protocol_raw or
        CARDS_PATH.read_bytes() != cards_raw or
        SAT_LEAN.read_bytes() != lean_raw):
        raise RuntimeError("protected mathematical or pilot source changed")
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "adjudication_status.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        if disagreement_packet is not None:
            (output_dir / "private_disagreement_packet.json").write_text(
                json.dumps(disagreement_packet, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            (output_dir / "private_adjudicator_template.json").write_text(
                json.dumps(blank_decisions, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", type=Path)
    parser.add_argument("--rater-a", type=Path)
    parser.add_argument("--rater-b", type=Path)
    parser.add_argument("--adjudicator", type=Path)
    parser.add_argument("--consent-attested", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/adjudication"))
    args = parser.parse_args(argv)
    report = run_adjudication(
        response_path=args.responses, rater_a_path=args.rater_a,
        rater_b_path=args.rater_b, adjudicator_path=args.adjudicator,
        consent_attested=args.consent_attested, output_dir=args.output_dir,
    )
    print(json.dumps({
        "status": report["status"],
        "rater_disagreement_count": report["rater_disagreement_count"],
        "independent_humans_authenticated": False,
        "clay_solution": report["clay_solution"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
