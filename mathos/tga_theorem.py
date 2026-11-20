"""Finite propositional theorem prover for MathOS proof-route graphs.

A complete truth-table decision procedure for graph-modeled implications only.
It cannot prove the mathematical truth of labels or authored implication edges.
"""
from __future__ import annotations

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import re

from .proof_analysis.gap_analysis import Claim
from .proof_analysis.certification_audit import graph_hash

IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_\-]{0,79}$")
MAX_OPEN = 16
MAX_NODES = 256


def parse_spec(raw):
    if not isinstance(raw, dict) or set(raw) != {"schema", "claims", "premises", "goal"} or raw["schema"] != 1:
        raise ValueError("expected schema 1 with claims, premises and goal")
    claims = raw["claims"]
    if not isinstance(claims, dict) or not claims or len(claims) > MAX_NODES:
        raise ValueError("claims must be a nonempty bounded object")
    graph = {}
    for name, node in claims.items():
        if not isinstance(name, str) or not IDENT.fullmatch(name) or not isinstance(node, dict):
            raise ValueError("invalid claim identifier or record")
        if set(node) != {"state", "routes"}:
            raise ValueError("each claim requires exactly state and routes")
        state, routes = node["state"], node["routes"]
        if state not in {"open", "established_external", "derived"} or not isinstance(routes, list):
            raise ValueError("invalid claim state or routes")
        if state == "derived":
            if not routes or any(not isinstance(route, list) or not route for route in routes):
                raise ValueError("derived claim requires nonempty AND routes")
        elif routes:
            raise ValueError("non-derived claim cannot have routes")
        for route in routes:
            if not isinstance(route, list) or any(not isinstance(dep, str) or dep not in claims for dep in route):
                raise ValueError("unknown route dependency")
            if len(route) != len(set(route)):
                raise ValueError("duplicate dependency")
        graph[name] = Claim(label=name, state=state, routes=tuple(tuple(r) for r in routes))
    premises = raw["premises"]
    goal = raw["goal"]
    if (not isinstance(premises, list) or any(not isinstance(x, str) or x not in graph for x in premises)
            or len(premises) != len(set(premises)) or not isinstance(goal, str) or goal not in graph):
        raise ValueError("invalid premise or goal")
    # A cycle is not allowed even in an unused route.
    order, active, done = [], set(), set()

    def visit(name):
        if name in active:
            raise ValueError("dependency cycle")
        if name in done:
            return
        active.add(name)
        for route in graph[name].routes:
            for dep in route:
                visit(dep)
        active.remove(name)
        done.add(name)
        order.append(name)

    for name in sorted(graph):
        visit(name)
    leaves = sorted(k for k, c in graph.items() if c.state == "open")
    if len(leaves) > MAX_OPEN:
        raise ValueError("too many open leaves for exhaustive proof")
    return graph, sorted(premises), goal, leaves, order


def canonical_spec(raw):
    graph, premises, goal, _, _ = parse_spec(raw)
    return {
        "schema": 1,
        "claims": {
            key: {
                "state": graph[key].state,
                "routes": [list(route) for route in graph[key].routes],
            } for key in sorted(graph)
        },
        "premises": premises,
        "goal": goal,
    }


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def decide(raw):
    """Exhaustively decide premise entailment under the stated Boolean graph semantics."""
    spec = canonical_spec(raw)
    graph, premises, goal, leaves, order = parse_spec(spec)
    checked = 0
    satisfying_premises = 0
    countermodel = None
    for bits in product((False, True), repeat=len(leaves)):
        enabled = {leaf for leaf, bit in zip(leaves, bits) if bit}
        values = {}
        for name in order:
            claim = graph[name]
            if claim.state == "open":
                values[name] = name in enabled
            elif claim.state == "established_external":
                values[name] = True
            else:
                values[name] = any(all(values[dep] for dep in route) for route in claim.routes)
        checked += 1
        if all(values[name] for name in premises):
            satisfying_premises += 1
            if not values[goal]:
                countermodel = {leaf: leaf in enabled for leaf in leaves}
                break
    proved = countermodel is None
    verdict = "ENTAILED_WITHIN_GRAPH" if proved else "COUNTERMODEL_FOUND"
    return {
        "schema": "mathos_tga_finite_entailment/1",
        "spec_sha256": digest(spec),
        "graph_sha256": graph_hash(graph),
        "premises": premises,
        "goal": goal,
        "open_leaves": leaves,
        "assignments_checked": checked,
        "premise_satisfying_assignments_checked": satisfying_premises,
        "verdict": verdict,
        "countermodel": countermodel,
        "mathematical_theorem_certified": False,
        "kernel_checked": False,
        "scope": "Complete finite Boolean graph entailment, up to 16 open leaves; route soundness assumed",
    }


def verify(raw, certificate):
    """Independently replay the decision from input and compare all certificate fields."""
    if not isinstance(certificate, dict):
        raise ValueError("certificate must be an object")
    expected = decide(raw)
    if certificate != expected:
        raise ValueError("certificate disagrees with exhaustive graph semantics")
    return {
        "verified": True,
        "scope": expected["scope"],
        "spec_sha256": expected["spec_sha256"],
        "mathematical_theorem_certified": False,
        "kernel_checked": False,
    }


def _unique(pairs):
    data = {}
    for k, v in pairs:
        if k in data:
            raise ValueError("duplicate JSON key: " + k)
        data[k] = v
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("prove", "verify"))
    parser.add_argument("spec", type=Path)
    parser.add_argument("certificate", type=Path, nargs="?")
    args = parser.parse_args()
    try:
        if args.spec.stat().st_size > 1_048_576:
            raise ValueError("spec exceeds 1 MiB")
        spec = json.loads(args.spec.read_text(encoding="utf-8"), object_pairs_hook=_unique)
        if args.operation == "prove":
            result = decide(spec)
        else:
            if args.certificate is None:
                raise ValueError("verify requires a certificate path")
            if args.certificate.stat().st_size > 1_048_576:
                raise ValueError("certificate exceeds 1 MiB")
            cert = json.loads(args.certificate.read_text(encoding="utf-8"), object_pairs_hook=_unique)
            result = verify(spec, cert)
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError) as exc:
        parser.exit(2, f"{exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
