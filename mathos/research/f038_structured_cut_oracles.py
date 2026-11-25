"""Projected and graphic parity-cut separation; explicit threshold semantics."""
import json
from heapq import heappush,heappop
from itertools import product,combinations
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research import f038_parity_cut_discovery as P

PLAN='docs/research/tga-universal/f038-mrax-structured-cut-oracles.json'


def point(X,D,n):
    require(type(D) is int and D>0 and len(X)==n and all(
        type(x) is int and 0<=x<=D for x in X),'invalid rational point')


def make_basis(vectors):
    B={}
    for v,p in vectors:
        while v:
            j=v.bit_length()-1
            if j not in B:
                B[j]=(v,p)
                break
            a,q=B[j]
            v^=a
            p^=q
    return B


def member(B,v):
    p=0
    while v:
        j=v.bit_length()-1
        if j not in B:
            return None
        a,q=B[j]
        v^=a
        p^=q
    return p


def projected(A,n,X,D):
    point(X,D,n)
    F=sum(1<<i for i,x in enumerate(X) if 0<x<D)
    I=sum(1<<i for i,x in enumerate(X) if x==D)
    B=make_basis(((a&F)|((b^P.parity(a&I))<<n),1<<i)
                 for i,(a,b) in enumerate(A))
    return F,I,B


def lift_cut(A,n,X,D,F,I,v,p):
    a,b=P.combine_rows(A,p)
    require(v==((a&F)|((b^P.parity(a&I))<<n)),'invalid projection provenance')
    z=P.nearest(v&((1<<n)-1),v>>n,X,D)
    if z is None or z[0]>=D:
        return None
    d,f=z
    f|=a&I
    result=d,p,f
    require(P.check_cut(A,n,X,D,result),'invalid lifted cut')
    return result


def separate_projected(A,n,X,D):
    F,I,B=projected(A,n,X,D)
    rows=[(0,0)]
    for a,b in B.values():
        rows.extend((v^a,p^b) for v,p in tuple(rows))
    best=None
    for v,p in rows:
        r=lift_cut(A,n,X,D,F,I,v,p)
        if r is not None and (best is None or r<best):
            best=r
    return best,len(rows)


def separate_half(A,n,X,D=2):
    point(X,D,n)
    require(all(x in (0,D) or 2*x==D for x in X),'not half-integral')
    F,I,B=projected(A,n,X,D)
    targets=(1<<n,)+tuple((1<<i)|(b<<n) for i in P.bits(F) for b in (0,1))
    for v in targets:
        p=member(B,v)
        if p is not None:
            r=lift_cut(A,n,X,D,F,I,v,p)
            require(r is not None,'membership did not lift')
            return r
    return None


def graph_rows(n,E,c):
    # Fundamental cycles from an explicit graph; independent of atom ordering.
    par=list(range(n))
    def root(i):
        while par[i]!=i:
            i=par[i]
        return i
    adj=[[] for _ in range(n)]
    chords=[]
    seen=set()
    for i,(u,v) in enumerate(E):
        require(0<=u<v<n and (u,v) not in seen,'not a simple graph')
        seen.add((u,v))
        a,b=root(u),root(v)
        if a==b:
            chords.append(i)
        else:
            par[a]=b
            adj[u].append((v,i))
            adj[v].append((u,i))
    A=[]
    for i in chords:
        u,v=E[i]
        stack=[(u,-1,1<<i)]
        while stack:
            x,p,a=stack.pop()
            if x==v:
                break
            stack.extend((y,x,a|(1<<j)) for y,j in adj[x] if y!=p)
        else:
            raise ValueError('missing forest path')
        A.append((a,P.parity(a&c)))
    return tuple(A)


def odd_path(n,E,c,X,D,v):
    adj=[[] for _ in range(2*n)]
    for i,(u,w) in enumerate(E):
        for p,f in product((0,1),repeat=2):
            a=2*u+p
            b=2*w+(p^f^(c>>i&1))
            weight=D-X[i] if f else X[i]
            adj[a].append((b,weight,i,f))
            adj[b].append((a,weight,i,f))
    start,end=2*v,2*v+1
    dist={start:0}
    prev={}
    Q=[(0,start)]
    while Q:
        d,u=heappop(Q)
        if d!=dist[u]:
            continue
        if u==end:
            walk=[]
            while u!=start:
                w,i,f=prev[u]
                walk.append((w//2,u//2,i,f))
                u=w
            return d,tuple(reversed(walk))
        for w,weight,i,f in adj[u]:
            z=d+weight
            if z<D and z<dist.get(w,D):
                dist[w]=z
                prev[w]=(u,i,f)
                heappush(Q,(z,w))
    return None


def odd_cycle(walk,c):
    # Stack decomposition of a closed walk, retaining one odd elementary cycle.
    vertices=[walk[0][0]]
    edges=[]
    for u,v,i,f in walk:
        require(vertices[-1]==u,'broken walk')
        edges.append((u,v,i,f))
        if v in vertices:
            k=vertices.index(v)
            cycle=edges[k:]
            if sum(f^(c>>i&1) for u,v,i,f in cycle)%2:
                return tuple(cycle)
            edges=edges[:k]
            vertices=vertices[:k+1]
        else:
            vertices.append(v)
    raise ValueError('odd walk without odd component')


def separate_graph(n,E,c,X,D):
    point(X,D,len(E))
    require(type(c) is int and 0<=c<1<<len(E),'invalid edge charge')
    A=graph_rows(n,E,c)
    B=make_basis((a,1<<i) for i,(a,b) in enumerate(A))
    for v in range(n):
        r=odd_path(n,E,c,X,D,v)
        if r is None:
            continue
        d,walk=r
        C=odd_cycle(walk,c)
        require(len(C)>=3 and len({i for u,v,i,f in C})==len(C),'short odd backtrack')
        a=sum(1<<i for u,v,i,f in C)
        f=sum(1<<i for u,v,i,f in C if f)
        p=member(B,a)
        require(p is not None,'cycle not in span')
        cost=sum(D-X[i] if f>>i&1 else X[i] for i in P.bits(a))
        result=cost,p,f
        require(cost<=d and P.check_cut(A,len(E),X,D,result),'bad graphic cut')
        return result
    return None


def brute(rows,X,D):
    best=D
    checks=0
    for a,b in rows:
        for f in P.submasks(a):
            if P.parity(f)==b:
                continue
            d=sum(D-X[i] if f>>i&1 else X[i] for i in P.bits(a))
            best=min(best,d)
            checks+=1
    return best,checks


def affine_audit():
    R=((1,0),(1,1),(2,0),(3,1),(4,0),(5,1),(6,0),(7,1))
    half=[0]*7
    grid=[0]*4
    for mask in range(256):
        A=tuple(r for i,r in enumerate(R) if mask>>i&1)
        rows={(a,b) for a,b,p in P.span_rows(A,3)}
        half[0]+=1
        for X in product(range(3),repeat=3):
            F=sum(1<<i for i,x in enumerate(X) if x==1)
            I=sum(1<<i for i,x in enumerate(X) if x==2)
            ms=tuple(w for w in range(8) if w&~F==I and all(
                P.parity(a&w)==b for a,b in A))
            forced=bool(ms) and any(all((w>>i&1)==(ms[0]>>i&1) for w in ms)
                                    for i in P.bits(F))
            want=0 if not ms else 1 if forced else 2
            best,k=brute(rows,X,2)
            r=separate_half(A,3,X)
            require(best==want and (2 if r is None else r[0])==best,'half oracle mismatch')
            half[1]+=1
            half[2]+=not ms
            half[3]+=forced
            half[4]+=bool(ms) and not forced
            half[5]+=r is not None
            half[6]+=k
        for X in product(range(5),repeat=3):
            best,k=brute(rows,X,4)
            r,size=separate_projected(A,3,X,4)
            require((4 if r is None else r[0])==best,'projected oracle mismatch')
            grid[0]+=1
            grid[1]+=r is not None
            grid[2]+=size
            grid[3]+=len(rows)
    return half,grid


def graphic_audit():
    all_edges=tuple(combinations(range(4),2))
    st=[0]*5
    for mask in range(64):
        E=tuple(e for i,e in enumerate(all_edges) if mask>>i&1)
        m=len(E)
        cycles=[]
        for a in range(1,1<<m):
            z=0
            for i in P.bits(a):
                u,v=E[i]
                z^=(1<<u)|(1<<v)
            if not z:
                cycles.append(a)
        st[0]+=1
        for c in range(1<<m):
            A=graph_rows(4,E,c)
            require({a for a,b,p in P.span_rows(A,m)}=={0,*cycles},'cycle span mismatch')
            rows=tuple((a,P.parity(a&c)) for a in cycles)
            for X in ((1,)*m,tuple(i%3*2 for i in range(m)),tuple((3*i+c)%5 for i in range(m))):
                best,k=brute(rows,X,4)
                r=separate_graph(4,E,c,X,4)
                require((r is not None)==(best<4),'graphic oracle mismatch')
                if r is not None:
                    require(P.check_cut(A,m,X,4,r),'bad returned cut')
                st[1]+=1
                st[2]+=r is not None
                st[3]+=bool(cycles)
                st[4]+=k
    return st


def controls():
    count=0
    for m in range(2,7):
        p=m+1
        n=m*p
        A=tuple((((1<<m)-1)<<(i*m),1) for i in range(p))
        # For every redundant row the nearest forbidden distance is >=m.
        for a,b,q in P.span_rows(A,n):
            z=P.nearest(a,b,(1,)*n,m)
            require(z is None or z[0]>=m,'fractional parity gap failed')
        require(2<=m and p>m,'bad pigeonhole dimensions')
        count+=1
    return count


def audit():
    half,grid=affine_audit()
    result={'half':half,'grid':grid,'graphic':graphic_audit(),'controls':controls()}
    print('F038_MRAX_STRUCTURED_CUT_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
