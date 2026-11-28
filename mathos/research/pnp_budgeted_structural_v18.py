"""Experimental budgeted matching-first portfolio. Production v18 is unchanged."""
import time
from .pnp_bounded_matching import solve as match, replay as replay_match
from .pnp_unified_discovery_v18 import solve as fallback_solve, verify as fallback_verify
from .pnp_evidence_scheduler import _limits
from .pnp_structural_kernel import Exhausted
from .pnp_unified_portfolio import fingerprint
from .pnp_evidence_benchmark import digest

SCHEMA = "mathos-pnp-budgeted-structural/1"


def solve(n, f, policy, plan, library, *, total=100_000, seconds=5):
    _limits(total, seconds)
    if total < 4:
        raise ValueError("portfolio requires at least four steps")
    deadline = time.monotonic() + seconds
    q = total // 4
    m = match(n, f, steps=q, seconds=seconds/4)
    used, decision = m["work_steps"], m["decision"]
    b = None
    left = deadline-time.monotonic()
    status = "not_needed" if decision!="unknown" else "deadline"
    if decision=="unknown" and left>0 and total-used>0:
        try:
            b = fallback_solve(n,f,policy,plan,library,total=total-used,seconds=left)
            used += b["work_steps"]
            decision = b["decision"]
            status = "attempted"
        except Exhausted:
            status = "resource_exhausted"
            used = total
    r = {"schema":SCHEMA,"input_sha256":fingerprint(n,f),"library_sha256":digest(library),
         "total_steps":total,"seconds":seconds,"work_steps":used,"matching":m,
         "fallback":b,"fallback_status":status,"decision":decision,
         "universal_obligation":"unresolved"}
    if used>total:
        raise ValueError("budget overrun")
    return r


def verify(n,f,policy,plan,library,r):
    total, seconds = r["total_steps"], r["seconds"]
    _limits(total,seconds)
    if (total<4 or r["schema"]!=SCHEMA or r["input_sha256"]!=fingerprint(n,f)
            or r["library_sha256"]!=digest(library) or r["universal_obligation"]!="unresolved"):
        raise ValueError("metadata")
    m,b,status = r["matching"],r["fallback"],r["fallback_status"]
    replay_match(n,f,m,steps=total//4)
    d,w = m["decision"],m["work_steps"]
    if d!="unknown":
        if b is not None or status!="not_needed":
            raise ValueError("fallback after proof")
    elif status=="attempted":
        if b is None or b["total_steps"]!=total-w or not 0<b["seconds"]<=seconds or b["retrieval"] is not True:
            raise ValueError("fallback allowance")
        fallback_verify(n,f,policy,plan,library,b)
        w+=b["work_steps"];d=b["decision"]
    elif status in ("deadline","resource_exhausted"):
        if b is not None:
            raise ValueError("uncredited fallback")
        if status=="resource_exhausted":w=total
    else:
        raise ValueError("missing fallback status")
    if type(r["work_steps"]) is not int or w!=r["work_steps"] or w>total or d!=r["decision"]:
        raise ValueError("portfolio conclusion")
    return True
