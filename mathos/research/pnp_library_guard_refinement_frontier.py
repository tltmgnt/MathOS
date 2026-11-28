"""Frozen orbit-disjoint comparison of replay-only and proof-repair guard refinement."""
import argparse
from collections import Counter
import json
from pathlib import Path
from time import perf_counter

from .pnp_library_frontier import audit as audit_v17, suite, case_key
from .pnp_library_admission_frontier import (generate, splits as prior_admission,
                                            train, budget, offline_budget, STEPS)
from .pnp_schema_portfolio_frontier import splits as prior_portfolio
from .pnp_implication_paths_frontier import fresh_cases as prior_paths
from .pnp_signed_horn_frontier import fresh as prior_horn
from .pnp_schema_portfolio import verify
from .pnp_library_admission import admit
from .pnp_library_ablation import independent_replay, oracle
from .pnp_proof_library import Index, reuse, reconstruct
from .pnp_library_canonical import compact
from .pnp_library_orbit_split import Registry, select
from .pnp_library_guard_refinement import refine_library
from .pnp_implication_paths_frontier import controls as path_controls
from .pnp_composite_paths_frontier import controls as composite_controls
from .pnp_evidence_benchmark import digest
from .pnp_abstraction_frontier import bytesize

SEED=171403
ARMS=("baseline","replay_only","repair")


def splits(source,failures,v17):
    if failures["seed"]==SEED:
        raise ValueError("seed overlap")
    old=prior_admission(source,failures,v17)
    corpus={}
    corpus["upstream"]=[r["case"] for rows in (source["rows"],failures["training"],
                        failures["evaluation"],v17["training"],v17["discovery"],
                        v17["heldout"],v17["retrospective"]) for r in rows]
    corpus["ablation_adaptive"]=[c for seed in (17103,17203) for c in suite(seed,24)]
    corpus["parameterized_controls"]=prior_paths()+path_controls()+prior_horn()+composite_controls()
    corpus["portfolio"]=[c for cases in prior_portfolio(source,failures,v17).values() for c in cases]
    corpus["admission"]=[c for cases in old.values() for c in cases]
    corpus["selection"]=[c for seed in (17801,17802,17803,17804,17805)
                         for c in generate(seed,24 if seed==17805 else 6)]
    corpus["retrieval"]=[c for seed in (17903,171003,171103) for c in generate(seed,24)]
    corpus["earlier_orbit_pools"]=[c for seed in (171203,171303) for c in generate(seed,96)]
    registry=Registry()
    b=offline_budget()
    for rows in corpus.values():
        for c in rows:
            registry.register(c,b,prior=True)
    manifest={"corpus":{k:{"cases":len(v),"sha256":digest(v)} for k,v in corpus.items()},
              "prior_counts":dict(registry.counts),"prior_registry_sha256":registry.fingerprint(),
              "orbit_cap":registry.cap,"max_active":registry.max_active,"pool_seed":SEED}
    pool=generate(SEED,96)
    chosen,reasons=select(registry,pool,b,per_family=24)
    manifest.update(pool_sha256=digest(pool),pool_cases=len(pool),selection=reasons,
                    final_registry_sha256=registry.fingerprint(),selected_sha256=digest(chosen),
                    screening_work=b.steps)
    return old["training"],{"fresh":chosen},manifest


def evaluate(c,indexes,source_ids,base_count):
    n,f=c["n"],c["clauses"]
    outcomes={}
    offset=int(case_key(c)[:8],16)%len(ARMS)
    for a in ARMS[offset:]+ARMS[:offset]:
        b=budget()
        start=perf_counter()
        index=indexes[a]
        r=reuse(n,f,index,b,shared_replay=True)
        r.update(work=b.steps,seconds=perf_counter()-start)
        if r["status"]=="verified":
            start=perf_counter()
            independent_replay(n,f,r["proof"])
            r.update(check_seconds=perf_counter()-start,proof_bytes=bytesize(r["proof"]),
                     uses_added=any(source_ids[a][i]>=base_count for i,_ in r["transfers"]))
        outcomes[a]=r
    sat=oracle(n,f)
    if sat and any(r["status"]=="verified" for r in outcomes.values()):
        raise AssertionError("false refutation")
    return {"case":c,"reference_sat":sat,"arms":outcomes}


def summary(rows):
    out={"cases":len(rows),"unsat":sum(not r["reference_sat"] for r in rows),"arms":{},"paired":{}}
    for a in ARMS:
        values=[r["arms"][a] for r in rows]
        hits=[v for v in values if v["status"]=="verified"]
        out["arms"][a]={"verified":len(hits),"statuses":dict(Counter(v["status"] for v in values)),
                         "work":sum(v["work"] for v in values),"seconds":sum(v["seconds"] for v in values),
                         "examined":sum(v["examined"] for v in values),
                         "check_seconds":sum(v["check_seconds"] for v in hits),
                         "proof_bytes":sum(v["proof_bytes"] for v in hits),
                         "uses_added":sum(v["uses_added"] for v in hits)}
    for x,y in (("baseline","replay_only"),("baseline","repair"),("replay_only","repair")):
        pairs=[(r["arms"][x]["status"]=="verified",r["arms"][y]["status"]=="verified") for r in rows]
        out["paired"][x+" -> "+y]={"gain":sum(not a and b for a,b in pairs),
                                     "loss":sum(a and not b for a,b in pairs),
                                     "both":sum(a and b for a,b in pairs)}
    return out


def summarize(data):
    s={k:summary(v) for k,v in data.items()}
    for f in ("random2","random3","mixed1234"):
        s[f]=summary([r for r in data["fresh"] if r["case"]["family"]==f])
    return s


def snapshots(base,expanded):
    b=offline_budget()
    baseline,compaction=compact(expanded,b)
    ids=[d["source"] for d in compaction if d["status"]=="kept"]
    libs={"baseline":baseline}
    source_ids={"baseline":ids}
    decisions={"compaction":compaction}
    cost={}
    for name,repair in (("replay_only",False),("repair",True)):
        start=perf_counter()
        lib,records=refine_library(baseline,allow_repair=repair)
        libs[name]=lib
        source_ids[name]=list(ids)
        decisions[name]=records
        cost[name]={"work":sum(r["work"] for r in records),"seconds":perf_counter()-start}
    return {k:Index(libs[k]) for k in ARMS},source_ids,decisions,cost


def refinement_summary(indexes,decisions):
    out={}
    for a in ARMS:
        lib=indexes[a].templates
        out[a]={"guards":sum(len(t["axioms"]) for t in lib),
                "steps":sum(len(t["steps"]) for t in lib),
                "bytes":bytesize(lib)}
        if a!="baseline":
            rs=decisions[a]
            out[a].update(minimal=sum(r["deletion_minimal"] for r in rs),
                          statuses=dict(Counter(r["status"] for r in rs)),
                          deletions=dict(Counter(d["status"] for r in rs for d in r["trace"])))
    return out


def run(source,scheduler,failures,v17):
    audit_v17(source,scheduler,failures,v17)
    base=tuple(v17["library"])
    train_cases,cases,manifest=splits(source,failures,v17)
    trained=[train(c,Index(base)) for c in train_cases]
    expanded,lineage=admit(base,trained,offline_budget())
    indexes,source_ids,decisions,cost=snapshots(base,expanded)
    hashes={k:digest(v.templates) for k,v in indexes.items()}
    data={k:[evaluate(c,indexes,source_ids,len(base)) for c in cs] for k,cs in cases.items()}
    if hashes!={k:digest(v.templates) for k,v in indexes.items()}:
        raise AssertionError("library mutation")
    return {"schema":"mathos-pnp-library-guard-refinement-frontier/1","seed":SEED,"step_cap":STEPS,
            "upstream":[digest(x) for x in (source,scheduler,failures,v17)],
            "training":trained,"lineage":lineage,"library_hashes":hashes,"orbit_manifest":manifest,
            "library_sizes":{k:len(v.templates) for k,v in indexes.items()},
            "refinement":decisions,"refinement_cost":cost,"source_ids":source_ids,
            "refinement_summary":refinement_summary(indexes,decisions),
            "data":data,"summary":summarize(data),"universal_obligation":"unresolved",
            "novel_theorem_verified":False,"p_equals_np_established":False,"p_not_equals_np_established":False}


def audit(source,scheduler,failures,v17,r):
    audit_v17(source,scheduler,failures,v17)
    if (r["schema"]!="mathos-pnp-library-guard-refinement-frontier/1" or r["seed"]!=SEED
            or r["step_cap"]!=STEPS or r["upstream"]!=[digest(x) for x in (source,scheduler,failures,v17)]
            or r["universal_obligation"]!="unresolved"
            or any(r[k] is not False for k in ("novel_theorem_verified","p_equals_np_established","p_not_equals_np_established"))):
        raise ValueError("metadata mismatch")
    base=tuple(v17["library"])
    train_cases,cases,manifest=splits(source,failures,v17)
    if digest(manifest)!=digest(r["orbit_manifest"]):
        raise ValueError("orbit screening mismatch")
    if digest(train_cases)!=digest([row["case"] for row in r["training"]]):
        raise ValueError("training split")
    for c,row in zip(train_cases,r["training"]):
        v=row["result"]
        if type(v["work"]) is not int or not 0<=v["work"]<=STEPS:
            raise ValueError("training work")
        if v["status"]=="verified":
            proof=verify(c["n"],c["clauses"],Index(base),v["recipe"],budget())
            independent_replay(c["n"],c["clauses"],proof)
            if oracle(c["n"],c["clauses"]) or digest(proof)!=digest(v["proof"]):
                raise ValueError("training certificate")
        elif v["status"] not in ("not_found","resource_exhausted") or any(k in v for k in ("proof","recipe")):
            raise ValueError("uncredited training")
    expanded,lineage=admit(base,r["training"],offline_budget())
    indexes,source_ids,decisions,_=snapshots(base,expanded)
    if (digest(lineage)!=digest(r["lineage"]) or r["library_hashes"]!={k:digest(v.templates) for k,v in indexes.items()}
            or r["library_sizes"]!={k:len(v.templates) for k,v in indexes.items()}
            or digest(decisions)!=digest(r["refinement"]) or source_ids!=r["source_ids"]
            or r["refinement_summary"]!=refinement_summary(indexes,decisions)):
        raise ValueError("library lineage")
    if set(r["data"])!=set(cases):
        raise ValueError("split mismatch")
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
                    raise ValueError("work cap")
                if v["status"]=="verified":
                    proof=reconstruct(n,f,indexes[a],v["transfers"],budget())
                    independent_replay(n,f,proof)
                    if (sat or digest(proof)!=digest(v["proof"]) or v["proof_bytes"]!=bytesize(proof)
                            or v["uses_added"] is not any(source_ids[a][i]>=len(base) for i,_ in v["transfers"])):
                        raise ValueError("proof mismatch")
                elif v["status"] not in ("not_found","transfer_limit","resource_exhausted") or any(
                        k in v for k in ("proof","transfers","uses_added")):
                    raise ValueError("uncredited result")
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
    print(json.dumps({k:r[k] for k in ("orbit_manifest","library_sizes","refinement_summary",
                                      "refinement_cost","summary")},indent=2))


if __name__=="__main__":
    main()
