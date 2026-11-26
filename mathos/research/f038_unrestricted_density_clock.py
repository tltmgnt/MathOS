"""Density-sensitive exact-stage witness search, finite semantic regression."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import valid
from mathos.research.f038_unrestricted_bijunctive_core import solve2

PLAN='docs/research/tga-universal/f038-unrestricted-density-clock.json'


def cap(n,k):
    require(type(n) is int and n>=1 and type(k) is int and k>=3,'dimensions')
    m,a,b=0,1,n**(k-2)
    while a*8**10<=b*7**10:
        m+=1
        a*=8**10
        b*=7**10
    return m


def truth(c,w):
    return any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c)


def matching(F):
    A=set()
    H=[]
    for c in F:
        if len(c)==3 and all(abs(l) not in A for l in c):
            H.append(c)
            A.update(map(abs,c))
    require(len(A)==3*len(H) and all(len(c)<3 or any(abs(l) in A for l in c)
                                      for c in F),'maximal matching')
    return H


def solve(n,F,H,b):
    """Prototype computes full matching for evidence; fixed tape program aborts early."""
    if len(H)>b:
        return None,0
    P=[]
    for c in H:
        P.append([tuple((abs(l),bool(x>>j&1)) for j,l in enumerate(c))
                  for x in range(8)
                  if any(bool(x>>j&1)==(l>0) for j,l in enumerate(c))])
        require(len(P[-1])==7,'local branch count')
    attempts=0
    for blocks in product(*P):
        attempts+=1
        A=dict(pair for block in blocks for pair in block)
        G=[(v if value else -v,) for v,value in A.items()]
        for c in F:
            if any(abs(l) in A and A[abs(l)]==(l>0) for l in c):
                continue
            r=tuple(l for l in c if abs(l) not in A)
            if not r:
                break
            require(len(r)<=2,'unhit triple')
            G.append(r)
        else:
            w=solve2(n,G)
            if w is not None:
                require(all(truth(c,w) for c in F),'invalid witness')
                return w,attempts
    return None,attempts


def fixtures(n,C):
    if n<=2:
        return list(range(1<<len(C)))
    P=[m<<(len(C)-8) for m in range(256)] if n==3 else []
    if n<=6:
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
          ((1,2,3),(4,5,6),(1,7,8)),
          ((1,2,3),(-1,-2,-3)),((1,2,3),(-1,),(-2,),(-3,)))
    return [sum(1<<i for i,c in enumerate(C) if c in S) for S in sets]


def rows():
    out=[]
    for n in (1,2,3,4,5,6,9):
        C=pool(n)
        P=fixtures(n,C)
        for k in (3,4,5):
            b=cap(n,k)
            st=[n,k,b,len(P),0,0,0,0,0,0,0,0,0,0]
            for p in P:
                F=[c for j,c in enumerate(C) if p>>j&1]
                W=[w for w in range(1<<n) if all(truth(c,w) for c in F)]
                H=matching(F)
                m=len(H)
                dense=len(W)**10*n**(k-2)>=1<<(10*n)
                require(len(W)*8**m<=(1<<n)*7**m,'density packing bound')
                require(not dense or m<=b,'density cap miss')
                st[4]+=m
                st[5]+=bool(W)
                st[6]+=len(W)
                st[7]+=dense
                w,t=solve(n,F,H,b)
                if m>b:
                    require(w is None and t==0,'cap behavior')
                    st[8]+=1
                    continue
                require((w is not None)==bool(W) and
                        (w is None or valid(C,n,p,w)) and 1<=t<=7**m,
                        'bounded search mismatch')
                st[9]+=1
                st[10]+=w is not None
                st[11]+=t
                st[12]+=7**m
                st[13]+=w is None
            out.append(st)
    return out


def controls():
    require(7**63<8**59,'clock slack constant')
    for n in (1,3,4,14,15,16,100,1000,1000000):
        for k in (3,4,5,10):
            b=cap(n,k)
            require(8**(10*b)<=n**(k-2)*7**(10*b) and
                    8**(10*(b+1))>n**(k-2)*7**(10*(b+1)),
                    'integer cap boundary')
    F=[(1,2,3),(1,4,5),(-1,-2,-3)]
    H=matching(F)
    require(len(H)==1 and solve(5,F,H,1)[0] is not None,'overlapping supports')
    F=[(1,2,3),(-1,),(-2,),(-3,)]
    require(solve(3,F,matching(F),1)==(None,7),'all branches exhausted')
    return 4


def audit():
    caps=[[n,*(cap(n,k) for k in (3,4,5,10))]
          for n in (1,3,4,14,15,16,100,1000,1000000)]
    result={'caps':caps,'controls':controls(),'rows':rows()}
    print('F038_UNRESTRICTED_DENSITY_CLOCK_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
