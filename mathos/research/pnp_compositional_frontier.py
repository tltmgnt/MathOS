"""Universal-obligation research via scoped compositional backdoor experiments."""
import argparse
import json
from pathlib import Path

from .pnp_compositional import search, isolated_obstruction, MAX_K, MAX_CANDIDATES
from .pnp_structural_kernel import Budget, Exhausted, brute, normalize
from .pnp_outcome_engine import checkpoint
from .pnp_outcome_registry import decompose


def family(m):
    """Disjoint signed ternary clauses; each is a separate component."""
    if type(m) is not int or not 1 <= m <= 64:
        raise ValueError("family size must be 1..64")
    return [tuple(v if (v+i)%2 else -v for v in range(3*i+1,3*i+4))
            for i in range(m)]


def probe(m,budget):
    n,f=3*m,family(m)
    artifact=search(n,f,budget,k=1)
    obstruction=isolated_obstruction(n,f,budget)
    if (artifact["decision"]!="sat" or not artifact["complete_strong_backdoor_cover"]
            or obstruction["lower_bound"]!=m or artifact["leaf_count"]!=2*m
            or any(len(p["backdoor"])!=1 for p in artifact["certified_components"])):
        raise AssertionError("disjoint family premises failed")
    # One variable per clause makes every residual globally 2-CNF. This
    # upper bound is a mathematical argument, not 2^m executed branches.
    return {"blocks":m,"variables":n,"global_backdoor_lower":m,
            "global_backdoor_upper_by_family_argument":m,
            "global_full_assignment_count":1<<m,
            "componentwise_verified_leaf_count":artifact["leaf_count"],
            "largest_component_backdoor":1,"artifact":artifact,"obstruction":obstruction,
            "scope":"full global assignment enumeration vs componentwise leaf replay; not a runtime lower bound"}


def investigate(n,f,budget,k,candidate_limit):
    a=search(n,f,budget,k=k,candidate_limit=candidate_limit)
    nn,nf,_=normalize(n,f)
    reference=brute(nn,nf,budget) if nn<=10 else None
    if reference is not None and a["decision"]!="unknown" and (a["decision"]=="sat")!=reference:
        raise AssertionError("compositional decision disagrees with brute force")
    return {"artifact":a,"reference":reference,
            "obstruction":isolated_obstruction(n,f,budget)}


def obligations():
    # Do not mutate the original outcome registry or close its universal IDs
    # using finite certificates or the abstract Lean composition lemmas.
    return [
        {"id":"O08","status":"unresolved","scoped_evidence":"normalization, complete branch replay and disjoint composition",
         "remaining":"uniform transformation finding and bounds on all SAT inputs"},
        {"id":"O09","status":"unresolved","scoped_evidence":"fixed-k componentwise direct-algebra backdoors",
         "remaining":"general coverage theorem and formal algorithm/complexity correctness"},
        {"id":"O10","status":"unresolved","remaining":"uniform polynomial-time SAT-preserving transformation on every input"},
        {"id":"O11","status":"unresolved","scoped_evidence":"isolated-scope lower bound on a specified backdoor model",
         "remaining":"algorithm-independent superpolynomial SAT lower bound; current model restriction is insufficient"},
        {"id":"O12","status":"unresolved","scoped_evidence":"separate Lean abstract finite composition targets",
         "remaining":"independent formal proof of the exact universal claim"},
    ]


def run(budget,*,sizes=(1,4,16,32,64),k=2,candidate_limit=MAX_CANDIDATES,target=None,checkpoint_path=None):
    if (not isinstance(sizes,(list,tuple)) or not 1<=len(sizes)<=64 or
            any(type(m) is not int or not 1<=m<=64 for m in sizes) or len(set(sizes))!=len(sizes)):
        raise ValueError("unique family sizes in 1..64 required")
    if type(k) is not int or not 0<=k<=MAX_K or type(candidate_limit) is not int or not 1<=candidate_limit<=MAX_CANDIDATES:
        raise ValueError("invalid research search limits")
    r={"schema":"mathos-pnp-compositional-frontier/1",
       "plans":[decompose("E01"),decompose("E02")],"obligations":obligations(),
       "universal_obligation":"unresolved","p_equals_np_established":False,
       "p_not_equals_np_established":False,"novel_theorem_verified":False,
       "formal_verification":"not_performed","completion":"documented_unresolved_obligations",
       "family":[],"controls":[],
       "restart":{"sizes":sizes,"k":k,"candidate_limit":candidate_limit,"target":target}}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        save()
        connected=[(1,2,3),(4,5,6),(3,4)]
        for name,f,limit,expected in (
                ("connected_one_split",connected,1,"unknown"),
                ("connected_two_splits",connected,2,"sat"),
                ("connected_unsat",connected+[(3,),(-3,)],2,"unsat"),
                ("unsat_with_unknown_component",[(1,2,3),()],0,"unsat")):
            a=investigate(6,f,budget,limit,MAX_CANDIDATES)
            if a["artifact"]["decision"]!=expected:
                raise AssertionError("control decision mismatch")
            r["controls"].append({"name":name,**a})
            save()
        for m in sizes:
            r["family"].append(probe(m,budget))
            save()
        if target is not None:
            r["target"]=investigate(target["n"],target["clauses"],budget,k,candidate_limit)
        r["completion"]="scoped_compositional_research_completed"
        r["next_obligation"]="Find efficiently discoverable decompositions on broader families, or establish a lower bound in a model that includes composition; no universal claim follows from this scoped result."
    except Exhausted as exc:
        r["completion"],r["reason"]="resource_exhausted",str(exc)
    except (AssertionError, ValueError) as exc:
        r["completion"],r["reason"]="diagnostic_required",str(exc)
    r["work_steps"]=budget.steps
    save()
    return r


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path)
    p.add_argument("--resume",type=Path)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--sizes",nargs="+",type=int,default=[1,4,16,32,64])
    p.add_argument("--k",type=int,default=2)
    p.add_argument("--candidate-limit",type=int,default=MAX_CANDIDATES)
    p.add_argument("--seconds",type=float,default=30)
    p.add_argument("--max-steps",type=int,default=20_000_000)
    p.add_argument("--max-cells",type=int,default=200_000)
    a=p.parse_args(argv)
    if a.input and a.resume:
        p.error("choose input or resume")
    def read(path):
        if path.stat().st_size>8_000_000:
            raise ValueError("JSON exceeds 8 MB")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        opts=read(a.resume)["restart"] if a.resume else {
            "sizes":a.sizes,"k":a.k,"candidate_limit":a.candidate_limit,
            "target":read(a.input) if a.input else None}
        r=run(Budget(a.seconds,a.max_steps,a.max_cells),checkpoint_path=a.checkpoint,**opts)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        p.error(str(exc))
    print(json.dumps(r,indent=2,sort_keys=True))
    return int(r["completion"]!="scoped_compositional_research_completed")


if __name__=="__main__":
    raise SystemExit(main())
