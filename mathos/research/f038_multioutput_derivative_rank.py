"""Degree-filtered Boolean output rank, derivative batches and exact monomial construction."""
import json
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_selector_degree_symmetry import mobius

PLAN='docs/research/tga-universal/f038-mrax-multioutput-derivative-rank.json'


def rank(rows):
    basis={}
    for v in rows:
        while v:
            j=v.bit_length()-1
            if j in basis:
                v^=basis[j]
            else:
                basis[j]=v
                break
    return len(basis)


def coefficients(n,f):
    require(type(n) is int and n>=1 and type(f) is int and 0<=f<1<<(1<<n),
            'invalid truth table')
    return sum(b<<i for i,b in enumerate(mobius(tuple(f>>j&1 for j in range(1<<n)),n)))


def derivative(n,a,I):
    require(0<=I<1<<n and 0<=a<1<<(1<<n),'invalid derivative')
    v=0
    for J in range(1<<n):
        if J&I==I and a>>J&1:
            v|=1<<(J^I)
    return v


def flip_difference(n,f,i):
    return sum((((f>>x)^(f>>(x^(1<<i))))&1)<<x for x in range(1<<n))


def filtered_rank(n,rows,d):
    require(2<=d<=n,'invalid degree threshold')
    mask=sum(1<<j for j in range(1<<n) if j.bit_count()>=d)
    return rank(v&mask for v in rows)


def lower_bound(n,rows,d):
    r=filtered_rank(n,rows,d)
    return d-2+r if r else 0


def monomials(n):
    # Boolean truth-table words for the free constant, inputs and actual AND DAG.
    N=1<<n
    V={0:(1<<N)-1}
    for i in range(n):
        V[1<<i]=sum(1<<x for x in range(N) if x>>i&1)
    gates=[]
    for J in range(1,N):
        if J.bit_count()<2:
            continue
        b=J&-J
        require(J^b in V and b in V,'missing monomial predecessor')
        V[J]=V[J^b]&V[b]
        gates.append((J,J^b,b))
    require(len(gates)==N-n-1,'monomial gate count failed')
    return V,gates


def affine_output(V,a):
    f=0
    while a:
        b=a&-a
        f^=V[b.bit_length()-1]
        a^=b
    return f


def derivative_batch(n,f):
    N=1<<n
    a=coefficients(n,f)
    require(a>>(N-1)&1,'not full degree')
    D=[derivative(n,a,I) for I in range(N)]
    V,G=monomials(n)
    ref=[f]
    for I in range(1,N):
        b=I&-I
        ref.append(flip_difference(n,ref[I^b],b.bit_length()-1))
    require(rank(D)==N,'derivatives not a basis')
    for I,v in enumerate(D):
        d=n-I.bit_count()
        top={j for j in range(N) if v>>j&1 and j.bit_count()>=d}
        require(top=={(N-1)^I},'wrong leading monomial')
        require(affine_output(V,v)==ref[I],'monomial circuit replay mismatch')
    return D,len(G)


def ranks():
    out=[]
    for n in (2,3,4):
        N=1<<n
        F=[f for f in range(1<<N) if f.bit_count()&1]
        if n==4:
            F=F[:128]+F[-128:]
        st=[n,len(F),0,0,0,0]
        for f in F:
            D,k=derivative_batch(n,f)
            for r in range(n-1):
                d=n-r
                B=[v for I,v in enumerate(D) if I.bit_count()<=r]
                q=filtered_rank(n,B,d)
                require(q==len(B),'filtered rank mismatch')
                st[2]+=1
                st[3]+=q
                st[4]+=lower_bound(n,B,d)
            require(lower_bound(n,[v for I,v in enumerate(D) if I.bit_count()<=n-2],2)==k,
                    'full-batch lower and upper bounds differ')
            st[5]+=k
        out.append(st)
    return out


def products():
    out=[]
    for n in (1,2,3):
        N=1<<n
        F=range(1<<N)
        D=[[flip_difference(n,f,i) for i in range(n)] for f in F]
        st=[n,0,0,0,0,0]
        for a in F:
            for b in F:
                st[1]+=1
                for i in range(n):
                    u,v=D[a][i],D[b][i]
                    d=D[a&b][i]
                    ordinary=(a&v)^(b&u)
                    cross=u&v
                    require(d==ordinary^cross,'finite difference product rule failed')
                    st[2]+=N
                    st[3]+=(d^ordinary).bit_count()
                    st[4]+=cross.bit_count()
                    st[5]+=d.bit_count()
        out.append(st)
    return out


def selector():
    out=[]
    for n in (1,2):
        C=pool(n)
        N=len(C)
        W=1<<N
        maxima=tuple(sum(1<<j for j,c in enumerate(C) if any(
            bool(x>>(abs(l)-1)&1)==(l>0) for l in c)) for x in range(1<<n))
        f=sum(1<<p for p in range(W) if any(p&a==p for a in maxima))
        D,k=derivative_batch(N,f)
        hist=[]
        for r in range(N-1):
            B=[v for I,v in enumerate(D) if I.bit_count()<=r]
            q=filtered_rank(N,B,N-r)
            require(q==len(B),'SAT derivative rank mismatch')
            hist.append(q)
        require(k==W-N-1 and hist[-1]==k,'SAT batch exact bound mismatch')
        out.append([n,N,W,rank(D),hist])
    return out


def controls():
    # AND_N has one highest-degree monomial; its derivatives are all submonomials.
    for n in range(2,7):
        N=1<<n
        D,k=derivative_batch(n,1<<(N-1))
        require(all(v==1<<((N-1)^I) for I,v in enumerate(D)) and k==N-n-1,
                'AND batch failed')
    require(lower_bound(4,[1,2,4,8],4)==0,'zero-rank premise ignored')
    require(flip_difference(1,2&2,0)==3 and ((2&3)^(2&3))==0,
            'ordinary Leibniz counterexample failed')
    try:
        coefficients(2,16)
    except ValueError:
        pass
    else:
        raise ValueError('out-of-range truth table accepted')
    return 4


def audit():
    result={'ranks':ranks(),'products':products(),'selector':selector(),'controls':controls()}
    print('F038_MRAX_DERIVATIVE_RANK_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
