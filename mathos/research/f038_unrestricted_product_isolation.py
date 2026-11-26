"""Exact small product-isolation probabilities and normalized restriction regression."""
import json
from itertools import product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_unrestricted_universal_search import encoded, valid
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import (
    cross, fixed, witness, fixture)
from mathos.research.f038_unrestricted_recursive_tiling import digit_masks, forbidden


def probability(m,r):
    N=m**r
    tuples=tuple(product(range(m),repeat=r))
    D=(m-1).bit_length()+2
    K=1<<(D-1)
    weights=[]
    for S in range(1<<m):
        a=S.bit_count()
        weights.append(sum((K>>k)**a*(K-(K>>k))**(m-a) for k in range(D)))
    den=D*K**m
    require(sum(weights)==den,'normalized mixture')
    boxes=[]
    for S in product(range(1<<m),repeat=r):
        mask=sum(1<<i for i,a in enumerate(tuples)
                 if all(S[g]>>v&1 for g,v in enumerate(a)))
        w=1
        for v in S:
            w*=weights[v]
        boxes.append((mask,w))
    require(sum(w for _,w in boxes)==den**r,'product distribution')
    checks=0
    least=den**r
    for A in range(1,1<<N):
        num=sum(w for B,w in boxes if (A&B).bit_count()==1)
        require(num*(16*D)**r>=3**r*den**r,'isolation probability')
        least=min(least,num)
        checks+=len(boxes)
    return [m,r,N,(1<<N)-1,len(boxes),checks,least,den**r]


def layout(m,rng):
    r=9
    n=19*m-7
    C=pool(n)
    loc={c:i for i,c in enumerate(C)}
    A=tuple(c for c in C if cross(c,r,m))
    require(len(A)==sum(comb(r,k)*m**k for k in (1,2,3)),'support count')
    Z=tuple(product(range(m),repeat=r))
    full=(1<<len(Z))-1
    masks=digit_masks(r,m,Z)
    bad={c:forbidden(c,m,masks,full) for c in A}
    D=(m-1).bit_length()+2
    row=[m,0,0,0,0,0,0,0]
    for mode in range(8):
        planted=tuple((i+mode)%m for i in range(r))
        pins=tuple((i+mode)%2 for i in range(m))
        F=fixed(r,m,n,pins)
        B=tuple(c for j,c in enumerate(A) if mode==7 or fixture(c,j,mode,m,planted))
        require(len(set(F+B))==len(F)+len(B),'fixed overlap')
        p=sum(1<<loc[c] for c in F+B)
        raw=encoded(n,p,C)
        require(raw[:n+1]=='1'*n+'0' and len(raw)==n+1+len(C),'header')
        blocked=0
        for c in B:
            blocked|=bad[c]
        models=full^blocked
        row[1]+=1
        row[2]+=models.bit_count()
        boxes=[((1<<m)-1,)*r,(0,)*r]
        if models:
            first=(models&-models).bit_length()-1
            boxes.append(tuple(1<<v for v in Z[first]))
        while len(boxes)<32:
            s=[]
            for g in range(r):
                k=rng(D)
                v=0
                for a in range(m):
                    if rng(1<<k)==0:
                        v|=1<<a
                s.append(v)
            boxes.append(tuple(s))
        for box in boxes:
            units=tuple((-(g*m+a+1),) for g in range(r) for a in range(m)
                        if not box[g]>>a&1)
            delta=sum(not p>>loc[c]&1 for c in units)
            restricted=p
            for c in units:
                restricted|=1<<loc[c]
            require((p&restricted)==p,'monotone selector')
            expected=models
            for g in range(r):
                keep=0
                for a in range(m):
                    if box[g]>>a&1:
                        keep|=masks[g][a]
                expected&=keep
            # Independent reconstruction from actual selected cross clauses.
            selected=tuple(c for c in A if restricted>>loc[c]&1)
            actual_bad=0
            for c in selected:
                actual_bad|=bad[c]
            actual=full^actual_bad
            require(actual==expected,'restriction equivalence')
            if actual:
                i=(actual&-actual).bit_length()-1
                w=witness(r,m,n,pins,Z[i])
                require(valid(C,n,restricted,w) and valid(C,n,p,w),'witness transfer')
            row[3]+=1
            row[4]+=delta
            row[5]+=actual.bit_count()
            row[6]+=actual.bit_count()==1
            row[7]+=bool(actual)
    return row


def audit():
    seed=39218
    def rng(n):
        nonlocal seed
        seed=(1664525*seed+1013904223)&0xffffffff
        return seed%n
    probs=[probability(m,r) for m,r in ((2,1),(2,2),(2,3),(3,1),(3,2))]
    counts=[p[:6] for p in probs]
    require(counts==[[2,1,2,3,4,12],[2,2,4,15,16,240],
                     [2,3,8,255,64,16320],[3,1,3,7,8,56],
                     [3,2,9,511,64,32704]],'JS probability counts')
    layouts=[layout(m,rng) for m in (2,3)]
    require(layouts==[[2,8,516,256,1560,573,11,16],
                      [3,8,19688,256,1869,34598,6,66]],'JS restriction counts')
    result={'probability_counts':counts,'layouts':layouts}
    print('F038_UNRESTRICTED_PRODUCT_ISOLATION_OK '+
          json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit()
