"""F034: bounded paired resolution and certificate routing.

One round of equal-tail resolution on original clauses only.
Derived clauses are consequences, not an equivalent formula.
Never lift a derived-subset SAT witness to original SAT.
"""
from collections import Counter
from random import Random

from . import tga_proctor_combined_boundary as paired
from . import tga_proctor_capacity as capacity
from . import tga_proctor_signed_hall as signed
from . import tga_proctor_hall as hall
from . import tga_proctor_xor_cnf as xor
from . import tga_proctor_xor_bve as bve
from . import tga_proctor_hybrid_sat as hybrid
from . import tga_proctor_blind_parity as blind
from . import tga_proctor_dynamic_resolution as graphs

PNP_RESOLUTION_STATUS = "OPEN"


def derive(n,clauses,signature_limit=200000,step_limit=100000):
    """Charge each examined normalized literal, and each unique output.

    On exhaustion keep the entailed prefix; do not call it saturation.
    """
    bve._budget(signature_limit)
    bve._budget(step_limit)
    cs=xor._input(n,clauses)
    seen,derived={},{}
    scanned=0

    def report(reason):
        return dict(clauses=tuple(derived),steps=tuple(derived.values()),
                    signature_count=scanned,resolution_steps=len(derived),
                    stopped=reason)

    if signature_limit==0 or step_limit==0:
        return report("DISABLED")
    for i,c in enumerate(cs):
        s=frozenset(c)
        if any(-l in s for l in s):
            continue
        for lit in sorted(s):
            if scanned==signature_limit:
                return report("SIGNATURE_LIMIT")
            tail=tuple(sorted(s-{lit}))
            scanned+=1
            j=seen.get((tail,-lit))
            if j is not None and tail not in derived:
                derived[tail]=(i,j,lit) if lit>0 else (j,i,-lit)
                if len(derived)==step_limit:
                    return report("STEP_LIMIT")
            seen.setdefault((tail,lit),i)
    return report("COMPLETE_SCAN")


def _infer(n,cs):
    """Only UNSAT engines; no recursive mixed inference or search."""
    scans=0
    for k in (1,2):
        r=capacity.solve(n,cs,k)
        scans+=r["edge_scans"]
        if r["status"]=="UNSAT":
            return "CAPACITY",r,scans
    for tag,module in (("SIGNED_HALL",signed),("HALL",hall)):
        r=module.solve(n,cs)
        scans+=r["edge_scans"]
        if r["status"]=="UNSAT":
            return tag,r,scans
    r=xor.solve(n,cs)
    if r["status"]=="UNSAT":
        return "XOR",r,scans
    return None,None,scans


def _verify_inner(n,cs,tag,proof):
    modules={"CAPACITY":capacity,"SIGNED_HALL":signed,"HALL":hall,"XOR":xor}
    return tag in modules and modules[tag].verify(n,cs,proof)


def solve(n,clauses,pair_limit=100000,node_limit=1024,*,
          signature_limit=200000,step_limit=100000,allow_wide=False):
    for b in (pair_limit,node_limit,signature_limit,step_limit):
        bve._budget(b)
    if type(allow_wide) is not bool:
        raise ValueError("allow_wide must be Boolean")
    cs=xor._input(n,clauses)
    # Try the unchanged policy's nonbranching stages first. Their
    # pair charge is retained; only remaining pair budget can be spent.
    direct=capacity.solve_hybrid(n,cs,pair_limit,0,allow_wide=allow_wide)
    spent=direct["pair_tests"]
    common=dict(signature_limit=signature_limit,step_limit=step_limit,
                signature_count=0,resolution_steps=0,mixed_edge_scans=0,
                mixed_stop="NOT_RUN")
    if direct["status"]=="UNSAT":
        return dict(direct,**common,node_limit=node_limit)
    d=derive(n,cs,signature_limit,step_limit)
    common.update(signature_count=d["signature_count"],
                  resolution_steps=d["resolution_steps"],mixed_stop=d["stopped"])
    if d["steps"]:
        # Augment, not replace, so partial derivations can interact with
        # original clauses. Also try the derived subset alone: keeping
        # guard clauses can obscure the recovered matching structure.
        for scope,target in (("DERIVED",d["clauses"]),("AUGMENTED",cs+d["clauses"])):
            tag,p,scans=_infer(n,target)
            common["mixed_edge_scans"]+=scans
            if tag is not None:
                out=dict(status="UNSAT",route="MIXED",proof=(d["steps"],scope,tag,p),
                         ids=hybrid._ids(cs),pair_tests=spent,search_nodes=0,
                         pair_limit=pair_limit,node_limit=node_limit,
                         cost_model="SEPARATE_ABSTRACT_SIGNATURE_STEP_PAIR_NODE_EDGE_COUNTS",
                         resolution_status=PNP_RESOLUTION_STATUS,**common)
                if not verify(n,cs,out,allow_wide=allow_wide):
                    raise AssertionError("mixed certificate rejected")
                return out
    if node_limit==0:
        return dict(direct,**common,node_limit=0)
    # Re-run old policy on ORIGINAL clauses with the remaining pair
    # budget. This may repeat uncharged recognition; no budget refund.
    r=capacity.solve_hybrid(n,cs,pair_limit-spent,node_limit,allow_wide=allow_wide)
    return dict(r,**common,pair_tests=spent+r["pair_tests"],pair_limit=pair_limit)


def verify(n,clauses,result,*,allow_wide=False):
    cs=xor._input(n,clauses)
    try:
        if result["route"]!="MIXED":
            return capacity.verify_hybrid(n,cs,result,allow_wide=allow_wide)
        if result["status"]!="UNSAT" or tuple(result["ids"])!=hybrid._ids(cs):
            return False
        steps,scope,tag,p=result["proof"]
        derived=paired.replay(n,cs,steps)
        if derived is None or not derived:
            return False
        if scope=="DERIVED":
            target=derived
        elif scope=="AUGMENTED":
            target=cs+derived
        else:
            return False
        return _verify_inner(n,target,tag,p)
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return False


def controls():
    rng=Random(34001)
    outcomes=Counter()
    for _ in range(1000):
        ids=tuple(10**40+19*i for i in range(rng.randrange(1,7)))
        n=2**200
        cs=tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                       for _ in range(rng.randrange(0,6)))
                 for _ in range(rng.randrange(18)))
        sat=xor._brute(cs)
        for sig,steps,pairs,nodes in ((0,0,0,0),(10,2,3,1),(1000,1000,20,10000)):
            r=solve(n,cs,pairs,nodes,signature_limit=sig,step_limit=steps,allow_wide=True)
            if (r["signature_count"]>sig or r["resolution_steps"]>steps
                    or r["pair_tests"]>pairs or r["search_nodes"]>nodes):
                raise AssertionError("budget violation")
            if r["status"]=="UNKNOWN":
                if verify(n,cs,r,allow_wide=True) or nodes==10000:
                    raise AssertionError("unexpected unknown")
            elif r["status"]!=("SAT" if sat else "UNSAT") or not verify(n,cs,r,allow_wide=True):
                raise AssertionError("incorrect mixed result")
            outcomes[r["status"]]+=1
    fixtures=[]
    for h in (4,5,6,7,16,32):
        n,cs=paired.guarded_php(h)
        n,cs=blind.relabel(n,cs,29)
        r=solve(n,cs,0,0)
        if r["route"]!="MIXED" or not verify(n,cs,r):
            raise AssertionError("guarded PHP route failed")
        fixtures.append(dict(family="PHP",size=h,clauses=len(cs),inner=r["proof"][2],
                             signatures=r["signature_count"],steps=r["resolution_steps"],
                             search_nodes=r["search_nodes"],pair_tests=r["pair_tests"]))
    for q in (4,8,16,32,64,80):
        n,cs=graphs.tseitin(q,graphs.cubic_graph(q,11),(True,)+(False,)*(q-1))
        n,cs=blind.shared_selector(n,cs)
        n,cs=blind.relabel(n,cs,29)
        r=solve(n,cs,0,0)
        if r["route"]!="MIXED" or not verify(n,cs,r):
            raise AssertionError("guarded XOR route failed")
        fixtures.append(dict(family="TSEITIN",size=q,clauses=len(cs),inner=r["proof"][2],
                             signatures=r["signature_count"],steps=r["resolution_steps"],
                             search_nodes=r["search_nodes"],pair_tests=r["pair_tests"]))
    return dict(random_cases=1000,budgeted_runs=3000,outcomes=dict(outcomes),fixtures=fixtures,
                resolution_status=PNP_RESOLUTION_STATUS,universal_bound=False,
                machine_refinement=False,independent_review=False)


if __name__=="__main__":
    import json
    print(json.dumps(controls(),indent=2))
