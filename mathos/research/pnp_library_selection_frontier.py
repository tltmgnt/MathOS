"""Iterative admission with independent discovery gates and a final untouched split."""
import argparse
from collections import Counter
import json
from pathlib import Path
from time import perf_counter

from .pnp_library_frontier import audit as audit_v17, suite, case_key
from .pnp_library_admission_frontier import (generate, splits as previous_admission,
                                            train, budget, offline_budget, STEPS)
from .pnp_schema_portfolio_frontier import splits as previous_portfolio
from .pnp_implication_paths_frontier import fresh_cases as prior_paths
from .pnp_signed_horn_frontier import fresh as prior_horn
from .pnp_schema_portfolio import verify
from .pnp_library_admission import admit
from .pnp_library_selection import bundles, choose, union_snapshot
from .pnp_library_ablation import independent_replay, oracle
from .pnp_proof_library import Index, reuse, reconstruct
from .pnp_evidence_benchmark import digest
from .pnp_abstraction_frontier import bytesize

SEEDS=(17801,17802,17803,17804,17805)
FINAL=("base","ungated","gated")


def splits(source,failures,v17):
    if failures["seed"] in SEEDS:
        raise ValueError("upstream seed overlap")
    seen={case_key(c) for c in prior_paths()+prior_horn()}
    seen.update(case_key(c) for seed in (17103,17203) for c in suite(seed,24))
    for old in (previous_portfolio(source,failures,v17),previous_admission(source,failures,v17)):
        seen.update(case_key(c) for cases in old.values() for c in cases)
    for rows in (source["rows"],failures["training"],failures["evaluation"],
                 v17["training"],v17["discovery"],v17["heldout"],v17["retrospective"]):
        seen.update(case_key(r["case"]) for r in rows)
    result={k:generate(seed,24 if k=="heldout" else 6)
            for k,seed in zip(("train1","discover1","train2","discover2","heldout"),SEEDS)}
    for cases in result.values():
        keys={case_key(c) for c in cases}
        if len(keys)!=len(cases) or keys & seen:
            raise ValueError("normalized input overlap")
        seen.update(keys)
    return result


def score(c,indexes,base_count):
    n,f=c["n"],c["clauses"]
    results={}
    order=tuple(indexes)
    offset=int(case_key(c)[:8],16)%len(order)
    for a in order[offset:]+order[:offset]:
        b=budget()
        start=perf_counter()
        r=reuse(n,f,indexes[a],b,shared_replay=True)
        r.update(work=b.steps,seconds=perf_counter()-start)
        if r["status"]=="verified":
            start=perf_counter()
            independent_replay(n,f,r["proof"])
            r.update(check_seconds=perf_counter()-start,proof_bytes=bytesize(r["proof"]),
                     uses_added=any(i>=base_count for i,_ in r["transfers"]))
        results[a]=r
    sat=oracle(n,f)
    if sat and any(r["status"]=="verified" for r in results.values()):
        raise AssertionError("false refutation")
    return {"case":c,"reference_sat":sat,"arms":results}


def summarize(rows,arms,incumbent):
    s={"cases":len(rows),"unsat":sum(not r["reference_sat"] for r in rows),"arms":{},"paired":{}}
    for a in arms:
        rs=[r["arms"][a] for r in rows]
        hits=[r for r in rs if r["status"]=="verified"]
        s["arms"][a]={"verified":len(hits),"statuses":dict(Counter(r["status"] for r in rs)),
                      "work":sum(r["work"] for r in rs),"seconds":sum(r["seconds"] for r in rs),
                      "check_seconds":sum(r["check_seconds"] for r in hits),
                      "proof_bytes":sum(r["proof_bytes"] for r in hits),
                      "uses_added":sum(r["uses_added"] for r in hits)}
        pairs=[(r["arms"][incumbent]["status"]=="verified",r["arms"][a]["status"]=="verified") for r in rows]
        s["paired"][a]={"gain":sum(not x and y for x,y in pairs),
                        "loss":sum(x and not y for x,y in pairs),
                        "both":sum(x and y for x,y in pairs),
                        "gain_using_added":sum(not x and y and r["arms"][a]["uses_added"]
                                               for (x,y),r in zip(pairs,rows))}
    return s


def final_summary(rows):
    return {"heldout":summarize(rows,FINAL,"base"),
            **{f:summarize([r for r in rows if r["case"]["family"]==f],FINAL,"base")
               for f in ("random2","random3","mixed1234")}}


def metadata(libraries):
    return {k:{"sha256":digest(v),"size":len(v),"bytes":bytesize(v)} for k,v in libraries.items()}


def epoch(current,training,discovery):
    start=perf_counter()
    trained=[train(c,Index(current)) for c in training]
    training_seconds=perf_counter()-start
    b=offline_budget()
    start=perf_counter()
    expanded,lineage=admit(current,trained,b)
    cost={"training_seconds":training_seconds,"admission_seconds":perf_counter()-start,"admission_work":b.steps}
    cohorts=bundles(current,expanded)
    indexes={k:Index(v) for k,v in cohorts.items()}
    rows=[score(c,indexes,len(current)) for c in discovery]
    picked=choose(rows,cohorts)
    record={"training":trained,"lineage":lineage,"expanded":expanded,
            "cohorts":metadata(cohorts),"chosen":picked,"discovery":rows,
            "discovery_summary":summarize(rows,tuple(cohorts),"retain"),"offline_cost":cost}
    return cohorts[picked],expanded,record


def run(source,scheduler,failures,v17):
    audit_v17(source,scheduler,failures,v17)
    cases=splits(source,failures,v17)
    base=tuple(v17["library"])
    current=base
    pools=[]
    epochs=[]
    for i in (1,2):
        current,pool,record=epoch(current,cases[f"train{i}"],cases[f"discover{i}"])
        pools.append(pool)
        epochs.append(record)
    libs={"base":base,"ungated":union_snapshot(base,pools),"gated":current}
    frozen=metadata(libs)
    indexes={k:Index(v) for k,v in libs.items()}
    rows=[score(c,indexes,len(base)) for c in cases["heldout"]]
    if metadata({k:v.templates for k,v in indexes.items()})!=frozen:
        raise AssertionError("snapshot mutation")
    return {"schema":"mathos-pnp-library-selection-frontier/1","seeds":SEEDS,"step_cap":STEPS,
            "upstream":[digest(x) for x in (source,scheduler,failures,v17)],
            "epochs":epochs,"libraries":libs,"library_metadata":frozen,
            "heldout":rows,"summary":final_summary(rows),
            "universal_obligation":"unresolved","novel_theorem_verified":False,
            "p_equals_np_established":False,"p_not_equals_np_established":False}


def check_training(cases,rows,current):
    if digest(cases)!=digest([r["case"] for r in rows]):
        raise ValueError("training mismatch")
    for c,r in zip(cases,rows):
        v=r["result"]
        if type(v["work"]) is not int or not 0<=v["work"]<=STEPS:
            raise ValueError("training work cap")
        if v["status"]=="verified":
            proof=verify(c["n"],c["clauses"],Index(current),v["recipe"],budget())
            independent_replay(c["n"],c["clauses"],proof)
            if oracle(c["n"],c["clauses"]) or digest(proof)!=digest(v["proof"]):
                raise ValueError("training proof mismatch")
        elif v["status"] not in ("not_found","resource_exhausted") or any(k in v for k in ("proof","recipe")):
            raise ValueError("uncredited training")


def check_scores(cases,rows,libraries,base_count):
    if digest(cases)!=digest([r["case"] for r in rows]):
        raise ValueError("evaluation cases mismatch")
    indexes={k:Index(v) for k,v in libraries.items()}
    for c,row in zip(cases,rows):
        n,f=c["n"],c["clauses"]
        sat=oracle(n,f)
        if row["reference_sat"] is not sat or set(row["arms"])!=set(libraries):
            raise ValueError("reference or arms mismatch")
        for a,v in row["arms"].items():
            if type(v["work"]) is not int or not 0<=v["work"]<=STEPS:
                raise ValueError("evaluation work cap")
            if v["status"]=="verified":
                proof=reconstruct(n,f,indexes[a],v["transfers"],budget())
                independent_replay(n,f,proof)
                if (sat or digest(proof)!=digest(v["proof"]) or v["proof_bytes"]!=bytesize(proof)
                        or v["uses_added"] is not any(i>=base_count for i,_ in v["transfers"])):
                    raise ValueError("certificate mismatch")
            elif v["status"] not in ("not_found","transfer_limit","resource_exhausted") or any(
                    k in v for k in ("proof","transfers","uses_added")):
                raise ValueError("uncredited evaluation")


def audit(source,scheduler,failures,v17,r):
    audit_v17(source,scheduler,failures,v17)
    if (r["schema"]!="mathos-pnp-library-selection-frontier/1"
            or tuple(r["seeds"])!=SEEDS or r["step_cap"]!=STEPS
            or r["upstream"]!=[digest(x) for x in (source,scheduler,failures,v17)]
            or r["universal_obligation"]!="unresolved"
            or any(r[k] is not False for k in ("novel_theorem_verified","p_equals_np_established","p_not_equals_np_established"))):
        raise ValueError("metadata mismatch")
    cases=splits(source,failures,v17)
    base=tuple(v17["library"])
    current=base
    pools=[]
    if len(r["epochs"])!=2:
        raise ValueError("wrong epoch count")
    for i,e in enumerate(r["epochs"],1):
        check_training(cases[f"train{i}"],e["training"],current)
        expanded,lineage=admit(current,e["training"],offline_budget())
        if digest(expanded)!=digest(e["expanded"]) or digest(lineage)!=digest(e["lineage"]):
            raise ValueError("lineage mismatch")
        cohorts=bundles(current,expanded)
        if metadata(cohorts)!=e["cohorts"]:
            raise ValueError("cohort mismatch")
        check_scores(cases[f"discover{i}"],e["discovery"],cohorts,len(current))
        selected=choose(e["discovery"],cohorts)
        if selected!=e["chosen"] or e["discovery_summary"]!=summarize(e["discovery"],tuple(cohorts),"retain"):
            raise ValueError("gate mismatch")
        current=cohorts[selected]
        pools.append(expanded)
    libs={"base":base,"ungated":union_snapshot(base,pools),"gated":current}
    if digest(libs)!=digest(r["libraries"]) or metadata(libs)!=r["library_metadata"]:
        raise ValueError("snapshot mismatch")
    check_scores(cases["heldout"],r["heldout"],libs,len(base))
    if r["summary"]!=final_summary(r["heldout"]):
        raise ValueError("summary mismatch")
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
    print(json.dumps({"epochs":[{"chosen":e["chosen"],"cohorts":e["cohorts"],
                                  "offline_cost":e["offline_cost"],"summary":e["discovery_summary"]}
                                 for e in r["epochs"]],
                      "libraries":r["library_metadata"],"summary":r["summary"]},indent=2))


if __name__=="__main__":
    main()
