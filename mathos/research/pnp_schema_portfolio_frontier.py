"""v17.6 shared-budget portfolio and cross-schema handoff evaluation."""
import argparse
from collections import Counter
import json
from pathlib import Path
from time import perf_counter

from .pnp_library_frontier import audit as audit_v17, case_key
from .pnp_library_ablation import independent_replay, oracle
from .pnp_composite_paths_frontier import splits as prior_splits
from .pnp_signed_horn_frontier import fresh as prior_horn
from .pnp_library_frontier import suite
from .pnp_proof_library import Index, reuse, reconstruct
from .pnp_composite_paths import propose as composite, verify_recipe
from .pnp_schema_portfolio import solve, verify
from .pnp_structural_kernel import Budget
from .pnp_evidence_benchmark import digest
from .pnp_abstraction_frontier import bytesize

SEED=17603
ARMS=("library","composite","sequential","cooperative")
STEPS=4_000_000


def budget():
    return Budget(seconds=15,max_steps=STEPS,max_cells=100000)


def splits(source,failures,v17):
    if failures["seed"]==SEED:
        raise ValueError("seed overlap")
    previous=prior_splits(source,failures,v17)["fresh"]
    seen={case_key(c) for c in previous+prior_horn()}
    from .pnp_implication_paths_frontier import fresh_cases
    seen.update(case_key(c) for c in fresh_cases())
    seen.update(case_key(c) for seed in (17103,17203) for c in suite(seed,24))
    for rows in (source["rows"],failures["training"],failures["evaluation"],
                 v17["training"],v17["discovery"],v17["heldout"],v17["retrospective"]):
        seen.update(case_key(r["case"]) for r in rows)
    fresh=suite(SEED,24)
    # Independent mixed-width generator; no planted units or templates.
    import random
    rng=random.Random(SEED+200000)
    for i in range(24):
        n=rng.randint(5,9)
        f=[]
        for _ in range(3*n):
            w=rng.choices((1,2,3,4),weights=(1,3,5,1))[0]
            f.append([v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),w)])
        fresh.append({"id":f"mixed_{i:02d}","family":"mixed1234","n":n,"clauses":f})
    keys={case_key(c) for c in fresh}
    if len(keys)!=len(fresh) or keys & seen:
        raise ValueError("duplicate normalized input")
    return {"fresh":fresh,"retrospective":previous}


def evaluate(c,index):
    n,f=c["n"],c["clauses"]
    results={}
    offset=int(case_key(c)[:8],16)%len(ARMS)
    for a in ARMS[offset:]+ARMS[:offset]:
        b=budget()
        start=perf_counter()
        if a=="library":
            r=reuse(n,f,index,b,shared_replay=True)
        elif a=="composite":
            r=composite(n,f,b)
        else:
            r=solve(n,f,index,b,cooperate=a=="cooperative")
        r.update(work=b.steps,seconds=perf_counter()-start)
        if r["status"]=="verified":
            start=perf_counter()
            independent_replay(n,f,r["proof"])
            r.update(check_seconds=perf_counter()-start,proof_bytes=bytesize(r["proof"]))
        results[a]=r
    sat=oracle(n,f)
    if sat and any(r["status"]=="verified" for r in results.values()):
        raise AssertionError("false refutation")
    return {"case":c,"reference_sat":sat,"arms":results}


def summary(rows):
    result={"cases":len(rows),"unsat":sum(not r["reference_sat"] for r in rows),"arms":{}}
    for a in ARMS:
        values=[r["arms"][a] for r in rows]
        hits=[v for v in values if v["status"]=="verified"]
        result["arms"][a]={"verified":len(hits),"statuses":dict(Counter(v["status"] for v in values)),
                           "work":sum(v["work"] for v in values),"seconds":sum(v["seconds"] for v in values),
                           "check_seconds":sum(v["check_seconds"] for v in hits),
                           "proof_bytes":sum(v["proof_bytes"] for v in hits)}
        if a in ("sequential","cooperative"):
            result["arms"][a]["proof_kinds"]=dict(Counter(v["recipe"]["kind"] for v in hits))
    result["contrasts"]={}
    for a in ("library","composite","sequential"):
        pairs=[(r["arms"][a]["status"]=="verified",r["arms"]["cooperative"]["status"]=="verified") for r in rows]
        result["contrasts"][a+" -> cooperative"]={"gain":sum(not x and y for x,y in pairs),
                "loss":sum(x and not y for x,y in pairs),"both":sum(x and y for x,y in pairs)}
    result["unique_cooperative"]=sum(r["arms"]["cooperative"]["status"]=="verified" and
                      all(r["arms"][a]["status"]!="verified" for a in ARMS[:-1]) for r in rows)
    return result


def summarize(data):
    s={k:summary(v) for k,v in data.items()}
    for fam in ("random2","random3","mixed1234"):
        s[fam]=summary([r for r in data["fresh"] if r["case"]["family"]==fam])
    return s


def run(source,scheduler,failures,v17):
    audit_v17(source,scheduler,failures,v17)
    index=Index(v17["library"])
    frozen=digest(index.templates)
    data={k:[evaluate(c,index) for c in cases] for k,cases in splits(source,failures,v17).items()}
    if digest(index.templates)!=frozen:
        raise AssertionError("library mutation")
    return {"schema":"mathos-pnp-schema-portfolio-frontier/1","seed":SEED,"step_cap":STEPS,
            "upstream":[digest(x) for x in (source,scheduler,failures,v17)],"library_sha256":frozen,
            "data":data,"summary":summarize(data),"universal_obligation":"unresolved",
            "novel_theorem_verified":False,"p_equals_np_established":False,"p_not_equals_np_established":False}


def audit(source,scheduler,failures,v17,r):
    audit_v17(source,scheduler,failures,v17)
    index=Index(v17["library"])
    if (r["schema"]!="mathos-pnp-schema-portfolio-frontier/1" or r["seed"]!=SEED
            or r["step_cap"]!=STEPS or r["library_sha256"]!=digest(index.templates)
            or r["upstream"]!=[digest(x) for x in (source,scheduler,failures,v17)]
            or r["universal_obligation"]!="unresolved"
            or any(r[k] is not False for k in ("novel_theorem_verified","p_equals_np_established","p_not_equals_np_established"))):
        raise ValueError("metadata mismatch")
    expected=splits(source,failures,v17)
    if set(r["data"])!=set(expected):
        raise ValueError("split mismatch")
    for k,cases in expected.items():
        rows=r["data"][k]
        if digest(cases)!=digest([row["case"] for row in rows]):
            raise ValueError("case mismatch")
        for c,row in zip(cases,rows):
            n,f=c["n"],c["clauses"]
            sat=oracle(n,f)
            if row["reference_sat"] is not sat or set(row["arms"])!=set(ARMS):
                raise ValueError("reference mismatch")
            for a,v in row["arms"].items():
                if type(v["work"]) is not int or not 0<=v["work"]<=STEPS:
                    raise ValueError("work cap")
                if a in ("sequential","cooperative"):
                    order=("composite","handoff","library") if a=="cooperative" else ("composite","library")
                    attempts=v["attempts"]
                    if len(attempts)>len(order):
                        raise ValueError("attempt count")
                    used=0
                    for route,t in zip(order,attempts):
                        divisor=8 if route=="composite" else 3 if route=="handoff" else 2
                        quota=max(1,(STEPS-used)//divisor)
                        if t["route"]!=route or t["quota"]!=quota or type(t["work"]) is not int or not 0<=t["work"]<=quota:
                            raise ValueError("quota mismatch")
                        used+=t["work"]
                    if used>v["work"]:
                        raise ValueError("work mismatch")
                if v["status"]=="verified":
                    if a=="library":
                        proof=reconstruct(n,f,index,v["transfers"],budget())
                    elif a=="composite":
                        proof=verify_recipe(n,f,v["recipe"],budget())
                    else:
                        if a=="sequential" and v["recipe"]["kind"]=="handoff":
                            raise ValueError("handoff in sequential arm")
                        proof=verify(n,f,index,v["recipe"],budget())
                    independent_replay(n,f,proof)
                    if sat or digest(proof)!=digest(v["proof"]) or v["proof_bytes"]!=bytesize(proof):
                        raise ValueError("proof mismatch")
                elif (any(x in v for x in ("proof","recipe","transfers")) or
                      v["status"] not in ("not_found","transfer_limit","resource_exhausted")):
                    raise ValueError("invalid uncredited result")
    if r["summary"]!=summarize(r["data"]):
        raise ValueError("aggregate mismatch")
    return True


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("benchmark","scheduler","failures","v17"):
        p.add_argument("--"+k,type=Path,required=True)
    m=p.add_mutually_exclusive_group(required=True)
    m.add_argument("--checkpoint",type=Path)
    m.add_argument("--audit",type=Path)
    a=p.parse_args()
    files=(a.benchmark,a.scheduler,a.failures,a.v17)
    inputs=tuple(json.loads(x.read_text()) for x in files)
    if a.audit:
        audit(*inputs,json.loads(a.audit.read_text()))
        print(json.dumps({"status":"positive_claims_replayed"}))
        return
    if a.checkpoint.resolve() in {x.resolve() for x in files}:
        p.error("cannot overwrite input")
    r=run(*inputs)
    a.checkpoint.write_text(json.dumps(r,indent=2,sort_keys=True))
    print(json.dumps(r["summary"],indent=2))


if __name__=="__main__":
    main()
