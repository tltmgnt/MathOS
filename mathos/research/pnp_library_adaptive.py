"""Adaptive, certificate-checked fragment agenda; no solver fallback."""
from collections import Counter, defaultdict
from itertools import permutations

from .pnp_proof_library import mapped, variables, reconstruct, verify_certificate
from .pnp_proof_abstraction import _original_clauses
from .pnp_structural_kernel import Exhausted


def search(f, known, budget, *, subsumption, limit=4096):
    """Dynamic clause ordering with exact witnesses first and a local node cap.

    Return a candidate only if its conclusion is not already subsumed.
    That novelty condition is a heuristic, not a completeness result.
    """
    vs=variables(known)
    if len(vs)<f["n"]:
        return None,"not_found"
    widths=defaultdict(list)
    for c in sorted(known):
        budget.tick(1+len(c))
        widths[len(c)].append(c)
    options=[]
    for a in f["axioms"]:
        choices=tuple(c for w in range(len(a),-1,-1)
                      if subsumption or w==len(a) for c in widths[w])
        if not choices:
            return None,"not_found"
        options.append((tuple(a),choices))
    goal=f["steps"][-1]
    count=0
    limited=False

    def tick():
        nonlocal count,limited
        budget.tick()
        if count>=limit:
            limited=True
            return False
        count+=1
        return True

    def novel(e):
        c=set(mapped(goal,e))
        for k in known:
            budget.tick(1+len(k))
            if len(k)<=len(c) and set(k)<=c:
                return False
        return True

    def finish(d,used):
        missing=[v for v in range(1,f["n"]+1) if v not in d]
        if not missing:
            e=tuple(d[v] for v in range(1,f["n"]+1))
            return e if novel(e) else None
        v=missing[0]
        for u in vs:
            if u in used:
                continue
            for x in (u,-u):
                if not tick():
                    return None
                r=finish({**d,v:x},used|{u})
                if r is not None or limited:
                    return r
        return None

    def compatible(a,choices,d,used):
        fixed={d[abs(x)] if x>0 else -d[abs(x)] for x in a if abs(x) in d}
        free=[x for x in a if abs(x) not in d]
        out=[]
        for c in choices:
            if not tick():
                return None
            remaining=tuple(x for x in c if x not in fixed)
            if len(remaining)<=len(free) and not any(abs(x) in used for x in remaining):
                out.append(remaining)
        return free,out

    def visit(todo,d,used):
        if not todo:
            return finish(d,used)
        # Choose the guard with the fewest compatible target clauses now.
        best=None
        for i in todo:
            a,choices=options[i]
            item=compatible(a,choices,d,used)
            if item is None or not item[1]:
                return None
            key=(len(item[1]),len(item[0]),-len(a),i)
            if best is None or key<best[0]:
                best=(key,i,item)
        _,i,(free,choices)=best
        rest=tuple(j for j in todo if j!=i)
        for c in choices:
            for lits in permutations(free,len(c)):
                if not tick():
                    return None
                add={abs(x):y if x>0 else -y for x,y in zip(lits,c)}
                r=visit(rest,{**d,**add},used|{abs(y) for y in c})
                if r is not None or limited:
                    return r
        return None

    e=visit(tuple(range(len(options))),{},set())
    return e,("matched" if e is not None else "candidate_limit" if limited else "not_found")


def adaptive_reuse(n,formula,index,budget,*,max_transfers=32,limit=4096,
                   rounds=4, allow_subsumption=True):
    """Exact-first agenda with short-conclusion priority and bounded fallback.

    Every credited transfer is replayed and final reconstruction shares the
    same cooperative budget. An exhausted or stalled agenda is UNKNOWN.
    """
    known=set(_original_clauses(n,formula))
    transfers=[]
    counts=Counter()
    # Candidate failures may be retried only when the known clause set grows.
    tried=set()
    def outcome(status,**kwargs):
        return {"status":status,"attempts":dict(counts),"transfers_used":len(transfers),**kwargs}
    try:
        for _ in range(rounds):
            changed=False
            for sub in ((False,True) if allow_subsumption else (False,)):
                ids=index.retrieve(known)
                ids.sort(key=lambda i:(len(index.templates[i]["steps"][-1]),
                                      len(index.templates[i]["axioms"]),
                                      len(index.templates[i]["steps"]),i))
                for i in ids:
                    budget.tick()
                    key=(i,sub,len(known))
                    if key in tried:
                        continue
                    tried.add(key)
                    f=index.templates[i]
                    e,status=search(f,known,budget,subsumption=sub,limit=limit)
                    counts[("sub_" if sub else "exact_")+status]+=1
                    if e is None:
                        continue
                    part=[mapped(c,e) for c in f["steps"]]
                    verify_certificate(n,sorted(known),part,budget,contradiction=False)
                    transfers.append((i,e))
                    known.update(part)
                    changed=True
                    if () in known:
                        proof=reconstruct(n,formula,index,transfers,budget)
                        return outcome("verified",transfers=transfers,proof=proof)
                    if len(transfers)>=max_transfers:
                        return outcome("transfer_limit")
                # Exact progress earns another exact pass before broadening.
                if changed:
                    break
            if not changed:
                return outcome("candidate_limit" if any(k.endswith("candidate_limit") for k in counts)
                               else "not_found")
    except Exhausted:
        return outcome("resource_exhausted")
    return outcome("round_limit")
