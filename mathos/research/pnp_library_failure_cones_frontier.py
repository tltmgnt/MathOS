"""Failure-directed offline abstraction; new orbit-disjoint evaluation."""
import argparse
from collections import Counter
import json
from pathlib import Path
from time import perf_counter

from .pnp_library_frontier import suite,case_key
from .pnp_library_admission_frontier import generate,splits as prior_admission,budget,offline_budget,STEPS
from .pnp_schema_portfolio_frontier import splits as prior_portfolio
from .pnp_implication_paths_frontier import fresh_cases as prior_paths,controls as path_controls
from .pnp_signed_horn_frontier import fresh as prior_horn
from .pnp_composite_paths_frontier import controls as composite_controls
from .pnp_library_orbit_split import Registry,select
from .pnp_library_orbit_split_frontier import audit as audit_prior,snapshots
from .pnp_library_admission import admit
from .pnp_library_failure_cones import discover,source_cones,matched_snapshots
from .pnp_library_ablation import independent_replay,oracle
from .pnp_proof_library import Index,reuse,reconstruct
from .pnp_evidence_benchmark import digest
from .pnp_abstraction_frontier import bytesize

SEED=171303
ARMS=("base","failure","success")

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
    corpus["previous_orbit_pool"]=generate(171203,96)
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
    return chosen,manifest


def baseline_and_sources(v17,prior):
    original=tuple(v17["library"])
    expanded,_=admit(original,prior["training"],offline_budget())
    idx,_,_,_=snapshots(original,expanded)
    base=idx["expanded_compact"].templates
    if digest(base)!=prior["library_hashes"]["expanded_compact"]:
        raise ValueError("baseline snapshot mismatch")
    return base,prior["data"]["fresh"]


def develop(rows):
    out=[]
    for row in rows:
        c=row["case"]
        b=budget()
        start=perf_counter()
        r=discover(c,b)
        r.update(work=b.steps,seconds=perf_counter()-start)
        if r["status"]=="verified" and oracle(c["n"],c["clauses"]):
            raise AssertionError("false resolution proof")
        out.append({"case":c,"baseline":row["arms"]["expanded_compact"],
                    "resolution":r})
    return out


def evaluate(c,indexes,base_count):
    n,f=c["n"],c["clauses"]
    outcomes={}
    offset=int(case_key(c)[:8],16)%len(ARMS)
    for a in ARMS[offset:]+ARMS[:offset]:
        b=budget()
        start=perf_counter()
        r=reuse(n,f,indexes[a],b,shared_replay=True)
        r.update(work=b.steps,seconds=perf_counter()-start)
        if r["status"]=="verified":
            start=perf_counter()
            independent_replay(n,f,r["proof"])
            r.update(check_seconds=perf_counter()-start,proof_bytes=bytesize(r["proof"]),
                     uses_added=any(i>=base_count for i,_ in r["transfers"]))
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
                         "proof_bytes":sum(v["proof_bytes"] for v in hits),
                         "uses_added":sum(v["uses_added"] for v in hits)}
    for x,y in (("base","failure"),("base","success"),("success","failure")):
        pairs=[(r["arms"][x]["status"]=="verified",r["arms"][y]["status"]=="verified") for r in rows]
        out["paired"][x+" -> "+y]={"gain":sum(not a and b for a,b in pairs),
                                     "loss":sum(a and not b for a,b in pairs),
                                     "both":sum(a and b for a,b in pairs)}
    return out


def summarize(rows):
    return {"fresh":summary(rows),**{f:summary([r for r in rows if r["case"]["family"]==f])
                 for f in ("random2","random3","mixed1234")}}


def development_summary(rows):
    out={}
    for group in ("failure","success"):
        rs=[r for r in rows if (r["baseline"]["status"]!="verified")==(group=="failure")]
        out[group]={"cases":len(rs),"resolution":dict(Counter(r["resolution"]["status"] for r in rs)),
                    "work":sum(r["resolution"]["work"] for r in rs),
                    "seconds":sum(r["resolution"]["seconds"] for r in rs)}
    return out


def run(source,scheduler,failures,v17,prior):
    audit_prior(source,scheduler,failures,v17,prior)
    base,old=baseline_and_sources(v17,prior)
    development=develop(old)
    b=offline_budget()
    start=perf_counter()
    libs,pools,count=matched_snapshots(base,development,b)
    cost={"work":b.steps,"seconds":perf_counter()-start}
    hashes={k:digest(v) for k,v in libs.items()}
    cases,manifest=splits(source,failures,v17)
    indexes={k:Index(v) for k,v in libs.items()}
    rows=[evaluate(c,indexes,len(base)) for c in cases]
    if hashes!={k:digest(v.templates) for k,v in indexes.items()}:
        raise AssertionError("snapshot mutation")
    return {"schema":"mathos-pnp-failure-cones-frontier/1","seed":SEED,"step_cap":STEPS,
            "upstream":[digest(x) for x in (source,scheduler,failures,v17,prior)],
            "development":development,"development_summary":development_summary(development),
            "pools":pools,"matched_count":count,"library_hashes":hashes,
            "library_sizes":{k:len(v) for k,v in libs.items()},"offline_cost":cost,
            "orbit_manifest":manifest,"rows":rows,"summary":summarize(rows),
            "universal_obligation":"unresolved","novel_theorem_verified":False,
            "p_equals_np_established":False,"p_not_equals_np_established":False}


def audit(source,scheduler,failures,v17,prior,r):
    audit_prior(source,scheduler,failures,v17,prior)
    if (r["schema"]!="mathos-pnp-failure-cones-frontier/1" or r["seed"]!=SEED
            or r["step_cap"]!=STEPS or r["upstream"]!=[digest(x) for x in (source,scheduler,failures,v17,prior)]
            or r["universal_obligation"]!="unresolved"
            or any(r[k] is not False for k in ("novel_theorem_verified","p_equals_np_established","p_not_equals_np_established"))):
        raise ValueError("metadata mismatch")
    base,old=baseline_and_sources(v17,prior)
    dev=r["development"]
    if len(old)!=len(dev):
        raise ValueError("development length")
    for a,b in zip(old,dev):
        if digest(a["case"])!=digest(b["case"]) or digest(a["arms"]["expanded_compact"])!=digest(b["baseline"]):
            raise ValueError("development source mismatch")
        v=b["resolution"]
        if type(v["work"]) is not int or not 0<=v["work"]<=STEPS:
            raise ValueError("offline search cap")
        if v["status"]=="verified":
            source_cones(b["case"],v,budget())
            if oracle(b["case"]["n"],b["case"]["clauses"]):
                raise ValueError("false resolution proof")
        elif v["status"] not in ("not_found","resource_exhausted") or any(k in v for k in ("dag","compressed")):
            raise ValueError("uncredited proof")
    libs,pools,count=matched_snapshots(base,dev,offline_budget())
    if (r["matched_count"]!=count or digest(r["pools"])!=digest(pools)
            or r["library_hashes"]!={k:digest(v) for k,v in libs.items()}
            or r["library_sizes"]!={k:len(v) for k,v in libs.items()}
            or r["development_summary"]!=development_summary(dev)):
        raise ValueError("admission mismatch")
    cases,manifest=splits(source,failures,v17)
    if digest(manifest)!=digest(r["orbit_manifest"]) or digest(cases)!=digest([x["case"] for x in r["rows"]]):
        raise ValueError("orbit split mismatch")
    indexes={k:Index(v) for k,v in libs.items()}
    for c,row in zip(cases,r["rows"]):
        n,f=c["n"],c["clauses"]
        sat=oracle(n,f)
        if row["reference_sat"] is not sat or set(row["arms"])!=set(ARMS):
            raise ValueError("reference mismatch")
        for a,v in row["arms"].items():
            if type(v["work"]) is not int or not 0<=v["work"]<=STEPS:
                raise ValueError("evaluation cap")
            if v["status"]=="verified":
                proof=reconstruct(n,f,indexes[a],v["transfers"],budget())
                independent_replay(n,f,proof)
                if (sat or digest(proof)!=digest(v["proof"]) or v["proof_bytes"]!=bytesize(proof)
                        or v["uses_added"] is not any(i>=len(base) for i,_ in v["transfers"])):
                    raise ValueError("proof mismatch")
            elif v["status"] not in ("not_found","transfer_limit","resource_exhausted") or any(
                    k in v for k in ("proof","transfers","uses_added")):
                raise ValueError("uncredited result")
    if r["summary"]!=summarize(r["rows"]):
        raise ValueError("aggregate mismatch")
    return True


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("benchmark","scheduler","failures","v17","prior"):
        p.add_argument("--"+k,type=Path,required=True)
    m=p.add_mutually_exclusive_group(required=True)
    m.add_argument("--checkpoint",type=Path)
    m.add_argument("--audit",type=Path)
    a=p.parse_args()
    files=(a.benchmark,a.scheduler,a.failures,a.v17,a.prior)
    inputs=tuple(json.loads(x.read_text()) for x in files)
    if a.audit:
        audit(*inputs,json.loads(a.audit.read_text()))
        print(json.dumps({"status":"positive_claims_replayed"}))
        return
    if a.checkpoint.resolve() in {x.resolve() for x in files}:
        p.error("cannot overwrite input")
    r=run(*inputs)
    a.checkpoint.write_text(json.dumps(r,indent=2,sort_keys=True))
    print(json.dumps({k:r[k] for k in ("development_summary","matched_count","library_sizes",
                   "offline_cost","orbit_manifest","summary")},indent=2))


if __name__=="__main__":
    main()
