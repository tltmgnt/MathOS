"""Automatic, bounded discovery of signed premise-strengthening mappings.

Unlike exact inclusion, a target subclause suffices for each template
axiom. The same target clause may witness multiple template axioms.
Only a verified embedding and explicit witnesses certify UNSAT.
"""
from .pnp_structural_kernel import normalize, Exhausted
from .pnp_proof_abstraction import verify_template
from .pnp_knowledge_library import verify_strengthening, budget
from .pnp_evidence_benchmark import digest

MAX_MATCH=4096


def _options(limit):
    if type(limit) is not int or not 1<=limit<=MAX_MATCH:
        raise ValueError("invalid matching limit")


def _target(n,clauses):
    _,f,mapping=normalize(n,clauses)
    return sorted({tuple(sorted(mapping[abs(x)-1] if x>0 else -mapping[-x-1] for x in c))
                   for c in f},key=lambda c:(len(c),c))


def find_strengthening(n,clauses,t,b,*,limit=MAX_MATCH):
    """Find a signed injection with one target subclause per mapped axiom.

    Partial feasibility is necessary only: each target witness's unmatched
    literals must fit into still-unassigned variables of the current axiom.
    Declared unused target variables are allowed as padding in an injection.
    Search is bounded; neither a miss nor exhaustion is a SAT certificate.
    """
    _options(limit)
    ax=verify_template(t,b)
    target=_target(n,clauses)
    if t["n"]>n or any(not any(len(q)<=len(c) for q in target) for c in ax):
        return {"status":"not_found","embedding":None,"witnesses":None,"candidates":0}
    pools=[]
    cells=0
    for c in ax:
        pool=[]
        for q in target:
            b.tick(1+len(q))
            if len(q)<=len(c):
                cells+=1+len(q)
                b.cells(cells)
                pool.append(set(q))
        pools.append(pool)
    order=sorted(range(1,t["n"]+1),key=lambda v:(-sum(v in c or -v in c for c in ax),v))
    active=sorted({abs(x) for q in target for x in q})
    active_set=set(active)
    inactive=[v for v in range(1,n+1) if v not in active_set]
    variables=active+inactive
    assigned={}
    used=set()
    attempts=0
    limited=False

    def feasible():
        for c,pool in zip(ax,pools):
            fixed={assigned[abs(x)] if x>0 else -assigned[abs(x)] for x in c if abs(x) in assigned}
            free=sum(abs(x) not in assigned for x in c)
            possible=False
            for q in pool:
                b.tick(1+len(c)+len(q))
                unmatched=q-fixed
                if len(unmatched)<=free and not ({abs(x) for x in unmatched}&used):
                    possible=True
                    break
            if not possible:
                return False
        return True

    def visit(i):
        nonlocal attempts,limited
        if i==len(order):
            if not feasible():
                return None
            emb=tuple(assigned[v] for v in range(1,t["n"]+1))
            witnesses=[]
            for c,pool in zip(ax,pools):
                mapped={emb[x-1] if x>0 else -emb[-x-1] for x in c}
                for q in pool:
                    b.tick(1+len(q))
                    if q<=mapped:
                        witnesses.append(tuple(sorted(q)))
                        break
            return emb,witnesses
        v=order[i]
        for u in variables:
            if u in used:
                continue
            for x in (u,-u):
                if attempts>=limit:
                    limited=True
                    return None
                attempts+=1
                b.tick()
                assigned[v]=x
                used.add(u)
                result=visit(i+1) if feasible() else None
                used.remove(u)
                del assigned[v]
                if result is not None:
                    return result
                if limited:
                    return None
        return None

    found=visit(0)
    if found is None:
        return {"status":"candidate_limit" if limited else "not_found",
                "embedding":None,"witnesses":None,"candidates":attempts}
    emb,witnesses=found
    verify_strengthening(n,clauses,t,emb,witnesses,b)
    return {"status":"matched","embedding":emb,"witnesses":witnesses,"candidates":attempts}


def query_strengthened(n,f,lib,*,limit=MAX_MATCH):
    _options(limit)
    attempts=[]
    match=None
    for e in lib["entries"]:
        t=e["template"]
        if e["id"]!=digest(t):
            raise ValueError("template identity mismatch")
        b=budget()
        try:
            a=find_strengthening(n,f,t,b,limit=limit)
        except Exhausted:
            a={"status":"resource_exhausted","embedding":None,"witnesses":None,"candidates":None}
        attempts.append({"id":e["id"],**a,"work_steps":b.steps})
        if a["status"]=="matched":
            match={"id":e["id"],"embedding":a["embedding"],"witnesses":a["witnesses"]}
            break
    r={"decision":"unsat" if match is not None else "unknown","match":match,
       "limit":limit,"attempts":attempts,"work_steps":sum(a["work_steps"] for a in attempts)}
    verify_query_strengthened(n,f,lib,r)
    return r


def verify_query_strengthened(n,f,lib,r):
    """Check positive certificates and traversal arithmetic, not search failure."""
    _options(r["limit"])
    attempts=iter(r["attempts"])
    work=0
    match=None
    for e in lib["entries"]:
        t=e["template"]
        if e["id"]!=digest(t):
            raise ValueError("template identity mismatch")
        a=next(attempts,None)
        if (a is None or a["id"]!=e["id"] or a["status"] not in
                ("matched","not_found","candidate_limit","resource_exhausted") or
                type(a["work_steps"]) is not int or not 0<=a["work_steps"]<=2_000_000):
            raise ValueError("attempt metadata mismatch")
        work+=a["work_steps"]
        if a["status"]=="resource_exhausted":
            if a["candidates"] is not None:
                raise ValueError("invalid exhaustion counter")
        elif type(a["candidates"]) is not int or not 0<=a["candidates"]<=r["limit"]:
            raise ValueError("invalid candidate count")
        if a["status"]=="matched":
            verify_strengthening(n,f,t,a["embedding"],a["witnesses"],budget())
            match={"id":e["id"],"embedding":a["embedding"],"witnesses":a["witnesses"]}
            break
        if a["embedding"] is not None or a["witnesses"] is not None:
            raise ValueError("uncredited witness")
    if (next(attempts,None) is not None or digest(match)!=digest(r["match"]) or
            r["decision"]!=("unsat" if match is not None else "unknown") or r["work_steps"]!=work):
        raise ValueError("query conclusion mismatch")
    return True
