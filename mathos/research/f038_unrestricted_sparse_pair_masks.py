"""Sparse-pair mask reference; no physical tape timing claims."""
import json
from fractions import Fraction
from itertools import combinations, product

G = tuple(range(9))
H = tuple(h for k in (1, 2, 3) for h in combinations(G, k))
PARITY = set(combinations(range(4), 3)) | {
    tuple(sorted(4+(i+j)%5 for j in range(3))) for i in range(5)}


def check(ok, msg):
    if not ok:
        raise AssertionError(msg)


def rem(a, b):
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length()-b.bit_length())
    return a


def field(k):
    q = 1 << k
    return next(p for p in range(q+1, 2*q, 2)
                if all(rem(p, d) for j in range(1,k//2+1)
                       for d in range(1<<j,1<<(j+1))))


def mul(a,b,p,q):
    c=0
    while b:
        if b&1: c^=a
        b>>=1
        a<<=1
        if a&q: a^=p
    return c


def masks(m,D):
    if D==0: return [frozenset(range(m))]
    q=1 << (D*(m-1).bit_length()).bit_length()
    p=field(q.bit_length()-1)
    out=[]
    for x in range(q):
        buckets=[set() for _ in range(q)]
        for a in range(m):
            digits=[]; z=a
            while z:
                digits.append(z%q); z//=q
            y=0
            for d in reversed(digits): y=mul(y,x,p,q)^d
            buckets[y].add(a)
        out.extend(frozenset(B) for B in buckets if B)
    return list(dict.fromkeys(out))


def bound(m,u,v,bad):
    rows={}
    for h,z in bad:
        if u not in h or v not in h: continue
        a=z[h.index(u)]
        ctx=next(((g,z[i]) for i,g in enumerate(h) if g not in (u,v)),None)
        rows.setdefault((a,ctx),set()).add(z[h.index(v)])
    return min(m,max(len(rows.get((a,None),()))+sum(
        max(len(rows.get((a,(g,c)),())) for c in range(m))
        for g in G if g not in (u,v)) for a in range(m)))


def factor(m,u,v,bad,Bs):
    common={(h,z) for h,z in bad if not (u in h and v in h)}
    tagged=set()
    for k,B in enumerate(Bs):
        tagged.update((k,(v,),(b,)) for b in range(m) if b not in B)
        for h,z in bad-common:
            if z[h.index(v)] in B:
                i=h.index(v)
                tagged.add((k,h[:i]+h[i+1:],z[:i]+z[i+1:]))
    return common,tagged


def predicate(bad):
    rows={}
    for h,z in bad: rows.setdefault(h,set()).add(z)
    return lambda z: not any(tuple(z[g] for g in h) in Z for h,Z in rows.items())


def control(m,mode):
    bad=set()
    for h in H:
        for z in product(range(m),repeat=len(h)):
            a=dict(zip(h,z)); pair=0 in h and 8 in h
            hit=False
            if mode==1: hit=h==(0,)
            elif mode==2: hit=len(h)==2 and z[1]==(z[0]+1)%m
            elif mode==3: hit=pair and (len(h)==2 and z[0]==z[1] or len(h)==3 and a[8]==(a[0]+a[next(g for g in h if g not in (0,8))])%m)
            elif mode==4:
                if len(h)==2 and not any(set(h)<=set(t) for t in PARITY):
                    hit=z[1]==(z[0]+1)%m
                if h in PARITY:
                    nz=[x for x in z if x]
                    hit=len(nz)%2==1 or len(nz)==2 and nz[0]==nz[1]
            elif mode==5: hit=pair and len(h)==3 and a[8]!=(a[0]+1)%m
            if hit: bad.add((h,z))
    return bad


def audit(repo=False):
    separation=0
    for m in range(2,9):
        for D in range(min(3,m-1)+1):
            Bs=masks(m,D)
            for a in range(m):
                for size in range(D+1):
                    for F in combinations([b for b in range(m) if b!=a],size):
                        check(any(a in B and B.isdisjoint(F) for B in Bs),'mask separation')
                        separation+=1
    # Multiple successful masks need not be disjoint, even for one fixed pair.
    Bs=masks(8,1)
    overlaps=sum(sum(a in B and b not in B for B in Bs)>1
                 for a,b in product(range(8),repeat=2) if a!=b)
    check(overlaps>0,'overlapping masks')
    rows=[]
    for m in (2,3,4):
        for mode in range(6):
            if m==2 and mode==4: continue
            bad=control(m,mode)
            D,u,v=min((bound(m,u,v,bad),u,v) for u,v in product(G,repeat=2) if u!=v) if mode==4 else (bound(m,0,8,bad),0,8)
            Bs=masks(m,D)
            C,T=factor(m,u,v,bad,Bs)
            check(all(not (u in h and v in h) for h,z in C) and all(len(h)<=2 and not (u in h and v in h) for k,h,z in T),'edge removal')
            branches=[predicate(C|{(h,z) for c,h,z in T if c==k}) for k in range(len(Bs))]
            direct=predicate(bad); count=hits=overlap=0; first=None
            for z in product(range(m),repeat=9):
                expected=direct(z)
                n=sum(p(z) for p in branches)
                check(bool(n)==expected,'exact union')
                count+=expected; hits+=n; overlap+=n>1
                if n and first is None: first=z
            if mode==4:
                check(count==1 and first==(0,)*9 and D==1,'unique high-conflict control')
                for a,b in combinations(G,2):
                    # One context alone distinguishes all nonempty rows.
                    t=next((t for t in PARITY if a in t and b in t),None)
                    h=t or (a,b)
                    masks0=[]
                    for x in range(m):
                        allowed=set()
                        for y in range(m):
                            z=tuple(x if g==a else y if g==b else 0 for g in h)
                            if (h,z) not in bad: allowed.add(y)
                        masks0.append(frozenset(allowed))
                    check(all(masks0) and len(set(masks0))==m,'all-conflict pair')
            if repo:
                from mathos.research.f038_unrestricted_distributed_hyperclique import fixed,witness
                from mathos.research.f038_unrestricted_universal_search import encoded,valid
                from mathos.research.f038_universal_witness_layout import pool
                n=19*m-7; P=pool(n); pos={c:i for i,c in enumerate(P)}
                pins=tuple(i%2 for i in range(m)); F=fixed(9,m,n,pins)
                def clauses(R): return {tuple(-(g*m+a+1) for g,a in zip(h,z)) for h,z in R}
                original=sum(1<<pos[c] for c in set(F)|clauses(bad))
                raw=encoded(n,original,P)
                check(len(raw)==n+1+len(P),'normalized length')
                if first is not None:
                    w=witness(9,m,n,pins,first)
                    check(valid(P,n,original,w),'original witness')
                    for k,p in enumerate(branches):
                        if p(first):
                            branch=sum(1<<pos[c] for c in set(F)|clauses(C|{(h,z) for c,h,z in T if c==k}))
                            check(valid(P,n,branch,w),'same normalized witness')
            rows.append([m,mode,D,len(Bs),len(bad),len(T),count,hits,overlap,m**9*len(Bs)])
    check(Fraction(62,7)+Fraction(10,7)*Fraction(1,10)==9,'cutoff')
    result={'fixtures':len(rows),'separation':separation,'overlap_pairs':overlaps,'sums':[sum(r[i] for r in rows) for i in range(2,10)]}
    print('F038_UNRESTRICTED_SPARSE_PAIR_MASKS_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    import sys
    audit('--repo' in sys.argv)
