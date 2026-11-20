"""Publication-scope audit for TECT-X Selmer-infinitude research.

The status file is a *declaration*, not a proof checker. By default this
tool reports blockers and exits 0 so CI can audit the open project.
With --require-ready it exits 2 unless all documented, human-reviewed
submission requirements are marked complete and backed by evidence.
It never asserts that the mathematics is true from booleans alone.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATUS = ROOT / "docs/research/papers/TECT_X_SUBMISSION_STATUS.v1.json"

REQUIRED = (
    "main_theorem_proved",
    "global_descent_verified",
    "independent_specialist_review",
    "novelty_and_priority_confirmed",
    "authorship_and_rights_confirmed",
    "journal_format_and_bibliography_checked",
)


def evaluate_status(payload: Any) -> dict:
    if not isinstance(payload, dict) or payload.get("schema_version") != "1.0":
        raise ValueError("expected TECT-X submission status version 1.0")
    gates = payload.get("gates")
    evidence = payload.get("gate_evidence")
    claims = payload.get("claims")
    publication = payload.get("publication")
    if not isinstance(gates, dict) or not isinstance(evidence, dict):
        raise ValueError("gates and evidence maps are required")
    if not isinstance(claims, dict) or not isinstance(publication, dict):
        raise ValueError("claims and publication maps are required")
    if set(gates) != set(REQUIRED) or set(evidence) != set(REQUIRED):
        raise ValueError("unrecognized or missing required gate")
    if any(type(value) is not bool for value in gates.values()):
        raise ValueError("every gate must be an exact boolean")
    if any(
        not isinstance(item, dict) or type(item.get("established")) is not bool
        for item in claims.values()
    ):
        raise ValueError("claims must each have a boolean established flag")
    if type(publication.get("journal_submission_authorized")) is not bool:
        raise ValueError("submission authorization must be a boolean")
    if type(publication.get("submitted")) is not bool:
        raise ValueError("submitted must be a boolean")

    blockers = []
    for key in REQUIRED:
        if not gates[key]:
            blockers.append(f"{key}: not completed")
        if gates[key] and (not isinstance(evidence[key], str) or not evidence[key].strip()):
            blockers.append(f"{key}: completed flag lacks evidence URI or path")

    theorem = claims.get("unconditional_infinite_selmer3")
    if not theorem or not theorem["established"]:
        blockers.append("unconditional infinite Selmer-3 theorem is open")
    elif not isinstance(theorem.get("source"), str) or not theorem["source"].strip():
        blockers.append("claimed infinite Selmer-3 theorem lacks a proof-artifact reference")
    if not payload.get("prior_art", {}).get("novelty_audit_complete", False):
        blockers.append("full novelty audit incomplete")

    ready = not blockers
    if publication["journal_submission_authorized"] and not ready:
        raise ValueError("submission authorization contradicts open proof/review gates")
    if publication["submitted"] and not publication["journal_submission_authorized"]:
        raise ValueError("submitted flag contradicts missing authorization")
    return {
        "project": payload.get("project"),
        "status": "READY_FOR_HUMAN_SUBMISSION_REVIEW" if ready else "BLOCKED",
        "required_gates": len(REQUIRED),
        "blockers": blockers,
        "proof_verified_by_software": False,
        "journal_submission_authorized": publication["journal_submission_authorized"],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--status-file", type=Path, default=DEFAULT_STATUS)
    p.add_argument("--require-ready", action="store_true")
    args = p.parse_args(argv)
    result = evaluate_status(json.loads(args.status_file.read_text(encoding="utf-8")))
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2 if args.require_ready and result["status"] != "READY_FOR_HUMAN_SUBMISSION_REVIEW" else 0


if __name__ == "__main__":
    raise SystemExit(main())
