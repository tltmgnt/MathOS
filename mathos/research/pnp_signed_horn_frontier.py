"""Frozen signed-Horn schema evaluation, separate from learned-template credit."""
import argparse
from collections import Counter
import json
from pathlib import Path
import random
from time import perf_counter

from .pnp_library_frontier import audit as audit_v17, suite, case_key
from .pnp_library_ablation import independent_replay, oracle
from .pnp_proof_library import Index, reuse, reconstruct
from .pnp_signed_horn import propose, verify_trace
from .pnp_structural_kernel import Budget
from .pnp_evidence_benchmark import digest
from .pnp_abstraction_frontier import bytesize

SEED=17403
ARMS=("exact","subsumption","horn_subset","signed_horn")
STEPS=4_000_000


def budget():
    return Budget(seconds=15,max_steps=STEPS,max_cells=100000)


def generated(seed):
    rng=random.Random(seed)
    out=[]
    for i in range(24):
        n=rng.randint(5,9)
        signs=[rng.choice((-1,1)) for _ in range(n)]
        f=[]
        for j in range(4*n):
            vs=rng.sample(range(1,n+1),rng.randint(1,min(n,4)))
            h=rng.choice(vs) if rng.randrange(3) else None
            f.append([v*signs[v-1]*(1 if v==h else -1) for v in vs])
        out.append({"id":f"signed_horn_{i:02d}","family":"signed_horn","n":n,"clauses":f})
    return out


def fresh():
    return suite(SEED,24)+generated(SEED+300000)


def evaluate(c,index):
    n,f=c["n"],c["clauses"]
    results={}
    offset=int(case_key(c)[:8],16)%len(ARMS)
    for a in ARMS[offset:]+ARMS[:offset]:
        b=budget()
        start=perf_counter()
        r=(propose(n,f,b,signed=a=="signed_horn") if a in ARMS[2:] else
           reuse(n,f,index,b,subsumption=a=="subsumption",shared_replay=True))
        r.update(work=b.steps,seconds=perf_counter()-start)
        if r["status"]=="verified":
            start=perf_counter()
            independent_replay(n,f,r["proof"])
            r.update(check_seconds=perf_counter()-start,proof_bytes=bytesize(r["proof"]),
                     recipe_bytes=bytesize(r.get("certificate",r.get("transfers"))))
        results[a]=r
    sat=oracle(n,f)
    if sat and any(r["status"]=="verified" for r in results.values()):
        raise AssertionError("false UNSAT")
    if c["family"]=="signed_horn" and results["signed_horn"]["status"]!="resource_exhausted":
        if results["signed_horn"]["status"]!=("not_found" if sat else "verified"):
            raise AssertionError("signed Horn recognition/completeness discrepancy")
    return {"case":c,"reference_sat":sat,"arms":results}


def summary(rows):
    result={"cases":len(rows),"unsat":sum(not r["reference_sat"] for r in rows),"arms":{}}
    for a in ARMS:
        values=[r["arms"][a] for r in rows]
        hits=[v for v in values if v["status"]=="verified"]
        result["arms"][a]={"verified":len(hits),"statuses":dict(Counter(v["status"] for v in values)),
                           "work":sum(v["work"] for v in values),"seconds":sum(v["seconds"] for v in values),
                           "proof_bytes":sum(v["proof_bytes"] for v in hits),
                           "recipe_bytes":sum(v["recipe_bytes"] for v in hits),
                           "check_seconds":sum(v["check_seconds"] for v in hits)}
    result["signed_only"]=sum(r["arms"]["signed_horn"]["status"]=="verified" and
                         all(r["arms"][a]["status"]!="verified" for a in ARMS[:3]) for r in rows)
    return result


def summarize(rows):
    return {"fresh":summary(rows),**{k:summary([r for r in rows if r["case"]["family"]==k])
                                      for k in ("random2","random3","signed_horn")}}


def cases(source,failures,v17):
    if failures["seed"]==SEED:
        raise ValueError("seed overlap")
    seen={case_key(c) for seed in (17103,17203,17303) for c in suite(seed,24)}
    # Also exclude the mixed part of the v17.3 split, without depending on its open PR.
    rng=random.Random(17303+200000)
    for _ in range(24):
        n=rng.randint(5,9)
        f=[]
        for j in range(3*n):
            w=2 if rng.randrange(2) else 3
            f.append([v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),w)])
        seen.add(case_key({"n":n,"clauses":f}))
    for rows in (source["rows"],failures["training"],failures["evaluation"],
                 v17["training"],v17["discovery"],v17["heldout"],v17["retrospective"]):
        seen.update(case_key(r["case"]) for r in rows)
    result=fresh()
    keys={case_key(c) for c in result}
    if len(keys)!=len(result) or keys & seen:
        raise ValueError("duplicate normalized formula")
    return result


def run(source,scheduler,failures,v17):
    audit_v17(source,scheduler,failures,v17)
    index=Index(v17["library"])
    frozen=digest(index.templates)
    rows=[evaluate(c,index) for c in cases(source,failures,v17)]
    if digest(index.templates)!=frozen:
        raise AssertionError("library changed")
    return {"schema":"mathos-pnp-signed-horn-frontier/1","seed":SEED,
            "upstream":[digest(x) for x in (source,scheduler,failures,v17)],
            "library_sha256":frozen,"step_cap":STEPS,"rows":rows,"summary":summarize(rows),
            "universal_obligation":"unresolved","novel_theorem_verified":False,
            "p_equals_np_established":False,"p_not_equals_np_established":False}


def audit(source,scheduler,failures,v17,r):
    audit_v17(source,scheduler,failures,v17)
    index=Index(v17["library"])
    if (r["schema"]!="mathos-pnp-signed-horn-frontier/1" or r["seed"]!=SEED
            or r["step_cap"]!=STEPS or r["library_sha256"]!=digest(index.templates)
            or r["upstream"]!=[digest(x) for x in (source,scheduler,failures,v17)]
            or r["universal_obligation"]!="unresolved"
            or any(r[k] is not False for k in ("novel_theorem_verified","p_equals_np_established",
                                               "p_not_equals_np_established"))):
        raise ValueError("metadata mismatch")
    expected=cases(source,failures,v17)
    if digest(expected)!=digest([row["case"] for row in r["rows"]]):
        raise ValueError("case mismatch")
    for c,row in zip(expected,r["rows"]):
        n,f=c["n"],c["clauses"]
        sat=oracle(n,f)
        if row["reference_sat"] is not sat or set(row["arms"])!=set(ARMS):
            raise ValueError("reference mismatch")
        for a,v in row["arms"].items():
            if type(v["work"]) is not int or not 0<=v["work"]<=STEPS:
                raise ValueError("work cap")
            if v["status"]=="verified":
                if a=="horn_subset" and tuple(v["certificate"]["signs"])!=(1,)*n:
                    raise ValueError("wrong route polarity")
                proof=(verify_trace(n,f,v["certificate"],budget()) if a in ARMS[2:] else
                       reconstruct(n,f,index,v["transfers"],budget()))
                independent_replay(n,f,proof)
                if sat or digest(proof)!=digest(v["proof"]):
                    raise ValueError("proof mismatch")
                if v["proof_bytes"]!=bytesize(proof) or v["recipe_bytes"]!=bytesize(v.get("certificate",v.get("transfers"))):
                    raise ValueError("byte count")
            elif (any(k in v for k in ("proof","certificate","transfers")) or
                  v["status"] not in ("not_found","not_renamable","transfer_limit","resource_exhausted")):
                raise ValueError("invalid uncredited result")
        if c["family"]=="signed_horn" and row["arms"]["signed_horn"]["status"]!="resource_exhausted":
            if row["arms"]["signed_horn"]["status"]!=("not_found" if sat else "verified"):
                raise ValueError("signed Horn discrepancy")
    if r["summary"]!=summarize(r["rows"]):
        raise ValueError("summary mismatch")
    return True


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("benchmark","scheduler","failures","v17"):
        p.add_argument("--"+k,type=Path,required=True)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checkpoint",type=Path)
    mode.add_argument("--audit",type=Path)
    a=p.parse_args()
    paths=(a.benchmark,a.scheduler,a.failures,a.v17)
    inputs=tuple(json.loads(x.read_text()) for x in paths)
    if a.audit:
        audit(*inputs,json.loads(a.audit.read_text()))
        print(json.dumps({"status":"positive_claims_replayed"}))
        return
    if a.checkpoint.resolve() in {x.resolve() for x in paths}:
        p.error("cannot overwrite input")
    r=run(*inputs)
    a.checkpoint.write_text(json.dumps(r,indent=2,sort_keys=True))
    print(json.dumps(r["summary"],indent=2))


if __name__=="__main__":
    main()
