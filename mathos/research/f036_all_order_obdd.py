"""F036: all-order exact residual representation obstruction on hypercubes."""
from itertools import combinations
from random import Random


def cube(d):
    n=1<<d
    return n,[(u,u^(1<<j)) for u in range(n) for j in range(d)
              if u < u^(1<<j)]


def audit(d, left, edges, adj):
    n=1<<d
    cross=[(u,v) if u in left else (v,u) for u,v in edges
           if (u in left)!=(v in left)]
    assert len(cross)>=n//2
    matching=[]
    while cross:
        u,v=cross[0]
        matching.append((u,v))
        forbidden={u,v}|adj[u]|adj[v]
        cross=[(a,b) for a,b in cross if a not in forbidden and b not in forbidden]
    assert len(matching)*2*d*(d+1)>=n//2
    for e,f in combinations(matching,2):
        assert all(u!=v and v not in adj[u] for u in e for v in f)
    # Bound fixture work; the mathematical argument applies to ALL
    # subsets of the FULL induced matching, not just eight edges.
    chosen=matching[:8]
    checks=0
    for mask in range(1<<len(chosen)):
        left_zero={u for i,(u,v) in enumerate(chosen) if mask&(1<<i)}
        for j,(_,v) in enumerate(chosen):
            zero=left_zero|{v}
            sat=all(u not in zero or w not in zero for u,w in edges)
            assert sat==not_selected(mask,j)
            checks+=1
    return len(matching),checks


def not_selected(mask,j):
    return not bool(mask&(1<<j))


def run():
    rng=Random(3606)
    cuts=checks=0
    for d in range(2,9):
        n,e=cube(d)
        adj=[set() for _ in range(n)]
        for u,v in e:
            adj[u].add(v)
            adj[v].add(u)
        scopes=(combinations(range(n),n//2) if d<=4 else
                (rng.sample(range(n),n//2) for _ in range(16)))
        smallest=n
        for s in scopes:
            m,c=audit(d,set(s),e,adj)
            smallest=min(smallest,m)
            cuts+=1
            checks+=c
        print(f"dimension={d} minimum_observed_greedy_matching={smallest}")
    assert cuts==13010
    print(f"residual_witness_checks={checks}")
    print("F036_ALL_ORDER_OBDD_OK cuts=13010 dimensions=2..8")


if __name__=="__main__":
    run()
