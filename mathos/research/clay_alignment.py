"""Audit complete Clay problem-target traceability without claiming proof.

This audits whether MathOS research protocols explicitly *name* the full Clay
problem, its quantifiers, missing bridge and evidence requirements. A score of
10/10 is a document field-coverage score, not a proof, novelty, official Clay
rating or estimate of how close a solution is.

Run: python -m mathos.research.clay_alignment
     python -m mathos.research.clay_alignment --output-dir artifacts/clay
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS, ROOT

TARGETS_PATH = ROOT / "docs/research/CLAY_FULL_TARGETS.v1.json"

EXPECTED_CLAY_URLS = {
    "Riemann": "https://www.claymath.org/millennium/riemann-hypothesis/",
    "P-versus-NP": "https://www.claymath.org/millennium/p-vs-np/",
    "Navier-Stokes": "https://www.claymath.org/millennium/navier-stokes-equation/",
    "Yang-Mills": "https://www.claymath.org/millennium/yang-mills-the-maths-gap/",
    "Hodge": "https://www.claymath.org/millennium/hodge-conjecture/",
    "Birch-Swinnerton-Dyer":
        "https://www.claymath.org/millennium/birch-and-swinnerton-dyer-conjecture/",
    "Poincare": "https://www.claymath.org/millennium/poincare-conjecture/",
}

EXPECTED_STATUS = {key: ("SOLVED_EXTERNALLY" if key == "Poincare"
                         else "ACTIVE" if key == "Navier-Stokes" else "UNSOLVED")
                   for key in EXPECTED_CLAY_URLS}

EXPECTED_CONTENT_MARKERS = {
    "Riemann": ("nontrivial zero", "every"),
    "P-versus-NP": ("polynomial-time", "NP"),
    "Navier-Stokes": ("existence-and-smoothness", "breakdown"),
    "Yang-Mills": ("four-dimensional", "mass gap"),
    "Hodge": ("rational Hodge class", "algebraic cycles"),
    "Birch-Swinnerton-Dyer": ("elliptic curve", "order of vanishing"),
    "Poincare": ("simply connected", "three-sphere"),
}


def audit_clay_alignment(
    targets_path: Path = TARGETS_PATH,
    register_path: Path = OBLIGATIONS,
    hypotheses_path: Path = HYPOTHESES,
) -> dict:
    source_bytes = {
        "targets": targets_path.read_bytes(),
        "register": register_path.read_bytes(),
        "hypotheses": hypotheses_path.read_bytes(),
    }
    sources = {key: json.loads(value) for key, value in source_bytes.items()}
    c, r, h = sources["targets"], sources["register"], sources["hypotheses"]

    if c.get("schema_version") != "1.0.0":
        raise ValueError("unsupported Clay target schema")
    if r.get("certification") != "NOT_CERTIFIED" or h.get("certification") != "NOT_CERTIFIED":
        raise ValueError("source registries are no longer explicitly NOT_CERTIFIED")

    policy = c.get("policy", {})
    expected_policy = {
        "canonical_certification": "NOT_CERTIFIED",
        "original_probes": "BOUNDED_ONLY",
        "proof_status": "NOT_ESTABLISHED",
        "clay_prize_readiness": "NOT_ELIGIBLE",
        "research_alignment_only": True,
    }
    if policy != expected_policy:
        raise ValueError("Clay audit must never promote a mathematical claim")

    if c.get("clay_rules_page") != "https://www.claymath.org/millennium-problems/rules/":
        raise ValueError("official rules source has changed")
    official_gates = c.get("cmi_gate")
    if official_gates != {
        "qualifying_publication": False,
        "two_years_elapsed": False,
        "general_mathematical_acceptance": False,
        "clay_consideration": False,
    }:
        raise ValueError("no Clay prize eligibility gate is established")

    dimensions = c.get("dimensions")
    expected_dimensions = (
        "clay_problem_page", "official_target", "quantified_scope",
        "permitted_solution_type", "hypotheses_and_conditions",
        "current_probe", "probe_limit", "missing_bridge",
        "required_proof_artifact", "external_review_gate"
    )
    if tuple(dimensions or ()) != expected_dimensions:
        raise ValueError("invalid field-coverage rubric; expected exactly ten dimensions")
    if c.get("coverage_metric") != (
        "10 required traceability fields per track, structural completeness only; "
        "not mathematical solution relevance or Clay approval"
    ):
        raise ValueError("must explicitly distinguish field coverage and mathematical progress")

    canonical = {x["model_key"]: x for x in r["tracks"]}
    prior_probes = {x["model_key"]: x["bounded_probe"] for x in h["experiments"]}
    targets = c.get("targets", [])
    if not isinstance(targets, list) or len(targets) != 7:
        raise ValueError("exactly seven separate Clay targets are required")
    keys = [t["model_key"] for t in targets]
    if (len(canonical) != 7 or len(prior_probes) != 7 or
        set(keys) != set(EXPECTED_CLAY_URLS) or len(set(keys)) != 7 or
        set(canonical) != set(prior_probes)):
        raise ValueError("Clay track mapping does not match MathOS")

    if (r["external_result"]["claim_id"] != "POINCARE.published" or
        r["external_result"]["graph_state"] != "established_external"):
        raise ValueError("Poincare must remain externally established")

    reports = []
    for entry in targets:
        model = entry["model_key"]
        if entry.get("clay_problem_page") != EXPECTED_CLAY_URLS[model]:
            raise ValueError(f"unrecognized official Clay source for {model}")
        if entry.get("clay_status") != EXPECTED_STATUS[model]:
            raise ValueError(f"official problem status mismatch for {model}")
        if entry.get("external_solution_known") is not (model == "Poincare"):
            raise ValueError(f"externally solved state must be protected: {model}")
        if entry.get("current_probe") != prior_probes[model]:
            raise ValueError(f"current experimental probe mismatch: {model}")
        mathematical_claims = canonical[model]
        if mathematical_claims["modeled_target_status"] != "BLOCKED" or any(
            p["graph_state"] != "open" or p["formal_check"] != "not_performed"
            or p["review_verdict"] != "not_reviewed"
            for p in mathematical_claims["work_packages"]
        ):
            raise ValueError(f"mathematical proof obligations were promoted: {model}")
        if set(entry.get("repo_open_claims", ())) != {
            p["claim_id"] for p in mathematical_claims["work_packages"]
        }:
            raise ValueError(f"missing canonical open obligations: {model}")

        coverage_flags = {}
        for dimension in expected_dimensions:
            field = entry.get(dimension)
            coverage_flags[dimension] = (
                isinstance(field, str) and bool(field.strip())
                and len(field.strip()) >= 18
            )
        if not all(coverage_flags.values()):
            missing = [k for k, valid in coverage_flags.items() if not valid]
            raise ValueError(f"incomplete Clay traceability for {model}: {missing}")
        for marker in EXPECTED_CONTENT_MARKERS[model]:
            if marker.lower() not in entry["official_target"].lower():
                raise ValueError(f"official target missing domain marker {marker}: {model}")
        if not isinstance(entry.get("direct_research_test"), str) or len(
            entry["direct_research_test"].strip()
        ) < 30:
            raise ValueError(f"missing direct future research test: {model}")

        reports.append({
            "model_key": model,
            "official_source": entry["clay_problem_page"],
            "official_status": entry["clay_status"],
            "full_problem_target": entry["official_target"],
            "direct_research_test": entry["direct_research_test"],
            "required_missing_bridge": entry["missing_bridge"],
            "field_coverage": {"completed": len(expected_dimensions),
                               "total": len(expected_dimensions),
                               "type": "SPECIFICATION_FIELD_COMPLETENESS_NOT_RELEVANCE"},
            "current_probe": entry["current_probe"],
            "current_probe_proves_full_target": False,
            "proof_completed": False,
            "independent_review_completed": False,
            "mathos_status": "BLOCKED",
            "mathos_certification": "NOT_CERTIFIED",
        })

    if sum(len(canonical[k]["work_packages"]) for k in canonical) != 14:
        raise ValueError("canonical open work-package count unexpectedly changed")
    result = {
        "schema_version": "1.0.0",
        "coverage_dimension_count": 10,
        "all_seven_targets_structurally_complete": True,
        "coverage_score": "10/10 FIELDS PER TRACK — NOT CLAY RELEVANCE OR MATHEMATICAL PROGRESS",
        "proof_readiness": "NO_COMPLETE_SOLUTION_SUBMITTED_OR_VERIFIED",
        "clay_prize_readiness": "NOT_ELIGIBLE",
        "certification": "NOT_CERTIFIED",
        "open_work_packages": 14,
        "original_experiments_only_bounded": True,
        "clay_rules": c["clay_rules_page"],
        "source_sha256": {k: hashlib.sha256(b).hexdigest() for k, b in source_bytes.items()},
        "targets": reports,
    }
    if any(path.read_bytes() != source_bytes[key] for key, path in (
        ("targets", targets_path), ("register", register_path),
        ("hypotheses", hypotheses_path)
    )):
        raise RuntimeError("input mathematical records modified by audit")
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args(argv)
    report = audit_clay_alignment()
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output_dir is None:
        print(text, end="")
    else:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        path = args.output_dir / "clay_target_alignment.json"
        path.write_text(text, encoding="utf-8")
        print(f"Wrote {path}; all proof claims remain NOT_CERTIFIED")


if __name__ == "__main__":
    main()
