"""Certified signed Horn forward-chaining schema. Search is not trusted."""
from collections import defaultdict, deque
from itertools import combinations

from .pnp_structural_kernel import validate, Exhausted
from .pnp_proof_library import verify_certificate


def normalized(n, formula, budget):
    out=[]
    for c in validate(n,formula):
        budget.tick(1+len(c))
        s=set(c)
        out.append(None if any(-x in s for x in s) else tuple(sorted(s)))
    return out


def rename(c, signs):
    return tuple(x*signs[abs(x)-1] for x in c)


def polarity(n, clauses, budget):
    """2-SAT constraints on signs: no two literals in a clause become positive.

    Positive sign variable means keep original polarity. SCC order supplies
    a candidate assignment; every constraint is rechecked independently.
    """
    g={s*v:set() for v in range(1,n+1) for s in (-1,1)}
    rev={v:set() for v in g}
    pairs=set()
    for c in clauses:
        if c is None:
            continue
        for a,b in combinations(c,2):
            budget.tick()
            pairs.add((-a,-b))
            budget.cells(len(pairs))
            for x,y in ((a,-b),(b,-a)):
                g[x].add(y)
                rev[y].add(x)
    seen=set()
    order=[]
    for root in g:
        if root in seen:
            continue
        seen.add(root)
        stack=[(root,iter(sorted(g[root])))]
        while stack:
            v,it=stack[-1]
            budget.tick()
            u=next(it,None)
            if u is None:
                order.append(v)
                stack.pop()
            elif u not in seen:
                seen.add(u)
                stack.append((u,iter(sorted(g[u]))))
    component={}
    k=0
    for root in reversed(order):
        if root in component:
            continue
        component[root]=k
        stack=[root]
        while stack:
            v=stack.pop()
            budget.tick(1+len(rev[v]))
            for u in sorted(rev[v]):
                if u not in component:
                    component[u]=k
                    stack.append(u)
        k+=1
    if any(component[v]==component[-v] for v in range(1,n+1)):
        return None
    signs=tuple(1 if component[v]>component[-v] else -1 for v in range(1,n+1))
    for a,b in pairs:
        budget.tick()
        if not any(x*signs[abs(x)-1]>0 for x in (a,b)):
            raise AssertionError("invalid polarity assignment")
    return signs


def verify_trace(n,formula,cert,budget):
    """Independent replay of signed original clause IDs, no SCC or queue."""
    raw=validate(n,formula)
    if cert.get("schema")!="mathos-pnp-signed-horn/1":
        raise ValueError("bad schema")
    signs=cert["signs"]
    if (not isinstance(signs,(list,tuple)) or len(signs)!=n or
            any(type(s) is not int or s not in (-1,1) for s in signs)):
        raise ValueError("bad polarity")
    trace=cert["trace"]
    if not isinstance(trace,(list,tuple)) or not 1<=len(trace)<=n+1:
        raise ValueError("bad trace length")
    known=set()
    proof=[]
    for j,i in enumerate(trace):
        if type(i) is not int or not 0<=i<len(raw):
            raise ValueError("bad original clause index")
        c={x*signs[abs(x)-1] for x in raw[i]}
        budget.tick(1+len(c))
        heads={x for x in c if x>0}
        if any(-x in c for x in c) or len(heads)>1 or any(-x not in known for x in c if x<0):
            raise ValueError("unjustified forward inference")
        if not heads:
            if j!=len(trace)-1:
                raise ValueError("trailing records")
            proof.append(())
            return proof
        h=next(iter(heads))
        if h in known:
            raise ValueError("duplicate head")
        known.add(h)
        proof.append((h*signs[h-1],))
    raise ValueError("missing conflict")


def propose(n,formula,budget,*,signed=True):
    """Full signed Horn recognition; ordinary Horn-subset route on explicit request.

    No result is credited on a failed rename, stalled propagation or exhaustion.
    The ordinary route may refute a non-Horn CNF using its Horn subset.
    """
    try:
        clauses=normalized(n,formula,budget)
        signs=polarity(n,clauses,budget) if signed else (1,)*n
        if signs is None:
            return {"status":"not_renamable"}
        watch=defaultdict(list)
        ready=deque()
        remaining={}
        head={}
        for i,c in enumerate(clauses):
            if c is None:
                continue
            budget.tick(1+len(c))
            a=rename(c,signs)
            positive=[x for x in a if x>0]
            if len(positive)>1:
                if signed:
                    raise AssertionError("renaming did not produce Horn")
                continue
            body=[-x for x in a if x<0]
            remaining[i]=len(body)
            head[i]=positive[0] if positive else None
            for v in body:
                watch[v].append(i)
            if not body:
                ready.append(i)
        known=set()
        trace=[]
        while ready:
            i=ready.popleft()
            budget.tick()
            h=head[i]
            if h is None:
                cert={"schema":"mathos-pnp-signed-horn/1","signs":signs,"trace":trace+[i]}
                proof=verify_trace(n,formula,cert,budget)
                verify_certificate(n,formula,proof,budget)
                return {"status":"verified","certificate":cert,"proof":proof}
            if h in known:
                continue
            known.add(h)
            trace.append(i)
            for j in watch[h]:
                budget.tick()
                remaining[j]-=1
                if remaining[j]==0:
                    ready.append(j)
        return {"status":"not_found"}
    except Exhausted:
        return {"status":"resource_exhausted"}
