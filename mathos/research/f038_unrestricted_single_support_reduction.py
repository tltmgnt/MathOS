"""Linear-variable single-support normal form for the original unrestricted selector SAT."""
import json
from itertools import combinations
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import valid
from mathos.research.f038_unrestricted_bijunctive_core import project

PLAN='docs/research/tga-universal/f038-unrestricted-single-support-reduction.json'


def norm(c):
    return tuple(sorted(c,key=abs))


def truth(c,w):
    return any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c)


def gadget():
    F=[norm((-(i+1),(i+a)%7+1,(i+b)%7+1))
       for i in range(7) for a,b in ((1,2),(3,5),(4,6))]
    S={tuple(map(abs,c)) for c in F}
    require(len(S)==21,'cyclic support collision')
    F.extend(tuple(-v for v in I) for I in combinations(range(1,8),3)
             if I not in S)
    return tuple(F)


def fixed(n):
    require(type(n) is int and n>=1,'invalid source size')
    F=list(gadget())
    for i in range(n):
        u=8+3*i
        v,d=u+1,u+2
        F.extend(map(norm,((-u,v,1),(u,-v,2),(-d,1,2),(u,v,-d))))
    return tuple(F)


def translate(c):
    D=[-(8+3*(-l-1)) if l<0 else 9+3*(l-1) for l in c]
    if len(D)<3:
        D.append(1)
    if len(D)<3:
        D.append(2)
    return norm(D)


def extend(n,x):
    return sum(3<<(7+3*i) for i in range(n) if x>>i&1)


def recover(n,w):
    return sum(((w>>(7+3*i))&1)<<i for i in range(n))


class Reduction:
    def __init__(self,n):
        self.n=n
        self.h=3*n+7
        self.C=pool(n)
        self.D=pool(self.h)
        self.F=fixed(n)
        self.M=tuple(map(translate,self.C))
        A=self.F+self.M
        require(len({tuple(map(abs,c)) for c in A})==len(A)
                and all(len(c)==3 for c in A),'support collision')
        I={c:j for j,c in enumerate(self.D)}
        self.base=sum(1<<I[c] for c in self.F)
        self.positions=tuple(I[c] for c in self.M)
    def encode(self,p):
        require(type(p) is int and 0<=p<1<<len(self.C),'invalid selector')
        return self.base|sum(1<<j for i,j in enumerate(self.positions) if p>>i&1)
    def decode(self,q):
        require(type(q) is int and 0<=q<1<<len(self.D),'invalid image selector')
        p=sum(((q>>j)&1)<<i for i,j in enumerate(self.positions))
        require(q==self.encode(p),'not an image selector')
        return p


def gadget_audit():
    F=gadget()
    W=[w for w in range(128) if all(truth(c,w) for c in F)]
    require(W==[0] and len(F)==35,'gadget models')
    return [len(F),21,W]


def fixtures(n,C):
    if n<=2:
        return list(range(1<<len(C)))
    P=[0,(1<<len(C))-1]
    for seed in range(128):
        x=seed+1
        p=0
        for j in range(len(C)):
            x=(1664525*x+1013904223)&0xffffffff
            if x>>29<2:
                p|=1<<j
        P.append(p)
    return P


def audit_rows():
    rows=[]
    for n in (1,2,3,4):
        Q=Reduction(n)
        F=Q.F
        W=[w for w in range(1<<Q.h) if all(truth(c,w) for c in F)]
        require(W==[extend(n,x) for x in range(1<<n)],'fixed model mismatch')
        P=fixtures(n,Q.C)
        st=[n,Q.h,len(Q.D),1<<Q.h,len(W),len(P),0,0,0,0,0]
        seen=set()
        for p in P:
            q=Q.encode(p)
            require(Q.decode(q)==p,'inverse selector mismatch')
            seen.add(q)
            good=0
            for x in range(1<<n):
                w=extend(n,x)
                require(recover(n,w)==x,'copy projection failed')
                want=valid(Q.C,n,p,x)
                got=valid(Q.D,Q.h,q,w)
                require(want==got,'translated model mismatch')
                good+=got
                st[7]+=1
            st[6]+=good>0
            st[8]+=good
            st[9]+=q.bit_count()
        st[10]=len(seen)
        require(len(seen)==len(set(P)),'selector collision')
        rows.append(st)
    return rows


def controls():
    # Exhaust all five cyclic orbits of 4-sets and check the spare triples.
    rot=lambda w:((w<<1)&127)|(w>>6)
    F=gadget()
    used={sum(1<<(abs(v)-1) for v in c) for c in F[:21]}
    seen=set()
    for w,s in ((15,11),(23,19),(27,25),(29,25),(43,11)):
        require(s& w==s and s.bit_count()==3 and s not in used,'spare orbit')
        V=[]
        for _ in range(7):
            V.append(w)
            w=rot(w)
        require(len(set(V))==7 and min(V)==V[0] and not seen.intersection(V),
                'orbit collision')
        seen.update(V)
    require(seen=={w for w in range(128) if w.bit_count()==4},'incomplete orbits')
    for i in range(8):
        R,G,W=project(1<<i)
        require(len(R)==7 and len(W)==8,'single clause locally reducible')
    Q=Reduction(4)
    q=Q.encode((1<<len(Q.C))-1)
    require(q.bit_count()==len(Q.F)+len(Q.C) and not q&((1<<(2*Q.h+2*Q.h*(Q.h-1)))-1),
            'nonternary clause or collision')
    # All dummy supports selected, pairwise disjoint.
    S=[{8+3*i,9+3*i,10+3*i} for i in range(Q.n)]
    require(len(set.union(*S))==3*Q.n and
            all(norm((8+3*i,9+3*i,-(10+3*i))) in Q.F for i in range(Q.n)),
            'disjoint core missing')
    try:
        Q.decode(0)
    except ValueError:
        pass
    else:
        raise ValueError('nonimage selector accepted')
    return 4


def audit():
    result={'controls':controls(),'gadget':gadget_audit(),'rows':audit_rows()}
    print('F038_UNRESTRICTED_SINGLE_SUPPORT_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
