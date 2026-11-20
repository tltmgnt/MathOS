"""Offline MathOS curriculum metadata validation (not student assessment)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name("catalog.json")
REQUIRED_COURSES = {"bridge", "zeta-tda", "topology", "proof", "agentic-clay", "topo406"}
REQUIRED_DIMENSIONS = {"breadth", "rigor", "reproducibility", "specialization", "accessibility", "external_validation"}
LEVELS = {"beginner", "intermediate", "advanced", "research", "cross_cutting"}
EVIDENCE = {"learner_work_reviewed_by_human", "human_scored_capstone", "human_scored_lab",
            "expert_reviewed_proof_dossier", "external_review_required", "human_reviewed_traceability"}


def validate(data: object, root: Path = ROOT) -> list[str]:
    """Return structural errors; never infer learning outcomes from passing checks."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["catalog must be an object"]
    if data.get("schema_version") != 1:
        errors.append("unsupported schema_version")
    if data.get("automatic_certification") is not False:
        errors.append("automatic_certification must be false")
    if data.get("external_validation_established") is not False:
        errors.append("external validation may not be asserted by metadata")
    courses = data.get("courses")
    if not isinstance(courses, list):
        return errors + ["courses must be an array"]
    ids = [c.get("id") for c in courses if isinstance(c, dict)]
    if len(ids) != len(courses) or len(ids) != len(set(ids)) or set(ids) != REQUIRED_COURSES:
        errors.append("course IDs must be unique and match required courses")
    course_index = {c["id"]: c for c in courses if isinstance(c, dict) and isinstance(c.get("id"), str)}
    for ident, course in course_index.items():
        for key in ("title", "syllabus", "verification", "outcome"):
            if not isinstance(course.get(key), str) or not course[key].strip():
                errors.append(f"{ident}: missing {key}")
        if course.get("level") not in LEVELS:
            errors.append(f"{ident}: invalid level")
        if type(course.get("duration_weeks")) is not int or not 1 <= course["duration_weeks"] <= 52:
            errors.append(f"{ident}: invalid duration_weeks")
        if course.get("evidence_type") not in EVIDENCE:
            errors.append(f"{ident}: invalid evidence_type")
        dependencies = course.get("prerequisites")
        if not isinstance(dependencies, list) or any(not isinstance(d, str) for d in dependencies):
            errors.append(f"{ident}: invalid prerequisites")
        elif len(dependencies) != len(set(dependencies)) or any(d not in course_index or d == ident for d in dependencies):
            errors.append(f"{ident}: unknown, duplicate or self prerequisite")
        path = course.get("syllabus")
        if isinstance(path, str):
            rel = Path(path)
            # Only regular files directly beneath this checkout may be referenced.
            if rel.is_absolute() or ".." in rel.parts or not (root / rel).is_file() or (root / rel).is_symlink():
                errors.append(f"{ident}: missing/unsafe syllabus path")
    seen: set[str] = set()
    active: set[str] = set()

    def visit(node: str) -> None:
        if node in active:
            errors.append(f"prerequisite cycle at {node}")
            return
        if node in seen:
            return
        active.add(node)
        course = course_index[node]
        for dep in course.get("prerequisites", []):
            if isinstance(dep, str) and dep in course_index and dep != node:
                visit(dep)
        active.remove(node)
        seen.add(node)

    for ident in course_index:
        visit(ident)
    dimensions = data.get("quality_dimensions")
    if not isinstance(dimensions, list):
        errors.append("quality_dimensions must be an array")
    else:
        dimension_ids = [d.get("id") for d in dimensions if isinstance(d, dict)]
        if len(dimension_ids) != len(dimensions) or len(set(dimension_ids)) != len(dimension_ids) or set(dimension_ids) != REQUIRED_DIMENSIONS:
            errors.append("quality dimension IDs mismatch")
        for d in dimensions:
            if not isinstance(d, dict) or not isinstance(d.get("gate"), str) or not d["gate"].strip() or type(d.get("external")) is not bool:
                errors.append("invalid quality dimension evidence gate")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.catalog.read_text(encoding="utf-8"))
        errors = validate(data)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors = [f"unable to read catalog: {exc}"]
    result = {"status": "structural_pass" if not errors else "structural_fail",
              "certification": "NOT_CERTIFIED",
              "external_validation": "NOT_ESTABLISHED",
              "errors": errors}
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
