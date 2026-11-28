"""Audit multi-stage implication and compact retrieval on a fresh suite."""
import argparse
import json
from pathlib import Path
from .pnp_evidence_benchmark import digest
from .pnp_semantic_frontier import audit as audit_v18, lift
from .pnp_semantic_implication import transfer, verify_transfer
from .pnp_knowledge_frontier import ref, strengthening_control
from .pnp_knowledge_library import build
from .pnp_guided_inference import investigate, verify_investigation
from .pnp_failure_synthesis import fresh_cases
from .pnp_structural_kernel import Exhausted
from .pnp_outcome_engine import checkpoint

SEED=19019


def controls():
    t=strengthening_control()["template"]
    # Two independent padding variables per premise (shared across premises).
    n,f=lift(t)
    g=[list(c)+[s*(n+1)] for c in f for s in (1,-1)]
    return [{"id":"two_wave_template","n":n+1,"clauses":g,"library":build([t])},
            {"id":"multi_wave_chain","n":4,"clauses":[[1],[-1,2],[-2,3],[-3,4],[-4]],"library":{"entries":[]}}]


def control_results():
    rows=[]
    for c in controls():
        n,f,lib=c["n"],c["clauses"],c["library"]
        old=transfer(n,f,lib)
        new=investigate(n,f,lib)
        if (ref(n,f) or old["decision"]!="unknown" or new["compact_decision"]!="unsat"
                or (c["id"]=="two_wave_template" and new["direct_refutation"])
                or (c["id"]=="multi_wave_chain" and not new["direct_refutation"])):
            raise AssertionError("multi-wave positive control failed")
        rows.append({"case":c,"single":old,"multi":new})
    return rows


def summary(rows):
    s={"cases":len(rows),"reference_unsat":0,"single_decisions":0,"multi_full_decisions":0,
       "multi_compact_decisions":0,"multi_direct_refutations":0,"multi_compact_transfers":0,
       "compact_only_vs_single":0,"single_only_vs_compact":0,
       "compact_only_vs_full":0,"full_only_vs_compact":0,
       "single_inference_work":0,"single_match_work":0,"multi_inference_work":0,
       "view_work":0,"full_match_work":0,"compact_match_work":0,
       "full_clauses":0,"compact_clauses":0,"multi_derived_clauses":0}
    for r in rows:
        a,m=r["single"],r["multi"]
        old=a["decision"]=="unsat"
        full=m["full_decision"]=="unsat"
        compact=m["compact_decision"]=="unsat"
        s["reference_unsat"]+=not r["reference"]
        s["single_decisions"]+=old
        s["multi_full_decisions"]+=full
        s["multi_compact_decisions"]+=compact
        s["multi_direct_refutations"]+=m["direct_refutation"]
        s["multi_compact_transfers"]+=compact and not m["direct_refutation"]
        s["compact_only_vs_single"]+=compact and not old
        s["single_only_vs_compact"]+=old and not compact
        s["compact_only_vs_full"]+=compact and not full
        s["full_only_vs_compact"]+=full and not compact
        s["single_inference_work"]+=a["closure"]["work_steps"]
        s["single_match_work"]+=a["query"]["work_steps"] if a["query"] else 0
        s["multi_inference_work"]+=m["inference"]["work_steps"]
        s["view_work"]+=m["view"]["work_steps"]
        s["full_match_work"]+=m["full_query"]["work_steps"] if m["full_query"] else 0
        s["compact_match_work"]+=m["compact_query"]["work_steps"] if m["compact_query"] else 0
        s["full_clauses"]+=m["full_size"]
        s["compact_clauses"]+=m["compact_size"]
        s["multi_derived_clauses"]+=len(m["inference"]["steps"])
    return s


def run(source,scheduler,failures,abstraction,knowledge,analogy,semantic,*,count=24,checkpoint_path=None):
    inputs=(source,scheduler,failures,abstraction,knowledge,analogy,semantic)
    audit_v18(*inputs)
    if failures["seed"]==SEED:
        raise ValueError("evaluation seed overlaps v13")
    lib=knowledge["library"]
    r={"schema":"mathos-pnp-guided-frontier/1","upstream":[digest(x) for x in inputs],
       "count":count,"controls":[],"rows":[],"completion":"running",
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        r["controls"]=control_results()
        save()
        for case in fresh_cases(SEED,count):
            n,f=case["n"],case["clauses"]
            reference=ref(n,f)
            a=transfer(n,f,lib)
            m=investigate(n,f,lib)
            if reference and "unsat" in (a["decision"],m["full_decision"],m["compact_decision"]):
                raise AssertionError("inference contradicts reference")
            r["rows"].append({"case":case,"reference":reference,"single":a,"multi":m})
            save()
        r["completion"]="completed"
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except (ValueError,AssertionError) as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["summary"]=summary(r["rows"])
    save()
    return r


def _check_config(a,m):
    c=a["closure"]
    if (c["width"],c["derived_limit"],c["pair_limit"])!=(4,256,20_000):
        raise ValueError("single-wave options mismatch")
    if a["query"] is not None and a["query"]["limit"]!=4096:
        raise ValueError("single-wave matching options mismatch")
    c=m["inference"]
    if (c["rounds"],c["width"],c["derived_limit"],c["pair_limit"],c["order"])!=(3,4,256,20_000,"short_first"):
        raise ValueError("multi-wave options mismatch")


def audit(source,scheduler,failures,abstraction,knowledge,analogy,semantic,r):
    inputs=(source,scheduler,failures,abstraction,knowledge,analogy,semantic)
    audit_v18(*inputs)
    if (r["schema"]!="mathos-pnp-guided-frontier/1" or r["upstream"]!=[digest(x) for x in inputs]
            or r["completion"]!="completed" or failures["seed"]==SEED or r["universal_obligation"]!="unresolved"
            or any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))):
        raise ValueError("source or governance mismatch")
    expected=controls()
    if len(r["controls"])!=len(expected):
        raise ValueError("control coverage mismatch")
    for c,row in zip(expected,r["controls"]):
        if digest(c)!=digest(row["case"]):
            raise ValueError("control provenance mismatch")
        n,f,lib=c["n"],c["clauses"],c["library"]
        a,m=row["single"],row["multi"]
        _check_config(a,m)
        verify_transfer(n,f,lib,a)
        verify_investigation(n,f,lib,m)
        if (ref(n,f) or a["decision"]!="unknown" or m["compact_decision"]!="unsat"
                or m["direct_refutation"]!=(c["id"]=="multi_wave_chain")):
            raise ValueError("control conclusion mismatch")
    lib=knowledge["library"]
    expected=fresh_cases(SEED,r["count"])
    if len(r["rows"])!=len(expected):
        raise ValueError("incomplete evaluation")
    for c,row in zip(expected,r["rows"]):
        n,f=c["n"],c["clauses"]
        if row["case"]!=c or row["reference"] is not ref(n,f):
            raise ValueError("reference mismatch")
        a,m=row["single"],row["multi"]
        _check_config(a,m)
        verify_transfer(n,f,lib,a)
        verify_investigation(n,f,lib,m)
        if row["reference"] and "unsat" in (a["decision"],m["full_decision"],m["compact_decision"]):
            raise ValueError("unsound decision")
    if r["summary"]!=summary(r["rows"]):
        raise ValueError("aggregate mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    names=("benchmark","scheduler","failures","abstraction","knowledge","analogy","semantic")
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
