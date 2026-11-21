"""Bounded, kernel-checkable F2 graph cycle-space certificates for TECT-X.

A strictly typed graph manifest is converted into Lean propositions asserting
the complete mod-2 cycle space and independent cycle-basis coefficients.
Lean must check the actual universally quantified propositions; the Python
Gauss elimination and brute-force checks are separate preflight diagnostics.

This is finite *graph 1-skeleton topology only*. No formal semantics of the
research conjectures, no proof that the Python model handles arbitrary
graphs, and no human independent research validation is implied.
"""
from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any

from mathos.research.tect_x_thematic_gate import ROOT

MANIFEST = ROOT / "docs/research/TECT_X_FINITE_GRAPH_CERTIFICATES.v1.json"
PINNED_LEAN = "4.14.0"
SCOPE = "BOUNDED_FINITE_GRAPH_1_SKELETON_OVER_F2"
NAME = re.compile(r"[a-z][a-z0-9_]{0,31}\Z")
VERSION = re.compile(r"^Lean \(version ([^, )]+)", re.MULTILINE)
MAX_GRAPHS, MAX_VERTICES, MAX_EDGES, MAX_H1 = 12, 7, 8, 4
MAX_SOURCE_BYTES = 120_000


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _xor(xs: list[str]) -> str:
    if not xs:
        return "false"
    result = xs[0]
    for item in xs[1:]:
        result = f"(Bool.xor {result} {item})"
    return result


def _conj(xs: list[str]) -> str:
    return "(" + (" ∧ ".join(xs) if xs else "True") + ")"


def _disj(xs: list[str]) -> str:
    return "(" + (" ∨ ".join(xs) if xs else "False") + ")"


def _topology(n: int, edges: list[tuple[int, int]]) -> dict[str, Any]:
    """Cross-check incidence nullspace, exhaustive cycles and connectivity.

    Gaussian elimination constructs a cycle basis. Independent brute-force
    enumeration checks every edge subset against the original incidence
    equations and verifies the generated span exactly. Union-find and BFS
    independently agree on H0 for each component.
    """
    m = len(edges)
    rows = [0] * n
    adjacency = [set() for _ in range(n)]
    parents = list(range(n))

    def find(i: int) -> int:
        while parents[i] != i:
            i = parents[i]
        return i

    for i, (u, v) in enumerate(edges):
        rows[u] ^= 1 << i
        rows[v] ^= 1 << i
        adjacency[u].add(v)
        adjacency[v].add(u)
        a, b = find(u), find(v)
        parents[a] = b

    seen: set[int] = set()
    bfs_component_count = 0
    for start in range(n):
        if start in seen:
            continue
        bfs_component_count += 1
        queue = deque([start])
        seen.add(start)
        while queue:
            cur = queue.popleft()
            for dest in sorted(adjacency[cur]):
                if dest not in seen:
                    seen.add(dest)
                    queue.append(dest)
    dsu_count = len({find(i) for i in range(n)})
    if bfs_component_count != dsu_count:
        raise ValueError("independent BFS / disjoint-set connectivity checks disagree")

    matrix = rows.copy()
    pivots: dict[int, int] = {}
    current = 0
    for column in range(m):
        pivot = next((i for i in range(current, n)
                      if (matrix[i] >> column) & 1), None)
        if pivot is None:
            continue
        matrix[current], matrix[pivot] = matrix[pivot], matrix[current]
        for other in range(n):
            if other != current and ((matrix[other] >> column) & 1):
                matrix[other] ^= matrix[current]
        pivots[column] = current
        current += 1
    basis = []
    for free in range(m):
        if free in pivots:
            continue
        mask = 1 << free
        for column, row in pivots.items():
            if (matrix[row] >> free) & 1:
                mask ^= 1 << column
        basis.append(mask)

    rank = len(pivots)
    beta = len(basis)
    if beta != m - n + dsu_count or rank != n - dsu_count:
        raise ValueError("Euler characteristic and incidence rank checks disagree")
    if beta > MAX_H1:
        raise ValueError("cycle-space dimension exceeds the bounded Lean case budget")

    def boundary_zero(mask: int) -> bool:
        return all((row & mask).bit_count() % 2 == 0 for row in rows)

    actual_cycles = {mask for mask in range(1 << m) if boundary_zero(mask)}
    span = set()
    for flags in range(1 << beta):
        combined = 0
        for i, vector in enumerate(basis):
            if (flags >> i) & 1:
                combined ^= vector
        if combined in span:
            raise ValueError("cycle basis is not independent")
        span.add(combined)
    if actual_cycles != span or len(span) != (1 << beta):
        raise ValueError("exhaustive F2 cycle enumeration disagrees with Gaussian basis")

    return {
        "h0_components": dsu_count,
        "h1_cycle_dimension": beta,
        "vertices": n,
        "edges": m,
        "cycle_basis_masks": basis,
        "cycle_masks": sorted(span),
        "number_of_1cycles": len(span),
        "scope": "Simple undirected finite graph with no 2-cells over F2",
    }


def analyze_manifest(raw: Any) -> dict[str, Any]:
    """Validate research assumptions and claimed graph dimensions, fail closed."""
    if not isinstance(raw, dict):
        raise ValueError("manifest must be a JSON object")
    if set(raw) != {
        "schema_version", "scope", "proof_status",
        "mathematical_theorem_certification", "graph_assumptions",
        "formal_check", "cases", "supported_scope", "assumption_policy",
        "no_clay_proof", "closed_conjecture_obligations",
    }:
        raise ValueError("unsupported or missing manifest fields")
    if (raw["schema_version"] != "1.0" or raw["scope"] != SCOPE or
            raw["proof_status"] != "KERNEL_CHECK_REQUIRED" or
            raw["mathematical_theorem_certification"] is not False or
            raw["no_clay_proof"] is not True or raw["closed_conjecture_obligations"] != []):
        raise ValueError("unsupported scope or illegal research-status promotion")
    if not isinstance(raw["graph_assumptions"], list) or len(raw["graph_assumptions"]) < 3:
        raise ValueError("explicit mathematical assumptions are required")
    for string_field in ("formal_check", "supported_scope", "assumption_policy"):
        if not isinstance(raw[string_field], str) or not raw[string_field].strip():
            raise ValueError(f"missing explanatory policy field: {string_field}")
    cases = raw["cases"]
    if not isinstance(cases, list) or not (1 <= len(cases) <= MAX_GRAPHS):
        raise ValueError("bounded case array required")
    ids: set[str] = set()
    results = []
    for item in cases:
        if not isinstance(item, dict) or set(item) != {
            "id", "vertices", "edges", "expected_h0", "expected_h1"
        }:
            raise ValueError("graph cases must contain exactly the canonical keys")
        name = item["id"]
        if not isinstance(name, str) or not NAME.fullmatch(name) or name in ids:
            raise ValueError("graph case id must be unique and a safe Lean identifier")
        ids.add(name)
        n = item["vertices"]
        if type(n) is not int or not 1 <= n <= MAX_VERTICES:
            raise ValueError(f"{name}: number of vertices is out of bounds")
        edges_raw = item["edges"]
        if not isinstance(edges_raw, list) or len(edges_raw) > MAX_EDGES:
            raise ValueError(f"{name}: number of edges is out of bounds")
        edges: list[tuple[int, int]] = []
        for edge in edges_raw:
            if (not isinstance(edge, list) or len(edge) != 2 or
                    any(type(v) is not int for v in edge)):
                raise ValueError(f"{name}: edges must be pairs of integers")
            u, v = edge
            if not (0 <= u < v < n):
                raise ValueError(f"{name}: every edge must have u < v and valid endpoints")
            edges.append((u, v))
        if len(set(edges)) != len(edges):
            raise ValueError(f"{name}: duplicate edge / multigraph not supported")
        for claim in ("expected_h0", "expected_h1"):
            if type(item[claim]) is not int or item[claim] < 0:
                raise ValueError(f"{name}: {claim} must be a nonnegative integer")
        topology = _topology(n, edges)
        if topology["h0_components"] != item["expected_h0"] or topology["h1_cycle_dimension"] != item["expected_h1"]:
            raise ValueError(f"{name}: claimed H0/H1 contradict the finite incidence complex")
        results.append({"id": name, **topology, "edge_pairs": edges})
    return {
        "schema_version": "1.0",
        "validated_scope": SCOPE,
        "source_audit_passed": True,
        "mathematical_theorem_certification": False,
        "scientific_claims_closed": [],
        "cases": results,
        "total_graphs": len(results),
    }


def _emit_graph(case: dict[str, Any]) -> tuple[str, list[str]]:
    name = case["id"]
    m, n = case["edge_pairs"], case["vertices"]
    evars = [f"e{i}" for i in range(len(m))]
    basis = case["cycle_basis_masks"]
    bvars = [f"b{i}" for i in range(len(basis))]
    bind_e = " ".join(f"({e} : Bool)" for e in evars)

    incidence = [
        _xor([evars[i] for i, edge in enumerate(m) if v in edge]) + " = false"
        for v in range(n)
    ]
    # Spanning target is enumerated from F2-basis combinations, and Lean
    # independently checks it against *every* edge incidence valuation.
    options: list[str] = []
    for flags in range(1 << len(basis)):
        mask = 0
        for i, vector in enumerate(basis):
            if (flags >> i) & 1:
                mask ^= vector
        options.append(_conj([
            f"{evars[i]} = {'true' if (mask >> i) & 1 else 'false'}"
            for i in range(len(evars))
        ]))
    target = _disj(options)
    cycle_name = f"MathOS.TECTX.GraphCertificates.{name}_cycles_exact"
    basis_name = f"MathOS.TECTX.GraphCertificates.{name}_basis_independent"

    if evars:
        split_e = "  " + " <;> ".join(f"cases {var}" for var in evars) + " <;> decide"
        cycle_source = (
            f"theorem {name}_cycles_exact {bind_e} :\n"
            f"    {_conj(incidence)} ↔ {target} := by\n"
            + split_e + "\n"
        )
    else:
        cycle_source = (
            f"theorem {name}_cycles_exact :\n"
            f"    {_conj(incidence)} ↔ {target} := by\n"
            "  decide\n"
        )

    if bvars:
        expansions = [
            _xor([bvars[i] for i, vector in enumerate(basis) if (vector >> j) & 1]) + " = false"
            for j in range(len(evars))
        ]
        injective_source = (
            f"theorem {name}_basis_independent "
            + " ".join(f"({b} : Bool)" for b in bvars) + " :\n"
            + f"    {_conj(expansions)} ↔ {_conj([f'{b} = false' for b in bvars])} := by\n"
            + "  " + " <;> ".join(f"cases {var}" for var in bvars) + " <;> decide\n"
        )
    else:
        injective_source = (
            f"theorem {name}_basis_independent : True := by\n"
            "  trivial\n"
        )
    return cycle_source + "\n" + injective_source + "\n", [cycle_name, basis_name]


def emit_lean(analysis: dict[str, Any]) -> tuple[str, list[str]]:
    """Emit no arbitrary Lean code. Every proof script is fixed and exhaustive."""
    body = [
        "import Init",
        "set_option warningAsError true",
        "/-! Bounded TECT-X F2 graph incidence and cycle-space certificate.",
        "All graphs are author-specified simple 1-skeleta (no 2-cells).",
        "These formulas concern exact finite Bool/F2 edge chains only.",
        "No correspondence to RH, BSD or Selmer is established. -/",
        "namespace MathOS.TECTX.GraphCertificates",
        "",
    ]
    all_theorems = []
    for case in analysis["cases"]:
        part, names = _emit_graph(case)
        body.append(part)
        all_theorems.extend(names)
    body.append("end MathOS.TECTX.GraphCertificates\n")
    body.extend(f"#print axioms {name}" for name in all_theorems)
    source = "\n".join(body) + "\n"
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ValueError("generated Lean source is too large")
    return source, all_theorems


def _parse_axiom_reports(output: str, theorem_names: list[str]) -> dict[str, list[str]]:
    verified = {}
    for theorem in theorem_names:
        # Require exactly one unambiguous report, no sorryAx, untrusted axiom,
        # or missing report. The pinned kernel is the actual verifier.
        lines = [
            line.strip() for line in output.splitlines()
            if f"'{theorem}' " in line and
            ("does not depend on any axioms" in line or "depends on axioms:" in line)
        ]
        if len(lines) != 1 or f"'{theorem}' does not depend on any axioms" not in lines[0]:
            raise ValueError(f"missing/ambiguous/nonempty transitive axiom report: {theorem}")
        verified[theorem] = []
    return verified


def replay(raw: Any, *, lean: str = "lean",
           output_dir: Path | None = None, run_lean: bool = False) -> dict[str, Any]:
    analysis = analyze_manifest(raw)
    source, theorem_names = emit_lean(analysis)
    result = {
        **analysis,
        "kernel_checked": False,
        "formal_status": "NOT_RUN",
        "formal_theorem_count": 0,
        "closed_conjecture_obligations": [],
        "generated_lean_sha256": _digest(source.encode("utf-8")),
        "manifest_sha256": _digest(
            json.dumps(raw, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ),
        "lean_version": None,
        "transitive_axioms": None,
        "ok": True,
    }
    if not run_lean:
        return result
    if output_dir is None:
        raise ValueError("a persistent output directory is required for kernel-replayed certificates")
    try:
        ver = subprocess.run([lean, "--version"], capture_output=True, text=True,
                             timeout=20, check=False)
        match = VERSION.search(ver.stdout)
        if ver.returncode or match is None or match.group(1) != PINNED_LEAN:
            raise ValueError("Lean 4.14.0 is required; no fallback to unpinned proof checking")
        with tempfile.TemporaryDirectory(prefix="mathos-tectx-general-f2-") as tmp:
            p = Path(tmp) / "TECTXGeneralFiniteGraph.lean"
            p.write_text(source, encoding="utf-8")
            checked = subprocess.run([lean, str(p)], cwd=tmp,
                                     capture_output=True, text=True, timeout=120,
                                     check=False)
            if checked.returncode or "warning:" in checked.stdout + checked.stderr:
                raise ValueError("Lean kernel rejected finite graph theorems: " +
                                 (checked.stdout + checked.stderr)[-2000:])
            axioms = _parse_axiom_reports(checked.stdout, theorem_names)
            if p.read_text(encoding="utf-8") != source:
                raise ValueError("generated theorem source changed during kernel check")
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "TECTXGeneralFiniteGraph.lean").write_text(source, encoding="utf-8")
        result.update({
            "kernel_checked": True,
            "formal_status": "LEAN_KERNEL_CHECKED_EXACT_FINITE_GRAPH_CYCLE_SPACES",
            "formal_theorem_count": len(theorem_names),
            "lean_version": ver.stdout.strip().splitlines()[0],
            "transitive_axioms": axioms,
            "generated_source_saved_to": "TECTXGeneralFiniteGraph.lean",
        })
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        result.update({"ok": False, "formal_status": "KERNEL_CHECK_FAILED",
                       "kernel_checked": False, "failure": str(exc)})
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST,
                        help="bounded finite graph manifest; not a theorem of arbitrary scope")
    parser.add_argument("--check-lean", action="store_true",
                        help="run pinned Lean on each all-Boolean edge-cycle theorem")
    parser.add_argument("--lean", default="lean", help="Lean 4.14.0 executable")
    parser.add_argument("--artifact-dir", type=Path,
                        default=Path("artifacts/tect-x/general-f2"))
    parser.add_argument("--report", type=Path, help="save JSON report")
    args = parser.parse_args(argv)
    try:
        if args.manifest.stat().st_size > 131_072:
            raise ValueError("manifest exceeds size budget")
        raw = json.loads(args.manifest.read_text(encoding="utf-8"))
        report = replay(raw, lean=args.lean, output_dir=args.artifact_dir,
                        run_lean=args.check_lean)
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        report = {
            "ok": False, "kernel_checked": False, "formal_status": "INVALID_INPUT",
            "scientific_claims_closed": [], "failure": str(exc),
        }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                               encoding="utf-8")
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
