"""Reproducible finite benchmark and independent evidence audit for v10."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import time

from .pnp_structural_kernel import Budget, Exhausted, brute, normalize
from .pnp_unified_portfolio import DEFAULT_PLANS, run, verify_report
from .pnp_outcome_engine import checkpoint
from .pnp_recursive_frontier import family as hub_family
from .pnp_triple_parity import signed_family
from .pnp_algebra_frontier import xor_block

VERSION = "mathos-pnp-benchmark/1"
CONFIG = {"depth": 4, "nodes": 1024, "k": 2, "cap": 4}
MAX_CASES = 64


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("ascii")).hexdigest()


def manifest(seed=11011, random_count=24):
    if type(seed) is not int or not 0 <= seed < 2**31:
        raise ValueError("invalid seed")
    if type(random_count) is not int or not 0 <= random_count <= 48:
        raise ValueError("invalid random count")
    cases=[]
    def add(name, group, n, f):
        cases.append({"id":name,"group":group,"n":n,"clauses":[list(c) for c in f]})
    add("binary_cycle","structured",3,[(1,2),(-1,2),(1,-2),(-1,-2)])
    add("horn_chain","structured",5,[(1,),(-1,2),(-2,3),(-3,4),(-4,5),(-5,)])
    add("renamable","structured",4,[(1,),(-2,),(-1,3,4),(-4,-3)])
    add("parity_sat","structured",6,signed_family(6))
    add("parity_unsat","structured",6,signed_family(6,inconsistent=True))
    add("affine","structured",6,xor_block((1,2,3),0)+xor_block((3,4,5,6),1))
    add("hub","structured",10,hub_family(3))
    add("hub_conflict","structured",10,hub_family(3)+[(1,),(-1,)])
    add("wide_or","structured",9,[tuple(range(1,10))])
    add("empty","structured",0,[])
    add("empty_clause","structured",0,[()])
    # Independent reference for ALL cases: no planted label used as truth.
    # Stratification is by generation method, not by actual SAT decision.
    for group,s in (("development",seed),("holdout",seed^0x6B31)):
        rng=random.Random(s)
        for i in range(random_count//2 if group=="development" else random_count-random_count//2):
            n=rng.randint(4,9)
            f=[]
            for _ in range(rng.randint(n,5*n)):
                size=rng.randint(2,min(n,4))
                f.append(tuple(v if rng.randrange(2) else -v
                               for v in rng.sample(range(1,n+1),size)))
            add(f"{group}_{i:02d}",group,n,f)
    return cases


def _quota(steps, seconds):
    if type(steps) is not int or not 1<=steps<=2_000_000:
        raise ValueError("per-plan work quota must be 1..2000000")
    if type(seconds) not in (int,float) or not 0<seconds<=60:
        raise ValueError("per-plan seconds must be in (0,60]")


def _plan_id(plan):
    return "/".join(plan)


def _metrics(rows):
    ids=[_plan_id(p) for p in DEFAULT_PLANS]
    by_plan={p:{"decided":0,"sat":0,"unsat":0,"unknown":0,"exhausted":0,
                "unique":0,"work_steps":0,"certificate_bytes":0,"replay_steps":0}
             for p in ids}
    groups={}
    solved=0
    for row in rows:
        g=groups.setdefault(row["case"]["group"],{"cases":0,"decided":0,"reference_sat":0,"reference_unsat":0})
        g["cases"]+=1
        g["reference_sat" if row["reference"] else "reference_unsat"]+=1
        known=[]
        for p in row["plans"]:
            e=p["report"]["entries"][0]
            key=_plan_id(e["plan"])
            s=by_plan[key]
            d=e["decision"]
            s[d]+=1
            s["exhausted"]+=e["status"]=="resource_exhausted"
            s["work_steps"]+=e["work_steps"]
            s["replay_steps"]+=p["replay_steps"]
            s["certificate_bytes"]+=len(canonical({"reduction":e["reduction"],"proof":e["proof"]}).encode("ascii")) if e["proof"] is not None else 0
            if d!="unknown":
                known.append(key)
                s["decided"]+=1
        if known:
            solved+=1
            g["decided"]+=1
        if len(known)==1:
            by_plan[known[0]]["unique"]+=1
    for s in by_plan.values():
        s["coverage_without_plan"]=solved-s["unique"]
    return {"cases":len(rows),"portfolio_union_decided":solved,
            "portfolio_union_unknown":len(rows)-solved,"groups":groups,"plans":by_plan}


def benchmark(*,seed=11011,random_count=24,steps=100_000,seconds=5,checkpoint_path=None):
    _quota(steps,seconds)
    cases=manifest(seed,random_count)
    r={"schema":VERSION,"seed":seed,"random_count":random_count,
       "manifest_sha256":digest(cases),"options":CONFIG.copy(),
       "per_plan_steps":steps,"per_plan_seconds":seconds,"rows":[],
       "completion":"running","universal_obligation":"unresolved",
       "p_equals_np_established":False,"p_not_equals_np_established":False,
       "novel_theorem_verified":False,
       "scope":"finite independent single-plan runs; union is not a timed portfolio run"}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        save()
        for case in cases:
            n,f=case["n"],case["clauses"]
            nn,nf,_=normalize(n,f)
            ref=brute(nn,nf,Budget(seconds=10,max_steps=2_000_000))
            row={"case":case,"reference":ref,"plans":[]}
            for plan in DEFAULT_PLANS:
                b=Budget(seconds=seconds,max_steps=steps,max_cells=200_000)
                start=time.perf_counter_ns()
                report=run(n,f,b,plans=(plan,),**CONFIG)
                elapsed=time.perf_counter_ns()-start
                replay=Budget(seconds=10,max_steps=4_000_000,max_cells=200_000)
                verify_report(n,f,report,replay)
                if report["decision"]!="unknown" and (report["decision"]=="sat")!=ref:
                    raise AssertionError("decision disagrees with independent reference")
                row["plans"].append({"report":report,"elapsed_ns":elapsed,"replay_steps":replay.steps})
            r["rows"].append(row)
            save()
        r["completion"]="completed"
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except (AssertionError,ValueError) as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["metrics"]=_metrics(r["rows"])
    save()
    return r


def audit(report):
    """Reconstruct manifest, reference decisions, proof replay and aggregates.

    Timings and search work counters are observations, not proof-certified.
    Replay steps are checked on the same implementation. A partial report
    can be audited, but cannot be mislabeled complete.
    """
    if (report["schema"]!=VERSION or report["universal_obligation"]!="unresolved" or
            any(report[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))):
        raise ValueError("invalid benchmark governance")
    steps,seconds=report["per_plan_steps"],report["per_plan_seconds"]
    _quota(steps,seconds)
    cases=manifest(report["seed"],report["random_count"])
    rows=report["rows"]
    if (report["manifest_sha256"]!=digest(cases) or report["options"]!=CONFIG or
            len(rows)>len(cases) or report["completion"] not in ("completed","resource_exhausted","diagnostic_required") or
            (report["completion"]=="completed" and len(rows)!=len(cases))):
        raise ValueError("manifest or completion mismatch")
    for case,row in zip(cases,rows):
        if row["case"]!=case or len(row["plans"])!=len(DEFAULT_PLANS):
            raise ValueError("case or plan coverage mismatch")
        n,f=case["n"],case["clauses"]
        nn,nf,_=normalize(n,f)
        ref=brute(nn,nf,Budget(seconds=10,max_steps=2_000_000))
        if row["reference"] is not ref:
            raise ValueError("reference mismatch")
        for plan,p in zip(DEFAULT_PLANS,row["plans"]):
            r=p["report"]
            if ([list(x) for x in r["plans"]]!=[list(plan)] or r["options"]!=CONFIG or
                    r["per_plan_work_quota"]!=steps or type(p["elapsed_ns"]) is not int or p["elapsed_ns"]<0):
                raise ValueError("plan configuration mismatch")
            e=r["entries"][0]
            if type(e["work_steps"]) is not int or not 0<=e["work_steps"]<=steps or r["work_steps"]!=e["work_steps"]:
                raise ValueError("invalid observed work accounting")
            replay=Budget(seconds=10,max_steps=4_000_000,max_cells=200_000)
            verify_report(n,f,r,replay)
            if p["replay_steps"]!=replay.steps:
                raise ValueError("replay work mismatch")
            if r["decision"]!="unknown" and (r["decision"]=="sat")!=ref:
                raise ValueError("reference decision mismatch")
    if report["metrics"]!=_metrics(rows):
        raise ValueError("aggregate mismatch")
    return {"status":"replayed","cases":len(rows),"complete":report["completion"]=="completed",
            "timings_and_search_work_certified":False,"universal_obligation":"unresolved"}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed",type=int,default=11011)
    p.add_argument("--random-count",type=int,default=24)
    p.add_argument("--steps",type=int,default=100_000)
    p.add_argument("--seconds",type=float,default=5)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    a=p.parse_args(argv)
    try:
        if a.audit:
            if a.audit.stat().st_size>32_000_000:
                raise ValueError("report exceeds 32 MB")
            result=audit(json.loads(a.audit.read_text(encoding="utf-8")))
            print(json.dumps(result,indent=2,sort_keys=True))
            return int(not result["complete"])
        r=benchmark(seed=a.seed,random_count=a.random_count,steps=a.steps,seconds=a.seconds,checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return int(r["completion"]!="completed")
    except (OSError,ValueError,KeyError,TypeError,Exhausted) as exc:
        p.error(str(exc))


if __name__=="__main__":
    raise SystemExit(main())
