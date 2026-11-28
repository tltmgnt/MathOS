"""Native Gaussian CDCL probe, preserving affine-projected fallback."""
import time
from . import pnp_native_xor_conflict as native
from .pnp_affine_projected import eligible as mixed_eligible
from . import pnp_affine_projected_portfolio as baseline
from .pnp_hall_certificate import eligible as hall_eligible
from .pnp_structural_kernel import validate
from .pnp_unified_portfolio import fingerprint
from .pnp_evidence_scheduler import _limits

SCHEMA="mathos-pnp-native-xor-portfolio/1"


def eligible(f):
    return (len({abs(x) for c in f for x in c})>16
            and mixed_eligible(f) and not hall_eligible(f))


def solve(n,clauses,policy,plan,*,total=100_000,seconds=5,attempt_fn=None):
    _limits(total,seconds)
    f=validate(n,clauses)
    use=eligible(f)
    start=time.monotonic()
    a,fb,used,decision=None,None,0,"unknown"
    if use:
        a=(native.attempt if attempt_fn is None else attempt_fn)(n,f,max(1,total//5),seconds/5)
        used,decision=a["work_steps"],a["decision"]
    if decision=="unknown" and used<total:
        left=seconds-(time.monotonic()-start) if use else seconds
        if left>0:
            fb=baseline.solve(n,f,policy,plan,total=total-used,seconds=left)
            used+=fb["work_steps"]
            decision=fb["decision"]
    r={"schema":SCHEMA,"input_sha256":fingerprint(n,f),
       "total_steps":total,"seconds":seconds,"eligible":use,
       "work_steps":used,"decision":decision,"native":a,"fallback":fb,
       "universal_obligation":"unresolved"}
    verify(n,f,policy,plan,r)
    return r


def verify(n,clauses,policy,plan,r):
    f=validate(n,clauses)
    total,seconds=r["total_steps"],r["seconds"]
    _limits(total,seconds)
    if (r["schema"]!=SCHEMA or r["input_sha256"]!=fingerprint(n,f)
            or r["eligible"] is not eligible(f) or r["universal_obligation"]!="unresolved"):
        raise ValueError("report binding")
    a,fb=r["native"],r["fallback"]
    used,decision=0,"unknown"
    if r["eligible"]:
        if a is None:
            raise ValueError("missing native attempt")
        native.replay(n,f,a,max(1,total//5))
        used,decision=a["work_steps"],a["decision"]
    elif a is not None:
        raise ValueError("unexpected native attempt")
    if fb is not None:
        if (decision!="unknown" or fb["total_steps"]!=total-used
                or not 0<fb["seconds"]<=seconds
                or (not r["eligible"] and fb["seconds"]!=seconds)):
            raise ValueError("fallback allocation")
        baseline.verify(n,f,policy,plan,fb)
        used+=fb["work_steps"]
        decision=fb["decision"]
    elif not r["eligible"]:
        raise ValueError("missing unchanged fallback")
    if (r["decision"]!=decision or type(r["work_steps"]) is not int
            or r["work_steps"]!=used or used>total):
        raise ValueError("conclusion or work mismatch")
    return True
