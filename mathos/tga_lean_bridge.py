"""Compile bounded TGA entailment into a Lean 4 kernel-checkable proposition.

The theorem concerns Boolean route semantics only. It is NOT a theorem about
the mathematical meaning of node labels or the validity of user-authored edges.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from .tga_theorem import canonical_spec, decide, parse_spec, _unique

MAX_LEAVES = 6
MAX_SOURCE = 65536
LEAN_VERSION = "4.14.0"
VERSION = re.compile(r"Lean \(version ([^, )]+)")
NO_AXIOMS = "'tga_graph_entailment' does not depend on any axioms"
AXIOMS = re.compile(r"'tga_graph_entailment' depends on axioms: \[([^\]]*)\]")


def compile_lean(raw: dict) -> dict:
    """Emit a closed Lean theorem whose quantifiers range over every open Bool."""
    spec = canonical_spec(raw)
    graph, premises, goal, leaves, _order = parse_spec(spec)
    if len(leaves) > MAX_LEAVES:
        raise ValueError("Lean bridge supports at most 6 open Boolean leaves")
    result = decide(spec)
    if result["verdict"] != "ENTAILED_WITHIN_GRAPH":
        raise ValueError("not entailed: a countermodel exists; refusing to emit a theorem")
    positions = {name: f"v{i}" for i, name in enumerate(leaves)}
    memo = {}

    def expr(node: str) -> str:
        if node in memo:
            return memo[node]
        claim = graph[node]
        if claim.state == "open":
            output = positions[node]
        elif claim.state == "established_external":
            output = "true"
        else:
            alternatives = []
            for route in claim.routes:
                alternatives.append("(" + " && ".join(expr(dep) for dep in route) + ")")
            output = "(" + " || ".join(alternatives) + ")"
        if len(output) > MAX_SOURCE // 2:
            raise ValueError("unfolded graph exceeds Lean source limit")
        memo[node] = output
        return output

    assumption = "(" + " && ".join(expr(name) for name in premises) + ")" if premises else "true"
    conclusion = expr(goal)
    binder = " ".join(f"(v{i} : Bool)" for i in range(len(leaves)))
    quantifier = f"∀ {binder}, " if binder else ""
    # Both sides are Boolean equality propositions, not informal labels.
    proposition = f"{quantifier}({assumption} = true) → ({conclusion} = true)"
    source = (
        "-- Generated from a MathOS TGA graph. Claims are Boolean abstractions.\n"
        "-- External claims are modeled as true *without independent proof*.\n"
        "set_option warningAsError true\n"
        "set_option maxHeartbeats 2000000\n"
        f"theorem tga_graph_entailment : {proposition} := by\n"
        "  decide\n"
        "#print axioms tga_graph_entailment\n"
    )
    if len(source.encode("utf-8")) > MAX_SOURCE:
        raise ValueError("generated Lean source too large")
    return {
        "schema": "mathos_tga_lean_bridge/1",
        "graph_spec_sha256": result["spec_sha256"],
        "lean_source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "source": source,
        "open_leaves": leaves,
        "external_assumptions": sorted(k for k, c in graph.items() if c.state == "established_external"),
        "lean_kernel_checked": False,
        "mathematical_statement_verified": False,
        "scope": "Finite graph-entailment proposition; route semantics are author-defined",
    }


def check_lean(raw: dict, executable: str = "lean") -> dict:
    artifact = compile_lean(raw)
    try:
        version_run = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("Lean is unavailable") from exc
    match = VERSION.search(version_run.stdout)
    if version_run.returncode != 0 or match is None or match.group(1) != LEAN_VERSION:
        raise ValueError("Lean 4.14.0 is required")
    with tempfile.TemporaryDirectory(prefix="mathos-tga-lean-") as temp:
        filename = Path(temp) / "TGA.lean"
        filename.write_text(artifact["source"], encoding="utf-8")
        try:
            result = subprocess.run([executable, str(filename)], cwd=temp, capture_output=True,
                                    text=True, timeout=90)
        except subprocess.TimeoutExpired as exc:
            raise ValueError("Lean timed out") from exc
    diagnostics = result.stdout + result.stderr
    if result.returncode != 0:
        raise ValueError("Lean rejected the generated theorem: " + diagnostics[:2000])
    # A pin, a passing compiler exit and an explicit axiom report are all required.
    lines = {line.strip() for line in diagnostics.splitlines()}
    if NO_AXIOMS not in lines:
        match_axioms = AXIOMS.search(diagnostics)
        raise ValueError("Lean axiom policy failed: " + (match_axioms.group(1) if match_axioms else "no axiom report"))
    return {
        "schema": "mathos_tga_lean_check/1",
        "lean_version": LEAN_VERSION,
        "graph_spec_sha256": artifact["graph_spec_sha256"],
        "lean_source_sha256": artifact["lean_source_sha256"],
        "lean_kernel_checked": True,
        "mathematical_statement_verified": False,
        "verified_scope": artifact["scope"],
        "external_assumptions": artifact["external_assumptions"],
        "axioms": [],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("emit", "check"))
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, help="Required for emit; destination .lean file")
    parser.add_argument("--lean", default="lean")
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 1_048_576:
            raise ValueError("graph input exceeds 1 MiB")
        spec = json.loads(args.input.read_text(encoding="utf-8"), object_pairs_hook=_unique)
        if args.operation == "emit":
            if args.output is None:
                raise ValueError("emit requires --output")
            result = compile_lean(spec)
            args.output.write_text(result.pop("source"), encoding="utf-8")
        else:
            result = check_lean(spec, args.lean)
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        parser.exit(2, str(exc) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
