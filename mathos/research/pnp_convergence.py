"""Bidirectional convergence: scoped upper/lower evidence and shared obligations."""
import argparse
from itertools import combinations
import json
from pathlib import Path

from .pnp_structural_kernel import Budget, Exhausted, brute, normalize, primal, two_sat
from .pnp_dual_bounds import converge, verify_bounds, EXACT_LIMIT
from .pnp_transformation_agent import unit_transform, verify_transform
from .pnp_outcome_registry import decompose
from .pnp_outcome_engine import checkpoint


SHARED_LEMMAS = (
    {"id": "S01", "statement": "Induced elimination width upper-bounds treewidth",
     "status": "established_mathematical_background", "scope": "finite graphs"},
    {"id": "S02", "statement": "Treewidth is at least induced subgraph minimum degree and clique minor order minus one",
     "status": "established_mathematical_background", "scope": "finite graphs"},
    {"id": "S03", "statement": "Equal certified bounds determine exact treewidth",
     "status": "established_mathematical_background", "scope": "same graph and convention"},
    {"id": "S04", "statement": "Unit propagation preserves satisfiability under projection",
     "status": "established_mathematical_background", "scope": "signed CNF, valid unit trace"},
    {"id": "S05", "statement": "A uniform polynomial-time SAT-preserving reduction to certified logarithmic width would imply P = NP",
     "status": "established_implication_only", "scope": "universal reduction with polynomial output and certificate construction"},
    {"id": "S06", "statement": "Such an unrestricted universal reduction exists iff P = NP",
     "status": "established_equivalence_only", "scope": "decision reduction; converse may output constant yes/no instances"},
    {"id": "S07", "statement": "An algorithm-independent superpolynomial SAT lower bound",
     "status": "unresolved", "scope": "all deterministic SAT decision algorithms"},
)

BARRIERS = [
    {"name": "relativization", "status": "not_assessed", "question": "Does the proposed proof relativize?"},
    {"name": "natural proofs", "status": "not_assessed", "question": "Does the circuit lower-bound method satisfy the naturalness hypotheses under the relevant cryptographic assumption?"},
    {"name": "algebrization", "status": "not_assessed", "question": "Does the proposed technique algebrize?"},
]


def adversarial_arena(budget):
    """One shared high-width graph, two opposite SAT decisions."""
    f = tuple(combinations(range(1, 9), 2))
    h = f + ((-1,), (-2,))
    g, other = primal(8, f, budget), primal(8, h, budget)
    if g != other:
        raise AssertionError("primal graphs differ")
    result = converge(g, budget)
    if not result["exact"] or result["lower"] != 7:
        raise Exhausted("arena exact bound not certified")
    verify_bounds(g, result, budget)
    decisions = [two_sat(8, q, budget) for q in (f, h)]
    references = [brute(8, q, budget) for q in (f, h)]
    if decisions != [True, False] or references != decisions:
        raise AssertionError("arena decision replay failed")
    return {"same_primal_graph": True, "bounds": result, "sat": decisions,
            "brute_crosscheck": references, "both_two_cnf": True,
            "claim_refuted": "unsigned primal graph alone determines satisfiability",
            "scope": "finite counterexample; high treewidth alone is not general SAT hardness"}


def _measure(n, f, c, budget, exact_limit):
    graph = primal(n, f, budget)
    report = converge(graph, budget, exact_limit=exact_limit)
    size = max(2, n + len(f) + sum(map(len, f)))
    threshold = (size ** c).bit_length() - 1
    lo, hi = report["lower"], report["upper"]
    report["N"], report["threshold"] = size, threshold
    report["width_classification"] = (
        "certified_width_condition" if hi is not None and hi <= threshold else
        "no_order_meets_threshold_on_this_graph" if lo > threshold else "undetermined")
    return report


def research(n, clauses, budget, *, c=1, exact_limit=EXACT_LIMIT, arena=False,
             checkpoint_path=None):
    if type(c) is not int or not 1 <= c <= 16:
        raise ValueError("fixed c must be an integer in 1..16")
    if type(exact_limit) is not int or not 0 <= exact_limit <= EXACT_LIMIT:
        raise ValueError("invalid exact limit")
    record = {"schema": "mathos-pnp-convergence/1", "plans": [decompose("E01"), decompose("E02")],
              "shared_question": "Does a universal efficient SAT-preserving transformation to certified logarithmic width exist?",
              "shared_lemmas": SHARED_LEMMAS, "proof_barriers": BARRIERS,
              "p_equals_np_established": False, "p_not_equals_np_established": False,
              "universal_obligation": "unresolved", "formal_verification": "not_performed",
              "completion": "documented_unresolved_obligations", "evidence": {}}
    try:
        nn, f, mapping = normalize(n, clauses)
        record["restart"] = {"n": n, "clauses": clauses, "c": c, "exact_limit": exact_limit, "arena": arena}
        if checkpoint_path:
            checkpoint(checkpoint_path, record)
        evidence = record["evidence"]
        evidence["normalized_mapping"] = mapping
        evidence["original_graph_bounds"] = _measure(nn, f, c, budget, exact_limit)
        if checkpoint_path:
            checkpoint(checkpoint_path, record)
        artifact = unit_transform(nn, f, budget)
        verify_transform(nn, f, artifact, budget)
        evidence["constructive_transform"] = {"certificate_replayed": True, **artifact,
                                               "scope": "unit propagation only, labels relative to normalized input"}
        evidence["transformed_graph_bounds"] = _measure(
            artifact["n"], artifact["clauses"], c, budget, exact_limit)
        if nn <= 10:
            before = brute(nn, f, budget)
            after = brute(artifact["n"], artifact["clauses"], budget)
            if before != after:
                raise AssertionError("transformation SAT cross-check failed")
            evidence["transform_sat_crosscheck"] = {"before": before, "after": after}
        if arena:
            evidence["adversarial_arena"] = adversarial_arena(budget)
        bounds = [evidence[key] for key in ("original_graph_bounds", "transformed_graph_bounds")]
        if any(b["stop_reason"] not in (None, "exact search vertex limit") for b in bounds):
            record["completion"] = "resource_exhausted"
        elif all(b["exact"] for b in bounds):
            record["completion"] = "scoped_structural_convergence"
        record["next_step"] = (
            "Seek transformations escaping graph-specific obstructions; neither exact treewidth "
            "nor a restricted obstruction discharges the universal obligation.")
    except Exhausted as exc:
        record["completion"], record["reason"] = "resource_exhausted", str(exc)
    except (AssertionError, ValueError) as exc:
        if "restart" not in record:
            raise
        record["completion"], record["reason"] = "diagnostic_required", str(exc)
    record["work_steps"] = budget.steps
    if checkpoint_path:
        checkpoint(checkpoint_path, record)
    return record


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, help="JSON object with n and clauses")
    p.add_argument("--resume", type=Path)
    p.add_argument("--checkpoint", type=Path)
    p.add_argument("--arena", action="store_true")
    p.add_argument("--c", type=int, default=1)
    p.add_argument("--exact-limit", type=int, default=EXACT_LIMIT)
    p.add_argument("--seconds", type=float, default=15)
    p.add_argument("--max-steps", type=int, default=4_000_000)
    p.add_argument("--max-cells", type=int, default=100_000)
    a = p.parse_args(argv)
    if a.input and a.resume:
        p.error("choose --input or --resume")

    def read(path):
        if path.stat().st_size > 2_000_000:
            raise ValueError("JSON input exceeds 2 MB")
        return json.loads(path.read_text(encoding="utf-8"))

    try:
        raw = read(a.resume)["restart"] if a.resume else (
            read(a.input) if a.input else {"n": 4, "clauses": [[1], [-1, 2, 3], [-2, 4], [-3, 4]]})
        options = {k: raw[k] for k in ("c", "exact_limit", "arena")} if a.resume else {
            "c": a.c, "exact_limit": a.exact_limit, "arena": a.arena}
        r = research(raw["n"], raw["clauses"], Budget(a.seconds, a.max_steps, a.max_cells),
                     checkpoint_path=a.checkpoint, **options)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.error(str(exc))
    print(json.dumps(r, indent=2, sort_keys=True))
    return int(r["completion"] == "diagnostic_required")


if __name__ == "__main__":
    raise SystemExit(main())
