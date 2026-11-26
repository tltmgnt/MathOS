"""Same-U cubic-stage necessary condition via exact local 2-CNF closure and hitting sets."""
import json
from itertools import combinations,product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import valid

PLAN='docs/research/tga-universal/f038-unrestricted-bijunctive-core.json'


def truth(c,w):
    return any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c)


LOCAL=tuple(pool(3))
PAIR=tuple(c for c in LOCAL if len(c)==2)
TRIPLE=tuple(c for c in LOCAL if len(c)==3)


def project(mask):
    require(type(mask) is int and 0<=mask<256,'invalid block')
    R=tuple(w for w in range(8)
            if all(not(mask>>i&1) or truth(c,w) for i,c in enumerate(TRIPLE)))
    G=tuple(c for c in PAIR if all(truth(c,w) for w in R))
    W=tuple(w for w in range(8) if all(truth(c,w) for c in G))
    return R,G,W


def classify():
    return tuple(G if R==W else None for R,G,W in map(project,range(256)))


def local():
    st=[0,0,0,0]
    H=[[i,0,0] for i in range(9)]
    for m in range(256):
        R,G,W=project(m)
        maj=all(((a&b)|(b&c)|(a&c)) in R for a,b,c in product(R,repeat=3))
        require((R==W)==maj,'majority versus pair closure')
        st[0]+=1
        st[1]+=R==W
        st[2]+=R!=W
        st[3]+=len(G)
        H[len(R)][1 if R==W else 2]+=1
    return st,H


def cap(n):
    require(type(n) is int and n>=1,'invalid source count')
    b=0
    while 3**(b+1)<=n:
        b+=1
    return b


def hit(S,b):
    """Bounded ternary branching; None is a certified cover miss, not SAT failure."""
    def visit(A):
        I=next((I for I in S if not any(v in A for v in I)),None)
        if I is None:
            return A
        if len(A)==b:
            return None
        for v in I:
            B=visit(A+(v,))
            if B is not None:
                return B
        return None
    return visit(())


def decompose(n,p,C):
    require(type(p) is int and 0<=p<1<<len(C),'invalid selector')
    start=2*n+4*comb(n,2)
    F=[c for j,c in enumerate(C[:start]) if p>>j&1]
    E=[]
    S=[]
    table=classify()
    for j,I in enumerate(combinations(range(1,n+1),3)):
        k=start+8*j
        m=(p>>k)&255
        G=table[m]
        if G is None:
            S.append(I)
            E.extend(C[k+h] for h in range(8) if m>>h&1)
        else:
            F.extend(tuple(I[abs(l)-1] if l>0 else -I[-l-1] for l in c) for c in G)
    return tuple(F),tuple(E),tuple(S)


def vertex(l):
    return 2*(abs(l)-1)+int(l>0)


def solve2(n,F):
    """Explicit reachability, not a random-access runtime claim."""
    N=2*n
    R=[1<<j for j in range(N)]
    for c in F:
        require(1<=len(c)<=2,'nonbinary residual')
        a,b=vertex(c[0]),vertex(c[-1])
        R[a^1]|=1<<b
        R[b^1]|=1<<a
    for k in range(N):
        r=R[k]
        for j in range(N):
            if R[j]>>k&1:
                R[j]|=r
    if any(R[2*i]==R[2*i+1] for i in range(n)):
        return None
    w=sum(int(R[2*i+1]<R[2*i])<<i for i in range(n))
    require(all(truth(c,w) for c in F),'reachability witness failed')
    return w


def solve(C,n,p):
    F,E,S=decompose(n,p,C)
    A=hit(S,cap(n))
    if A is None:
        return None,S,None
    require(all(any(v in A for v in I) for I in S),'invalid cover')
    for a in range(1<<len(A)):
        P={v:bool(a>>i&1) for i,v in enumerate(A)}
        G=list(F)+[(v if P[v] else -v,) for v in A]
        for c in E:
            if any(abs(l) in P and P[abs(l)]==(l>0) for l in c):
                continue
            r=tuple(l for l in c if abs(l) not in P)
            if not r:
                break
            require(len(r)<=2,'unhit triple')
            G.append(r)
        else:
            w=solve2(n,G)
            if w is not None:
                require(valid(C,n,p,w),'source witness failed')
                return w,S,A
    return None,S,A


def fixtures(n,C):
    if n<=2:
        return list(range(1<<len(C)))
    P=[m<<(len(C)-8) for m in range(256)] if n==3 else []
    if n<=5:
        for seed in range(128):
            x=seed+1
            w=seed%(1<<n)
            p=0
            for i,c in enumerate(C):
                x=(1664525*x+1013904223)&0xffffffff
                if x>>29<2 and (not seed&1 or truth(c,w)):
                    p|=1<<i
            P.append(p)
        return P
    sets=((),((1,2,3),),((1,2,3),(4,5,6)),
          ((1,2,3),(4,5,6),(7,8,9)),
          ((1,2,3),(1,4,5),(1,6,7),(1,8,9)),
          ((1,2,3),(4,5,6),(1,7,8)))
    P=[sum(1<<i for i,c in enumerate(C) if c in S) for S in sets]
    P.append(sum(1<<i for i,c in enumerate(C) if len(c)==3 and truth(c,0x155)))
    P.append(sum(1<<i for i,c in enumerate(C) if len(c)==3 and tuple(map(abs,c))==(1,2,3)))
    return P


def audit_rows():
    rows=[]
    for n in (1,2,3,4,5,9):
        C=pool(n)
        P=fixtures(n,C)
        b=cap(n)
        st=[n,b,len(P),0,0,0,0,0,0,0]
        for p in P:
            w,S,A=solve(C,n,p)
            F=[c for j,c in enumerate(C) if p>>j&1]
            W=[w0 for w0 in range(1<<n) if all(truth(c,w0) for c in F)]
            cover=any(all(any(v in B for v in I) for I in S)
                      for k in range(b+1) for B in combinations(range(1,n+1),k))
            require(cover==(A is not None),'cover existence mismatch')
            require((w is not None)==(cover and bool(W)),'bounded solver mismatch')
            require(w is None or w in W,'invalid output')
            st[3]+=len(S)
            st[4]+=cover
            st[5]+=not cover
            st[6]+=bool(W)
            st[7]+=w is not None
            st[8]+=cover and not W
            st[9]+=len(W)
        rows.append(st)
    return rows


def controls():
    # Exact original selector order, including the sign-index convention.
    for n in (3,5,9):
        C=pool(n)
        start=2*n+4*comb(n,2)
        for j,I in enumerate(combinations(range(1,n+1),3)):
            G=tuple(tuple(v*b for v,b in zip(I,B)) for B in product((-1,1),repeat=3))
            require(C[start+8*j:start+8*j+8]==G,'original pool order')
    require(solve2(1,((1,),))==1 and solve2(1,((-1,),))==0
            and solve2(1,((1,),(-1,))) is None,'implication control')
    require(hit(((1,2,3),(4,5,6),(7,8,9)),2) is None
            and len(hit(((1,2,3),(4,5,6),(7,8,9)),3))==3,'cover cap')
    require(all(cap(n)==b for n,b in ((1,0),(2,0),(3,1),(8,1),(9,2),(26,2),(27,3))),
            'budget boundaries')
    return 4


def audit():
    a,b=local()
    result={'controls':controls(),'hist':b,'local':a,'rows':audit_rows()}
    print('F038_UNRESTRICTED_BIJUNCTIVE_CORE_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
