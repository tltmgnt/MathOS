"""Evaluate indexed proof retrieval and certified premise strengthening."""
import argparse
import json
from pathlib import Path
from .pnp_evidence_benchmark import digest, canonical
from .pnp_abstraction_frontier import audit as audit_v15, variants
from .pnp_failure_synthesis import fresh_cases
from .pnp_structural_kernel import normalize, brute, Exhausted
from .pnp_resolution_refutation import propose
from .pnp_proof_abstraction import compress, verify_embedding
from .pnp_knowledge_library import build, verify_library, query, verify_query, strengthen, verify_strengthening, budget
from .pnp_outcome_engine import checkpoint

SEED=16016


def templates(abstraction):
    result=[r["compact"]["template"] for r in abstraction["records"]]
    # Explicit synthetic controls, not discoveries from fresh evaluation.
    controls=[(2,[(1,),(-1,2),(-2,)]),
              (2,[(1,2),(-1,2),(1,-2),(-1,-2)]),
              (3,[(1,),(-1,2),(-2,3),(-3,)]),
              (3,[(1,2,3),(1,2,-3),(1,-2,3),(1,-2,-3),
                   (-1,2,3),(-1,2,-3),(-1,-2,3),(-1,-2,-3)])]
    for n,f in controls:
        p=propose(n,f,budget(),width=8)
        if p is None:
            raise AssertionError("synthetic control not refuted")
        result.append(compress(n,f,p,budget())["template"])
    # Deliberate exact duplicate tests certified deduplication.
    result.append(result[-1])
    return result


def cases(lib,count):
    rows=[]
    for i,e in enumerate(lib["entries"]):
        n,f,_=variants(e["template"])
        rows.append({"id":f"embedded_{i:02d}","group":"positive_control","n":n,"clauses":[list(c) for c in f]})
    rows.extend({"group":"fresh",**c} for c in fresh_cases(SEED,count))
    rows.extend([{"id":"single_clause","group":"negative_control","n":3,"clauses":[[1,2,3]]},
                 {"id":"empty_conjunction","group":"negative_control","n":0,"clauses":[]}])
    return rows


def ref(n,f):
    nn,g,_=normalize(n,f)
    if nn>14:
        raise ValueError("reference input too large")
    return brute(nn,g,budget())


def strengthening_control():
    f=[(1,2),(-1,2),(1,-2),(-1,-2)]
    t=compress(2,f,propose(2,f,budget()),budget())["template"]
    # Strictly stronger target: replace one pair clause by a unit.
    target=[(1,),(-1,2),(1,-2),(-1,-2)]
    w=strengthen(2,target,t,(1,2),budget())
    if w is None or ref(2,target):
        raise AssertionError("strengthening control failed")
    try:
        verify_embedding(2,target,t,(1,2),budget())
    except ValueError:
        exact=False
    else:
        exact=True
    if exact:
        raise AssertionError("expected exact inclusion rejection")
    return {"n":2,"clauses":target,"template":t,"embedding":(1,2),"witnesses":w,
            "exact_inclusion_accepted":False,"strengthening_verified":True}


def summary(r):
    rows=r["rows"]
    out={"input_templates":len(r["library"]["input_ids"]),"retained_templates":len(r["library"]["entries"]),
         "covered_templates":sum(d["status"]=="covered" for d in r["library"]["dispositions"]),
         "cases":len(rows),"fresh_cases":sum(x["case"]["group"]=="fresh" for x in rows),
         "fresh_reference_unsat":sum(x["case"]["group"]=="fresh" and not x["reference"] for x in rows),
         "indexed":{"matches":0,"fresh_matches":0,"attempts":0,"work_steps":0},
         "linear":{"matches":0,"fresh_matches":0,"attempts":0,"work_steps":0},
         "strengthening_verified":r.get("strengthening",{}).get("strengthening_verified",False)}
    for x in rows:
        for arm in ("indexed","linear"):
            a=x[arm]
            m=a["decision"]=="unsat"
            out[arm]["matches"]+=m
            out[arm]["fresh_matches"]+=m and x["case"]["group"]=="fresh"
            out[arm]["attempts"]+=len(a["attempts"])
            out[arm]["work_steps"]+=a["work_steps"]
    return out


def run(source,scheduler,failures,abstraction,*,count=24,checkpoint_path=None):
    audit_v15(source,scheduler,failures,abstraction)
    if failures["seed"]==SEED:
        raise ValueError("evaluation seed overlaps v13")
    ts=templates(abstraction)
    lib=build(ts)
    r={"schema":"mathos-pnp-knowledge-frontier/1","upstream":[digest(x) for x in (source,scheduler,failures,abstraction)],
       "count":count,"library":lib,"rows":[],"completion":"running",
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        r["strengthening"]=strengthening_control()
        save()
        for case in cases(lib,count):
            n,f=case["n"],case["clauses"]
            reference=ref(n,f)
            row={"case":case,"reference":reference}
            for arm in ("indexed","linear"):
                a=query(n,f,lib,indexed=arm=="indexed")
                verify_query(n,f,lib,a)
                if reference and a["decision"]=="unsat":
                    raise AssertionError("retrieval contradicts reference")
                row[arm]=a
            r["rows"].append(row)
            save()
        r["completion"]="completed"
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except (ValueError,AssertionError) as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["summary"]=summary(r)
    save()
    return r


def audit(source,scheduler,failures,abstraction,r):
    audit_v15(source,scheduler,failures,abstraction)
    if (r["schema"]!="mathos-pnp-knowledge-frontier/1" or
            r["upstream"]!=[digest(x) for x in (source,scheduler,failures,abstraction)] or
            r["completion"]!="completed" or failures["seed"]==SEED or
            r["universal_obligation"]!="unresolved" or
            any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))):
        raise ValueError("source or governance mismatch")
    lib=r["library"]
    verify_library(templates(abstraction),lib)
    c=r["strengthening"]
    if digest(c)!=digest(strengthening_control()):
        raise ValueError("strengthening control mismatch")
    verify_strengthening(c["n"],c["clauses"],c["template"],c["embedding"],c["witnesses"],budget())
    expected=cases(lib,r["count"])
    if len(expected)!=len(r["rows"]):
        raise ValueError("incomplete evaluation")
    for case,x in zip(expected,r["rows"]):
        n,f=case["n"],case["clauses"]
        if x["case"]!=case or x["reference"] is not ref(n,f):
            raise ValueError("reference mismatch")
        for arm in ("indexed","linear"):
            a=x[arm]
            if a["indexed"]!=(arm=="indexed") or a["limit"]!=4096:
                raise ValueError("arm configuration mismatch")
            verify_query(n,f,lib,a)
            if x["reference"] and a["decision"]=="unsat":
                raise ValueError("unsound retrieval")
    if r["summary"]!=summary(r):
        raise ValueError("summary mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("benchmark","scheduler","failures","abstraction"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    p.add_argument("--count",type=int,default=24)
    a=p.parse_args(argv)
    def read(path):
        if path.stat().st_size>32_000_000:
            raise ValueError("JSON exceeds 32 MB")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        paths=(a.benchmark,a.scheduler,a.failures,a.abstraction)
        inputs=tuple(read(x) for x in paths)
        if a.audit:
            audit(*inputs,read(a.audit))
            print(json.dumps({"status":"replayed","universal_obligation":"unresolved"}))
            return 0
        if a.checkpoint and a.checkpoint.resolve() in {x.resolve() for x in paths}:
            raise ValueError("cannot overwrite upstream evidence")
        r=run(*inputs,count=a.count,checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return int(r["completion"]!="completed")
    except (OSError,ValueError,KeyError,TypeError,Exhausted) as exc:
        p.error(str(exc))


if __name__=="__main__":
    raise SystemExit(main())
