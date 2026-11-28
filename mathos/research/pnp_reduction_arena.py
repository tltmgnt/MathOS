"""Outcome-driven, deterministic hypothesis arena for restricted reductions."""
import argparse
import json
from itertools import combinations
from pathlib import Path

from .pnp_structural_kernel import Budget, Exhausted, brute, normalize, primal, truth
from .pnp_dual_bounds import converge
from .pnp_outcome_engine import checkpoint
from .pnp_outcome_registry import decompose
from .pnp_reduction_portfolio import PROFILES, reduce_cnf, verify_reduction
from .pnp_semantic_escape import propose, verify


def measure(n, f, c, budget):
    graph = primal(n, f, budget)
    bounds = converge(graph, budget)
    if bounds["stop_reason"] not in (None, "exact search vertex limit"):
        raise Exhausted(bounds["stop_reason"])
    size = max(2, n + len(f) + sum(map(len, f)))
    threshold = (size ** c).bit_length() - 1
    return {**bounds, "N": size, "threshold": threshold,
            "width_condition": bounds["upper"] <= threshold,
            "obstructed_current_graph": bounds["lower"] > threshold}


def family(n, satisfiable):
    """Complete unsigned primal graph, equal-length clauses, both polarities.

    Mixed-sign triples are all satisfied by the all-true assignment. The
    monochromatic positive/negative triples are unsatisfiable for n >= 5.
    """
    if type(n) is not int or not 5 <= n <= 24:
        raise ValueError("family size must be 5..24")
    f = []
    for triple in combinations(range(1, n+1), 3):
        if satisfiable:
            for v in triple:
                f.append(tuple(-x if x == v else x for x in triple))
                f.append(tuple(x if x == v else -x for x in triple))
        else:
            f.extend((triple, tuple(-x for x in triple)))
    return f


def family_evidence(n, cap, c, budget):
    reports = []
    for expected in (True, False):
        f = family(n, expected)
        nn, normalized, _ = normalize(n, f)
        a = reduce_cnf(n, f, budget, cap=cap)
        verify_reduction(n, f, a, budget)
        # Independently check the decision: SAT witness, or UNSAT subformula
        # over five variables with all 32 assignments checked.
        if expected:
            if not truth(normalized, (True,) * n):
                raise AssertionError("family witness rejected")
            decision = {"sat": True, "witness": [True] * n}
        else:
            core = tuple(tuple(sorted(q)) for q in family(5, False))
            if not set(core) <= set(normalized) or brute(5, core, budget):
                raise AssertionError("family UNSAT core rejected")
            decision = {"sat": False, "unsat_core": core, "assignments_checked": 32}
        # Explicitly verify structural premises for the restricted obstruction.
        g = primal(nn, normalized, budget)
        occ = {x for clause in normalized for x in clause}
        signs_balanced = all(v in occ and -v in occ for v in g)
        equal_triples = all(len(q) == 3 for q in normalized)
        complete = nn == n and all(len(ns) == n-1 for ns in g.values())
        blocked = complete and signs_balanced and equal_triples and n-1 > cap
        unchanged = not a["steps"] and a["n"] == n and a["clauses"] == normalized
        if blocked and not unchanged:
            raise AssertionError("restricted obstruction violated")
        escape = propose(nn, normalized, budget)
        if escape is None or not verify(nn, normalized, escape, budget):
            raise AssertionError("semantic escape failed")
        escape_bounds = measure(escape["n"], escape["clauses"], c, budget)
        reports.append({"decision": decision, "artifact": a,
                        "semantic_escape": {"artifact": escape, "certificate_replayed": True,
                                            "bounds": escape_bounds},
                        "certificate_replayed": True, "bounds": measure(nn, normalized, c, budget),
                        "premises": {"complete_primal": complete, "both_polarities": signs_balanced,
                                     "distinct_equal_length_triples": equal_triples,
                                     "neighbor_cap_blocks_every_variable": n-1 > cap},
                        "all_rules_blocked": blocked, "unchanged": unchanged})
    return reports


def research(n, clauses, budget, *, c=1, cap=4, family_size=16, checkpoint_path=None):
    if type(c) is not int or not 1 <= c <= 16:
        raise ValueError("fixed c must be 1..16")
    if type(cap) is not int or not 0 <= cap <= 12:
        raise ValueError("neighbor cap must be 0..12")
    if type(family_size) is not int or not 5 <= family_size <= 24:
        raise ValueError("family size must be 5..24")
    r = {"schema": "mathos-pnp-reduction-arena/1", "plans": [decompose("E01"), decompose("E02")],
         "universal_obligation": "unresolved", "p_equals_np_established": False,
         "p_not_equals_np_established": False, "formal_verification": "not_performed",
         "completion": "documented_unresolved_obligations", "c": c, "neighbor_cap": cap,
         "portfolio": [], "hypotheses": []}
    try:
        nn, f, mapping = normalize(n, clauses)
        r["restart"] = {"n": n, "clauses": clauses, "c": c, "cap": cap, "family_size": family_size}
        if checkpoint_path:
            checkpoint(checkpoint_path, r)
        r["baseline"] = measure(nn, f, c, budget)
        reference = brute(nn, f, budget) if nn <= 10 else None
        for profile in PROFILES:
            a = reduce_cnf(n, clauses, budget, profile=profile, cap=cap)
            verify_reduction(n, clauses, a, budget)
            cross = None
            if reference is not None:
                cross = brute(a["n"], a["clauses"], budget)
                if cross != reference:
                    raise AssertionError("SAT decision mismatch")
            b = measure(a["n"], a["clauses"], c, budget)
            r["portfolio"].append({"profile": profile, "artifact": a, "bounds": b,
                                   "certificate_replayed": True, "independent_sat_crosscheck": cross,
                                   "active_variables_removed": nn-a["n"]})
            if checkpoint_path:
                checkpoint(checkpoint_path, r)
        # Rank by certified width condition, then certified upper bound,
        # then output size. This is a heuristic, not a runtime comparison.
        best = min(r["portfolio"], key=lambda p: (
            not p["bounds"]["width_condition"], p["bounds"]["upper"], p["bounds"]["N"], p["profile"]))
        r["selected_profile"] = best["profile"]
        controls = family_evidence(family_size, cap, c, budget)
        r["adversarial_family"] = controls
        escape = propose(nn, f, budget)
        if escape is not None:
            verify(nn, f, escape, budget)
            r["semantic_escape"] = {"artifact": escape, "certificate_replayed": True,
                                    "bounds": measure(escape["n"], escape["clauses"], c, budget)}
        blocked = all(x["all_rules_blocked"] and x["unchanged"] for x in controls)
        width_failure = any(x["all_rules_blocked"] and x["unchanged"] and
                            x["bounds"]["obstructed_current_graph"] for x in controls)
        r["hypotheses"] = [
            {"id": "H01", "claim": "The configured preprocessing portfolio reduces active variables on every nonempty active CNF",
             "status": "refuted_by_replayed_instance" if blocked else "not_refuted_in_this_run",
             "scope": "configured rules and cap only"},
            {"id": "H02", "claim": "The configured preprocessing portfolio always produces a graph meeting the fixed logarithmic-width condition",
             "status": "refuted_by_replayed_instance" if width_failure else "not_refuted_in_this_run",
             "scope": "configured rules, cap and fixed c only"}]
        r["completion"] = "scoped_research_cycle_completed"
        r["next_obligation"] = ("Generalize the certified semantic escape beyond constant witnesses and bounded cores; "
                                "bound its output size and runtime over a family, not just a finite sample.")
    except Exhausted as exc:
        r["completion"], r["reason"] = "resource_exhausted", str(exc)
    except AssertionError as exc:
        r["completion"], r["reason"] = "diagnostic_required", str(exc)
    r["work_steps"] = budget.steps
    if checkpoint_path:
        checkpoint(checkpoint_path, r)
    return r


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path)
    p.add_argument("--resume", type=Path)
    p.add_argument("--checkpoint", type=Path)
    p.add_argument("--c", type=int, default=1)
    p.add_argument("--cap", type=int, default=4)
    p.add_argument("--family-size", type=int, default=16)
    p.add_argument("--seconds", type=float, default=20)
    p.add_argument("--max-steps", type=int, default=10_000_000)
    p.add_argument("--max-cells", type=int, default=100_000)
    a = p.parse_args(argv)
    if a.input and a.resume:
        p.error("choose --input or --resume")

    def read(path):
        if path.stat().st_size > 2_000_000:
            raise ValueError("input exceeds 2 MB")
        return json.loads(path.read_text(encoding="utf-8"))

    try:
        raw = read(a.resume)["restart"] if a.resume else (
            read(a.input) if a.input else {"n": 4, "clauses": [[1, 2, 3], [-1, -2, 4], [-3, -4]]})
        opts = {k: raw[k] for k in ("c", "cap", "family_size")} if a.resume else {
            "c": a.c, "cap": a.cap, "family_size": a.family_size}
        result = research(raw["n"], raw["clauses"], Budget(a.seconds, a.max_steps, a.max_cells),
                          checkpoint_path=a.checkpoint, **opts)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        p.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(result["completion"] == "diagnostic_required")


if __name__ == "__main__":
    raise SystemExit(main())
