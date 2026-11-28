"""Unified certificate-producing research portfolio (v10).

Each plan has an optional certified equisatisfiable preprocessing step and
one existing decision mechanism. Unknown/exhaustion is not a contradiction.
The independent report verifier checks proofs against the original input,
not search logs, resource estimates, or assertions of universal coverage.
"""
import hashlib
import json

from .pnp_structural_kernel import Budget, Exhausted, validate, normalize
from . import pnp_certificate_routes as semantic
from . import pnp_triple_parity as parity
from . import pnp_constraint_algebra as algebra
from . import pnp_compositional as components
from . import pnp_recursive_separators as recursive
from . import pnp_reduction_portfolio as reduction

DIRECT = semantic.ROUTES + ("triple_parity", "bijunctive", "affine",
                            "mixed", "components", "recursive")
PROFILES = ("none",) + reduction.PROFILES
DEFAULT_PLANS = tuple((p, r) for p in PROFILES for r in
                      (DIRECT if p == "none" else ("recursive",)))
MAX_PLANS = 64


def _options(depth, nodes, k, cap):
    for v, lo, hi in ((depth,0,recursive.MAX_DEPTH),(nodes,1,recursive.MAX_NODES),
                      (k,0,components.MAX_K),(cap,0,12)):
        if type(v) is not int or not lo<=v<=hi:
            raise ValueError("invalid portfolio options")


def _plans(plans):
    if not isinstance(plans,(list,tuple)) or not 1<=len(plans)<=MAX_PLANS:
        raise ValueError("invalid plan count")
    result=[]
    for p in plans:
        if (not isinstance(p,(list,tuple)) or len(p)!=2 or
                p[0] not in PROFILES or p[1] not in DIRECT):
            raise ValueError("invalid transformation plan")
        result.append(tuple(p))
    if len(set(result))!=len(result):
        raise ValueError("duplicate plan")
    return tuple(result)


def fingerprint(n,clauses):
    f=validate(n,clauses)
    return hashlib.sha256(json.dumps([n,f],separators=(",",":")).encode("ascii")).hexdigest()


class Slice:
    """Cooperative per-plan work quota and shared global deadline/cell cap."""
    def __init__(self,parent,quota):
        self.parent=parent
        self.max_steps=quota
        self.max_cells=parent.max_cells
        self.deadline=parent.deadline
        self.steps=0
    def tick(self,count=1):
        if self.steps+count>self.max_steps:
            raise Exhausted("plan work quota")
        self.parent.tick(count)
        self.steps+=count
    def cells(self,count):
        self.tick()
        if count>self.max_cells:
            raise Exhausted("factor-cell limit")


def _propose(n,f,route,budget,depth,nodes,k):
    if route in semantic.ROUTES:
        return semantic.propose(n,f,route,budget)
    if route=="triple_parity":
        return parity.propose(n,f,budget)
    if route in algebra.MODES:
        return algebra.propose(n,f,route,budget)
    if route=="mixed":
        return algebra.solve(n,f,budget)
    if route=="components":
        return components.search(n,f,budget,k=k)
    return recursive.search(n,f,budget,depth=depth,nodes=nodes)


def _verify_decision(n,f,route,proof,budget,depth,nodes,k):
    if proof is None:
        return "unknown"
    if route in semantic.ROUTES:
        if proof["route"]!=route:
            raise ValueError("semantic route mismatch")
        semantic.verify(n,f,proof,budget)
    elif route=="triple_parity":
        parity.verify(n,f,proof,budget)
    elif route in algebra.MODES:
        if proof["mode"]!=route:
            raise ValueError("algebra mode mismatch")
        algebra.verify(n,f,proof,budget)
    elif route=="mixed":
        algebra.verify_solution(n,f,proof,budget)
    elif route=="components":
        if proof["k"]!=k:
            raise ValueError("backdoor cap mismatch")
        components.verify_certificate(n,f,proof,budget)
        return proof["decision"]
    elif route=="recursive":
        if proof["depth_limit"]!=depth or proof["node_limit"]!=nodes:
            raise ValueError("recursive limits mismatch")
        recursive.verify_certificate(n,f,proof,budget)
        return proof["decision"]
    else:
        raise ValueError("unknown proof route")
    return "sat" if not proof["clauses"] else "unsat"


def _replay_plan(n,f,plan,entry,budget,depth,nodes,k,cap):
    profile,route=plan
    trace=entry["reduction"]
    if profile=="none":
        if trace is not None:
            raise ValueError("unexpected preprocessing")
        nn,nf=n,f
    else:
        if trace is None or trace["profile"]!=profile or trace["neighbor_cap"]!=cap:
            raise ValueError("preprocessing profile mismatch")
        reduction.verify_reduction(n,f,trace,budget)
        nn,nf=trace["n"],trace["clauses"]
    return _verify_decision(nn,nf,route,entry["proof"],budget,depth,nodes,k)


def _conclusion(outcomes):
    known={x for x in outcomes if x!="unknown"}
    if len(known)>1:
        raise ValueError("conflicting replayed decisions")
    return next(iter(known),"unknown")


def run(n,clauses,budget,*,plans=DEFAULT_PLANS,depth=4,nodes=1024,k=2,cap=4):
    """Investigate all configured plans under equal non-borrowing work quotas.

    A plan is credited only after replay. A malformed internal certificate or
    conflicting decision aborts with a diagnostic rather than a valid report.
    """
    _options(depth,nodes,k,cap)
    plans=_plans(plans)
    f=validate(n,clauses)
    digest=fingerprint(n,f)
    available=budget.max_steps-budget.steps
    quota=max(0,available//len(plans))
    entries=[]
    for profile,route in plans:
        local=Slice(budget,quota)
        try:
            local.tick()
            trace=None
            nn,nf=n,f
            if profile!="none":
                trace=reduction.reduce_cnf(n,f,local,profile=profile,cap=cap)
                # Check before passing the residual to another engine.
                reduction.verify_reduction(n,f,trace,local)
                nn,nf=trace["n"],trace["clauses"]
            proof=_propose(nn,nf,route,local,depth,nodes,k)
            entry={"plan":(profile,route),"reduction":trace,"proof":proof}
            decision=_replay_plan(n,f,(profile,route),entry,local,depth,nodes,k,cap)
            entry.update(decision=decision,status="replayed" if proof is not None else "unrecognized")
        except Exhausted as exc:
            entry={"plan":(profile,route),"reduction":None,"proof":None,
                   "decision":"unknown","status":"resource_exhausted","reason":str(exc)}
        entry["work_steps"]=local.steps
        entries.append(entry)
    decision=_conclusion(e["decision"] for e in entries)
    return {"schema":"mathos-pnp-unified/1","input_sha256":digest,
            "options":{"depth":depth,"nodes":nodes,"k":k,"cap":cap},
            "plans":plans,"entries":entries,"decision":decision,
            "universal_obligation":"unresolved","p_equals_np_established":False,
            "p_not_equals_np_established":False,"novel_theorem_verified":False,
            "formal_verification":"not_performed","per_plan_work_quota":quota,
            "work_steps":sum(e["work_steps"] for e in entries)}


def verify_report(n,clauses,report,budget):
    """Check every credited proof and reconstruct the exact decision.

    Exhaustion/unrecognized metadata cannot establish a lower bound. Search
    completeness and work counters are not certified by this verifier.
    """
    f=validate(n,clauses)
    if report["schema"]!="mathos-pnp-unified/1" or report["input_sha256"]!=fingerprint(n,f):
        raise ValueError("input digest or schema mismatch")
    if (report["universal_obligation"]!="unresolved" or
            any(report[x] is not False for x in
                ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified")) or
            report["formal_verification"]!="not_performed"):
        raise ValueError("unsupported universal claim")
    depth,nodes,k,cap=(report["options"][x] for x in ("depth","nodes","k","cap"))
    _options(depth,nodes,k,cap)
    plans=_plans(report["plans"])
    entries=report["entries"]
    if len(entries)!=len(plans):
        raise ValueError("missing plan entries")
    outcomes=[]
    for plan,e in zip(plans,entries):
        budget.tick()
        if tuple(e["plan"])!=plan:
            raise ValueError("plan order mismatch")
        status=e["status"]
        if status=="resource_exhausted":
            if e["proof"] is not None or e["reduction"] is not None:
                raise ValueError("exhausted plan cannot credit partial proof")
            decision="unknown"
        elif status in ("replayed","unrecognized"):
            if (e["proof"] is None)!=(status=="unrecognized"):
                raise ValueError("proof/status mismatch")
            decision=_replay_plan(n,f,plan,e,budget,depth,nodes,k,cap)
        else:
            raise ValueError("unknown plan status")
        if e["decision"]!=decision:
            raise ValueError("plan conclusion mismatch")
        outcomes.append(decision)
    if report["decision"]!=_conclusion(outcomes):
        raise ValueError("global conclusion mismatch")
    return True
