"""Length-parameterized implication-path refutations over CNF binary subsets.

A known 2-SAT argument, not a discovered novel theorem. No SAT claim on miss.
"""
from collections import deque
from .pnp_structural_kernel import validate, Exhausted
from .pnp_proof_library import verify_certificate


def binary_clauses(n, formula, budget):
    """Extract original normalized units and binary clauses, not inferred edges."""
    out=set()
    empty=False
    for raw in validate(n,formula):
        budget.tick(1+len(raw))
        c=tuple(sorted(set(raw)))
        if not c:
            empty=True
        elif len(c)<=2 and not any(-x in c for x in c):
            out.add(c)
    return out,empty


def graph(n,clauses,budget):
    g={s*v:set() for v in range(1,n+1) for s in (-1,1)}
    rev={v:set() for v in g}
    for c in sorted(clauses):
        a,b=c[0],c[-1]
        for x,y in ((-a,b),(-b,a)):
            budget.tick()
            g[x].add(y)
            rev[y].add(x)
    budget.cells(len(g)+sum(map(len,g.values()))+sum(map(len,rev.values())))
    return {v:tuple(sorted(ns)) for v,ns in g.items()}, {v:tuple(sorted(ns)) for v,ns in rev.items()}


def components(g,rev,budget):
    """Iterative Kosaraju; component labels are not trusted as certificates."""
    seen=set()
    order=[]
    for root in g:
        if root in seen:
            continue
        seen.add(root)
        stack=[(root,iter(g[root]))]
        while stack:
            v,it=stack[-1]
            budget.tick()
            u=next(it,None)
            if u is None:
                order.append(v)
                stack.pop()
            elif u not in seen:
                seen.add(u)
                stack.append((u,iter(g[u])))
    labels={}
    for root in reversed(order):
        if root in labels:
            continue
        labels[root]=root
        todo=[root]
        while todo:
            v=todo.pop()
            budget.tick(1+len(rev[v]))
            for u in rev[v]:
                if u not in labels:
                    labels[u]=root
                    todo.append(u)
    return labels


def path(g,start,end,budget):
    parents={start:None}
    q=deque([start])
    while q:
        v=q.popleft()
        budget.tick(1+len(g[v]))
        if v==end:
            result=[]
            while v is not None:
                budget.tick()
                result.append(v)
                v=parents[v]
            return tuple(reversed(result))
        for u in g[v]:
            if u not in parents:
                parents[u]=v
                q.append(u)
    raise AssertionError("component witness path missing")


def verify_paths(n,formula,certificate,budget):
    """Verify each edge against original clauses, without graph/SCC search."""
    if certificate.get("schema")!="mathos-pnp-implication-paths/1":
        raise ValueError("wrong path schema")
    p=certificate["pivot"]
    if type(p) is not int or not 1<=p<=n:
        raise ValueError("invalid pivot")
    # Independent membership extraction; no graph or search function called.
    raw=validate(n,formula)
    known=set()
    for c in raw:
        budget.tick(1+len(c))
        s=frozenset(c)
        if 1<=len(s)<=2 and not any(-x in s for x in s):
            known.add(s)
    for key,start,end in (("forward",p,-p),("backward",-p,p)):
        seq=certificate[key]
        if (not isinstance(seq,(list,tuple)) or not 2<=len(seq)<=2*n
                or any(type(x) is not int or not 0<abs(x)<=n for x in seq)
                or seq[0]!=start or seq[-1]!=end or len(set(seq))!=len(seq)):
            raise ValueError("invalid simple signed path")
        for a,b in zip(seq,seq[1:]):
            budget.tick()
            if frozenset((-a,b)) not in known:
                raise ValueError("path edge absent from original CNF")
    return [(-p,),(p,),()]


def propose(n,formula,budget):
    """Search a binary-subformula contradiction; return checked proof or unknown."""
    try:
        clauses,empty=binary_clauses(n,formula,budget)
        if empty:
            verify_certificate(n,formula,[],budget)
            return {"status":"input_empty","proof":[]}
        g,rev=graph(n,clauses,budget)
        labels=components(g,rev,budget)
        for p in range(1,n+1):
            budget.tick()
            if labels[p]!=labels[-p]:
                continue
            cert={"schema":"mathos-pnp-implication-paths/1","pivot":p,
                  "forward":path(g,p,-p,budget),"backward":path(g,-p,p,budget)}
            proof=verify_paths(n,formula,cert,budget)
            verify_certificate(n,formula,proof,budget)
            return {"status":"verified","certificate":cert,"proof":proof}
        return {"status":"not_found"}
    except Exhausted:
        return {"status":"resource_exhausted"}
