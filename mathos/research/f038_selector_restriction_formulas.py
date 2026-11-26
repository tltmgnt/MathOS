"""Finite selector-block restriction, formula subfunctions and DAG reuse audit."""
import json
from itertools import combinations,product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool

PLAN='docs/research/tga-universal/f038-mrax-selector-restriction-formulas.json'


def negate(l):
    return not l if type(l) is bool else -l


def normalize(C):
    if any(type(l) is bool and l for l in C):
        return None
    D=set(l for l in C if type(l) is not bool)
    if any(-l in D for l in D):
        return None
    require(bool(D) and all(l!=0 for l in D),'unexpected empty clause')
    return tuple(sorted(D,key=abs))


def gadget(h,T):
    require(type(h) is int and h>=1 and 0<=T<1<<(1<<h),'bad table')
    m=1<<h
    C={(-(h+1),),(-(h+2),)}
    next_var=h+3
    def add(c):
        d=normalize(c)
        if d is not None:
            C.add(d)
    def rec(d,p):
        nonlocal next_var
        if d==h:
            return bool(T>>p&1)
        a,b=rec(d+1,p),rec(d+1,p|(1<<d))
        y=next_var
        next_var+=1
        x=d+1
        for c in ((x,negate(a),y),(x,a,-y),(-x,negate(b),y),(-x,b,-y)):
            add(c)
        return y
    add((rec(0,0),))
    n=h+2+m-1
    require(next_var==n+1,'auxiliary count mismatch')
    B=tuple((l,h+1,h+2) for i in range(1,h+1) for l in (i,-i))
    return n,tuple(sorted(C)),B


def sat(C,w):
    return all(any(bool(w>>(abs(l)-1)&1)==(l>0) for l in c) for c in C)


def mux():
    rows=[]
    for h in (1,2,3):
        m=1<<h
        n=h+2+m-1
        U=set(pool(n))
        st=[h,n,1<<m,0,0,0,0,0]
        for T in range(1<<m):
            n1,C,B=gadget(h,T)
            require(n1==n and set(C)<=U and set(B)<=U and not set(C)&set(B),
                    'gadget outside selector pool or overlaps block')
            A=[]
            for w in range(m):
                good=sum(sat(C,w|(z<<(h+2))) for z in range(1<<(m-1)))
                require(good==(T>>w&1),'bad mux extension')
                A.append(good)
                st[3]+=1
                st[4]+=1<<(m-1)
                st[5]+=good
                st[6]+=good==1
            for p in range(1<<(2*h)):
                D=tuple(c for i,c in enumerate(B) if p>>i&1)
                got=any(a and sat(D,w) for w,a in enumerate(A))
                want=any(T>>w&1 and all(not(p>>(2*i+(1 if w>>i&1 else 0))&1)
                                            for i in range(h)) for w in range(m))
                require(got==want,'partial residual mismatch')
                st[7]+=1
        rows.append(st)
    return rows


def blocks():
    rows=[]
    for n in (6,12,24,48,96):
        r=n//3
        h=(r+1).bit_length()-1
        m=1<<h
        seen=set()
        count=0
        for j in range(r//h):
            for u,v in combinations(range(r+1,2*r+1),2):
                B={(l,u,v) for i in range(j*h+1,(j+1)*h+1) for l in (i,-i)}
                require(len(B)==2*h and not B&seen,'block collision')
                require(all(1<=abs(a)<b<c<=n for a,b,c in B),'bad block indices')
                seen|=B
                count+=1
        require(count==(r//h)*r*(r-1)//2 and m-1<=n-2*r,'partition bound failed')
        rows.append([n,r,h,m,count,len(seen),count*((m+5)//4)])
    return rows


def gate(t,a,b):
    return t>>(2*a+b)&1


def formulas():
    st=[0]*5
    for a,b,c in product(range(16),repeat=3):
        table=tuple(gate(c,gate(a,x&1,x>>1&1),gate(b,x&1,x>>2&1))
                    for x in range(8))
        st[0]+=1
        for B in range(1,8):
            ell=2*bool(B&1)+bool(B&2)+bool(B&4)
            R=set()
            for z in range(8):
                if z&B:
                    continue
                R.add(tuple(table[x|z] for x in range(8) if not x&~B))
                st[2]+=1
            require(len(R)<=4**(2*ell-1),'formula skeleton bound failed')
            st[1]+=1
            st[3]+=len(R)
            st[4]=max(st[4],len(R))
    return st


def diamond(k):
    n=k+1
    G=[]
    y=0
    def add(a,b,t):
        G.append((a,b,t))
        return n+len(G)-1
    for x in range(1,n):
        y=add(add(y,x,8),add(y,x,14),6)
    return n,tuple(G),y


def paths(n,G,o):
    count=[0]*(n+len(G))
    require(0<=o<len(count),'bad output')
    count[o]=1
    for j in reversed(range(len(G))):
        a,b,t=G[j]
        require(0<=a<n+j and 0<=b<n+j and 0<=t<16,'bad gate')
        count[a]+=count[n+j]
        count[b]+=count[n+j]
    require(sum(count[:n])==sum(count[n:])+1,'unfolded tree identity failed')
    return count


def sharing():
    rows=[]
    for k in (1,2,4,8):
        n,G,o=diamond(k)
        P=paths(n,G,o)
        for w in range(1<<n):
            V=[w>>i&1 for i in range(n)]
            for a,b,t in G:
                V.append(gate(t,V[a],V[b]))
            require(V[o]==(w.bit_count()&1),'diamond parity failed')
        L=sum(P[:n])
        require(len(G)==3*k and L==3*(1<<k)-2 and P[0]==1<<k
                and L<=len(G)*max(P[n:])+1,'sharing count mismatch')
        rows.append([k,len(G),L,P[0],1<<n])
    return rows


def controls():
    # All false/all true tables, and explicitly contradictory pins.
    for T in (0,3):
        n,C,B=gadget(1,T)
        require(not any(sat(C+B,w) for w in range(1<<n)),'contradictory pins accepted')
        require(any(sat(C,w) for w in range(1<<n))==bool(T),'constant table failed')
    try:
        gadget(2,16)
    except ValueError:
        pass
    else:
        raise ValueError('malformed table accepted')
    try:
        paths(1,((0,1,8),),1)
    except ValueError:
        pass
    else:
        raise ValueError('forward gate accepted')
    require(paths(1,((0,0,8),),1)==[2,1],'repeated wire multiplicity lost')
    return 4


def audit():
    result={'blocks':blocks(),'mux':mux(),'formulas':formulas(),'sharing':sharing(),'controls':controls()}
    print('F038_MRAX_SELECTOR_FORMULAS_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
