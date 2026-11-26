"""Finite contextual support/dominance regression; not a compiled U machine."""
import json
from itertools import combinations, product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_unrestricted_universal_search import encoded, valid
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import (
    group, digit, cross, fixed, witness)
from mathos.research.f038_unrestricted_signature_dominance import (
    pick as parent_pick, signatures, frontiers)

R=9
H=tuple(h for k in (1,2,3) for h in combinations(range(R),k))
XOR_H=tuple(tuple(sorted((i,(i+1)%R,(i+3)%R))) for i in range(R))


def pick(c,j,mode,m,planted):
    if mode<12:
        return parent_pick(c,j,mode,m,planted)
    g=tuple(group(-x,m) for x in c)
    d=tuple(digit(-x,m) for x in c)
    if mode==12:
        return ((len(c)==2 and g[1]==g[0]+1 and any(d)) or
                (len(c)==3 and g[0]%3==0 and g[1]==g[0]+1 and
                 g[2]==g[0]+2 and d[1]==(d[0]+1)%m and d[2]==d[0]))
    if mode==13:
        return ((len(c)==1 and g[0]==0 and d[0]!=0) or
                (len(c)==2 and g[1]==g[0]+1 and d[0]!=d[1]))
    return len(c)==3 and g in XOR_H and (d[0]^d[1]^d[2])!=0


def local_tables(m,bad):
    tables=[]
    for h in H:
        sub=[(k,tuple(h.index(g) for g in k)) for k in H if set(k)<=set(h)]
        entries=[]
        for z in product(range(m),repeat=len(h)):
            ok=not any(tuple(z[i] for i in inds) in bad.get(k,())
                       for k,inds in sub)
            entries.append((z,ok))
        tables.append((h,entries))
    require(sum(len(v) for _,v in tables)==9*m+36*m*m+84*m**3,
            'complete local tables')
    return tables


def in_domains(z,D):
    return all(D[g]>>a&1 for g,a in enumerate(z))


def prune(m,tables,models,unique):
    D=[(1<<m)-1]*R
    rounds=sdel=ddel=0
    def count(dom):
        return sum(x.bit_count() for x in dom)
    while True:
        rounds+=1
        old=D[:]
        before=[z for z in models if in_domains(z,D)]
        support=D[:]
        for h,entries in tables:
            seen=[0]*len(h)
            for z,ok in entries:
                if ok and all(D[g]>>a&1 for g,a in zip(h,z)):
                    for i,a in enumerate(z):
                        seen[i]|=1<<a
            for g,bits in zip(h,seen):
                support[g]&=bits
        sdel+=count(D)-count(support)
        require(all(in_domains(z,support) for z in before),'support preserves every model')
        D=support
        new=D[:]
        if all(D):
            for g in range(R):
                live=[a for a in range(m) if D[g]>>a&1]
                sig=[]
                contexts=[]
                for a in live:
                    v=[]
                    keys=[]
                    for h,entries in tables:
                        if g not in h:
                            continue
                        i=h.index(g)
                        for z,ok in entries:
                            if z[i]==a and all(k==g or D[k]>>b&1
                                               for k,b in zip(h,z)):
                                v.append(not ok)
                                keys.append((h,z[:i]+z[i+1:]))
                    sig.append(v)
                    contexts.append(keys)
                require(all(c==contexts[0] for c in contexts),'aligned restricted contexts')
                le=[[all(x<=y for x,y in zip(a,b)) for b in sig] for a in sig]
                for i,a in enumerate(live):
                    if any(i!=j and le[j][i] and (unique or not le[i][j] or b<a)
                           for j,b in enumerate(live)):
                        new[g]&=~(1<<a)
        ddel+=count(D)-count(new)
        D=new
        after=[z for z in models if in_domains(z,D)]
        if not unique:
            require(bool(before)==bool(after),'general preservation')
        elif len(models)==1:
            require(after==models,'unique preservation')
        require(rounds<=R*m+1,'round bound')
        if not all(D) or D==old:
            return [rounds,sdel,ddel,min(x.bit_count() for x in D),len(after)],D


def layout(m,modes):
    n=19*m-7
    C=pool(n)
    L=n+1+len(C)
    require(L==n+1+2*n*n+8*comb(n,3),'original length')
    pos={c:i for i,c in enumerate(C)}
    A=tuple(c for c in C if cross(c,R,m))
    rows=[]
    for mode in modes:
        pins=tuple((i+mode)%2 for i in range(m))
        planted=tuple((i+mode)%m for i in range(R))
        F=fixed(R,m,n,pins)
        B=tuple(c for j,c in enumerate(A) if pick(c,j,mode,m,planted))
        require(len(set(F+B))==len(F)+len(B),'fixed/cross overlap')
        p=sum(1<<pos[c] for c in F+B)
        raw=encoded(n,p,C)
        require(raw[:n+1]=='1'*n+'0' and len(raw)==L,'normalized input')
        selected=tuple(c for c in A if raw[n+1+pos[c]]=='1')
        require(selected==B,'actual selector extraction')
        S,_=signatures(R,m,A,raw,pos,n)
        oldR,oldU,_,_=frontiers(S,m)
        bad={}
        for c in selected:
            g=tuple(group(-x,m) for x in c)
            d=tuple(digit(-x,m) for x in c)
            bad.setdefault(g,set()).add(d)
        models=[z for z in product(range(m),repeat=R)
                if not any(tuple(z[g] for g in h) in v for h,v in bad.items())]
        tables=local_tables(m,bad)
        general,G=prune(m,tables,models,False)
        special,U=prune(m,tables,models,True)
        if mode in (12,14):
            require(len(models)==1 and all(len(v)==m for v in oldR+oldU),
                    'raw full antichain unique control')
        if mode==12:
            require(all(v==1 for v in G+U),'strict separation width one')
        if mode==14:
            require(all(v==(1<<m)-1 for v in G+U),'full-width XOR fixed point')
        # Check actual original and restricted witness when a model survives.
        for D in (G,U):
            z=next((z for z in models if in_domains(z,D)),None)
            if z is not None:
                w=witness(R,m,n,pins,z)
                restricted=p
                for g in range(R):
                    for a in range(m):
                        if not D[g]>>a&1:
                            restricted|=1<<pos[(-(g*m+a+1),)]
                require(valid(C,n,p,w) and valid(C,n,restricted,w),'original verifier')
        rows.append([mode,len(models),min(map(len,oldR))]+general+special)
    return [m,L,rows]


def matrix_rank():
    rows=[sum(1<<g for g in h) for h in XOR_H]
    rank=0
    for g in range(R):
        p=next((i for i in range(rank,R) if rows[i]>>g&1),None)
        if p is None:
            continue
        rows[p],rows[rank]=rows[rank],rows[p]
        for i in range(R):
            if i!=rank and rows[i]>>g&1:
                rows[i]^=rows[rank]
        rank+=1
    require(rank==R and rows==[1<<g for g in range(R)],'invertible cyclic XOR')
    return rank


EXPECTED=[
[2,37914,[[0,512,1,2,0,9,1,1,1,0,18,0,0],[1,0,0,1,18,0,0,0,1,18,0,0,0],[2,1,1,2,9,0,1,1,2,9,0,1,1],[3,2,2,1,0,0,2,2,1,0,0,2,2],[4,0,1,1,12,0,0,0,1,12,0,0,0],[5,0,2,1,4,0,0,0,1,4,0,0,0],[6,1,1,2,9,0,1,1,2,9,0,1,1],[7,0,0,1,18,0,0,0,1,18,0,0,0],[8,2,1,2,8,1,1,1,1,8,2,0,0],[9,1,1,2,9,0,1,1,2,9,0,1,1],[10,384,1,2,0,9,1,1,1,0,16,0,0],[11,384,1,2,0,9,1,1,1,0,16,0,0],[12,1,2,2,9,0,1,1,2,9,0,1,1],[13,1,1,5,9,0,1,1,5,9,0,1,1],[14,1,2,1,0,0,2,1,1,0,0,2,1]]],
[3,161851,[[0,19683,1,2,0,18,1,1,1,0,27,0,0],[1,0,0,1,27,0,0,0,1,27,0,0,0],[2,1,1,2,18,0,1,1,2,18,0,1,1],[3,3,3,1,0,0,3,3,1,0,0,3,3],[4,0,2,3,22,0,0,0,3,22,0,0,0],[5,0,3,1,0,0,3,0,1,0,0,3,0],[6,1,1,2,18,0,1,1,2,18,0,1,1],[7,0,0,1,27,0,0,0,1,27,0,0,0],[8,3,1,2,16,2,1,1,1,16,3,0,0],[9,1,1,2,18,0,1,1,2,18,0,1,1],[10,13122,1,2,0,18,1,1,1,0,25,0,0],[11,15309,1,2,0,18,1,1,1,0,26,0,0],[12,1,3,2,18,0,1,1,2,18,0,1,1],[13,1,1,5,18,0,1,1,5,18,0,1,1]]],
[4,428744,[[14,1,4,1,0,0,4,1,1,0,0,4,1]]]]


def audit():
    data=[layout(2,range(15)),layout(3,range(14)),layout(4,(14,))]
    require(data==EXPECTED,'independent JS reference totals')
    allrows=[row for _,_,rows in data for row in rows]
    counts=[len(allrows),sum(len(rows)*m**9 for m,_,rows in data),
            sum(row[1] for row in allrows),sum(row[1]>0 for row in allrows),
            sum(row[1]==1 for row in allrows)]
    counts.extend(sum(row[i] for row in allrows) for i in (3,4,5,8,9,10))
    require(counts==[30,545386,49416,22,12,56,287,84,48,287,133],
            'aggregate checks')
    result={'counts':counts,'rank':matrix_rank()}
    print('F038_UNRESTRICTED_CONTEXT_FIXEDPOINT_OK '+
          json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit()
