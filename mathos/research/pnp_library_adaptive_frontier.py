"""Paired evaluation of adaptive fragment scheduling on a fresh frozen split."""
import argparse
from collections import Counter
import json
from pathlib import Path
from time import perf_counter, process_time

from .pnp_library_frontier import audit as audit_v17, suite, case_key
from .pnp_library_ablation import NEW_SEED as ABLATION_SEED, independent_replay, oracle
from .pnp_abstraction_frontier import bytesize
from .pnp_evidence_benchmark import digest
from .pnp_proof_library import Index, reuse, reconstruct
from .pnp_library_adaptive import adaptive_reuse
from .pnp_structural_kernel import Budget

SEED=17203
ARMS=("exact","subsumption","adaptive_exact","adaptive")
STEPS=4_000_000


def budget():
    return Budget(seconds=15,max_steps=STEPS,max_cells=100000)


def evaluate(case,index):
    n,f=case["n"],case["clauses"]
    results={}
    offset=int(case_key(case)[:8],16)%len(ARMS)
    for arm in ARMS[offset:]+ARMS[:offset]:
        b=budget()
        start,cpu=perf_counter(),process_time()
        if arm.startswith("adaptive"):
            r=adaptive_reuse(n,f,index,b,allow_subsumption=arm=="adaptive")
        else:
            r=reuse(n,f,index,b,subsumption=arm=="subsumption",shared_replay=True)
        r.update(work=b.steps,wall_seconds=perf_counter()-start,
                 cpu_seconds=process_time()-cpu)
        if r["status"]=="verified":
            start=perf_counter()
            independent_replay(n,f,r["proof"])
            r.update(check_seconds=perf_counter()-start,proof_bytes=bytesize(r["proof"]),
                     recipe_bytes=bytesize(r["transfers"]))
        results[arm]=r
    sat=oracle(n,f)
    if sat and any(r["status"]=="verified" for r in results.values()):
        raise AssertionError("false UNSAT")
    return {"case":case,"reference_sat":sat,"arms":results}


def summary(rows):
    result={"cases":len(rows),"unsat":sum(not r["reference_sat"] for r in rows),"arms":{}}
    for arm in ARMS:
        values=[r["arms"][arm] for r in rows]
        hits=[r for r in values if r["status"]=="verified"]
        result["arms"][arm]={"verified":len(hits),"status":dict(Counter(v["status"] for v in values)),
                             "work":sum(v["work"] for v in values),
                             "wall_seconds":sum(v["wall_seconds"] for v in values),
                             "cpu_seconds":sum(v["cpu_seconds"] for v in values),
                             "proof_bytes":sum(v["proof_bytes"] for v in hits),
                             "recipe_bytes":sum(v["recipe_bytes"] for v in hits),
                             "check_seconds":sum(v["check_seconds"] for v in hits)}
    result["contrasts"]={}
    for a,b in (("exact","adaptive_exact"),("subsumption","adaptive"),
                ("adaptive_exact","adaptive"),("exact","adaptive")):
        pairs=[(r["arms"][a]["status"]=="verified",r["arms"][b]["status"]=="verified") for r in rows]
        result["contrasts"][a+" -> "+b]={"gain":sum(not x and y for x,y in pairs),
                                        "loss":sum(x and not y for x,y in pairs),
                                        "both":sum(x and y for x,y in pairs)}
    return result


def splits(source,failures,v17):
    if failures["seed"]==SEED:
        raise ValueError("overlapping upstream seed")
    previous=suite(ABLATION_SEED,24)
    fresh=suite(SEED,24)
    seen={case_key(c) for c in previous}
    for rows in (source["rows"],failures["training"],failures["evaluation"],
                 v17["training"],v17["discovery"],v17["heldout"],v17["retrospective"]):
        seen.update(case_key(r["case"]) for r in rows)
    keys={case_key(c) for c in fresh}
    if len(keys)!=len(fresh) or keys & seen:
        raise ValueError("duplicate normalized formula")
    return {"fresh":fresh,"retrospective":previous}


def summarize(data):
    out={k:summary(v) for k,v in data.items()}
    for family in ("random2","random3"):
        out[family]=summary([r for r in data["fresh"] if r["case"]["family"]==family])
    return out


def run(source,scheduler,failures,v17):
    audit_v17(source,scheduler,failures,v17)
    index=Index(v17["library"])
    frozen=digest(index.templates)
    data={k:[evaluate(c,index) for c in cases]
          for k,cases in splits(source,failures,v17).items()}
    if digest(index.templates)!=frozen:
        raise AssertionError("library changed")
    return {"schema":"mathos-pnp-adaptive-reuse/1","seed":SEED,
            "upstream":[digest(x) for x in (source,scheduler,failures,v17)],
            "library_sha256":frozen,"step_cap":STEPS,"data":data,"summary":summarize(data),
            "universal_obligation":"unresolved","novel_theorem_verified":False,
            "p_equals_np_established":False,"p_not_equals_np_established":False}


def audit(source,scheduler,failures,v17,r):
    audit_v17(source,scheduler,failures,v17)
    index=Index(v17["library"])
    if (r["schema"]!="mathos-pnp-adaptive-reuse/1" or r["seed"]!=SEED
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
            sat=oracle(n,f)
            if row["reference_sat"] is not sat or set(row["arms"])!=set(ARMS):
                raise ValueError("reference or arm mismatch")
            for a in row["arms"].values():
                if type(a["work"]) is not int or not 0<=a["work"]<=STEPS:
                    raise ValueError("work outside cap")
                if a["status"]=="verified":
                    proof=reconstruct(n,f,index,a["transfers"],budget())
                    independent_replay(n,f,proof)
                    if sat or digest(proof)!=digest(a["proof"]):
                        raise ValueError("certificate mismatch")
                    if a["proof_bytes"]!=bytesize(proof) or a["recipe_bytes"]!=bytesize(a["transfers"]):
                        raise ValueError("byte count mismatch")
                elif ("proof" in a or "transfers" in a or a["status"] not in
                      ("not_found","candidate_limit","transfer_limit","round_limit","resource_exhausted")):
                    raise ValueError("invalid uncredited outcome")
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
