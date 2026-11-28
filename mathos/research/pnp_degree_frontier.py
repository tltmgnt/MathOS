"""Audited adaptive degree closure and independently checked obstructions."""
import argparse
import json
import random
from pathlib import Path

from .pnp_degree_closure import adaptive,verify_adaptive
from .pnp_boolean_lift_frontier import audit as audit_v29,attempt as lift_attempt,verify_attempt
from .pnp_evidence_benchmark import digest
from .pnp_inference_complexity import budget
from .pnp_structural_kernel import normalize,brute,Exhausted
from .pnp_outcome_engine import checkpoint
from .pnp_outcome_registry import decompose

SCHEMA="mathos-pnp-degree-frontier/1"
SEED=30030


def cases():
    out=[{"id":"empty","n":0,"clauses":[]},
         {"id":"empty_conflict","n":0,"clauses":[[]]},
         {"id":"chain_conflict","n":5,"clauses":[[1],[-1,2],[-2,3],[-3,4],[-4,5],[-5]]},
         {"id":"strict_lift","n":3,"clauses":[[-1,2],[1,-2],[1,2],[-1,3],[-2,-3]]},
         {"id":"sat_clause","n":3,"clauses":[[1,2,3]]},
         {"id":"sat_mixed","n":4,"clauses":[[1,2],[-1,3],[-2,-3,4]]}]
    rng=random.Random(SEED)
    for i in range(24):
        n=rng.randint(4,5)
        f=[]
        for _ in range(4*n):
            vs=rng.sample(range(1,n+1),2+i%2)
            f.append([v if rng.randrange(2) else -v for v in vs])
        out.append({"id":f"fresh_{i:02d}","n":n,"clauses":f})
    return out


def reference(c):
    n,f,_=normalize(c["n"],c["clauses"])
    return brute(n,f,budget())


def _check(row):
    c=row["case"]
    n,f=c["n"],c["clauses"]
    sat=reference(c)
    if row["reference"] is not sat:
        raise ValueError("reference mismatch")
    verify_attempt(c,row["one_wave"],"multiply",4)
    if row["one_wave"]["decision"]!="unknown" and (row["one_wave"]["decision"]=="sat")!=sat:
        raise ValueError("one-wave decision disagrees with reference")
    a=row["attempts"]
    verify_adaptive(n,f,a,budget)
    last=a[-1]
    if last["status"]=="refuted" and sat:
        raise ValueError("refutation of satisfiable formula")
    if last["status"]=="closed_no_refutation" and not sat:
        raise ValueError("full-degree closure contradicts reference")
    return True


def summary(rows):
    return {"cases":len(rows),"reference_unsat":sum(not r["reference"] for r in rows),
            "one_wave_refutations":sum(r["one_wave"]["decision"]=="unsat" for r in rows),
            "adaptive_refutations":sum(r["attempts"][-1]["status"]=="refuted" for r in rows),
            "adaptive_only_refutations":sum(r["attempts"][-1]["status"]=="refuted" and r["one_wave"]["decision"]!="unsat" for r in rows),
            "one_wave_only_refutations":sum(r["one_wave"]["decision"]=="unsat" and r["attempts"][-1]["status"]!="refuted" for r in rows),
            "closed_spaces":sum(a["status"]=="closed_no_refutation" for r in rows for a in r["attempts"]),
            "certified_unsat_degree_obstructions":sum(a["status"]=="closed_no_refutation" for r in rows if not r["reference"] for a in r["attempts"]),
            "minimum_degree_certificates":sum(r["attempts"][-1]["status"]=="refuted" for r in rows),
            "resource_exhausted":sum(r["attempts"][-1]["status"]=="resource_exhausted" for r in rows),
            "inference_records":sum(len(a["proof"]["steps"]) for r in rows for a in r["attempts"] if a["proof"] is not None),
            "universal_obligations_closed":0}


def run(simulation,barriers,hypotheses,refinement,symbolic,lifting,*,checkpoint_path=None):
    inputs=(simulation,barriers,hypotheses,refinement,symbolic,lifting)
    audit_v29(*inputs)
    r={"schema":SCHEMA,"upstream":[digest(x) for x in inputs],"rows":[],
       "completion":"running","universal_obligation":"unresolved",
       "p_equals_np_established":False,"p_not_equals_np_established":False,
       "novel_theorem_verified":False,"barriers":barriers["dossier"]["barriers"],
       "objectives":[decompose(x) for x in ("E01","E02","E08","E10","E19")],
       "scope":"square-free Boolean polynomial calculus; degree measured after Boolean reduction"}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        for c in cases():
            row={"case":c,"reference":reference(c),"one_wave":lift_attempt(c,"multiply",4),
                 "attempts":adaptive(c["n"],c["clauses"],budget)}
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


def audit(simulation,barriers,hypotheses,refinement,symbolic,lifting,r):
    inputs=(simulation,barriers,hypotheses,refinement,symbolic,lifting)
    audit_v29(*inputs)
    if (r["schema"]!=SCHEMA or r["upstream"]!=[digest(x) for x in inputs]
            or r["completion"]!="completed" or r["universal_obligation"]!="unresolved"
            or r["barriers"]!=barriers["dossier"]["barriers"]
            or any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))
            or digest(r["objectives"])!=digest([decompose(x) for x in ("E01","E02","E08","E10","E19")])
            or r["scope"]!="square-free Boolean polynomial calculus; degree measured after Boolean reduction"):
        raise ValueError("invalid report governance")
    if [x["case"] for x in r["rows"]]!=cases():
        raise ValueError("incomplete evaluation")
    for row in r["rows"]:
        _check(row)
    if r["summary"]!=summary(r["rows"]):
        raise ValueError("summary mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    names=("simulation","barriers","hypotheses","refinement","symbolic","lifting")
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
