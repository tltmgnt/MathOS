"""Evidence-preserving external SAT1 review intake, not an expert-review substitute.

A GitHub invitation is not independent review. A submitted review is not
an authenticated expert assessment merely because it passes a JSON schema.
Only real human scholarly review can establish mathematical significance.

python -m mathos.research.external_review --output-dir artifacts/external-review
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from mathos.research.hypothesis_pipeline import ROOT
from mathos.research.paper_packet import audit_paper_packet

LEDGER_PATH = ROOT / "docs/research/papers/SAT1_INDEPENDENT_REVIEW_REGISTER.v1.json"
ISSUE_RE = re.compile(r"https://github\.com/tltmgnt/MathOS/issues/[1-9][0-9]*\Z")
EVIDENCE_RE = re.compile(
    r"https://github\.com/tltmgnt/MathOS/"
    r"(?:issues/[1-9][0-9]*#issuecomment-[1-9][0-9]*"
    r"|pull/[1-9][0-9]*(?:#issuecomment-[1-9][0-9]*)?)\Z"
)
HANDLE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}\Z")
HEX_RE = re.compile(r"[a-f0-9]{64}\Z")
DATE_RE = re.compile(r"20[0-9]{2}-[01][0-9]-[0-3][0-9]\Z")
POLICY = {
    "review_request": "PUBLIC_OPEN_CALL_NOT_INDEPENDENT_ASSESSMENT",
    "expert_verdict": "NOT_INDEPENDENTLY_VALIDATED",
    "independent_reviewer_verified": False,
    "mathematical_novelty": "NOT_ESTABLISHED",
    "theorem_claim_promotion": False,
    "journal_submission": "NOT_SUBMITTED",
    "clay_solution": "NOT_CERTIFIED",
}
REVIEW_FIELDS = {
    "review_id", "reviewer_github_handle", "external_review_url",
    "reviewer_affiliation_or_background", "reviewer_self_declares_independence",
    "conflicts_of_interest", "review_date_utc", "source_sha256",
    "lean_replay_description", "formal_statement_assessment",
    "mathematical_criticism", "prior_art_findings", "sat_complexity_assessment",
    "recommendation",
}
VERDICTS = {
    "LIMITED_SCOPE_ACCEPTABLE", "REQUEST_REVISIONS", "REJECT_UNSUPPORTED_CLAIMS",
    "INCONCLUSIVE",
}


def _long_text(value: object, name: str, minimum: int = 40) -> None:
    if type(value) is not str or not minimum <= len(value.strip()) <= 5000:
        raise ValueError(f"missing meaningful {name}")


def audit_external_reviews(
    *, ledger_path: Path = LEDGER_PATH,
    output_dir: Path | None = None,
    verify_lean: bool = False,
) -> dict:
    raw = ledger_path.read_bytes()
    data = json.loads(raw)
    if type(data) is not dict or set(data) != {
        "schema_version", "scope", "policy", "review_request_url",
        "reviews", "note",
    }:
        raise ValueError("external review ledger schema changed")
    if (data["schema_version"] != "1.0.0" or
        data["scope"] != "SAT1_CHOICE_WORD_SUPPORT_ONLY" or
        data["policy"] != POLICY):
        raise ValueError("external review ledger falsely claims expert validation")
    _long_text(data["note"], "no-review-is-validation warning")
    request_url = data["review_request_url"]
    if request_url is not None and (
        type(request_url) is not str or not ISSUE_RE.fullmatch(request_url)
    ):
        raise ValueError("only a MathOS GitHub issue can be the public call")
    reviews = data["reviews"]
    if type(reviews) is not list or len(reviews) > 16:
        raise ValueError("external review records exceed bounded schema")
    packet = audit_paper_packet(verify_lean=verify_lean)
    expected_sha = packet["sources_sha256"]["formal_lean_source"]
    summaries = []
    identifiers: set[str] = set()
    evidence_urls: set[str] = set()
    for entry in reviews:
        if type(entry) is not dict or set(entry) != REVIEW_FIELDS:
            raise ValueError("external review submission is not fully traceable")
        rid = entry["review_id"]
        if type(rid) is not str or not re.fullmatch(r"EXTREV-[0-9]{4}", rid):
            raise ValueError("invalid review identifier")
        if rid in identifiers:
            raise ValueError("duplicate external review identifier")
        identifiers.add(rid)
        handle = entry["reviewer_github_handle"]
        if (type(handle) is not str or not HANDLE_RE.fullmatch(handle) or
            handle.lower() in {"tltmgnt", "github-actions", "dependabot"}):
            raise ValueError("reviewer cannot be the repository maintainer or automation")
        origin = entry["external_review_url"]
        if type(origin) is not str or not EVIDENCE_RE.fullmatch(origin):
            raise ValueError("external evidence must have a public review URL")
        if origin in evidence_urls:
            raise ValueError("duplicate reviewer evidence URL")
        evidence_urls.add(origin)
        if entry["reviewer_self_declares_independence"] is not True:
            raise ValueError("reviewer must explicitly declare independence")
        for key in (
            "reviewer_affiliation_or_background", "conflicts_of_interest",
            "lean_replay_description", "formal_statement_assessment",
            "mathematical_criticism", "prior_art_findings",
            "sat_complexity_assessment",
        ):
            _long_text(entry[key], key)
        if (type(entry["review_date_utc"]) is not str or
            not DATE_RE.fullmatch(entry["review_date_utc"])):
            raise ValueError("missing dated external review")
        sha = entry["source_sha256"]
        if type(sha) is not str or not HEX_RE.fullmatch(sha):
            raise ValueError("missing exact Lean reviewed-source SHA-256")
        if entry["recommendation"] not in VERDICTS:
            raise ValueError("reviewer recommendation cannot assert Clay proof")
        summaries.append({
            "review_id": rid,
            "reviewer_github_handle": handle,
            "external_review_url": origin,
            "review_date_utc": entry["review_date_utc"],
            "reviewer_claimed_verdict": entry["recommendation"],
            "reviewed_exact_current_lean_source": sha == expected_sha,
            "independence_authentication": "REQUIRES_HUMAN_VERIFICATION",
            "review_authenticity": "REQUIRES_HUMAN_VERIFICATION",
            "mathematical_validity_of_review": "NOT_AUTOMATICALLY_ASSESSED",
            "expert_acceptance_recorded": False,
        })

    if ledger_path.read_bytes() != raw:
        raise RuntimeError("external review register mutated during audit")
    report = {
        "schema_version": "1.0.0",
        "scope": "SAT1_CHOICE_WORD_SUPPORT_ONLY",
        "review_request_url": request_url,
        "review_request_status": (
            "PUBLIC_INVITATION_POSTED_NOT_REVIEWED" if request_url else
            "INVITATION_NOT_YET_PUBLISHED"
        ),
        "submitted_external_review_count": len(summaries),
        "authenticated_independent_expert_review_count": 0,
        "independent_mathematical_assessment": "NOT_VERIFIED",
        "literature_novelty": "NOT_ESTABLISHED",
        "clay_solution": "NOT_CERTIFIED",
        "formal_status": packet["formal_status"],
        "proof_source_sha256": expected_sha,
        "review_register_sha256": hashlib.sha256(raw).hexdigest(),
        "reviews": summaries,
        "limitations": (
            "A URL and self-attestation do not authenticate a person or "
            "their professional independence. No automated verdict promotes "
            "a theorem; real independent specialists must author, reproduce, "
            "and review their findings, with a separate human provenance check."
        ),
    }
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "external_review_status.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/external-review"))
    parser.add_argument("--verify-lean", action="store_true")
    args = parser.parse_args(argv)
    report = audit_external_reviews(
        output_dir=args.output_dir, verify_lean=args.verify_lean,
    )
    print(json.dumps({
        "review_request_status": report["review_request_status"],
        "submitted_external_review_count": report["submitted_external_review_count"],
        "independent_mathematical_assessment": report["independent_mathematical_assessment"],
        "clay_solution": report["clay_solution"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
