"""Fail-closed Clay proof-route topology audit (bookkeeping, not theorem proving).

Models independently proposed OR routes of AND obligations. Minimal completion
sets are relative to *authored*, unreviewed routes: they are not rigorous
sufficiency proofs, estimates of difficulty, or Clay certification.

Run: python -m mathos.research.clay_proof_topology --output-dir artifacts/clay
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from mathos.proof_analysis.gap_analysis import Claim, analyze
from mathos.research.clay_alignment import TARGETS_PATH, audit_clay_alignment
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS, ROOT

ROUTES_PATH = ROOT / "docs/research/CLAY_PROOF_ROUTES.v1.json"
EXTERNAL_PATH = ROOT / "docs/research/CLAY_EXTERNAL_CLAIMS.v1.json"

# Whitelisting stops a modified route manifest silently dropping difficult
# proof work or inventing a "complete" alternative.
EXPECTED_ROUTES = {
    "Riemann": {
        "RH.spectral": ("RH.operator", "RH.zero_identity",
                        "BRIDGE.RH.spectral"),
    },
    "P-versus-NP": {
        "PNP.equality": ("PNP.sat_correctness", "PNP.sat_runtime",
                         "BRIDGE.PNP.sat_to_class"),
        "PNP.separation": ("BRIDGE.PNP.unrestricted_lower_bound",),
    },
    "Navier-Stokes": {
        "NS.A": ("NS.critical_bound", "BRIDGE.NS.A_full_scope"),
        "NS.B": ("NS.critical_bound", "BRIDGE.NS.B_full_scope"),
        "NS.C": ("BRIDGE.NS.C_forced_breakdown",),
        "NS.D": ("BRIDGE.NS.D_forced_breakdown",),
    },
    "Yang-Mills": {
        "YM.continuum_mass": ("YM.continuum", "YM.axioms",
                              "YM.uniform_gap", "BRIDGE.YM.complete_theory"),
    },
    "Hodge": {
        "HODGE.cycles": ("HODGE.primitive_cycles", "HODGE.reduction",
                         "BRIDGE.HODGE.full_quantifiers"),
    },
    "Birch-Swinnerton-Dyer": {
        "BSD.rank_refined": ("BSD.analytic_selmer", "BSD.sha_finiteness",
                             "BSD.leading_term", "BRIDGE.BSD.full_formula"),
    },
    "Poincare": {
        "POINCARE.replay": ("POINCARE.reconstruction",),
    },
}

EXPECTED_ALTERNATIVES = {
    "RH.spectral": "universal_RH_proof",
    "PNP.equality": "P_equals_NP",
    "PNP.separation": "P_not_equals_NP",
    "NS.A": "A_unforced_R3",
    "NS.B": "B_unforced_periodic",
    "NS.C": "C_forced_R3_breakdown",
    "NS.D": "D_forced_periodic_breakdown",
    "YM.continuum_mass": "existence_and_mass_gap",
    "HODGE.cycles": "rational_cycle_representation",
    "BSD.rank_refined": "core_rank_plus_refined_route",
    "POINCARE.replay": "independent_reconstruction_only",
}


def _nontrivial_text(value: object, field: str) -> None:
    if not isinstance(value, str) or len(value.strip()) < 25:
        raise ValueError(f"missing substantial {field} metadata")


def audit_clay_proof_topology(
    routes_path: Path = ROUTES_PATH,
    targets_path: Path = TARGETS_PATH,
    register_path: Path = OBLIGATIONS,
    hypotheses_path: Path = HYPOTHESES,
    external_path: Path = EXTERNAL_PATH,
) -> dict:
    # Reuse the PR #19 rules: all seven official targets, 14 still-open
    # canonical obligations, no forged Clay eligibility or proof promotion.
    alignment = audit_clay_alignment(targets_path, register_path, hypotheses_path)
    paths = {
        "routes": routes_path, "targets": targets_path,
        "register": register_path, "hypotheses": hypotheses_path,
        "external": external_path,
    }
    original = {name: path.read_bytes() for name, path in paths.items()}
    spec = json.loads(original["routes"])
    register = json.loads(original["register"])
    targets = json.loads(original["targets"])
    external = json.loads(original["external"])
    if spec.get("schema_version") != "1.0.0":
        raise ValueError("unsupported proof route schema")
    if spec.get("policy") != {
        "certification": "NOT_CERTIFIED",
        "route_sufficiency": "NOT_VALIDATED",
        "mathematical_proof": "NOT_ESTABLISHED",
        "external_review": "NOT_PERFORMED",
        "no_automatic_promotion": True,
    }:
        raise ValueError("a proof-route manifest cannot assert mathematical validity")

    canonical = {
        track["model_key"]: {claim["claim_id"]: claim for claim in track["work_packages"]}
        for track in register["tracks"]
    }
    if set(canonical) != set(EXPECTED_ROUTES):
        raise ValueError("canonical proof register no longer matches seven targets")
    aligned = {entry["model_key"]: entry for entry in targets["targets"]}
    if set(aligned) != set(EXPECTED_ROUTES):
        raise ValueError("Clay target mapping changed")

    # Externally announced work belongs to a separate ledger. It is neither
    # a MathOS proof nor automatic Clay acceptance. No network status polling
    # or live verification is claimed by this dated snapshot.
    if external.get("schema_version") != "1.0.0" or external.get("policy") != {
        "mathos_certification": "NOT_CERTIFIED",
        "external_claims_do_not_promote_mathos": True,
        "clay_prize_readiness": "NOT_ELIGIBLE",
    }:
        raise ValueError("invalid external-claims nonpromotion policy")
    if external.get("status_as_of") != "2026-11-13":
        raise ValueError("external-claims snapshot date changed without review")
    expected_events = {
        "POINCARE.published": ("Poincare", "ACCEPTED_EXTERNAL", "SOLVED_EXTERNALLY"),
        "NS.2026_openai_claim": ("Navier-Stokes", "ANNOUNCED_UNDER_EXAMINATION", "ACTIVE"),
    }
    events = external.get("events")
    if not isinstance(events, list) or len(events) != len(expected_events):
        raise ValueError("expected external mathematical result and announcement")
    event_ids = [e.get("claim_id") for e in events if isinstance(e, dict)]
    if len(event_ids) != len(events) or set(event_ids) != set(expected_events):
        raise ValueError("duplicate or unknown external mathematical claim")
    for event in events:
        key, state, official = expected_events[event["claim_id"]]
        if (event.get("model_key"), event.get("state"),
            event.get("official_clay_status"), event.get("mathos_proof")) != (
                key, state, official, False
        ) or aligned[key]["clay_status"] != official:
            raise ValueError("external claim incorrectly promoted or misattributed")
        if (event.get("source") != (
            "https://www.claymath.org/millennium/poincare-conjecture/"
            if key == "Poincare" else
            "https://openai.com/index/navier-stokes-solution/"
        )):
            raise ValueError("external claim has an unrecognized primary source")
        if key == "Navier-Stokes" and (
            event.get("event_date") != "2026-09-08" or
            event.get("cmi_response") !=
            "https://www.claymath.org/news/navier-stokes-announcement/"
        ):
            raise ValueError("Navier-Stokes announcement review metadata changed")
        _nontrivial_text(event.get("note"), f"{key}.external_note")

    raw_bridges = spec.get("candidate_bridges")
    raw_routes = spec.get("routes")
    if not isinstance(raw_bridges, list) or not isinstance(raw_routes, list):
        raise ValueError("routes and candidate bridges must be lists")
    bridge_ids = [b.get("claim_id") for b in raw_bridges if isinstance(b, dict)]
    route_ids = [r.get("route_id") for r in raw_routes if isinstance(r, dict)]
    if len(bridge_ids) != len(raw_bridges) or len(set(bridge_ids)) != len(bridge_ids):
        raise ValueError("duplicate or malformed bridge")
    if len(route_ids) != len(raw_routes) or len(set(route_ids)) != len(route_ids):
        raise ValueError("duplicate or malformed proof route")

    allowed_bridges = {
        dep for options in EXPECTED_ROUTES.values()
        for deps in options.values() for dep in deps
        if dep.startswith("BRIDGE.")
    }
    if set(bridge_ids) != allowed_bridges:
        raise ValueError("missing or extraneous proposed bridge")
    bridges = {b["claim_id"]: b for b in raw_bridges}
    all_canonical = set().union(*(set(x) for x in canonical.values()))
    seen_canonical: set[str] = set()
    for b in raw_bridges:
        claim_id, key = b["claim_id"], b.get("model_key")
        if key not in canonical or claim_id not in {
            dep for route in EXPECTED_ROUTES[key].values() for dep in route
        }:
            raise ValueError(f"bridge attached to incorrect track: {claim_id}")
        if (b.get("status"), b.get("review_verdict"), b.get("formal_check"),
            b.get("evidence_artifacts")) != (
                "OPEN", "not_reviewed", "not_performed", []
        ):
            raise ValueError(f"bridge claims cannot be promoted: {claim_id}")
        for field in ("statement", "quantifiers", "assumptions",
                      "counterexample_checks", "acceptance"):
            _nontrivial_text(b.get(field), f"{claim_id}.{field}")

    by_track: dict[str, dict[str, dict]] = {key: {} for key in canonical}
    for route in raw_routes:
        key, route_id = route.get("model_key"), route.get("route_id")
        if key not in EXPECTED_ROUTES or route_id not in EXPECTED_ROUTES[key]:
            raise ValueError(f"unknown or cross-track proof route: {route_id}")
        if route_id in by_track[key]:
            raise ValueError(f"duplicate proof route: {route_id}")
        deps = route.get("obligations")
        if (not isinstance(deps, list) or
            tuple(deps) != EXPECTED_ROUTES[key][route_id]):
            raise ValueError(f"missing/changed dependencies in {route_id}")
        if route.get("alternative") != EXPECTED_ALTERNATIVES[route_id]:
            raise ValueError(f"incorrect official alternative in {route_id}")
        if (route.get("status"), route.get("sufficiency_review"),
            route.get("quantifier_review"), route.get("evidence_artifacts")) != (
                "PROPOSED_NOT_VALIDATED", "not_reviewed", "not_reviewed", []
        ):
            raise ValueError(f"unearned proof-route approval: {route_id}")
        for field in ("scope", "interpretation", "required_proof"):
            _nontrivial_text(route.get(field), f"{route_id}.{field}")
        for dep in deps:
            if dep in canonical[key]:
                seen_canonical.add(dep)
                if (canonical[key][dep]["graph_state"] != "open" or
                    canonical[key][dep]["review_verdict"] != "not_reviewed" or
                    canonical[key][dep]["formal_check"] != "not_performed"):
                    raise ValueError(f"canonical proof claim promoted: {dep}")
            elif dep not in bridges or bridges[dep]["model_key"] != key:
                raise ValueError(f"missing, invalid, or cross-track bridge: {dep}")
        by_track[key][route_id] = route
    if seen_canonical != all_canonical:
        raise ValueError("not all 14 canonical open obligations are represented")
    if any(set(by_track[key]) != set(EXPECTED_ROUTES[key]) for key in EXPECTED_ROUTES):
        raise ValueError("required official alternatives are missing")

    reports = []
    for key in EXPECTED_ROUTES:
        graph: dict[str, Claim] = {}
        for claim_id, entry in canonical[key].items():
            graph[claim_id] = Claim(entry["statement"], "open")
        for claim_id, bridge in bridges.items():
            if bridge["model_key"] == key:
                graph[claim_id] = Claim(bridge["statement"], "open")
        route_nodes = []
        for route_id, route in by_track[key].items():
            node = "ROUTE:" + route_id
            route_nodes.append(node)
            graph[node] = Claim(
                route["interpretation"], "derived",
                (tuple(route["obligations"]),),
                "Author-proposed sufficient route; sufficiency NOT mathematically checked.",
            )
        graph["TARGET"] = Claim(
            aligned[key]["official_target"], "derived",
            tuple((node,) for node in route_nodes),
            "OR of authored candidate routes; no mathematical sufficiency established.",
        )
        analysis = analyze(graph, "TARGET")
        if analysis["status"] != "BLOCKED" or not analysis["minimal_completion_sets"]:
            raise ValueError(f"unexpectedly closed research route: {key}")
        if key != "Poincare" and any(
            not any(claim.startswith("BRIDGE.") for claim in completion)
            for completion in analysis["minimal_completion_sets"]
        ):
            raise ValueError(f"unreviewed bridge omitted from {key} completion set")
        reports.append({
            "model_key": key,
            "official_status": aligned[key]["clay_status"],
            "mathos_status": "BLOCKED",
            "route_count": len(route_nodes),
            "candidate_routes": [
                {
                    "route_id": route_id,
                    "alternative": route["alternative"],
                    "scope": route["scope"],
                    "status": "PROPOSED_NOT_VALIDATED",
                    "obligations": route["obligations"],
                }
                for route_id, route in by_track[key].items()
            ],
            "minimal_completion_sets": analysis["minimal_completion_sets"],
            "common_to_all_modeled_routes": analysis["common_to_all_modeled_routes"],
            "warning": "Graph-minimal missing sets are conditional on authored AND/OR semantics; routes are not proven sufficient.",
        })

    if any(path.read_bytes() != original[name] for name, path in paths.items()):
        raise RuntimeError("audit modified its input records")
    return {
        "schema_version": "1.0.0",
        "method": "Author-proposed AND/OR graph with minimal unresolved leaf sets",
        "certification": "NOT_CERTIFIED",
        "proof_status": "NOT_ESTABLISHED",
        "route_sufficiency": "NOT_VALIDATED",
        "clay_prize_readiness": "NOT_ELIGIBLE",
        "field_coverage_is_not_proof": True,
        "official_targets": len(reports),
        "canonical_open_work_packages": alignment["open_work_packages"],
        "additional_proposed_bridges": len(bridges),
        "alternative_routes": len(raw_routes),
        "poincare_externally_solved": True,
        "poincare_mathos_reconstruction": "BLOCKED",
        "external_claims_as_of": external["status_as_of"],
        "external_claims": [
            {
                "claim_id": e["claim_id"],
                "model_key": e["model_key"],
                "state": e["state"],
                "source": e["source"],
                "mathos_proof": False,
            } for e in events
        ],
        "source_sha256": {
            name: hashlib.sha256(content).hexdigest()
            for name, content in original.items()
        },
        "targets": reports,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args(argv)
    report = audit_clay_proof_topology()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output_dir is None:
        print(rendered, end="")
    else:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        target = args.output_dir / "clay_proof_topology.json"
        target.write_text(rendered, encoding="utf-8")
        print(f"Wrote {target}; all proof routes remain NOT_VALIDATED")


if __name__ == "__main__":
    main()
