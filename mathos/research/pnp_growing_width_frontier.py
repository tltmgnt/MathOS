"""Scaling audit of toroidal parity width obstructions and affine decisions."""
import argparse
import json
from pathlib import Path
from .pnp_growing_width import family,certificate,verify,balanced_cut
from .pnp_constraint_algebra import propose as affine,verify as verify_affine
from .pnp_guided_inference import derive,replay
from .pnp_inference_complexity import budget
from .pnp_structural_kernel import Exhausted
from .pnp_outcome_engine import checkpoint
from .pnp_outcome_registry import decompose
from .pnp_evidence_benchmark import digest

SIDES=(3,4,6,8,12,16)
SCHEMA="mathos-pnp-growing-width/1"


def investigate(s,odd):
    n,f,_=family(s,odd=odd)
    c=certificate(s,n,f,budget(),odd=odd)
    # A strip of floor(s/2) complete rows attains the balanced cut bound.
    strip=list(range(s*(s//2)))
    cut=balanced_cut(s,strip,budget())
    if cut["size"]!=2*s:
        raise AssertionError("balanced cut upper witness mismatch")
    b=budget()
    p=affine(n,f,"affine",b)
    if p is None or bool(p["clauses"])!=odd:
        raise AssertionError("affine escape missing")
    verify_affine(n,f,p,budget())
    wave=None
    if s<=6:
        wave=derive(n,f,budget(),width=4,rounds=4)
        if () in replay(n,f,wave,budget()):
            raise AssertionError("width-four refutation contradicts bound")
    return {"side":s,"odd":odd,"variables":n,"clauses":len(f),
            "literal_occurrences":sum(map(len,f)),"certificate":c,
            "balanced_strip":strip,"cut":cut,"affine_proof":p,
            "affine_work_steps":b.steps,"width_four_probe":wave,
            "decision":"unsat" if odd else "sat"}


def summary(rows):
    return {"cases":len(rows),"affine_decisions":len(rows),
            "odd_width_bounds":[{"side":r["side"],"variables":r["variables"],
                "lower_bound":r["certificate"]["resolution_width_lower"]} for r in rows if r["odd"]],
            "balanced_cut_witnesses":sum(r["cut"]["size"]==2*r["side"] for r in rows),
            "width_four_probes":sum(r["width_four_probe"] is not None for r in rows),
            "max_variables":max((r["variables"] for r in rows),default=0)}


def run(*,checkpoint_path=None):
    r={"schema":SCHEMA,"rows":[],"completion":"running",
       "objectives":[decompose("E01"),decompose("E02"),decompose("E08")],
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False,
       "formal_verification":"abstract lemmas only; family width proof documented"}
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
            digest(r["objectives"])!=digest([decompose("E01"),decompose("E02"),decompose("E08")]) or
            r["formal_verification"]!="abstract lemmas only; family width proof documented" or
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
        c=a["certificate"]
        verify(s,n,f,c,budget())
        if c["odd"] is not o:
            raise ValueError("parity control mismatch")
        strip=list(range(s*(s//2)))
        if a["balanced_strip"]!=strip or a["cut"]!=balanced_cut(s,strip,budget()) or a["cut"]["size"]!=2*s:
            raise ValueError("cut witness mismatch")
        p=a["affine_proof"]
        verify_affine(n,f,p,budget())
        if p["mode"]!="affine" or bool(p["clauses"])!=o or a["decision"]!=("unsat" if o else "sat"):
            raise ValueError("decision mismatch")
        if type(a["affine_work_steps"]) is not int or not 0<=a["affine_work_steps"]<=4_000_000:
            raise ValueError("invalid work counter")
        w=a["width_four_probe"]
        if s<=6:
            if w is None or (w["rounds"],w["width"],w["derived_limit"],w["pair_limit"],w["order"])!=(4,4,256,20_000,"short_first"):
                raise ValueError("probe configuration mismatch")
            if () in replay(n,f,w,budget()):
                raise ValueError("unexpected restricted refutation")
        elif w is not None:
            raise ValueError("unexpected probe")
    if r["summary"]!=summary(r["rows"]):
        raise ValueError("summary mismatch")
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
