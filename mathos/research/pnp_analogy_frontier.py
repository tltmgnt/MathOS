"""Compare automatic strengthened-premise analogy with exact retrieval."""
import argparse
import json
from pathlib import Path

from .pnp_evidence_benchmark import digest
from .pnp_knowledge_frontier import audit as audit_v16, ref, strengthening_control
from .pnp_knowledge_library import query, verify_query, budget
from .pnp_analogy import query_strengthened, verify_query_strengthened, find_strengthening
from .pnp_failure_synthesis import fresh_cases
from .pnp_abstraction_frontier import variants
from .pnp_structural_kernel import Exhausted
from .pnp_outcome_engine import checkpoint

SEED=17017


def cases(lib,count):
    rows=[]
    # For each template, replace one longest axiom by a strict subclause.
    # These are positive controls designed from known proofs, not discoveries.
    for i,e in enumerate(lib["entries"]):
        t=e["template"]
        n,f,emb=variants(t)
        f=f[:-1]  # omit the unrelated clause in variants()
        j=max(range(len(f)),key=lambda j:len(f[j]))
        if not f[j]:
            continue
        f[j]=f[j][1:]
        rows.append({"id":f"strengthened_{i:02d}","group":"positive_control",
                     "n":n,"clauses":[list(c) for c in f],"origin":e["id"]})
    rows.extend({"group":"fresh",**c} for c in fresh_cases(SEED,count))
    rows.extend([{"id":"one_unit","group":"negative_control","n":3,"clauses":[[1]]},
                 {"id":"empty","group":"negative_control","n":3,"clauses":[]}])
    return rows


def isolated_control():
    c=strengthening_control()
    t=c["template"]
    a=find_strengthening(c["n"],c["clauses"],t,budget())
    if a["status"]!="matched":
        raise AssertionError("automatic strengthening control missed")
    return {"n":c["n"],"clauses":c["clauses"],"template":t,"match":a,
            "exact_inclusion_accepted":False}


def summary(r):
    s={"cases":len(r["rows"]),"fresh_cases":0,"fresh_reference_unsat":0,
       "exact":{"matches":0,"fresh_matches":0,"work_steps":0},
       "strengthened":{"matches":0,"fresh_matches":0,"work_steps":0},
       "strengthened_only":0,"exact_only":0,"both_matched":0,"both_unknown":0,
       "fresh_strengthened_only":0,"positive_controls":0}
    for row in r["rows"]:
        fresh=row["case"]["group"]=="fresh"
        s["fresh_cases"]+=fresh
        s["fresh_reference_unsat"]+=fresh and not row["reference"]
        s["positive_controls"]+=row["case"]["group"]=="positive_control"
        for arm in ("exact","strengthened"):
            a=row[arm]
            m=a["decision"]=="unsat"
            s[arm]["matches"]+=m
            s[arm]["fresh_matches"]+=m and fresh
            s[arm]["work_steps"]+=a["work_steps"]
        e,a=(row[k]["decision"]=="unsat" for k in ("exact","strengthened"))
        s["both_matched" if e and a else "exact_only" if e else "strengthened_only" if a else "both_unknown"]+=1
        s["fresh_strengthened_only"]+=fresh and a and not e
    return s


def run(source,scheduler,failures,abstraction,knowledge,*,count=24,checkpoint_path=None):
    audit_v16(source,scheduler,failures,abstraction,knowledge)
    if failures["seed"]==SEED:
        raise ValueError("evaluation seed overlaps v13")
    lib=knowledge["library"]
    r={"schema":"mathos-pnp-analogy-frontier/1",
       "upstream":[digest(x) for x in (source,scheduler,failures,abstraction,knowledge)],
       "count":count,"rows":[],"completion":"running",
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        r["control"]=isolated_control()
        save()
        for case in cases(lib,count):
            n,f=case["n"],case["clauses"]
            reference=ref(n,f)
            exact=query(n,f,lib,indexed=True)
            verify_query(n,f,lib,exact)
            strengthened=query_strengthened(n,f,lib)
            if reference and any(a["decision"]=="unsat" for a in (exact,strengthened)):
                raise AssertionError("unsound analogy")
            if case["group"]=="positive_control" and reference:
                raise AssertionError("positive control is SAT")
            r["rows"].append({"case":case,"reference":reference,"exact":exact,"strengthened":strengthened})
            save()
        r["completion"]="completed"
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except (ValueError,AssertionError) as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["summary"]=summary(r)
    save()
    return r


def audit(source,scheduler,failures,abstraction,knowledge,r):
    audit_v16(source,scheduler,failures,abstraction,knowledge)
    if (r["schema"]!="mathos-pnp-analogy-frontier/1" or
            r["upstream"]!=[digest(x) for x in (source,scheduler,failures,abstraction,knowledge)] or
            r["completion"]!="completed" or failures["seed"]==SEED or
            r["universal_obligation"]!="unresolved" or
            any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))):
        raise ValueError("source or governance mismatch")
    if digest(r["control"])!=digest(isolated_control()):
        raise ValueError("automatic strengthening control mismatch")
    lib=knowledge["library"]
    expected=cases(lib,r["count"])
    if len(expected)!=len(r["rows"]):
        raise ValueError("missing evaluation rows")
    for case,row in zip(expected,r["rows"]):
        n,f=case["n"],case["clauses"]
        if row["case"]!=case or row["reference"] is not ref(n,f):
            raise ValueError("reference mismatch")
        if row["exact"]["indexed"] is not True or row["exact"]["limit"]!=4096 or row["strengthened"]["limit"]!=4096:
            raise ValueError("query configuration mismatch")
        verify_query(n,f,lib,row["exact"])
        verify_query_strengthened(n,f,lib,row["strengthened"])
        if row["reference"] and any(row[a]["decision"]=="unsat" for a in ("exact","strengthened")):
            raise ValueError("unsound analogy")
    if r["summary"]!=summary(r):
        raise ValueError("summary mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("benchmark","scheduler","failures","abstraction","knowledge"):
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
        paths=(a.benchmark,a.scheduler,a.failures,a.abstraction,a.knowledge)
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
