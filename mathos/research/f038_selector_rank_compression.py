"""Exact unit/nonunit selector matrix restrictions and finite rank audits."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool

PLAN='docs/research/tga-universal/f038-mrax-selector-rank-compression.json'


def partials(n):
    return tuple(tuple((a//(3**i))%3 for i in range(n)) for a in range(3**n))


def units(a):
    require(all(t in (0,1,2) for t in a),'invalid partial assignment')
    return tuple(((i+1) if t==2 else -(i+1),) for i,t in enumerate(a) if t)


def gadget(b):
    n=len(b)
    require(n>=2 and all(t in (0,1,2) for t in b),'invalid gadget dimensions')
    C=set()
    for i,t in enumerate(b):
        if t:
            l=(i+1) if t==2 else -(i+1)
            z=(i+1)%n+1
            for v in (-z,z):
                C.add(tuple(sorted((l,v),key=abs)))
    return tuple(sorted(C))


def models(C,n):
    return sum(1<<w for w in range(1<<n) if all(
        any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c) for c in C))


def compatible(a,b):
    return all(not x or not y or x==y for x,y in zip(a,b))


def rank2(rows,m):
    B={}
    for v in rows:
        while v:
            j=v.bit_length()-1
            if j not in B:
                B[j]=v
                break
            v^=B[j]
    require(all(v<1<<m for v in B.values()),'row outside matrix')
    return len(B)


def rank3(rows,m):
    # Integer residue arithmetic, not floating-point rank.
    A=[[(v>>j)&1 for j in range(m)] for v in rows]
    r=0
    for j in range(m):
        k=next((k for k in range(r,len(A)) if A[k][j]),None)
        if k is None:
            continue
        A[r],A[k]=A[k],A[r]
        p=A[r][j]
        if p==2:
            A[r]=[(2*x)%3 for x in A[r]]
        for k in range(r+1,len(A)):
            p=A[k][j]
            if p:
                A[k][j:]=[(a-p*b)%3 for a,b in zip(A[k][j:],A[r][j:])]
        r+=1
    return r


def matrix(n):
    P=partials(n)
    N=len(P)
    U=set(pool(n))
    A=[models(units(a),n) for a in P]
    B=[]
    for i,b in enumerate(P):
        C=gadget(b)
        require(all(len(c)==2 and c in U for c in C),'nonunit gadget outside pool')
        m=models(C,n)
        require(m==A[i],'literal forcing failed')
        B.append(m)
    rows=[]
    # Rectangle cover, indexed by assignments.
    rect=[sum(1<<j for j,v in enumerate(B) if v>>w&1) for w in range(1<<n)]
    for i,a in enumerate(P):
        v=sum(1<<j for j,b in enumerate(B) if A[i]&b)
        expected=sum(1<<j for j,b in enumerate(P) if compatible(a,b))
        require(v==expected,'compatibility mismatch')
        cover=0
        for w in range(1<<n):
            if A[i]>>w&1:
                cover|=rect[w]
        require(cover==v,'witness rectangle cover mismatch')
        rows.append(v)
    full=[i for i,a in enumerate(P) if all(a)]
    require(len(full)==1<<n,'bad complete assignment indices')
    for i in full:
        require(all(bool(rows[i]>>j&1)==(i==j) for j in full),'identity restriction failed')
    r=rank2(rows,N)
    require(r==N and rank3(rows,N)==N,'rank mismatch')
    require(len(set(rows))==N and all(rows),'semantic row count mismatch')
    return [n,N,N*N,N*N*(1<<n),sum(v.bit_count() for v in rows),r,len(set(rows)),len(full)]


def controls():
    for n in (2,3):
        P=partials(n)
        B=[models(gadget(b),n) for b in P]
        U=tuple(c for c in pool(n) if len(c)==1)
        rows=set()
        for p in range(1<<len(U)):
            A=models(tuple(c for i,c in enumerate(U) if p>>i&1),n)
            rows.add(sum(1<<j for j,b in enumerate(B) if A&b))
        require(len(rows)==3**n+1 and 0 in rows,'raw unit row count failed')
    # All signed binary clauses distinguish complete assignments.
    for n in (2,3,4):
        C=tuple(c for c in pool(n) if len(c)==2)
        R={tuple(bool(models((c,),n)>>w&1) for c in C) for w in range(1<<n)}
        require(len(R)==1<<n,'binary residual collision')
    try:
        gadget((1,))
    except ValueError:
        pass
    else:
        raise ValueError('one-variable gadget accepted')
    require(rank2((0,1,1),2)==1 and rank3((0,1,1),2)==1,'singular control failed')
    return 4


def audit():
    result={'matrix':[matrix(n) for n in (2,3,4,5)],'controls':controls()}
    print('F038_MRAX_SELECTOR_RANK_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
