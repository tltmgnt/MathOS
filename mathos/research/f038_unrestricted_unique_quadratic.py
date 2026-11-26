"""Unique-model exact quadratic residual census, finite combinatorial regression."""
import json
from fractions import Fraction
from itertools import combinations,product
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_crossing_adversary import onehot,true,norm
from mathos.research.f038_unrestricted_quadratic_stage import weight_bound

PLAN='docs/research/tga-universal/f038-unrestricted-unique-quadratic.json'


def rectangles():
    rows=[]
    for m in range(4):
        N=1<<m
        K=1<<N
        st=[m,K*K,0,0,0]
        for a in range(K):
            A=[x for x in range(N) if a>>x&1]
            for b in range(K):
                B=[y for y in range(N) if b>>y&1]
                if any((x&y).bit_count()==1 for x in A for y in B):
                    continue
                count=sum(not (x&y) for x in A for y in B)
                require(count<=N,'singleton-free rectangle')
                st[2]+=1
                st[3]=max(st[3],count)
                st[4]+=count
        rows.append(st)
    return rows


def layout():
    rows=[]
    for m in (2,3):
        n=10*m+3
        X=[tuple(range((k+1)*m+1,(k+2)*m+1)) for k in range(3)]
        Y=[tuple(range(4*m+k*(m-1)+1,4*m+(k+1)*(m-1)+1)) for k in range(3)]
        Z=[tuple(range((7+k)*m+1,(8+k)*m+1)) for k in range(3)]
        F=[]
        used=set()
        for x,y,z in zip(X,Y,Z):
            F.extend(onehot(x,y))
            for a,b in zip(x,z):
                F.extend(((-a,b),(a,-b)))
            used.update(x+y+z)
        p=10*m+1
        used.add(p)
        F.extend((p,a,b) for a,b in product((1-n,n-1),(-n,n)))
        F.extend((-i,) for i in range(1,n+1) if i not in used)
        F=tuple(map(norm,F))
        C=pool(n)
        I={c:j+n+1 for j,c in enumerate(C)}
        L=n+1+len(C)
        P=L-8*comb(n-m,3)
        E=L-8*comb(n-2*m,3)
        Q=L-8*comb(n-7*m,3)
        J=tuple(product(range(m),repeat=3))
        A=tuple(tuple(-X[k][j[k]] for k in range(3)) for j in J)
        B=tuple(tuple(-Z[k][j[k]] for k in range(3)) for j in J)
        require(len(set(F+A+B))==len(F+A+B) and all(c in I for c in F+A+B),
                'clause positions')
        require(all(P<=I[c]<E for c in A) and all(I[c]>=Q for c in B)
                and all(I[c]>=Q for c in F if p in c),'cut geometry')
        W=[]
        for j in J:
            ones=[p]
            for k,i in enumerate(j):
                ones.extend((X[k][i],Z[k][i]))
                ones.extend(y for l,y in enumerate(Y[k]) if i<=l+1)
            W.append(sum(1<<(i-1) for i in ones))
        tests=0
        for i,w in enumerate(W):
            require(all(true(c,w) for c in F),'fixed model')
            for j in range(len(J)):
                require(true(A[j],w)==(i!=j) and true(B[j],w)==(i!=j),
                        'index predicates')
                tests+=2
        # Exhaust the one-hot and auxiliary truth table in local coordinates.
        H=onehot(tuple(range(1,m+1)),tuple(range(m+1,2*m)))
        for x in range(1<<m):
            require(sum(all(true(c,x|(y<<m)) for c in H) for y in range(1<<(m-1)))
                    ==int(x.bit_count()==1),'unique auxiliary extension')
        require(len(set(W))==m**3 and len(used)==9*m-2,'used variable count')
        rows.append([m,n,len(J),len(F),len(W),tests])
    return rows


def controls():
    C=Fraction(3*1000*(81**3-31**3),4*101**6)
    require(C==Fraction(1504950000,4246080602404) and
            weight_bound()<Fraction(1,5000) and Fraction(1,5000)/C<Fraction(57,100),
            'weighted crossing slack')
    require(2**79<3**50 and Fraction(29,50)>Fraction(1,2),'rectangle exponent')
    require(Fraction(3000,8*101**3)>Fraction(1,3000),'length exponent')
    return 3


def audit():
    result={'controls':controls(),'layout':layout(),'rectangles':rectangles()}
    print('F038_UNRESTRICTED_UNIQUE_QUADRATIC_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
