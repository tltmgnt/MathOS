"""F036: exact integrality-gap audit for clique and odd-cycle capacities.

No numerical LP solver is needed: all coordinates are exactly 1/3.
The finite coloring search is a test oracle, not a polynomial algorithm.
"""
from itertools import combinations


def graph(k):
    assert k >= 5 and k % 2
    edges = set()
    for i in range(k):
        j = (i+1) % k
        edges.update(tuple(sorted(e)) for e in
                     [(i,j),(i,k+j),(j,k+i),(k+i,2*k)])
    return 2*k+1, sorted(edges)


def cnf(n, edges):
    rows = []
    for v in range(n):
        triple = (3*v+1,3*v+2,3*v+3)
        rows.append(triple)
        rows.extend((-a,-b) for a,b in combinations(triple,2))
    for u,v in edges:
        rows.extend((-3*u-c,-3*v-c) for c in range(1,4))
    return rows


def colorable(n, edges, colors, omit=-1):
    adj = [set() for _ in range(n)]
    for u,v in edges:
        adj[u].add(v)
        adj[v].add(u)
    a = [-1]*n

    def visit(left):
        if not left:
            return True
        candidates = []
        for v in range(n):
            if v != omit and a[v] < 0:
                forbidden = {a[u] for u in adj[v] if a[u] >= 0}
                candidates.append((len(forbidden),len(adj[v]),-v,forbidden))
        _,_,neg_v,forbidden = max(candidates,key=lambda t:t[:3])
        v = -neg_v
        for c in range(colors):
            if c not in forbidden:
                a[v] = c
                if visit(left-1):
                    return True
                a[v] = -1
        return False

    return visit(n-int(omit >= 0))


def audit(k):
    n,edges = graph(k)
    assert len(edges) == 4*k
    E = set(edges)
    assert not any((a,b) in E and (a,c) in E and (b,c) in E
                   for a,b,c in combinations(range(n),3))
    assert not colorable(n,edges,3)
    assert colorable(n,edges,4)
    assert colorable(n,edges,3,omit=2*k)
    rows = cnf(n,edges)
    assert len(rows) == 20*k+4
    # Multiply all clause-relaxation inequalities by 3.
    assert all(sum(1 if l>0 else 2 for l in c)>=3 for c in rows)
    m = 3*n
    adj = {v:set() for v in range(1,m+1)}
    for c in rows:
        if len(c) == 2:
            u,v = (-l for l in c)
            adj[u].add(v)
            adj[v].add(u)
    triangles = 0
    for a in adj:
        for b in adj[a]:
            if b <= a:
                continue
            for c in adj[a] & adj[b]:
                if c > b:
                    triangles += 1
                    # No four-clique implies every clique inequality
                    # holds at x=1/3, including unrestricted sizes.
                    assert not any(d>c for d in adj[a]&adj[b]&adj[c])
    assert triangles == n
    # Every possible simple odd cycle length satisfies its capacity
    # inequality at this point; no cycle enumeration is needed.
    for length in range(3,m+1,2):
        assert length <= 3*(length//2)
    # Every independent set selects at most one color per vertex;
    # 3-uncolorability excludes size n, and deleting the apex
    # supplies size n-1. Thus the exact full-graph capacity is n-1.
    assert m == 3*n
    return n,m,len(rows),n-1,n


if __name__=='__main__':
    for k in range(5,20,2):
        result = audit(k)
        assert result == (2*k+1,6*k+3,20*k+4,2*k,2*k+1)
        print(k,*result)
    print('F036_COLORING_GAP_OK families=8 max_variables=117 max_clauses=384')
