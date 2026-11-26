"""Same-U unique-witness isolation, exact seed census and bounded-stage replay."""
import json
from itertools import product
from fractions import Fraction
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import valid,stage

PLAN='docs/research/tga-universal/f038-unrestricted-isolation-transfer.json'


def truth(F,x):
    return all(any(bool(x>>(abs(l)-1)&1)==(l>0) for l in c) for c in F)


def hash_pass(n,seed,r,x):
    for i in range(r):
        b=(seed>>(i*(n+1)))&1
        a=(seed>>(i*(n+1)+1))&((1<<n)-1)
        if b^((a&x).bit_count()&1):
            return False
    return True


def extend(n,seed,x):
    w=x
    for i in range(n+1):
        b=(seed>>(i*(n+1)))&1
        w|=b<<(n+i*(n+1))
        for j in range(1,n+1):
            b^=((seed>>(i*(n+1)+j))&1)*((x>>(j-1))&1)
            w|=b<<(n+i*(n+1)+j)
    return w


class Isolation:
    def __init__(self,n,p):
        require(type(n) is int and n>=1,'invalid n')
        self.n=n
        self.h=n+(n+1)**2
        self.C=pool(n)
        require(type(p) is int and 0<=p<1<<len(self.C),'invalid selector')
        self.p=p
        self.F=tuple(c for j,c in enumerate(self.C) if p>>j&1)
        self.D=pool(self.h)
        self.index={c:j for j,c in enumerate(self.D)}
    def clauses(self,r,seed):
        n=self.n
        require(type(r) is int and 1<=r<=n+1 and type(seed) is int
                and 0<=seed<1<<((n+1)**2),'invalid isolation seed')
        F=list(self.F)
        for i in range(n+1):
            a=n+1+i*(n+1)
            F.append((a if seed>>(i*(n+1))&1 else -a,))
            for j in range(1,n+1):
                c=a+1
                if seed>>(i*(n+1)+j)&1:
                    F.extend(((j,a,-c),(-j,a,c),(j,-a,c),(-j,-a,-c)))
                else:
                    F.extend(((-a,c),(a,-c)))
                a=c
            if i<r:
                F.append((-a,))
        require(len(set(F))==len(F),'duplicate clause')
        return tuple(F)
    def encode(self,F):
        return sum(1<<self.index[c] for c in F)
    def recover(self,F):
        n=self.n
        S=set(F)
        source={c:j for j,c in enumerate(self.C)}
        p=sum(1<<source[c] for c in S if all(abs(l)<=n for l in c))
        seed=r=0
        for i in range(n+1):
            a=n+1+i*(n+1)
            require(((a,) in S)!=((-a,) in S),'bad offset')
            seed|=int((a,) in S)<<(i*(n+1))
            for j in range(1,n+1):
                c=a+1
                seed|=int((j,a,-c) in S)<<(i*(n+1)+j)
                a=c
            r+=(-a,) in S
        require(p==self.p and S==set(self.clauses(r,seed)),'bad isolation encoding')
        return p,r,seed


def census():
    rows=[]
    bounds=[]
    for n in (1,2):
        C=pool(n)
        seeds=1<<((n+1)**2)
        H=[[0,0,0,0] for _ in range(n+1)]
        min_unique=seeds
        st=[n,0,0,0,0,0,0,0,0]
        for p in range(1<<len(C)):
            W=[x for x in range(1<<n) if valid(C,n,p,x)]
            st[1]+=1
            st[2]+=bool(W)
            r0=(len(W)-1).bit_length()+1 if W else 0
            for r in range(1,n+2):
                u=0
                for seed in range(seeds):
                    z=sum(hash_pass(n,seed,r,x) for x in W)
                    st[3]+=1
                    st[4]+=z==0
                    st[5]+=z==1
                    st[6]+=z>1
                    st[7]+=z
                    u+=z==1
                if r==r0:
                    st[8]+=u
                    require(16*u>=3*seeds,'isolation probability bound failed')
                    min_unique=min(min_unique,u)
                    h=H[r-1]
                    h[0]+=1
                    h[1]+=u
                    h[2]=u if h[0]==1 else min(h[2],u)
                    h[3]=max(h[3],u)
        rows.append(st)
        bounds.append([n,seeds,min_unique,H])
    return rows,bounds


def encoding():
    rows=[]
    S=[[s,0,0,0,0,0] for s in range(9)]
    for n in (1,2):
        C=pool(n)
        seen=set()
        st=[n,0,0,0,0,0,0]
        for p in range(1<<len(C)):
            Q=Isolation(n,p)
            seeds=range(16) if n==1 else (0,1,7,85,170,255,256,511)
            for r in range(1,n+2):
                for seed in seeds:
                    F=Q.clauses(r,seed)
                    q=Q.encode(F)
                    require(q not in seen and Q.recover(F)==(p,r,seed),'encoding collision')
                    seen.add(q)
                    st[1]+=1
                    st[2]+=len(F)
                    W=[]
                    for x in range(1<<n):
                        w=extend(n,seed,x)
                        ok=truth(F,w)
                        require(ok==(truth(Q.F,x) and hash_pass(n,seed,r,x)),
                                'hash extension mismatch')
                        st[3]+=1
                        st[4]+=ok
                        if ok:
                            W.append(w)
                        for j in range(n,Q.h):
                            require(not truth(F,w^(1<<j)),'flipped auxiliary accepted')
                            st[5]+=1
                    if n==1:
                        V=[w for w in range(1<<Q.h) if valid(Q.D,Q.h,q,w)]
                        require(sorted(W)==V,'full model set mismatch')
                        st[6]+=1<<Q.h
                        for s in range(9):
                            w=stage(Q.D,Q.h,q,s)[0]
                            require(w is None or w in V,'unverified isolation output')
                            if w is not None:
                                require(valid(C,n,p,w&((1<<n)-1)),'projection failed')
                            a=S[s]
                            a[1]+=1
                            a[2]+=len(W)==1
                            a[3]+=w is not None
                            a[4]+=len(W)==1 and w is None
                            a[5]+=bool(W) and w is None
        rows.append(st)
    return rows,S


def controls():
    require(Fraction(13,16)**4<Fraction(1,2),'advice union bound failed')
    for n in (1,2,3):
        for r in range(1,n+2):
            for x in range(1<<n):
                for y in range(x+1,1<<n):
                    # Single-row output pairs must occur equally often.
                    pairs=[0]*4
                    for seed in range(1<<(n+1)):
                        a=hash_pass(n,seed,1,x)
                        b=hash_pass(n,seed,1,y)
                        pairs[2*int(a)+int(b)]+=1
                    require(len(set(pairs))==1,'pairwise independence failed')
    Q=Isolation(1,0)
    require(Q.encode(Q.clauses(1,0))!=Q.encode(Q.clauses(2,0)),'row count lost')
    try:
        Q.clauses(0,0)
    except ValueError:
        pass
    else:
        raise ValueError('invalid row count accepted')
    return 4


def audit():
    a,b=census()
    c,d=encoding()
    result={'census':a,'bounds':b,'encoding':c,'stages':d,'controls':controls()}
    print('F038_UNRESTRICTED_ISOLATION_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
