"""TECT-X thematic source-audit gate (not a theorem or independent review checker).

Validates the six-theme evidence index, local source anchors, and alignment
with existing bounded experiment and manuscript blockers. A green result
certifies consistency of repository records *only*.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "docs/research/TECT_X_THEMATIC_REGISTER.v1.json"
KINDS = {
    "BOUNDED_COMPUTATION_REPORT",
    "DOCUMENTED_EXACT_ARGUMENT",
    "DOCUMENTED_NEGATIVE_RESULT",
    "DOCUMENTED_SCOPE_BOUNDARY",
    "OPEN_PROOF_OBLIGATION",
    "IMPLEMENTED_WORKFLOW",
    "IMPLEMENTED_EDUCATIONAL_MATERIAL",
}
REQUIRED_FALSE_FLAGS = {
    "riemann_hypothesis_proved",
    "bsd_proved",
    "selmer_infinitude_proved",
    "full_million_point_h1_computed",
    "independent_specialist_review_complete",
    "external_reproduction_complete",
    "journal_submission_authorized",
}
METRIC_KEYS = (
    "variant_count",
    "family_count",
    "variants_per_family",
    "rips_h01_sample_size_per_family",
    "zero_sets_computed",
    "million_point_h1_persistence_computed",
)
EXPECTED_THEMES = {f"T{i}" for i in range(1, 7)}
EXPERIMENT_PATH = "docs/research/TECT_X_ZETA_TDA_AUDIT.v1.json"
SELMER_PATH = "docs/research/papers/TECT_X_SUBMISSION_STATUS.v1.json"


def _safe_repository_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        return False
    p = PurePosixPath(value)
    return (
        not p.is_absolute()
        and all(part not in (".", "..") for part in value.split("/"))
        and str(p) == value
    )


def _load_json(root: Path, relative_path: str) -> Any:
    return json.loads((root / relative_path).read_text(encoding="utf-8"))


def evaluate_register(payload: Any, root: Path = ROOT) -> dict[str, Any]:
    """Return explicit blockers without promoting source assertions to truth."""
    problems: list[str] = []

    if not isinstance(payload, dict):
        return {"ok": False, "issues": ["register must be a JSON object"]}
    if payload.get("schema_version") != "1.0":
        problems.append("schema_version must be 1.0")
    if payload.get("assurance_level") != "REPOSITORY_SOURCE_AUDIT_ONLY":
        problems.append("assurance_level cannot assert independent certification")
    if not isinstance(payload.get("scope"), str) or not payload["scope"].strip():
        problems.append("scope must be explicit")
    if not isinstance(payload.get("reviewed_on"), str) or not payload["reviewed_on"]:
        problems.append("reviewed_on required")

    flags = payload.get("certification_flags")
    if not isinstance(flags, dict) or set(flags) != REQUIRED_FALSE_FLAGS:
        problems.append("certification_flags must have exactly the expected keys")
    else:
        for key, value in flags.items():
            if value is not False:
                problems.append(f"unsupported certification flag: {key}")

    evidence = payload.get("evidence")
    themes = payload.get("themes")
    if not isinstance(evidence, list) or not evidence:
        problems.append("evidence must be a nonempty array")
        evidence = []
    if not isinstance(themes, list) or len(themes) != 6:
        problems.append("exactly six themes required")
        themes = themes if isinstance(themes, list) else []

    evidence_ids: set[str] = set()
    for idx, entry in enumerate(evidence):
        if not isinstance(entry, dict):
            problems.append(f"evidence[{idx}] must be an object")
            continue
        eid = entry.get("id")
        if not isinstance(eid, str) or not eid.startswith("E") or not eid[1:].isdigit():
            problems.append(f"invalid evidence id at index {idx}")
        elif eid in evidence_ids:
            problems.append(f"duplicate evidence id: {eid}")
        else:
            evidence_ids.add(eid)
        if entry.get("kind") not in KINDS:
            problems.append(f"invalid evidence kind: {eid}")
        for key in ("statement", "limitation"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                problems.append(f"missing {key}: {eid}")
        paths = entry.get("source_paths")
        if not isinstance(paths, list) or not paths:
            problems.append(f"missing source_paths: {eid}")
            continue
        if len(paths) != len(set(p for p in paths if isinstance(p, str))):
            problems.append(f"duplicate source path: {eid}")
        for value in paths:
            if not _safe_repository_path(value):
                problems.append(f"unsafe source path: {eid}: {value!r}")
            elif not (root / value).is_file():
                problems.append(f"missing source file: {eid}: {value}")

    theme_ids: set[str] = set()
    linked_evidence: set[str] = set()
    for idx, entry in enumerate(themes):
        if not isinstance(entry, dict):
            problems.append(f"themes[{idx}] must be an object")
            continue
        tid = entry.get("id")
        if tid not in EXPECTED_THEMES:
            problems.append(f"unrecognized theme id: {tid}")
        elif tid in theme_ids:
            problems.append(f"duplicate theme id: {tid}")
        else:
            theme_ids.add(tid)
        for key in ("name", "finding", "open_obligation"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                problems.append(f"missing {key}: {tid}")
        if entry.get("priority") not in {"MEDIUM", "HIGH", "CRITICAL"}:
            problems.append(f"invalid priority: {tid}")
        refs = entry.get("evidence_ids")
        if not isinstance(refs, list) or not refs:
            problems.append(f"theme missing evidence: {tid}")
        else:
            if len(refs) != len(set(refs)):
                problems.append(f"repeated evidence reference: {tid}")
            for eid in refs:
                if eid not in evidence_ids:
                    problems.append(f"unknown evidence reference {tid}: {eid}")
                else:
                    linked_evidence.add(eid)
    if theme_ids != EXPECTED_THEMES:
        problems.append("theme IDs must be T1..T6")
    for orphan in sorted(evidence_ids - linked_evidence):
        problems.append(f"unlinked evidence record: {orphan}")

    priorities = payload.get("priorities")
    if not isinstance(priorities, list) or not priorities:
        problems.append("priorities must be nonempty")
    else:
        priority_ids: set[str] = set()
        for idx, item in enumerate(priorities):
            if not isinstance(item, dict):
                problems.append(f"invalid priority at index {idx}")
                continue
            pid = item.get("id")
            if not isinstance(pid, str) or pid in priority_ids:
                problems.append(f"invalid or duplicate priority id: {pid}")
            else:
                priority_ids.add(pid)
            if not isinstance(item.get("action"), str) or not item["action"].strip():
                problems.append(f"missing priority action: {pid}")
            if not isinstance(item.get("acceptance"), str) or not item["acceptance"].strip():
                problems.append(f"missing priority acceptance: {pid}")
            refs = item.get("theme_ids")
            if not isinstance(refs, list) or not refs or any(ref not in EXPECTED_THEMES for ref in refs):
                problems.append(f"invalid priority theme references: {pid}")

    snapshot = payload.get("metrics_snapshot")
    if not isinstance(snapshot, dict) or snapshot.get("experiment") != EXPERIMENT_PATH:
        problems.append("metrics_snapshot must link to the canonical experiment")
    else:
        try:
            experiment = _load_json(root, EXPERIMENT_PATH)
            for key in METRIC_KEYS:
                if type(snapshot.get(key)) is not type(experiment.get(key)) or snapshot.get(key) != experiment.get(key):
                    problems.append(f"experiment metric mismatch: {key}")
            science = experiment["scientific_claims"]
            for key in ("riemann_hypothesis_proved", "bsd_or_selmer_rank_proved", "independent_math_review_completed"):
                if science.get(key) is not False:
                    problems.append(f"unexpected experiment science claim: {key}")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            problems.append(f"cannot validate experiment status: {exc}")

    try:
        selmer = _load_json(root, SELMER_PATH)
        if selmer.get("status") != "BLOCKED_OPEN_MAIN_THEOREM":
            problems.append("Selmer manuscript must remain blocked for this source-audit version")
        if selmer["claims"]["unconditional_infinite_selmer3"].get("established") is not False:
            problems.append("unexpected Selmer infinitude promotion")
        if selmer["publication"].get("journal_submission_authorized") is not False:
            problems.append("unexpected Selmer journal authorization")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        problems.append(f"cannot validate Selmer status: {exc}")

    return {
        "ok": not problems,
        "issues": problems,
        "theme_count": len(themes),
        "evidence_count": len(evidence),
        "assurance_level": "REPOSITORY_SOURCE_AUDIT_ONLY",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", type=Path, default=REGISTER)
    parser.add_argument("--json", action="store_true", help="machine-readable audit summary")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.register.read_text(encoding="utf-8"))
        report = evaluate_register(payload)
    except (OSError, ValueError) as exc:
        report = {"ok": False, "issues": [str(exc)]}
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("TECT-X thematic registry: " + ("CONSISTENT" if report["ok"] else "BLOCKED"))
        for item in report["issues"]:
            print(f" - {item}")
        print("Record consistency only; no mathematical or external review certification.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
