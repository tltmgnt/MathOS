"""Audited expander resolution-size separation and direct parity decisions."""
import argparse
import json
from pathlib import Path
from .pnp_expander_size import family,certify,verify
from .pnp_inference_complexity import budget
from .pnp_structural_kernel import Exhausted
from .pnp_outcome_engine import checkpoint
from .pnp_outcome_registry import decompose
from .pnp_evidence_benchmark import digest

SIDES=(2,3,4,6,8,10)
SCHEMA="mathos-pnp-expander-frontier/1"
DEPENDENCIES={
    "spectral":"Margulis–Gabber–Galil, second eigenvalue at most 5 sqrt(2)",
    "width_size":"Ben-Sasson–Wigderson (2001), Corollary 3.6, DOI 10.1145/375827.375835",
    "support_width":"minimum equation support argument in v22/v23 specifications",
    "formal_status":"imported theorems not formalized here; finite spectral premises checked exactly"
}


def investigate(s,odd):
    n,f,_=family(s,odd=odd)
    b=budget()
    p=certify(s,odd=odd,b=b)
    replay=budget()
    verify(s,n,f,p,replay)
    return {"side":s,"odd":odd,"variables":n,"clauses":len(f),
            "literal_occurrences":sum(map(len,f)),"certificate":p,
            "decision":"unsat" if odd else "sat",
            "construction_work_steps":b.steps,"replay_work_steps":replay.steps}


def summary(rows):
    return {"cases":len(rows),"exact_spectral_checks":len(rows),
            "parity_decisions":len(rows),
            "odd_bounds":[{"side":r["side"],**r["certificate"]["parameters"]} for r in rows if r["odd"]],
            "positive_exponent_ratios":sum(r["odd"] and r["certificate"]["parameters"]["size_exponent_ratio"][0]>0 for r in rows),
            "max_variables":max((r["variables"] for r in rows),default=0)}


def run(*,checkpoint_path=None):
    r={"schema":SCHEMA,"rows":[],"completion":"running",
       "dependencies":DEPENDENCIES.copy(),
       "objectives":[decompose("E01"),decompose("E02"),decompose("E08"),decompose("E15")],
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        save()
        for s in SIDES:
            for odd in (True,False):
                r["rows"].append(investigate(s,odd))
                save()
        r["completion"]="completed"
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except (ValueError,AssertionError) as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["summary"]=summary(r["rows"])
    save()
    return r


def audit(r):
    if (r["schema"]!=SCHEMA or r["completion"]!="completed" or
            r["dependencies"]!=DEPENDENCIES or
            digest(r["objectives"])!=digest([decompose(x) for x in ("E01","E02","E08","E15")]) or
            r["universal_obligation"]!="unresolved" or
            any(r[k] is not False for k in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))):
        raise ValueError("report governance mismatch")
    if [(a["side"],a["odd"]) for a in r["rows"]]!=[(s,o) for s in SIDES for o in (True,False)]:
        raise ValueError("incomplete scaling suite")
    for a in r["rows"]:
        s,o=a["side"],a["odd"]
        n,f,_=family(s,odd=o)
        if (a["variables"],a["clauses"],a["literal_occurrences"])!=(n,len(f),sum(map(len,f))):
            raise ValueError("input size mismatch")
        p=a["certificate"]
        b=budget()
        verify(s,n,f,p,b)
        if p["odd"] is not o or a["decision"]!=("unsat" if o else "sat"):
            raise ValueError("decision mismatch")
        for key in ("construction_work_steps","replay_work_steps"):
            if type(a[key]) is not int or not 0<=a[key]<=4_000_000:
                raise ValueError("invalid work counter")
        if a["replay_work_steps"]!=b.steps:
            raise ValueError("replay work mismatch")
    if r["summary"]!=summary(r["rows"]):
        raise ValueError("aggregate mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    a=p.parse_args(argv)
    try:
        if a.audit:
            if a.audit.stat().st_size>32_000_000:
                raise ValueError("JSON exceeds 32 MB")
            audit(json.loads(a.audit.read_text(encoding="utf-8")))
            print(json.dumps({"status":"replayed","universal_obligation":"unresolved"}))
            return 0
        r=run(checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return int(r["completion"]!="completed")
    except (OSError,ValueError,KeyError,TypeError,Exhausted) as exc:
        p.error(str(exc))


if __name__=="__main__":
    raise SystemExit(main())
