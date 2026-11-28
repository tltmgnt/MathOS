"""Reproducible model-boundary controls; no barrier-avoidance certification."""
import argparse
import json
from pathlib import Path
from .pnp_complexity_barriers import (transcript,verify_transcript,algebraic_control,
    verify_algebraic,natural_control,verify_natural,dossier,verify_dossier)
from .pnp_outcome_registry import decompose
from .pnp_outcome_engine import checkpoint
from .pnp_evidence_benchmark import digest

SIZES=(1,2,3,4,6,8,10,12)
SCHEMA="mathos-pnp-barrier-frontier/1"


def metrics(rows):
    return {"sizes":len(rows),"incomplete_transcripts":sum(x["partial"]["unqueried"] is not None for x in rows),
            "complete_transcripts":sum(x["complete"]["unqueried"] is None for x in rows),
            "algebraic_promise_controls":len(rows),
            "algebraic_cancellation_counterexamples":sum(x["algebraic"]["unrestricted_counterexample"] is not None for x in rows),
            "restricted_natural_property_controls":len(rows),
            "largest_query_bound":max((x["partial"]["query_lower_bound"] for x in rows),default=0),
            "barriers_overcome":0}


def run(*,checkpoint_path=None):
    r={"schema":SCHEMA,"rows":[],"dossier":dossier(),"completion":"running",
       "objectives":[decompose(x) for x in ("E01","E02","E04","E05","E08","E19")],
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False,
       "formal_verification":"abstract local lemmas only; published barriers imported"}
    for n in SIZES:
        N=1<<n
        partial=transcript(n,list(range(N-1)))
        complete=transcript(n,list(range(N)))
        algebraic=algebraic_control(n)
        natural=natural_control(n)
        verify_transcript(n,list(range(N-1)),partial)
        verify_transcript(n,list(range(N)),complete)
        verify_algebraic(algebraic)
        verify_natural(natural)
        r["rows"].append({"n":n,"partial":partial,"complete":complete,
                          "algebraic":algebraic,"natural":natural})
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    r["completion"]="completed"
    r["summary"]=metrics(r["rows"])
    if checkpoint_path:
        checkpoint(checkpoint_path,r)
    return r


def audit(r):
    if (r["schema"]!=SCHEMA or r["completion"]!="completed" or
            r["universal_obligation"]!="unresolved" or
            any(r[k] is not False for k in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified")) or
            r["formal_verification"]!="abstract local lemmas only; published barriers imported" or
            digest(r["objectives"])!=digest([decompose(x) for x in ("E01","E02","E04","E05","E08","E19")])):
        raise ValueError("invalid governance")
    verify_dossier(r["dossier"])
    if [x["n"] for x in r["rows"]]!=list(SIZES):
        raise ValueError("incomplete scaling suite")
    for row in r["rows"]:
        n=row["n"]
        N=1<<n
        verify_transcript(n,list(range(N-1)),row["partial"])
        verify_transcript(n,list(range(N)),row["complete"])
        if row["algebraic"]["n"]!=n or row["natural"]["n"]!=n:
            raise ValueError("cross-control dimension mismatch")
        verify_algebraic(row["algebraic"])
        verify_natural(row["natural"])
    if r["summary"]!=metrics(r["rows"]):
        raise ValueError("incorrect aggregate")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    a=p.parse_args(argv)
    try:
        if a.audit:
            if a.audit.stat().st_size>4_000_000:
                raise ValueError("oversized report")
            audit(json.loads(a.audit.read_text(encoding="utf-8")))
            print(json.dumps({"status":"replayed","universal_obligation":"unresolved"}))
            return 0
        r=run(checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return 0
    except (OSError,ValueError,KeyError,TypeError) as e:
        p.error(str(e))


if __name__=="__main__":
    raise SystemExit(main())
