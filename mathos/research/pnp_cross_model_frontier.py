"""Audited cross-model separation on linear-size prism parity CNFs."""
import argparse
import json
from pathlib import Path
from .pnp_cross_model import prism,propose,verify
from .pnp_constraint_algebra import propose as affine, verify as verify_affine
from .pnp_guided_inference import derive,replay
from .pnp_inference_complexity import budget
from .pnp_structural_kernel import Exhausted
from .pnp_evidence_benchmark import digest
from .pnp_outcome_registry import decompose
from .pnp_outcome_engine import checkpoint

SIZES=(3,4,8,16,32,64)
SCHEMA="mathos-pnp-cross-model/1"


def investigate(m,inconsistent):
    n,f,_=prism(m,inconsistent=inconsistent)
    cert=propose(n,f,budget())
    if cert is None:
        raise AssertionError("parity structure not recognized")
    verify(n,f,cert,budget())
    b=budget()
    blocked=derive(n,f,b,width=3,rounds=4)
    g=replay(n,f,blocked,budget())
    if blocked["steps"] or () in g:
        raise AssertionError("restricted width bound violated")
    a=budget()
    proof=affine(n,f,"affine",a)
    if proof is None or bool(proof["clauses"])!=inconsistent:
        raise AssertionError("affine escape failed")
    verify_affine(n,f,proof,budget())
    return {"m":m,"inconsistent":inconsistent,"variables":n,"clauses":len(f),
            "literal_occurrences":sum(map(len,f)),"certificate":cert,
            "blocked_wave":blocked,"affine_proof":proof,
            "affine_work_steps":a.steps,"decision":"unsat" if inconsistent else "sat"}


def summary(rows):
    return {"cases":len(rows),"unsat_cases":sum(r["inconsistent"] for r in rows),
            "sat_cases":sum(not r["inconsistent"] for r in rows),
            "width_three_blocked":sum(not r["blocked_wave"]["steps"] for r in rows),
            "affine_decisions":sum(r["decision"] in ("sat","unsat") for r in rows),
            "max_variables":max((r["variables"] for r in rows),default=0)}


def run(*,checkpoint_path=None):
    r={"schema":SCHEMA,"rows":[],"completion":"running",
       "objectives":[decompose("E01"),decompose("E02"),decompose("E08")],
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False,
       "formal_verification":"abstract Boolean lemmas only"}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        save()
        for m in SIZES:
            for inconsistent in (True,False):
                r["rows"].append(investigate(m,inconsistent))
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
            r["universal_obligation"]!="unresolved" or
            r["formal_verification"]!="abstract Boolean lemmas only" or
            digest(r["objectives"])!=digest([decompose("E01"),decompose("E02"),decompose("E08")]) or
            any(r[k] is not False for k in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))):
        raise ValueError("report governance mismatch")
    if [(a["m"],a["inconsistent"]) for a in r["rows"]]!=[(m,i) for m in SIZES for i in (True,False)]:
        raise ValueError("incomplete scaling suite")
    for a in r["rows"]:
        m,i=a["m"],a["inconsistent"]
        n,f,_=prism(m,inconsistent=i)
        if (a["variables"],a["clauses"],a["literal_occurrences"])!=(n,len(f),sum(map(len,f))):
            raise ValueError("input size mismatch")
        cert=a["certificate"]
        verify(n,f,cert,budget())
        if cert["xor_rhs"]!=int(i):
            raise ValueError("parity identity mismatch")
        p=a["blocked_wave"]
        if (p["width"],p["rounds"],p["derived_limit"],p["pair_limit"],p["order"])!=(3,4,256,20_000,"short_first"):
            raise ValueError("wave configuration mismatch")
        if () in replay(n,f,p,budget()) or p["steps"]:
            raise ValueError("restricted width obstruction violated")
        if type(p["work_steps"]) is not int or not 0<=p["work_steps"]<=4_000_000:
            raise ValueError("invalid wave work")
        q=a["affine_proof"]
        verify_affine(n,f,q,budget())
        if q["mode"]!="affine" or bool(q["clauses"])!=i or a["decision"]!=("unsat" if i else "sat"):
            raise ValueError("affine conclusion mismatch")
        if type(a["affine_work_steps"]) is not int or not 0<=a["affine_work_steps"]<=4_000_000:
            raise ValueError("invalid affine work")
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
