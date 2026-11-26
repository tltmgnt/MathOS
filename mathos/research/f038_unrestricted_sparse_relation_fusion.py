"""Exact sparse-relation fusion reference, not a physical tape simulator."""
import json
from fractions import Fraction
from itertools import combinations, product

G=tuple(range(9))
H=tuple(h for k in (1,2,3) for h in combinations(G,k))
T=set(combinations(range(4),3))|{tuple(sorted(4+(i+j)%5 for j in range(3))) for i in range(5)}


def need(ok,msg):
    if not ok: raise AssertionError(msg)


def predicate(groups,records):
    by={}
    for h,z in records: by.setdefault(tuple(groups.index(g) for g in h),set()).add(z)
    return lambda z: not any(tuple(z[i] for i in ix) in vals for ix,vals in by.items())


def allowed(m,P,bad):
    p=predicate(P,[(h,z) for h,z in bad if set(h)<=set(P)])
    return [z for z in product(range(m),repeat=len(P)) if p(z)]


def control(m,mode):
    out=set()
    for h in H:
        for z in product(range(m),repeat=len(h)):
            hit=False
            if mode==1: hit=h==(0,)
            elif mode==2: hit=h==(0,8) and z[0]!=z[1]
            elif mode==3: hit=h==(0,3,8) and (z[0]+z[1])%m!=z[2]
            elif mode==4: hit=(sum(h)+sum((i+2)*v for i,v in enumerate(z)))%7==0
            elif mode==5:
                if h in T:
                    nz=[v for v in z if v]
                    hit=len(nz)%2==1 or len(nz)==2 and nz[0]==nz[1]
                elif len(h)==2 and not any(set(h)<=set(t) for t in T):
                    a,b=z
                    hit=a!=0 and b!=0 and (b-a)%(m-1)<(m-1)//2
            elif mode==6: hit=len(h)==3 and h==(0,3,8) and z!=(0,)*3
            if hit: out.add((h,z))
    return out


def fuse_tile(m,b,P,chunk,others,offset,bad):
    # Local group 0 is the fused coordinate; groups 1..r-1 are others.
    r=1+len(others); local=set(); generated=0
    for h,z in bad:
        fixed=dict(zip(h,z)); plain=tuple(g for g in h if g not in P)
        vals=tuple(fixed[g]-offset[others.index(g)] for g in plain)
        if not all(0<=v<b for v in vals): continue
        ids=tuple(1+others.index(g) for g in plain)
        inside=tuple(g for g in h if g in P)
        if not inside:
            local.add((ids,vals)); generated+=1
        else:
            for j,p in enumerate(chunk):
                if all(p[P.index(g)]==fixed[g] for g in inside):
                    local.add(((0,)+ids,(j,)+vals)); generated+=1
    pad={((0,),(j,)) for j in range(len(chunk),b)}
    for i,o in enumerate(offset,1):
        pad.update(((i,),(j,)) for j in range(b) if o+j>=m)
    local|=pad
    need(all(1<=len(h)<=3 and len(h)==len(set(h)) and len(h)==len(z) and all(0<=a<b for a in z) for h,z in local),'local clause layout')
    need(len(local)<=sum(len(list(combinations(range(r),k)))*b**k for k in (1,2,3)),'local capacity')
    return local,generated,len(pad)


def fixture(m,mode,P,b,repo=False):
    bad=control(m,mode); original=predicate(G,bad)
    pairs=allowed(m,P,bad); others=tuple(g for g in G if g not in P)
    r=1+len(others); actual=set(); stats=[0]*6
    expected={z for z in product(range(m),repeat=9) if original(z)}
    covered=set(); first=None
    for start in range(0,len(pairs),b):
        chunk=pairs[start:start+b]
        for block in product(range((m+b-1)//b),repeat=len(others)):
            offset=tuple(b*j for j in block)
            local,gen,pad=fuse_tile(m,b,P,chunk,others,offset,bad)
            p=predicate(tuple(range(r)),local)
            stats[0]+=1; stats[1]+=gen; stats[2]+=pad
            for z in product(range(b),repeat=r):
                stats[3]+=1
                good=z[0]<len(chunk) and all(o+a<m for o,a in zip(offset,z[1:]))
                if not good:
                    need(not p(z),'padding exclusion'); continue
                d=dict(zip(P,chunk[z[0]])); d.update(zip(others,(o+a for o,a in zip(offset,z[1:]))))
                outer=tuple(d[g] for g in G)
                need(outer not in covered,'disjoint tiles'); covered.add(outer)
                stats[4]+=1
                ok=p(z); need(ok==(outer in expected),'local equivalence')
                if ok:
                    actual.add(outer); stats[5]+=1
                    if first is None: first=(outer,z,local)
    need(len(covered)==len(pairs)*m**len(others) and actual==expected,'exact model set')
    if mode==5:
        need(expected=={(0,)*9},'unique parity control')
        for u,v in combinations(G,2):
            t=next((t for t in T if u in t and v in t),None)
            h=t or (u,v)
            rows=[frozenset(y for y in range(m) if (h,tuple(x if g==u else y if g==v else 0 for g in h)) not in bad) for x in range(m)]
            need(all(rows) and len(set(rows))==m,'maximal conflicts')
            need(max(m-len(row) for row in rows)>=(m-1)//2,'large forbidden degree both directions')
    if repo and first is not None:
        from mathos.research.f038_unrestricted_distributed_hyperclique import fixed,witness
        from mathos.research.f038_unrestricted_universal_search import valid,encoded
        from mathos.research.f038_universal_witness_layout import pool
        def verify(R,M,records,z,pins):
            n=(2*R+1)*M-R+2; C=pool(n); pos={c:i for i,c in enumerate(C)}
            clauses={tuple(-(g*M+a+1) for g,a in zip(h,v)) for h,v in records}
            F=set(fixed(R,M,n,pins)); need(not F&clauses,'fixed clauses disjoint')
            p=sum(1<<pos[c] for c in F|clauses)
            need(len(encoded(n,p,C))==n+1+len(C),'normalized length')
            need(valid(C,n,p,witness(R,M,n,pins,z)),'actual verifier')
        outer,z,local=first
        verify(9,m,bad,outer,tuple(i%2 for i in range(m)))
        verify(r,b,local,z,(0,)*b)
    return [m,mode,len(P),b,len(pairs),len(bad),len(expected),*stats]


def audit(repo=False):
    rows=[]
    for m in (2,3):
        for mode,P in ((0,(0,8)),(1,(0,3,8)),(2,(0,8)),(3,(0,3,8)),(4,(2,5)),(4,(1,4,7)),(6,(0,3,8))):
            rows.append(fixture(m,mode,P,2,repo))
    for m in (3,4): rows.append(fixture(m,5,(0,1,2),2,repo))
    for k in (2,3):
        r=10-k
        for delta in (Fraction(2),Fraction(1,4),Fraction(1,20)):
            beta=3/(r+delta-3)
            need(3-beta*(r-3)==beta*delta,'tile balance')
            need(0<beta<=1,'block range')
    result={'fixtures':len(rows),'sums':[sum(row[i] for row in rows) for i in range(4,len(rows[0]))]}
    print('F038_UNRESTRICTED_SPARSE_RELATION_FUSION_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    import sys
    audit('--repo' in sys.argv)
