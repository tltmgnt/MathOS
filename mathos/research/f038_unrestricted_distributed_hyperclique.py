"""Reference checks of distributed forbidden projections, not compiled U code."""
import json
from itertools import product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_unrestricted_crossing_adversary import onehot, norm, true
from mathos.research.f038_unrestricted_universal_search import encoded, valid
from mathos.research.f038_universal_witness_layout import pool


def group(x,m):
    return (x-1)//m


def digit(x,m):
    return (x-1)%m


def cross(c,r,m):
    return all(-r*m<=x<0 for x in c) and len({group(-x,m) for x in c})==len(c)


def fixed(r,m,n,pins):
    F=[]
    for g in range(r):
        X=tuple(g*m+j+1 for j in range(m))
        Y=tuple(r*m+g*(m-1)+i+1 for i in range(m-1))
        F.extend(onehot(X,Y))
    F.extend(((1-n,),(-n,)))
    for i,b in enumerate(pins):
        p=n-m-1+i
        F.extend((p if b else -p,a,z) for a,z in product((1-n,n-1),(-n,n)))
    return tuple(map(norm,F))


def witness(r,m,n,pins,a):
    ones=[n-m-1+i for i,b in enumerate(pins) if b]
    for g,j in enumerate(a):
        ones.append(g*m+j+1)
        ones.extend(r*m+g*(m-1)+i+1 for i in range(m-1) if j<=i+1)
    return sum(1<<(v-1) for v in ones)


def fixture(c,j,mode,m,planted):
    G=tuple(group(-x,m) for x in c)
    D=tuple(digit(-x,m) for x in c)
    if mode==0:
        return False
    if mode==1:
        return len(c)==1 and G[0]==0
    if mode==2:
        return len(c)==1 and D[0]!=planted[G[0]]
    if mode==3:
        return len(c)==2 and G[1]==G[0]+1 and D[0]!=D[1]
    if mode==4:
        return (j*17+13)%31<3
    if mode==5:
        return len(c)==3 and (j*19+7)%23<7
    return len(c)==3 and any(d!=planted[g] for g,d in zip(G,D))


def expand(B,r,m,p):
    # Direct completion generation, not a scan of all suffixes for each clause.
    records=[]
    for c in B:
        D={group(-x,m):digit(-x,m) for x in c}
        if any(p[g]!=d for g,d in D.items() if g<r-3):
            continue
        choices=[(D[g],) if g in D else range(m) for g in range(r-3,r)]
        records.extend((a*m+b)*m+c for a,b,c in product(*choices))
    require(len(records)<=sum(comb(r,k) for k in (1,2,3))*m**3,'workspace bound')
    records.sort()
    missing=0
    for j in records:
        if j>missing:
            break
        if j==missing:
            missing+=1
    return records, missing if missing<m**3 else None


def layout(r,m):
    n=(2*r+1)*m-r+2
    C=pool(n)
    L=n+1+len(C)
    require(L==n+1+2*n*n+8*comb(n,3),'length')
    pos={c:i for i,c in enumerate(C)}
    A=tuple(c for c in C if cross(c,r,m))
    require(len(A)==sum(comb(r,k)*m**k for k in (1,2,3)),'cross count')
    fixtures=sat=unique=candidates=prefixes=records=models=0
    for mode in range(7):
        pins=tuple((i+mode)%2 for i in range(m))
        planted=tuple((i+mode)%m for i in range(r))
        F=fixed(r,m,n,pins)
        B=tuple(c for j,c in enumerate(A) if fixture(c,j,mode,m,planted))
        require(len(set(F+B))==len(F)+len(B),'fixed/cross overlap')
        mask=sum(1<<pos[c] for c in F+B)
        raw=encoded(n,mask,C)
        require(raw[:n+1]=='1'*n+'0' and len(raw)==L,'raw encoding')
        extracted=tuple(c for c,b in zip(C,raw[n+1:]) if b=='1' and cross(c,r,m))
        recovered=tuple(int(b) for c,b in zip(C,raw[n+1:]) if len(c)==3
                        and n-m-1<=c[0]<=n-2 and c[1:]==(1-n,-n))
        require(extracted==B and recovered==pins,'normalized extraction')
        count=0
        first=None
        for p in product(range(m),repeat=r-3):
            stream,gap=expand(extracted,r,m,p)
            blocked=set(stream)
            expected_gap=None
            prefixes+=1
            records+=len(stream)
            for j,s in enumerate(product(range(m),repeat=3)):
                a=p+s
                expected=not any(all(a[group(-x,m)]==digit(-x,m) for x in c) for c in B)
                require(expected==(j not in blocked),'prefix projection')
                w=witness(r,m,n,pins,a)
                require(all(true(c,w) for c in F),'fixed extension')
                require(all(true(c,w) for c in B)==expected,'actual clause truth')
                candidates+=1
                if expected:
                    count+=1
                    if expected_gap is None:
                        expected_gap=j
                    if first is None:
                        first=w
            require(gap==expected_gap,'sorted gap')
        require((first is not None)==bool(count),'first witness')
        if first is not None:
            require(valid(C,n,mask,first),'original verifier')
        fixtures+=1
        sat+=bool(count)
        unique+=count==1
        models+=count
    return [r,m,n,L,fixtures,sat,unique,candidates,prefixes,records,models]


EXPECTED=[[3,2,13,2640,7,6,2,56,7,45,19],
          [3,3,20,9941,7,6,2,189,7,171,62],
          [4,2,16,5009,7,6,3,112,14,168,25],
          [4,3,25,19676,7,6,2,567,21,978,124],
          [5,2,19,8494,7,5,3,224,28,636,37],
          [5,3,30,34311,7,6,2,1701,63,5391,262],
          [6,2,22,13311,7,4,2,448,56,2184,68],
          [6,3,35,54846,7,6,2,5103,189,27486,741]]


def audit():
    rows=[layout(r,m) for r in range(3,7) for m in (2,3)]
    require(rows==EXPECTED,'independent reference totals')
    require([sum(row[i] for row in rows) for i in (4,5,6,7,8,9,10)]
            ==[56,45,18,8400,385,37059,1338],'aggregate counts')
    require(comb(6,3)==20 and all(r+3<9 for r in (3,4,5)) and 6+3==9,'stage slack')
    print('F038_UNRESTRICTED_DISTRIBUTED_HYPERCLIQUE_OK '+json.dumps(rows,separators=(',',':')))
    return rows


if __name__=='__main__':
    audit()
