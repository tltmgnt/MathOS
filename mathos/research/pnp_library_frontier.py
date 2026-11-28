"""Frozen-split v17 experiment; no target solver fallback is credited."""
import argparse
import json
import random
import time
from pathlib import Path

from .pnp_abstraction_frontier import targets, reference, bytesize
from .pnp_evidence_benchmark import digest
from .pnp_failure_synthesis import fresh_cases
from .pnp_proof_abstraction import compress, find_embedding, verify_embedding, _original_clauses
from .pnp_resolution_refutation import propose
from .pnp_structural_kernel import Budget, Exhausted
from .pnp_proof_library import build, Index, reuse, reconstruct, verify_certificate, mapped, clause

TRAIN, DISCOVERY, HOLDOUT = 17001, 17002, 17003
RETROSPECTIVE = 15015


def budget():
    return Budget(seconds=15,max_steps=4_000_000,max_cells=100_000)


def suite(seed, count):
    # Separate generators; no template is consulted, planted or transformed.
    out = [{**c,"family":"random3"} for c in fresh_cases(seed,count)]
    rng = random.Random(seed + 100000)
    for i in range(count):
        n = rng.randint(5,9)
        f = [[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),2)]
             for _ in range(2*n)]
        out.append({"id":f"random2_{i:02d}","family":"random2","n":n,"clauses":f})
    return out


def case_key(c):
    return digest(sorted(_original_clauses(c["n"],c["clauses"])))


def baseline(case, templates, b):
    n,f = case["n"],case["clauses"]
    statuses = []
    try:
        for i,t in enumerate(templates):
            a = find_embedding(n,f,t,b)
            statuses.append({"record":i,"status":a["status"],"candidates":a["candidates"],
                             "template_n":t["n"],"template_widths":sorted(set(map(len,t["axioms"])))})
            if a["status"] == "matched":
                verify_embedding(n,f,t,a["embedding"],b)
                known = list(map(tuple,t["axioms"]))
                for p,q,v in t["steps"]:
                    known.append(clause((set(known[p])-{v}) | (set(known[q])-{-v})))
                expanded = [mapped(c,a["embedding"]) for c in known[len(t["axioms"]):]]
                verify_certificate(n,f,expanded,budget())
                return {"status":"verified","record":i,"embedding":a["embedding"],
                        "certificate_bytes":bytesize({"template":t,"embedding":a["embedding"]}),
                        "expanded_bytes":bytesize(expanded),"attempts":statuses}
    except Exhausted:
        return {"status":"resource_exhausted","attempts":statuses}
    return {"status":"candidate_limit" if any(a["status"]=="candidate_limit" for a in statuses)
            else "not_found","attempts":statuses}


def measure(case, templates, index, *, compose=True, subsumption=True):
    n,f = case["n"],case["clauses"]
    b = budget()
    start = time.perf_counter()
    old = baseline(case,templates,b)
    old.update(work=b.steps,seconds=time.perf_counter()-start)
    b = budget()
    start = time.perf_counter()
    new = reuse(n,f,index,b,compose=compose,subsumption=subsumption)
    new.update(work=b.steps,seconds=time.perf_counter()-start)
    if new["status"] == "verified":
        check = budget()
        start = time.perf_counter()
        replay = reconstruct(n,f,index,new["transfers"],check)
        if replay != new["proof"]:
            raise AssertionError("reconstruction mismatch")
        new.update(verification_work=check.steps,verification_seconds=time.perf_counter()-start,
                   expanded_bytes=bytesize(replay),recipe_bytes=bytesize(new["transfers"]),
                   standalone_bytes=bytesize({"transfers":new["transfers"],
                     "templates":{i:index.templates[i] for i,_ in new["transfers"]}}))
    ref = reference(n,f)
    if ref and any(x["status"]=="verified" for x in (old,new)):
        raise AssertionError("false UNSAT transfer")
    return {"case":case,"reference_sat":ref,"v15":old,"v17":new}


def totals(rows):
    result = {"cases":len(rows),"unsat":sum(not r["reference_sat"] for r in rows)}
    for k in ("v15","v17"):
        verified = [r[k] for r in rows if r[k]["status"]=="verified"]
        result[k] = {"verified":len(verified),"work":sum(r[k]["work"] for r in rows),
                     "seconds":sum(r[k]["seconds"] for r in rows),
                     "expanded_bytes":sum(r["expanded_bytes"] for r in verified),
                     "statuses":{s:sum(r[k]["status"]==s for r in rows) for s in
                        sorted({r[k]["status"] for r in rows})}}
    result["v17"].update(recipe_bytes=sum(r["v17"].get("recipe_bytes",0) for r in rows),
                         standalone_bytes=sum(r["v17"].get("standalone_bytes",0) for r in rows),
                         verification_work=sum(r["v17"].get("verification_work",0) for r in rows),
                         composed=sum(len(r["v17"].get("transfers",[]))>1 for r in rows))
    result["v15"]["certificate_bytes"]=sum(r["v15"].get("certificate_bytes",0) for r in rows)
    return result


def run(source,scheduler,failures):
    if failures["seed"] in (TRAIN,DISCOVERY,HOLDOUT,RETROSPECTIVE):
        raise ValueError("upstream seed overlaps")
    work = targets(source,scheduler,failures)
    old = [compress(c["n"],c["clauses"],p,budget())["template"] for c,p in work]
    train, discovery, heldout = suite(TRAIN,12),suite(DISCOVERY,8),suite(HOLDOUT,16)
    retrospective = [{**c,"family":"random3"} for c in fresh_cases(RETROSPECTIVE,16)]
    # Require disjoint exact normalized inputs; not a proof of orbit disjointness.
    seen = {case_key(c) for c,_ in work}
    for split in (train,discovery,heldout,retrospective):
        keys = {case_key(c) for c in split}
        if len(keys)!=len(split) or seen.intersection(keys):
            raise ValueError("duplicate normalized input across splits")
        seen.update(keys)
    extra, training = [], []
    for c in train:
        b=budget()
        start=time.perf_counter()
        try:
            p=propose(c["n"],c["clauses"],b,width=8)
            t=compress(c["n"],c["clauses"],p,b) if p is not None else None
            status="verified" if t is not None else "not_refuted"
            if t is not None:
                extra.append(t["template"])
        except Exhausted:
            t,status=None,"resource_exhausted"
        training.append({"case":c,"status":status,"compact":t,
                         "work":b.steps,"seconds":time.perf_counter()-start})
    b=Budget(seconds=60,max_steps=25_000_000)
    start=time.perf_counter()
    original_library,original_refinement=build(old,b)
    library,refinement=build(old+extra,b)
    build_cost={"work":b.steps,"seconds":time.perf_counter()-start}
    index=Index(library)
    frozen=digest(library)
    # Discovery diagnostics do not update or select the library.
    d=[measure(c,old,index) for c in discovery]
    historical=[measure(c,old,Index(original_library),compose=False,subsumption=False)
                for c in retrospective]
    h=[measure(c,old,index) for c in heldout]
    if digest(library)!=frozen:
        raise AssertionError("library changed during evaluation")
    return {"schema":"mathos-pnp-proof-library/1","upstream":[digest(x) for x in (source,scheduler,failures)],
            "seeds":{"training":TRAIN,"discovery":DISCOVERY,"heldout":HOLDOUT,"retrospective":RETROSPECTIVE},
            "v15_source_templates":old,"training":training,"library":library,"library_sha256":frozen,
            "library_bytes":bytesize(library),"original_library":original_library,
            "refinement":refinement,"original_refinement":original_refinement,"build_cost":build_cost,
            "discovery":d,"retrospective":historical,"heldout":h,
            "summary":{"retrospective":totals(historical),"discovery":totals(d),
                       "heldout":totals(h),"heldout_random3":totals([r for r in h if r["case"]["family"]=="random3"]),
                       "heldout_random2":totals([r for r in h if r["case"]["family"]=="random2"])},
            "universal_obligation":"unresolved","novel_theorem_verified":False,
            "p_equals_np_established":False,"p_not_equals_np_established":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("benchmark","scheduler","failures","checkpoint"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    paths=(a.benchmark,a.scheduler,a.failures)
    if a.checkpoint.resolve() in {x.resolve() for x in paths}:
        p.error("cannot overwrite upstream evidence")
    result=run(*(json.loads(x.read_text()) for x in paths))
    a.checkpoint.parent.mkdir(parents=True,exist_ok=True)
    a.checkpoint.write_text(json.dumps(result,sort_keys=True,indent=2))
    print(json.dumps(result["summary"],indent=2))


if __name__=="__main__":
    main()
