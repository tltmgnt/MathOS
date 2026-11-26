"""Same-U residual census: injective guarded-prefix queries and bounded frontier."""
import json
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import valid,stage

PLAN='docs/research/tga-universal/f038-unrestricted-residual-census.json'


class Queries:
    def __init__(self,n,p):
        require(type(n) is int and n>=1,'invalid source size')
        self.n=n
        self.C=pool(n)
        require(type(p) is int and 0<=p<1<<len(self.C),'invalid selector')
        self.p=p
        self.D=pool(n+1)
        self.idx={c:j for j,c in enumerate(self.D)}
        self.base=sum(1<<self.idx[c] for j,c in enumerate(self.C) if p>>j&1)
    def pair(self,i,a,b):
        require(type(i) is int and 1<=i<=self.n and type(a) is int and type(b) is int
                and 0<=a<1<<i and 0<=b<1<<i and a!=b,'invalid prefix pair')
        z=self.n+1
        q=self.base
        for j in range(i):
            l=j+1
            q|=1<<self.idx[(l if a>>j&1 else -l,z)]
            q|=1<<self.idx[(l if b>>j&1 else -l,-z)]
        return q
    def recover(self,q):
        require(type(q) is int and 0<=q<1<<len(self.D),'invalid query selector')
        z=self.n+1
        src={c:j for j,c in enumerate(self.C)}
        p=0
        A={}
        B={}
        for j,c in enumerate(self.D):
            if not q>>j&1:
                continue
            if all(abs(l)!=z for l in c):
                p|=1<<src[c]
            else:
                require(len(c)==2 and abs(c[-1])==z,'not a guarded pair')
                T=A if c[-1]>0 else B
                l=c[0]
                require(abs(l) not in T,'duplicate guard')
                T[abs(l)]=int(l>0)
        i=len(A)
        require(1<=i<=self.n and set(A)==set(B)==set(range(1,i+1)),'bad guard depth')
        a=sum(v<<(j-1) for j,v in A.items())
        b=sum(v<<(j-1) for j,v in B.items())
        require(a!=b,'equal prefixes')
        return p,i,a,b


def frontier(n,p,s,b):
    require(type(s) is int and s>=0 and type(b) is int and b>=1,'invalid search budget')
    Q=Queries(n,p)
    F=[0]
    log=[]
    calls=hits=0
    for i in range(1,n+1):
        F=[w for a in F for w in (a,a|(1<<(i-1)))]
        while len(F)>b:
            a=F[0]
            others=tuple(F[1:b+1])
            ids=[]
            for v in others:
                q=Q.pair(i,a,v)
                ids.append(q)
                w=stage(Q.D,n+1,q,s)[0]
                calls+=1
                if w is not None:
                    require(valid(Q.D,n+1,q,w),'invalid stage output')
                    x=w&((1<<n)-1)
                    require(valid(Q.C,n,p,x),'invalid projection')
                    return x,log,calls,hits+1
            require(len(set(ids))==b,'star query collision')
            log.append((i,a,others,tuple(ids)))
            del F[0]
    x=next((x for x in F if valid(Q.C,n,p,x)),None)
    require(calls<=n*b*b,'query budget exceeded')
    return x,log,calls,hits


def at_exponents(n,p,k,d):
    require(type(k) is int and k>=1 and type(d) is int and d>=0,'invalid exponents')
    L=n+1+len(pool(n))
    L2=n+2+len(pool(n+1))
    return frontier(n,p,k*(L2-1).bit_length(),L**d)


def recover_star(n,p,s,b,x,log):
    Q=Queries(n,p)
    require(valid(Q.C,n,p,x),'not a source witness')
    for i,a,others,ids in log:
        if x&((1<<i)-1)!=a:
            continue
        require(len(ids)==len(others)==b and len(set(ids))==b,'invalid star size')
        for v,q in zip(others,ids):
            require(q==Q.pair(i,a,v) and Q.recover(q)==(p,i,a,v)
                    and valid(Q.D,n+1,q,x) and stage(Q.D,n+1,q,s)[0] is None,
                    'bad star replay')
        return tuple((q,x) for q in ids)
    raise ValueError('no lost model prefix')


def encoding():
    st=[0]*5
    seen=set()
    n=2
    for p in range(1<<len(pool(n))):
        Q=Queries(n,p)
        for i in range(1,n+1):
            for a in range(1<<i):
                for b in range(1<<i):
                    if a==b:
                        continue
                    q=Q.pair(i,a,b)
                    require(q not in seen and Q.recover(q)==(p,i,a,b),'encoding collision')
                    seen.add(q)
                    st[0]+=1
                    st[3]+=q.bit_count()
                    for w in range(1<<(n+1)):
                        x=w&((1<<n)-1)
                        want=valid(Q.C,n,p,x) and x&((1<<i)-1)==(b if w>>n&1 else a)
                        got=valid(Q.D,n+1,q,w)
                        require(got==want,'guarded disjunction mismatch')
                        st[1]+=1
                        st[2]+=got
    st[4]=len(seen)
    return st


def frontier_audit():
    rows=[]
    n=2
    C=pool(n)
    for s in range(7):
        for b in (1,2,3,4):
            st=[s,b,0,0,0,0,0,0,0,0,0]
            for p in range(1<<len(C)):
                W=tuple(x for x in range(1<<n) if valid(C,n,p,x))
                x,log,calls,hits=frontier(n,p,s,b)
                require(x is None or x in W,'false witness')
                require(calls<=n*b*b,'frontier cost overflow')
                stars=sum(any(w&((1<<i)-1)==a for w in W) for i,a,_,_ in log)
                failed=bool(W) and x is None
                if failed:
                    require(stars>0,'missing satisfiable deletion')
                    for w in W:
                        S=recover_star(n,p,s,b,w,log)
                        require(len(S)==b and all(v==w for _,v in S),'common witness lost')
                st[2]+=1
                st[3]+=bool(W)
                st[4]+=x is not None
                st[5]+=failed
                st[6]+=calls
                st[7]+=hits
                st[8]+=len(log)
                st[9]+=stars
                st[10]+=stars if failed else 0
            rows.append(st)
    return rows


def controls():
    Q=Queries(2,0)
    require(Q.pair(1,0,1)!=Q.pair(1,1,0),'ordered prefixes lost')
    # Force both source bits zero: the first pivot can be lost at stage zero.
    C=pool(2)
    p=sum(1<<C.index(c) for c in ((-1,),(-2,)))
    x,log,_,_=frontier(2,p,0,1)
    require(x is None and len(recover_star(2,p,0,1,0,log))==1,'loss control')
    require(frontier(2,p,6,1)[0]==0,'exhaustive fallback failed')
    require(at_exponents(2,p,1,1)[0]==0,'exact exponent wrapper failed')
    try:
        Q.pair(1,0,0)
    except ValueError:
        pass
    else:
        raise ValueError('equal prefix accepted')
    return 5


def audit():
    result={'encoding':encoding(),'frontier':frontier_audit(),'controls':controls()}
    print('F038_UNRESTRICTED_CENSUS_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
