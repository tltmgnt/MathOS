"""Audited finite conjecture refinement, with separate frozen holdout cases."""
import argparse
import json
from pathlib import Path
from .pnp_conjecture_refinement import (grammar,refine,verify_refinement,
    holdout,certify,verify_case,predict,reference)
from .pnp_hypothesis_obligations import run as hypotheses_run,audit as hypotheses_audit
from .pnp_proof_simulation_frontier import run as simulation_run
from .pnp_barrier_frontier import run as barrier_run
from .pnp_evidence_benchmark import digest
from .pnp_outcome_registry import decompose
from .pnp_outcome_engine import checkpoint
from .pnp_structural_kernel import Exhausted

SCHEMA="mathos-pnp-conjecture-refinement/1"


def summary(r):
    a=r.get("refinement",{})
    rounds=a.get("rounds",[])
    rows=r["holdout"]
    return {"generated_candidates":len(grammar()),
            "refinement_rounds":len(rounds),
            "eliminated_candidates":sum(len(x["eliminated"]) for x in rounds),
            "bounded_survivor":a.get("selected"),
            "training_descriptors_examined_final_round":a.get("final_examined"),
            "counterexample_components":[len(x["case"]) for x in rounds],
            "holdout_cases":len(rows),
            "holdout_sat":sum(x["proof"]["decision"]=="sat" for x in rows),
            "holdout_unsat":sum(x["proof"]["decision"]=="unsat" for x in rows),
            "baseline_correct":sum(x["baseline"]==(x["proof"]["decision"]=="sat") for x in rows),
            "refined_correct":sum(x["prediction"]==(x["proof"]["decision"]=="sat") for x in rows),
            "universal_obligations_closed":0,"barriers_overcome":0}


def run(simulation,barriers,hypotheses,*,checkpoint_path=None):
    hypotheses_audit(simulation,barriers,hypotheses)
    r={"schema":SCHEMA,"upstream":[digest(x) for x in (simulation,barriers,hypotheses)],
       "holdout":[],"completion":"running","universal_obligation":"unresolved",
       "p_equals_np_established":False,"p_not_equals_np_established":False,
       "novel_theorem_verified":False,"barriers":barriers["dossier"]["barriers"],
       "objectives":[decompose(x) for x in ("E01","E02","E07","E12","E19")],
       "scope":"finite descriptor grammar and independently checked CNF witnesses; no universal closure"}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        r["refinement"]=refine()
        verify_refinement(r["refinement"])
        selected=r["refinement"]["selected"]
        if selected is None:
            raise AssertionError("no bounded survivor")
        save()
        for case in holdout():
            p=certify(case)
            r["holdout"].append({"case":case,"proof":p,
                "baseline":predict(("global",),case),"prediction":predict(selected,case)})
            save()
        r["completion"]="completed"
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except (AssertionError,ValueError) as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["summary"]=summary(r)
    save()
    return r


def audit(simulation,barriers,hypotheses,r):
    hypotheses_audit(simulation,barriers,hypotheses)
    if (r["schema"]!=SCHEMA or r["upstream"]!=[digest(x) for x in (simulation,barriers,hypotheses)]
            or r["completion"]!="completed" or r["universal_obligation"]!="unresolved"
            or any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))
            or r["barriers"]!=barriers["dossier"]["barriers"]
            or digest(r["objectives"])!=digest([decompose(x) for x in ("E01","E02","E07","E12","E19")])
            or r["scope"]!="finite descriptor grammar and independently checked CNF witnesses; no universal closure"):
        raise ValueError("report governance mismatch")
    verify_refinement(r["refinement"])
    selected=r["refinement"]["selected"]
    cases=holdout()
    if selected is None or len(r["holdout"])!=len(cases):
        raise ValueError("missing bounded survivor or holdout cases")
    for case,row in zip(cases,r["holdout"]):
        if digest(row["case"])!=digest(case):
            raise ValueError("holdout case mismatch")
        verify_case(case,row["proof"])
        if row["baseline"] is not predict(("global",),case) or row["prediction"] is not predict(selected,case):
            raise ValueError("holdout prediction mismatch")
    if digest(r["summary"])!=digest(summary(r)):
        raise ValueError("summary mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    names=("simulation","barriers","hypotheses")
    for name in names:
        p.add_argument("--"+name,type=Path)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    a=p.parse_args(argv)
    def read(path):
        if path.stat().st_size>32_000_000:
            raise ValueError("oversized input")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        paths=tuple(getattr(a,k) for k in names)
        if any(paths) and not all(paths):
            raise ValueError("provide all three upstream reports or none")
        if a.checkpoint and any(a.checkpoint.resolve()==x.resolve() for x in paths if x):
            raise ValueError("cannot overwrite upstream")
        if all(paths):
            s,b,h=(read(x) for x in paths)
        elif a.audit:
            raise ValueError("audit requires exact upstream reports")
        else:
            s,b=simulation_run(),barrier_run()
            h=hypotheses_run(s,b)
        if a.audit:
            audit(s,b,h,read(a.audit))
            print(json.dumps({"status":"replayed","universal_obligation":"unresolved"}))
            return 0
        r=run(s,b,h,checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return int(r["completion"]!="completed")
    except (OSError,ValueError,KeyError,TypeError,Exhausted) as exc:
        p.error(str(exc))


if __name__=="__main__":
    raise SystemExit(main())
