"""F033: shared-selector PHP obstruction to the current combined policy.

Separate one-round resolution+Hall experiment; does not change the
existing hybrid or claim a lower bound for the combined proof language.
"""
from collections import Counter
from random import Random

from . import tga_proctor_capacity as capacity
from . import tga_proctor_hall as hall
from . import tga_proctor_signed_hall as signed
from . import tga_proctor_xor_cnf as xor
from . import tga_proctor_blind_parity as blind
from . import tga_proctor_xor_bve as bve
from . import tga_proctor_dynamic_resolution as resolution
from .tga_proctor_hybrid_adversary import pigeonhole

PNP_RESOLUTION_STATUS = "OPEN"


def guarded_php(holes,pigeons=None):
    n,cs=pigeonhole(holes,pigeons)
    return blind.shared_selector(n,cs)


def paired_resolvents(n,clauses):
    """Find equal tails with opposing pivots, using only original clauses.

    At most one representative per derived tail. No oracle selector,
    full BVE cross-product, repeated saturation or search.
    """
    cs=xor._input(n,clauses)
    seen,derived={},{}
    signatures=0
    for i,c in enumerate(cs):
        s=frozenset(c)
        if any(-l in s for l in s):
            continue
        for lit in sorted(s):
            tail=tuple(sorted(s-{lit}))
            signatures+=1
            j=seen.get((tail,-lit))
            if j is not None:
                if lit>0:
                    step=(i,j,lit)
                else:
                    step=(j,i,-lit)
                derived.setdefault(tail,step)
            seen.setdefault((tail,lit),i)
    return tuple(derived),tuple(derived.values()),signatures


def replay(n,clauses,steps):
    """Check one-step resolution parents and reconstruct their exact tails."""
    cs=xor._input(n,clauses)
    try:
        out=[]
        for a,b,p in steps:
            if (any(type(i) is not int or not 0<=i<len(cs) for i in (a,b))
                    or type(p) is not int or not 1<=p<=n):
                return None
            left,right=set(cs[a]),set(cs[b])
            if p not in left or -p not in right:
                return None
            if any(-l in left for l in left) or any(-l in right for l in right):
                return None
            tail=left-{p}
            if tail!=right-{-p}:
                return None
            out.append(tuple(sorted(tail)))
        return tuple(out)
    except (TypeError,ValueError,IndexError,AttributeError):
        return None


def solve_paired_hall(n,clauses):
    cs=xor._input(n,clauses)
    derived,steps,count=paired_resolvents(n,cs)
    h=signed.solve(n,derived)
    common=dict(signature_count=count,resolution_steps=len(steps),
                hall_edge_scans=h["edge_scans"],resolution_status=PNP_RESOLUTION_STATUS)
    if h["status"]!="UNSAT":
        return dict(status="UNKNOWN",**common)
    out=dict(status="UNSAT",certificate=(steps,h),**common)
    if not verify_paired_hall(n,cs,out):
        raise AssertionError("paired Hall replay failed")
    return out


def verify_paired_hall(n,clauses,result):
    cs=xor._input(n,clauses)
    try:
        if result["status"]!="UNSAT":
            return False
        steps,h=result["certificate"]
        residual=replay(n,cs,steps)
        return residual is not None and signed.verify(n,residual,h)
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return False


def audit(holes,seed,node_limit):
    n,cs=guarded_php(holes)
    n,cs=blind.relabel(n,cs,seed)
    # Audit each shortcut separately, rather than infer failure solely
    # from the wrapper result.
    if any(capacity.solve(n,cs,k)["status"]!="UNKNOWN" for k in (1,2)):
        raise AssertionError("capacity shortcut unexpectedly recognized")
    if signed.solve(n,cs)["status"]!="UNKNOWN" or hall.solve(n,cs)["status"]!="UNKNOWN":
        raise AssertionError("Hall shortcut unexpectedly recognized")
    if xor.detect(n,cs) or blind.schedule(n,cs):
        raise AssertionError("algebraic shortcut unexpectedly recognized")
    result=capacity.solve_hybrid(n,cs,1000,node_limit,allow_wide=True)
    if result["pair_tests"]!=0 or result["search_nodes"]>node_limit:
        raise AssertionError("wrong hybrid counters")
    proof_lines=None
    if result["status"]=="UNSAT":
        if result["route"]!="DYNAMIC_PROJECTED" or not capacity.verify_hybrid(n,cs,result,allow_wide=True):
            raise AssertionError("wrong hybrid refutation")
        pre,search=result["proof"]
        residual=bve.replay(n,cs,pre)
        if pre["steps"] or pre["eliminations"] or residual!=tuple(tuple(sorted(c)) for c in cs):
            raise AssertionError("expected identity projection")
        p=resolution.extract(n,residual,search,wide=True)
        if not resolution.verify(n,residual,p,wide=True):
            raise AssertionError("resolution proof failed")
        proof_lines=len(p["steps"])
    elif result["status"]!="UNKNOWN":
        raise AssertionError("guarded PHP cannot be SAT")
    mixed=solve_paired_hall(n,cs)
    if mixed["status"]!="UNSAT" or not verify_paired_hall(n,cs,mixed):
        raise AssertionError("mixed certificate failed")
    return dict(holes=holes,seed=seed,clauses=len(cs),hybrid_status=result["status"],
                hybrid_node_limit=node_limit,hybrid_nodes=result["search_nodes"],hybrid_resolution_lines=proof_lines,
                hybrid_pair_tests=result["pair_tests"],
                mixed_resolution_steps=mixed["resolution_steps"],
                mixed_signature_count=mixed["signature_count"],
                mixed_hall_edge_scans=mixed["hall_edge_scans"])


def controls():
    rng=Random(33004)
    counts=Counter()
    for _ in range(1600):
        ids=tuple(10**40+19*i for i in range(rng.randrange(1,7)))
        n=2**200
        cs=tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                       for _ in range(rng.randrange(0,6)))
                 for _ in range(rng.randrange(18)))
        derived,steps,count=paired_resolvents(n,cs)
        if replay(n,cs,steps)!=derived or count>sum(map(len,cs)):
            raise AssertionError("bad signature replay")
        r=solve_paired_hall(n,cs)
        if r["status"]=="UNSAT":
            if xor._brute(cs) or not verify_paired_hall(n,cs,r):
                raise AssertionError("false mixed refutation")
        elif r["status"]!="UNKNOWN" or verify_paired_hall(n,cs,r):
            raise AssertionError("bad result")
        counts[r["status"]]+=1
    fixtures=[audit(h,seed,100000 if h<=5 else (1000 if h<=7 else 1))
              for h in (4,5,6,7,16,32) for seed in (11,29)]
    for row in fixtures:
        if row["holes"]<=5 and row["hybrid_status"]!="UNSAT":
            raise AssertionError("small dynamic comparison exhausted")
    equal=0
    for h in (4,5,6,7,16,32):
        n,cs=guarded_php(h,h)
        n,cs=blind.relabel(n,cs,11)
        if solve_paired_hall(n,cs)["status"]!="UNKNOWN":
            raise AssertionError("equal-size false refutation")
        equal+=1
    return dict(random_cases=1600,outcomes=dict(counts),fixtures=fixtures,
                equal_controls=equal,resolution_status=PNP_RESOLUTION_STATUS,
                combined_proof_system_lower_bound=False,machine_refinement=False,
                independent_review=False)


if __name__=="__main__":
    import json
    print(json.dumps(controls(),indent=2))
