"""Finite-domain Boolean views: exact local implication certificates.

No general CSP decision completeness or formal machine-cost claim.
A missing contradiction is UNKNOWN. Views are explicit truth tables.
"""
from collections import deque
from dataclasses import dataclass
from itertools import combinations, product
from random import Random


@dataclass(frozen=True)
class Relation:
    scope: tuple
    allowed: frozenset


@dataclass(frozen=True)
class View:
    scope: tuple
    bits: tuple


def relation(q, scope, predicate):
    scope = tuple(scope)
    return Relation(scope, frozenset(a for a in product(range(q),repeat=len(scope))
                                    if predicate(a)))


def view(q, scope, predicate):
    scope = tuple(scope)
    return View(scope, tuple(int(predicate(a)) for a in product(range(q),repeat=len(scope))))


def evaluate(q, v, x):
    i = 0
    for u in v.scope:
        i = q*i+x[u]
    return v.bits[i]


def forbidden(q, constraints, a, b):
    scope = sorted(set(a.scope) | set(b.scope))
    local = [c for c in constraints if set(c.scope) <= set(scope)]
    seen = set()
    for vals in product(range(q),repeat=len(scope)):
        x = dict(zip(scope,vals))
        if all(tuple(x[u] for u in c.scope) in c.allowed for c in local):
            seen.add((evaluate(q,a,x),evaluate(q,b,x)))
    return {(i,j) for i in (0,1) for j in (0,1)} - seen


def path(adj, start, goal):
    queue = deque([start])
    parent = {start:None}
    while queue:
        u = queue.popleft()
        if u == goal:
            out = []
            while u is not None:
                out.append(u)
                u = parent[u]
            return tuple(reversed(out))
        for v in sorted(adj[u]):
            if v not in parent:
                parent[v] = u
                queue.append(v)
    return None


def check(q, constraints, views, cert):
    p,r = cert
    if not p or not r or any(not 0<=u<2*len(views) for u in (*p,*r)):
        return False
    if p[0]^1 != p[-1] or r[0]!=p[-1] or r[-1]!=p[0]:
        return False
    for seq in (p,r):
        for a,b in zip(seq,seq[1:]):
            if (a%2,1-b%2) not in forbidden(q,constraints,views[a//2],views[b//2]):
                return False
    return True


def discover(q, constraints, views):
    adj = [set() for _ in range(2*len(views))]
    for i,a in enumerate(views):
        for j in range(i,len(views)):
            for u,v in forbidden(q,constraints,a,views[j]):
                adj[2*i+u].add(2*j+1-v)
                adj[2*j+v].add(2*i+1-u)
    for i in range(len(views)):
        p = path(adj,2*i,2*i+1)
        if p is not None:
            r = path(adj,2*i+1,2*i)
            if r is not None:
                cert = p,r
                assert check(q,constraints,views,cert)
                return cert
    return None


def boolean_views(n, constraints, pairs=True):
    out = [view(2,(i,),lambda a:a[0]) for i in range(n)]
    if pairs:
        ps = sorted({p for c in constraints for p in combinations(sorted(c.scope),2)})
        out.extend(view(2,p,lambda a:a[0]^a[1]) for p in ps)
    return out


def parity_blocks(t,bad):
    out=[]
    for i in range(t):
        x,y,z,w=range(4*i,4*i+4)
        for u in (z,w):
            for a,b in product(range(2),repeat=2):
                d=1-(a^b)
                # Four width-three clauses express each XOR equation.
                out.append(relation(2,(x,y,u),lambda v:v!=(a,b,d)))
        out.append(relation(2,(z,w),lambda v:(v[0]!=v[1])==bad))
    return out


def recoloring_cycle(k):
    # Standard Mycielski cycle with apex color fixed to 2 by symmetry.
    # Remove apex; its edges become unary exclusions on shadows.
    constraints=[]
    for i in range(k):
        j=(i+1)%k
        for s in ((i,j),(i,k+j),(j,k+i)):
            constraints.append(relation(3,s,lambda a:a[0]!=a[1]))
        constraints.append(relation(3,(k+i,),lambda a:a[0]!=2))
    # Total Boolean table; the arbitrary fallback at shadow=2 is
    # irrelevant because that shadow value violates the unary exclusion.
    views=[view(3,(i,k+i),lambda a:(int(a[1]==1) if a[0]==2 else a[0]))
           for i in range(k)]
    return constraints,views


def brute(q, n, constraints):
    return any(all(tuple(x[v] for v in c.scope) in c.allowed for c in constraints)
               for x in product(range(q),repeat=n))


def run():
    for t in range(1,9):
        bad=parity_blocks(t,True)
        assert discover(2,bad,boolean_views(4*t,bad,False)) is None
        vs=boolean_views(4*t,bad)
        cert=discover(2,bad,vs)
        assert cert is not None and check(2,bad,vs,cert)
        good=parity_blocks(t,False)
        assert discover(2,good,boolean_views(4*t,good)) is None
    for k in range(5,17):
        cs,vs=recoloring_cycle(k)
        cert=discover(3,cs,vs)
        assert (cert is not None)==bool(k%2)
    # Corrupt an otherwise valid contradiction path.
    cs=parity_blocks(1,True)
    vs=boolean_views(4,cs)
    p,r=discover(2,cs,vs)
    assert not check(2,cs,vs,(p[:-1],r))
    assert not check(2,[],vs,(p,r))
    assert not check(2,cs,vs,((2*len(vs),),r))
    rng=Random(3605)
    accepted=0
    for _ in range(128):
        cs=[]
        for j in range(15):
            s=tuple(sorted(rng.sample(range(5),2+j%2)))
            bad=tuple(rng.randrange(2) for _ in s)
            cs.append(relation(2,s,lambda a:a!=bad))
        vs=boolean_views(5,cs)
        cert=discover(2,cs,vs)
        if cert is not None:
            assert check(2,cs,vs,cert) and not brute(2,5,cs)
            accepted+=1
    print(f"random accepted={accepted}")
    print("F036_BOOLEAN_VIEWS_OK parity=8 parity_sat=8 graph_unsat=6 graph_sat=6 random=128 rejection=3")


if __name__=="__main__":
    run()
