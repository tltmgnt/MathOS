"""TECT-X topological gap analysis / intelligent proof-verification *audit*.

A deterministic research assistant for authored proof obligations, not an LLM,
formal proof assistant, independent verifier, or theorem-certification engine.

It reuses MathOS's existing AND/OR proof dependency analyzer, indexes the
six-theme evidence registry, rejects unsupported claim promotion, computes the
topology of the *dependency graph's undirected 1-skeleton*, and ranks actionable
open proof obligations. Graph H0/H1 describes bookkeeping connectivity only:
it is not homology of a mathematical object appearing in a conjecture.
"""
from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
from typing import Any

from mathos.proof_analysis.gap_analysis import Claim, analyze
from mathos.research.tect_x_thematic_gate import ROOT, evaluate_register

CASES_PATH = "docs/research/TECT_X_PROOF_VERIFIER_CASES.v1.json"
THEMES_PATH = "docs/research/TECT_X_THEMATIC_REGISTER.v1.json"
OBLIGATIONS_PATH = "docs/proof-analysis/OBLIGATIONS.v1.json"
REQUIRED_CASES = {"RH-TGA", "SELMER-TGA", "ZETA-FINITE"}
# Prevent a valid-looking case ID being silently replaced with a trivial
# or differently quantified target. These are modeling invariants, not proofs.
CASE_INVARIANTS = {
    "RH-TGA": ("RH.target", "UNIVERSAL", {"RH.operator", "RH.zero_identity", "RH.global_bridge"}),
    "SELMER-TGA": ("SEL.target", "INFINITE_FAMILY", {"SEL.squareclasses", "SEL.local_images", "SEL.mean16", "SEL.infinitude"}),
    "ZETA-FINITE": ("ZETA.target", "FINITE", {"ZETA.features", "ZETA.rips_sample", "ZETA.controls"}),
}
MAX_MODELED_COMBINATIONS = 8192
KINDS = {"DERIVED", "OPEN_OBLIGATION", "BOUNDED_EVIDENCE"}
SCOPES = {"FINITE", "CONDITIONAL", "INFINITE_FAMILY", "UNIVERSAL"}
NODE_KEYS = {"id", "kind", "scope", "routes", "evidence_ids", "mapped_claim", "next_action"}
CASE_KEYS = {"id", "title", "target", "target_scope", "theme_ids", "route_warning", "nodes"}


def _load(root: Path, path: str) -> Any:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _source_digest(root: Path, path: str) -> str:
    return hashlib.sha256((root / path).read_bytes()).hexdigest()


def _topology(nodes: dict[str, dict], target: str) -> dict[str, Any]:
    """Finite graph H0 and H1 of a one-dimensional undirected CW complex.

    Directed proof-graph cycles are separately rejected by the AND/OR analyzer.
    An undirected cycle may simply reflect shared proof dependencies.
    """
    adjacency: dict[str, set[str]] = {key: set() for key in nodes}
    edges: set[tuple[str, str]] = set()
    for parent, item in nodes.items():
        for route in item.get("routes", []):
            for child in route:
                edge = tuple(sorted((parent, child)))
                edges.add(edge)
                adjacency[parent].add(child)
                adjacency[child].add(parent)

    seen: set[str] = set()
    connected: list[list[str]] = []
    for start in sorted(nodes):
        if start in seen:
            continue
        component = []
        queue = deque([start])
        seen.add(start)
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in sorted(adjacency[current]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        connected.append(sorted(component))

    if not connected:
        raise ValueError("empty graph is not a valid proof route")
    target_component = next(comp for comp in connected if target in comp)
    return {
        "graph_vertices": len(nodes),
        "graph_edges": len(edges),
        "graph_h0_components": len(connected),
        "graph_h1_cycle_rank": len(edges) - len(nodes) + len(connected),
        "disconnected_from_target": sorted(set(nodes) - set(target_component)),
        "meaning": (
            "H0 and H1 concern the undirected dependency 1-skeleton, "
            "not the topology or truth of the theorem being analyzed."
        ),
    }


def _is_scope_gap(leaf_scope: str, target_scope: str) -> bool:
    if leaf_scope == "CONDITIONAL":
        return target_scope != "CONDITIONAL"
    rank = {"FINITE": 0, "INFINITE_FAMILY": 1, "UNIVERSAL": 2}
    if target_scope == "CONDITIONAL":
        return leaf_scope != "CONDITIONAL"
    return rank[leaf_scope] < rank[target_scope]


def _route_combination_budget(nodes: dict[str, dict], target: str) -> None:
    """Upper-bound authored OR/AND Cartesian products to avoid explosive audits.

    The estimate deliberately overcounts overlap; it protects the generic
    analyzer from adversarial models with combinatorially many proof routes.
    """
    cache: dict[str, int] = {}
    active: set[str] = set()

    def count(key: str) -> int:
        if key in cache:
            return cache[key]
        if key in active:
            raise ValueError("Dependency cycle: " + key)
        active.add(key)
        node = nodes[key]
        if node["kind"] != "DERIVED":
            total = 1
        else:
            total = 0
            for route in node["routes"]:
                choices = 1
                for dep in route:
                    choices *= count(dep)
                    if choices > MAX_MODELED_COMBINATIONS:
                        raise ValueError("too many modeled proof-route combinations")
                total += choices
                if total > MAX_MODELED_COMBINATIONS:
                    raise ValueError("too many modeled proof-route combinations")
        active.remove(key)
        cache[key] = total
        return total

    count(target)


def _analyze_case(case: dict[str, Any]) -> dict[str, Any]:
    nodes = {node["id"]: node for node in case["nodes"]}
    _route_combination_budget(nodes, case["target"])
    graph = {
        key: Claim(
            label=key,
            state="derived" if node["kind"] == "DERIVED" else "open",
            routes=tuple(tuple(route) for route in node.get("routes", [])),
            note=node.get("next_action", ""),
        )
        for key, node in nodes.items()
    }
    modeled = analyze(graph, case["target"])
    topology = _topology(nodes, case["target"])
    completion = modeled["minimal_completion_sets"]
    required = set(modeled["common_to_all_modeled_routes"])
    leaves = [node for node in case["nodes"] if node["kind"] != "DERIVED"]
    suggestions = []
    scopes_to_review = []
    for leaf in leaves:
        leaf_id = leaf["id"]
        n_routes = sum(leaf_id in route for route in completion)
        if not n_routes:
            continue
        bounded = leaf["kind"] == "BOUNDED_EVIDENCE"
        scope_gap = _is_scope_gap(leaf["scope"], case["target_scope"])
        if scope_gap:
            scopes_to_review.append({
                "obligation": leaf_id,
                "evidence_scope": leaf["scope"],
                "target_scope": case["target_scope"],
                "limitation": "Narrow or conditional evidence does not establish the target's quantified scope.",
            })
        # The score only orders next review steps; it is not a probability
        # of truth, performance estimate or estimate of proof progress.
        score = (100 if leaf_id in required else 0) + 10 * n_routes + (20 if not bounded else 0) + (10 if scope_gap else 0)
        suggestions.append({
            "obligation": leaf_id,
            "priority_score": score,
            "common_to_all_authored_routes": leaf_id in required,
            "modeled_completion_sets_containing": n_routes,
            "evidence_kind": leaf["kind"],
            "evidence_ids": leaf["evidence_ids"],
            "source_scope": leaf["scope"],
            "scope_gap": scope_gap,
            "recommended_next_action": leaf["next_action"],
        })
    suggestions.sort(key=lambda item: (-item["priority_score"], item["obligation"]))
    return {
        "case_id": case["id"],
        "title": case["title"],
        "target": case["target"],
        "target_scope": case["target_scope"],
        "conclusion": "BLOCKED_NOT_MATHEMATICALLY_VERIFIED",
        "authored_route_warning": case["route_warning"],
        "topological_gap_analysis": topology,
        "minimal_completion_sets": completion,
        "common_to_all_authored_routes": sorted(required),
        "scope_transfer_flags": scopes_to_review,
        "prioritized_unresolved_obligations": suggestions,
        "interpretation": (
            "The proposed dependency edges and evidence summaries have not been "
            "independently proved sufficient. Every leaf remains an unverified "
            "proof obligation, including those with bounded evidence."
        ),
    }


def verify_cases(payload: Any, root: Path = ROOT) -> dict[str, Any]:
    """Fail closed on metadata mistakes; never assert a mathematical proof."""
    issues: list[str] = []
    report: dict[str, Any] = {
        "ok": False,
        "validation": "SOURCE_CONSISTENCY_ONLY",
        "scientific_certification": False,
        "issues": issues,
        "cases": [],
    }

    if not isinstance(payload, dict):
        issues.append("proof cases must be a JSON object")
        return report
    if payload.get("schema_version") != "1.0":
        issues.append("schema_version must be 1.0")
    if payload.get("scientific_status") != "NOT_PROOF_CERTIFIED":
        issues.append("scientific_status cannot assert mathematical certification")
    if payload.get("thematic_register") != THEMES_PATH or payload.get("obligation_register") != OBLIGATIONS_PATH:
        issues.append("canonical thematic and obligation register paths required")
    if not isinstance(payload.get("model_semantics"), str) or not payload["model_semantics"].strip():
        issues.append("model_semantics must declare graph limitations")

    try:
        thematic = _load(root, THEMES_PATH)
        theme_result = evaluate_register(thematic, root)
        if not theme_result["ok"]:
            issues.append("thematic evidence register failed existing gate: " + "; ".join(theme_result["issues"]))
        evidence_ids = {entry["id"] for entry in thematic["evidence"]}
        theme_ids = {entry["id"] for entry in thematic["themes"]}
        obligation_data = _load(root, OBLIGATIONS_PATH)
        mapped_work_packages = {
            item["claim_id"]: item
            for track in obligation_data["tracks"]
            for item in track["work_packages"]
        }
        report["source_sha256"] = {
            "thematic_register": _source_digest(root, THEMES_PATH),
            "obligation_register": _source_digest(root, OBLIGATIONS_PATH),
        }
    except (OSError, ValueError, KeyError, TypeError) as exc:
        issues.append(f"cannot load or validate source registers: {exc}")
        return report

    cases = payload.get("cases")
    if not isinstance(cases, list):
        issues.append("cases must be an array")
        return report
    if len(cases) != len(REQUIRED_CASES):
        issues.append("expected exactly the three anchored research cases")
    actual_ids = []
    for c in cases:
        actual_ids.append(c.get("id") if isinstance(c, dict) else None)
    if set(actual_ids) != REQUIRED_CASES or len(actual_ids) != len(set(actual_ids)):
        issues.append("case ids must be unique and include RH-TGA, SELMER-TGA, ZETA-FINITE")

    for idx, case in enumerate(cases):
        start_issues = len(issues)
        if not isinstance(case, dict):
            issues.append(f"case[{idx}] must be an object")
            continue
        cid = str(case.get("id"))
        if set(case) - CASE_KEYS:
            issues.append(f"{cid}: unsupported case fields: {sorted(set(case) - CASE_KEYS)}")
        if not isinstance(case.get("title"), str) or not case["title"].strip():
            issues.append(f"{cid}: missing title")
        if not isinstance(case.get("route_warning"), str) or not case["route_warning"].strip():
            issues.append(f"{cid}: missing route warning")
        if case.get("target_scope") not in {"FINITE", "INFINITE_FAMILY", "UNIVERSAL"}:
            issues.append(f"{cid}: invalid target scope")
        refs = case.get("theme_ids")
        if not isinstance(refs, list) or not refs or any(ref not in theme_ids for ref in refs) or len(refs) != len(set(refs)):
            issues.append(f"{cid}: invalid thematic references")
        nodes = case.get("nodes")
        if not isinstance(nodes, list) or not (2 <= len(nodes) <= 30):
            issues.append(f"{cid}: expected between 2 and 30 nodes")
            continue
        if any(not isinstance(n, dict) for n in nodes):
            issues.append(f"{cid}: all nodes must be objects")
            continue
        node_ids = [n.get("id") for n in nodes]
        if any(not isinstance(nid, str) or not nid.strip() for nid in node_ids) or len(set(node_ids)) != len(node_ids):
            issues.append(f"{cid}: duplicate or invalid node IDs")
            continue
        node_map = {n["id"]: n for n in nodes}
        requirements = CASE_INVARIANTS.get(cid)
        if requirements:
            required_target, required_scope, required_nodes = requirements
            if (case.get("target") != required_target or
                    case.get("target_scope") != required_scope):
                issues.append(f"{cid}: canonical target or quantified scope has changed")
            if not required_nodes.issubset(node_map):
                issues.append(f"{cid}: a required scientific blocker was removed")
        if case.get("target") not in node_map or node_map[case["target"]].get("kind") != "DERIVED":
            issues.append(f"{cid}: target must be a known DERIVED node")
        elif node_map[case["target"]].get("scope") != case["target_scope"]:
            issues.append(f"{cid}: target scope must match target node")
        for node in nodes:
            nid = node["id"]
            if set(node) - NODE_KEYS:
                issues.append(f"{cid}/{nid}: unsupported node fields: {sorted(set(node) - NODE_KEYS)}")
            if node.get("kind") not in KINDS or node.get("scope") not in SCOPES:
                issues.append(f"{cid}/{nid}: invalid kind or scope")
                continue
            if node["kind"] == "DERIVED":
                routes = node.get("routes")
                if not isinstance(routes, list) or not routes or len(routes) > 4:
                    issues.append(f"{cid}/{nid}: missing or excessive AND/OR routes")
                    continue
                for route in routes:
                    if not isinstance(route, list) or not route or len(route) > 10:
                        issues.append(f"{cid}/{nid}: invalid route")
                    elif len(route) != len(set(route)) or any(dep not in node_map for dep in route):
                        issues.append(f"{cid}/{nid}: unknown or repeated route dependency")
                if node.get("evidence_ids") or node.get("mapped_claim") or node.get("next_action"):
                    issues.append(f"{cid}/{nid}: derived nodes cannot bypass dependency review with evidence")
            else:
                if node.get("routes"):
                    issues.append(f"{cid}/{nid}: evidence leaves cannot contain proof routes")
                evidence = node.get("evidence_ids")
                if not isinstance(evidence, list) or not evidence or len(evidence) != len(set(evidence)) or any(eid not in evidence_ids for eid in evidence):
                    issues.append(f"{cid}/{nid}: missing or invalid evidence links")
                if not isinstance(node.get("next_action"), str) or not node["next_action"].strip():
                    issues.append(f"{cid}/{nid}: next_action required")
                mapping = node.get("mapped_claim")
                if mapping is not None:
                    work_package = mapped_work_packages.get(mapping)
                    if not work_package or work_package.get("graph_state") != "open":
                        issues.append(f"{cid}/{nid}: mapped claim must match an open existing proof obligation")
        if len(issues) > start_issues:
            continue
        try:
            result = _analyze_case(case)
            if result["topological_gap_analysis"]["disconnected_from_target"]:
                issues.append(f"{cid}: disconnected nodes not part of target dependency graph")
                continue
            report["cases"].append(result)
        except (ValueError, TypeError, RecursionError) as exc:
            issues.append(f"{cid}: invalid or cyclic authored proof graph: {exc}")

    report["ok"] = not issues
    report["summary"] = {
        "valid_cases_analyzed": len(report["cases"]),
        "total_open_or_bounded_obligations": sum(
            len(c["prioritized_unresolved_obligations"]) for c in report["cases"]
        ),
        "mathematical_theorems_certified": 0,
        "notion_of_topology": "H0/H1 of an undirected proof-dependency 1-skeleton",
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=ROOT / CASES_PATH)
    parser.add_argument("--report", type=Path, help="write a full machine-readable JSON report")
    parser.add_argument("--json", action="store_true", help="print JSON rather than summary")
    parser.add_argument("--require-proof", action="store_true", help="fail until independent mathematical certification exists (not supplied here)")
    parser.add_argument("--verify-lean-certificate", action="store_true",
                        help="run pinned Lean on exact finite F2 lemmas; never promote a conjecture")
    parser.add_argument("--verify-typed-arguments", action="store_true",
                        help="check typed proof terms against separately authored Lean reference goals")
    parser.add_argument("--lean", default="lean", help="Lean 4.14.0 executable for finite certificate replay")
    parser.add_argument("--verify-general-graph-cycles", action="store_true",
                        help="kernel-check finite F2 graph cycle spaces; does not certify conjectures")
    args = parser.parse_args(argv)

    try:
        input_data = json.loads(args.cases.read_text(encoding="utf-8"))
        result = verify_cases(input_data)
    except (OSError, ValueError) as exc:
        result = {"ok": False, "issues": [str(exc)], "cases": [], "scientific_certification": False}
    # The kernel certifies specific finite graph-chain lemmas, NOT authored
    # TGA edges or any open mathematical statement. Import lazily so the
    # independent certificate module can reference this graph checker safely.
    if args.verify_lean_certificate:
        from mathos.research.tect_x_formal_certificates import audit as formal_audit
        certificate = formal_audit(check_kernel=True, executable=args.lean)
        result["finite_f2_formal_certificate"] = {
            "status": certificate["formal_status"],
            "kernel_checked": certificate["kernel_checked"],
            "verified_theorems": certificate.get("verified_theorems", []),
            "transitive_axioms": certificate.get("transitive_axioms"),
            "closed_conjecture_obligations": [],
        }
        if not certificate.get("ok") or not certificate["kernel_checked"]:
            result["ok"] = False
            result["issues"].append("pinned Lean finite-F2 certificate replay failed")
        # Do not change mathematical_theorems_certified, the case verdicts,
        # or scientific_certification under any circumstance.
    if args.verify_general_graph_cycles:
        from mathos.research.tect_x_general_graph_certificates import (
            MANIFEST as GRAPH_MANIFEST, replay as general_replay
        )
        try:
            graph_manifest = json.loads(GRAPH_MANIFEST.read_text(encoding="utf-8"))
            graph_output_dir = ((args.report.parent if args.report is not None
                                else Path("artifacts/tect-x")) / "general-f2")
            graph_cert = general_replay(graph_manifest, lean=args.lean,
                                        output_dir=graph_output_dir, run_lean=True)
            result["general_graph_cycle_certificates"] = {
                "formal_status": graph_cert["formal_status"],
                "kernel_checked": graph_cert["kernel_checked"],
                "formal_theorem_count": graph_cert["formal_theorem_count"],
                "finite_graph_cases": graph_cert["total_graphs"],
                "verified_scope": graph_cert["validated_scope"],
                "closed_conjecture_obligations": [],
            }
            if not graph_cert["ok"] or not graph_cert["kernel_checked"]:
                result["ok"] = False
                result["issues"].append("pinned Lean general graph cycle-space certificate check failed")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            result["ok"] = False
            result["issues"].append(f"general finite graph proof checker failed: {exc}")
            result["general_graph_cycle_certificates"] = {
                "formal_status": "INVALID_OR_UNAVAILABLE",
                "kernel_checked": False,
                "closed_conjecture_obligations": [],
            }
        # Never mutate TGA case conclusions or convert graph facts into a
        # verified research theorem. Formal status applies to finite F2 graphs only.
    if args.verify_typed_arguments:
        from mathos.research.tect_x_typed_argument_gate import (
            MANIFEST as TYPED_MANIFEST, replay as typed_replay
        )
        try:
            manifest = json.loads(TYPED_MANIFEST.read_text(encoding="utf-8"))
            typed = typed_replay(manifest, check_lean=True, lean=args.lean)
            result["typed_argument_certificates"] = {
                "formal_status": typed["formal_status"],
                "kernel_checked": typed["kernel_checked"],
                "exact_formal_goals_checked": sum(bool(b["kernel_checked"]) for b in typed["bundles"]),
                "semantic_faithfulness_certified": False,
                "remaining_semantic_gaps": typed["gaps"],
                "closed_research_obligations": [],
            }
            if not typed["ok"] or not typed["kernel_checked"]:
                result["ok"] = False
                result["issues"].append("pinned Lean typed argument contract replay failed")
        except (OSError, ValueError, TypeError, KeyError) as exc:
            result["ok"] = False
            result["issues"].append("typed argument checker unavailable: " + str(exc))
            result["typed_argument_certificates"] = {
                "kernel_checked": False,
                "semantic_faithfulness_certified": False,
                "closed_research_obligations": [],
            }
        # No pass may promote semantic faithfulness or RH/Selmer research status.
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print("TECT-X intelligent proof-gap audit: " + ("CONSISTENT" if result["ok"] else "INVALID"))
        for case in result["cases"]:
            topo = case["topological_gap_analysis"]
            print(f"  {case['case_id']}: {case['conclusion']}; H0={topo['graph_h0_components']}, H1={topo['graph_h1_cycle_rank']}")
            print(f"    modeled alternatives: {len(case['minimal_completion_sets'])}; open review steps: {len(case['prioritized_unresolved_obligations'])}")
            for suggestion in case["prioritized_unresolved_obligations"][:3]:
                print(f"    - {suggestion['obligation']}: {suggestion['recommended_next_action']}")
        for issue in result["issues"]:
            print("  ERROR: " + issue)
        print("No mathematical proof certified. Topology measures the dependency graph only.")
    if not result["ok"]:
        return 1
    if args.require_proof:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
