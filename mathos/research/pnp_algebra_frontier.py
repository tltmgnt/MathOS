"""Generalized Boolean relation research: affine, bijunctive and mixed routes."""
import argparse
import json
from itertools import product
from pathlib import Path

from .pnp_constraint_algebra import MODES, propose, verify, solve, verify_solution
from .pnp_structural_kernel import Budget, Exhausted, brute, normalize
from .pnp_outcome_engine import checkpoint
from .pnp_outcome_registry import decompose


def xor_block(variables, rhs):
    """CNF encoding of one parity equation, using its forbidden assignments."""
    variables=tuple(variables)
    if (not 1<=len(variables)<=4 or tuple(sorted(set(variables)))!=variables or
            any(type(v) is not int or v<1 for v in variables) or
            type(rhs) is not int or rhs not in (0,1)):
        raise ValueError("invalid XOR block")
    return [tuple(-v if b else v for v,b in zip(variables,bits))
            for bits in product((False,True),repeat=len(variables))
            if sum(bits)%2!=rhs]


def controls():
    affine=xor_block((1,2,3),0)+xor_block((1,2,4),1)
    # Two incompatible equations on the same scope yield all eight forbidden
    # assignments, so the local relation is empty.
    affine_unsat=xor_block((1,2,3),0)+xor_block((1,2,3),1)
    mixed=xor_block((1,2,3),0)+[(1,4)]
    mixed_unsat=mixed+[(1,),(-2,),(-3,)]
    return [
        ("affine_sat",4,affine,True),
        ("affine_unsat",3,affine_unsat,False),
        ("bijunctive_sat",3,[(1,2),(-1,3),(-2,-3)],True),
        ("mixed_sat",4,mixed,True),
        ("mixed_unsat",4,mixed_unsat,False),
        ("unrecognized",6,[(1,2,3),(4,5,6)],True),
    ]


def investigate(n,clauses,budget):
    nn,f,_=normalize(n,clauses)
    reference=brute(nn,f,budget) if nn<=10 else None
    modes={}
    for mode in MODES:
        a=propose(n,clauses,mode,budget)
        if a is not None:
            verify(n,clauses,a,budget)
            if reference is not None and (not a["clauses"])!=reference:
                raise AssertionError("direct algebra reference mismatch")
        modes[mode]=a
    result=solve(n,clauses,budget)
    if result is not None:
        verify_solution(n,clauses,result,budget)
        if reference is not None and (not result["clauses"])!=reference:
            raise AssertionError("mixed algebra reference mismatch")
    return {"n":n,"clauses":clauses,"normalized_variables":nn,"sat_reference":reference,
            "direct_modes":{m:a is not None for m,a in modes.items()},
            "certificate":result,"certificate_replayed":result is not None,
            "status":"unrecognized" if result is None else ("sat" if not result["clauses"] else "unsat")}


def run(budget,*,target=None,checkpoint_path=None):
    r={"schema":"mathos-pnp-algebra-frontier/1",
       "plans":[decompose("E01"),decompose("E02")],
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False,
       "formal_verification":"not_performed","completion":"documented_unresolved_obligations",
       "controls":[],"restart":{"target":target}}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        save()
        for name,n,f,expected in controls():
            a=investigate(n,f,budget)
            if a["sat_reference"]!=expected:
                raise AssertionError("control decision mismatch")
            if name.startswith("mixed"):
                if any(a["direct_modes"].values()) or a["certificate"] is None or a["certificate"]["kind"]!="conditioned":
                    raise AssertionError("mixed escape premise failed")
            if name=="affine_sat" and a["direct_modes"]!={"bijunctive":False,"affine":True}:
                raise AssertionError("affine control premise failed")
            if name=="unrecognized" and a["certificate"] is not None:
                raise AssertionError("grammar gap premise failed")
            if name!="unrecognized" and not a["certificate_replayed"]:
                raise AssertionError("expected route missing")
            r["controls"].append({"name":name,**a})
            save()
        if target is not None:
            r["target"]=investigate(target["n"],target["clauses"],budget)
        r["completion"]="scoped_algebra_research_completed"
        r["next_obligation"]="Find additional relation representations or bounded decompositions; formalize their uniform overhead and scope without treating unrecognized instances as hard."
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except AssertionError as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["work_steps"]=budget.steps
    save()
    return r


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path)
    p.add_argument("--resume",type=Path)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--seconds",type=float,default=30)
    p.add_argument("--max-steps",type=int,default=20_000_000)
    p.add_argument("--max-cells",type=int,default=200_000)
    a=p.parse_args(argv)
    if a.input and a.resume:
        p.error("choose input or resume")
    def read(path):
        if path.stat().st_size>4_000_000:
            raise ValueError("input exceeds 4 MB")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        target=read(a.resume)["restart"]["target"] if a.resume else (read(a.input) if a.input else None)
        r=run(Budget(a.seconds,a.max_steps,a.max_cells),target=target,checkpoint_path=a.checkpoint)
    except (OSError,ValueError,TypeError,KeyError) as exc:
        p.error(str(exc))
    print(json.dumps(r,indent=2,sort_keys=True))
    return int(r["completion"]!="scoped_algebra_research_completed")


if __name__=="__main__":
    raise SystemExit(main())
