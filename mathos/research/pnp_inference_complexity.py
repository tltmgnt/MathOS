"""Scaling audit with exact restricted-model obstructions and escape proofs."""
import argparse
import json
from pathlib import Path
from .pnp_structural_kernel import Budget, Exhausted
from .pnp_guided_inference import derive, replay
from .pnp_resolution_refutation import propose, verify
from .pnp_certificate_routes import propose as semantic, verify as verify_semantic
from .pnp_inference_obstructions import (chain,cube,chain_certificate,cube_certificate,
    verify_chain,verify_cube,balanced_proof,depth_support)
from .pnp_evidence_benchmark import digest
from .pnp_outcome_engine import checkpoint
from .pnp_outcome_registry import decompose

CHAIN_SIZES=(1,3,7,15,16,31,63,127,255)
CUBE_SIZES=(3,4,5,6,7,8)
SCHEMA="mathos-pnp-inference-complexity/1"


def budget():
    return Budget(seconds=15,max_steps=4_000_000,max_cells=200_000)


def wave(n,f,width,rounds):
    b=budget()
    a=derive(n,f,b,width=width,rounds=rounds)
    g=replay(n,f,a,budget())
    return {"proof":a,"direct_refutation":() in g,"derived":len(a["steps"]),
            "work_steps":b.steps}


def chain_row(n):
    f=chain(n)
    c=chain_certificate(n)
    verify_chain(n,f,c,budget())
    b=budget()
    p=balanced_proof(n,b)
    stats=depth_support(n,f,p,budget())
    if stats["depth"]!=c["minimum_depth"] or stats["axiom_support"]!=n+1:
        raise AssertionError("balanced proof does not meet lower bound")
    b2=budget()
    escape=semantic(n,f,"two_sat",b2)
    if escape is None or not escape["clauses"]:
        raise AssertionError("2-SAT escape failed")
    verify_semantic(n,f,escape,budget())
    return {"n":n,"certificate":c,"balanced_proof":p,"balanced_stats":stats,
            "balanced_work_steps":b.steps,"two_sat":escape,"two_sat_work_steps":b2.steps,
            "waves":[wave(n,f,2,r) for r in (1,2,3,4)]}


def cube_row(k):
    f=cube(k)
    c=cube_certificate(k)
    verify_cube(k,f,c,budget())
    blocked=wave(k,f,min(4,k-2),4)
    if blocked["derived"]!=0 or blocked["direct_refutation"]:
        raise AssertionError("derived-width obstruction violated")
    b=budget()
    p=propose(k,f,b,width=k-1,records=8192,strategy="ascending")
    if p is None:
        raise AssertionError("width escape failed")
    stats=depth_support(k,f,p,budget())
    if stats["maximum_derived_width"]!=k-1:
        raise AssertionError("width escape does not meet lower bound")
    return {"k":k,"certificate":c,"blocked_wave":blocked,
            "boundary_wave":wave(k,f,k-1,4) if k<=5 else None,
            "escape_proof":p,"escape_stats":stats,"escape_work_steps":b.steps}


def summary(chains,cubes):
    return {"chain_cases":len(chains),"cube_cases":len(cubes),
            "chain_exact_depth_matches":sum(r["balanced_stats"]["depth"]==r["certificate"]["minimum_depth"] for r in chains),
            "chain_two_sat_escapes":len(chains),
            "chain_four_wave_refutations":sum(r["waves"][-1]["direct_refutation"] for r in chains),
            "chain_four_wave_provably_blocked":sum(r["certificate"]["minimum_depth"]>4 for r in chains),
            "chain_four_wave_unresolved_within_depth":sum(not r["waves"][-1]["direct_refutation"] and r["certificate"]["minimum_depth"]<=4 for r in chains),
            "cube_blocked_first_steps":sum(r["blocked_wave"]["derived"]==0 for r in cubes),
            "cube_exact_width_matches":sum(r["escape_stats"]["maximum_derived_width"]==r["certificate"]["minimum_first_derived_width"] for r in cubes)}


def run(*,checkpoint_path=None):
    r={"schema":SCHEMA,"chains":[],"cubes":[],"completion":"running",
       "model":"binary resolution from original axioms; derived width and proof depth only",
       "objectives":[decompose("E01"),decompose("E02"),decompose("E08")],
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False,
       "formal_verification":"abstract lemmas only; full family proof not formalized"}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        save()
        for n in CHAIN_SIZES:
            r["chains"].append(chain_row(n))
            save()
        for k in CUBE_SIZES:
            r["cubes"].append(cube_row(k))
            save()
        r["completion"]="completed"
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except (ValueError,AssertionError) as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["summary"]=summary(r["chains"],r["cubes"])
    save()
    return r


def _check_wave(n,f,r,width,rounds):
    p=r["proof"]
    if (p["rounds"],p["width"],p["derived_limit"],p["pair_limit"],p["order"])!=(rounds,width,256,20_000,"short_first"):
        raise ValueError("wave configuration mismatch")
    g=replay(n,f,p,budget())
    if (r["direct_refutation"] is not (() in g) or r["derived"]!=len(p["steps"]) or
            type(r["work_steps"]) is not int or not 0<=r["work_steps"]<=4_000_000 or
            r["work_steps"]!=p["work_steps"]):
        raise ValueError("wave summary mismatch")


def _work(r,key):
    if type(r[key]) is not int or not 0<=r[key]<=4_000_000:
        raise ValueError("invalid observed work")


def audit(r):
    if (r["schema"]!=SCHEMA or r["completion"]!="completed" or
            r["model"]!="binary resolution from original axioms; derived width and proof depth only" or
            digest(r["objectives"])!=digest([decompose("E01"),decompose("E02"),decompose("E08")]) or
            r["universal_obligation"]!="unresolved" or
            r["formal_verification"]!="abstract lemmas only; full family proof not formalized" or
            any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))):
        raise ValueError("invalid report governance")
    if [x["n"] for x in r["chains"]]!=list(CHAIN_SIZES) or [x["k"] for x in r["cubes"]]!=list(CUBE_SIZES):
        raise ValueError("incomplete scaling suite")
    for a in r["chains"]:
        n=a["n"]
        f=chain(n)
        verify_chain(n,f,a["certificate"],budget())
        stats=depth_support(n,f,a["balanced_proof"],budget())
        if (a["balanced_stats"]!=stats or stats["depth"]!=n.bit_length() or
                stats["axiom_support"]!=n+1 or stats["maximum_derived_width"]>2 or
                stats["derived_steps"]!=n):
            raise ValueError("balanced proof statistics mismatch")
        if a["two_sat"]["route"]!="two_sat" or not a["two_sat"]["clauses"]:
            raise ValueError("missing independent 2-SAT escape")
        verify_semantic(n,f,a["two_sat"],budget())
        _work(a,"balanced_work_steps")
        _work(a,"two_sat_work_steps")
        if len(a["waves"])!=4:
            raise ValueError("incomplete depth sweep")
        for d,w in enumerate(a["waves"],1):
            _check_wave(n,f,w,2,d)
            if w["direct_refutation"] and d<n.bit_length():
                raise ValueError("refutation contradicts depth bound")
    for a in r["cubes"]:
        k=a["k"]
        f=cube(k)
        verify_cube(k,f,a["certificate"],budget())
        _check_wave(k,f,a["blocked_wave"],min(4,k-2),4)
        if a["blocked_wave"]["derived"]!=0 or a["blocked_wave"]["direct_refutation"]:
            raise ValueError("width obstruction mismatch")
        if k<=5:
            _check_wave(k,f,a["boundary_wave"],k-1,4)
        elif a["boundary_wave"] is not None:
            raise ValueError("unexpected boundary run")
        stats=depth_support(k,f,a["escape_proof"],budget())
        if a["escape_stats"]!=stats or stats["maximum_derived_width"]!=k-1:
            raise ValueError("width escape mismatch")
        _work(a,"escape_work_steps")
    if r["summary"]!=summary(r["chains"],r["cubes"]):
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
