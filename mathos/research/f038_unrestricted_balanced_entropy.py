"""Complement-symmetric high-entropy selector embedding; exact finite checks."""
import json
from itertools import product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import valid

PLAN='docs/research/tga-universal/f038-unrestricted-balanced-entropy.json'


def norm(c):
    return tuple(sorted(c,key=abs))


def nae(c):
    return (norm(c),norm(-l for l in c))


def truth(F,w):
    return all(any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c) for c in F)


class Balanced:
    def __init__(self,n,R):
        require(type(n) is int and n>=1 and type(R) is int and R>=1,'dimensions')
        self.n,self.R=n,R
        self.C=pool(n)
        self.z=n+1
        self.b=n+1+8*comb(n,3)
        self.t=2*self.b+1
        self.h=self.t+R
        self.D=pool(self.h)
        self.I={c:i for i,c in enumerate(self.D)}
        u=self.z
        groups=[]
        for c in self.C:
            if len(c)<3:
                G=nae((*c,self.z))
            else:
                u+=1
                G=nae((c[0],c[1],u))+nae((-u,c[2],self.z))
            groups.append(G)
        require(u==self.b,'aux dimensions')
        self.groups=tuple(groups)
        F=[]
        for v in range(1,self.b+1):
            w=self.b+v
            F.extend(((-v,w),(v,-w)))
            if v!=self.z:
                F.extend(nae((self.z,v,-w)))
        for v in range(self.t+1,self.h+1):
            F.extend(nae((self.z,self.t,v)))
        self.fixed=tuple(F)
        allc=self.fixed+tuple(c for G in groups for c in G)
        require(len(set(allc))==len(allc) and all(c in self.I for c in allc),
                'clause position collision')
        self.markers=tuple(self.I[G[0]] for G in groups)

    def base(self,p):
        require(type(p) is int and 0<=p<1<<len(self.C),'selector')
        return tuple(c for i,G in enumerate(self.groups) if p>>i&1 for c in G)

    def formula(self,p):
        return self.base(p)+self.fixed

    def encode(self,p):
        return sum(1<<self.I[c] for c in self.formula(p))

    def decode(self,q):
        require(type(q) is int and 0<=q<1<<len(self.D),'target selector')
        p=sum(((q>>i)&1)<<j for j,i in enumerate(self.markers))
        require(self.encode(p)==q,'not image')
        return p

    def project(self,w):
        mask=(1<<self.n)-1
        return (w&mask)^(mask if w>>(self.z-1)&1 else 0)

    def lift(self,u,t,s):
        return u|(u<<self.b)|(t<<(self.t-1))|(s<<self.t)

    def connected(self,F):
        R={self.z}
        while True:
            old=len(R)
            for c in F:
                S=set(map(abs,c))
                if S&R:
                    R|=S
            if len(R)==old:
                return len(R)==self.h


def fixtures(n,C):
    if n==1:
        return range(4)
    if n==2:
        return (0,255,1,2,4,8,16,32,64,128,85,170,17,34,68,136)
    return (0,(1<<len(C))-1,1,2,4,8,0x55555,0xaaaaa)


def rows():
    out=[]
    for n in (1,2,3):
        Q=Balanced(n,n)
        P=fixtures(n,Q.C)
        st=[n,n,len(P),Q.h,0,0,0,0,0,0,0,0,0]
        seen=set()
        mask=(1<<Q.h)-1
        for p in P:
            G=Q.base(p)
            F=Q.formula(p)
            q=Q.encode(p)
            require(q not in seen and Q.decode(q)==p and Q.connected(F),'image geometry')
            seen.add(q)
            require(set(F)=={norm(-l for l in c) for c in F},'not complement closed')
            W={x for x in range(1<<n) if valid(Q.C,n,p,x)}
            st[4]+=len(F)
            st[5]+=len(W)
            base=0
            projected=set()
            models=set()
            ones=[0]*Q.h
            essential=0
            for u in range(1<<Q.b):
                st[6]+=1
                if not truth(G,u):
                    continue
                base+=1
                x=Q.project(u)
                require(x in W,'base projection')
                projected.add(x)
                z=(u>>(Q.z-1))&1
                for t,s in product(range(2),range(1<<Q.R)):
                    w=Q.lift(u,t,s)
                    st[7]+=1
                    got=truth(F,w)
                    require(got==(t!=z or s==((1<<Q.R)-1 if not z else 0)),
                            'reservoir extension')
                    if not got:
                        continue
                    models.add(w)
                    for j in range(Q.h):
                        ones[j]+=(w>>j)&1
                        if not essential>>j&1 and not truth(F,w^(1<<j)):
                            essential|=1<<j
            M=len(models)
            require(projected==W and base>=2*len(W) and M==base*((1<<Q.R)+1)
                    and all(2*v==M for v in ones) and all(w^mask in models for w in models)
                    and (not M or essential==mask),'model properties')
            if M:
                w=min(models)
                require(valid(Q.D,Q.h,q,w) and valid(Q.D,Q.h,q,w^mask)
                        and valid(Q.C,n,p,Q.project(w)),'original full verifier')
            st[8]+=base
            st[9]+=M
            st[10]+=bool(M)
            st[11]+=Q.h if M else 0
            if n<=2:
                V={w for w in range(1<<Q.h) if valid(Q.D,Q.h,q,w)}
                require(V==models,'exhaustive target model set')
                st[12]+=1<<Q.h
        out.append(st)
    return out


def controls():
    for a,b,c,z in product(range(2),repeat=4):
        count=0
        for u in range(2):
            count+=(not (a==b==u)) and (not ((1-u)==c==z))
        require(bool(count)==(not (a==b==c==z)),'split NAE')
    for n in range(1,20):
        b=n+1+8*comb(n,3)
        h=2*b+1+(n+2)**4
        require(h>2*b and h>n,'padding geometry')
    Q=Balanced(1,1)
    require(Q.connected(Q.fixed),'base graph disconnected')
    try:
        Q.decode(0)
    except ValueError:
        pass
    else:
        raise ValueError('nonimage accepted')
    return 4


def audit():
    result={'controls':controls(),'rows':rows()}
    print('F038_UNRESTRICTED_BALANCED_ENTROPY_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
