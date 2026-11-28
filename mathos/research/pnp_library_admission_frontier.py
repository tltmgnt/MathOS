"""v17.7 offline admission followed by frozen, paired held-out scoring."""
import argparse
from collections import Counter
import json
from pathlib import Path
from time import perf_counter

from .pnp_library_frontier import audit as audit_v17, suite, case_key
from .pnp_schema_portfolio_frontier import splits as previous_splits
from .pnp_schema_portfolio import solve, verify
from .pnp_library_admission import admit
from .pnp_library_ablation import independent_replay, oracle
from .pnp_proof_library import Index, reuse, reconstruct
from .pnp_structural_kernel import Budget
from .pnp_evidence_benchmark import digest
from .pnp_abstraction_frontier import bytesize

TRAIN,DISCOVERY,HOLDOUT=17701,17702,17703
ARMS=("base","admitted")
STEPS=4_000_000


def budget():
    return Budget(seconds=15,max_steps=STEPS,max_cells=100000)


def offline_budget():
    return Budget(seconds=120,max_steps=60_000_000,max_cells=100000)


def generate(seed,count):
    import random
    out=suite(seed,count)
    rng=random.Random(seed+200000)
    for i in range(count):
        n=rng.randint(5,9)
        f=[]
        for _ in range(3*n):
            w=rng.choices((1,2,3,4),weights=(1,3,5,1))[0]
            f.append([v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),w)])
        out.append({"id":f"mixed_{i:02d}","family":"mixed1234","n":n,"clauses":f})
    return out


def splits(source,failures,v17):
    if failures["seed"] in (TRAIN,DISCOVERY,HOLDOUT):
        raise ValueError("upstream seed overlap")
    previous=previous_splits(source,failures,v17)
    seen={case_key(c) for cases in previous.values() for c in cases}
    from .pnp_implication_paths_frontier import fresh_cases
    from .pnp_signed_horn_frontier import fresh as prior_horn
    seen.update(case_key(c) for c in fresh_cases()+prior_horn())
    seen.update(case_key(c) for seed in (17103,17203) for c in suite(seed,24))
    for rows in (source["rows"],failures["training"],failures["evaluation"],
                 v17["training"],v17["discovery"],v17["heldout"],v17["retrospective"]):
        seen.update(case_key(r["case"]) for r in rows)
    out={"training":generate(TRAIN,12),"discovery":generate(DISCOVERY,8),
         "heldout":generate(HOLDOUT,24)}
    for cases in out.values():
        keys={case_key(c) for c in cases}
        if len(keys)!=len(cases) or keys & seen:
            raise ValueError("duplicate normalized input")
        seen.update(keys)
    return out


def train(case,index):
    b=budget()
    start=perf_counter()
    r=solve(case["n"],case["clauses"],index,b)
    r.update(work=b.steps,seconds=perf_counter()-start)
    if r["status"]=="verified":
        independent_replay(case["n"],case["clauses"],r["proof"])
        if oracle(case["n"],case["clauses"]):
            raise AssertionError("false training refutation")
    return {"case":case,"result":r}


def evaluate(c,indexes,base_count):
    n,f=c["n"],c["clauses"]
    results={}
    order=ARMS if int(case_key(c)[:8],16)%2==0 else ARMS[::-1]
    for a in order:
        b=budget()
        start=perf_counter()
        r=reuse(n,f,indexes[a],b,shared_replay=True)
        r.update(work=b.steps,seconds=perf_counter()-start)
        if r["status"]=="verified":
            independent_replay(n,f,r["proof"])
            r.update(proof_bytes=bytesize(r["proof"]),
                     uses_admitted=any(i>=base_count for i,_ in r["transfers"]))
        results[a]=r
    sat=oracle(n,f)
    if sat and any(r["status"]=="verified" for r in results.values()):
        raise AssertionError("false evaluation refutation")
    return {"case":c,"reference_sat":sat,"arms":results}


def summary(rows):
    result={"cases":len(rows),"unsat":sum(not r["reference_sat"] for r in rows),"arms":{}}
    for a in ARMS:
        values=[r["arms"][a] for r in rows]
        hits=[v for v in values if v["status"]=="verified"]
        result["arms"][a]={"verified":len(hits),"statuses":dict(Counter(v["status"] for v in values)),
                           "work":sum(v["work"] for v in values),
                           "seconds":sum(v["seconds"] for v in values),
                           "proof_bytes":sum(v["proof_bytes"] for v in hits),
                           "uses_admitted":sum(v["uses_admitted"] for v in hits)}
    pairs=[(r["arms"]["base"]["status"]=="verified",r["arms"]["admitted"]["status"]=="verified") for r in rows]
    result["paired"]={"gain":sum(not x and y for x,y in pairs),
                      "loss":sum(x and not y for x,y in pairs),"both":sum(x and y for x,y in pairs)}
    result["gains_using_admitted"]=sum(not x and y and r["arms"]["admitted"]["uses_admitted"]
                                      for (x,y),r in zip(pairs,rows))
    return result


def summarize(data):
    s={k:summary(v) for k,v in data.items()}
    for fam in ("random2","random3","mixed1234"):
        s["heldout_"+fam]=summary([r for r in data["heldout"] if r["case"]["family"]==fam])
    return s


def run(source,scheduler,failures,v17):
    audit_v17(source,scheduler,failures,v17)
    base=tuple(v17["library"])
    cases=splits(source,failures,v17)
    start=perf_counter()
    training=[train(c,Index(base)) for c in cases["training"]]
    training_seconds=perf_counter()-start
    b=offline_budget()
    start=perf_counter()
    library,lineage=admit(base,training,b)
    cost={"work":b.steps,"seconds":perf_counter()-start,"training_seconds":training_seconds}
    frozen={"base":digest(base),"admitted":digest(library)}
    indexes={"base":Index(base),"admitted":Index(library)}
    data={k:[evaluate(c,indexes,len(base)) for c in cases[k]] for k in ("discovery","heldout")}
    if {k:digest(v.templates) for k,v in indexes.items()}!=frozen:
        raise AssertionError("library mutation")
    return {"schema":"mathos-pnp-library-admission-frontier/1",
            "seeds":[TRAIN,DISCOVERY,HOLDOUT],"step_cap":STEPS,
            "upstream":[digest(x) for x in (source,scheduler,failures,v17)],
            "library_hashes":frozen,"library_sizes":{"base":len(base),"admitted":len(library)},
            "library_bytes":{"base":bytesize(base),"admitted":bytesize(library)},
            "training":training,"lineage":lineage,"library":library,"offline_cost":cost,
            "data":data,"summary":summarize(data),"universal_obligation":"unresolved",
            "novel_theorem_verified":False,"p_equals_np_established":False,"p_not_equals_np_established":False}


def audit(source,scheduler,failures,v17,r):
    audit_v17(source,scheduler,failures,v17)
    base=tuple(v17["library"])
    if (r["schema"]!="mathos-pnp-library-admission-frontier/1"
            or r["seeds"]!=[TRAIN,DISCOVERY,HOLDOUT] or r["step_cap"]!=STEPS
            or r["upstream"]!=[digest(x) for x in (source,scheduler,failures,v17)]
            or r["universal_obligation"]!="unresolved"
            or any(r[k] is not False for k in ("novel_theorem_verified","p_equals_np_established","p_not_equals_np_established"))):
        raise ValueError("metadata mismatch")
    cases=splits(source,failures,v17)
    if digest(cases["training"])!=digest([x["case"] for x in r["training"]]):
        raise ValueError("training split mismatch")
    for row in r["training"]:
        c,v=row["case"],row["result"]
        if type(v["work"]) is not int or not 0<=v["work"]<=STEPS:
            raise ValueError("training work cap")
        if v["status"]=="verified":
            proof=verify(c["n"],c["clauses"],Index(base),v["recipe"],budget())
            independent_replay(c["n"],c["clauses"],proof)
            if oracle(c["n"],c["clauses"]) or digest(proof)!=digest(v["proof"]):
                raise ValueError("training certificate mismatch")
        elif v["status"] not in ("not_found","resource_exhausted") or any(k in v for k in ("proof","recipe")):
            raise ValueError("uncredited training result")
    library,lineage=admit(base,r["training"],offline_budget())
    if (digest(library)!=digest(r["library"]) or digest(lineage)!=digest(r["lineage"])
            or r["library_hashes"]!={"base":digest(base),"admitted":digest(library)}
            or r["library_sizes"]!={"base":len(base),"admitted":len(library)}
            or r["library_bytes"]!={"base":bytesize(base),"admitted":bytesize(library)}):
        raise ValueError("admission lineage mismatch")
    indexes={"base":Index(base),"admitted":Index(library)}
    if set(r["data"])!={"discovery","heldout"}:
        raise ValueError("evaluation split mismatch")
    for k,rows in r["data"].items():
        if digest(cases[k])!=digest([row["case"] for row in rows]):
            raise ValueError("case mismatch")
        for c,row in zip(cases[k],rows):
            n,f=c["n"],c["clauses"]
            sat=oracle(n,f)
            if row["reference_sat"] is not sat or set(row["arms"])!=set(ARMS):
                raise ValueError("reference mismatch")
            for a,v in row["arms"].items():
                if type(v["work"]) is not int or not 0<=v["work"]<=STEPS:
                    raise ValueError("evaluation work cap")
                if v["status"]=="verified":
                    proof=reconstruct(n,f,indexes[a],v["transfers"],budget())
                    independent_replay(n,f,proof)
                    uses=any(i>=len(base) for i,_ in v["transfers"])
                    if sat or digest(proof)!=digest(v["proof"]) or v["proof_bytes"]!=bytesize(proof) or v["uses_admitted"] is not uses:
                        raise ValueError("evaluation proof mismatch")
                elif v["status"] not in ("not_found","transfer_limit","resource_exhausted") or any(x in v for x in ("proof","transfers","uses_admitted")):
                    raise ValueError("uncredited evaluation result")
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
    print(json.dumps({"library_sizes":r["library_sizes"],"offline_cost":r["offline_cost"],"summary":r["summary"]},indent=2))


if __name__=="__main__":
    main()
