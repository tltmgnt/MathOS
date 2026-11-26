"""Layered cyclic-mask graph census and original normalized layout regression."""
import json
from itertools import combinations, product
from math import comb, factorial
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_unrestricted_crossing_adversary import norm, true
from mathos.research.f038_unrestricted_universal_search import encoded, valid
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed, witness


def largest(m,X,Y):
    """Allowed BC edges that do not close any AB-AC path."""
    Z=0
    for b,c in product(range(m),repeat=2):
        if not any((X>>(a*m+b)&1) and (Y>>(a*m+c)&1) for a in range(m)):
            Z|=1<<(b*m+c)
    return Z


def transpose(m,X):
    return sum(((X>>(a*m+b))&1)<<(b*m+a) for a,b in product(range(m),repeat=2))


def maximal(m,X,Y,Z):
    return (Z==largest(m,X,Y) and
            Y==largest(m,transpose(m,X),Z) and
            X==largest(m,transpose(m,Y),transpose(m,Z)))


def rejected(m,X,Y,Z):
    return not (Z&~largest(m,X,Y))


def census(m):
    N=1<<(m*m)
    full=N-1
    # Precompute the unique maximal-compatible third edge mask.
    table=[[largest(m,X,Y) for Y in range(N)] for X in range(N)]
    tr=[transpose(m,X) for X in range(N)]
    maxima=[]
    total=matching=incomparable=0
    by_size=[0]*(3*m*m+1)
    for X in range(N):
        cols=[tr[X]>>(b*m)&((1<<m)-1) for b in range(m)]
        incomparable+=all(cols[b]&~cols[c] for b,c in product(range(m),repeat=2) if b!=c)
        for Y in range(N):
            Z=table[X][Y]
            total+=1<<Z.bit_count()
            if Y!=table[tr[X]][Z] or X!=table[tr[Y]][tr[Z]]:
                continue
            maxima.append((X,Y,Z))
            by_size[X.bit_count()+Y.bit_count()+Z.bit_count()]+=1
            matching+=all((Z>>(b*m)&((1<<m)-1)).bit_count()==1 and
                          (tr[Z]>>(b*m)&((1<<m)-1)).bit_count()==1
                          for b in range(m))
    require(matching==factorial(m)*incomparable,'matching characterization')
    if m<=2:
        direct=0
        for X,Y,Z in product(range(N),repeat=3):
            tri=any((X>>(a*m+b)&1) and (Y>>(a*m+c)&1) and (Z>>(b*m+c)&1)
                    for a,b,c in product(range(m),repeat=3))
            require((not tri)==rejected(m,X,Y,Z),'direct triangle predicate')
            if not tri:
                direct+=1
                require(any(not (X&~U or Y&~V or Z&~W) for U,V,W in maxima),
                        'maximal downward box cover')
        require(direct==total,'triangle-free count')
        for (X,Y,Z),(U,V,W) in combinations(maxima,2):
            require(not (rejected(m,X,V,W) and rejected(m,U,Y,Z) and
                         rejected(m,X,Y,W) and rejected(m,U,V,Z)),
                    'simultaneous-cut fooling set')
        # One-cut complementary fooling sets with a fixed identity matching.
        I=sum(1<<(i*m+i) for i in range(m))
        for S,T in combinations(range(N),2):
            require(rejected(m,S,full^S,I) and rejected(m,T,full^T,I),
                    'left complementary rejection')
            require(not (rejected(m,S,full^T,I) and rejected(m,T,full^S,I)),
                    'left cut fooling set')
            require(rejected(m,I,full^S,S) and rejected(m,I,full^T,T),
                    'right complementary rejection')
            require(not (rejected(m,I,full^S,T) and rejected(m,I,full^T,S)),
                    'right cut fooling set')
    return [m,total,len(maxima),matching,incomparable,by_size]


def allowed(mode,g,j,d,a,b):
    if mode==0:
        return True
    if mode==1:
        return g!=0
    if mode==2:
        return d==a==b==0
    if mode==3:
        return a==b
    if mode==4:
        return a==b if g==2 else a<=b if g==0 else a>b
    if mode==5:
        return (j*19+g*13+7)%23<11
    if mode==6:
        return (j*17+g*7+3)%31<26
    return a!=b if g==0 else a==b if g==1 else True


def layout(m):
    n=19*m-7
    C=pool(n)
    L=n+1+len(C)
    require(L==n+1+2*n*n+8*comb(n,3),'selector size')
    loc={c:i for i,c in enumerate(C)}
    F=fixed(9,m,n,(0,)*m)+tuple(
        norm((-(g*m+a+1),-(h*m+b+1)))
        for g,h in ((0,3),(0,6),(1,4),(2,7),(5,8))
        for a,b in product(range(m),repeat=2) if a!=b)
    D=tuple(product(range(m),repeat=3))
    A=tuple(tuple(tuple(-((3*g+i)*m+v+1) for i,v in enumerate(d))
                  for d in D) for g in range(3))
    cuts=(0,L-8*comb(n-3*m,3),L-8*comb(n-6*m,3),L)
    require(len(set(F+sum(A,())))==len(F)+3*m**3,'fixed/mask disjoint')
    for g in range(3):
        require(all(cuts[g]<=n+1+loc[c]<cuts[g+1] for c in A[g]),'physical cut')
        require(list(map(loc.get,A[g]))==sorted(map(loc.get,A[g])),'stream order')
    row=[m,L,0,0,0,0,0,0,0,0]
    for mode in range(8):
        masks=tuple(tuple(allowed(mode,g,j,*d) for j,d in enumerate(D))
                    for g in range(3))
        B=tuple(c for g in range(3) for c,b in zip(A[g],masks[g]) if not b)
        p=sum(1<<loc[c] for c in F+B)
        raw=encoded(n,p,C)
        require(raw[:n+1]=='1'*n+'0' and len(raw)==L,'normalized input')
        require(tuple(tuple(raw[n+1+loc[c]]=='0' for c in A[g])
                      for g in range(3))==masks,'extraction')
        ix=lambda d,a,b:(d*m+a)*m+b
        expected={(d,a,b,d,a,c,d,b,c) for d,a,b,c in product(range(m),repeat=4)
                  if masks[0][ix(d,a,b)] and masks[1][ix(d,a,c)] and masks[2][ix(d,b,c)]}
        count=0
        first=None
        for z in product(range(m),repeat=9):
            w=witness(9,m,n,(0,)*m,z)
            ok=all(true(c,w) for c in F+B)
            require(ok==(z in expected),'full clause truth vs triangle')
            row[3]+=1
            if ok:
                count+=1
                if first is None:
                    first=w
        require(count==len(expected),'model count')
        if first is not None:
            require(valid(C,n,p,first),'original verifier')
        row[2]+=1
        row[4]+=m**4
        row[5]+=count
        row[6]+=count>0
        row[7]+=count==1
        row[8]+=len(F)
        row[9]+=len(B)
    return row


def audit():
    graphs=[census(m) for m in (1,2,3)]
    require(graphs==[
        [1,7,3,2,2,[0,0,3,0]],
        [2,1699,49,4,2,[0,0,0,0,0,0,4,36,9,0,0,0,0]],
        [3,10347433,6825,72,12,[0,0,0,0,0,0,0,0,0,0,0,0,135,1296,2700,1620,1026,27,21,0,0,0,0,0,0,0,0,0]]
    ],'independent JS graph counts')
    layouts=[layout(m) for m in (2,3)]
    require(layouts==[[2,37914,8,4096,128,35,6,1,520,77],
                      [3,161851,8,157464,648,162,6,1,1072,286]],
            'independent JS layout counts')
    result={'graphs':graphs,'layouts':layouts}
    print('F038_UNRESTRICTED_CYCLIC_SEMANTIC_BOXES_OK '+
          json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit()
