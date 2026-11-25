"""Auditable TGA reports, independent finite truth-table checks and replay."""
import argparse
import hashlib
import json
from pathlib import Path

from .gap_analysis import Claim, models
from .certification_audit import exhaustive_check, canonical_graph
from .tga_engine import Limits, ResourceLimitError, solve, minimal_blockers

ORACLE_MAX_OPEN = 10


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def reachable(graph, target):
    found, todo = set(), [target]
    while todo:
        key = todo.pop()
        if key not in found:
            found.add(key)
            todo.extend(d for route in graph[key].routes for d in route)
    return {key: graph[key] for key in sorted(found)}


def report(graph, target, *, limits=None):
    limits = limits if limits is not None else Limits()
    try:
        answer, metrics = solve(graph, target, limits=limits)
        completions = answer["minimal_completion_sets"]
        blockers = minimal_blockers(completions, limits=limits)
    except ResourceLimitError as exc:
        return {"status": "RESOURCE_LIMIT", "target": target, "reason": str(exc),
                "minimal_completion_sets": None, "minimal_blocking_sets": None,
                "mathematical_certification": "NOT_CERTIFIED", "level_6_certified": False}
    subgraph = reachable(graph, target)
    # Separate truth-table evaluator, not the antichain recurrence.
    opens = sum(c.state == "open" for c in subgraph.values())
    if opens <= ORACLE_MAX_OPEN and len(subgraph) <= 100:
        oracle = {"status": "PASS", **exhaustive_check(subgraph, target, completions,
                                                       max_open=ORACLE_MAX_OPEN)}
        if blockers:
            # Independently enumerate all minimal hitting sets at this bounded size.
            from itertools import combinations
            leaves = sorted(k for k, c in subgraph.items() if c.state == "open")
            expected = []
            for n in range(len(leaves) + 1):
                for values in combinations(leaves, n):
                    s = set(values)
                    if all(s.intersection(route) for route in completions) and not any(t <= s for t in expected):
                        expected.append(s)
            if {frozenset(s) for s in expected} != {frozenset(s) for s in blockers}:
                raise ValueError("blocking-set oracle mismatch")
        elif [] not in completions:
            raise ValueError("nonclosed model must have a blocking set")
    else:
        oracle = {"status": "NOT_RUN_SIZE_LIMIT", "reachable_open_leaves": opens}
    graph_data = json.loads(json.dumps(canonical_graph(graph)))
    payload = {
        "schema": "mathos.tga.exact-report/1",
        "graph": graph_data, "graph_sha256": digest(graph_data),
        "target": target, "limits": vars(limits),
        "status": answer["status"], "minimal_completion_sets": completions,
        "common_to_all_modeled_routes": answer["common_to_all_modeled_routes"],
        "minimal_blocking_sets": blockers,
        "finite_oracle": oracle, "engine_metrics": metrics,
        "mathematical_certification": "NOT_CERTIFIED", "level_6_certified": False,
        "scope": "Authored finite monotone Boolean routes; external leaves and sufficiency assumed",
    }
    return dict(payload, sha256=digest(payload))


def replay(packet):
    if not isinstance(packet, dict):
        raise ValueError("packet must be an object")
    payload = {k: v for k, v in packet.items() if k != "sha256"}
    if packet.get("sha256") != digest(payload) or packet.get("schema") != "mathos.tga.exact-report/1":
        raise ValueError("invalid report checksum or schema")
    # Never accept a supplied verdict: reconstruct from the graph and rerun.
    # Do not let an untrusted packet raise resource limits above local defaults.
    limits = Limits(**packet["limits"])
    if any(v > getattr(Limits(), k) for k, v in vars(limits).items()):
        raise ValueError("packet exceeds local replay limits")
    graph = {k: Claim(v["label"], v["state"], tuple(tuple(r) for r in v["routes"]), v["note"])
             for k, v in packet["graph"].items()}
    if report(graph, packet["target"], limits=limits) != packet:
        raise ValueError("report does not reproduce")
    return {"reproduced": True, "graph_sha256": packet["graph_sha256"],
            "mathematical_certification": "NOT_CERTIFIED", "level_6_certified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("suite", "replay"))
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    if args.operation == "replay":
        print(json.dumps(replay(json.loads(args.path.read_text(encoding="utf-8"))), indent=2))
        return
    from mathos.research.tga_universal_bridges import graph, TARGETS
    cases = [(name, g, "target") for name, g in models().items()]
    universal = graph()
    cases.extend(("universal-" + key, universal, key) for key in TARGETS)
    args.path.mkdir(parents=True, exist_ok=False)
    for name, g, key in cases:
        result = report(g, key)
        if result.get("finite_oracle", {}).get("status") != "PASS":
            raise RuntimeError("required bounded oracle did not pass: " + name)
        replay(result)
        (args.path / (name + ".json")).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                                                 encoding="utf-8")
    print(f"{len(cases)} scoped reports generated and replayed")


if __name__ == "__main__":
    main()
