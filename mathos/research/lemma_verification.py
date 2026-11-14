"""Exact, bounded polynomial-lemma counterexample checks with Lean handoffs.

This checks a deliberately tiny, non-executable DSL over integer polynomials,
linked to one registered OPEN MathOS research obligation. It never interprets
agent text as code, updates proof statuses, or certifies a Clay solution.

Usage:
  python -m mathos.research.lemma_verification --output-dir artifacts/lemmas
  python -m mathos.research.lemma_verification --output-dir artifacts/lemmas --verify-lean
"""
from __future__ import annotations

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any

from mathos.research.clay_alignment import TARGETS_PATH
from mathos.research.clay_proof_topology import (
    EXTERNAL_PATH, ROUTES_PATH, audit_clay_proof_topology,
)
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS, ROOT

MANIFEST_PATH = ROOT / "docs/research/LEMMA_CANDIDATES.v1.json"
MAX_CANDIDATES = 8
MAX_VARIABLES = 4
MAX_AST_NODES = 100
MAX_AST_DEPTH = 10
MAX_MONOMIALS = 4096
MAX_COEFFICIENT_BITS = 1024
MAX_TEST_POINTS = 625
IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")
CANDIDATE_ID = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,80}\Z")
POLICY = {
    "certification": "NOT_CERTIFIED",
    "clay_solution": "NOT_ESTABLISHED",
    "mathematical_scope": "TOY_INTEGER_POLYNOMIALS_ONLY",
    "proof_route_sufficiency": "NOT_VALIDATED",
    "automatic_claim_promotion": False,
    "independent_review": "NOT_PERFORMED",
}
Poly = dict[tuple[int, ...], int]


def _keys(obj: Any, expected: set[str], where: str) -> dict:
    if type(obj) is not dict or set(obj) != expected:
        raise ValueError(f"invalid {where} keys")
    return obj


def _text(value: Any, where: str, minimum: int = 12) -> str:
    if (type(value) is not str or len(value.strip()) < minimum
            or len(value) > 1500):
        raise ValueError(f"invalid {where}")
    return value


def _int(value: Any, where: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"invalid {where}")
    return value


def _clean(poly: Poly) -> Poly:
    result = {k: v for k, v in poly.items() if v}
    if len(result) > MAX_MONOMIALS or any(
        abs(c).bit_length() > MAX_COEFFICIENT_BITS for c in result.values()
    ):
        raise ValueError("polynomial resource limit exceeded")
    return result


def _add(a: Poly, b: Poly) -> Poly:
    result = dict(a)
    for k, c in b.items():
        result[k] = result.get(k, 0) + c
    return _clean(result)


def _mul(a: Poly, b: Poly) -> Poly:
    if len(a) * len(b) > MAX_MONOMIALS * 4:
        raise ValueError("polynomial intermediate resource limit exceeded")
    result: Poly = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            key = tuple(x + y for x, y in zip(ea, eb))
            result[key] = result.get(key, 0) + ca * cb
    return _clean(result)


def _neg(poly: Poly) -> Poly:
    return {k: -c for k, c in poly.items()}


def _parse_expr(expr: Any, variables: list[str], budget: list[int],
                depth: int = 0) -> Poly:
    budget[0] += 1
    if depth > MAX_AST_DEPTH or budget[0] > MAX_AST_NODES:
        raise ValueError("expression resource limit exceeded")
    if type(expr) is not dict or type(expr.get("op")) is not str:
        raise ValueError("expression must be a tagged object")
    op = expr["op"]
    zero = (0,) * len(variables)
    if op == "const":
        _keys(expr, {"op", "value"}, "constant")
        value = _int(expr["value"], "constant", -100, 100)
        return {zero: value} if value else {}
    if op == "var":
        _keys(expr, {"op", "name"}, "variable")
        if type(expr["name"]) is not str or expr["name"] not in variables:
            raise ValueError("undeclared variable")
        e = tuple(int(v == expr["name"]) for v in variables)
        return {e: 1}
    if op in ("add", "mul"):
        _keys(expr, {"op", "args"}, "n-ary expression")
        args = expr["args"]
        if type(args) is not list or not 2 <= len(args) <= 4:
            raise ValueError("invalid n-ary arity")
        value = {} if op == "add" else {zero: 1}
        for arg in args:
            child = _parse_expr(arg, variables, budget, depth + 1)
            value = _add(value, child) if op == "add" else _mul(value, child)
        return value
    if op == "sub":
        _keys(expr, {"op", "left", "right"}, "subtraction")
        a = _parse_expr(expr["left"], variables, budget, depth + 1)
        b = _parse_expr(expr["right"], variables, budget, depth + 1)
        return _add(a, _neg(b))
    if op == "neg":
        _keys(expr, {"op", "arg"}, "negation")
        return _neg(_parse_expr(expr["arg"], variables, budget, depth + 1))
    if op == "pow":
        _keys(expr, {"op", "base", "exponent"}, "power")
        exp = _int(expr["exponent"], "power", 0, 5)
        base = _parse_expr(expr["base"], variables, budget, depth + 1)
        result: Poly = {zero: 1}
        for _ in range(exp):
            result = _mul(result, base)
        return result
    raise ValueError("unsupported polynomial operation")


def _evaluate_expr(expr: dict, assignment: dict[str, int]) -> int:
    # Independent recursive evaluator to cross-check the symbolic expansion.
    op = expr["op"]
    if op == "const":
        return expr["value"]
    if op == "var":
        return assignment[expr["name"]]
    if op == "neg":
        return -_evaluate_expr(expr["arg"], assignment)
    if op == "sub":
        return (_evaluate_expr(expr["left"], assignment) -
                _evaluate_expr(expr["right"], assignment))
    if op == "pow":
        return _evaluate_expr(expr["base"], assignment) ** expr["exponent"]
    if op == "add":
        return sum(_evaluate_expr(e, assignment) for e in expr["args"])
    if op == "mul":
        result = 1
        for e in expr["args"]:
            result *= _evaluate_expr(e, assignment)
        return result
    raise ValueError("invalid expression")


def _evaluate_poly(poly: Poly, variables: list[str],
                   assignment: dict[str, int]) -> int:
    return sum(
        coefficient * product_of_powers(exponents, variables, assignment)
        for exponents, coefficient in poly.items()
    )


def product_of_powers(exponents: tuple[int, ...], variables: list[str],
                      assignment: dict[str, int]) -> int:
    value = 1
    for name, degree in zip(variables, exponents):
        value *= assignment[name] ** degree
    return value


def _lean_expr(expr: dict, assignment: dict[str, int] | None = None) -> str:
    op = expr["op"]
    if op == "const":
        return f"({expr['value']} : Int)"
    if op == "var":
        name = expr["name"]
        return f"({assignment[name]} : Int)" if assignment is not None else name
    if op == "neg":
        return f"(-{_lean_expr(expr['arg'], assignment)})"
    if op == "sub":
        return (f"({_lean_expr(expr['left'], assignment)} - "
                f"{_lean_expr(expr['right'], assignment)})")
    if op == "pow":
        return f"({_lean_expr(expr['base'], assignment)} ^ {expr['exponent']})"
    if op == "add":
        return "(" + " + ".join(
            _lean_expr(e, assignment) for e in expr["args"]) + ")"
    if op == "mul":
        return "(" + " * ".join(
            _lean_expr(e, assignment) for e in expr["args"]) + ")"
    raise ValueError("invalid expression")


def _lean_handoff(candidate: dict, witness: dict | None) -> str:
    left = candidate["left"]
    right = candidate["right"]
    label = candidate["candidate_id"].replace(".", "_").replace("-", "_")
    lines = [
        "import Init",
        "",
        "/-",
        "Generated from a restricted MathOS integer-polynomial AST.",
        "No model-written Lean code is executed. This cannot solve a Clay problem.",
        "The attached route, novelty and proof implications are NOT validated.",
        "-/",
        "",
    ]
    if witness is not None:
        lhs = _lean_expr(left, witness["assignment"])
        rhs = _lean_expr(right, witness["assignment"])
        lines.extend([
            "-- Concrete falsification of the claimed universal equality.",
            "-- This proves only the explicit integer witness if Lean accepts it.",
            f"theorem mathos_witness_{label} : {lhs} ≠ {rhs} := by",
            "  decide",
        ])
    else:
        vars_decl = " ".join(candidate["variables"])
        lines.extend([
            "-- STATEMENT ONLY: no theorem has been submitted to Lean.",
            "-- The following proposed statement has no proof term.",
            "-- A Python-normalized identity is not an independently checked proof.",
            f"-- theorem mathos_candidate_{label} ({vars_decl} : Int) :",
            f"--   {_lean_expr(left)} = {_lean_expr(right)} := by",
            "--   -- Independent formal proof required.",
        ])
    return "\n".join(lines) + "\n"


def _canonical_json(data: Any) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def _formal_replay(filename: Path) -> dict:
    lean = shutil.which("lean")
    if lean is None:
        raise RuntimeError("Lean unavailable: --verify-lean requires pinned Lean 4.14.0")
    version = subprocess.run([lean, "--version"], capture_output=True, text=True,
                             timeout=15, check=False)
    if version.returncode or not version.stdout.startswith("Lean (version 4.14.0"):
        raise RuntimeError("only pinned Lean 4.14.0 is permitted")
    result = subprocess.run([lean, str(filename)], capture_output=True,
                            text=True, timeout=90, check=False)
    if result.returncode:
        raise RuntimeError("Lean failed to check the generated counterexample witness")
    return {"status": "LEAN_KERNEL_CHECKED_CONCRETE_COUNTEREXAMPLE",
            "lean_version": version.stdout.strip().splitlines()[0],
            "source_sha256": hashlib.sha256(filename.read_bytes()).hexdigest()}


def verify_lemmas(
    manifest_path: Path = MANIFEST_PATH, *,
    output_dir: Path,
    agent_report_path: Path | None = None,
    verify_lean: bool = False,
    routes_path: Path = ROUTES_PATH,
    targets_path: Path = TARGETS_PATH,
    register_path: Path = OBLIGATIONS,
    hypotheses_path: Path = HYPOTHESES,
    external_path: Path = EXTERNAL_PATH,
) -> dict:
    source_paths = {
        "manifest": manifest_path, "routes": routes_path,
        "clay_targets": targets_path, "obligations": register_path,
        "hypotheses": hypotheses_path, "external": external_path,
    }
    if agent_report_path is not None:
        source_paths["agent_report"] = agent_report_path
    original = {name: path.read_bytes() for name, path in source_paths.items()}
    topology = audit_clay_proof_topology(
        routes_path=routes_path, targets_path=targets_path,
        register_path=register_path, hypotheses_path=hypotheses_path,
        external_path=external_path,
    )
    spec = json.loads(original["manifest"])
    _keys(spec, {"schema_version", "policy", "candidates"}, "manifest")
    if spec["schema_version"] != "1.0.0" or spec["policy"] != POLICY:
        raise ValueError("lemma manifest claims unsupported proof or policy status")
    candidates = spec["candidates"]
    if type(candidates) is not list or not 1 <= len(candidates) <= MAX_CANDIDATES:
        raise ValueError("invalid number of lemma candidates")
    route_map = {
        (t["model_key"], r["route_id"]): r
        for t in topology["targets"] for r in t["candidate_routes"]
    }
    agent_packets: dict[tuple[str, str, str], dict] = {}
    if agent_report_path is not None:
        agent = json.loads(original["agent_report"])
        if (agent.get("certification") != "NOT_CERTIFIED" or
            agent.get("proof_promotion") != "NONE" or
            agent.get("automatic_merge_or_claim_promotion") is not False or
            agent.get("proof_topology_route_sufficiency") != "NOT_VALIDATED"):
            raise ValueError("agent report is not an unverified research handoff")
        hashes = agent.get("source_sha256", {})
        if not isinstance(hashes, dict) or any(
            hashes.get(key) != hashlib.sha256(original[key]).hexdigest()
            for key in ("routes", "clay_targets", "obligations", "hypotheses", "external")
        ):
            raise ValueError("agent evidence does not match registered source bytes")
        for packet in agent.get("packets", []):
            if (packet.get("certification") != "NOT_CERTIFIED" or
                packet.get("proof_completed") is not False or
                packet.get("promoted_to_solution") is not False or
                packet.get("route_sufficiency_validated") is not False or
                packet.get("independent_mathematical_review") is not False):
                raise ValueError("agent packet asserts unearned proof or review")
            focus = packet.get("research_focus", {})
            key = (packet.get("model_key"), focus.get("route_id"),
                   packet.get("traceable_claim_id"))
            if key in agent_packets:
                raise ValueError("duplicate agent research focus")
            agent_packets[key] = packet

    ids: set[str] = set()
    lean_filenames: set[str] = set()
    outputs = []
    payloads: list[tuple[str, str]] = []
    for candidate in candidates:
        _keys(candidate, {"candidate_id", "model_key", "route_id", "claim_id",
                          "statement", "scope_note", "variables", "left", "right",
                          "search"}, "candidate")
        cid = candidate["candidate_id"]
        if (type(cid) is not str or not CANDIDATE_ID.fullmatch(cid)
                or cid in ids):
            raise ValueError("unsafe or duplicate candidate ID")
        ids.add(cid)
        key = (candidate["model_key"], candidate["route_id"])
        route = route_map.get(key)
        if route is None or candidate["claim_id"] not in route["obligations"]:
            raise ValueError("candidate is not attached to an open registered route claim")
        _text(candidate["statement"], f"{cid}.statement", minimum=20)
        _text(candidate["scope_note"], f"{cid}.scope_note", minimum=40)
        variables = candidate["variables"]
        if (type(variables) is not list or not 1 <= len(variables) <= MAX_VARIABLES
            or any(type(v) is not str or not IDENTIFIER.fullmatch(v)
                   or v in {"Int", "theorem", "by", "import", "where"}
                   for v in variables) or len(set(variables)) != len(variables)):
            raise ValueError("invalid bounded polynomial variables")
        search = _keys(candidate["search"], {"min", "max"}, "search")
        low = _int(search["min"], "minimum", -4, 4)
        high = _int(search["max"], "maximum", -4, 4)
        if low > high or (high - low + 1) ** len(variables) > MAX_TEST_POINTS:
            raise ValueError("finite search exceeds allowed evaluation budget")
        budget = [0]
        lhs = _parse_expr(candidate["left"], variables, budget)
        rhs = _parse_expr(candidate["right"], variables, budget)
        difference = _add(lhs, _neg(rhs))
        witness = None
        count = 0
        for tuple_values in product(range(low, high + 1), repeat=len(variables)):
            assignment = dict(zip(variables, tuple_values))
            lv = _evaluate_expr(candidate["left"], assignment)
            rv = _evaluate_expr(candidate["right"], assignment)
            if lv != _evaluate_poly(lhs, variables, assignment):
                raise RuntimeError("symbolic LHS normalization disagrees with direct evaluation")
            if rv != _evaluate_poly(rhs, variables, assignment):
                raise RuntimeError("symbolic RHS normalization disagrees with direct evaluation")
            count += 1
            if lv != rv:
                witness = {"assignment": assignment, "left_value": str(lv),
                           "right_value": str(rv)}
                break

        if witness is not None:
            status = "CONCRETE_COUNTEREXAMPLE_FOUND"
        elif not difference:
            status = "EXACT_POLYNOMIAL_IDENTITY_BY_PYTHON_NORMALIZATION"
        else:
            status = "FINITE_SEARCH_INCONCLUSIVE"
        filename = cid.replace(".", "_").replace("-", "_") + ".lean"
        if filename in lean_filenames:
            raise ValueError("duplicate generated Lean filename")
        lean_filenames.add(filename)
        generated = _lean_handoff(candidate, witness)
        payloads.append((filename, generated))
        packet_key = (candidate["model_key"], candidate["route_id"],
                      candidate["claim_id"])
        if agent_report_path is not None and packet_key not in agent_packets:
            raise ValueError("candidate does not match any recorded agent research focus")
        outputs.append({
            "candidate_id": cid,
            "model_key": candidate["model_key"],
            "route_id": candidate["route_id"],
            "claim_id": candidate["claim_id"],
            "candidate_sha256": hashlib.sha256(_canonical_json(candidate)).hexdigest(),
            "status": status,
            "verification_domain": "INTEGER_POLYNOMIAL_EQUALITY_ONLY",
            "symbolic_difference": [
                {"exponents": list(exp), "coefficient": str(coeff)}
                for exp, coeff in sorted(difference.items())
            ],
            "evaluations": count,
            "search_domain": {"min": low, "max": high,
                              "variable_count": len(variables)},
            "witness": witness,
            "lean_handoff_file": "lean/" + filename,
            "lean_handoff_sha256": hashlib.sha256(generated.encode()).hexdigest(),
            "lean_certificate": "NOT_RUN",
            "lean_check": None,
            "agent_report_linked_by_digest": agent_report_path is not None,
            "novelty_verified": False,
            "complete_proof_of_registered_claim": False,
            "clay_problem_solved": False,
            "research_claim_promoted": False,
        })
    # Materialize only after every candidate, ledger and agent-link check passes.
    output_dir.mkdir(parents=True, exist_ok=True)
    lean_dir = output_dir / "lean"
    lean_dir.mkdir(parents=True, exist_ok=True)
    for filename, generated in payloads:
        (lean_dir / filename).write_text(generated, encoding="utf-8")
    if verify_lean:
        for result in outputs:
            if result["witness"] is not None:
                proof_path = output_dir / result["lean_handoff_file"]
                result["lean_check"] = _formal_replay(proof_path)
                result["lean_certificate"] = "CONCRETE_COUNTEREXAMPLE_ONLY"
    report = {
        "schema_version": "1.0.0",
        "certification": "NOT_CERTIFIED",
        "clay_prize_readiness": "NOT_ELIGIBLE",
        "proof_route_sufficiency": "NOT_VALIDATED",
        "mathematical_scope": POLICY["mathematical_scope"],
        "formal_proof_of_clay_target": False,
        "agent_report_linked": agent_report_path is not None,
        "source_sha256": {name: hashlib.sha256(blob).hexdigest()
                          for name, blob in original.items()},
        "results": outputs,
        "limitations": [
            "All integer polynomial ASTs are bounded toy subclaims, not Clay solutions.",
            "Exact symbolic normalization in Python is not Lean kernel proof.",
            "A compiled Lean witness only disproves that precise universal equality.",
            "Finite search without a witness never establishes universal truth.",
            "The attached registered research route is not mathematically validated.",
        ],
    }
    for name, path in source_paths.items():
        if path.read_bytes() != original[name]:
            raise RuntimeError("registered mathematical evidence changed during verification")
    (output_dir / "lemma_verification_report.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/lemmas"))
    parser.add_argument("--agent-report", type=Path, default=None)
    parser.add_argument("--verify-lean", action="store_true")
    args = parser.parse_args(argv)
    report = verify_lemmas(
        args.manifest, output_dir=args.output_dir,
        agent_report_path=args.agent_report, verify_lean=args.verify_lean)
    print(json.dumps({"candidates": len(report["results"]),
                      "counterexamples": sum(
                          r["status"] == "CONCRETE_COUNTEREXAMPLE_FOUND"
                          for r in report["results"]),
                      "certification": report["certification"],
                      "output_dir": str(args.output_dir)}, sort_keys=True))


if __name__ == "__main__":
    main()
