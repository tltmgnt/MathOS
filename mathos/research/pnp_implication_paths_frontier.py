"""Frozen comparison of finite fragments and a length-parameterized path schema."""
import argparse
from collections import Counter
import json
from pathlib import Path
import random
from time import perf_counter

from .pnp_library_frontier import audit as audit_v17, suite, case_key
from .pnp_library_ablation import independent_replay, oracle
from .pnp_proof_library import Index, reuse, reconstruct
from .pnp_implication_paths import propose, verify_paths, binary_clauses
from .pnp_structural_kernel import Budget, two_sat, Exhausted
from .pnp_evidence_benchmark import digest
from .pnp_abstraction_frontier import bytesize

SEED=17303
ARMS=("exact","subsumption","paths")
STEPS=4_000_000


def budget():
    return Budget(seconds=15,max_steps=STEPS,max_cells=100000)


def fresh_cases():
    out=suite(SEED,24)
    rng=random.Random(SEED+200000)
    for i in range(24):
        n=rng.randint(5,9)
        f=[]
        for j in range(3*n):
            width=2 if rng.randrange(2) else 3
            f.append([v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),width)])
        out.append({"id":f"mixed_{i:02d}","family":"mixed23","n":n,"clauses":f})
    return out


def controls():
    out=[]
    for n in (1,4,10,32,64,128):
        f=[[1]]+[[-i,i+1] for i in range(1,n)]
        for sat in (False,True):
            out.append({"id":f"chain_{n}_{int(sat)}","family":"chain_control","n":n,
                        "clauses":f+[[n if sat else -n]]})
    return out


def reference(case):
    n,f=case["n"],case["clauses"]
    if case["family"]=="chain_control":
        # Existing independently implemented reachability checker.
        return two_sat(n,[tuple(c) for c in f],Budget(seconds=15,max_steps=20_000_000))
    return oracle(n,f)


def evaluate(case,index):
    n,f=case["n"],case["clauses"]
    results={}
    offset=int(case_key(case)[:8],16)%len(ARMS)
    for arm in ARMS[offset:]+ARMS[:offset]:
        b=budget()
        start=perf_counter()
        r=(propose(n,f,b) if arm=="paths" else
           reuse(n,f,index,b,subsumption=arm=="subsumption",shared_replay=True))
        r.update(work=b.steps,seconds=perf_counter()-start)
        if r["status"] in ("verified","input_empty"):
            start=perf_counter()
            independent_replay(n,f,r["proof"])
            r.update(check_seconds=perf_counter()-start,proof_bytes=bytesize(r["proof"]),
                     recipe_bytes=bytesize(r.get("certificate",r.get("transfers",[]))))
        results[arm]=r
    sat=reference(case)
    if sat and any(a["status"] in ("verified","input_empty") for a in results.values()):
        raise AssertionError("false refutation")
    # Compare path recognition to legacy 2-SAT on exactly the binary subset.
    b=Budget(seconds=15,max_steps=20_000_000)
    binary,empty=binary_clauses(n,f,b)
    binary_sat=not empty and two_sat(n,sorted(binary),b)
    if results["paths"]["status"]!="resource_exhausted":
        if (results["paths"]["status"]=="not_found")!=binary_sat:
            raise AssertionError("binary recognition disagreement")
    return {"case":case,"reference_sat":sat,"binary_reference_sat":binary_sat,"arms":results}


def summary(rows):
    result={"cases":len(rows),"unsat":sum(not r["reference_sat"] for r in rows),
            "binary_subset_unsat":sum(not r["binary_reference_sat"] for r in rows),"arms":{}}
    for arm in ARMS:
        a=[r["arms"][arm] for r in rows]
        hits=[v for v in a if v["status"]=="verified"]
        result["arms"][arm]={"verified":len(hits),"statuses":dict(Counter(v["status"] for v in a)),
             "work":sum(v["work"] for v in a),"seconds":sum(v["seconds"] for v in a),
             "proof_bytes":sum(v["proof_bytes"] for v in hits),
             "recipe_bytes":sum(v["recipe_bytes"] for v in hits),
             "check_seconds":sum(v["check_seconds"] for v in hits)}
    result["union_coverage"]=sum(any(r["arms"][a]["status"]=="verified" for a in ARMS) for r in rows)
    result["paths_only"]=sum(r["arms"]["paths"]["status"]=="verified" and
                             all(r["arms"][a]["status"]!="verified" for a in ARMS[:2]) for r in rows)
    return result


def splits(source,failures,v17):
    if failures["seed"]==SEED:
        raise ValueError("seed overlap")
    seen={case_key(c) for seed in (17103,17203) for c in suite(seed,24)}
    for rows in (source["rows"],failures["training"],failures["evaluation"],
                 v17["training"],v17["discovery"],v17["heldout"],v17["retrospective"]):
        seen.update(case_key(r["case"]) for r in rows)
    fresh=fresh_cases()
    keys={case_key(c) for c in fresh}
    if len(keys)!=len(fresh) or keys & seen:
        raise ValueError("duplicate normalized input")
    return {"fresh":fresh,"controls":controls()}


def summarize(data):
    s={k:summary(v) for k,v in data.items()}
    for fam in ("random2","random3","mixed23"):
        s[fam]=summary([r for r in data["fresh"] if r["case"]["family"]==fam])
    return s


def run(source,scheduler,failures,v17):
    audit_v17(source,scheduler,failures,v17)
    index=Index(v17["library"])
    frozen=digest(index.templates)
    data={k:[evaluate(c,index) for c in cases] for k,cases in splits(source,failures,v17).items()}
    if digest(index.templates)!=frozen:
        raise AssertionError("library mutation")
    return {"schema":"mathos-pnp-parameterized-paths/1","seed":SEED,
            "upstream":[digest(x) for x in (source,scheduler,failures,v17)],
            "library_sha256":frozen,"step_cap":STEPS,"data":data,"summary":summarize(data),
            "universal_obligation":"unresolved","novel_theorem_verified":False,
            "p_equals_np_established":False,"p_not_equals_np_established":False}


def audit(source,scheduler,failures,v17,r):
    audit_v17(source,scheduler,failures,v17)
    index=Index(v17["library"])
    if (r["schema"]!="mathos-pnp-parameterized-paths/1" or r["seed"]!=SEED
            or r["step_cap"]!=STEPS or r["library_sha256"]!=digest(index.templates)
            or r["upstream"]!=[digest(x) for x in (source,scheduler,failures,v17)]
            or r["universal_obligation"]!="unresolved"
            or any(r[k] is not False for k in ("novel_theorem_verified","p_equals_np_established",
                                               "p_not_equals_np_established"))):
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
            sat=reference(c)
            binary,empty=binary_clauses(n,f,budget())
            binary_sat=not empty and two_sat(n,sorted(binary),Budget(seconds=15,max_steps=20_000_000))
            if row["reference_sat"] is not sat or row["binary_reference_sat"] is not binary_sat or set(row["arms"])!=set(ARMS):
                raise ValueError("reference or arms mismatch")
            for arm,a in row["arms"].items():
                if type(a["work"]) is not int or not 0<=a["work"]<=STEPS:
                    raise ValueError("work cap")
                if a["status"] in ("verified","input_empty"):
                    if a["status"]=="input_empty":
                        if arm!="paths" or not empty:
                            raise ValueError("invalid input empty credit")
                        proof=[]
                    elif arm=="paths":
                        proof=verify_paths(n,f,a["certificate"],budget())
                    else:
                        proof=reconstruct(n,f,index,a["transfers"],budget())
                    independent_replay(n,f,proof)
                    if sat or digest(proof)!=digest(a["proof"]):
                        raise ValueError("proof mismatch")
                    if a["proof_bytes"]!=bytesize(proof) or a["recipe_bytes"]!=bytesize(a.get("certificate",a.get("transfers",[]))):
                        raise ValueError("byte count mismatch")
                elif (any(key in a for key in ("proof","certificate","transfers")) or
                      a["status"] not in ("not_found","transfer_limit","resource_exhausted")):
                    raise ValueError("invalid uncredited result")
            if row["arms"]["paths"]["status"]!="resource_exhausted" and (
                    row["arms"]["paths"]["status"]=="not_found")!=binary_sat:
                raise ValueError("binary recognition mismatch")
    if r["summary"]!=summarize(r["data"]):
        raise ValueError("aggregate mismatch")
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
