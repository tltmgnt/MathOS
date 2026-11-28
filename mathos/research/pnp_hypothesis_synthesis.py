"""Bounded counterexample-guided synthesis of certificate-producing SAT routes.

This synthesizes a finite route-selection program, not a new SAT algorithm
or a mathematical theorem. Every success requires independent replay.
"""
import argparse
from itertools import combinations
import json
from pathlib import Path
import random

from .pnp_certificate_routes import ROUTES, propose, verify, execute
from .pnp_outcome_engine import checkpoint
from .pnp_outcome_registry import decompose
from .pnp_reduction_arena import family
from .pnp_structural_kernel import Budget, Exhausted, brute, normalize

ROUTE_SCOPE = {
    "constant": "all-true or all-false witness",
    "two_sat": "2-CNF; SCC assignment or opposing implication paths",
    "horn": "Horn CNF; least model or forced-unit contradiction",
    "renamable_horn": "a sign renaming found by 2-SAT produces Horn CNF",
    "bounded_core": "a contradictory subformula on at most five variables; exhaustive support search only for n <= 12, plus v4 fixed-core fast path",
}


def _flip(f, variables):
    return [tuple(-x if abs(x) in variables else x for x in c) for c in f]


def controls():
    chain = []
    for i in range(1, 6):
        chain.extend(((-i, i+1), (i, -(i+1))))
    chain.extend(((1, 6), (-1, -6)))
    # An odd parity cycle requires all six variables for its contradiction.
    # Its binary clauses are not renamable Horn, since their renaming
    # constraints are the original unsatisfiable binary clauses.
    renamed = [[1], [-2], [-1, 3, 4], [-4, -3]]
    return [
        ("constant_seed", 5, family(5, True)),
        ("binary_cycle", 6, chain),
        ("renamed_horn", 4, renamed),
        ("shifted_core", 7, [(1,), (-2,)] +
         [tuple(x+2 if x > 0 else x-2 for x in c) for c in family(5, False)]),
        ("grammar_gap", 5, _flip(family(5, True), {1})),
    ]


def _random_cases(seed, count, prefix):
    rng = random.Random(seed)
    for i in range(count):
        n = rng.randint(3, 7)
        literals = [x for x in range(-n, n+1) if x]
        f = [tuple(rng.choices(literals, k=rng.randint(1, 4)))
             for _ in range(rng.randint(4, 15))]
        yield f"{prefix}_{i:02d}", n, f


def _key(n, f):
    nn, nf, _ = normalize(n, f)
    return nn, nf


def evaluate(name, n, clauses, budget):
    nn, f, _ = normalize(n, clauses)
    if nn > 8:
        raise ValueError("synthesis controls must have at most eight active variables")
    expected = brute(nn, f, budget)
    certificates = {}
    for route in ROUTES:
        candidate = propose(nn, f, route, budget)
        if candidate is None:
            continue
        try:
            verify(nn, f, candidate, budget)
        except ValueError as exc:
            raise AssertionError(f"route {route} produced an invalid certificate") from exc
        if (candidate["kind"] == "sat_witness") != expected:
            raise AssertionError(f"route {route} disagrees with brute-force decision")
        certificates[route] = candidate
    return {"name": name, "n": nn, "clauses": f, "sat_reference": expected,
            "covered_routes": [r for r in ROUTES if r in certificates],
            "certificates": certificates}


def covered(program, case):
    return any(r in case["covered_routes"] for r in program)


def select_program(examples, budget):
    """Exact minimum cardinality in the fixed finite route grammar."""
    for size in range(len(ROUTES)+1):
        for program in combinations(ROUTES, size):
            budget.tick(1 + len(examples))
            if all(covered(program, e) for e in examples):
                return program
    raise AssertionError("training examples are not coverable by the grammar")


def minimize(case, program, budget, *, grammar_gap=False, max_trials=64):
    """Greedy deletion minimization; report whether a full final pass finished.

    Preserve the independent SAT decision and the relevant coverage failure.
    For a refinement counterexample, also preserve coverage by some route.
    """
    if type(max_trials) is not int or not 0 <= max_trials <= 256:
        raise ValueError("max_trials must be in 0..256")
    current = case
    def predicate(e):
        return (not covered(program, e) and
                (not e["covered_routes"] if grammar_gap else bool(e["covered_routes"])) and
                e["sat_reference"] == case["sat_reference"])
    if not predicate(case):
        raise ValueError("not a counterexample to the requested scope")
    i = trials = 0
    while i < len(current["clauses"]) and trials < max_trials:
        trial = current["clauses"][:i] + current["clauses"][i+1:]
        trials += 1
        nn, f, _ = normalize(current["n"], trial)
        if brute(nn, f, budget) != case["sat_reference"]:
            i += 1
            continue
        candidate = evaluate(case["name"], nn, f, budget)
        if predicate(candidate):
            current = candidate
            i = 0
        else:
            i += 1
    return {"original_clause_count": len(case["clauses"]),
            "remaining_clause_count": len(current["clauses"]),
            "trials": trials, "deletion_minimal": i == len(current["clauses"]),
            "case": current,
            "scope": "preserved SAT reference and observed fixed-grammar coverage predicate"}


def _summary(case, program):
    return {"name": case["name"], "n": case["n"], "clauses": case["clauses"],
            "sat_reference": case["sat_reference"], "covered_routes": case["covered_routes"],
            "program_covered": covered(program, case),
            "grammar_covered": bool(case["covered_routes"]),
            "certificates": case["certificates"]}


def synthesize(budget, *, seed=5205, random_cases=12, target=None,
               checkpoint_path=None):
    if type(seed) is not int or not 0 <= seed <= 2**31-1:
        raise ValueError("seed out of range")
    if type(random_cases) is not int or not 0 <= random_cases <= 32:
        raise ValueError("random_cases must be in 0..32")
    if target is not None:
        normalize(target["n"], target["clauses"])
    record = {
        "schema": "mathos-pnp-hypothesis-synthesis/1",
        "plans": [decompose("E01"), decompose("E02")],
        "grammar": ROUTE_SCOPE, "program": [], "refinements": [], "training": [],
        "challenge": [], "heldout": [], "unresolved_examples": [],
        "completion": "documented_unresolved_obligations",
        "universal_obligation": "unresolved", "p_equals_np_established": False,
        "p_not_equals_np_established": False, "novel_theorem_verified": False,
        "formal_verification": "not_performed",
        "restart": {"seed": seed, "random_cases": random_cases, "target": target},
    }

    def save():
        if checkpoint_path is not None:
            checkpoint(checkpoint_path, record)

    try:
        save()
        entries = controls()
        initial = evaluate(*entries[0], budget)
        training = [initial]
        record["training"] = training
        program = select_program(training, budget)
        record["program"] = program
        save()
        # The adversary is a finite deterministic suite. A failed probe is
        # not a proof of absence beyond this explicit grammar.
        candidates = []
        keys = {_key(initial["n"], initial["clauses"])}
        for name, n, f in entries[1:] + list(_random_cases(seed, random_cases, "challenge")):
            key = _key(n, f)
            if key in keys:
                continue
            keys.add(key)
            candidates.append(evaluate(name, n, f, budget))
        for _ in range(1 << len(ROUTES)):
            bad = next((e for e in candidates if e["covered_routes"] and not covered(program, e)), None)
            if bad is None:
                break
            minimized = minimize(bad, program, budget)
            training.append(minimized["case"])
            previous = program
            program = select_program(training, budget)
            if previous == program:
                raise AssertionError("refinement did not exclude failing program")
            record["refinements"].append({"previous_program": previous,
                "counterexample": bad, "minimized": minimized, "new_program": program})
            record["program"] = program
            save()
        else:
            raise AssertionError("finite synthesis search did not terminate")
        record["challenge"] = [_summary(e, program) for e in candidates]
        record["training"] = training
        keys.update(_key(e["n"], e["clauses"]) for e in training)
        # Separate holdout seed and sign variants; never added to training.
        holdout_entries = [
            ("holdout_renamed", 4, _flip(entries[2][2], {4})),
            ("holdout_gap", 5, _flip(family(5, True), {2, 4})),
        ] + list(_random_cases(seed ^ 0x5A17, random_cases, "heldout"))
        for name, n, f in holdout_entries:
            key = _key(n, f)
            if key in keys:
                continue
            keys.add(key)
            e = evaluate(name, n, f, budget)
            record["heldout"].append(_summary(e, program))
        for e in candidates:
            if not e["covered_routes"]:
                record["unresolved_examples"].append(
                    minimize(e, ROUTES, budget, grammar_gap=True))
                if len(record["unresolved_examples"]) == 2:
                    break
        if target is not None:
            try:
                proof = execute(target["n"], target["clauses"], program, budget)
            except ValueError as exc:
                raise AssertionError("selected program certificate rejected") from exc
            record["target_result"] = {"certificate": proof,
                "status": "certificate_replayed" if proof is not None else "unrecognized"}
        record["statistics"] = {
            "program_size": len(program),
            "grammar_size": len(ROUTES),
            "refinements": len(record["refinements"]),
            "challenge_cases": len(candidates),
            "challenge_program_covered": sum(covered(program, e) for e in candidates),
            "challenge_grammar_covered": sum(bool(e["covered_routes"]) for e in candidates),
            "heldout_cases": len(record["heldout"]),
            "heldout_program_covered": sum(e["program_covered"] for e in record["heldout"]),
            "heldout_grammar_covered": sum(e["grammar_covered"] for e in record["heldout"]),
        }
        record["completion"] = "finite_synthesis_cycle_completed"
        record["next_obligation"] = (
            "Extend the route grammar or construct a new proof technique for "
            "the replayed grammar gaps; finite coverage is not a universal theorem.")
    except Exhausted as exc:
        record["completion"], record["reason"] = "resource_exhausted", str(exc)
    except AssertionError as exc:
        record["completion"], record["reason"] = "diagnostic_required", str(exc)
    record["work_steps"] = budget.steps
    save()
    return record


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path)
    p.add_argument("--resume", type=Path)
    p.add_argument("--checkpoint", type=Path)
    p.add_argument("--seed", type=int, default=5205)
    p.add_argument("--random-cases", type=int, default=12)
    p.add_argument("--seconds", type=float, default=30)
    p.add_argument("--max-steps", type=int, default=20_000_000)
    p.add_argument("--max-cells", type=int, default=100_000)
    a = p.parse_args(argv)
    if a.input and a.resume:
        p.error("choose --input or --resume")

    def read(path):
        if path.stat().st_size > 2_000_000:
            raise ValueError("input exceeds 2 MB")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        options = read(a.resume)["restart"] if a.resume else {
            "seed": a.seed, "random_cases": a.random_cases,
            "target": read(a.input) if a.input else None}
        result = synthesize(Budget(a.seconds, a.max_steps, a.max_cells),
                            checkpoint_path=a.checkpoint, **options)
    except (OSError, ValueError, KeyError, TypeError, Exhausted) as exc:
        p.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(result["completion"] == "diagnostic_required")


if __name__ == "__main__":
    raise SystemExit(main())
