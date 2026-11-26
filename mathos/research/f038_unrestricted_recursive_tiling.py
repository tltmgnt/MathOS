"""Finite domain-tiling and witness-transfer reference; not a compiled U solver."""
import json
from fractions import Fraction
from itertools import product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_unrestricted_universal_search import encoded, valid
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import (
    group, digit, cross, fixed, witness, fixture)


def block_size(r,m):
    b=2
    while b**(r-1)<m**3:
        b+=1
    require(2<=b<=m and (b==2 or (b-1)**(r-1)<m**3),'block size')
    return b


def digit_masks(r,m,tuples):
    masks=[[0]*m for _ in range(r)]
    for j,a in enumerate(tuples):
        bit=1<<j
        for g,d in enumerate(a):
            masks[g][d]|=bit
    return masks


def forbidden(c,m,masks,full):
    result=full
    for x in c:
        result &= masks[group(-x,m)][digit(-x,m)]
    return result


def translate(B,r,m,b,t):
    Q=[]
    for c in B:
        pairs=[(group(-x,m),digit(-x,m)) for x in c]
        z=[(g,d-b*t[g]) for g,d in pairs]
        if all(0<=d<b for g,d in z):
            Q.append(tuple(-(g*b+d+1) for g,d in z))
    padding=[(-(g*b+d+1),) for g in range(r) for d in range(b)
             if b*t[g]+d>=m]
    require(len(Q)<=sum(comb(r,h)*b**h for h in (1,2,3)),'tile space')
    require(len(set(Q+padding))==len(Q)+len(padding),'translation injective')
    return Q,padding


def layout(r,m):
    b=block_size(r,m)
    n=(2*r+1)*m-r+2
    nb=(2*r+1)*b-r+2
    C=pool(n)
    D=pool(nb)
    pos={c:i for i,c in enumerate(C)}
    loc={c:i for i,c in enumerate(D)}
    A=tuple(c for c in C if cross(c,r,m))
    AD=tuple(c for c in D if cross(c,r,b))
    direct=tuple(product(range(m),repeat=r))
    local=tuple(product(range(b),repeat=r))
    full=(1<<len(direct))-1
    full_local=(1<<len(local))-1
    masks=digit_masks(r,m,direct)
    lmasks=digit_masks(r,b,local)
    outer_bad={c:forbidden(c,m,masks,full) for c in A}
    local_bad={c:forbidden(c,b,lmasks,full_local) for c in AD}
    FL=fixed(r,b,nb,(0,)*b)
    base_local=sum(1<<loc[c] for c in FL)
    require(len(set(FL))==len(FL),'local fixed unique')
    tiles=[]
    partition=set()
    for t in product(range((m+b-1)//b),repeat=r):
        mapping=[]
        for z in local:
            a=tuple(d+b*t[g] for g,d in enumerate(z))
            j=-1
            if all(d<m for d in a):
                j=0
                for d in a:
                    j=j*m+d
                require(j not in partition,'disjoint tiles')
                partition.add(j)
            mapping.append(j)
        tiles.append((t,mapping))
    require(len(partition)==len(direct),'tile coverage')
    stats=[r,m,b,0,0,0,0,0,0,0,0]
    for mode in range(8):
        pins=tuple((i+mode)%2 for i in range(m))
        planted=tuple((i+mode)%m for i in range(r))
        F=fixed(r,m,n,pins)
        B=tuple(c for j,c in enumerate(A) if mode==7 or fixture(c,j,mode,m,planted))
        require(len(set(F+B))==len(F)+len(B),'outer fixed/variable overlap')
        selector=sum(1<<pos[c] for c in F+B)
        raw=encoded(n,selector,C)
        require(raw[:n+1]=='1'*n+'0' and len(raw)==n+1+len(C),'outer input')
        selected=tuple(c for c,v in zip(C,raw[n+1:]) if v=='1' and cross(c,r,m))
        recovered=tuple(int(v) for c,v in zip(C,raw[n+1:]) if len(c)==3
                        and n-m-1<=c[0]<=n-2 and c[1:]==(1-n,-n))
        require(selected==B and recovered==pins,'outer selector and pins')
        blocked=0
        for c in B:
            blocked|=outer_bad[c]
        expected=full^blocked
        found=0
        tested_witness=False
        for t,mapping in tiles:
            Q,padding=translate(selected,r,m,b,t)
            P=Q+padding
            require(all(c in loc and c in local_bad for c in P),'local pool positions')
            require(len(set(FL+tuple(P)))==len(FL)+len(P),'local fixed/variable overlap')
            bad=0
            for c in P:
                bad|=local_bad[c]
            allowed=full_local^bad
            # Check every local tuple, including out-of-range padding, against
            # the independently constructed original-domain forbidden bitset.
            for i,j in enumerate(mapping):
                ok=j>=0 and bool(expected>>j&1)
                require(bool(allowed>>i&1)==ok,'tile equivalence')
                if j>=0:
                    stats[6]+=1
                else:
                    stats[9]+=1
                if ok:
                    require(not (found>>j&1),'duplicate model')
                    found|=1<<j
            if allowed and not tested_witness:
                i=(allowed&-allowed).bit_length()-1
                z=local[i]
                a=tuple(d+b*t[g] for g,d in enumerate(z))
                local_selector=base_local+sum(1<<loc[c] for c in P)
                local_raw=encoded(nb,local_selector,D)
                require(local_raw[:nb+1]=='1'*nb+'0' and
                        len(local_raw)==nb+1+len(D),'local normalized header')
                local_selected=tuple(c for c,v in zip(D,local_raw[nb+1:]) if v=='1')
                require(set(local_selected)==set(FL+tuple(P)),'local normalized bits')
                require(valid(D,nb,local_selector,witness(r,b,nb,(0,)*b,z)),
                        'local verifier')
                require(valid(C,n,selector,witness(r,m,n,recovered,a)),
                        'transferred outer witness verifier')
                tested_witness=True
            stats[4]+=1
            stats[5]+=len(mapping)
            stats[7]+=len(Q)
            stats[8]+=len(padding)
        require(found==expected and tested_witness==bool(expected),'model bijection')
        stats[3]+=1
        stats[10]+=found.bit_count()
    return stats


EXPECTED=[[4,2,2,8,8,128,128,119,0,0,25],
          [4,3,3,8,8,648,648,356,0,0,124],
          [5,2,2,8,8,256,256,253,0,0,37],
          [5,3,3,8,8,1944,1944,790,0,0,262],
          [6,2,2,8,8,512,512,462,0,0,68],
          [6,3,2,8,512,32768,5832,14176,1536,26936,741],
          [7,2,2,8,8,1024,1024,767,0,0,132],
          [7,3,2,8,1024,131072,17496,46096,3584,113576,2197],
          [8,2,2,8,8,2048,2048,1184,0,0,260],
          [8,3,2,8,2048,524288,52488,140608,8192,471800,6566],
          [9,2,2,8,8,4096,4096,1734,0,0,516],
          [9,3,2,8,4096,2097152,157464,407936,18432,1939688,19688]]


def controls():
    require(Fraction(7)+Fraction(6,6)==8,'seven-group exponent')
    require((Fraction(8)+Fraction(6,7))/3==Fraction(62,21)<3,'eight-group exponent')
    require(Fraction(9)+Fraction(6,8)>9,'nine-group no slack')
    for r in range(6,11):
        d=Fraction(2)
        for _ in range(12):
            e=r+d
            a=3/(e-3)
            q=r+3-a*(r-3)
            require(q==r+a*d,'balanced extraction and solve')
            new=3*d/(r-3+d)
            require(q==r+new and 0<new<d,'recursive contraction')
            if r==6:
                require(1/new==1/d+Fraction(1,3),'reciprocal recurrence')
            else:
                require(new<=Fraction(3,r-3)*d,'geometric contraction')
            d=new
    return 3


def audit():
    rows=[layout(r,m) for r in range(4,10) for m in (2,3)]
    require(rows==EXPECTED,'independent JS reference rows')
    require([sum(row[i] for row in rows) for i in range(3,11)]
            ==[96,7744,2795936,243936,614481,31744,2552000,30616],'aggregate')
    result={'controls':controls(),'rows':rows}
    print('F038_UNRESTRICTED_RECURSIVE_TILING_OK '+json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit()
