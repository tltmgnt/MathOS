"""Parity-preserving reductions to subcubic bipartite independent sets.

An exact small-instance factor eliminator is an audit oracle, not a
polynomial-time algorithm: its intermediate table width is unbounded.
"""
from itertools import combinations, product
from mathos.research.f037_log_backdoor import normalize, satisfies


def core(n, f):
    # Literal vertices: 2*i is false, 2*i+1 true, variable i+1.
    # Each variable guard is adjacent to both choices. Each clause
    # guard is adjacent to all literal choices satisfying that clause.
    edges=set()
    top=2*n
    for i in range(n):
        a,b=2*i,2*i+1
        edges.update(((a,b),(a,top),(b,top)))
        top+=1
    for c in normalize(f):
        for l in c:
            assert 1<=abs(l)<=n
            edges.add((2*(abs(l)-1)+int(l>0),top))
        top+=1
    return top,tuple(sorted(edges))


def expand(n,edges):
    """All clones in side zero; original edges become length-4
    paths, consecutive clones joined by length-6 paths."""
    adj=[[] for _ in range(n)]
    for i,(u,v) in enumerate(edges):
        adj[u].append(i)
        adj[v].append(i)
    top=0
    clones={}
    owners=[]
    side=[]
    out=[]
    def vertex(b):
        nonlocal top
        v=top
        top+=1
        side.append(b)
        return v
    for v in range(n):
        cs=[vertex(0) for _ in range(max(1,len(adj[v])))]
        owners.append(cs)
        for i,c in zip(adj[v],cs):
            clones[v,i]=c
    def path(u,v,k):
        for j in range(1,k):
            w=vertex(j%2)
            out.append(tuple(sorted((u,w))))
            u=w
        out.append(tuple(sorted((u,v))))
    for cs in owners:
        for a,b in zip(cs,cs[1:]):
            path(a,b,6)
    for i,(u,v) in enumerate(edges):
        path(clones[u,i],clones[v,i],4)
    degree=[0]*top
    for a,b in out:
        assert side[a]!=side[b]
        degree[a]+=1
        degree[b]+=1
    assert len(set(out))==len(out)
    assert max(degree,default=0)<=3
    return top,tuple(sorted(out)),tuple(side)


def path_matrix(k):
    a=[[1,0],[0,1]]
    b=[[1,1],[1,0]]
    for _ in range(k):
        a=[[sum(a[i][s]*b[s][j] for s in (0,1))
            for j in (0,1)] for i in (0,1)]
    return tuple(tuple(v%2 for v in row) for row in a)


def brute_graph(n,edges):
    return sum(not any((x>>u)&1 and (x>>v)&1 for u,v in edges)
               for x in range(1<<n))%2


def eliminate(n,edges):
    # Generic binary factor elimination over GF(2), without knowing
    # the reduction gadgets. Factor tables are bit masks.
    factors=[((u,v),7) for u,v in edges]  # excludes selected/selected
    remaining=set(range(n))
    width=0
    while remaining:
        adj={v:set() for v in remaining}
        for s,_ in factors:
            for v in s:
                adj[v].update(w for w in s if w!=v)
        v=min(remaining,key=lambda w:(len(adj[w]),w))
        used=[(s,t) for s,t in factors if v in s]
        factors=[(s,t) for s,t in factors if v not in s]
        scope=tuple(sorted(adj[v]))
        width=max(width,len(scope))
        if not used:
            return 0,width
        positions={w:i for i,w in enumerate(scope)}
        out=0
        for a in range(1<<len(scope)):
            val=0
            for b in (0,1):
                term=1
                for s,t in used:
                    index=sum((b if w==v else (a>>positions[w])&1)<<i
                              for i,w in enumerate(s))
                    term&=(t>>index)&1
                val^=term
            out|=val<<a
        if out==0:
            return 0,width
        if scope:
            factors.append((scope,out))
        remaining.remove(v)
    return 1,width


def audit():
    assert path_matrix(4)==((1,1),(1,0))
    assert path_matrix(6)==((1,0),(0,1))
    paths=0
    for k in (4,6):
        for a,b in product((0,1),repeat=2):
            count=sum(not any(z[i] and z[i+1] for i in range(k))
                      for bits in product((0,1),repeat=k-1)
                      for z in [(a,*bits,b)])
            assert count%2==path_matrix(k)[a][b]
            paths+=1
    graphs=0
    for n in range(5):
        es=tuple(combinations(range(n),2))
        for bits in range(1<<len(es)):
            e=tuple(row for i,row in enumerate(es) if bits&(1<<i))
            N,E,_=expand(n,e)
            assert eliminate(N,E)[0]==brute_graph(n,e)
            graphs+=1
    rows=((),(1,),(-1,),(2,3),(1,-1),(1,1,1),
          (-1,-2,-3),(-1,-2,3),(1,2,-3),(1,2,3),(2,1),(1,2))
    odd=sat=expanded=max_vertices=max_width=0
    for bits in range(1<<len(rows)):
        f=tuple(row for i,row in enumerate(rows) if bits&(1<<i))
        count=sum(satisfies(f,dict(zip((1,2,3),z)))
                  for z in product((False,True),repeat=3))
        n,e=core(3,f)
        got,width=eliminate(n,e)
        assert got==count%2
        sat+=count>0
        odd+=got
        # All 4096 core reductions; 256 regularly spaced full expansions.
        if bits%16==0:
            N,E,_=expand(n,e)
            got,width=eliminate(N,E)
            assert got==count%2
            expanded+=1
            max_vertices=max(max_vertices,N)
            max_width=max(max_width,width)
    # A satisfiable formula with even model count is invisible to
    # unconditioned parity. No parity reduction is a SAT decider alone.
    assert eliminate(*core(2,((1,),)))[0]==0
    assert paths==8 and graphs==76 and expanded==256 and sat==1280
    print(f'odd_formulas={odd} expanded_max_vertices={max_vertices} audit_max_width={max_width}')
    print('F038_PARITY_COMPLEXITY_OK formulas=4096 expanded=256 graphs=76 path_cases=8 sat=1280')


if __name__=='__main__':
    audit()
