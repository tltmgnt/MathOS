"""Build a reproducible SAT1 specialist-review packet; never a Clay submission.

This package contains the published-source links and the precise Lean-checked
limited combinatorial theorem, plus human-review blanks and a fail-closed
research-status manifest. It does not perform peer review or a novelty search.

    python -m mathos.research.paper_packet --output-dir artifacts/paper
    python -m mathos.research.paper_packet --verify-lean --output-dir artifacts/paper
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from mathos.research.hypothesis_pipeline import ROOT
from mathos.research.theorem_assurance import (
    SAT_LEAN, THEOREMS_PATH, audit_theorem_assurance,
)

PAPER_DIR = ROOT / "docs/research/papers"
PAPER_PATH = PAPER_DIR / "SAT1_FORMAL_NOTE.md"
LEDGER_PATH = PAPER_DIR / "SAT1_LITERATURE_LEDGER.v1.json"
REVIEW_PATH = PAPER_DIR / "SAT1_EXTERNAL_REVIEW.md"

REFERENCE_URLS = {
    "R1": "https://doi.org/10.1145/800157.805047",
    "R2": "https://doi.org/10.1145/237814.237860",
    "R3": "https://eccc.weizmann.ac.il/report/2014/052/",
    "R4": "https://www.claymath.org/millennium-problems/rules/",
}
LEDGER_POLICY = {
    "reference_discovery": "INITIAL_TARGETED_DISCOVERY_ONLY",
    "systematic_prior_art_search": "NOT_COMPLETED",
    "full_text_expert_review": "NOT_PERFORMED",
    "novelty_determination": "NOT_INDEPENDENTLY_ASSESSED",
    "external_review": "NOT_PERFORMED",
    "submission": "NOT_SUBMITTED",
    "clay_solution": "NOT_ESTABLISHED",
    "auto_promotion": False,
}
PAPER_SENTINELS = (
    "REVIEW_DRAFT_NOT_SUBMITTED",
    "No claim of mathematical novelty or a solution to P versus NP.",
    "MathOS.satSupport_certificate",
    "SAT1_LITERATURE_LEDGER.v1.json",
    "SAT1_EXTERNAL_REVIEW.md",
    "not a new complexity-theoretic breakthrough",
    "**Not proved**",
    "not presently kernel-checked",
    "not a complete",
)
# Keep required scientific denials independent of capitalization/typography:
PAPER_WORDS = (
    "full embedding", "not formalized", "unrestricted SAT",
    "not establish", "independent review", "not submitted",
)
REVIEW_SENTINELS = (
    "REVIEW_READY_NOT_SUBMISSION_READY",
    "No reviewer has been recruited or contacted",
    "NOT_PROVIDED",
    "NOT_INDEPENDENTLY_REPLAYED",
    "NOT_ASSESSED",
    "NOT_REVIEWED",
    "NOT_REQUESTED",
    "Never represent this packet as a submission",
)


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_set(value: object, expected: set[str], label: str) -> dict:
    if type(value) is not dict or set(value) != expected:
        raise ValueError(f"invalid {label} schema")
    return value


def audit_paper_packet(
    *, paper_path: Path = PAPER_PATH,
    ledger_path: Path = LEDGER_PATH,
    review_path: Path = REVIEW_PATH,
    lean_path: Path = SAT_LEAN,
    theorem_path: Path = THEOREMS_PATH,
    output_dir: Path | None = None,
    verify_lean: bool = False,
) -> dict:
    protected = {
        "manuscript": paper_path, "literature_ledger": ledger_path,
        "review_protocol": review_path, "formal_lean_source": lean_path,
        "theorem_assurance_registry": theorem_path,
    }
    raw = {key: path.read_bytes() for key, path in protected.items()}
    try:
        paper = raw["manuscript"].decode("utf-8")
        review = raw["review_protocol"].decode("utf-8")
        ledger = json.loads(raw["literature_ledger"])
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("invalid review packet encoding or ledger JSON") from exc

    if len(paper) < 4500 or len(paper) > 80_000:
        raise ValueError("manuscript length outside research-review bounds")
    if not all(needle in paper for needle in PAPER_SENTINELS):
        raise ValueError("manuscript lost required result, source or non-solution disclosures")
    if not all(needle in paper.lower() for needle in PAPER_WORDS):
        raise ValueError("manuscript lost specific mathematical limitations")
    # Refuse unqualified positive solution claims. Negative statements are
    # checked above, and these flags catch explicit forged declarations.
    if re.search(
        r"(?im)^\s*(?:status|result|conclusion)\s*:\s*"
        r"(?:SOLVED|CERTIFIED|NOVELTY_VERIFIED|ACCEPTED_BY_CLAY)\b", paper
    ):
        raise ValueError("manuscript attempts unsupported status promotion")
    if len(review) < 1200 or not all(
        needle in review for needle in REVIEW_SENTINELS
    ):
        raise ValueError("independent review form lost its unfilled-state declarations")

    _require_set(
        ledger,
        {"schema_version", "manuscript", "as_of", "policy",
         "search_log", "references", "open_review_tasks"},
        "literature ledger",
    )
    if (ledger["schema_version"] != "1.0.0" or
        ledger["manuscript"] != "docs/research/papers/SAT1_FORMAL_NOTE.md" or
        ledger["as_of"] != "2026-11-13" or
        ledger["policy"] != LEDGER_POLICY):
        raise ValueError("literature ledger claims unsupported novelty/review status")

    refs = ledger["references"]
    if type(refs) is not list or len(refs) != len(REFERENCE_URLS):
        raise ValueError("initial reference metadata has changed without review")
    if set(x.get("id") for x in refs if type(x) is dict) != set(REFERENCE_URLS):
        raise ValueError("missing or duplicated literature reference")
    for entry in refs:
        _require_set(
            entry, {"id", "citation", "url", "relevance", "metadata_checked",
                    "independent_full_text_analysis", "proves_specific_sat1_fact"},
            "reference",
        )
        if (entry["url"] != REFERENCE_URLS[entry["id"]] or
            entry["metadata_checked"] is not True or
            entry["independent_full_text_analysis"] is not False or
            entry["proves_specific_sat1_fact"] is not False or
            type(entry["citation"]) is not str or
            len(entry["citation"]) < 35 or
            type(entry["relevance"]) is not str or
            len(entry["relevance"]) < 35 or
            f"[{entry['id'][1:]}]" not in paper or
            entry["url"] not in paper):
            raise ValueError("background reference lacks support or falsely claims review")

    queries = ledger["search_log"]
    if type(queries) is not list or len(queries) != 4:
        raise ValueError("initial targeted search log must remain fully disclosed")
    if any(
        type(q) is not dict or set(q) != {
            "id", "query", "method", "scope", "completeness"
        } or q["completeness"] != "NOT_SYSTEMATIC" or
        type(q["query"]) is not str or len(q["query"]) < 25
        for q in queries
    ) or len({q["id"] for q in queries}) != len(queries):
        raise ValueError("search log cannot pass as systematic novelty assessment")
    tasks = ledger["open_review_tasks"]
    if type(tasks) is not list or len(tasks) != 4 or any(
        type(t) is not dict or set(t) != {"task_id", "question", "status"} or
        t["status"] != "OPEN_REQUIRES_HUMAN" or
        type(t["question"]) is not str or len(t["question"]) < 30
        for t in tasks
    ) or len({t["task_id"] for t in tasks}) != len(tasks):
        raise ValueError("independent literature-review tasks cannot auto-close")

    theorem = audit_theorem_assurance(
        assurance_path=theorem_path, lean_path=lean_path,
        verify_lean=verify_lean,
    )
    if (
        theorem["certification"] != "NOT_CERTIFIED" or
        theorem["clay_route_implication"] != "NOT_PROVEN" or
        theorem["external_expert_review"] != "NOT_PERFORMED" or
        theorem["mathematical_novelty"] != "NOT_INDEPENDENTLY_ASSESSED" or
        theorem["clay_solution"] is not False or
        theorem["canonical_claim_promotion"] is not False
    ):
        raise ValueError("formal assurance no longer preserves research boundaries")

    if any(path.read_bytes() != raw[key] for key, path in protected.items()):
        raise RuntimeError("protected research manuscript or source changed during audit")

    report = {
        "schema_version": "1.0.0",
        "packet_classification": "REVIEW_READY_NOT_SUBMISSION_READY",
        "manuscript_status": "REVIEW_DRAFT_NOT_SUBMITTED",
        "mathematical_theorem": "MATHOS_SAT1_CHOICE_WORDS_ONLY",
        "formal_status": theorem["formal_result"]["status"],
        "pinned_lean_replay_requested": verify_lean,
        "novelty_assessment": "NOT_INDEPENDENTLY_ASSESSED",
        "systematic_literature_review": "NOT_COMPLETED",
        "independent_expert_review": "NOT_PERFORMED",
        "journal_submission": "NOT_SUBMITTED",
        "clay_submission": "NOT_SUBMITTED",
        "clay_prize_eligibility": "NOT_ESTABLISHED",
        "canonical_certification": "NOT_CERTIFIED",
        "clay_problem_solved": False,
        "registered_proof_obligations_closed": 0,
        "route_implication": "NOT_PROVEN",
        "sources_sha256": {k: _hash(blob) for k, blob in raw.items()},
        "additional_sources_sha256": theorem["sources_sha256"],
        "background_references": [
            {"id": entry["id"], "url": entry["url"],
             "human_full_text_reviewed": False} for entry in refs
        ],
        "independent_review_task_count": len(tasks),
        "limitations": (
            "This pack is an unrefereed technical note; mathematical novelty, "
            "formal polynomial-ring embedding, SAT complexity and Clay proof "
            "implications remain unestablished."
        ),
    }

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        for src, dest in (
            (paper_path, "SAT1_FORMAL_NOTE.md"),
            (ledger_path, "SAT1_LITERATURE_LEDGER.v1.json"),
            (review_path, "SAT1_EXTERNAL_REVIEW.md"),
            (lean_path, "SATSupport.lean"),
        ):
            shutil.copyfile(src, output_dir / dest)
        (output_dir / "packet_manifest.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (output_dir / "review_readme.md").write_text(
            "# SAT1 independent-review handoff\n\n"
            "**Status: REVIEW_READY_NOT_SUBMISSION_READY.**\n\n"
            "Open SAT1_FORMAL_NOTE.md and SAT1_EXTERNAL_REVIEW.md, "
            "inspect SATSupport.lean, and verify the pinned Lean source "
            "before making any mathematical assessment. "
            "The references are preliminary contextual sources only.\n\n"
            "No submission, expert acceptance, novelty determination, "
            "or Clay solution has been established.\n",
            encoding="utf-8",
        )
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/paper"))
    parser.add_argument("--verify-lean", action="store_true")
    args = parser.parse_args(argv)
    report = audit_paper_packet(
        output_dir=args.output_dir, verify_lean=args.verify_lean
    )
    print(json.dumps({
        "packet_classification": report["packet_classification"],
        "formal_status": report["formal_status"],
        "manuscript_status": report["manuscript_status"],
        "output_dir": str(args.output_dir),
        "clay_problem_solved": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
