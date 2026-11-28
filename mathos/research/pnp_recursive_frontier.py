"""Connected-family separator research and scoped proof-obligation accounting."""
import argparse
import json
from pathlib import Path

from .pnp_recursive_separators import search, scope_obstruction, MAX_DEPTH, MAX_NODES
from .pnp_structural_kernel import Budget, Exhausted, brute, normalize
from .pnp_outcome_engine import checkpoint
from .pnp_outcome_registry import decompose


def family(m):
    """One hub connected by binary clauses to m disjoint ternary supports."""
    if type(m) is not int or not 2<=m<=64:
        raise ValueError("family size must be 2..64")
    return [(2+3*i,3+3*i,4+3*i) for i in range(m)]+[(1,2+3*i) for i in range(m)]


def probe(m,budget):
    n,f=1+3*m,family(m)
    a=search(n,f,budget,depth=2)
    ob=scope_obstruction(n,f,budget)
    if (a["decision"]!="sat" or a["tree"]["kind"]!="split" or a["tree"]["variable"]!=1
            or a["tree"]["separator_parts"]!=m or a["metrics"]["unknown_leaves"]
            or a["metrics"]["leaves"]!=4*m or ob["global_backdoor_lower"]!=m):
        raise AssertionError("connected-family certificate or count mismatch")
    return {"blocks":m,"variables":n,"clauses":2*m,"connected":True,
            "global_backdoor_lower":m,"global_backdoor_upper_by_argument":m,
            "global_full_assignment_count":1<<m,"recursive_verified_leaves":4*m,
            "recursive_split_depth":2,"artifact":a,"obstruction":ob,
            "scope":"specified global enumeration vs recursive tree, not SAT runtime"}


def investigate(n,f,budget,depth,nodes):
    a=search(n,f,budget,depth=depth,nodes=nodes)
    nn,nf,_=normalize(n,f)
    reference=brute(nn,nf,budget) if nn<=10 else None
    if reference is not None and a["decision"]!="unknown" and (a["decision"]=="sat")!=reference:
        raise AssertionError("recursive decision disagrees with reference")
    return {"artifact":a,"reference":reference,"obstruction":scope_obstruction(n,f,budget)}


def run(budget,*,sizes=(2,4,8,16,32,64),depth=4,nodes=MAX_NODES,target=None,checkpoint_path=None):
    if (not isinstance(sizes,(list,tuple)) or not 1<=len(sizes)<=63
            or any(type(m) is not int or not 2<=m<=64 for m in sizes)
            or len(set(sizes))!=len(sizes)):
        raise ValueError("unique family sizes 2..64 required")
    if type(depth) is not int or not 0<=depth<=MAX_DEPTH or type(nodes) is not int or not 1<=nodes<=MAX_NODES:
        raise ValueError("invalid recursion limits")
    r={"schema":"mathos-pnp-recursive-frontier/1",
       "plans":[decompose("E01"),decompose("E02")],
       "obligations":[
           {"id":"O08","status":"unresolved","evidence":"recursive restrictions and disjoint partition replay"},
           {"id":"O09","status":"unresolved","evidence":"bounded separator and algebra decision composition"},
           {"id":"O10","status":"unresolved","remaining":"uniform efficient discovery and polynomial proof size for all SAT"},
           {"id":"O11","status":"unresolved","evidence":"exclusive scope packing lower bound in static direct-algebra backdoor model only"},
           {"id":"O12","status":"unresolved","evidence":"abstract three-valued tree soundness proof target"}],
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False,
       "formal_verification":"not_performed","completion":"documented_unresolved_obligations",
       "family":[],"controls":[],"restart":{"sizes":sizes,"depth":depth,"nodes":nodes,"target":target}}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        save()
        for name,n,f,d,expected in (
            ("depth_limited",7,family(2),1,"unknown"),
            ("connected_escape",7,family(2),2,"sat"),
            ("connected_conflict",7,family(2)+[(1,),(-1,)],2,"unsat"),
            ("unknown_and_unsat",4,[(1,),(-1,),(2,3,4)],0,"unsat"),
        ):
            a=investigate(n,f,budget,d,nodes)
            if a["artifact"]["decision"]!=expected:
                raise AssertionError("recursive control mismatch")
            r["controls"].append({"name":name,**a})
            save()
        for m in sizes:
            r["family"].append(probe(m,budget))
            save()
        if target is not None:
            r["target"]=investigate(target["n"],target["clauses"],budget,depth,nodes)
        r["completion"]="scoped_recursive_research_completed"
        r["next_obligation"]="Investigate uniform separator or semantic-route discovery with certified total costs on broader connected families; static backdoor size does not bound all recursive methods."
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
    p.add_argument("--sizes",nargs="+",type=int,default=[2,4,8,16,32,64])
    p.add_argument("--depth",type=int,default=4)
    p.add_argument("--nodes",type=int,default=MAX_NODES)
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
            "sizes":a.sizes,"depth":a.depth,"nodes":a.nodes,
            "target":read(a.input) if a.input else None}
        r=run(Budget(a.seconds,a.max_steps,a.max_cells),checkpoint_path=a.checkpoint,**opts)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        p.error(str(exc))
    print(json.dumps(r,indent=2,sort_keys=True))
    return int(r["completion"]!="scoped_recursive_research_completed")


if __name__=="__main__":
    raise SystemExit(main())
