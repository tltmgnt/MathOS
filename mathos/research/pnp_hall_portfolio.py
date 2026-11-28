"""Experimental Hall-first route with unchanged v16 fallback."""
import time
from . import pnp_adaptive_decision as adaptive
from . import pnp_hall_certificate as hall
from .pnp_structural_kernel import Budget, Exhausted, validate
from .pnp_evidence_scheduler import _limits
from .pnp_unified_portfolio import fingerprint

SCHEMA = "mathos-pnp-hall-portfolio/1"


def solve(n, clauses, policy, plan, *, total=100_000, seconds=5):
    _limits(total, seconds)
    f = validate(n, clauses)
    eligible = hall.eligible(f)
    start = time.monotonic()
    used, decision, attempt, fallback = 0, "unknown", None, None
    if eligible:
        q = max(1, total // 5)
        b = Budget(seconds=seconds / 5, max_steps=q, max_cells=200_000)
        payload, status = None, "unrecognized"
        try:
            payload = hall.propose(n, f, b)
            if payload is not None:
                hall.verify(n, f, payload, b)
                decision, status = payload["decision"], "replayed"
        except Exhausted:
            payload, decision, status = None, "unknown", "resource_exhausted"
        used = b.steps
        attempt = {"quota": q, "work_steps": used, "status": status,
                   "payload": payload}
    if decision == "unknown" and used < total:
        left = seconds - (time.monotonic() - start) if eligible else seconds
        if left > 0:
            fallback = adaptive.solve(n, f, policy, plan, total=total-used, seconds=left)
            used += fallback["work_steps"]
            decision = fallback["decision"]
    r = {"schema": SCHEMA, "input_sha256": fingerprint(n, f),
         "total_steps": total, "seconds": seconds, "eligible": eligible,
         "work_steps": used, "decision": decision, "hall": attempt,
         "fallback": fallback, "universal_obligation": "unresolved"}
    verify(n, f, policy, plan, r)
    return r


def verify(n, clauses, policy, plan, r):
    f = validate(n, clauses)
    total, seconds = r["total_steps"], r["seconds"]
    _limits(total, seconds)
    if (r["schema"] != SCHEMA or r["input_sha256"] != fingerprint(n, f)
            or r["universal_obligation"] != "unresolved"
            or r["eligible"] is not hall.eligible(f)):
        raise ValueError("invalid report binding")
    a, fallback, used, known = r["hall"], r["fallback"], 0, "unknown"
    if r["eligible"]:
        if not isinstance(a, dict) or a["quota"] != max(1, total // 5):
            raise ValueError("missing or incorrect Hall allowance")
        used = a["work_steps"]
        if type(used) is not int or not 0 <= used <= a["quota"]:
            raise ValueError("Hall accounting")
        p = a["payload"]
        if a["status"] == "replayed":
            if p is None:
                raise ValueError("missing Hall certificate")
            hall.verify(n, f, p, adaptive._audit_budget())
            known = p["decision"]
        elif a["status"] not in ("unrecognized", "resource_exhausted") or p is not None:
            raise ValueError("uncredited Hall payload")
    elif a is not None:
        raise ValueError("unexpected Hall attempt")
    if fallback is not None:
        if (known != "unknown" or fallback["total_steps"] != total-used
                or not 0 < fallback["seconds"] <= seconds
                or (not r["eligible"] and fallback["seconds"] != seconds)):
            raise ValueError("invalid fallback allocation")
        adaptive.verify_report(n, f, policy, plan, fallback)
        used += fallback["work_steps"]
        known = fallback["decision"]
    elif not r["eligible"]:
        raise ValueError("missing unchanged fallback")
    if (r["decision"] != known or type(r["work_steps"]) is not int
            or r["work_steps"] != used or used > total):
        raise ValueError("conclusion or accounting mismatch")
    return True
