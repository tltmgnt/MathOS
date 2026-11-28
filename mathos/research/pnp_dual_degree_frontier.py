"""Dual degree certificates, cross-model controls and a finite obstruction search."""
import argparse
import json
import random
from itertools import combinations
from pathlib import Path

from .pnp_dual_degree import static,from_closure,verify as verify_dual
from .pnp_degree_closure import derive,verify as verify_closure
from .pnp_resolution_algebra import lift,verify as verify_lift
from .pnp_resolution_refutation import propose as resolution
from .pnp_cross_model import propose as first_step,verify as verify_first_step
from .pnp_algebra_frontier import xor_block
from .pnp_structural_kernel import normalize,brute,Exhausted
from .pnp_inference_complexity import budget
from .pnp_outcome_engine import checkpoint

SCHEMA="mathos-pnp-dual-degree-frontier/1"
SEED=31031


def tetrahedron(odd):
    edges=list(combinations(range(4),2))
    f=[]
    for i in range(4):
        scope=tuple(j+1 for j,e in enumerate(edges) if i in e)
        f.extend(xor_block(scope,int(odd and i==0)))
    return {"id":"tetrahedron_odd" if odd else "tetrahedron_even",
            "n":6,"clauses":[list(c) for c in f]}


def cases():
    out=[{"id":"empty","n":0,"clauses":[]},
         {"id":"empty_conflict","n":0,"clauses":[[]]},
         {"id":"chain","n":5,"clauses":[[1],[-1,2],[-2,3],[-3,4],[-4,5],[-5]]},
         {"id":"static_gap","n":3,"clauses":[[-1,2],[1,-2],[1,2],[-1,3],[-2,-3]]},
         {"id":"sat_clause","n":3,"clauses":[[1,2,3]]},
         tetrahedron(True),tetrahedron(False)]
    rng=random.Random(SEED)
    for i in range(16):
        n=6+i%3
        f=[]
        for _ in range(4*n):
            vs=rng.sample(range(1,n+1),3)
            f.append([v if rng.randrange(2) else -v for v in vs])
        out.append({"id":f"search_{i:02d}","n":n,"clauses":f})
    return out


def reference(c):
    nn,g,_=normalize(c["n"],c["clauses"])
    return brute(nn,g,budget())


def row(c):
    n,f=c["n"],c["clauses"]
    sat=reference(c)
    nn,g,_=normalize(n,f)
    d=max(map(len,g),default=0)
    r={"case":c,"reference":sat,"degree":d,"closure":None,"dual":None,
       "static":None,"resolution_simulation":None,"first_step":None,
       "status":"resource_exhausted"}
    try:
        p=derive(n,f,budget(),degree=d)
        verify_closure(n,f,p,budget())
        h=None
        if p["status"]=="closed_no_refutation":
            h=from_closure(n,f,p,budget())
            verify_dual(n,f,h,budget())
        r.update(closure=p,dual=h,status=p["status"])
    except Exhausted:
        pass
    if c["id"]=="static_gap":
        r["static"]=static(n,f,budget(),degree=d)
    if c["id"] in ("empty_conflict","chain","static_gap","tetrahedron_odd"):
        p=resolution(n,f,budget(),width=8)
        if p is None:
            raise AssertionError("control resolution proof missing")
        r["resolution_simulation"]=lift(n,f,p,budget())
    if c["id"].startswith("tetrahedron_"):
        r["first_step"]=first_step(n,f,budget())
    check(r)
    return r


def check(r):
    c=r["case"]
    n,f=c["n"],c["clauses"]
    _,g,_=normalize(n,f)
    d=max(map(len,g),default=0)
    if r["degree"]!=d or r["reference"] is not reference(c):
        raise ValueError("case metadata mismatch")
    p,h=r["closure"],r["dual"]
    if r["status"]=="resource_exhausted":
        if p is not None or h is not None:
            raise ValueError("exhausted case credited")
    else:
        if p is None or p["status"]!=r["status"] or p["degree"]!=d:
            raise ValueError("closure status mismatch")
        verify_closure(n,f,p,budget())
        if r["status"]=="refuted":
            if r["reference"] or h is not None:
                raise ValueError("invalid refutation")
        elif r["status"]=="closed_no_refutation":
            if h is None or h["degree"]!=d:
                raise ValueError("missing dual certificate")
            verify_dual(n,f,h,budget())
        else:
            raise ValueError("unknown closure status")
    ident=c["id"]
    s=r["static"]
    if ident=="static_gap":
        if (s is None or s["scope"]!="static" or s["degree"]!=d
                or r["status"]!="refuted" or r["reference"]):
            raise ValueError("missing static-versus-dynamic gap")
        verify_dual(n,f,s,budget(),require_dynamic=False)
        # A static certificate is not automatically a dynamic one.
        try:
            verify_dual(n,f,{**s,"scope":"dynamic"},budget())
        except ValueError:
            pass
        else:
            raise ValueError("static certificate unexpectedly closed")
    elif s is not None:
        raise ValueError("unexpected static certificate")
    sim=r["resolution_simulation"]
    if ident in ("empty_conflict","chain","static_gap","tetrahedron_odd"):
        if sim is None or r["reference"]:
            raise ValueError("missing simulation")
        verify_lift(n,f,sim,budget())
    elif sim is not None:
        raise ValueError("unexpected simulation")
    a=r["first_step"]
    if ident.startswith("tetrahedron_"):
        if a is None:
            raise ValueError("missing first-step bound")
        verify_first_step(n,f,a,budget())
        if a["xor_rhs"]!=int(ident=="tetrahedron_odd"):
            raise ValueError("parity control mismatch")
        if ident=="tetrahedron_odd" and (r["status"]!="refuted" or d!=3):
            raise ValueError("missing cross-model separation")
    elif a is not None:
        raise ValueError("unexpected first-step bound")
    return True


def summary(rows):
    searched=[r for r in rows if r["case"]["id"].startswith("search_")]
    return {"cases":len(rows),"search_cases":len(searched),
            "search_unsat":sum(not r["reference"] for r in searched),
            "search_unsat_degree_obstructions":sum(not r["reference"] and r["dual"] is not None for r in searched),
            "dynamic_dual_certificates":sum(r["dual"] is not None for r in rows),
            "static_gap_controls":sum(r["static"] is not None for r in rows),
            "refutations":sum(r["status"]=="refuted" for r in rows),
            "resource_exhausted":sum(r["status"]=="resource_exhausted" for r in rows),
            "dual_functionals":sum(len(r["dual"]["functionals"]) for r in rows if r["dual"] is not None),
            "resolution_simulations":sum(r["resolution_simulation"] is not None for r in rows),
            "cross_model_separations":sum(r["case"]["id"]=="tetrahedron_odd" and r["status"]=="refuted" for r in rows),
            "universal_obligations_closed":0}


def run(*,checkpoint_path=None):
    r={"schema":SCHEMA,"rows":[],"completion":"running",
       "scope":"bounded Boolean quotient degree; dual closure and resolution simulation",
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False}
    try:
        for c in cases():
            r["rows"].append(row(c))
            if checkpoint_path:
                checkpoint(checkpoint_path,r)
        r["completion"]="completed"
    except (ValueError,AssertionError,Exhausted) as e:
        r["completion"]="diagnostic_required"
        r["reason"]=str(e)
    r["summary"]=summary(r["rows"])
    if checkpoint_path:
        checkpoint(checkpoint_path,r)
    return r


def audit(r):
    if (r["schema"]!=SCHEMA or r["completion"]!="completed"
            or r["scope"]!="bounded Boolean quotient degree; dual closure and resolution simulation"
            or r["universal_obligation"]!="unresolved"
            or any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))):
        raise ValueError("invalid governance")
    if [a["case"] for a in r["rows"]]!=cases():
        raise ValueError("incomplete evaluation")
    for a in r["rows"]:
        check(a)
    if r["summary"]!=summary(r["rows"]):
        raise ValueError("incorrect aggregate")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    a=p.parse_args(argv)
    try:
        if a.audit:
            if a.audit.stat().st_size>32_000_000:
                raise ValueError("oversized report")
            audit(json.loads(a.audit.read_text(encoding="utf-8")))
            print(json.dumps({"status":"replayed","universal_obligation":"unresolved"}))
            return 0
        r=run(checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return int(r["completion"]!="completed")
    except (OSError,ValueError,TypeError,KeyError,Exhausted) as e:
        p.error(str(e))


if __name__=="__main__":
    raise SystemExit(main())
