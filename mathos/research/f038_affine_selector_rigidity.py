"""Semantic affine SAT selector covers and local monotone certificates."""
import json
from itertools import combinations
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool

PLAN='docs/research/tga-universal/f038-mrax-affine-selector-rigidity.json'


def maxima(n):
    C=pool(n)
    X=tuple(sum(1<<i for i,c in enumerate(C) if any(
        bool(x>>(abs(l)-1)&1)==(l>0) for l in c)) for x in range(1<<n))
    require(len(set(X))==1<<n and len({v.bit_count() for v in X})==1,'invalid maximal selectors')
    return len(C),X


def contained(p,X):
    return any(p&v==p for v in X)


def affine_layers(points):
    P=frozenset(points)
    layer={frozenset((v,)) for v in P}
    while layer:
        yield layer
        nxt=set()
        for F in layer:
            a=min(F)
            for b in P-F:
                Q=frozenset(v^a^b for v in F)
                if Q<=P:
                    require(not F&Q,'cosets overlap')
                    nxt.add(F|Q)
        layer=nxt


def pair_flat(x,y):
    same=x&y
    xonly=x^same
    yonly=y^same
    H=set()
    z=same
    while True:
        H.update((z|xonly,z|yonly))
        if not z:
            break
        z=(z-1)&same
    return frozenset(H)


def flats():
    rows=[]
    for n in (1,2):
        N,X=maxima(n)
        q=X[0].bit_count()
        P={p for p in range(1<<N) if contained(p,X)}
        hist=[]
        twohist=[]
        bad=rigid=0
        pair_dims={}
        for d,L in enumerate(affine_layers(P)):
            hist.append(len(L))
            two=0
            for F in L:
                K=tuple(sorted(set(X)&F))
                bad+=len(K)>=3
                require(d<=q and len(K)<=2,'affine dimension or triple obstruction failed')
                if len(K)==2:
                    x,y=K
                    bound=q-(x^y).bit_count()//2+1
                    require(d<=bound,'pair deficit failed')
                    pair_dims[K]=max(pair_dims.get(K,-1),d)
                    two+=1
                if d==q:
                    is_cube=len(K)==1 and all(p&K[0]==p for p in F)
                    rigid+=is_cube
                    require(n==1 or is_cube,'maximal dimension rigidity failed')
            twohist.append(two)
        for x,y in combinations(sorted(X),2):
            d=q-(x^y).bit_count()//2+1
            F=pair_flat(x,y)
            require(len(F)==1<<d and F<=P and pair_dims[x,y]==d,
                    'pair bound not attained')
        rows.append([n,N,q,len(P),sum(hist),hist,twohist,bad,rigid])
    return rows


def volumes():
    rows=[]
    for n in (1,2,3,4):
        N,X=maxima(n)
        q=X[0].bit_count()
        W=len(X)
        intersections=[(1<<N)-1]
        size=0
        for s in range(1,1<<W):
            b=s&-s
            v=intersections[s^b]&X[b.bit_length()-1]
            intersections.append(v)
            term=1<<v.bit_count()
            size+=term if s.bit_count()&1 else -term
        delta=N
        overlap=pairs=triples=0
        for i,j in combinations(range(W),2):
            d=(X[i]^X[j]).bit_count()//2
            require(d==sum(comb(n,k)-comb(n-(i^j).bit_count(),k)
                           for k in range(1,min(3,n)+1)),'distance formula failed')
            delta=min(delta,d)
            overlap+=1<<(q-d)
            pairs+=1
        for i,j,k in combinations(range(W),3):
            require(not contained(X[i]^X[j]^X[k],X),'triple XOR accepted')
            triples+=1
        require(size>=W*(1<<q)-overlap,'inclusion exclusion bound failed')
        if n>=3:
            require(overlap<1<<q,'cover bound failed')
        if n>=4:
            require(2*overlap<1<<q,'optimal cover rigidity bound failed')
        rows.append([n,N,q,delta,pairs,triples,str(size),str(overlap),
                     (size+(1<<q)-1)//(1<<q)])
    return rows


def local():
    n=3
    N=1<<n
    F=tuple(H for layer in affine_layers(range(N)) for H in layer)
    st=[n,len(F),0,0,0,0,0]
    for word in range(1<<N):
        def val(x):
            return word>>x&1
        if any(val(x)>val(x|1<<i) for x in range(N) for i in range(n)):
            continue
        st[2]+=1
        for x in range(N):
            c=a=n
            for P in range(N):
                if all((x^y)&P or val(y)==val(x) for y in range(N)):
                    c=min(c,P.bit_count())
                st[4]+=1
            for H in F:
                if x in H and all(val(y)==val(x) for y in H):
                    a=min(a,n-(len(H).bit_length()-1))
                st[5]+=1
            require(a==c,'local affine certificate mismatch')
            st[3]+=1
            st[6]+=c
    return st


def controls():
    # Unit-only SAT: exactly 3^n models, each selector pair avoids conflict.
    for n in range(1,7):
        count=sum(all((p>>(2*i)&3)!=3 for i in range(n)) for p in range(1<<(2*n)))
        require(count==3**n,'unit-only volume failed')
    N,X=maxima(2)
    require(all(len(pair_flat(x,y))==1<<(X[0].bit_count()-(x^y).bit_count()//2+1)
                for x,y in combinations(X,2)),'pair construction failed')
    # Monotone local certificate equality includes both constant functions.
    require(len(tuple(affine_layers(range(4))))==3,'full flat lattice missing')
    N,X=maxima(1)
    require(not contained(3,X) and contained(0,X),'unit boundary failed')
    return 4


def audit():
    result={'flats':flats(),'volumes':volumes(),'local':local(),'controls':controls()}
    print('F038_MRAX_AFFINE_SELECTOR_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
