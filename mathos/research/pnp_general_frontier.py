"""Constructive/obstruction research on a shared certificate portfolio."""
import argparse
import json
from pathlib import Path
from .pnp_structural_kernel import Budget, Exhausted, brute, normalize
from .pnp_unified_portfolio import run as portfolio, verify_report, DEFAULT_PLANS
from .pnp_recursive_separators import scope_obstruction
from .pnp_recursive_frontier import family
from .pnp_outcome_registry import decompose
from .pnp_outcome_engine import checkpoint


def controls():
    return [
        ("binary_conflict",2,[(1,2),(-1,2),(1,-2),(-1,-2)],False),
        ("connected_separator",7,family(2),True),
        ("reduction_needed",5,[(1,2,3,4,5)],True),
        ("reduction_conflict",3,[(1,),(-1,2),(-2,3),(-3,)],False),
    ]


def investigate(n,f,budget,**options):
    r=portfolio(n,f,budget,**options)
    nn,nf,_=normalize(n,f)
    reference=brute(nn,nf,budget) if nn<=10 else None
    if reference is not None and r["decision"]!="unknown" and (r["decision"]=="sat")!=reference:
        raise AssertionError("portfolio disagrees with independent reference")
    return {"report":r,"reference":reference,
            "static_model_obstruction":scope_obstruction(n,f,budget)}


def run(budget,*,target=None,depth=4,nodes=1024,k=2,cap=4,checkpoint_path=None):
    r={"schema":"mathos-pnp-general-frontier/1","plans":[decompose("E01"),decompose("E02")],
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False,
       "formal_verification":"not_performed","controls":[],
       "completion":"documented_unresolved_obligations",
       "restart":{"target":target,"depth":depth,"nodes":nodes,"k":k,"cap":cap}}
    options=dict(depth=depth,nodes=nodes,k=k,cap=cap)
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        save()
        # Divide the remaining work across all control/target experiments.
        # A local budget also shares the caller's absolute deadline.
        from .pnp_unified_portfolio import Slice
        count=len(controls())+int(target is not None)+1
        quota=(budget.max_steps-budget.steps)//count
        for name,n,f,expected in controls():
            a=investigate(n,f,Slice(budget,quota),**options)
            if a["reference"]!=expected:
                raise AssertionError("control reference mismatch")
            r["controls"].append({"name":name,**a})
            save()
        # A precisely delimited counterexample to depth-zero direct recursive
        # algebra; not a counterexample to the full portfolio or polynomial SAT.
        f=family(2)
        limited=portfolio(7,f,Slice(budget,quota),plans=(("none","recursive"),),
                          depth=0,nodes=nodes,k=k,cap=cap)
        r["scoped_challenge"]={"claim":"Depth-zero direct recursive algebra decides this connected family member",
            "status":"observed_unrecognized" if limited["entries"][0]["status"]=="replayed" and limited["decision"]=="unknown" else "not_demonstrated",
            "input":{"n":7,"clauses":f},"report":limited,
            "scope":"configured route and depth only; no lower bound on SAT"}
        if target is not None:
            r["target"]=investigate(target["n"],target["clauses"],Slice(budget,quota),**options)
        r["completion"]="scoped_portfolio_research_completed"
        r["next_obligations"]=[
            {"id":"O10","status":"unresolved","missing":"uniform polynomial discovery, execution and total coverage on arbitrary SAT"},
            {"id":"O11","status":"unresolved","missing":"algorithm-independent superpolynomial lower bound; restricted model failures do not suffice"},
            {"id":"O12","status":"unresolved","missing":"formal proof of exact universal statement, not abstract composition alone"}]
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except (AssertionError,ValueError) as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["work_steps"]=budget.steps
    save()
    return r


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path)
    p.add_argument("--resume",type=Path)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--depth",type=int,default=4)
    p.add_argument("--nodes",type=int,default=1024)
    p.add_argument("--k",type=int,default=2)
    p.add_argument("--cap",type=int,default=4)
    p.add_argument("--seconds",type=float,default=60)
    p.add_argument("--max-steps",type=int,default=40_000_000)
    p.add_argument("--max-cells",type=int,default=200_000)
    a=p.parse_args(argv)
    if a.input and a.resume:
        p.error("choose input or resume")
    def read(path):
        if path.stat().st_size>16_000_000:
            raise ValueError("JSON exceeds 16 MB")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        opts=read(a.resume)["restart"] if a.resume else {
            "target":read(a.input) if a.input else None,
            "depth":a.depth,"nodes":a.nodes,"k":a.k,"cap":a.cap}
        r=run(Budget(a.seconds,a.max_steps,a.max_cells),checkpoint_path=a.checkpoint,**opts)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        p.error(str(exc))
    print(json.dumps(r,indent=2,sort_keys=True))
    return int(r["completion"]!="scoped_portfolio_research_completed")


if __name__=="__main__":
    raise SystemExit(main())
