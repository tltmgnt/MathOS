"""Validate and plan the 24-week MathOS agentic Clay research curriculum.

This audits curriculum metadata and can demonstrate the OFFLINE agent handoff.
It cannot award course completion or mathematically certify any Millennium
problem. Running a scripted offline agent is NOT a live model experiment.

python -m mathos.research.agentic_curriculum --track all
python -m mathos.research.agentic_curriculum --track Hodge --rehearsal
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from mathos.research.agentic_clay import OfflineBackend, _write_packet, run_agent
from mathos.research.clay_alignment import TARGETS_PATH, audit_clay_alignment
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS, ROOT

SYLLABUS = ROOT / "curriculum/agentic-clay-v1.json"

EXPECTED_MODULE_IDS = tuple(f"M{i:02d}" for i in range(1, 7))
EXPECTED_COMPLETION_POLICY = {
    "automatic_certification": False,
    "learner_progress_is_mathematical_proof": False,
    "completion_requires_human_assessment": True,
    "canonical_certification": "NOT_CERTIFIED",
    "canonical_math_state": "BLOCKED",
    "offline_harness_is_not_ai_research": True,
    "clay_prize_eligibility": False,
}
RUBRIC_KEYS = {
    "claim_precision", "assumptions", "independent_checks",
    "adversarial_review", "proof_scope", "provenance", "communication",
}


def _require_string(value: object, label: str, minimum: int = 8) -> None:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise ValueError(f"missing or short {label}")


def build_curriculum_plan(
    *,
    track: str = "all",
    syllabus_path: Path = SYLLABUS,
    targets_path: Path = TARGETS_PATH,
    obligations_path: Path = OBLIGATIONS,
    hypotheses_path: Path = HYPOTHESES,
) -> dict:
    """Check full curriculum and canonical math status; never grade humans."""
    inputs = {
        "syllabus": syllabus_path.read_bytes(),
        "clay_targets": targets_path.read_bytes(),
        "obligations": obligations_path.read_bytes(),
        "hypotheses": hypotheses_path.read_bytes(),
    }
    syllabus = json.loads(inputs["syllabus"])
    targets = json.loads(inputs["clay_targets"])
    obligations = json.loads(inputs["obligations"])
    hypotheses = json.loads(inputs["hypotheses"])

    clay_audit = audit_clay_alignment(
        targets_path=targets_path,
        register_path=obligations_path,
        hypotheses_path=hypotheses_path,
    )
    if syllabus.get("schema_version") != "1.0.0":
        raise ValueError("unsupported agentic curriculum schema")
    if syllabus.get("duration_weeks") != 24 or syllabus.get("hours_per_week") != {
        "minimum": 8, "maximum": 12
    }:
        raise ValueError("curriculum must follow the existing 24-week 8–12h path")
    if syllabus.get("completion_policy") != EXPECTED_COMPLETION_POLICY:
        raise ValueError("automatic academic or mathematical certification is forbidden")
    if (syllabus.get("prior_curriculum") != "curriculum/proof-analysis-verification.md"
        or syllabus.get("agent_process") != "docs/research/AGENTIC_RESEARCH_PROCESS.md"
        or syllabus.get("clay_target_registry") != "docs/research/CLAY_FULL_TARGETS.v1.json"
        or syllabus.get("hypotheses_registry") != "docs/research/HYPOTHESES.v1.json"
        or syllabus.get("canonical_obligations") != "docs/proof-analysis/OBLIGATIONS.v1.json"):
        raise ValueError("source provenance or prerequisite path mismatch")

    evaluate = syllabus.get("evaluation", {})
    if (evaluate.get("claimed_passes_without_human_review") is not False
        or not isinstance(evaluate.get("rubric_points"), dict)
        or set(evaluate["rubric_points"]) != RUBRIC_KEYS
        or sum(evaluate["rubric_points"].values()) != 100
        or any(type(v) is not int or v <= 0
               for v in evaluate["rubric_points"].values())):
        raise ValueError("human-only grading rubric invalid")
    for key in ("mechanical_checks", "human_gates"):
        _require_string(evaluate.get(key), f"evaluation.{key}", 30)

    modules = syllabus.get("modules")
    if not isinstance(modules, list) or len(modules) != 6:
        raise ValueError("exactly six four-week modules required")
    weeks = []
    artifacts = []
    for i, module in enumerate(modules):
        if module.get("id") != EXPECTED_MODULE_IDS[i]:
            raise ValueError("module ordering invalid")
        left, right = 4 * i + 1, 4 * (i + 1)
        if module.get("weeks") != [left, right]:
            raise ValueError("module week interval invalid")
        rows = module.get("weekly")
        if not isinstance(rows, list) or len(rows) != 4:
            raise ValueError("each module must have four actionable weekly labs")
        if module.get("gate") not in {
            "HUMAN_REVIEW_PENDING", "SUBJECT_EXPERT_REVIEW_PENDING",
            "FORMAL_REVIEW_PENDING", "HUMAN_ASSESSMENT_REQUIRED",
        }:
            raise ValueError("module must never auto-award completion")
        _require_string(module.get("title"), "module.title")
        _require_string(module.get("goal"), "module.goal", 20)
        if not module.get("skills") or len(module.get("acceptance", [])) < 3:
            raise ValueError("module skill and acceptance gate missing")
        for j, row in enumerate(rows):
            if row.get("week") != left + j:
                raise ValueError("missing or duplicate week number")
            for key in ("topic", "assignment", "artifact"):
                _require_string(row.get(key), f"week {left+j}: {key}", 5)
            if "/" in row["artifact"] or "\\" in row["artifact"]:
                raise ValueError("artifact names must be relative filenames only")
            weeks.append(row["week"])
            artifacts.append(row["artifact"])
    if weeks != list(range(1, 25)) or len(set(artifacts)) != 24:
        raise ValueError("weeks or learning artifacts are not unique and complete")

    canonical = {x["model_key"]: x for x in obligations["tracks"]}
    clay = {x["model_key"]: x for x in targets["targets"]}
    probes = {x["model_key"]: x["bounded_probe"] for x in hypotheses["experiments"]}
    entries = syllabus.get("tracks")
    if not isinstance(entries, list) or len(entries) != 7:
        raise ValueError("all seven Clay learning tracks must exist")
    names = [x.get("model_key") for x in entries]
    if len(set(names)) != 7 or set(names) != set(clay) or set(names) != set(canonical):
        raise ValueError("missing, duplicate or unexpected Clay learning track")
    selected = names if track == "all" else [track]
    if any(x not in names for x in selected):
        raise ValueError(f"unknown curriculum track: {track!r}")

    for entry in entries:
        key = entry["model_key"]
        if entry.get("first_probe") != clay[key]["current_probe"] or (
            entry["first_probe"] != probes[key]
        ):
            raise ValueError(f"first executable use case mismatch for {key}")
        if set(entry.get("obligations", [])) != {
            x["claim_id"] for x in canonical[key]["work_packages"]
        }:
            raise ValueError(f"canonical mathematical obligation mismatch for {key}")
        if canonical[key]["modeled_target_status"] != "BLOCKED":
            raise ValueError(f"math target no longer BLOCKED: {key}")
        if not isinstance(entry.get("prerequisites"), list) or len(entry["prerequisites"]) < 3:
            raise ValueError(f"specialist foundations missing for {key}")
        for field in ("starter", "beyond_starter", "principal_risk"):
            _require_string(entry.get(field), f"{key}.{field}", 30)

    if clay_audit["certification"] != "NOT_CERTIFIED" or (
        clay_audit["open_work_packages"] != 14
    ):
        raise ValueError("canonical math safety gate changed")

    plans = []
    for key in selected:
        entry = next(e for e in entries if e["model_key"] == key)
        plans.append({
            "model_key": key,
            "official_problem_source": clay[key]["clay_problem_page"],
            "clay_target": clay[key]["official_target"],
            "prerequisites": entry["prerequisites"],
            "first_executable_use_case": entry["starter"],
            "first_probe_id": entry["first_probe"],
            "research_capstone": entry["beyond_starter"],
            "known_failure_mode": entry["principal_risk"],
            "missing_global_proof": clay[key]["missing_bridge"],
            "canonical_open_claims": entry["obligations"],
            "learning_state": "CURRICULUM_PLAN_ONLY",
            "mathematical_state": "BLOCKED",
            "completion_awarded": False,
        })
    result = {
        "curriculum": syllabus["name"],
        "duration_weeks": 24,
        "workload_hours_per_week": [8, 12],
        "weeks_covered": weeks,
        "modules": [{
            "id": m["id"], "weeks": m["weeks"], "title": m["title"],
            "goal": m["goal"], "learning_gate": m["gate"],
            "weekly": m["weekly"], "gate_assessed": False,
        } for m in modules],
        "selected_tracks": plans,
        "rubric_points": evaluate["rubric_points"],
        "rubric_assessed": False,
        "human_assessment_required": True,
        "rehearsal_status": "NOT_RUN",
        "certification": "NOT_CERTIFIED",
        "mathematical_claim_promotion": "NONE",
        "clay_prize_eligibility": False,
        "open_work_packages": 14,
        "source_sha256": {
            name: hashlib.sha256(contents).hexdigest()
            for name, contents in inputs.items()
        },
    }
    for name, file in (
        ("syllabus", syllabus_path), ("clay_targets", targets_path),
        ("obligations", obligations_path), ("hypotheses", hypotheses_path)
    ):
        if file.read_bytes() != inputs[name]:
            raise RuntimeError("curriculum changed canonical source input")
    return result


def rehearse_plan(
    track: str,
    *,
    syllabus_path: Path = SYLLABUS,
    targets_path: Path = TARGETS_PATH,
    obligations_path: Path = OBLIGATIONS,
    hypotheses_path: Path = HYPOTHESES,
) -> tuple[dict, dict]:
    """Execute deterministic NON-AI agent simulation for training only."""
    plan = build_curriculum_plan(
        track=track, syllabus_path=syllabus_path,
        targets_path=targets_path, obligations_path=obligations_path,
        hypotheses_path=hypotheses_path
    )
    number = len(plan["selected_tracks"])
    agent = run_agent(
        OfflineBackend(), track=track, rounds=1,
        max_model_calls=4 * number,
        targets_path=targets_path, obligations_path=obligations_path,
        hypotheses_path=hypotheses_path,
    )
    if agent["ai_generated"] or agent["certification"] != "NOT_CERTIFIED" or (
        len(agent["packets"]) != number
    ):
        raise RuntimeError("offline rehearsal was falsely treated as verified AI")
    plan["rehearsal_status"] = "OFFLINE_SCRIPTED_SIMULATION_COMPLETED"
    plan["rehearsal_model_calls"] = agent["bounded_model_calls"]
    plan["rehearsal_is_ai_research"] = False
    return plan, agent


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", default="all",
                        help="Clay research track name, or all")
    parser.add_argument("--rehearsal", action="store_true",
                        help="run scripted offline agent practice; no API calls")
    parser.add_argument("--output-dir", type=Path,
                        default=Path("artifacts/curriculum"))
    args = parser.parse_args(argv)

    if args.rehearsal:
        plan, agent = rehearse_plan(args.track)
    else:
        plan = build_curriculum_plan(track=args.track)
        agent = None
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "curriculum_plan.json").write_text(
        json.dumps(plan, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    if agent is not None:
        _write_packet(args.output_dir / "offline_rehearsal", agent)
    print(json.dumps({
        "modules": len(plan["modules"]),
        "weeks": plan["duration_weeks"],
        "tracks": len(plan["selected_tracks"]),
        "rehearsal_status": plan["rehearsal_status"],
        "completion_awarded": False,
        "certification": "NOT_CERTIFIED",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
