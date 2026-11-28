"""Memoized signed guard matching, preserving the v17 search order.

Cache only fully explored failed states for one immutable known-clause set.
A cutoff never becomes a logical impossibility.
"""
from collections import defaultdict
from itertools import permutations

from .pnp_proof_abstraction import _original_clauses
from .pnp_proof_library import variables, mapped, verify_certificate, reconstruct
from .pnp_structural_kernel import Exhausted

CACHE_CAP=4096


def memo_find(f,n,known,budget,*,subsumption=True,limit=4096,stats=None):
    stats={} if stats is None else stats
    for key in ("hits","stored","candidate_ticks","lookups","cutoffs"):
        stats.setdefault(key,0)
    vs=variables(known)
    if len(vs)<f["n"]:
        return None
    by_width=defaultdict(list)
    for c in sorted(known):
        by_width[len(c)].append(c)
    options=[(a,tuple(c for w in sorted(by_width) if
                     (w<=len(a) if subsumption else w==len(a))
                     for c in by_width[w])) for a in f["axioms"]]
    options.sort(key=lambda pair:(len(pair[1]),-len(pair[0]),pair[0]))
    attempts=0
    goal=f["steps"][-1]
    dead=set()

    def tick():
        nonlocal attempts
        budget.tick()
        attempts+=1
        stats["candidate_ticks"]+=1
        return attempts<=limit

    def finish(d,used):
        missing=[v for v in range(1,f["n"]+1) if v not in d]
        if not missing:
            e=tuple(d[v] for v in range(1,f["n"]+1))
            return e if mapped(goal,e) not in known else None
        v=missing[0]
        for u in vs:
            if u in used:
                continue
            for x in (u,-u):
                if not tick():
                    return None
                answer=finish({**d,v:x},used|{u})
                if answer is not None:
                    return answer
        return None

    def visit(i,d,used):
        if attempts>=limit:
            return None
        # The used variable set is determined by d. The known clauses,
        # guard order and goal are constant during this invocation.
        key=(i,tuple(sorted(d.items())))
        budget.tick()
        stats["lookups"]+=1
        if key in dead:
            stats["hits"]+=1
            return None
        if i==len(options):
            answer=finish(d,used)
        else:
            answer=None
            a,choices=options[i]
            fixed={d[abs(x)] if x>0 else -d[abs(x)] for x in a if abs(x) in d}
            free=[x for x in a if abs(x) not in d]
            for c in choices:
                if not tick():
                    return None
                remaining=sorted(set(c)-fixed)
                if len(remaining)>len(free) or any(abs(x) in used for x in remaining):
                    continue
                for lits in permutations(free,len(remaining)):
                    if not tick():
                        return None
                    add={abs(x):y if x>0 else -y for x,y in zip(lits,remaining)}
                    answer=visit(i+1,{**d,**add},used|{abs(y) for y in remaining})
                    if answer is not None:
                        return answer
        # Strict inequality is deliberately conservative: a local cutoff
        # cannot be stored, even if the final attempted branch was complete.
        if answer is None and attempts<limit and len(dead)<min(CACHE_CAP,budget.max_cells):
            budget.cells(len(dead)+1)
            dead.add(key)
            stats["stored"]+=1
        return answer

    result=visit(0,{},set())
    if result is None and attempts>=limit:
        stats["cutoffs"]+=1
    return result


def memo_reuse(n,formula,index,budget,*,rounds=4,max_transfers=32):
    """Same traversal, limits and replay as v17 reuse, with memoized find."""
    known=set(_original_clauses(n,formula))
    transfers=[]
    examined=0
    stats={k:0 for k in ("hits","stored","candidate_ticks","lookups","cutoffs")}
    def miss(status):
        return {"status":status,"examined":examined,"memo":stats}
    try:
        for _ in range(rounds):
            changed=False
            for i in index.retrieve(known):
                f=index.templates[i]
                examined+=1
                e=memo_find(f,n,known,budget,stats=stats)
                if e is None:
                    continue
                part=[mapped(c,e) for c in f["steps"]]
                verify_certificate(n,sorted(known),part,budget,contradiction=False)
                transfers.append((i,e))
                known.update(part)
                changed=True
                if () in known:
                    proof=reconstruct(n,formula,index,transfers,budget)
                    return {**miss("verified"),"transfers":transfers,"proof":proof}
                if len(transfers)>=max_transfers:
                    return miss("transfer_limit")
            if not changed:
                break
    except Exhausted:
        return miss("resource_exhausted")
    return miss("not_found")
