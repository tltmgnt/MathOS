"""Audit the common obstruction on the Brinkmann graph.

Adjacency data: SageMath BrinkmannGraph, smallgraphs.py.
https://doc.sagemath.org/html/en/reference/graphs/sage/graphs/generators/smallgraphs.html
The exhaustive coloring oracle is not a polynomial-time solver.
"""
from itertools import combinations, product
from mathos.research.f036_coloring_gap import colorable, cnf
from mathos.research.f036_global_affine import insert, close


def graph():
    # Upper triangular adjacency entries for the 21-vertex graph.
    rows = (
        (2,5,7,13),(3,6,7,8),(4,8,9),(5,9,10),(6,10,11),
        (11,12),(12,13),(15,20),(14,16),(15,17),(16,18),
        (17,19),(18,20),(14,19),(17,18),(18,19),(19,20),(20,)
    )
    return 21, [(i,j) for i,ns in enumerate(rows) for j in ns]


def audit():
    n,e = graph()
    adj=[set() for _ in range(n)]
    for u,v in e:
        adj[u].add(v)
        adj[v].add(u)
    assert len(e)==42 and all(len(a)==4 for a in adj)
    for u,v in combinations(range(n),2):
        common=adj[u]&adj[v]
        assert len(common)<=1
        assert not (common and v in adj[u])
    assert not colorable(n,e,3) and colorable(n,e,4)
    subsets=patterns=pairs=0
    for k in range(1,5):
        for s in combinations(range(n),k):
            rows=[]
            edges=[(i,j) for i,j in combinations(range(k),2) if s[j] in adj[s[i]]]
            for a in product(range(3),repeat=k):
                if all(a[i]!=a[j] for i,j in edges):
                    rows.append(sum(1<<(3*i+c) for i,c in enumerate(a)))
            subsets+=1
            patterns+=len(rows)
            assert rows
            basis=[0]*(3*k)
            rank=sum(insert(basis,a^rows[0],3*k) for a in rows)
            assert rank==2*k
            for i,j in combinations(range(3*k),2):
                seen={((a>>i)&1,(a>>j)&1) for a in rows}
                conflict=i//3==j//3 or (i%3==j%3 and s[j//3] in adj[s[i//3]])
                expected={(0,0),(0,1),(1,0)}
                if not conflict:
                    expected.add((1,1))
                assert seen==expected
                pairs+=1
    assert (subsets,patterns,pairs)==(7546,347445,446103)
    f=cnf(n,e)
    assert len(f)==210
    assert all(sum(1 if l>0 else 2 for l in c)>=3 for c in f)
    a=close(3*n,f)
    assert not a.refuted and a.rank==n
    # Independent parity reachability for all recoloring starts.
    states=[s for u,v in e for s in ((u,v),(v,u))]
    index={s:i for i,s in enumerate(states)}
    tests=0
    for w in range(n):
        trans=[[index[v,z] for z in adj[v] if adj[w]&adj[u]&adj[z]]
               for u,v in states]
        for i in range(len(states)):
            queue=[2*i]
            seen=set(queue)
            for a in queue:
                for b in trans[a//2]:
                    t=2*b+1-a%2
                    if t not in seen:
                        seen.add(t)
                        queue.append(t)
            assert 2*i+1 not in seen
            tests+=1
    assert tests==1764
    print("F036_HYBRID_BARRIER_OK variables=63 clauses=210 scopes=7546 patterns=347445 pairs=446103 recoloring=1764")


if __name__=="__main__":
    audit()
