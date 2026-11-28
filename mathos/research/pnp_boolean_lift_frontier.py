"""Audit bounded monomial lifting and a one-wave consequence refinement."""
import argparse
import json
import random
from pathlib import Path
from .pnp_boolean_lift import propose,verify
from .pnp_symbolic_frontier import audit as audit_v28
from .pnp_structural_kernel import normalize,brute,Exhausted
from .pnp_inference_complexity import budget
from .pnp_evidence_benchmark import digest
from .pnp_outcome_registry import decompose
from .pnp_outcome_engine import checkpoint

SCHEMA="mathos-pnp-boolean-lift-frontier/1"
SEED=29029
MODES=(("base",3),("multiply",4))


def cases():
    result=[
        {"id":"strict_relaxation","group":"control","n":3,
         "clauses":[[-1,2],[1,-2],[1,2],[-1,3],[-2,-3]]},
        {"id":"satisfiable_control","group":"control","n":3,
         "clauses":[[1,2],[-1,3]]},
        {"id":"unit_conflict","group":"control","n":1,"clauses":[[1],[-1]]},
        {"id":"empty_clause","group":"control","n":0,"clauses":[[]]},
        {"id":"empty_formula","group":"control","n":3,"clauses":[]},
    ]
    rng=random.Random(SEED)
    for i in range(24):
        n=rng.randint(4,5)
        f=[]
        for _ in range(4*n):
            width=2 if i%2==0 else 3
            f.append([v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),width)])
        result.append({"id":f"fresh_{i:02d}","group":"fresh","n":n,"clauses":f})
    return result


def reference(case):
    n,f,_=normalize(case["n"],case["clauses"])
    return brute(n,f,budget())


def attempt(case,mode,degree):
    n,f=case["n"],case["clauses"]
    b=budget()
    try:
        r=propose(n,f,b,degree=degree,mode=mode)
        verify(n,f,r,budget())
        return {"mode":mode,"degree":degree,"status":"replayed","decision":r["decision"],
                "proof":r,"observed_work":b.steps}
    except Exhausted:
        return {"mode":mode,"degree":degree,"status":"resource_exhausted",
                "decision":"unknown","proof":None,"observed_work":b.steps}


def verify_attempt(case,a,mode,degree):
    if (a["mode"],a["degree"])!=(mode,degree) or type(a["observed_work"]) is not int or not 0<=a["observed_work"]<=4_000_000:
        raise ValueError("invalid attempt metadata")
    if a["status"]=="resource_exhausted":
        if a["proof"] is not None or a["decision"]!="unknown":
            raise ValueError("exhausted attempt credited with a result")
    elif a["status"]=="replayed":
        p=a["proof"]
        if p is None or (p["mode"],p["degree"])!=(mode,degree):
            raise ValueError("missing or misconfigured certificate")
        verify(case["n"],case["clauses"],p,budget())
        if a["decision"]!=p["decision"]:
            raise ValueError("decision mismatch")
    else:
        raise ValueError("unknown attempt status")
    return True


def _check(row):
    c=row["case"]
    ref=reference(c)
    if row["reference"] is not ref or len(row["attempts"])!=2:
        raise ValueError("reference or attempt mismatch")
    for a,(mode,degree) in zip(row["attempts"],MODES):
        verify_attempt(c,a,mode,degree)
        if a["decision"]!="unknown" and (a["decision"]=="sat")!=ref:
            raise ValueError("unsound decision")
    if c["id"]=="strict_relaxation":
        a,b=row["attempts"]
        if (ref or a["status"]!="replayed" or a["decision"]!="unknown"
                or a["proof"]["linear_proof"]["decision"]!="sat"
                or not a["proof"]["inconsistent_products"] or b["decision"]!="unsat"):
            raise ValueError("strict refinement control failed")
    return True


def summary(rows):
    result={"cases":len(rows),"fresh_cases":sum(r["case"]["group"]=="fresh" for r in rows),
            "fresh_reference_unsat":sum(r["case"]["group"]=="fresh" and not r["reference"] for r in rows)}
    for group in ("all","fresh"):
        items=[r for r in rows if group=="all" or r["case"]["group"]=="fresh"]
        s={}
        for j,(mode,_) in enumerate(MODES):
            a=[r["attempts"][j] for r in items]
            s[mode]={"sat":sum(x["decision"]=="sat" for x in a),
                     "unsat":sum(x["decision"]=="unsat" for x in a),
                     "unknown":sum(x["decision"]=="unknown" for x in a),
                     "resource_exhausted":sum(x["status"]=="resource_exhausted" for x in a),
                     "linear_sat_unknown":sum(x["proof"] is not None and x["decision"]=="unknown" for x in a),
                     "rows":sum(len(x["proof"]["rows"]) for x in a if x["proof"] is not None),
                     "columns":sum(len(x["proof"]["monomials"]) for x in a if x["proof"] is not None),
                     "observed_work":sum(x["observed_work"] for x in a)}
        s["multiply_only"]=sum(r["attempts"][0]["decision"]=="unknown" and r["attempts"][1]["decision"]!="unknown" for r in items)
        s["base_only"]=sum(r["attempts"][1]["decision"]=="unknown" and r["attempts"][0]["decision"]!="unknown" for r in items)
        result[group]=s
    return result


def run(simulation,barriers,hypotheses,refinement,symbolic,*,checkpoint_path=None):
    inputs=(simulation,barriers,hypotheses,refinement,symbolic)
    audit_v28(*inputs)
    r={"schema":SCHEMA,"upstream":[digest(x) for x in inputs],"rows":[],
       "completion":"running","universal_obligation":"unresolved",
       "p_equals_np_established":False,"p_not_equals_np_established":False,
       "novel_theorem_verified":False,"barriers":barriers["dossier"]["barriers"],
       "objectives":[decompose(x) for x in ("E01","E02","E09","E10","E12","E19")],
       "scope":"bounded Boolean monomial relaxation with one-wave multiplication; no universal completeness claim"}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        for c in cases():
            row={"case":c,"reference":reference(c),
                 "attempts":[attempt(c,mode,degree) for mode,degree in MODES]}
            _check(row)
            r["rows"].append(row)
            save()
        r["completion"]="completed"
    except Exhausted as e:
        r["completion"],r["reason"]="resource_exhausted",str(e)
    except (ValueError,AssertionError) as e:
        r["completion"],r["reason"]="diagnostic_required",str(e)
    r["summary"]=summary(r["rows"])
    save()
    return r


def audit(simulation,barriers,hypotheses,refinement,symbolic,r):
    inputs=(simulation,barriers,hypotheses,refinement,symbolic)
    audit_v28(*inputs)
    if (r["schema"]!=SCHEMA or r["upstream"]!=[digest(x) for x in inputs]
            or r["completion"]!="completed" or r["universal_obligation"]!="unresolved"
            or r["barriers"]!=barriers["dossier"]["barriers"]
            or any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))
            or digest(r["objectives"])!=digest([decompose(x) for x in ("E01","E02","E09","E10","E12","E19")])
            or r["scope"]!="bounded Boolean monomial relaxation with one-wave multiplication; no universal completeness claim"):
        raise ValueError("report governance mismatch")
    if [x["case"] for x in r["rows"]]!=cases():
        raise ValueError("incomplete evaluation")
    for row in r["rows"]:
        _check(row)
    if r["summary"]!=summary(r["rows"]):
        raise ValueError("summary mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    names=("simulation","barriers","hypotheses","refinement","symbolic")
    for name in names:
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    a=p.parse_args(argv)
    def read(path):
        if path.stat().st_size>32_000_000:
            raise ValueError("oversized report")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        paths=tuple(getattr(a,k) for k in names)
        if a.checkpoint and a.checkpoint.resolve() in {x.resolve() for x in paths}:
            raise ValueError("cannot overwrite upstream")
        inputs=tuple(read(x) for x in paths)
        if a.audit:
            audit(*inputs,read(a.audit))
            print(json.dumps({"status":"replayed","universal_obligation":"unresolved"}))
            return 0
        r=run(*inputs,checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return int(r["completion"]!="completed")
    except (OSError,ValueError,KeyError,TypeError,Exhausted) as e:
        p.error(str(e))


if __name__=="__main__":
    raise SystemExit(main())
