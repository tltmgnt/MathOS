"""Finite-cover obstruction to bounded-support universal model repair.

Use a proper 3-coloring with two neighbors of each alternate color.
Any other coloring differing at a vertex must change at least two
neighbors there. The changed vertices contain a cycle.
"""
from itertools import combinations, permutations
from collections import deque
from mathos.research.f037_log_backdoor import satisfies


def cover(n,edges,colors):
    parent=list(range(n))
    def root(v):
        while parent[v]!=v:
            v=parent[v]
        return v
    labels=[]
    rank=0
    for u,v in edges:
        a,b=root(u),root(v)
        if a!=b:
            parent[a]=b
            labels.append((u,v,0))
        else:
            labels.append((u,v,1<<rank))
            rank+=1
    m=1<<rank
    out=[(u*m+s,v*m+(s^b)) for u,v,b in labels for s in range(m)]
    return n*m,out,[c for c in colors for _ in range(m)]


def adjacency(n,edges):
    a=[set() for _ in range(n)]
    for u,v in edges:
        a[u].add(v)
        a[v].add(u)
    return a


def girth(adj):
    best=len(adj)+1
    for u in range(len(adj)):
        d={u:0}
        p={u:None}
        q=deque([u])
        while q:
            v=q.popleft()
            for w in adj[v]:
                if w not in d:
                    d[w]=d[v]+1
                    p[w]=v
                    q.append(w)
                elif p[v]!=w and p[w]!=v:
                    best=min(best,d[v]+d[w]+1)
        assert len(d)==len(adj)
    return best


def cnf(n,edges):
    f=[]
    for v in range(n):
        a,b,c=range(3*v+1,3*v+4)
        f.extend(((a,b,c),(-a,-b),(-a,-c),(-b,-c)))
    for u,v in edges:
        f.extend((-3*u-c,-3*v-c) for c in (1,2,3))
    return tuple(f)


def audit():
    edges=[(u,v) for u,v in combinations(range(6),2) if u//2!=v//2]
    n,edges,colors=cover(6,edges,[0,0,1,1,2,2])
    assert n==768 and len(edges)==1536
    a=adjacency(n,edges)
    assert girth(a)==6
    for v in range(n):
        assert len(a[v])==4
        counts=[sum(colors[w]==c for w in a[v]) for c in range(3)]
        assert counts[colors[v]]==0 and sorted(counts)==[0,2,2]
    # For nonadjacent vertices a graph fold would require neighborhood
    # inclusion; such inclusion entails a four-cycle here.
    pairs=0
    for u,v in combinations(range(n),2):
        assert not (a[u]<=a[v] or a[v]<=a[u])
        pairs+=1
    f=cnf(n,edges)
    assert len(f)==7680
    models=[]
    for p in permutations(range(3)):
        model={3*v+c+1:p[colors[v]]==c for v in range(n) for c in range(3)}
        assert satisfies(f,model)
        models.append(model)
    # Both values of every bit occur in the six frozen colorings.
    for v in range(1,3*n+1):
        assert {m[v] for m in models}=={False,True}
    assert pairs==294528
    print("F037_FROZEN_MODEL_OK vertices=768 variables=2304 clauses=7680 girth=6 pairs=294528 models=6")


if __name__=="__main__":
    audit()
