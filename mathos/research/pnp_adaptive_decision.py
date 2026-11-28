"""Bounded adaptive decision research; never infer UNSAT from exhaustion."""
import time

from .pnp_structural_kernel import Budget, Exhausted, validate
from .pnp_unified_portfolio import fingerprint
from .pnp_evidence_scheduler import execute, replay, _limits
from .pnp_certified_learning import candidates, verify_lemma, _options, RECORDS
from . import pnp_resolution_refutation as resolution
from . import pnp_proof_abstraction as abstraction

SCHEMA = "mathos-pnp-adaptive-decision/1"
MAX_SEARCH_DEPTH = 64
STAGES = ("search", "fallback", "resolution", "learn", "retry")


def search(n, f, budget):
    """Shortest-clause branching, unit propagation, original-clause proof tree.

    A conflict leaf names an original clause. A split covers both truth
    values. A forced literal is a split with an immediate conflict child.
    No reference decisions or benchmark identities are available here.
    """
    f = validate(n, f)
    assigned = {}

    def visit():
        budget.tick()
        if len(assigned) >= MAX_SEARCH_DEPTH:
            raise Exhausted("search depth cap")
        residual = []
        for i, c in enumerate(f):
            budget.tick(1 + len(c))
            if any(assigned.get(abs(x)) == (x > 0) for x in c):
                continue
            free = tuple(sorted({x for x in c if abs(x) not in assigned}))
            if not free:
                return "unsat", ["leaf", i]
            residual.append((i, free))
        if not residual:
            return "sat", [assigned.get(v, False) for v in range(1, n + 1)]

        i, shortest = min(residual, key=lambda row: (len(row[1]), row[0]))
        if len(shortest) == 1:
            literal = shortest[0]
        else:
            # Count occurrences in the active residual, favor short clauses.
            scores = {}
            for _, c in residual:
                budget.tick(1 + len(c))
                for x in c:
                    scores[x] = scores.get(x, 0) + max(1, 8 // len(c))
            literal = max(shortest, key=lambda x: (scores.get(x, 0)
                          + scores.get(-x, 0), scores.get(x, 0), -abs(x), x))
        v, preferred = abs(literal), literal > 0
        children = [None, None]
        for value in (preferred, not preferred):
            assigned[v] = value
            try:
                if len(shortest) == 1 and value != preferred:
                    status, proof = "unsat", ["leaf", i]
                else:
                    status, proof = visit()
            finally:
                del assigned[v]
            if status == "sat":
                return status, proof
            children[int(value)] = proof
        return "unsat", ["split", v, *children]

    decision, certificate = visit()
    return {"decision": decision, "certificate": certificate}


def verify_search(n, clauses, result, budget):
    """Independent direct model or complete case-split replay."""
    f = validate(n, clauses)
    proof = result["certificate"]
    decision = result["decision"]
    if decision == "sat":
        if not isinstance(proof, list) or len(proof) != n or any(type(x) is not bool for x in proof):
            raise ValueError("invalid model")
        for c in f:
            budget.tick(1 + len(c))
            if not any(proof[abs(x) - 1] == (x > 0) for x in c):
                raise ValueError("model falsifies input")
        return True
    if decision != "unsat":
        raise ValueError("unknown is not a proof")
    # Iterative checker, separate from recursive proposer. Check both children.
    todo = [(proof, {})]
    while todo:
        node, assignment = todo.pop()
        budget.tick()
        if not isinstance(node, list) or not node:
            raise ValueError("invalid proof node")
        if node[0] == "leaf" and len(node) == 2:
            i = node[1]
            if type(i) is not int or not 0 <= i < len(f):
                raise ValueError("invalid conflict index")
            c = f[i]
            budget.tick(1 + len(c))
            if not all(abs(x) in assignment and assignment[abs(x)] != (x > 0) for x in c):
                raise ValueError("conflict clause is not falsified")
        elif node[0] == "split" and len(node) == 4:
            v = node[1]
            if type(v) is not int or not 1 <= v <= n or v in assignment or len(assignment) >= MAX_SEARCH_DEPTH:
                raise ValueError("invalid split")
            todo.append((node[2], {**assignment, v: False}))
            todo.append((node[3], {**assignment, v: True}))
        else:
            raise ValueError("invalid proof node")
    return True


def _audit_budget():
    return Budget(seconds=10, max_steps=4_000_000, max_cells=200_000)


def _features(f):
    active = len({abs(x) for c in f for x in c})
    return active, len(f) >= 3 * max(1, active)


def quota(stage, total, used, features):
    left = total - used
    active, dense = features
    if left <= 0:
        return 0
    if stage == "search":
        return min(left, max(1, total // (2 if active <= 16 else 20)))
    if stage == "fallback":
        # Preserve all v12 plans, reserving a refutation opportunity on
        # dense residuals. This is not a theorem of equal-budget dominance.
        return max(1, left * 4 // 5) if dense else left
    if stage == "resolution":
        return max(1, left * 2 // 3)
    if stage == "learn":
        return max(1, left // 2)
    return left


def _search_attempt(n, f, b):
    result = search(n, f, b)
    verify_search(n, f, result, b)
    return result


def _resolution_attempt(n, f, plan, b):
    proof = resolution.propose(n, f, b, strategy=plan[0], width=plan[1], records=RECORDS)
    if proof is None:
        return None
    resolution.verify(n, f, proof, b)
    # Keep the checked original if compact representation is unaffordable.
    try:
        compact = abstraction.compress(n, f, proof, b)
    except Exhausted:
        compact = None
    return {"decision": "unsat", "proof": proof, "compact": compact}


def _learn_attempt(n, f, plan, b):
    choices = candidates(n, f, 2)
    # A bounded pair of opposite singleton probes; borrow unused work,
    # abandon this route on exhaustion. No unproved lemma is appended.
    for assumptions in choices:
        augmented = tuple(f) + tuple((x,) for x in assumptions)
        proof = resolution.propose(n, augmented, b, strategy=plan[0], width=plan[1], records=RECORDS)
        if proof is not None:
            lemma = {"assumptions": list(assumptions),
                     "clause": sorted(-x for x in assumptions), "proof": proof}
            verify_lemma(n, f, lemma, b)
            return {"decision": "unknown", "lemma": lemma}
    return None


def solve(n, clauses, policy, plan, *, total=100_000, seconds=5):
    _limits(total, seconds)
    _options(plan, max(3, total), seconds, 2)
    f = validate(n, clauses)
    extended = f
    features = _features(f)
    start = time.perf_counter_ns()
    deadline = time.monotonic() + seconds
    used, decision, attempts = 0, "unknown", []
    learned = False
    for stage in STAGES:
        if stage == "retry" and not learned:
            break
        q = quota(stage, total, used, features)
        left_time = deadline - time.monotonic()
        if not q or left_time <= 0:
            break
        # Bound each non-final route by its share of remaining time as well
        # as work; reserve the rest. Unused work and time carry forward.
        allowance = left_time * q / (total - used)
        if stage != "retry":
            allowance = min(left_time, allowance)
        b = Budget(seconds=allowance, max_steps=q, max_cells=200_000)
        payload, status = None, "unrecognized"
        try:
            if stage == "fallback":
                payload = execute(n, f, policy, "learned", q, allowance)
                work = payload["work_steps"]
            else:
                if stage in ("search", "retry"):
                    payload = _search_attempt(n, extended, b)
                elif stage == "resolution":
                    payload = _resolution_attempt(n, f, plan, b)
                else:
                    payload = _learn_attempt(n, f, plan, b)
                work = b.steps
            if payload is not None:
                status = "replayed" if payload["decision"] != "unknown" or stage == "learn" else "unrecognized"
        except Exhausted:
            payload, status, work = None, "resource_exhausted", b.steps
        if payload is not None:
            decision = payload["decision"]
            if stage == "learn":
                extended = f + (tuple(payload["lemma"]["clause"]),)
                learned = True
        attempts.append({"stage": stage, "quota": q, "work_steps": work,
                         "status": status, "payload": payload})
        used += work
        if decision != "unknown":
            break
    report = {"schema": SCHEMA, "input_sha256": fingerprint(n, f),
              "plan": list(plan), "total_steps": total, "seconds": seconds,
              "attempts": attempts, "work_steps": used, "decision": decision,
              "elapsed_ns": time.perf_counter_ns() - start,
              "universal_obligation": "unresolved"}
    verify_report(n, f, policy, plan, report)
    return report


def _check_resolution(n, f, plan, proof):
    if (proof["strategy"], proof["width_cap"], proof["record_cap"]) != (*plan, RECORDS):
        raise ValueError("resolution plan mismatch")
    resolution.verify(n, f, proof, _audit_budget())


def verify_report(n, clauses, policy, plan, r):
    f = validate(n, clauses)
    total, seconds = r["total_steps"], r["seconds"]
    _limits(total, seconds)
    _options(plan, max(3, total), seconds, 2)
    if (r["schema"] != SCHEMA or r["input_sha256"] != fingerprint(n, f)
            or r["plan"] != list(plan) or r["universal_obligation"] != "unresolved"):
        raise ValueError("input or policy mismatch")
    attempts = r["attempts"]
    if not isinstance(attempts, list) or len(attempts) > len(STAGES):
        raise ValueError("invalid attempts")
    extended, used, known, learned = f, 0, "unknown", False
    for stage, a in zip(STAGES, attempts):
        q = quota(stage, total, used, _features(f))
        w, p, status = a["work_steps"], a["payload"], a["status"]
        if (known != "unknown" or (stage == "retry" and not learned)
                or a["stage"] != stage or not q or a["quota"] != q
                or type(w) is not int or not 0 <= w <= q
                or status not in ("replayed", "unrecognized", "resource_exhausted")):
            raise ValueError("invalid route or accounting")
        used += w
        if p is None:
            if status == "replayed":
                raise ValueError("missing proof")
            continue
        if status == "resource_exhausted":
            raise ValueError("exhausted route carries payload")
        if stage == "fallback":
            if p["arm"] != "learned" or p["work_steps"] != w:
                raise ValueError("fallback mismatch")
            replay(n, f, policy, q, p)
            known = p["decision"]
        elif stage in ("search", "retry"):
            verify_search(n, extended, p, _audit_budget())
            known = p["decision"]
        elif stage == "resolution":
            if p["decision"] != "unsat":
                raise ValueError("invalid resolution verdict")
            _check_resolution(n, f, plan, p["proof"])
            if p["compact"] is not None:
                c = p["compact"]
                abstraction.verify_embedding(n, f, c["template"], c["source_embedding"], _audit_budget())
            known = "unsat"
        else:
            lemma = p["lemma"]
            if p["decision"] != "unknown" or tuple(lemma["assumptions"]) not in candidates(n, f, 2):
                raise ValueError("invalid learned assumption")
            _check_resolution(n, f + tuple((x,) for x in lemma["assumptions"]), plan, lemma["proof"])
            extended = f + (verify_lemma(n, f, lemma, _audit_budget()),)
            learned = True
        if status != ("replayed" if known != "unknown" or stage == "learn" else "unrecognized"):
            raise ValueError("route status mismatch")
    if (r["decision"] != known or type(r["work_steps"]) is not int
            or r["work_steps"] != used or used > total
            or type(r["elapsed_ns"]) is not int or r["elapsed_ns"] < 0):
        raise ValueError("conclusion or accounting mismatch")
    return True
