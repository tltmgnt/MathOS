"""Evaluate inference-derived premise transfer against direct analogy."""
import argparse
import json
from pathlib import Path

from .pnp_evidence_benchmark import digest
from .pnp_analogy_frontier import audit as audit_v17
from .pnp_knowledge_frontier import ref, strengthening_control
from .pnp_knowledge_library import build
from .pnp_analogy import query_strengthened, verify_query_strengthened
from .pnp_semantic_implication import transfer, verify_transfer, MAX_WIDTH, MAX_DERIVED, MAX_PAIRS
from .pnp_failure_synthesis import fresh_cases
from .pnp_structural_kernel import Exhausted
from .pnp_outcome_engine import checkpoint

SEED=18018


def lift(t,*,distinct=False):
    """Replace each premise C by (C OR z) AND (C OR NOT z)."""
    n=t["n"]
    f=[]
    for i,c in enumerate(t["axioms"]):
        z=n+1+i if distinct else n+1
        f.extend([list(c)+[z],list(c)+[-z]])
    return (n+len(t["axioms"]) if distinct else n+1),f


def control():
    t=strengthening_control()["template"]
    n,f=lift(t,distinct=True)
    lib=build([t])
    raw=query_strengthened(n,f,lib)
    semantic=transfer(n,f,lib)
    if (raw["decision"]!="unknown" or semantic["decision"]!="unsat" or
            semantic["reason"]!="template_transfer" or ref(n,f)):
        raise AssertionError("isolated implication-only control failed")
    return {"n":n,"clauses":f,"library":lib,"raw":raw,"semantic":semantic}


def cases(lib,count):
    rows=[]
    for i,e in enumerate(lib["entries"]):
        n,f=lift(e["template"])
        rows.append({"id":f"lifted_{i:02d}","group":"positive_control","n":n,"clauses":f})
    rows.extend({"group":"fresh",**c} for c in fresh_cases(SEED,count))
    rows.extend([{"id":"direct_units","group":"direct_control","n":1,"clauses":[[1],[-1]]},
                 {"id":"satisfiable_chain","group":"negative_control","n":3,"clauses":[[1,2],[-2,3]]}])
    return rows


def summary(rows):
    s={"cases":len(rows),"fresh_cases":0,"fresh_reference_unsat":0,
       "raw_matches":0,"semantic_decisions":0,"template_transfers":0,
       "direct_refutations":0,"semantic_only":0,"raw_only":0,
       "fresh_raw_matches":0,"fresh_semantic_decisions":0,
       "fresh_semantic_only":0,"fresh_template_transfers":0,
       "derived_clauses":0,"closure_work_steps":0,
       "raw_match_work_steps":0,"augmented_match_work_steps":0}
    for row in rows:
        fresh=row["case"]["group"]=="fresh"
        raw=row["raw"]["decision"]=="unsat"
        sem=row["semantic"]
        decided=sem["decision"]=="unsat"
        template=sem["reason"]=="template_transfer"
        s["fresh_cases"]+=fresh
        s["fresh_reference_unsat"]+=fresh and not row["reference"]
        s["raw_matches"]+=raw
        s["semantic_decisions"]+=decided
        s["template_transfers"]+=template
        s["direct_refutations"]+=sem["reason"]=="direct_empty_clause"
        s["semantic_only"]+=decided and not raw
        s["raw_only"]+=raw and not decided
        s["fresh_raw_matches"]+=fresh and raw
        s["fresh_semantic_decisions"]+=fresh and decided
        s["fresh_semantic_only"]+=fresh and decided and not raw
        s["fresh_template_transfers"]+=fresh and template
        s["derived_clauses"]+=len(sem["closure"]["steps"])
        s["closure_work_steps"]+=sem["closure"]["work_steps"]
        s["raw_match_work_steps"]+=row["raw"]["work_steps"]
        s["augmented_match_work_steps"]+=sem["query"]["work_steps"] if sem["query"] else 0
    return s


def run(source,scheduler,failures,abstraction,knowledge,analogy,*,count=24,checkpoint_path=None):
    inputs=(source,scheduler,failures,abstraction,knowledge,analogy)
    audit_v17(*inputs)
    if failures["seed"]==SEED:
        raise ValueError("evaluation seed overlaps v13")
    lib=knowledge["library"]
    r={"schema":"mathos-pnp-semantic-frontier/1","upstream":[digest(x) for x in inputs],
       "count":count,"rows":[],"completion":"running","universal_obligation":"unresolved",
       "p_equals_np_established":False,"p_not_equals_np_established":False,"novel_theorem_verified":False}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        r["control"]=control()
        save()
        for case in cases(lib,count):
            n,f=case["n"],case["clauses"]
            reference=ref(n,f)
            raw=query_strengthened(n,f,lib)
            sem=transfer(n,f,lib)
            if reference and (raw["decision"]=="unsat" or sem["decision"]=="unsat"):
                raise AssertionError("unsound implication transfer")
            if case["group"]=="positive_control" and reference:
                raise AssertionError("lifted control is SAT")
            r["rows"].append({"case":case,"reference":reference,"raw":raw,"semantic":sem})
            save()
        r["completion"]="completed"
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except (ValueError,AssertionError) as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["summary"]=summary(r["rows"])
    save()
    return r


def audit(source,scheduler,failures,abstraction,knowledge,analogy,r):
    inputs=(source,scheduler,failures,abstraction,knowledge,analogy)
    audit_v17(*inputs)
    if (r["schema"]!="mathos-pnp-semantic-frontier/1" or r["upstream"]!=[digest(x) for x in inputs] or
            r["completion"]!="completed" or failures["seed"]==SEED or r["universal_obligation"]!="unresolved" or
            any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))):
        raise ValueError("source or governance mismatch")
    c=r["control"]
    expected=control()
    if (c["n"]!=expected["n"] or c["clauses"]!=expected["clauses"] or
            digest(c["library"])!=digest(expected["library"])):
        raise ValueError("control provenance mismatch")
    verify_query_strengthened(c["n"],c["clauses"],c["library"],c["raw"])
    verify_transfer(c["n"],c["clauses"],c["library"],c["semantic"])
    if c["raw"]["decision"]!="unknown" or c["semantic"]["reason"]!="template_transfer":
        raise ValueError("control decision mismatch")
    lib=knowledge["library"]
    expected=cases(lib,r["count"])
    if len(expected)!=len(r["rows"]):
        raise ValueError("incomplete evaluation")
    for case,row in zip(expected,r["rows"]):
        n,f=case["n"],case["clauses"]
        if row["case"]!=case or row["reference"] is not ref(n,f):
            raise ValueError("reference mismatch")
        a=row["semantic"]["closure"]
        if (a["width"],a["derived_limit"],a["pair_limit"])!=(MAX_WIDTH,MAX_DERIVED,MAX_PAIRS) or row["raw"]["limit"]!=4096:
            raise ValueError("closure configuration mismatch")
        if row["semantic"]["query"] is not None and row["semantic"]["query"]["limit"]!=4096:
            raise ValueError("query configuration mismatch")
        verify_query_strengthened(n,f,lib,row["raw"])
        verify_transfer(n,f,lib,row["semantic"])
        if row["reference"] and any(row[k]["decision"]=="unsat" for k in ("raw","semantic")):
            raise ValueError("unsound implication")
    if r["summary"]!=summary(r["rows"]):
        raise ValueError("summary mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    names=("benchmark","scheduler","failures","abstraction","knowledge","analogy")
    for name in names:
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
        paths=tuple(getattr(a,k) for k in names)
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
