"""Same-U suffix adversary and explicit surviving-description bound."""
import json
from itertools import product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import (
    encode_tm,decode_tm,tape_run,stage,valid)

PLAN='docs/research/tga-universal/f038-unrestricted-prefix-adversary.json'


def dimensions(n):
    require(type(n) is int and n>=8 and n%4==0,'bad suffix size')
    h=n//4-1
    N=sum((1<<j)*comb(n,j) for j in (1,2,3))
    L=n+1+N
    B=L-8*comb(n//2,3)
    R=B-n
    require(2*R>=L,'short prefix')
    return h,N,L,B,R


def geometry():
    out=[]
    for n in (8,12,16,24,32,64,128):
        h,N,L,B,R=dimensions(n)
        s=(L-1).bit_length()
        if n<=24:
            C=pool(n)
            split=B-n-1
            require(len(C)==N and all(len(c)==3 and min(map(abs,c))>n//2
                                      for c in C[split:]) and
                    not any(len(c)==3 and min(map(abs,c))>n//2 for c in C[:split]),
                    'suffix pool order mismatch')
        out.append([n,h,N,L,B,R,s,max(0,s-(R.bit_length()-1)),int((1<<h)>(1<<(s+1)))])
    return out


def tape_codes(s):
    q=1
    while 4+q+3*q*(q.bit_length()+4)<=s:
        options=tuple(product(range(q+1),range(3),(-1,0,1)))
        for T in product(options,repeat=3*q):
            yield encode_tm(T,q)
        q+=1


def pin_projection(n,x):
    h,N,L,B,R=dimensions(n)
    return (x>>(n//2+h))&((1<<h)-1)


def forbidden(n,s):
    h,N,L,B,R=dimensions(n)
    C=pool(n)
    F={0}
    count=blind=emits=0
    for d in tape_codes(s):
        count+=1
        t=1<<(s-len(d))
        if t>R:
            continue
        blind+=1
        x=tape_run(C,n,0,d,t)
        if x is not None:
            emits+=1
            F.add(pin_projection(n,x))
    a=0
    while a in F:
        a+=1
    return (a if a<1<<h else -1),count,blind,emits,len(F)


def blind_audit():
    rows=[]
    for n,s in ((8,10),(12,12),(16,13),(24,15),(8,20),(12,21)):
        h,N,L,B,R=dimensions(n)
        a,c,d,e,f=forbidden(n,s)
        rows.append([n,s,h,c,d,e,f,a])
    return rows


def lift(F,n,a):
    h,N,L,B,R=dimensions(n)
    require(0<=a<1<<h,'bad pin pattern')
    require(all(1<=len(c)<=3 and len(set(map(abs,c)))==len(c)
                and all(1<=abs(l)<=h for l in c) for c in F),'bad source clause')
    G=[]
    u,v=n-1,n
    def add(c):
        if len(c)==1:
            G.extend(c+(x,y) for x,y in product((-u,u),(-v,v)))
        elif len(c)==2:
            G.extend(c+(x,) for x in (-u,u))
        else:
            G.append(c)
    for c in F:
        add(tuple(sorted(((n//2+abs(l))*(1 if l>0 else -1) for l in c),key=abs)))
    for i in range(h):
        l=n//2+h+i+1
        add((l if a>>i&1 else -l,))
    return tuple(G)


def encode(F,n):
    C=pool(n)
    I={c:j for j,c in enumerate(C)}
    require(all(c in I for c in F),'lifted clause outside pool')
    p=sum(1<<I[c] for c in set(F))
    h,N,L,B,R=dimensions(n)
    require(not p&((1<<(B-n-1))-1),'nonzero prefix selector')
    return p


def truth(F,x):
    return all(any(bool(x>>(abs(l)-1)&1)==(l>0) for l in c) for c in F)


def embedding():
    C=pool(2)
    st=[0]*6
    n=12
    a=1
    for p in range(1<<len(C)):
        F=tuple(c for j,c in enumerate(C) if p>>j&1)
        G=lift(F,n,a)
        encode(G,n)
        ok=False
        for z in range(64):
            got=truth(G,z<<6)
            want=(z>>2&3)==a and truth(F,z&3)
            require(got==want,'lift equivalence failed')
            ok|=got
            st[1]+=1
            st[2]+=got
        st[0]+=1
        st[3]+=ok
        st[4]+=len(G)
        st[5]=max(st[5],len(G))
    return st


def controls():
    n=8
    h,N,L,B,R=dimensions(n)
    C=pool(n)
    s=(L-1).bit_length()
    a,*_=forbidden(n,s)
    p=encode(lift((),n,a),n)
    w=a<<(n//2+h)
    require(a>=0 and valid(C,n,p,w) and stage(C,n,p,s)[0] is None,
            'actual unrestricted stage bad witness failed')
    # Actual generic interpreter: common prefix including the output read.
    d=encode_tm([(1,1,0)]*3,1)
    require(len(d)==20 and decode_tm(d) is not None and
            tape_run(C,n,0,d,1)==tape_run(C,n,p,d,1)==(1<<n)-1,
            'prefix replay failed')
    require(forbidden(8,20)[0]==-1,'exhausted pattern space control failed')
    try:
        lift(((1,2),),8,1)
    except ValueError:
        pass
    else:
        raise ValueError('out-of-range source slot accepted')
    return 4


def audit():
    result={'geometry':geometry(),'blind':blind_audit(),'embedding':embedding(),'controls':controls()}
    print('F038_UNRESTRICTED_PREFIX_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
