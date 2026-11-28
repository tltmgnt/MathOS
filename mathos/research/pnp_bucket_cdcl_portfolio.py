"""Explicit two-factor ablation: indexed search and probe quota."""
import time
from . import pnp_indexed_rup as indexed
from . import pnp_bucket_cdcl as optimized
from . import pnp_coloring_portfolio as fallback
from .pnp_indexed_rup_portfolio import eligible
from .pnp_structural_kernel import validate
from .pnp_unified_portfolio import fingerprint
from .pnp_evidence_scheduler import _limits

SCHEMA="mathos-pnp-bucket-cdcl-portfolio/1"
MODES=("optimized_half","frozen_extended","candidate")


def quota(mode,total,seconds):
    if mode not in MODES:
        raise ValueError("unknown mode")
    if mode=="optimized_half":
        return max(1,total//2),seconds/2
    return max(1,2*total//3),2*seconds/3


def solve(n,clauses,policy,plan,*,total=100_000,seconds=5,mode="candidate"):
    _limits(total,seconds)
    cap,probe_seconds=quota(mode,total,seconds)
    f=validate(n,clauses)
    use=eligible(f)
    start=time.monotonic()
    a,fb,used,decision=None,None,0,"unknown"
    if use:
        engine=indexed if mode=="frozen_extended" else optimized
        a=engine.attempt(n,f,cap,probe_seconds)
        used,decision=a["work_steps"],a["decision"]
    if decision=="unknown" and used<total:
        left=seconds-(time.monotonic()-start) if use else seconds
        if left>0:
            fb=fallback.solve(n,f,policy,plan,total=total-used,seconds=left)
            used+=fb["work_steps"]
            decision=fb["decision"]
    r={"schema":SCHEMA,"input_sha256":fingerprint(n,f),
       "mode":mode,"total_steps":total,"seconds":seconds,"eligible":use,
       "work_steps":used,"decision":decision,"indexed":a,"fallback":fb,
       "universal_obligation":"unresolved"}
    verify(n,f,policy,plan,r,mode=mode)
    return r


def verify(n,clauses,policy,plan,r,*,mode="candidate"):
    f=validate(n,clauses)
    total,seconds=r["total_steps"],r["seconds"]
    _limits(total,seconds)
    cap,_=quota(mode,total,seconds)
    if (r["schema"]!=SCHEMA or r["input_sha256"]!=fingerprint(n,f)
            or r["mode"]!=mode or r["eligible"] is not eligible(f)
            or r["universal_obligation"]!="unresolved"):
        raise ValueError("report binding")
    a,fb=r["indexed"],r["fallback"]
    used,decision=0,"unknown"
    if r["eligible"]:
        if a is None:
            raise ValueError("missing indexed attempt")
        indexed.replay(n,f,a,cap)
        used,decision=a["work_steps"],a["decision"]
    elif a is not None:
        raise ValueError("unexpected indexed attempt")
    if fb is not None:
        if (decision!="unknown" or fb["total_steps"]!=total-used
                or not 0<fb["seconds"]<=seconds
                or (not r["eligible"] and fb["seconds"]!=seconds)):
            raise ValueError("fallback allocation")
        fallback.verify(n,f,policy,plan,fb)
        used+=fb["work_steps"]
        decision=fb["decision"]
    elif not r["eligible"]:
        raise ValueError("missing unchanged fallback")
    if (r["decision"]!=decision or type(r["work_steps"]) is not int
            or r["work_steps"]!=used or used>total):
        raise ValueError("conclusion or work mismatch")
    return True
