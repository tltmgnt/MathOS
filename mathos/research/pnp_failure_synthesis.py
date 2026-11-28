"""Investigate audited v12 failures; synthesize a bounded refutation policy.

The previous holdout is now development evidence. Evaluation uses a new
seeded suite; no new evaluation rows enter policy selection.
"""
import argparse
import json
import random
from pathlib import Path
from .pnp_evidence_benchmark import audit as audit_source, digest
from .pnp_evidence_scheduler import audit as audit_scheduler
from .pnp_structural_kernel import Budget, Exhausted, normalize, brute
from .pnp_resolution_refutation import STRATEGIES, propose, verify
from .pnp_outcome_engine import checkpoint

GRAMMAR=tuple((s,w) for w in (3,5,8) for s in STRATEGIES)
EVAL_SEED=13013


def attempt(n,f,plan,steps):
    strategy,width=plan
    b=Budget(seconds=5,max_steps=steps,max_cells=50_000)
    try:
        proof=propose(n,f,b,width=width,records=8192,strategy=strategy)
        status="refuted" if proof is not None else "unrecognized"
        if proof is not None:
            verify(n,f,proof,Budget(seconds=5,max_steps=2_000_000,max_cells=50_000))
    except Exhausted:
        proof,status=None,"resource_exhausted"
    return {"plan":list(plan),"status":status,"proof":proof,"work_steps":b.steps}


def minimize_unsat(n,f,steps,limit=128):
    """Deletion-minimize UNSAT by exhaustive reference, not portfolio failure."""
    nn,local,_=normalize(n,f)
    b=Budget(seconds=15,max_steps=20_000_000)
    if brute(nn,local,b):
        raise ValueError("UNSAT minimization requires an UNSAT input")
    original=len(local)
    i=trials=0
    while i<len(local) and trials<limit:
        candidate=local[:i]+local[i+1:]
        trials+=1
        m,g,_=normalize(nn,candidate)
        if not brute(m,g,b):
            local=candidate
            i=0
        else:
            i+=1
    m,g,mapping=normalize(nn,local)
    return {"n":m,"clauses":g,"original_clause_count":original,
            "trials":trials,"deletion_minimal":i==len(local),
            "scope":"UNSAT only; does not preserve previous portfolio failure"}


def fresh_cases(seed=EVAL_SEED,count=24):
    # The orbit-disjoint frontier screens a bounded pool of 96 per family.
    # Preserve the seeded stream and existing smaller evaluation suites.
    if type(seed) is not int or not 0<=seed<2**31 or type(count) is not int or not 1<=count<=96:
        raise ValueError("invalid evaluation configuration")
    rng=random.Random(seed)
    result=[]
    for i in range(count):
        n=rng.randint(5,9)
        # Pure 3-CNF near the usual random satisfiability transition;
        # finite generator only, not a representative hardness distribution.
        f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3))
           for _ in range(4*n+rng.randint(0,n))]
        result.append({"id":f"fresh_{i:02d}","n":n,"clauses":[list(c) for c in f]})
    return result


def _select(rows):
    # Maximize refuted original failures, then minimize observed work.
    # A minimized core is explanatory only, not a training/evaluation row.
    def score(i):
        attempts=[r["attempts"][i] for r in rows]
        return (-sum(a["status"]=="refuted" for a in attempts),
                sum(a["work_steps"] for a in attempts),i)
    return list(GRAMMAR[min(range(len(GRAMMAR)),key=score)])


def _reference(n,f):
    nn,g,_=normalize(n,f)
    return brute(nn,g,Budget(seconds=10,max_steps=2_000_000))


def run(source,scheduler,*,steps=100_000,seed=EVAL_SEED,count=24,checkpoint_path=None):
    if type(steps) is not int or not 1<=steps<=2_000_000:
        raise ValueError("invalid per-attempt budget")
    if not audit_source(source)["complete"] or not audit_scheduler(source,scheduler)["complete"]:
        raise ValueError("complete audited evidence required")
    old_ids={q["case_id"] for q in scheduler["summary"]["research_queue"]}
    # Include union failures from v11 even if a scheduler had a different budget.
    targets=[r for r in source["rows"] if r["case"]["id"] in old_ids or
             all(p["report"]["decision"]=="unknown" for p in r["plans"])]
    result={"schema":"mathos-pnp-failure-synthesis/1","source_sha256":digest(source),
            "scheduler_sha256":digest(scheduler),"steps":steps,"seed":seed,"count":count,
            "training":[],"evaluation":[],"completion":"running",
            "universal_obligation":"unresolved","p_equals_np_established":False,
            "p_not_equals_np_established":False,"novel_theorem_verified":False}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,result)
    try:
        save()
        for row in targets:
            case=row["case"]
            n,f=case["n"],case["clauses"]
            attempts=[attempt(n,f,p,steps) for p in GRAMMAR]
            if row["reference"] and any(a["status"]=="refuted" for a in attempts):
                raise AssertionError("refutation contradicts reference")
            core=None if row["reference"] else minimize_unsat(n,f,steps)
            result["training"].append({"case":case,"reference":row["reference"],
                                       "attempts":attempts,"minimized_unsat":core})
            save()
        plan=_select(result["training"])
        result["selected_plan"]=plan
        # Same generated cases and quotas for selected and fixed baseline.
        for case in fresh_cases(seed,count):
            n,f=case["n"],case["clauses"]
            ref=_reference(n,f)
            a=attempt(n,f,plan,steps)
            baseline=attempt(n,f,("min_product",5),steps)
            if ref and (a["status"]=="refuted" or baseline["status"]=="refuted"):
                raise AssertionError("fresh refutation contradicts reference")
            result["evaluation"].append({"case":case,"reference":ref,"selected":a,"baseline":baseline})
            save()
        result["completion"]="completed"
    except Exhausted as exc:
        result["completion"],result["reason"]="resource_exhausted",str(exc)
    except (AssertionError,ValueError) as exc:
        result["completion"],result["reason"]="diagnostic_required",str(exc)
    result["summary"]=summarize(result)
    save()
    return result


def summarize(r):
    training=r["training"]
    evaluation=r["evaluation"]
    plan=r.get("selected_plan")
    index=GRAMMAR.index(tuple(plan)) if plan else None
    return {"training_cases":len(training),
            "training_refuted_by_any":sum(any(a["status"]=="refuted" for a in x["attempts"]) for x in training),
            "training_refuted_by_selected":sum(x["attempts"][index]["status"]=="refuted" for x in training) if index is not None else 0,
            "fresh_cases":len(evaluation),"fresh_reference_unsat":sum(not x["reference"] for x in evaluation),
            "fresh_selected_refuted":sum(x["selected"]["status"]=="refuted" for x in evaluation),
            "fresh_baseline_refuted":sum(x["baseline"]["status"]=="refuted" for x in evaluation),
            "unresolved_training_ids":[x["case"]["id"] for x in training if index is None or x["attempts"][index]["status"]!="refuted"]}


def _check_attempt(n,f,a,plan,steps,reference):
    if (a["plan"]!=list(plan) or type(a["work_steps"]) is not int or
            not 0<=a["work_steps"]<=steps or a["status"] not in
            ("refuted","unrecognized","resource_exhausted")):
        raise ValueError("invalid attempt")
    p=a["proof"]
    if a["status"]=="refuted":
        if reference or p is None or (p["strategy"],p["width_cap"])!=tuple(plan) or p["record_cap"]!=8192:
            raise ValueError("incorrect refutation metadata")
        verify(n,f,p,Budget(seconds=5,max_steps=2_000_000,max_cells=50_000))
    elif p is not None:
        raise ValueError("unknown attempt cannot contain credited proof")


def audit(source,scheduler,r):
    if not audit_source(source)["complete"] or not audit_scheduler(source,scheduler)["complete"]:
        raise ValueError("incomplete upstream evidence")
    if (r["schema"]!="mathos-pnp-failure-synthesis/1" or r["source_sha256"]!=digest(source) or
            r["scheduler_sha256"]!=digest(scheduler) or r["universal_obligation"]!="unresolved" or
            any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified")) or
            r["completion"]!="completed" or type(r["steps"]) is not int or not 1<=r["steps"]<=2_000_000):
        raise ValueError("invalid report metadata")
    old_ids={q["case_id"] for q in scheduler["summary"]["research_queue"]}
    targets=[x for x in source["rows"] if x["case"]["id"] in old_ids or
             all(p["report"]["decision"]=="unknown" for p in x["plans"])]
    if len(targets)!=len(r["training"]):
        raise ValueError("missing training cases")
    for row,expected in zip(r["training"],targets):
        if row["case"]!=expected["case"] or row["reference"] is not expected["reference"] or len(row["attempts"])!=len(GRAMMAR):
            raise ValueError("training case mismatch")
        n,f=row["case"]["n"],row["case"]["clauses"]
        for a,p in zip(row["attempts"],GRAMMAR):
            _check_attempt(n,f,a,p,r["steps"],row["reference"])
        core=None if row["reference"] else minimize_unsat(n,f,r["steps"])
        if digest(core)!=digest(row["minimized_unsat"]):
            raise ValueError("minimization replay mismatch")
    plan=_select(r["training"])
    if r["selected_plan"]!=plan:
        raise ValueError("policy mismatch")
    cases=fresh_cases(r["seed"],r["count"])
    if len(cases)!=len(r["evaluation"]):
        raise ValueError("missing evaluation cases")
    for row,case in zip(r["evaluation"],cases):
        n,f=case["n"],case["clauses"]
        if row["case"]!=case or row["reference"] is not _reference(n,f):
            raise ValueError("evaluation reference mismatch")
        _check_attempt(n,f,row["selected"],plan,r["steps"],row["reference"])
        _check_attempt(n,f,row["baseline"],("min_product",5),r["steps"],row["reference"])
    if r["summary"]!=summarize(r):
        raise ValueError("summary mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--benchmark",type=Path,required=True)
    p.add_argument("--scheduler",type=Path,required=True)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    p.add_argument("--steps",type=int,default=100_000)
    p.add_argument("--seed",type=int,default=EVAL_SEED)
    p.add_argument("--count",type=int,default=24)
    a=p.parse_args(argv)
    def read(path):
        if path.stat().st_size>32_000_000:
            raise ValueError("JSON exceeds 32 MB")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        source,scheduler=read(a.benchmark),read(a.scheduler)
        if a.audit:
            audit(source,scheduler,read(a.audit))
            print(json.dumps({"status":"replayed","universal_obligation":"unresolved"}))
            return 0
        if a.checkpoint and a.checkpoint.resolve() in (a.benchmark.resolve(),a.scheduler.resolve()):
            raise ValueError("cannot overwrite upstream evidence")
        r=run(source,scheduler,steps=a.steps,seed=a.seed,count=a.count,checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return int(r["completion"]!="completed")
    except (OSError,ValueError,KeyError,TypeError,Exhausted) as exc:
        p.error(str(exc))


if __name__=="__main__":
    raise SystemExit(main())
