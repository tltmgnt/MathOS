"""Finite context-rectangle reference, not a compiled original machine."""
import json
from fractions import Fraction
from itertools import combinations, product

R=9
H=tuple(h for k in (1,2,3) for h in combinations(range(R),k))


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)


def contexts(u,v,m):
    return [None]+[(g,c) for g in range(R) if g not in (u,v) for c in range(m)]


def row_masks(m,u,v,bad):
    out=[]
    for ctx in contexts(u,v,m):
        h=tuple(sorted((u,v) if ctx is None else (u,v,ctx[0])))
        forbidden=bad.get(h,set())
        rows=[]
        for a in range(m):
            mask=0
            for b in range(m):
                vals={u:a,v:b}
                if ctx is not None: vals[ctx[0]]=ctx[1]
                if tuple(vals[g] for g in h) not in forbidden: mask|=1<<b
            rows.append(mask)
        out.append(rows)
    return out


def colors(rows,m):
    adj=[set() for _ in range(m)]
    for a,b in combinations(range(m),2):
        if any(M[a] and M[b] and M[a]!=M[b] for M in rows):
            adj[a].add(b); adj[b].add(a)
    label=[]
    for a in range(m):
        used={label[b] for b in adj[a] if b<a}
        label.append(next(k for k in range(m) if k not in used))
    K=max(label)+1
    need(K<=max(map(len,adj))+1,'greedy degree bound')
    return [tuple(a for a in range(m) if label[a]==k) for k in range(K)]


def branches(m,u,v,bad):
    rows=row_masks(m,u,v,bad)
    classes=colors(rows,m)
    out=[]
    for A in classes:
        Q={h:set(z) for h,z in bad.items() if not (u in h and v in h)}
        def add(g,a,ctx):
            vals={g:a}
            if ctx is not None: vals[ctx[0]]=ctx[1]
            h=tuple(sorted(vals))
            Q.setdefault(h,set()).add(tuple(vals[i] for i in h))
        for a in range(m):
            if a not in A: add(u,a,None)
        for ctx,M in zip(contexts(u,v,m),rows):
            common=next((M[a] for a in A if M[a]),0)
            for a in A:
                need(M[a] in (0,common),'rectangle class')
                if not M[a]: add(u,a,ctx)
            for b in range(m):
                if not (common>>b&1): add(v,b,ctx)
            for a,b in product(A,range(m)):
                need(bool(M[a]>>b&1)==(bool(M[a]) and bool(common>>b&1)),'slice factorization')
        need(all(not (u in h and v in h) for h in Q),'edge removed')
        out.append((A,Q))
    return out


def predicate(bad):
    return lambda z: not any(tuple(z[g] for g in h) in B for h,B in bad.items())


def fixture(m,mode,u,v):
    bad={}
    pair=tuple(sorted((u,v)))
    cyclic={tuple(sorted(4+(i+j)%5 for j in range(3))) for i in range(5)}
    for h in H:
        for z in product(range(m),repeat=len(h)):
            a=dict(zip(h,z))
            hit=False
            if mode==1: hit=h==(u,)
            elif mode==2: hit=len(h)==2 and z==(1,1)
            elif mode==3: hit=len(h)==3 and (sum(h)+sum((i+2)*x for i,x in enumerate(z)))%5==0
            elif mode==4: hit=len(h)==3 and any(z)
            elif mode==5:
                hit=len(h)==3 and u in h and v in h and a[u]!=a[next(g for g in h if g not in (u,v))]
            elif mode==6:
                hit=len(h)==2 and z==(1,1)
                if len(h)==3 and (max(h)<4 or h in cyclic):
                    nz=[x for x in z if x]
                    hit=len(nz)%2==1 or len(nz)==2 and nz[0]==nz[1]
            elif mode==7:
                hit=(h==pair and a[u]==a[v]) or (len(h)==3 and u in h and v in h and sum(z)%m==0)
            if hit: bad.setdefault(h,set()).add(z)
    return bad


def audit():
    rows=[]
    for m,modes in ((2,range(8)),(3,range(8)),(4,(5,6,7))):
        for mode in modes:
            u,v=(0,8) if mode%2==0 else (8,0)
            bad=fixture(m,mode,u,v)
            bs=branches(m,u,v,bad)
            if mode in (2,6): need(len(bs)==2,'two-color dense control')
            if mode==5: need(len(bs)==1,'empty rows merge')
            if mode==7: need(len(bs)==m,'all rows conflict')
            orig=predicate(bad)
            ps=[(set(A),predicate(Q)) for A,Q in bs]
            count=checks=0
            for z in product(range(m),repeat=R):
                expected=orig(z)
                actual=sum(p(z) for _,p in ps)
                need(actual==int(expected),'disjoint exact branch union')
                count+=expected; checks+=len(ps)
            if mode==6 and m>=3: need(count==1,'dense unique')
            rows.append([m,mode,len(bs),sum(map(len,bad.values())),count,checks])
    # Exhaust every binary matrix at m=2,3, including empty and full rows.
    matrices=0
    for m in (2,3):
        for code in range(1<<(m*m)):
            M=[(code>>(a*m))&((1<<m)-1) for a in range(m)]
            C=colors([M],m)
            need(len(C)==max(1,len(set(M)-{0})),'single-context optimal colors')
            matrices+=1
    # Two contexts with independently varying row masks.
    multi=0
    for x,y in product(range(16),repeat=2):
        Ms=[[(code>>(a*2))&3 for a in range(2)] for code in (x,y)]
        C=colors(Ms,2)
        need(len(C)==(2 if any(M[0] and M[1] and M[0]!=M[1] for M in Ms) else 1),'two-context conflicts')
        multi+=1
    e=Fraction(62,7)
    need(e+Fraction(1,7)==9,'clock slack')
    result={'fixtures':len(rows),'sums':[sum(row[i] for row in rows) for i in range(2,6)],'matrices':matrices,'two_contexts':multi,'exponent':str(e)}
    print('F038_UNRESTRICTED_CONTEXT_RECTANGLES_OK '+json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit()
