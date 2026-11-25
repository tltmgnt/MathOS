"""Explicit common obstruction for selected F036/F037 promises.

The embedded non-3-colorable graph is the previously audited
Brinkmann graph; no claim of hardness for general SAT is made.
"""
from itertools import product
from random import Random
from mathos.research.f036_hybrid_barrier import graph as base_graph
from mathos.research.f036_coloring_gap import cnf, colorable
from mathos.research.f037_qhorn import valid


def graph(t):
    assert t>=3
    edges=[]
    n=t
    for u in range(t):
        for v in range(u+1,t):
            a,b=n,n+1
            n+=2
            edges.extend(((u,a),(a,b),(b,v)))
    assert n==t*t
    offset=n
    m,e=base_graph()
    n+=m
    edges.extend((offset+u,offset+v) for u,v in e)
    for i in range(2):
        a,b=n,n+1
        n+=2
        edges.extend(((i,a),(a,b),(b,offset+i)))
    return n,edges


def adjacency(n,edges):
    a=[set() for _ in range(n)]
    for u,v in edges:
        a[u].add(v)
        a[v].add(u)
    return a


def components(a,removed):
    seen=set(removed)
    maximum=count=0
    for u in range(len(a)):
        if u in seen:
            continue
        q=[u]
        seen.add(u)
        for v in q:
            for w in a[v]-seen:
                seen.add(w)
                q.append(w)
        maximum=max(maximum,len(q))
        count+=1
    return maximum,count


def audit():
    n,e=base_graph()
    assert not colorable(n,e,3)
    assert colorable(n,e,4)
    f=cnf(1,[])
    assert all(not valid(f,dict(zip((1,2,3),w)))
               for w in product(range(3),repeat=3))
    rng=Random(3705)
    cuts=articulation=0
    for t in (8,12,16,24,32):
        n,e=graph(t)
        assert n==t*t+25
        a=adjacency(n,e)
        for v in range(n):
            seen=set()
            for u in a[v]:
                for w in a[u]-{v}:
                    assert w not in a[v] and w not in seen
                    seen.add(w)
            assert components(a,{v})[1]==1
            articulation+=1
        f=cnf(n,e)
        # Exactly the primal graph of the coloring CNF.
        b=adjacency(3*n,[(abs(x)-1,abs(y)-1)
                     for c in f for i,x in enumerate(c)
                     for y in c[i+1:]])
        for s in range((t-2)//2+1):
            bound=3*((t-s)**2-2*s)
            for _ in range(16):
                removed=rng.sample(range(3*n),s)
                maximum,count=components(b,removed)
                assert maximum>=bound
                if bound>2*n:
                    assert maximum>2*n
                cuts+=1
        print(f"t={t} variables={3*n} clauses={len(f)} backdoor_lower_bound={n}")
    assert cuts==736 and articulation==2189
    print("F037_PORTFOLIO_BARRIER_OK families=5 cuts=736 articulation=2189 weights=27 max_variables=3147")


if __name__=="__main__":
    audit()
