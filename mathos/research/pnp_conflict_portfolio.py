"""Experimental CDCL route before the unchanged Hall/v16 fallback."""
import time
from . import pnp_conflict_learning as cdcl
from . import pnp_hall_portfolio as baseline
from .pnp_hall_certificate import eligible as hall_eligible
from .pnp_structural_kernel import validate
from .pnp_unified_portfolio import fingerprint
from .pnp_evidence_scheduler import _limits

SCHEMA = "mathos-pnp-conflict-portfolio/1"


def eligible(f):
    return len({abs(x) for c in f for x in c}) > 16 and not hall_eligible(f)


def solve(n, clauses, policy, plan, *, total=100_000, seconds=5):
    _limits(total, seconds)
    f = validate(n, clauses)
    use = eligible(f)
    start = time.monotonic()
    used, decision, a, fallback = 0, "unknown", None, None
    if use:
        q = max(1, total*3//5)
        a = cdcl.attempt(n, f, q, seconds*3/5)
        used, decision = a["work_steps"], a["decision"]
    if decision == "unknown" and used < total:
        left = seconds - (time.monotonic()-start) if use else seconds
        if left > 0:
            fallback = baseline.solve(n, f, policy, plan, total=total-used, seconds=left)
            used += fallback["work_steps"]
            decision = fallback["decision"]
    r = {"schema": SCHEMA, "input_sha256": fingerprint(n,f),
         "total_steps": total, "seconds": seconds, "eligible": use,
         "work_steps": used, "decision": decision, "cdcl": a,
         "fallback": fallback, "universal_obligation": "unresolved"}
    verify(n,f,policy,plan,r)
    return r


def verify(n, clauses, policy, plan, r):
    f = validate(n, clauses)
    total, seconds = r["total_steps"], r["seconds"]
    _limits(total, seconds)
    if (r["schema"] != SCHEMA or r["input_sha256"] != fingerprint(n,f)
            or r["eligible"] is not eligible(f) or r["universal_obligation"] != "unresolved"):
        raise ValueError("report binding")
    a, fallback = r["cdcl"], r["fallback"]
    used, decision = 0, "unknown"
    if r["eligible"]:
        if a is None:
            raise ValueError("missing CDCL attempt")
        cdcl.replay(n,f,a,max(1,total*3//5))
        used, decision = a["work_steps"], a["decision"]
    elif a is not None:
        raise ValueError("unexpected CDCL attempt")
    if fallback is not None:
        if (decision != "unknown" or fallback["total_steps"] != total-used
                or not 0 < fallback["seconds"] <= seconds
                or (not r["eligible"] and fallback["seconds"] != seconds)):
            raise ValueError("fallback allocation")
        baseline.verify(n,f,policy,plan,fallback)
        used += fallback["work_steps"]
        decision = fallback["decision"]
    elif not r["eligible"]:
        raise ValueError("missing unchanged fallback")
    if (r["decision"] != decision or type(r["work_steps"]) is not int
            or r["work_steps"] != used or used > total):
        raise ValueError("conclusion or work mismatch")
    return True
