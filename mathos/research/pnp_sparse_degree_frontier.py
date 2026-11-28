"""Scaling and obstruction search with compressed monomial coordinates."""
import argparse
import json
import random
from itertools import combinations
from math import comb
from pathlib import Path
from .pnp_sparse_degree import derive,evaluation,verify,coordinates
from .pnp_degree_closure import derive as dense,verify as verify_dense
from .pnp_cross_model import prism
from .pnp_component_parity import propose as parity,verify as verify_parity
from .pnp_structural_kernel import normalize,brute,Exhausted,Budget
from .pnp_inference_complexity import budget
from .pnp_outcome_engine import checkpoint

SCHEMA="mathos-pnp-sparse-degree-frontier/1"
SEED=32032


def pigeonhole(p,h):
    f=[]
    for i in range(p):
        f.append([i*h+j+1 for j in range(h)])
        f.extend([-i*h-a-1,-i*h-b-1] for a,b in combinations(range(h),2))
    for j in range(h):
        f.extend([-a*h-j-1,-b*h-j-1] for a,b in combinations(range(p),2))
    return p*h,f


def cases():
    out=[]
    for m in (3,4,6,8,9):
        for odd in (True,False):
            n,f,_=prism(m,inconsistent=odd)
            out.append({"id":f"prism_{m}_{int(odd)}","group":"parity",
                        "n":n,"clauses":[list(c) for c in f],"odd":odd})
    for p,h in ((3,2),(3,3),(4,3)):
        n,f=pigeonhole(p,h)
        out.append({"id":f"php_{p}_{h}","group":"pigeonhole","n":n,"clauses":f})
    out.append({"id":"chain64","group":"evaluation","n":64,
                "clauses":[[-i,i+1] for i in range(1,64)]})
    rng=random.Random(SEED)
    for i in range(12):
        n=(9,10,12)[i%3]
        f=[[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
           for _ in range(4*n+2)]
        out.append({"id":f"search_{i:02d}","group":"search","n":n,"clauses":f})
    return out


def _reference(c):
    n,f=c["n"],c["clauses"]
    if c["group"]=="parity":
        p=parity(n,f,budget())
        if p is None:
            raise AssertionError("missing parity reference")
        verify_parity(n,f,p,budget())
        return p["decision"]=="sat",p
    if c["group"]=="evaluation":
        if any(all(x>0 for x in cl) for cl in f):
            raise AssertionError("zero model fails")
        return True,None
    nn,g,_=normalize(n,f)
    return brute(nn,g,budget()),None


def _search_budget():
    return Budget(seconds=10,max_steps=1_500_000,max_cells=200_000)


def row(c):
    n,f=c["n"],c["clauses"]
    nn,g,_=normalize(n,f)
    d=max(map(len,g),default=0)
    sat,ref=_reference(c)
    method="evaluation" if c["group"]=="evaluation" or (c["group"]=="parity" and sat) else "closure"
    r={"case":c,"reference":sat,"reference_proof":ref,"active_variables":nn,
       "degree":d,"dimension":sum(comb(nn,k) for k in range(d+1)),
       "legacy_coordinate_bits":1<<nn,"method":method,"proof":None,
       "status":"resource_exhausted"}
    b=_search_budget()
    try:
        p=evaluation(n,f,b,degree=d,assignment=0) if method=="evaluation" else derive(n,f,b,degree=d)
        verify(n,f,p,budget())
        r.update(proof=p,status=p["status"])
    except Exhausted:
        pass
    r["observed_work"]=b.steps
    check(r)
    return r


def check(r):
    c=r["case"]
    n,f=c["n"],c["clauses"]
    nn,g,_=normalize(n,f)
    d=max(map(len,g),default=0)
    sat,ref=_reference(c)
    if r["reference"] is not sat or r["active_variables"]!=nn or r["degree"]!=d:
        raise ValueError("incorrect reference")
    if c["group"]=="parity":
        p=r["reference_proof"]
        verify_parity(n,f,p,budget())
        if (p["decision"]=="sat")!=sat:
            raise ValueError("parity reference mismatch")
    elif r["reference_proof"] is not None:
        raise ValueError("unexpected reference proof")
    if (r["dimension"]!=sum(comb(nn,k) for k in range(d+1))
            or r["legacy_coordinate_bits"]!=1<<nn
            or type(r["observed_work"]) is not int or not 0<=r["observed_work"]<=1_500_000):
        raise ValueError("invalid representation or work metadata")
    method="evaluation" if c["group"]=="evaluation" or (c["group"]=="parity" and sat) else "closure"
    if r["method"]!=method:
        raise ValueError("incorrect method")
    if r["status"]=="resource_exhausted":
        if r["proof"] is not None:
            raise ValueError("exhausted attempt credited")
    else:
        p=r["proof"]
        if p is None or p["degree"]!=d or p["dimension"]!=r["dimension"] or p["status"]!=r["status"]:
            raise ValueError("proof metadata mismatch")
        verify(n,f,p,budget())
        if p["status"]=="refuted" and sat:
            raise ValueError("false refutation")
        if method=="evaluation" and (p["status"]!="closed_no_refutation" or p["functionals"]!=[1]):
            raise ValueError("incorrect all-zero evaluation certificate")
    if c["group"]=="parity" and r["status"]!=("closed_no_refutation" if sat else "refuted"):
        raise ValueError("parity scaling control failed")
    if c["group"]=="evaluation" and r["status"]!="closed_no_refutation":
        raise ValueError("64-variable scaling control failed")
    return True


def summary(rows):
    return {"cases":len(rows),
            "reference_unsat":sum(not r["reference"] for r in rows),
            "refutations":sum(r["status"]=="refuted" for r in rows),
            "closed_spaces":sum(r["status"]=="closed_no_refutation" for r in rows),
            "unsat_degree_obstructions":sum(not r["reference"] and r["status"]=="closed_no_refutation" for r in rows),
            "resource_exhausted":sum(r["status"]=="resource_exhausted" for r in rows),
            "larger_than_v30":sum(r["active_variables"]>8 and r["proof"] is not None for r in rows),
            "max_verified_variables":max((r["active_variables"] for r in rows if r["proof"] is not None),default=0),
            "max_refuted_variables":max((r["active_variables"] for r in rows if r["status"]=="refuted"),default=0),
            "max_coordinate_dimension":max((r["dimension"] for r in rows),default=0),
            "universal_obligations_closed":0}


def run(*,checkpoint_path=None):
    r={"schema":SCHEMA,"rows":[],"completion":"running",
       "scope":"compressed degree coordinates; finite obstruction search and supplied-model controls",
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
            or r["scope"]!="compressed degree coordinates; finite obstruction search and supplied-model controls"
            or r["universal_obligation"]!="unresolved"
            or any(r[k] is not False for k in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))):
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
