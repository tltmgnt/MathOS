"""Paired composition evaluation with frozen libraries and independent replay."""
import argparse
from collections import Counter
import json
from pathlib import Path
import random
from time import perf_counter

from .pnp_library_frontier import audit as audit_v17, suite, case_key
from .pnp_library_ablation import independent_replay, oracle
from .pnp_implication_paths import propose as paths, verify_paths
from .pnp_implication_paths_frontier import fresh_cases as prior_paths
from .pnp_composite_paths import propose, verify_recipe
from .pnp_proof_library import Index, reuse, reconstruct
from .pnp_structural_kernel import Budget
from .pnp_evidence_benchmark import digest
from .pnp_abstraction_frontier import bytesize

SEED=17503
ARMS=("units","paths","composite","subsumption")
STEPS=4_000_000
HITS=("verified","input_empty")


def budget():
    return Budget(seconds=15,max_steps=STEPS,max_cells=100000)


def fresh():
    result=suite(SEED,24)
    rng=random.Random(SEED+200000)
    for i in range(24):
        n=rng.randint(5,9)
        f=[]
        for _ in range(3*n):
            w=rng.choices((1,2,3,4),weights=(1,3,5,1))[0]
            f.append([v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),w)])
        result.append({"id":f"mixed_{i:02d}","family":"mixed1234","n":n,"clauses":f})
    return result


def controls():
    out=[]
    # Four binary clauses form a contradictory square. Guard them with
    # distinct forced literals; remove one clause for a SAT twin.
    for n in (3,5,8,12):
        facts=[[v] for v in range(3,n+1)]
        core=[[-(3+i%(n-2)),a,b] for i,(a,b) in enumerate(((1,2),(1,-2),(-1,2),(-1,-2)))]
        for sat in (False,True):
            out.append({"id":f"guarded_{n}_{int(sat)}","family":"guarded_control","n":n,
                        "clauses":facts+(core[:-1] if sat else core)})
    return out


def splits(source,failures,v17):
    if failures["seed"]==SEED:
        raise ValueError("seed overlap")
    seen={case_key(c) for seed in (17103,17203,17403) for c in suite(seed,24)}
    seen.update(case_key(c) for c in prior_paths())
    # Reproduce the v17.4 signed-Horn generator without depending on its PR.
    rng=random.Random(317403)
    for _ in range(24):
        n=rng.randint(5,9)
        signs=[rng.choice((-1,1)) for _ in range(n)]
        f=[]
        for j in range(4*n):
            vs=rng.sample(range(1,n+1),rng.randint(1,min(n,4)))
            h=rng.choice(vs) if rng.randrange(3) else None
            f.append([v*signs[v-1]*(1 if v==h else -1) for v in vs])
        seen.add(case_key({"n":n,"clauses":f}))
    for rows in (source["rows"],failures["training"],failures["evaluation"],
                 v17["training"],v17["discovery"],v17["heldout"],v17["retrospective"]):
        seen.update(case_key(r["case"]) for r in rows)
    cases=fresh()
    keys={case_key(c) for c in cases}
    if len(keys)!=len(cases) or keys & seen:
        raise ValueError("duplicate normalized input")
    return {"fresh":cases,"controls":controls()}


def evaluate(c,index):
    n,f=c["n"],c["clauses"]
    results={}
    offset=int(case_key(c)[:8],16)%len(ARMS)
    for arm in ARMS[offset:]+ARMS[:offset]:
        b=budget()
        start=perf_counter()
        if arm=="paths":
            r=paths(n,f,b)
        elif arm=="subsumption":
            r=reuse(n,f,index,b,subsumption=True,shared_replay=True)
        else:
            r=propose(n,f,b,compose=arm=="composite")
        r.update(work=b.steps,seconds=perf_counter()-start)
        if r["status"] in HITS:
            start=perf_counter()
            independent_replay(n,f,r["proof"])
            r.update(check_seconds=perf_counter()-start,proof_bytes=bytesize(r["proof"]))
        results[arm]=r
    sat=oracle(n,f)
    if sat and any(v["status"] in HITS for v in results.values()):
        raise AssertionError("false refutation")
    if c["family"]=="guarded_control" and not sat:
        if (results["units"]["status"]!="not_found" or results["paths"]["status"]!="not_found"
                or results["composite"]["status"]!="verified"):
            raise AssertionError("composition control failed")
    return {"case":c,"reference_sat":sat,"arms":results}


def summary(rows):
    result={"cases":len(rows),"unsat":sum(not r["reference_sat"] for r in rows),"arms":{}}
    for arm in ARMS:
        values=[r["arms"][arm] for r in rows]
        hits=[v for v in values if v["status"] in HITS]
        result["arms"][arm]={"verified":len(hits),"statuses":dict(Counter(v["status"] for v in values)),
                            "work":sum(v["work"] for v in values),"seconds":sum(v["seconds"] for v in values),
                            "proof_bytes":sum(v["proof_bytes"] for v in hits),
                            "check_seconds":sum(v["check_seconds"] for v in hits)}
    result["composition_only"]=sum(r["arms"]["composite"]["status"] in HITS and
                              all(r["arms"][a]["status"] not in HITS for a in ("units","paths")) for r in rows)
    result["composite_only_vs_all"]=sum(r["arms"]["composite"]["status"] in HITS and
                              all(r["arms"][a]["status"] not in HITS for a in ("units","paths","subsumption")) for r in rows)
    result["composition_losses"]=sum(r["arms"]["composite"]["status"] not in HITS and
                              any(r["arms"][a]["status"] in HITS for a in ("units","paths")) for r in rows)
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
    return {"schema":"mathos-pnp-composite-paths/1","seed":SEED,"step_cap":STEPS,
            "upstream":[digest(x) for x in (source,scheduler,failures,v17)],
            "library_sha256":frozen,"data":data,"summary":summarize(data),
            "universal_obligation":"unresolved","novel_theorem_verified":False,
            "p_equals_np_established":False,"p_not_equals_np_established":False}


def audit(source,scheduler,failures,v17,r):
    audit_v17(source,scheduler,failures,v17)
    index=Index(v17["library"])
    if (r["schema"]!="mathos-pnp-composite-paths/1" or r["seed"]!=SEED
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
                if v["status"] in HITS:
                    if v["status"]=="input_empty":
                        if a!="paths" or not any(not c for c in f):
                            raise ValueError("invalid input-empty status")
                        proof=[]
                    elif a=="paths":
                        proof=verify_paths(n,f,v["certificate"],budget())
                    elif a=="subsumption":
                        proof=reconstruct(n,f,index,v["transfers"],budget())
                    else:
                        if a=="units" and v["recipe"]["kind"]!="unit":
                            raise ValueError("wrong proof route")
                        proof=verify_recipe(n,f,v["recipe"],budget())
                    independent_replay(n,f,proof)
                    if sat or digest(proof)!=digest(v["proof"]) or v["proof_bytes"]!=bytesize(proof):
                        raise ValueError("proof mismatch")
                elif (any(x in v for x in ("proof","recipe","certificate","transfers")) or
                      v["status"] not in ("not_found","transfer_limit","resource_exhausted")):
                    raise ValueError("invalid uncredited result")
            if k=="controls" and not sat:
                if (row["arms"]["units"]["status"]!="not_found" or row["arms"]["paths"]["status"]!="not_found"
                        or row["arms"]["composite"]["status"]!="verified"):
                    raise ValueError("control mismatch")
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
