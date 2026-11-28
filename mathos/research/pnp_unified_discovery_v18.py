"""Experimental v18 portfolio; frozen library, checked decisions, no universal claim."""
import time
from .pnp_structural_kernel import Budget, Exhausted, validate
from .pnp_unified_portfolio import fingerprint
from .pnp_evidence_benchmark import digest
from .pnp_adaptive_decision import solve as adaptive, verify_report
from .pnp_proof_library import Index, reuse, reconstruct, verify_certificate
from .pnp_evidence_scheduler import _limits

SCHEMA = "mathos-pnp-unified-discovery/1"


def features(n, clauses):
    f = validate(n, clauses)
    return {"active": len({abs(x) for c in f for x in c}),
            "clauses": len(f), "width": max(map(len, f), default=0),
            "units": sum(len(c) == 1 for c in f),
            "horn": all(sum(x > 0 for x in c) <= 1 for c in f)}


def route_order(info, library, retrieval):
    if not retrieval or not library:
        return ("adaptive",)
    # Keep the cheap constructive route first on the small regime where v16
    # already decided all 50 archived instances. This is a hypothesis, not a
    # proof of dominance. Large active support gets a bounded retrieval probe.
    return ("adaptive", "library") if info["active"] <= 16 else ("library", "adaptive")


def allowance(route, index, order, total, used):
    left = total - used
    if index == len(order)-1:
        return left
    return min(left, max(1, total * (3 if route == "adaptive" else 1) // 4))


def solve(n, clauses, policy, plan, library, *, total=100_000, seconds=5, retrieval=True):
    _limits(total, seconds)
    if type(retrieval) is not bool:
        raise ValueError("invalid retrieval switch")
    f = validate(n, clauses)
    info = features(n, f)
    order = route_order(info, library, retrieval)
    used, attempts, decision = 0, [], "unknown"
    deadline = time.monotonic() + seconds
    frozen = digest(library)
    for i, route in enumerate(order):
        q = allowance(route, i, order, total, used)
        left = deadline - time.monotonic()
        if q <= 0 or left <= 0:
            break
        duration = left * q / (total - used)
        payload = None
        b = Budget(seconds=duration, max_steps=q, max_cells=100_000)
        try:
            if route == "adaptive":
                payload = adaptive(n, f, policy, plan, total=q, seconds=duration)
                work = payload["work_steps"]
                decision = payload["decision"]
            else:
                payload = reuse(n, f, Index(library), b)
                work = b.steps
                if payload["status"] == "verified":
                    # Independent from template lookup; require explicit RUP
                    # certificate on the original, not the enlarged guard set.
                    verify_certificate(n, f, payload["proof"], b)
                    work = b.steps
                    decision = "unsat"
        except Exhausted:
            # A proof whose replay exhausts resources earns no decision.
            # Conservatively charge the full route quota on thrown exhaustion.
            payload, work, decision = None, q, "unknown"
        attempts.append({"route": route, "quota": q, "work_steps": work,
                         "seconds": duration, "payload": payload})
        used += work
        if decision != "unknown":
            break
    if digest(library) != frozen:
        raise ValueError("library mutated")
    result = {"schema": SCHEMA, "input_sha256": fingerprint(n, f),
              "library_sha256": frozen, "features": info, "retrieval": retrieval,
              "total_steps": total, "seconds": seconds, "work_steps": used,
              "attempts": attempts, "decision": decision,
              "universal_obligation": "unresolved"}
    verify(n, f, policy, plan, library, result)
    return result


def verify(n, clauses, policy, plan, library, r):
    f = validate(n, clauses)
    total, seconds = r["total_steps"], r["seconds"]
    _limits(total, seconds)
    if (r["schema"] != SCHEMA or r["input_sha256"] != fingerprint(n, f)
            or r["library_sha256"] != digest(library)
            or r["features"] != features(n, f)
            or type(r["retrieval"]) is not bool
            or r["universal_obligation"] != "unresolved"):
        raise ValueError("metadata mismatch")
    order = route_order(r["features"], library, r["retrieval"])
    if not isinstance(r["attempts"], list) or len(r["attempts"]) > len(order):
        raise ValueError("route count")
    used, known = 0, "unknown"
    for i, a in enumerate(r["attempts"]):
        route = order[i]
        q = allowance(route, i, order, total, used)
        w, p = a["work_steps"], a["payload"]
        if (known != "unknown" or a["route"] != route or a["quota"] != q
                or q <= 0 or type(w) is not int or not 0 <= w <= q
                or not 0 < a["seconds"] <= seconds):
            raise ValueError("route accounting")
        used += w
        if p is None:
            if w != q:
                raise ValueError("exhaustion accounting")
            continue
        if route == "adaptive":
            if (p["total_steps"], p["seconds"], p["work_steps"]) != (q, a["seconds"], w):
                raise ValueError("adaptive accounting")
            verify_report(n, f, policy, plan, p)
            known = p["decision"]
        elif p["status"] == "verified":
            b = Budget(seconds=15, max_steps=4_000_000, max_cells=200_000)
            proof = reconstruct(n, f, Index(library), p["transfers"], b)
            if digest(proof) != digest(p["proof"]):
                raise ValueError("library proof mismatch")
            verify_certificate(n, f, proof, Budget(seconds=15, max_steps=4_000_000))
            known = "unsat"
        elif p["status"] not in ("not_found", "resource_exhausted", "transfer_limit") or "proof" in p or "transfers" in p:
            raise ValueError("uncredited library payload")
    if (r["decision"] != known or type(r["work_steps"]) is not int
            or r["work_steps"] != used or used > total):
        raise ValueError("conclusion mismatch")
    return True


def abstract_verified_tree(n, clauses, result, budget):
    """Offline: turn a checked split tree into a bounded guarded RUP fragment.

    At a conflict leaf, negating its path-blocking clause fixes the path
    assignment and falsifies the cited input clause. At a split, the two
    child blocking clauses force opposite pivot values under the negated
    parent blocker. Hence postorder blockers are RUP, ending with empty.
    No optimality, semantic minimality, or uniform complexity is claimed.
    """
    from .pnp_adaptive_decision import verify_search
    f = validate(n, clauses)
    if result["decision"] != "unsat":
        raise ValueError("abstraction requires a checked contradiction")
    verify_search(n, f, result, budget)
    guards, steps, seen = set(), [], set()

    def visit(node, path):
        budget.tick()
        if node[0] == "leaf":
            guards.add(tuple(sorted(set(f[node[1]]))))
        else:
            v = node[1]
            visit(node[2], path + (-v,))
            visit(node[3], path + (v,))
        blocker = tuple(sorted(-x for x in path))
        if blocker not in seen:
            if len(steps) >= 64:
                raise Exhausted("offline abstraction step cap")
            seen.add(blocker)
            steps.append(blocker)
    visit(result["certificate"], ())
    active = sorted({abs(x) for c in list(guards) + steps for x in c})
    if len(active) > 9:
        raise Exhausted("offline abstraction support cap")
    labels = {v: i+1 for i, v in enumerate(active)}
    def rename(c):
        return tuple(sorted(labels[abs(x)] if x > 0 else -labels[abs(x)] for x in c))
    template = {"n": len(active), "axioms": tuple(sorted(map(rename, guards))),
                "steps": tuple(map(rename, steps)), "edges": ()}
    record = {"source_sha256": fingerprint(n, f), "template": template,
              "source_embedding": tuple(active)}
    check_abstraction(n, f, record, budget)
    return record


def check_abstraction(n, clauses, record, budget):
    from .pnp_proof_abstraction import _original_clauses
    from .pnp_proof_library import mapped
    f = validate(n, clauses)
    t, e = record["template"], record["source_embedding"]
    if (record["source_sha256"] != fingerprint(n, f)
            or type(t["n"]) is not int or not 0 <= t["n"] <= 9
            or not 1 <= len(t["steps"]) <= 64
            or len(e) != t["n"] or any(type(x) is not int or not 0 < abs(x) <= n for x in e)
            or len({abs(x) for x in e}) != len(e)
            or t["edges"] not in ((), [])):
        raise ValueError("abstraction metadata")
    verify_certificate(t["n"], t["axioms"], t["steps"], budget)
    original = _original_clauses(n, f)
    for c in t["axioms"]:
        budget.tick(1 + len(c))
        if mapped(c, e) not in original:
            raise ValueError("abstraction lacks source guard")
    verify_certificate(n, f, [mapped(c, e) for c in t["steps"]], budget)
    return True


def admit_offline(library, n, clauses, record, budget):
    """Return a new immutable library snapshot; never mutate a scored one.

    Caller must preserve the source and record in a separate provenance log.
    Admission is not called by solve or held-out evaluation.
    """
    from .pnp_proof_library import MAX_TEMPLATES
    check_abstraction(n, clauses, record, budget)
    t = record["template"]
    if any(digest(x) == digest(t) for x in library):
        return tuple(library)
    if len(library) >= MAX_TEMPLATES:
        raise Exhausted("library admission cap")
    # JSON roundtrip prevents aliasing caller-owned candidate objects.
    import json
    return tuple(json.loads(json.dumps(x)) for x in (*library, t))
