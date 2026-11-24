"""F034: round-depth audit and bounded chained paired replay.

Separate experimental router. A full round uses only the preceding
frontier; it is not general resolution or complete SAT inference.
"""
from collections import Counter
from itertools import product
from random import Random

from . import tga_proctor_mixed_routing as mixed
from . import tga_proctor_combined_boundary as paired
from . import tga_proctor_capacity as capacity
from . import tga_proctor_blind_parity as blind
from . import tga_proctor_xor_cnf as xor
from . import tga_proctor_xor_bve as bve
from . import tga_proctor_dynamic_resolution as graphs
from . import tga_proctor_hybrid_sat as hybrid
from .tga_proctor_hybrid_adversary import pigeonhole

PNP_RESOLUTION_STATUS = "OPEN"


def guarded(n,clauses,depth):
    """Explicit all-pattern guard expansion, equivalent pointwise.

    Exponential in depth, not a succinct encoding. Depth capped for
    this fixture generator, not a complexity claim about arbitrary CNF.
    """
    if type(depth) is not int or not 0<=depth<=5:
        raise ValueError("fixture depth must be 0..5")
    cs=xor._input(n,clauses)
    guards=tuple(range(n+1,n+depth+1))
    return n+depth,tuple(c+tuple(v if b else -v for v,b in zip(guards,bits))
                         for c in cs for bits in product((False,True),repeat=depth))


def replay(n,clauses,batches):
    """Replay each nonempty batch using only previous frontier parents.

    No derivation or inference discovery. Reject invalid parent indices
    and empty batches, which cannot make progress to a nonempty proof.
    """
    cs=xor._input(n,clauses)
    try:
        for steps in batches:
            steps=tuple(steps)
            if not steps:
                return None
            cs=paired.replay(n,cs,steps)
            if cs is None:
                return None
        return cs
    except (TypeError,ValueError,IndexError,AttributeError):
        return None


def solve(n,clauses,round_limit=2,signature_limit=200000,step_limit=100000):
    """UNSAT-only experiment, budgets shared across all rounds.

    Try the same four inner engines on each frontier. Never assert SAT.
    Original hybrid routing is intentionally untouched.
    """
    for b in (round_limit,signature_limit,step_limit):
        bve._budget(b)
    cs=xor._input(n,clauses)
    frontier=cs
    batches=[]
    sig=steps=scans=0

    def report(status,reason,**kw):
        return dict(status=status,reason=reason,rounds=len(batches),
                    signature_count=sig,resolution_steps=steps,edge_scans=scans,
                    round_limit=round_limit,signature_limit=signature_limit,
                    step_limit=step_limit,resolution_status=PNP_RESOLUTION_STATUS,**kw)

    for _ in range(round_limit):
        if sig==signature_limit or steps==step_limit:
            return report("UNKNOWN","BUDGET")
        d=mixed.derive(n,frontier,signature_limit-sig,step_limit-steps)
        sig+=d["signature_count"]
        steps+=d["resolution_steps"]
        if not d["steps"]:
            return report("UNKNOWN","NO_NEW_FRONTIER")
        batches.append(d["steps"])
        frontier=d["clauses"]
        tag,p,work=mixed._infer(n,frontier)
        scans+=work
        if tag is not None:
            out=report("UNSAT","CERTIFIED",certificate=(tuple(batches),tag,p))
            if not verify(n,cs,out):
                raise AssertionError("chained replay failed")
            return out
        if d["stopped"]!="COMPLETE_SCAN":
            return report("UNKNOWN","BUDGET")
    return report("UNKNOWN","ROUND_LIMIT")


def verify(n,clauses,result):
    cs=xor._input(n,clauses)
    try:
        if result["status"]!="UNSAT":
            return False
        batches,tag,p=result["certificate"]
        batches=tuple(batches)
        if not batches:
            return False
        frontier=replay(n,cs,batches)
        return frontier is not None and mixed._verify_inner(n,frontier,tag,p)
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return False


def controls():
    rng=Random(34002)
    outcomes=Counter()
    for _ in range(1200):
        ids=tuple(10**40+19*i for i in range(rng.randrange(1,7)))
        n=2**200
        cs=tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                       for _ in range(rng.randrange(0,6)))
                 for _ in range(rng.randrange(18)))
        sat=xor._brute(cs)
        for rounds,sig,steps in ((0,0,0),(2,10,3),(3,1000,1000)):
            r=solve(n,cs,rounds,sig,steps)
            if r["rounds"]>rounds or r["signature_count"]>sig or r["resolution_steps"]>steps:
                raise AssertionError("shared budget exceeded")
            if r["status"]=="UNSAT":
                if sat or not verify(n,cs,r):
                    raise AssertionError("unsound chained inference")
            elif r["status"]!="UNKNOWN" or verify(n,cs,r):
                raise AssertionError("bad outcome")
            outcomes[r["status"]]+=1
    fixtures=[]
    for h in (4,5,8,16):
        for depth in (2,3):
            n,cs=guarded(*pigeonhole(h),depth)
            n,cs=blind.relabel(n,cs,29)
            old=mixed.solve(n,cs,0,0,signature_limit=2000000,step_limit=500000)
            if old["status"]!="UNKNOWN":
                raise AssertionError("one-round PHP obstruction failed")
            low=solve(n,cs,depth-1,2000000,500000)
            high=solve(n,cs,depth,2000000,500000)
            if low["status"]!="UNKNOWN" or high["status"]!="UNSAT" or not verify(n,cs,high):
                raise AssertionError("PHP depth boundary failed")
            fixtures.append(dict(family="PHP",size=h,depth=depth,clauses=len(cs),
                                 old_status=old["status"],low_status=low["status"],
                                 rounds=high["rounds"],signatures=high["signature_count"],
                                 steps=high["resolution_steps"],inner=high["certificate"][1]))
    # For XOR, guards leave the forbidden patterns independent of the
    # guard bits. With a remaining guard, no full XOR block is present.
    # Check this empirically rather than assert all other shortcuts fail.
    for q in (4,8,16,32):
        for depth in (2,3):
            base=graphs.tseitin(q,graphs.cubic_graph(q,11),(True,)+(False,)*(q-1))
            n,cs=guarded(*base,depth)
            n,cs=blind.relabel(n,cs,29)
            old=mixed.solve(n,cs,0,0)
            low=solve(n,cs,depth-1)
            high=solve(n,cs,depth)
            if old["status"]!="UNKNOWN" or low["status"]!="UNKNOWN" or high["status"]!="UNSAT" or not verify(n,cs,high):
                raise AssertionError("Tseitin depth boundary failed")
            fixtures.append(dict(family="TSEITIN",size=q,depth=depth,clauses=len(cs),
                                 old_status=old["status"],low_status=low["status"],
                                 rounds=high["rounds"],signatures=high["signature_count"],
                                 steps=high["resolution_steps"],inner=high["certificate"][1]))
    equal=0
    for h in (4,8):
        for depth in (2,3):
            n,cs=guarded(*pigeonhole(h,h),depth)
            n,cs=blind.relabel(n,cs,11)
            if solve(n,cs,depth)["status"]!="UNKNOWN":
                raise AssertionError("satisfiable guarded PHP refuted")
            equal+=1
    return dict(random_cases=1200,budgeted_runs=3600,outcomes=dict(outcomes),
                fixtures=fixtures,equal_controls=equal,resolution_status=PNP_RESOLUTION_STATUS,
                universal_bound=False,machine_refinement=False,independent_review=False)


if __name__=="__main__":
    import json
    print(json.dumps(controls(),indent=2))
