"""Frozen 2x2 library-size and incidence filtering ablation, with independent replay."""
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
from .pnp_library_incidence import indexed_reuse
from .pnp_evidence_benchmark import digest
from .pnp_abstraction_frontier import bytesize

SEED=171003
ARMS=("base_plain","base_indexed","expanded_plain","expanded_indexed")


def splits(source,failures,v17):
    if failures["seed"]==SEED:
        raise ValueError("seed overlap")
    old=prior_admission(source,failures,v17)
    seen={case_key(c) for cases in old.values() for c in cases}
    seen.update(case_key(c) for cases in prior_portfolio(source,failures,v17).values() for c in cases)
    seen.update(case_key(c) for c in prior_paths()+prior_horn())
    seen.update(case_key(c) for seed in (17103,17203) for c in suite(seed,24))
    for seed in (17801,17802,17803,17804,17805):
        seen.update(case_key(c) for c in generate(seed,24 if seed==17805 else 6))
    seen.update(case_key(c) for c in generate(17903,24))
    for rows in (source["rows"],failures["training"],failures["evaluation"],
                 v17["training"],v17["discovery"],v17["heldout"],v17["retrospective"]):
        seen.update(case_key(r["case"]) for r in rows)
    fresh=generate(SEED,24)
    keys={case_key(c) for c in fresh}
    if len(keys)!=len(fresh) or keys & seen:
        raise ValueError("normalized input overlap")
    return old["training"],{"fresh":fresh,"retrospective":generate(17903,24)}


def evaluate(c,indexes,base_count):
    n,f=c["n"],c["clauses"]
    outcomes={}
    offset=int(case_key(c)[:8],16)%len(ARMS)
    for a in ARMS[offset:]+ARMS[:offset]:
        b=budget()
        start=perf_counter()
        index=indexes[a.split("_")[0]]
        r=indexed_reuse(n,f,index,b) if a.endswith("_indexed") else reuse(n,f,index,b,shared_replay=True)
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
                         "examined":sum(v["examined"] for v in values),
                         "check_seconds":sum(v["check_seconds"] for v in hits),
                         "proof_bytes":sum(v["proof_bytes"] for v in hits),
                         "uses_added":sum(v["uses_added"] for v in hits)}
        if a.endswith("_indexed"):
            out["arms"][a]["incidence"]={k:sum(v["incidence"][k] for v in values)
                for k in ("considered","width_rejected","count_rejected","pair_rejected","matched_searches","snapshots","pair_checks","pair_cap_skips","filter_work")}
    for x,y in (("base_plain","base_indexed"),("expanded_plain","expanded_indexed"),
                ("base_plain","expanded_plain"),("base_indexed","expanded_indexed")):
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


def run(source,scheduler,failures,v17):
    audit_v17(source,scheduler,failures,v17)
    base=tuple(v17["library"])
    train_cases,cases=splits(source,failures,v17)
    trained=[train(c,Index(base)) for c in train_cases]
    expanded,lineage=admit(base,trained,offline_budget())
    indexes={"base":Index(base),"expanded":Index(expanded)}
    hashes={k:digest(v.templates) for k,v in indexes.items()}
    data={k:[evaluate(c,indexes,len(base)) for c in cs] for k,cs in cases.items()}
    if hashes!={k:digest(v.templates) for k,v in indexes.items()}:
        raise AssertionError("library mutation")
    return {"schema":"mathos-pnp-library-incidence-frontier/1","seed":SEED,"step_cap":STEPS,
            "upstream":[digest(x) for x in (source,scheduler,failures,v17)],
            "training":trained,"lineage":lineage,"library_hashes":hashes,
            "library_sizes":{"base":len(base),"expanded":len(expanded)},
            "data":data,"summary":summarize(data),"universal_obligation":"unresolved",
            "novel_theorem_verified":False,"p_equals_np_established":False,"p_not_equals_np_established":False}


def audit(source,scheduler,failures,v17,r):
    audit_v17(source,scheduler,failures,v17)
    if (r["schema"]!="mathos-pnp-library-incidence-frontier/1" or r["seed"]!=SEED
            or r["step_cap"]!=STEPS or r["upstream"]!=[digest(x) for x in (source,scheduler,failures,v17)]
            or r["universal_obligation"]!="unresolved"
            or any(r[k] is not False for k in ("novel_theorem_verified","p_equals_np_established","p_not_equals_np_established"))):
        raise ValueError("metadata mismatch")
    base=tuple(v17["library"])
    train_cases,cases=splits(source,failures,v17)
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
    indexes={"base":Index(base),"expanded":Index(expanded)}
    if (digest(lineage)!=digest(r["lineage"]) or r["library_hashes"]!={k:digest(v.templates) for k,v in indexes.items()}
            or r["library_sizes"]!={"base":len(base),"expanded":len(expanded)}):
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
                if a.endswith("_indexed"):
                    m=v["incidence"]
                    if (set(m)!={"considered","width_rejected","count_rejected","pair_rejected",
                                 "matched_searches","snapshots","pair_checks","pair_cap_skips","filter_work"}
                            or any(type(x) is not int or x<0 for x in m.values())
                            or m["matched_searches"]!=v["examined"]
                            or m["matched_searches"]+m["width_rejected"]+m["count_rejected"]+m["pair_rejected"]>m["considered"]
                            or m["filter_work"]>v["work"] or m["pair_cap_skips"]>m["pair_checks"]):
                        raise ValueError("incidence counters")
                if v["status"]=="verified":
                    proof=reconstruct(n,f,indexes[a.split("_")[0]],v["transfers"],budget())
                    independent_replay(n,f,proof)
                    if (sat or digest(proof)!=digest(v["proof"]) or v["proof_bytes"]!=bytesize(proof)
                            or v["uses_added"] is not any(i>=len(base) for i,_ in v["transfers"])):
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
    print(json.dumps({"library_sizes":r["library_sizes"],"summary":r["summary"]},indent=2))


if __name__=="__main__":
    main()
