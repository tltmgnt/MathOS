"""Same-U cubic interval: one-state prefix theorem and unique residual counting."""
import json
from itertools import product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import (
    encode_tm,decode_tm,tape_run,encoded,valid,BUILTINS,run_program)
from mathos.research.f038_unrestricted_quadratic_stage import length,count
from mathos.research.f038_unrestricted_cubic_fixture import PIN

PLAN='docs/research/tga-universal/f038-unrestricted-cubic-interval.json'


def tables():
    options=tuple((a,w,m) for a in range(2) for w in range(3) for m in (-1,0,1))
    return product(options,repeat=3)


def macro(T,a):
    seen=set()
    while a not in seen:
        seen.add(a)
        h,w,m=T[a]
        if h:
            return 'halt',w,m
        if m:
            return 'move',w,m
        a=w
    return 'loop',0,0


def classify(T):
    if T[1][0]:
        return 0
    if T[0][0]:
        return 1
    if not T[2][0]:
        return 2
    one,zero=macro(T,1),macro(T,0)
    if one[0]!='move' or one[2]==-1:
        return 3
    if zero[0]!='move':
        return 4
    if zero[2]==1:
        return 5
    if one[1]==zero[1]==1:
        return 6
    return 7


def classification():
    st=[0]*8
    for T in tables():
        st[classify(T)]+=1
    return st


def raw_run(T,S,n,t):
    off=t+1
    V=[2]*(2*t+len(S)+n+4)
    V[off:off+len(S)]=S
    h=off
    for _ in range(t):
        a,w,m=T[V[h]]
        V[h]=w
        h+=m
        if a:
            bits=V[h:h+n]
            require(len(bits)==n,'output outside tape fixture')
            if 2 in bits:
                return None
            return sum(v<<j for j,v in enumerate(bits))
    return None


def prefix_audit():
    rows=[]
    for n in (3,4):
        for kind in (0,1):
            P=[1]*n+[0]+[kind*(1-j%2) for j in range(n)]
            for t in (1,4,16,64):
                st=[n,kind,t,0,0,0,0,0]
                O=set()
                for T in tables():
                    w=raw_run(T,P,n,t)
                    st[3]+=1
                    if w is not None:
                        O.add(w)
                        st[6]+=1
                    if classify(T) in (2,5,6):
                        require(w is None,'nonemitting structural branch produced output')
                    for b in range(8):
                        S=P+[(b>>j)&1 for j in range(3)]
                        v=raw_run(T,S,n,t)
                        require(v==w,'one-state suffix invariance failed')
                        st[4]+=1
                        st[5]+=v is not None
                st[7]=len(O)
                rows.append(st)
    return rows


def dimensions(n):
    N=2*n+4*comb(n,2)+8*comb(n,3)
    L=n+1+N
    return L,3*(L-1).bit_length()


def geometry():
    rows=[]
    for n in range(52,93):
        L,s=dimensions(n)
        P=L-8*comb(31,3)
        R=P-n
        t=1<<(s-length(2))
        require(length(1)<=length(2)<=s<length(3) and s-3<n and t<=R
                and P>=2*n+1 and n-31>=2,'invalid interval clock')
        rows.append([n,L,s,R,t])
    return rows


def counts():
    margins=[dimensions(n)[1]-n-3 for n in range(1,52)]
    require(min(margins)>=0,'earlier exhaustive cutoff failed')
    L,s=dimensions(93)
    require(s>=length(3),'next description not active')
    D=count(1)+count(2)
    M=(1<<29)-D-1
    E=7*comb(31,3)-116
    require(M>0 and E>=0,'invalid census bound')
    return [len(margins),min(margins),93,L,s,D,M,E,7*comb(52,3)-208+2]


def truth(c,w):
    return any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c)


def pin_formula(n,w):
    # First n-2 bits use the last two variables as guards; last two bits
    # use x1,x2 as guards. No clause depends on its own pinned variable.
    F=[(i if w>>(i-1)&1 else -i,u,v)
       for i in range(1,n-1) for u,v in product((1-n,n-1),(-n,n))]
    F.extend((u,v,j if w>>(j-1)&1 else -j)
             for j in (n-1,n) for u,v in product((-1,1),(-2,2)))
    require(len(F)==len(set(F))==4*n,'pin clause collision')
    return tuple(F)


def layouts():
    rows=[]
    for n in (52,59,74,92):
        C=pool(n)
        L,s=dimensions(n)
        start=len(C)-8*comb(31,3)
        require(len(C)==L-n-1 and all(len(c)==3 and abs(c[0])>=n-30 for c in C[start:]),
                'actual suffix mismatch')
        require(not any(len(c)==3 and abs(c[0])>=n-30 for c in C[:start]),
                'earlier suffix clause')
        patterns=(0,1,0x1234567,(1<<29)-1)
        F=[pin_formula(n,a<<(n-31)) for a in patterns]
        needed=set(c for clauses in F for c in clauses)
        index={c:j for j,c in enumerate(C) if c in needed}
        require(len(index)==len(needed),'pin clause outside pool')
        st=[n,0,0,0,0,0,0]
        first=None
        for a,G in zip(patterns,F):
            w=a<<(n-31)
            pre=tuple(sorted(index[c] for c in G if index[c]<start))
            suf=[c for c in G if index[c]>=start]
            if first is None:
                first=pre
            require(pre==first and len(suf)==116,'prefix independence failed')
            require(all(len(c)==3 and truth(c,w) for c in G),'pin witness failed')
            good=sum(truth(c,w) for c in C[start:])
            for j in range(n):
                require(not all(truth(c,w^(1<<j)) for c in G),'pin flip accepted')
                st[6]+=1
            st[1]+=1
            st[2]+=len(pre)
            st[3]+=len(suf)
            st[4]+=good
            st[5]+=good-len(suf)
        rows.append(st)
    return rows


def explicit():
    n=52
    C=pool(n)
    I={c:j for j,c in enumerate(C)}
    rows=[]
    old=pin_formula(n,PIN)[:200]
    old_p=sum(1<<I[c] for c in old)
    L,s=dimensions(n)
    start=2*n+4*comb(n,2)
    require(s==54 and 1<<(s-length(2))<=start+1,'old fixture clock')
    require(valid(C,n,old_p,PIN) and len(old)==200,'old fixture mismatch')
    for g in range(4):
        w=PIN|(g<<50)
        F=pin_formula(n,w)
        p=sum(1<<I[c] for c in F)
        require(old_p&p==old_p and not p&((1<<start)-1)
                and valid(C,n,p,w) and valid(C,n,old_p,w),'explicit extension failed')
        require(all(not valid(C,n,p,run_program(C,n,p,d,1<<(s-len(d))))
                    for d in BUILTINS),'built-in accepted extension')
        good=sum(truth(c,w) for c in C[start:])
        for j in range(n):
            require(not all(truth(c,w^(1<<j)) for c in F),'explicit pin flip accepted')
        rows.append([g,str(w),len(F),good,good-len(F),n])
    return rows


def controls():
    # Compare raw fixture interpreter to the unchanged parent interpreter
    # on a real width-three selector, for every one-state description.
    n=3
    C=pool(n)
    p=1<<(2*n+4*comb(n,2))
    S=list(map(int,encoded(n,p,C)))
    for T in tables():
        d=encode_tm(T,1)
        require(decode_tm(d)==(1,list(T)),'description roundtrip')
        require(raw_run(T,S,n,16)==tape_run(C,n,p,d,16),'parent interpreter mismatch')
    require(sum(classification())==count(1),'one-state table coverage')
    require(length(3)==61 and length(2)==42 and length(1)==20,'description boundary')
    require(7*comb(31,3)==31465 and 7*comb(52,3)==154700,'ternary census')
    return 4


def audit():
    result={'classification':classification(),'counts':counts(),'explicit':explicit(),
            'geometry':geometry(),'layouts':layouts(),'prefix':prefix_audit(),'controls':controls()}
    print('F038_UNRESTRICTED_CUBIC_INTERVAL_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
