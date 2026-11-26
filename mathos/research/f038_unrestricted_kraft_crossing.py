"""Prefix-free incoming crossing census, exact integer finite cubic bounds."""
import json
from fractions import Fraction
from itertools import product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import valid,encode_tm,decode_tm
from mathos.research.f038_unrestricted_quadratic_stage import length,count
from mathos.research.f038_unrestricted_cubic_crossing_census import pin,truth,trace,table,binary_tape,ceil

PLAN='docs/research/tga-universal/f038-unrestricted-kraft-crossing.json'


def shapes():
    H=[[0]*3 for _ in range(3)]
    initial=dead=0
    for T in product(tuple(product(range(3),(-1,0,1))),repeat=6):
        if T[1][0]==2:
            initial+=729
            continue
        R={0}
        for _ in range(2):
            R|={a for i,(a,d) in enumerate(T) if i//3 in R and a<2}
        if not any(a==2 and i//3 in R for i,(a,d) in enumerate(T)):
            dead+=729
            continue
        l={a for i,(a,d) in enumerate(T) if i//3 in R and a<2 and d==-1}
        r={a for i,(a,d) in enumerate(T) if i//3 in R and a<2 and d==1}
        H[len(l)][len(r)]+=729
    require(initial+dead+sum(map(sum,H))==count(2),'shape partition')
    return {'dead':dead,'high':H[1][2]+H[2][1]+H[2][2],'initial':initial,'matrix':H}


def bound(n,m,S):
    L=n+1+2*n*n+8*comb(n,3)
    s=3*(L-1).bit_length()
    g=8*(comb(n-1,3)-comb(n-m,3))+1
    h=g-n
    require(h>0,'bad cuts')
    t=1<<(s-length(2))
    k,r=divmod((t+g)//2,h)
    A,B=1<<m,1<<(n-m)
    C=0
    for l in range(3):
        for rr in range(3):
            if l==0 or rr==0 or l==rr==1:
                C+=S['matrix'][l][rr]*(A+(0 if rr==0 else 2 if rr==2 and l==0 else 1)*B)
    F=count(1)+count(3)+4+S['initial']
    u=(Fraction(S['high']*g*(A+B)*(1<<(k+1)),2*h-r)+Fraction(g*C,h)+F)/(1<<n)
    return u,[n,m,s,g,k,str(ceil(10**9*u))],L


def geometry(S):
    rows=[]
    for n in range(186,235):
        u,row,L=min((bound(n,m,S) for m in range(2*n//5,(13*n+19)//20+1)),key=lambda a:a[0])
        s=row[2]
        require(s<length(4) and s-3<n and (1<<(s-length(3)))+n<=n+1+2*n*n,
                'stage eligibility')
        if 191<=n<=233:
            require(s==72 and 8*u<7,'census inequality')
        else:
            require(u>=1,'unexpected interval')
        rows.append((u,row))
    good=[(u,row) for u,row in rows if 191<=row[0]<=233]
    u,row=max(good,key=lambda a:a[0])
    return {'boundSum':str(sum(int(v[-1]) for _,v in good)),
            'endpoints':[v for _,v in rows if v[0] in (186,190,191,192,193,200,210,233,234)],
            'lower191':str(ceil((1-good[0][0])*(1<<191))),
            'maxCeil':str(ceil(10**9*u)),'maxN':row[0],'sizes':len(good)}


def formula(n,m,w):
    require(3<=m<=n-3,'split')
    F=[]
    for I in ((1,2,3),(n-2,n-1,n)):
        for S in product((-1,1),repeat=3):
            c=tuple(v*b for v,b in zip(I,S))
            if truth((c,),w):
                F.append(c)
    for lo,hi,g,h in ((4,m,1,2),(m+1,n-3,n-1,n)):
        for i in range(lo,hi+1):
            F.extend(pin(i,(w>>(i-1))&1,g,h))
    require(len(F)==len(set(F))==4*n-10,'pin clauses')
    return F


def pins():
    rows=[]
    for n in (6,7,8):
        m=(n+1)//2
        C=pool(n)
        L=n+1+len(C)
        P=L-8*comb(n-1,3)
        Q=L-8*comb(n-m,3)
        I={c:i+n+1 for i,c in enumerate(C)}
        st=[n,m,0,0,0,0]
        seen=set()
        for w in range(1<<n):
            F=formula(n,m,w)
            pos=tuple(sorted(I[c] for c in F))
            require(pos not in seen,'pin injection')
            seen.add(pos)
            require(all(I[c]<P if max(map(abs,c))<=m else
                        min(map(abs,c))>m and I[c]>=Q for c in F),'cut geometry')
            W=[x for x in range(1<<n) if truth(F,x)]
            p=sum(1<<(j-n-1) for j in pos)
            require(W==[w] and valid(C,n,p,w),'unique model')
            st[2]+=1
            st[3]+=1<<n
            st[4]+=len(W)
            st[5]+=len(F)
        rows.append(st)
    return rows


def transcripts():
    rows=[]
    for t in (8,16,32):
        st=[t,256,0,0,0,0,0,0]
        for seed in range(256):
            T=table(seed)
            require(decode_tm(encode_tm(T,2))==(2,T),'syntax')
            G={}
            for a,b in product(range(4),repeat=2):
                kind,w,h,E=trace(binary_tape(a,b),4,T,t)
                st[2]+=1
                if kind!=2:
                    continue
                st[3]+=1
                for c in range(7,13):
                    if h<c<=h+3:
                        continue
                    cross=[(x,y,z) for x,y,z in E if (x<c)!=(y<c)]
                    if any(z==2 for x,y,z in cross):
                        continue
                    side=h>=c
                    seq=tuple(z for x,y,z in cross if (y>=c)==side)
                    key=c,side,b if side else a
                    M=G.setdefault(key,{})
                    require(seq not in M or M[seq]==w,'incoming determinism')
                    M[seq]=w
                    st[4]+=1
                    st[5]+=w==(a|(b<<2))
            for M in G.values():
                require(all(a==b or b[:len(a)]!=a for a in M for b in M),
                        'prefix violation')
                require(sum(Fraction(1,1<<len(a)) for a in M)<=1,'Kraft violation')
                st[6]+=1
                st[7]+=len(M)
        rows.append(st)
    return rows


def controls():
    for h in range(1,5):
        for J in product(range(5),repeat=h):
            k,r=divmod(sum(J),h)
            require(sum(Fraction(1,1<<j) for j in J)>=Fraction(2*h-r,1<<(k+1)),
                    'convex bound')
    require([length(q) for q in (1,2,3,4)]==[20,42,61,92],'description lengths')
    require(sum(Fraction(1,1<<len(w)) for w in ((0,),(1,0),(1,1)))==1,
            'nontrivial prefix code')
    return 3


def audit():
    S=shapes()
    result={'controls':controls(),'geometry':geometry(S),'pins':pins(),'shapes':S,'traces':transcripts()}
    print('F038_UNRESTRICTED_KRAFT_CROSSING_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
