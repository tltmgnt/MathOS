"""Reference checks of mobile projection semantics and abstract track shifts."""
import json
from itertools import product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_unrestricted_crossing_adversary import true
from mathos.research.f038_unrestricted_universal_search import encoded, valid
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import (
    group, digit, cross, fixed, witness, fixture)


def pure(c,r,m):
    return len(c)==3 and cross(c,r,m) and all(group(-x,m)>=r-3 for x in c)


def capacity(r,m):
    d=r-3
    return sum(comb(3,h)*m**h*sum(comb(d,k) for k in range(min(d,3-h)+1))
               for h in range(3))-1


def project(B,r,m,p):
    records=[]
    for c in B:
        if pure(c,r,m):
            continue
        pairs=tuple((group(-x,m),digit(-x,m)) for x in c)
        if any(g<r-3 and p[g]!=d for g,d in pairs):
            continue
        records.append(tuple((g-r+3,d) for g,d in pairs if g>=r-3))
    require(len(records)<=capacity(r,m),'quadratic record bound')
    return records


def layout(r,m):
    n=(2*r+1)*m-r+2
    C=pool(n)
    L=n+1+len(C)
    pos={c:i for i,c in enumerate(C)}
    A=tuple(c for c in C if cross(c,r,m))
    suffix=tuple(product(range(m),repeat=3))
    pure_pos=tuple(i for i,c in enumerate(C) if pure(c,r,m))
    require(pure_pos==tuple(pos[tuple(-((r-3+h)*m+d+1) for h,d in enumerate(z))]
                            for z in suffix),'pure positions/order')
    fixtures=sat=unique=tests=prefixes=records=maximum=models=0
    for mode in range(8):
        pins=tuple((i+mode)%2 for i in range(m))
        planted=tuple((i+mode)%m for i in range(r))
        F=fixed(r,m,n,pins)
        B=tuple(c for j,c in enumerate(A) if mode==7 or fixture(c,j,mode,m,planted))
        require(len(set(F+B))==len(F)+len(B),'fixed/cross overlap')
        mask=sum(1<<pos[c] for c in F+B)
        raw=encoded(n,mask,C)
        require(raw[:n+1]=='1'*n+'0' and len(raw)==L,'raw input')
        bits=raw[n+1:]
        selected=tuple(c for c,b in zip(C,bits) if b=='1' and cross(c,r,m))
        require(selected==B,'normalized projection input')
        recovered=tuple(int(b) for c,b in zip(C,bits) if len(c)==3
                        and n-m-1<=c[0]<=n-2 and c[1:]==(1-n,-n))
        require(recovered==pins,'pins')
        count=0
        first=None
        for p in product(range(m),repeat=r-3):
            R=project(selected,r,m,p)
            if mode==7:
                require(len(R)==capacity(r,m),'dense fixture attains bound')
            prefixes+=1
            records+=len(R)
            maximum=max(maximum,len(R))
            for i,z in enumerate(suffix):
                ok=bits[pure_pos[i]]=='0' and not any(
                    all(z[g]==d for g,d in q) for q in R)
                w=witness(r,m,n,pins,p+z)
                require(all(true(c,w) for c in F),'fixed extension')
                require(ok==all(true(c,w) for c in B),'projection iff clause truth')
                tests+=1
                if ok:
                    count+=1
                    if first is None:
                        first=w
        require((first is not None)==bool(count),'witness exists')
        if first is not None:
            require(valid(C,n,mask,first),'original verifier')
        fixtures+=1
        sat+=bool(count)
        unique+=count==1
        models+=count
    require(maximum==capacity(r,m),'maximum capacity')
    return [r,m,n,L,fixtures,sat,unique,tests,prefixes,records,maximum,models]


def carry_shift(tape,indices):
    # Abstract product symbols; the first component is the stationary input.
    carry=-1
    for i in indices:
        a,b=tape[i]
        tape[i]=(a,carry)
        carry=b
    require(carry==-1,'outside work interval is blank')


def shifts():
    count=0
    for length in range(1,5):
        for source in range(16):
            inp=[source>>i&1 if i<4 else 2 for i in range(10)]
            for w in product(range(3),repeat=length):
                for a in range(1,5):
                    tape=[(v,-1) for v in inp]
                    for i,v in enumerate(w,a):
                        tape[i]=(inp[i],v)
                    old=tape[:]
                    carry_shift(tape,range(a,a+length+1))
                    require([v for v,_ in tape]==inp,'stationary input on right shift')
                    require([b for _,b in tape]==[-1]*(a+1)+list(w)+[-1]*(9-a-length),
                            'right shift')
                    carry_shift(tape,range(a+length,a-1,-1))
                    require(tape==old,'inverse left shift and stationary input')
                    count+=2
    require(count==15360,'shift count')
    return count


EXPECTED=[[3,2,13,2640,8,6,2,64,8,29,18,19],
          [3,3,20,9941,8,6,2,216,8,61,36,62],
          [4,2,16,5009,8,6,3,128,16,129,37,25],
          [4,3,25,19676,8,6,2,648,24,408,73,124],
          [5,2,19,8494,8,5,3,256,32,458,63,37],
          [5,3,30,34311,8,6,2,1944,72,2111,120,262],
          [6,2,22,13311,8,4,2,512,64,1461,97,68],
          [6,3,35,54846,8,6,2,5832,216,9670,178,741],
          [7,2,25,19676,8,4,2,1024,128,4332,140,132],
          [7,3,40,82281,8,5,2,17496,648,41193,248,2197]]


def audit():
    rows=[layout(r,m) for r in range(3,8) for m in (2,3)]
    require(rows==EXPECTED,'independent reference rows')
    require([sum(row[i] for row in rows) for i in (4,5,6,7,8,9,11)]
            ==[80,54,22,28120,1216,59852,3667],'aggregate counts')
    require(max(row[10] for row in rows)==248,'maximum records')
    require(all(max(6,r+2)<9 for r in range(3,7)) and 7+2==9,'clock slack')
    result={'rows':rows,'shifts':shifts()}
    print('F038_UNRESTRICTED_MOBILE_PROJECTION_OK '+json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit()
