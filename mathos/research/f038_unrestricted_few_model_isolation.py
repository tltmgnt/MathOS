"""Deterministic bounded-model isolation and exact same-U residual transfer."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import valid

PLAN='docs/research/tga-universal/f038-unrestricted-few-model-isolation.json'


def rem(x,p):
    while x and x.bit_length()>=p.bit_length():
        x^=p<<(x.bit_length()-p.bit_length())
    return x


def modulus(r):
    require(type(r) is int and r>=1,'field dimension')
    for p in range(1<<r,1<<(r+1)):
        if all(rem(p,q) for e in range(1,r//2+1)
               for q in range(1<<e,1<<(e+1))):
            return p
    raise ValueError('no irreducible polynomial')


def mul(a,b,p):
    q=1<<(p.bit_length()-1)
    v=0
    while b:
        if b&1:
            v^=a
        b>>=1
        a<<=1
        if a&q:
            a^=p
    return v


def dimension(n,d):
    require(type(n) is int and n>=1 and type(d) is int and d>=1,'dimensions')
    return max(1,(2*(n-1)*(n**d-1)).bit_length())


def evaluate(n,p,a,x):
    y=0
    for i in range(n-1,-1,-1):
        y=mul(y,a,p)^((x>>i)&1)
    return y


def fields():
    out=[]
    for r in range(1,7):
        p=modulus(r)
        q=1<<r
        s=0
        for a,b in product(range(q),repeat=2):
            c=mul(a,b,p)
            require(0<=c<q and (bool(c)==bool(a and b)),'field product')
            s+=c
        out.append([r,p,q*q,s])
    return out


def rows():
    out=[]
    for n in range(1,5):
        r=dimension(n,1)
        q=1<<r
        p=modulus(r)
        masks=(range(1<<(1<<n)) if n<=3 else
               [0,65535]+[((1664525*(i+1)+1013904223)&0xffffffff)>>16
                          for i in range(128)])
        st=[n,r,p,len(masks),0,0,0,0,0,0,0]
        for mask in masks:
            W=[x for x in range(1<<n) if mask>>x&1]
            M=len(W)
            counts=[0]*M
            small=0<M<=n
            st[4]+=small
            for a in range(q):
                H=[evaluate(n,p,a,x) for x in W]
                buckets=[0]*q
                for b in H:
                    buckets[b]+=1
                for v in buckets:
                    st[5]+=1
                    st[6]+=v==1
                    st[7]+=v>1
                    st[8]+=v==0
                for j,b in enumerate(H):
                    counts[j]+=buckets[b]==1
            if small:
                lower=q-(n-1)*(M-1)
                require(2*lower>=q and all(v>=lower for v in counts),'model isolation bound')
                st[9]+=sum(counts)
                st[10]+=M*lower
        out.append(st)
    return out


def truth(F,w):
    return all(any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c) for c in F)


class Buckets:
    def __init__(self,n,d):
        self.n=n
        self.r=dimension(n,d)
        self.q=1<<self.r
        self.mod=modulus(self.r)
        self.h=n+self.r*(n+2)
        self.C=pool(n)
        self.D=pool(self.h)
        self.I={c:j for j,c in enumerate(self.D)}
        self.source_positions=tuple(self.I[c] for c in self.C)

    def powers(self,a):
        require(0<=a<self.q,'field argument')
        P=[1]
        for _ in range(1,self.n):
            P.append(mul(P[-1],a,self.mod))
        return P

    def start(self,i):
        return self.n+1+i*(self.n+1)

    def tag(self,i):
        return self.n+self.r*(self.n+1)+i+1

    def formula(self,p,a,b):
        require(0<=p<1<<len(self.C) and 0<=a<self.q and 0<=b<self.q,'bucket input')
        P=self.powers(a)
        F=[c for j,c in enumerate(self.C) if p>>j&1]
        for i in range(self.r):
            u=self.start(i)
            F.append((u if b>>i&1 else -u,))
            for j in range(1,self.n+1):
                v=u+1
                if P[j-1]>>i&1:
                    F.extend(((j,u,-v),(-j,u,v),(j,-u,v),(-j,-u,-v)))
                else:
                    F.extend(((-u,v),(u,-v)))
                u=v
            F.append((-u,))
            tag=self.tag(i)
            F.append((tag if a>>i&1 else -tag,))
        require(len(set(F))==len(F),'duplicate clause')
        return F

    def encode(self,F):
        return sum(1<<self.I[c] for c in F)

    def recover(self,q):
        p=sum(((q>>j)&1)<<i for i,j in enumerate(self.source_positions))
        a=sum(((q>>self.I[(self.tag(i),)])&1)<<i for i in range(self.r))
        b=sum(((q>>self.I[(self.start(i),)])&1)<<i for i in range(self.r))
        require(self.encode(self.formula(p,a,b))==q,'not a bucket selector')
        return p,a,b

    def lift(self,a,b,x):
        P=self.powers(a)
        w=x
        for i in range(self.r):
            u=self.start(i)-1
            v=(b>>i)&1
            w|=v<<u
            for j in range(self.n):
                v^=((P[j]>>i)&1)*((x>>j)&1)
                w|=v<<(u+j+1)
            w|=((a>>i)&1)<<(self.tag(i)-1)
        return w


def encoding():
    out=[]
    for n in (1,2,3):
        B=Buckets(n,1)
        P=(range(4) if n==1 else
           (0,255,1,2,4,8,16,32,64,128,85,170,17,34,68,136) if n==2 else
           (0,(1<<len(B.C))-1,1,2,4,8,0x55555,0xaaaaa))
        E=range(B.q) if n<3 else (0,1,2,B.q-1)
        st=[n,B.r,B.h,len(B.D),len(P),0,0,0,0,0,0,0]
        seen=set()
        for p,a,b in product(P,E,E):
            F=B.formula(p,a,b)
            q=B.encode(F)
            require(q not in seen and B.recover(q)==(p,a,b),'selector injection')
            seen.add(q)
            st[5]+=1
            st[10]+=len(F)
            W=[]
            for x in range(1<<n):
                w=B.lift(a,b,x)
                got=truth(F,w)
                want=valid(B.C,n,p,x) and evaluate(n,B.mod,a,x)==b
                require(got==want and valid(B.D,B.h,q,w)==got and
                        (w&((1<<n)-1))==x,'model correspondence')
                st[6]+=1
                if got:
                    W.append(w)
                for j in range(n,B.h):
                    require(not truth(F,w^(1<<j)),'flipped auxiliary accepted')
                    st[11]+=1
            if n==1:
                require(sorted(W)==[w for w in range(1<<B.h) if valid(B.D,B.h,q,w)],
                        'full target model set')
            st[7]+=len(W)
            st[8]+=len(W)==1
            st[9]+=len(W)>1
        out.append(st)
    return out


def controls():
    B=Buckets(1,1)
    require(B.encode(B.formula(0,0,0))!=B.encode(B.formula(0,1,0)),
            'alpha tag required')
    for n in range(1,30):
        for d in (1,2,3):
            q=1<<dimension(n,d)
            require(q>2*(n-1)*(n**d-1) and q<=4*n**(d+1),'field capacity')
    try:
        B.recover(0)
    except ValueError:
        pass
    else:
        raise ValueError('nonimage accepted')
    return 3


def audit():
    result={'controls':controls(),'encoding':encoding(),'fields':fields(),'rows':rows()}
    print('F038_UNRESTRICTED_FEW_MODEL_ISOLATION_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
