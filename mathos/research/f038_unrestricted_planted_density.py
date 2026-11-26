"""Same-U cubic-stage exclusion by complete ternary blocks; exact finite census."""
import json
from itertools import combinations,product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import valid

PLAN='docs/research/tga-universal/f038-unrestricted-planted-density.json'


def cap(n):
    require(type(n) is int and n>=1,'invalid n')
    return (n.bit_length()-1)//4


def truth(c,w):
    return any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c)


def scan(C,n,p):
    """Algorithmic prototype, not a compiled U description or a time measurement."""
    require(type(p) is int and 0<=p<1<<len(C),'invalid selector')
    start=2*n+4*comb(n,2)
    pins={}
    blocks=0
    for j,I in enumerate(combinations(range(1,n+1),3)):
        k=start+8*j
        block=(p>>k)&255
        if block==255:
            return None,blocks,-1,0
        if block.bit_count()!=7:
            continue
        blocks+=1
        missing=(255^block).bit_length()-1
        for h,v in enumerate(I):
            b=1-((missing>>(2-h))&1)
            if v in pins and pins[v]!=b:
                return None,blocks,-1,0
            pins[v]=b
    U=[v for v in range(1,n+1) if v not in pins]
    u=len(U)
    if u>cap(n):
        return None,blocks,u,0
    base=sum(b<<(v-1) for v,b in pins.items())
    for a in range(1<<u):
        w=base|sum(((a>>j)&1)<<(v-1) for j,v in enumerate(U))
        if valid(C,n,p,w):
            return w,blocks,u,a+1
    return None,blocks,u,1<<u


def fixtures(n,C):
    if n<=2:
        return list(range(1<<len(C)))
    if n==3:
        return [p<<(2*n+4*comb(n,2)) for p in range(256)]
    I={c:j for j,c in enumerate(C)}
    out=[]
    for w in (0,1,0xaa&((1<<n)-1),(1<<n)-1):
        for omit in (0,1,2):
            F=[c for c in C if len(c)==3 and max(map(abs,c))<=n-omit and truth(c,w)]
            F.extend((j if w>>(j-1)&1 else -j,) for j in range(n-omit+1,n+1))
            p=sum(1<<I[c] for c in F)
            require(valid(C,n,p,w),'planted fixture invalid')
            out.append(p)
    return out


def audit_scan():
    rows=[]
    for n in (1,2,3,4,16):
        C=pool(n)
        P=fixtures(n,C)
        st=[n,len(P),0,0,0,0,0,0]
        for p in P:
            w,b,u,t=scan(C,n,p)
            require(w is None or valid(C,n,p,w),'invalid emitted witness')
            if n<=4:
                W=[x for x in range(1<<n) if valid(C,n,p,x)]
                require(not W or (u>=0 and (u>cap(n) or w in W)),'missed covered SAT')
                require(u>=0 or not W,'contradiction on SAT')
            st[2]+=w is not None
            st[3]+=b
            st[4]+=u<0
            st[5]+=u>cap(n)
            st[6]+=t
            st[7]+=w if w is not None else 0
        rows.append(st)
    return rows


def histogram():
    rows=[]
    for n in (3,4,5):
        T=[sum(1<<i for i in I) for I in combinations(range(n),3)]
        m=len(T)
        H=[0]*(n+1)
        for p in range(1<<m):
            covered=0
            for j,M in enumerate(T):
                if p>>j&1:
                    covered|=M
            H[n-covered.bit_count()]+=127**(m-p.bit_count())
        require(sum(H)==128**m,'histogram mass')
        for r in range(1,n+1):
            # Multiply exact probabilities by 128**m. No floating point.
            h=m-comb(n-r,3)
            bound=comb(n,r)*127**h*128**(m-h)
            require(sum(H[r:])<=bound,'union bound failed')
        rows.append([n,m,list(map(str,H))])
    return rows


def controls():
    for n in (3,4,16):
        C=pool(n)
        start=2*n+4*comb(n,2)
        for j,I in enumerate(combinations(range(1,n+1),3)):
            expected=tuple(tuple(v*s for v,s in zip(I,S)) for S in product((-1,1),repeat=3))
            require(C[start+8*j:start+8*j+8]==expected,'actual pool block order')
    C=pool(4)
    start=2*4+4*comb(4,2)
    p=(254<<start)|(127<<(start+8))
    require(scan(C,4,p)[2]==-1 and not any(valid(C,4,p,x) for x in range(16)),
            'incompatible forced blocks')
    C=pool(16)
    P=fixtures(16,C)
    require(scan(C,16,P[10])[0]==65535 and scan(C,16,P[10])[3]==2 and
            scan(C,16,P[11])[2]==2 and scan(C,16,P[11])[0] is None,
            'enumeration cap boundary')
    require(all(cap(n)==u for n,u in ((15,0),(16,1),(255,1),(256,2))),
            'cap arithmetic')
    return 4


def audit():
    result={'controls':controls(),'hist':histogram(),'scan':audit_scan()}
    print('F038_UNRESTRICTED_PLANTED_DENSITY_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
