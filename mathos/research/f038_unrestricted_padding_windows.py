"""Seeded single-support padding and simultaneous polynomial-window residual transfer."""
import json
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import valid,stage
from mathos.research.f038_unrestricted_single_support_reduction import (
    fixed,translate,extend,recover)

PLAN='docs/research/tga-universal/f038-unrestricted-padding-windows.json'


class Padding:
    def __init__(self,n,h,d):
        require(type(n) is int and n>=1 and type(h) is int and h>=3*n+7
                and type(d) is int and d>=1,'invalid dimensions')
        self.n,self.h,self.h0,self.d=n,h,3*n+7,d
        self.seeds=h**d
        require((self.seeds-1).bit_length()<=h-self.h0,'seed capacity')
        self.C,self.D=pool(n),pool(h)
        I={c:j for j,c in enumerate(self.D)}
        F=fixed(n)
        M=tuple(map(translate,self.C))
        pins=tuple(((1,2,-v),(1,2,v)) for v in range(self.h0+1,h+1))
        A=F+M+tuple(c[0] for c in pins)
        require(len({tuple(map(abs,c)) for c in A})==len(A)
                and all(len(c)==3 for c in A),'support collision')
        self.base=sum(1<<I[c] for c in F)
        self.positions=tuple(I[c] for c in M)
        self.pins=tuple((I[a],I[b]) for a,b in pins)

    def encode(self,p,z):
        require(type(p) is int and 0<=p<1<<len(self.C) and
                type(z) is int and 0<=z<self.seeds,'invalid source or seed')
        return (self.base|sum(1<<j for i,j in enumerate(self.positions) if p>>i&1)
                |sum(1<<pos[(z>>i)&1] for i,pos in enumerate(self.pins)))

    def decode(self,q):
        require(type(q) is int and 0<=q<1<<len(self.D),'invalid target')
        p=sum(((q>>j)&1)<<i for i,j in enumerate(self.positions))
        z=sum(((q>>b)&1)<<i for i,(_,b) in enumerate(self.pins))
        require(q==self.encode(p,z),'not a seeded image')
        return p,z

    def lift(self,x,z):
        require(0<=x<1<<self.n and 0<=z<self.seeds,'invalid assignment or seed')
        return extend(self.n,x)|(z<<self.h0)


def fixtures(n):
    return range(4) if n==1 else (0,255,1,2,4,8,16,32,64,128,85,170,17,34,68,136)


def rows():
    out=[]
    for n,H in ((1,(14,15,16)),(2,(18,19,20))):
        for h in H:
            Q=Padding(n,h,1)
            P=fixtures(n)
            st=[n,h,len(P),Q.seeds,0,0,0,0,0,0,0,0,0]
            seen=set()
            for p in P:
                W=[x for x in range(1<<n) if valid(Q.C,n,p,x)]
                for z in range(Q.seeds):
                    q=Q.encode(p,z)
                    require(q not in seen and Q.decode(q)==(p,z),'injection failed')
                    seen.add(q)
                    st[4]+=1
                    st[8]+=q.bit_count()
                    models=0
                    for x in range(1<<n):
                        w=Q.lift(x,z)
                        got=valid(Q.D,h,q,w)
                        require(got==(x in W) and recover(n,w)==x,'model correspondence')
                        st[5]+=1
                        models+=got
                        if got:
                            for v in range(Q.h0,h):
                                require(not valid(Q.D,h,q,w^(1<<v)),'padding flip accepted')
                                st[9]+=1
                    st[6]+=models>0
                    st[7]+=models
                    if z in (0,Q.seeds-1):
                        for s in range(3):
                            w=stage(Q.D,h,q,s)[0]
                            require((w is not None)==(s>=1 and z==0 and 0 in W),
                                    'small exact stage mismatch')
                            require(w is None or valid(Q.C,n,p,recover(n,w)),
                                    'stage projection failed')
                            st[10]+=1
                            st[11]+=w is not None
                            st[12]+=models>0 and w is None
            out.append(st)
    return out


def search(C,n,p,windows,stage_of):
    """Finite prototype. The theorem uses stage_of(h)=k*ceil(log2 L(h))."""
    attempts=0
    for Q in windows:
        require(Q.n==n and Q.C==C,'window source mismatch')
        for z in range(Q.seeds):
            q=Q.encode(p,z)
            attempts+=1
            w=stage(Q.D,Q.h,q,stage_of(Q.h))[0]
            if w is not None:
                x=recover(n,w)
                require(valid(C,n,p,x),'bad projected witness')
                return x,attempts
    return None,attempts


def wrapper():
    C=pool(1)
    Q=[Padding(1,h,1) for h in (14,15,16)]
    out=[]
    for s in range(3):
        st=[s,4,0,0,0]
        for p in range(4):
            x,t=search(C,1,p,Q,lambda h:s)
            require((x is not None)==(s>=1 and valid(C,1,p,0)),'window result')
            st[2]+=t
            st[3]+=x is not None
            st[4]+=x is None
        out.append(st)
    return out


def controls():
    # Capacity checked with integer bit lengths; no floating point rounding.
    Q=Padding(1,14,1)
    require(Q.decode(Q.encode(0,13))==(0,13),'seed endpoint')
    try:
        Padding(1,11,1)
    except ValueError:
        pass
    else:
        raise ValueError('oversized seed range accepted')
    try:
        Q.encode(0,14)
    except ValueError:
        pass
    else:
        raise ValueError('out of range seed accepted')
    q=Q.encode(0,0)
    try:
        Q.decode(q^(1<<Q.pins[0][0]))
    except ValueError:
        pass
    else:
        raise ValueError('missing padding pin accepted')
    return 4


def audit():
    result={'controls':controls(),'rows':rows(),'wrapper':wrapper()}
    print('F038_UNRESTRICTED_PADDING_WINDOWS_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
