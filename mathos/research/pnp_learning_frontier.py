"""Fresh paired evaluation of v14 certified learning and the v12 scheduler."""
import argparse
import json
from pathlib import Path
from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train, execute, replay
from .pnp_failure_synthesis import audit as audit_v13, fresh_cases
from .pnp_structural_kernel import Budget, Exhausted, normalize, brute
from .pnp_certified_learning import solve, verify_hybrid, _options
from .pnp_outcome_engine import checkpoint

SEED=14014


def reference(n,f):
    nn,nf,_=normalize(n,f)
    return brute(nn,nf,Budget(seconds=10,max_steps=2_000_000))


def summary(rows):
    out={"cases":len(rows),"reference_sat":sum(r["reference"] for r in rows),
         "reference_unsat":sum(not r["reference"] for r in rows),
         "baseline":{"sat":0,"unsat":0,"unknown":0,"work_steps":0},
         "hybrid":{"sat":0,"unsat":0,"unknown":0,"work_steps":0},
         "hybrid_only":0,"baseline_only":0,"both_unknown":0,"both_decided":0,
         "learned_clauses":0,"learning_phase_cases":0,"refutation_phase_decisions":0,
         "unresolved_ids":[]}
    for r in rows:
        b,h=r["baseline"],r["hybrid"]
        for name,a in (("baseline",b),("hybrid",h)):
            out[name][a["decision"]]+=1
            out[name]["work_steps"]+=a["work_steps"]
        bd,hd=b["decision"]!="unknown",h["decision"]!="unknown"
        out["both_decided" if bd and hd else "baseline_only" if bd else "hybrid_only" if hd else "both_unknown"]+=1
        out["learned_clauses"]+=h["learned_clauses"]
        out["learning_phase_cases"]+=h["final"] is not None
        out["refutation_phase_decisions"]+=h["refutation"] is not None and h["refutation"]["status"]=="refuted"
        if not hd:
            out["unresolved_ids"].append(r["case"]["id"])
    return out


def run(source,scheduler,failures,*,total=100_000,seconds=5,probes=16,seed=SEED,count=24,checkpoint_path=None):
    audit_v13(source,scheduler,failures)
    policy=train(source)
    plan=failures["selected_plan"]
    _options(plan,total,seconds,probes)
    if seed==failures["seed"]:
        raise ValueError("evaluation seed must differ from v13")
    cases=fresh_cases(seed,count)
    r={"schema":"mathos-pnp-learning-frontier/1",
       "upstream":[digest(x) for x in (source,scheduler,failures)],"policy":policy,
       "resolution_plan":plan,"options":{"total":total,"seconds":seconds,"probes":probes},
       "seed":seed,"count":count,"rows":[],"completion":"running",
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        save()
        for i,case in enumerate(cases):
            n,f=case["n"],case["clauses"]
            ref=reference(n,f)
            entry={"case":case,"reference":ref}
            for arm in (("baseline","hybrid") if i%2==0 else ("hybrid","baseline")):
                if arm=="baseline":
                    a=execute(n,f,policy,"learned",total,seconds)
                    replay(n,f,policy,total,a)
                else:
                    a=solve(n,f,policy,plan,total=total,seconds=seconds,probes=probes)
                if a["decision"]!="unknown" and (a["decision"]=="sat")!=ref:
                    raise AssertionError("decision contradicts independent reference")
                entry[arm]=a
            r["rows"].append(entry)
            save()
        r["completion"]="completed"
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except (AssertionError,ValueError) as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["summary"]=summary(r["rows"])
    save()
    return r


def audit(source,scheduler,failures,r):
    audit_v13(source,scheduler,failures)
    policy=train(source)
    plan=failures["selected_plan"]
    total,seconds,probes=(r["options"][k] for k in ("total","seconds","probes"))
    _options(plan,total,seconds,probes)
    if (r["schema"]!="mathos-pnp-learning-frontier/1" or
            r["upstream"]!=[digest(x) for x in (source,scheduler,failures)] or
            r["policy"]!=policy or r["resolution_plan"]!=plan or
            r["completion"]!="completed" or r["seed"]==failures["seed"] or
            r["universal_obligation"]!="unresolved" or
            any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))):
        raise ValueError("source or governance mismatch")
    cases=fresh_cases(r["seed"],r["count"])
    if len(cases)!=len(r["rows"]):
        raise ValueError("missing evaluation cases")
    for case,row in zip(cases,r["rows"]):
        n,f=case["n"],case["clauses"]
        if row["case"]!=case or row["reference"] is not reference(n,f):
            raise ValueError("evaluation reference mismatch")
        b,h=row["baseline"],row["hybrid"]
        if (b["arm"]!="learned" or h["plan"]!=plan or h["total_steps"]!=total or
                h["seconds"]!=seconds or h["probe_limit"]!=probes):
            raise ValueError("evaluation configuration mismatch")
        replay(n,f,policy,total,b)
        verify_hybrid(n,f,policy,h)
        for a in (b,h):
            if a["decision"]!="unknown" and (a["decision"]=="sat")!=row["reference"]:
                raise ValueError("reference decision mismatch")
    if r["summary"]!=summary(r["rows"]):
        raise ValueError("aggregate mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("benchmark","scheduler","failures"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    p.add_argument("--total-steps",type=int,default=100_000)
    p.add_argument("--seconds",type=float,default=5)
    p.add_argument("--probes",type=int,default=16)
    p.add_argument("--seed",type=int,default=SEED)
    p.add_argument("--count",type=int,default=24)
    a=p.parse_args(argv)
    def read(path):
        if path.stat().st_size>32_000_000:
            raise ValueError("JSON exceeds 32 MB")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        inputs=(read(a.benchmark),read(a.scheduler),read(a.failures))
        if a.audit:
            audit(*inputs,read(a.audit))
            print(json.dumps({"status":"replayed","universal_obligation":"unresolved"}))
            return 0
        if a.checkpoint and a.checkpoint.resolve() in {p.resolve() for p in (a.benchmark,a.scheduler,a.failures)}:
            raise ValueError("cannot overwrite upstream evidence")
        r=run(*inputs,total=a.total_steps,seconds=a.seconds,probes=a.probes,seed=a.seed,count=a.count,checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return int(r["completion"]!="completed")
    except (OSError,ValueError,KeyError,TypeError,Exhausted) as exc:
        p.error(str(exc))


if __name__=="__main__":
    raise SystemExit(main())
