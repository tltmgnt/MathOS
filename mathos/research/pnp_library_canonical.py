"""Bounded exact signed-orbit canonicalization of guarded conclusions.

This identifies the same guarded consequence, not identical proof DAGs
or all logically equivalent guards. Unknown canonicalizations are kept.
"""
from collections import defaultdict, Counter
from itertools import permutations, product

from .pnp_proof_library import mapped, verify_certificate
from .pnp_evidence_benchmark import digest

ORBIT_CAP=8192


def signature(f,budget):
    """Variable polarity profiles from unique guards and distinguished goal."""
    n=f["n"]
    guards=tuple(sorted({tuple(sorted(set(c))) for c in f["axioms"]}))
    goal=tuple(sorted(set(f["steps"][-1])))
    profiles={s*v:Counter() for v in range(1,n+1) for s in (-1,1)}
    for c in guards:
        budget.tick(1+len(c))
        for x in c:
            profiles[x][len(c)]+=1
    for x in goal:
        budget.tick()
        profiles[x][-1]+=1
    groups=defaultdict(list)
    for v in range(1,n+1):
        budget.tick()
        p=tuple(sorted(profiles[v].items()))
        m=tuple(sorted(profiles[-v].items()))
        groups[min(p,m),max(p,m)].append((v,(1,-1) if p==m else ((1,) if p<m else (-1,))))
    return guards,goal,tuple(tuple(groups[k]) for k in sorted(groups))


def canonical(f,budget,*,cap=ORBIT_CAP):
    """Exact key if all profile-compatible bijections are explored.

    The canonical labels are assigned in increasing invariant profile order.
    Tied profiles and polarities are enumerated, never guessed.
    """
    if type(cap) is not int or cap<1:
        raise ValueError("positive orbit cap required")
    guards,goal,groups=signature(f,budget)
    n=f["n"]
    total=1
    for group in groups:
        for j in range(1,len(group)+1):
            total*=j
            if total>cap:
                return {"status":"unknown","reason":"orbit_cap"}
        for _,signs in group:
            total*=len(signs)
            if total>cap:
                return {"status":"unknown","reason":"orbit_cap"}
    best=None
    best_e=None
    examined=0
    def visit(i,start,e):
        nonlocal best,best_e,examined
        if i==len(groups):
            budget.tick(1+sum(map(len,guards))+len(goal))
            examined+=1
            key=(n,tuple(sorted(mapped(c,e) for c in guards)),mapped(goal,e))
            if best is None or key<best:
                best,best_e=key,tuple(e)
            return
        group=groups[i]
        for labels in permutations(range(start,start+len(group))):
            for signs in product(*(s for _,s in group)):
                budget.tick()
                for (v,_),label,sign in zip(group,labels,signs):
                    e[v-1]=label*sign
                visit(i+1,start+len(group),e)
    visit(0,1,[0]*n)
    if examined!=total:
        raise AssertionError("orbit enumeration accounting")
    return {"status":"exact","key":best,"embedding":best_e,"examined":examined}


def witness(source,target):
    """Compose source->canonical with inverse target->canonical."""
    inv={abs(x):v if x>0 else -v for v,x in enumerate(target,1)}
    return tuple(inv[abs(x)] if x>0 else -inv[abs(x)] for x in source)


def verify_equivalence(a,b,e,budget):
    """Directly check signed bijection of premise sets and conclusion."""
    n=a["n"]
    if (n!=b["n"] or len(e)!=n or any(type(x) is not int or not 0<abs(x)<=n for x in e)
            or len({abs(x) for x in e})!=n):
        raise ValueError("invalid signed bijection")
    budget.tick(1+sum(map(len,a["axioms"]))+sum(map(len,b["axioms"])))
    if ({mapped(c,e) for c in a["axioms"]}!={tuple(c) for c in b["axioms"]}
            or mapped(a["steps"][-1],e)!=tuple(b["steps"][-1])):
        raise ValueError("guard or goal mismatch")
    return True


def compact(library,budget,*,cap=ORBIT_CAP):
    """Keep first representative of each exact guarded-conclusion orbit.

    Both proofs must replay; deletion has an explicit equivalence witness.
    Unknowns never collide with exact keys or each other. IDs in the new
    library are local; provenance records original IDs.
    """
    frozen=digest(library)
    seen={}
    kept=[]
    decisions=[]
    for i,f in enumerate(library):
        verify_certificate(f["n"],f["axioms"],f["steps"],budget,contradiction=False)
        c=canonical(f,budget,cap=cap)
        if c["status"]=="exact" and c["key"] in seen:
            j,old=seen[c["key"]]
            e=witness(c["embedding"],old)
            verify_equivalence(f,library[j],e,budget)
            decisions.append({"source":i,"status":"duplicate","representative":j,
                              "embedding":e,"examined":c["examined"]})
        else:
            kept.append(f)
            d={"source":i,"status":"kept","new_id":len(kept)-1,
               "canonical":c["status"]}
            if c["status"]=="exact":
                seen[c["key"]]=(i,c["embedding"])
                d["examined"]=c["examined"]
            decisions.append(d)
    if frozen!=digest(library):
        raise AssertionError("library mutated")
    return tuple(kept),decisions
