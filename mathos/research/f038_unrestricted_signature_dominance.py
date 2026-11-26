"""Finite reference: explicit-context dominance and eight-group branch transfer."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_unrestricted_universal_search import encoded, valid
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import (
    group, digit, cross, fixed, witness, fixture)
from mathos.research.f038_unrestricted_recursive_tiling import digit_masks, forbidden


def pick(c,j,mode,m,planted):
    if mode<7:
        return fixture(c,j,mode,m,planted)
    if mode==7:
        return True
    g=tuple(group(-x,m) for x in c)
    d=tuple(digit(-x,m) for x in c)
    if mode==8:
        return len(c)==1 and g[0]!=0 and d[0]!=planted[g[0]]
    if mode==9:
        return len(c)==3 and any(d)
    if mode==10:
        return len(c)==2 and g==(0,1) and d[0]>d[1]
    return len(c)==2 and g==(0,1) and d[0]>0 and d[1]==0


def signatures(r,m,A,raw,loc,n):
    records=[]
    for c in A:
        for x in c:
            rest=tuple(-v for v in c if v!=x)
            records.append((group(-x,m),digit(-x,m),len(rest),rest,
                            int(raw[n+1+loc[c]])))
    records.sort()
    S=[[[] for _ in range(m)] for _ in range(r)]
    keys=[[[] for _ in range(m)] for _ in range(r)]
    for g,a,k,rest,bit in records:
        S[g][a].append(bit)
        keys[g][a].append((k,rest))
    h=1+(r-1)*m+(r-1)*(r-2)//2*m*m
    for g,a in product(range(r),range(m)):
        require(len(S[g][a])==h and keys[g][a]==keys[g][0],
                'complete aligned contexts')
    return S,len(records)


def frontiers(S,m):
    R,U,rel=[],[],[]
    comparisons=0
    for G in S:
        live=[a for a in range(m) if not G[a][0]]
        le=[[all(x<=y for x,y in zip(G[a],G[b]))
             for b in range(m)] for a in range(m)]
        R.append([b for b in live if not any(a!=b and le[a][b] and
                    (not le[b][a] or a<b) for a in live)])
        U.append([b for b in live if not any(a!=b and le[a][b] for a in live)])
        rel.append(le)
        comparisons+=len(live)*(len(live)-1)
    return R,U,rel,comparisons


def project(B,g,a,m):
    Q=set()
    for c in B:
        pivot=next((x for x in c if group(-x,m)==g),None)
        if pivot is not None and digit(-pivot,m)!=a:
            continue
        d=tuple(-((group(-x,m)-(group(-x,m)>g))*m+digit(-x,m)+1)
                for x in c if group(-x,m)!=g)
        require(bool(d),'live pivot cannot yield empty clause')
        Q.add(d)
    return Q


def layout(m):
    r=9
    n=19*m-7
    n8=17*m-6
    C,C8=pool(n),pool(n8)
    loc={c:i for i,c in enumerate(C)}
    loc8={c:i for i,c in enumerate(C8)}
    A=tuple(c for c in C if cross(c,r,m))
    A8=tuple(c for c in C8 if cross(c,8,m))
    Z=tuple(product(range(m),repeat=r))
    Z8=tuple(product(range(m),repeat=8))
    full=(1<<len(Z))-1
    full8=(1<<len(Z8))-1
    masks=digit_masks(r,m,Z)
    masks8=digit_masks(8,m,Z8)
    bad={c:forbidden(c,m,masks,full) for c in A}
    bad8={c:forbidden(c,m,masks8,full8) for c in A8}
    F8=fixed(8,m,n8,(0,)*m)
    row=[m]+[0]*13
    for mode in range(12):
        planted=tuple((i+mode)%m for i in range(r))
        pins=tuple((i+mode)%2 for i in range(m))
        F=fixed(r,m,n,pins)
        B=tuple(c for j,c in enumerate(A) if pick(c,j,mode,m,planted))
        require(len(set(F+B))==len(F)+len(B),'fixed/cross overlap')
        p=sum(1<<loc[c] for c in F+B)
        raw=encoded(n,p,C)
        require(raw[:n+1]=='1'*n+'0' and len(raw)==n+1+len(C),'outer input')
        selected=tuple(c for c in A if raw[n+1+loc[c]]=='1')
        require(selected==B,'selector extraction')
        S,count=signatures(r,m,A,raw,loc,n)
        row[2]+=count
        R,U,rel,comparisons=frontiers(S,m)
        row[3]+=comparisons
        blocked=0
        for c in selected:
            blocked|=bad[c]
        modelbits=full^blocked
        models=[z for i,z in enumerate(Z) if modelbits>>i&1]
        modelset=set(models)
        for z in models:
            for g in range(r):
                for a in range(m):
                    if rel[g][a][z[g]]:
                        q=z[:g]+(a,)+z[g+1:]
                        require(q in modelset,'weak dominance substitution')
                        row[4]+=1
        reduced=[z for z in models if all(a in R[g] for g,a in enumerate(z))]
        unique_core=[z for z in models if all(a in U[g] for g,a in enumerate(z))]
        require(bool(reduced)==bool(models),'general core preserves SAT')
        if len(models)==1:
            require(unique_core==models,'unique core preserves witness')
        row[5]+=len(models)
        row[6]+=len(reduced)
        row[7]+=len(unique_core)
        row[8]+=len(models)==1
        for lists in (R,U):
            g=min(range(r),key=lambda i:len(lists[i]))
            for a in lists[g]:
                Q=project(selected,g,a,m)
                require(Q.isdisjoint(F8) and Q<=set(A8),'local pool slots')
                p8=sum(1<<loc8[c] for c in F8)+sum(1<<loc8[c] for c in Q)
                raw8=encoded(n8,p8,C8)
                require(len(raw8)==n8+1+len(C8) and raw8[:n8+1]=='1'*n8+'0',
                        'local normalized header')
                P={c for c in A8 if raw8[n8+1+loc8[c]]=='1'}
                require(P==Q,'local selector extraction')
                block8=0
                for c in P:
                    block8|=bad8[c]
                models8=full8^block8
                first=None
                for i,z in enumerate(Z8):
                    outer=z[:g]+(a,)+z[g:]
                    ok=bool(models8>>i&1)
                    require(ok==(outer in modelset),'branch model equivalence')
                    if ok and first is None:
                        first=z
                    row[10]+=1
                if first is not None:
                    outer=first[:g]+(a,)+first[g:]
                    require(valid(C8,n8,p8,witness(8,m,n8,(0,)*m,first)),
                            'original local verifier')
                    require(valid(C,n,p,witness(r,m,n,pins,outer)),
                            'original outer verifier')
                    row[12]+=1
                row[9]+=1
                row[11]+=models8.bit_count()
        row[1]+=1
        row[13]+=any(len(v)<m for v in R)
    return row


def audit():
    rows=[layout(m) for m in (2,3)]
    require(rows==[[2,12,27864,158,22081,1287,9,5,3,20,5120,779,14,10],
                   [3,12,89748,474,1237929,48123,10,6,3,26,170586,19696,16,10]],
            'independent JS totals')
    print('F038_UNRESTRICTED_SIGNATURE_DOMINANCE_OK '+
          json.dumps(rows,separators=(',',':')))
    return rows


if __name__=='__main__':
    audit()
