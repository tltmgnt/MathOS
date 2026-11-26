"""Finite exact cubic-stage crossing census; existential family, not a full-clock enumeration."""
import json
from fractions import Fraction
from itertools import product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import (
    encoded,valid,encode_tm,decode_tm,tape_run)
from mathos.research.f038_unrestricted_quadratic_stage import length,count

PLAN='docs/research/tga-universal/f038-unrestricted-cubic-crossing-census.json'


def dimensions(n):
    m=(n+1)//2
    L=n+1+2*n*n+8*comb(n,3)
    P=L-8*comb(n-1,3)
    Q=L-8*comb(n-m,3)
    s=3*(L-1).bit_length()
    return m,L,P,Q,s


def parity_counts(r):
    return (sum(1<<j for j in range(0,r+1,2)),
            sum(1<<j for j in range(1,r+1,2)))


def best_bound(n):
    m,L,P,Q,s=dimensions(n)
    g=Q-P+1
    a,b=m-2,n-m-2
    t=1<<(s-length(2))
    D0=count(1)+count(3)+1
    best=None
    for r in range(1,257):
        den=(r+1)*(g-n)-t
        if den<=0:
            continue
        E,O=parity_counts(r)
        u=Fraction(count(2)*(E*(1<<a)+O*(1<<b))*(r+1)*g+D0*den,
                   (1<<(n-4))*den)
        if best is None or u<best[0]:
            best=u,r
    require(best is not None,'no positive crossing denominator')
    u,r=best
    return u,[n,m,L,s,P,Q,g,r,str(ceil(10**9*u))]


def ceil(x):
    return -(-x.numerator//x.denominator)


def geometry():
    require([length(q) for q in (1,2,3,4)]==[20,42,61,92]
            and [count(q) for q in (1,2,3)]==[18**3,27**6,36**9],
            'actual description geometry')
    R=[]
    for n in range(93,187):
        u,row=best_bound(n)
        s=row[3]
        if n<=185:
            require(s<length(4) and s-3<n and
                    (1<<(s-length(3)))+n<=n+1+2*n*n and 8*u<7,
                    'cubic census bound failed')
        else:
            require(u>1,'next-size boundary changed')
        R.append((u,row))
    old=R[:-1]
    u,row=max(old,key=lambda pair:pair[0])
    require(R[0][0]*1024<1,'strong n=93 bound')
    return {'boundSum':str(sum(int(v[8]) for _,v in old)),
            'endpoints':[v for _,v in R if v[0] in (93,116,117,147,148,185,186)],
            'gSum':sum(v[6] for _,v in old),
            'lower93':str(ceil((1-R[0][0])*(1<<89))),
            'maxCeil':str(ceil(10**9*u)),'maxN':row[0],
            'rSum':sum(v[7] for _,v in old),'sizes':len(old),
            'stages':[[s,sum(v[3]==s for _,v in old)] for s in (63,66,69)]}


def pin(i,v,g,h):
    return [tuple(sorted((i if v else -i,x,y),key=abs))
            for x,y in product((-g,g),(-h,h))]


def formula(n,a,b):
    m=(n+1)//2
    require(n>=8 and 0<=a<1<<(m-2) and 0<=b<1<<(n-m-2),'pin input')
    F=[]
    for i in range(3,m+1):
        F.extend(pin(i,(a>>(i-3))&1,1,2))
    for i in range(m+1,n-1):
        F.extend(pin(i,(b>>(i-m-1))&1,n-1,n))
    F.extend(pin(1,0,3,4)+pin(2,0,3,4)+pin(n-1,0,1,2)+pin(n,0,1,2))
    require(len(F)==len(set(F))==4*n,'pin clause collision')
    return tuple(F)


def truth(F,w):
    return all(any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c) for c in F)


def pins():
    rows=[]
    for n in (8,9,10):
        m,L,P,Q,s=dimensions(n)
        C=pool(n)
        require(len(C)+n+1==L,'actual selector length')
        I={c:i+n+1 for i,c in enumerate(C)}
        st=[n,m,0,0,0,0]
        seen=set()
        for a in range(1<<(m-2)):
            for b in range(1<<(n-m-2)):
                F=formula(n,a,b)
                pos=tuple(sorted(I[c] for c in F))
                require(pos not in seen,'pin family injection')
                seen.add(pos)
                cut=4*(m-2)
                end=4*(n-4)
                require(all(I[c]<P for c in F[:cut]) and
                        all(I[c]>=Q for c in F[cut:end]),'actual tape partition')
                w=(a<<2)|(b<<m)
                W=[x for x in range(1<<n) if truth(F,x)]
                p=sum(1<<(j-n-1) for j in pos)
                require(W==[w] and valid(C,n,p,w),'unique witness mismatch')
                st[2]+=1
                st[3]+=1<<n
                st[4]+=len(W)
                st[5]+=len(F)
        rows.append(st)
    return rows


def table(seed):
    T=[]
    x=seed+1
    for j in range(6):
        x=(1664525*x+1013904223)&0xffffffff
        v=(x>>16)%27
        T.append((v//9,(v//3)%3,v%3-1))
    return T


def trace(S,n,T,t):
    V=dict(enumerate(S))
    a=h=0
    events=[]
    for _ in range(t):
        z,w,m=T[3*a+V.get(h,2)]
        V[h]=w
        events.append((h,h+m,z))
        h+=m
        a=z
        if a==2:
            W=[V.get(h+i,2) for i in range(n)]
            return (1,None,h,events) if 2 in W else (2,sum(v<<i for i,v in enumerate(W)),h,events)
    return 0,None,h,events


def binary_tape(a,b):
    return [1,1,1,1,0,a&1,a>>1,0,0,0,0,0,b&1,b>>1]


def transcripts():
    rows=[]
    cuts=range(7,13)
    g=len(cuts)
    for t in (8,16,32):
        st=[t,256,0,0,0,0,0,0,0,0,0]
        for seed in range(256):
            T=table(seed)
            d=encode_tm(T,2)
            require(decode_tm(d)==(2,T),'actual two-state syntax')
            groups={}
            success=0
            good=[[0]*g for _ in range(4)]
            for a,b in product(range(4),repeat=2):
                kind,w,h,events=trace(binary_tape(a,b),4,T,t)
                st[2]+=1
                st[3+kind]+=1
                if kind!=2:
                    continue
                ok=w==(a|(b<<2))
                success+=ok
                st[6]+=ok
                for j,c in enumerate(cuts):
                    seq=tuple(z for x,y,z in events if (x<c)!=(y<c))
                    if h<c<=h+3:
                        st[7]+=1
                        continue
                    if 2 in seq:
                        st[8]+=1
                        continue
                    side=int(h>=c)
                    require(len(seq)%2==side,'crossing parity')
                    key=(c,side,a if side==0 else b,seq)
                    require(key not in groups or groups[key]==w,'side output mismatch')
                    groups[key]=w
                    st[9]+=1
                    if ok:
                        for r in range(4):
                            good[r][j]+=len(seq)<=r
            for r in range(4):
                E,O=parity_counts(r)
                require(all(v<=4*(E+O) for v in good[r]),'per-cut count')
                total=sum(good[r])
                require(total*(r+1)>=success*((r+1)*(g-4)-t),
                        'double count failed')
                st[10]+=total
        rows.append(st)
    return rows


def controls():
    # A genuine well-formed output following a halting crossing: exclude that cut.
    T=[(1,0,1),(0,1,1),(2,2,0),(1,0,1),(2,1,1),(2,2,0)]
    kind,w,h,E=trace(binary_tape(2,0),4,T,16)
    require((kind,w,h)==(2,0,7) and E[-1]==(6,7,2),'halting crossing control')
    # Actual decoder/interpreter agreement on a complete normalized selector.
    n=8
    C=pool(n)
    I={c:j for j,c in enumerate(C)}
    p=sum(1<<I[c] for c in formula(n,2,3))
    S=list(map(int,encoded(n,p,C)))
    for seed in range(16):
        T=table(seed)
        d=encode_tm(T,2)
        require(trace(S,n,T,32)[1]==tape_run(C,n,p,d,32),'actual interpreter mismatch')
    require(parity_counts(3)==(5,10) and parity_counts(0)==(1,0),'transcript counting')
    # Stage 63 and 69 actual clocks.
    require((1<<(63-length(2)))==2097152 and (1<<(69-length(2)))==134217728,
            'exact clock')
    return 4


def audit():
    result={'controls':controls(),'geometry':geometry(),'pins':pins(),'traces':transcripts()}
    print('F038_UNRESTRICTED_CUBIC_CROSSING_CENSUS_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
