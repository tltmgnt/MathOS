"""Exact symbolic same-U bounded counterexample compiler (no selector truth tables)."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import (
    valid, stage, encode_tm, decode_tm, tape_run)
from mathos.research.f038_unrestricted_prefix_adversary import tape_codes

PLAN='docs/research/tga-universal/f038-unrestricted-symbolic-counterexamples.json'


class Circuit:
    """Signed literals, one forced true wire, AND definitions in topological order."""
    def __init__(self,inputs):
        self.inputs=inputs
        self.one=inputs+1
        self.gates=[]
        self.memo={}
    def AND(self,a,b):
        c=self.one
        if a==-c or b==-c or a==-b:
            return -c
        if a==c or a==b:
            return b
        if b==c:
            return a
        key=tuple(sorted((a,b)))
        if key not in self.memo:
            y=self.one+len(self.gates)+1
            self.memo[key]=y
            self.gates.append((y,*key))
        return self.memo[key]
    def OR(self,a,b):
        return -self.AND(-a,-b)
    def all(self,V):
        a=self.one
        for b in V:
            a=self.AND(a,b)
        return a
    def any(self,V):
        return -self.all(-v for v in V)
    def evaluate(self,inputs,mask=1):
        require(len(inputs)==self.inputs,'wrong input length')
        V=[0]+list(inputs)+[mask]
        def val(a):
            return V[a] if a>0 else mask^V[-a]
        for y,a,b in self.gates:
            require(y==len(V),'gate order')
            V.append(val(a)&val(b))
        return V
    def cnf(self,output):
        C=[(self.one,)]
        for y,a,b in self.gates:
            C.extend(((-y,a),(-y,b),(y,-a,-b)))
        C.append((output,))
        return self.one+len(self.gates),tuple(C)


def lit(V,a,mask=1):
    return V[a] if a>0 else mask^V[-a]


def verify(G,C,P,X):
    return G.all(G.OR(-p,G.any(X[l-1] if l>0 else -X[-l-1] for l in c))
                 for p,c in zip(P,C))


def simulate(G,n,P,T,q,t):
    require(type(t) is int and t>=1 and q>=1 and len(T)==3*q and
            all(0<=a<=q and 0<=w<=2 and m in (-1,0,1) for a,w,m in T),
            'invalid machine or clock')
    c=G.one
    lo,hi=-t,t+n
    cells=range(lo,hi)
    # Arrays indexed by i-lo. Symbols ordered zero, one, blank.
    S=[]
    H=[]
    for i in cells:
        if 0<=i<n:
            z=(-c,c,-c)
        elif i==n:
            z=(c,-c,-c)
        elif n<i<n+1+len(P):
            a=P[i-n-1]
            z=(-a,a,-c)
        else:
            z=(-c,-c,c)
        S.append(z)
        H.append(tuple(c if i==0 and a==0 else -c for a in range(q+1)))
    for _ in range(t):
        A=[]
        B=[[[] for _ in range(q+1)] for i in cells]
        for i in cells:
            j=i-lo
            keep=-G.any(H[j][:q])
            writes=[[G.AND(keep,S[j][w])] for w in range(3)]
            B[j][q].append(H[j][q])
            for a in range(q):
                for u in range(3):
                    v=G.AND(H[j][a],S[j][u])
                    b,w,m=T[3*a+u]
                    writes[w].append(v)
                    if lo<=i+m<hi:
                        B[j+m][b].append(v)
            A.append(tuple(G.any(V) for V in writes))
        S=A
        H=[tuple(G.any(V) for V in row) for row in B]
    X=[]
    binary=[]
    for k in range(n):
        z=G.any(G.AND(H[i-lo][q],S[i+k-lo][0]) for i in range(-t,t+1))
        o=G.any(G.AND(H[i-lo][q],S[i+k-lo][1]) for i in range(-t,t+1))
        X.append(o)
        binary.append(G.OR(z,o))
    return G.all(binary),tuple(X)


def residue3(G,P):
    c=G.one
    R=(c,-c,-c)
    a=1
    for p in P:
        R=tuple(G.OR(G.AND(-p,R[i]),G.AND(p,R[(i-a)%3])) for i in range(3))
        a=3-a
    return R


def stage_circuit(G,C,n,P,s):
    require(type(s) is int and s>=0,'invalid stage')
    c=G.one
    def assignment(x):
        return tuple(c if x>>i&1 else -c for i in range(n))
    # Parent exhaustive built-in is allowed exactly at this threshold.
    if s>=n+3:
        return G.any(verify(G,C,P,assignment(x)) for x in range(1<<n))
    A=[]
    for d,x,t in (('0',0,1),('1',1,2),('00',2,3),('01',3,1)):
        if len(d)<=s and t<=1<<(s-len(d)) and x<1<<n:
            A.append(verify(G,C,P,assignment(x)))
    if s>=2:
        t=1<<(s-2)
        if t>=2:
            clock=c if t>=4 else G.any(residue3(G,P)[:t-1])
            X=tuple(P[i] if i<2 else -c for i in range(n))
            inrange=-P[1] if n==1 else c
            A.append(G.all((clock,inrange,verify(G,C,P,X))))
    for d in tape_codes(s):
        q,T=decode_tm(d)
        ok,X=simulate(G,n,P,T,q,1<<(s-len(d)))
        A.append(G.AND(ok,verify(G,C,P,X)))
    return G.any(A)


def compile_bad(n,s):
    require(type(n) is int and n>=1 and type(s) is int and s>=0,'invalid dimensions')
    C=pool(n)
    N=len(C)
    G=Circuit(N+n)
    P=tuple(range(1,N+1))
    X=tuple(range(N+1,N+n+1))
    success=stage_circuit(G,C,n,P,s)
    bad=G.AND(-success,verify(G,C,P,X))
    return G,success,bad


def words(N):
    W=1<<N
    return [(sum(1<<x for x in range(W) if x>>i&1)) for i in range(N)],(1<<W)-1


def fixture(q,seed):
    x=seed+1
    T=[]
    for _ in range(3*q):
        x=(1664525*x+1013904223)&0xffffffff
        k=(x>>16)%(9*(q+1))
        T.append((k//9,k//3%3,k%3-1))
    return T


def programs():
    rows=[]
    for q in (1,2,3):
        st=[q,0,0,0,0,0,0]
        for seed in range(32):
            T=fixture(q,seed)
            d=encode_tm(T,q)
            require(decode_tm(d)==(q,T),'description mismatch')
            for n in (1,2):
                C=pool(n)
                N=len(C)
                P=tuple(range(1,N+1))
                for t in (1,2,4):
                    G=Circuit(N)
                    ok,X=simulate(G,n,P,T,q,t)
                    verified=G.AND(ok,verify(G,C,P,X))
                    W,mask=words(N)
                    V=G.evaluate(W,mask)
                    a=lit(V,ok,mask)
                    B=[lit(V,b,mask) for b in X]
                    v=lit(V,verified,mask)
                    st[1]+=1
                    for p in range(1<<N):
                        got=sum(((b>>p)&1)<<i for i,b in enumerate(B)) if a>>p&1 else None
                        want=tape_run(C,n,p,d,t)
                        require(got==want and bool(v>>p&1)==valid(C,n,p,want),'symbolic machine mismatch')
                        st[2]+=1
                        st[3]+=got is not None
                        st[4]+=valid(C,n,p,got)
                        st[5]+=got if got is not None else 0
                        st[6]+=got is None
        rows.append(st)
    return rows


def stages():
    rows=[]
    for n in (1,2):
        C=pool(n)
        N=len(C)
        for s in range(7):
            G,S,B=compile_bad(n,s)
            h,F=G.cnf(B)
            require(all(1<=len(c)<=3 for c in F) and h==G.one+len(G.gates),'bad CNF width')
            st=[n,s,0,0,0,0,0]
            for p in range(1<<N):
                success=stage(C,n,p,s)[0] is not None
                W=[x for x in range(1<<n) if valid(C,n,p,x)]
                st[2]+=1
                st[3]+=success
                st[4]+=bool(W) and not success
                st[5]+=len(W)
                st[6]+=0 if success else len(W)
                for x in range(1<<n):
                    inp=p|(x<<N)
                    V=G.evaluate([(inp>>i)&1 for i in range(N+n)])
                    want=valid(C,n,p,x) and not success
                    require(bool(lit(V,S))==success and bool(lit(V,B))==want,'counterexample predicate mismatch')
                    require(all(any(lit(V,a) for a in c) for c in F)==want,'CNF extension mismatch')
            rows.append(st)
    return rows


def controls():
    C=pool(1)
    # Exhaustive fallback at a stage with valid general codes.
    G,S,B=compile_bad(1,20)
    for p in range(4):
        V=G.evaluate([p&1,p>>1,0])
        require(bool(lit(V,S))==any(valid(C,1,p,x) for x in range(2)) and not lit(V,B),
                'active fallback failed')
    # Explicit generic halt, left blank output, and timeout.
    for T,want in [([(1,1,0)]*3,1), ([(1,0,-1)]*3,None), ([(0,1,0)]*3,None)]:
        G=Circuit(2)
        ok,X=simulate(G,1,(1,2),T,1,1)
        V=G.evaluate([0,0])
        got=lit(V,X[0]) if lit(V,ok) else None
        require(got==want,'halt boundary failed')
    # Every nonconstant gate has a unique extension for each input pair.
    G=Circuit(2)
    out=G.AND(1,2)
    h,F=G.cnf(out)
    for a,b in product((0,1),repeat=2):
        V=G.evaluate([a,b])
        require(all(any(lit(V,z) for z in c) for c in F[:-1]),'gate clauses failed')
        V[out]^=1
        require(not all(any(lit(V,z) for z in c) for c in F[:-1]),'nonunique extension')
    # Width-three source clauses are compiled with binary gates, not width-four clauses.
    G,S,B=compile_bad(3,0)
    h,F=G.cnf(B)
    require(all(len(c)<=3 for c in F),'wide verifier clause')
    for p,x in ((0,0),((1<<len(pool(3)))-1,0)):
        V=G.evaluate([(p|(x<<len(pool(3))))>>i&1 for i in range(G.inputs)])
        require(bool(lit(V,B))==valid(pool(3),3,p,x),'ternary verifier failed')
    try:
        compile_bad(1,-1)
    except ValueError:
        pass
    else:
        raise ValueError('invalid stage accepted')
    return 5


def audit():
    result={'programs':programs(),'stages':stages(),'controls':controls()}
    print('F038_UNRESTRICTED_SYMBOLIC_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
