"""Exact same-U integer-two stage: sparse program weights and compressed records."""
import json
from fractions import Fraction
from itertools import product,combinations
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import encode_tm,decode_tm
from mathos.research.f038_unrestricted_crossing_adversary import onehot,true,norm,trace,tiny,reason

PLAN='docs/research/tga-universal/f038-unrestricted-quadratic-stage.json'


def length(q):
    require(type(q) is int and q>=1,'invalid state count')
    return 4+q+3*q*(q.bit_length()+4)


def count(q):
    return (9*(q+1))**(3*q)


def bits(q):
    return (q-1).bit_length()


def weight(q):
    return Fraction(count(q),1<<length(q))


def weight_bound():
    r=Fraction(729,8192)
    tail=r**4*(4-3*r)/(16*(1-r)**2)
    return weight(2)+2*weight(3)+tail


def counts():
    return [[q,length(q),bits(q),str(count(q))] for q in range(1,8)]


def dimensions(m):
    require(type(m) is int and m>=1,'invalid group size')
    n=11*m
    M=m**3
    N=sum((1<<j)*comb(n,j) for j in (1,2,3))
    L=n+1+N
    P=L-8*comb(10*m,3)
    E=L-8*comb(9*m,3)
    F=L-8*comb(4*m,3)
    R=P-n
    g=F-E+1
    return n,M,L,P,E,F,R,g


def subsequence():
    rows=[]
    for j in (16,24,32,40,48,56,64):
        cap=1<<j
        lo=hi=1
        while dimensions(hi)[2]<=cap:
            hi*=2
        while lo+1<hi:
            mid=(lo+hi)//2
            if dimensions(mid)[2]<=cap:
                lo=mid
            else:
                hi=mid
        n,M,L,P,E,F,R,g=dimensions(lo)
        require(L<=cap<dimensions(lo+1)[2] and (L-1).bit_length()==j,
                'subsequence selection failed')
        rows.append([j,*map(str,(lo,n,M,L,R,g)),1000000*L//cap,1000000*M*g//(L*L)])
    return rows


def encoding(m,pins):
    n,M,L,P,E,F,R,g=dimensions(m)
    require(m>=3 and 0<=pins<1<<(m-2),'invalid pin pattern')
    X=tuple(tuple(range((1+i)*m+1,(2+i)*m+1)) for i in range(3))
    Y=tuple(tuple(range(4*m+i*(m-1)+1,4*m+(i+1)*(m-1)+1)) for i in range(3))
    Z=tuple(tuple(range((7+i)*m+1,(8+i)*m+1)) for i in range(3))
    fixed=[]
    for A,B,G in zip(X,Z,Y):
        fixed.extend(onehot(A,G))
        for a,b in zip(A,B):
            fixed.extend(((-a,b),(a,-b)))
    pinclauses=[]
    for j in range(m-2):
        l=10*m+j+1
        if not pins>>j&1:
            l=-l
        pinclauses.extend((l,a,b) for a,b in product((1-n,n-1),(-n,n)))
    fixed.extend(pinclauses)
    I=tuple(product(range(m),repeat=3))
    A=tuple(tuple(-X[k][j[k]] for k in range(3)) for j in I)
    B=tuple(tuple(-Z[k][j[k]] for k in range(3)) for j in I)
    C=tuple(map(norm,fixed))
    U=pool(n)
    idx={c:i+n+1 for i,c in enumerate(U)}
    require(len(U)==L-n-1 and all(c in idx for c in C),'fixed clause outside pool')
    require(all(P<=idx[c]<E for c in A) and all(idx[c]>=F for c in B+tuple(pinclauses)),
            'separation geometry failed')
    W=[]
    for j in I:
        ones=[10*m+i+1 for i in range(m-2) if pins>>i&1]
        for k,b in enumerate(j):
            ones.extend((X[k][b],Z[k][b]))
            ones.extend(v for i,v in enumerate(Y[k]) if b<=i+1)
        w=sum(1<<(i-1) for i in ones)
        require(all(true(c,w) for c in C),'fixed model failed')
        W.append(w)
    for i,w in enumerate(W):
        require(all(true(c,w)==(i!=j) for j,c in enumerate(A)) and
                all(true(c,w)==(i!=j) for j,c in enumerate(B)),'index truth failed')
    return C,A,B,W


def layout():
    rows=[]
    for m in (3,4):
        C,A,B,W=encoding(m,1)
        M=len(W)
        st=[m,11*m,M,0,0,0,0]
        for a in range(3):
            for b in range(5):
                F=C+tuple(c for j,c in enumerate(A) if j%3==a)+tuple(c for j,c in enumerate(B) if j%5==b)
                good=0
                for j,w in enumerate(W):
                    ok=all(true(c,w) for c in F)
                    require(ok==(j%3!=a and j%5!=b),'modular forbidden set failed')
                    st[4]+=1
                    good+=ok
                st[3]+=1
                st[5]+=good
                st[6]+=bool(good)
        rows.append(st)
    return rows


def pack(v,a,b,q):
    seq=v[2]
    terminal=bool(seq and seq[-1]==q)
    running=seq[:-1] if terminal else seq
    c=bits(q)
    payload=''.join(format(k,'0'+str(c)+'b') if c else '' for k in running)
    require(all(0<=k<q for k in running) and len(payload)==len(running)*c,'bad crossing state')
    record=(v[0],v[1],len(seq),terminal,v[3],v[4],reason(v,a,b),payload)
    # Decode the compressed crossing sequence, including a zero-width running alphabet.
    size=record[2]-int(record[3])
    unpacked=tuple(int(payload[i*c:(i+1)*c],2) if c else 0 for i in range(size))
    if terminal:
        unpacked+=(q,)
    require(unpacked==seq,'compressed crossing roundtrip failed')
    return record


def machines(q):
    for seed in range(5832 if q==1 else 256):
        T=[]
        z=seed
        x=seed+1
        for i in range(3*q):
            if q==1:
                k=z%18
                z//=18
            else:
                x=(1664525*x+1013904223)&0xffffffff
                k=(x>>16)%(9*(q+1))
            T.append((k//9,(k//3)%3,k%3-1))
        yield tuple(T)


def splice():
    rows=[]
    for q in (1,2,3):
        st=[q,0,0,0,0,0,0,0,0]
        for T in machines(q):
            d=encode_tm(T,q)
            require(len(d)==length(q) and decode_tm(d)==(q,list(T)),'description mismatch')
            st[1]+=1
            for t in (1,4,8):
                for cut in (2,3,4):
                    V=[trace(T,q,tiny(a,a^3),t,cut,2) for a in range(4)]
                    K=[pack(v,a,a^3,q) for a,v in enumerate(V)]
                    st[2]+=4
                    for v,k in zip(V,K):
                        st[5]+=len(v[2])
                        st[6]+=k[3]
                        st[7]+=len(k[-1])
                    for i,j in combinations(range(4),2):
                        if K[i]!=K[j]:
                            continue
                        st[3]+=1
                        for a,b in ((i,j^3),(j,i^3)):
                            v=trace(T,q,tiny(a,b),t,cut,2)
                            require(pack(v,a,b,q)==K[i] and reason(v,a,b)!=-2,'compressed splice failed')
                            st[4]+=1
                            st[8]+=(a|b)!=3
        rows.append(st)
    return rows


def controls():
    require(weight_bound()<Fraction(1,5000),'weighted payload bound failed')
    require(Fraction(1995,4*1331**2)>Fraction(1,4000),'asymptotic geometry bound failed')
    for q in range(1,129):
        require(length(q)<=20*q*q and weight(q)<=Fraction(729,8192)**q/16,
                'syntax weight envelope failed')
    require(bits(1)==0 and weight(1)>weight_bound(),'one-state payload distinction failed')
    return 4


def audit():
    result={'counts':counts(),'subsequence':subsequence(),'splice':splice(),'layout':layout(),'controls':controls()}
    print('F038_UNRESTRICTED_QUADRATIC_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
