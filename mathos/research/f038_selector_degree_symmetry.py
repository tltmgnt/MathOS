"""Selector polynomial degree via symmetry; finite coefficient and gate audits."""
import json
from itertools import combinations,product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research import f038_circuit_range_avoidance as A

PLAN='docs/research/tga-universal/f038-mrax-selector-degree-symmetry.json'


def mobius(values,n,p=2):
    require(len(values)==1<<n and p>=2,'bad transform dimensions')
    a=list(values)
    for j in range(n):
        for i in range(1<<n):
            if i>>j&1:
                a[i]=(a[i]-a[i^(1<<j)])%p
    return tuple(a)


def degree(a):
    return max((i.bit_count() for i,v in enumerate(a) if v),default=0)


def falsified(C,x):
    return sum(1<<i for i,c in enumerate(C) if not any(
        bool(x>>(abs(l)-1)&1)==(l>0) for l in c))


def union_polynomial(F):
    seen=set()
    odd=set()
    # Enumerate nonempty subsets of assignment acceptance monomials.
    for mask in range(1,1<<len(F)):
        u=0
        for i,a in enumerate(F):
            if mask>>i&1:
                u|=a
        seen.add(u)
        if u in odd:
            odd.remove(u)
        else:
            odd.add(u)
    return seen,odd


def polynomials():
    out=[]
    for n in (1,2,3,4):
        C=pool(n)
        N=len(C)
        F=tuple(falsified(C,x) for x in range(1<<n))
        seen,odd=union_polynomial(F)
        top=(1<<N)-1
        d=max(u.bit_count() for u in odd)
        require(top in odd and d==N,'full degree failed')
        if n<=2:
            # q variables are complements of selectors.
            table=tuple(int(any(a&q==a for a in F)) for q in range(1<<N))
            coeff=mobius(table,N)
            require({i for i,b in enumerate(coeff) if b}==odd,'union formula mismatch')
            orig=tuple(int(any(not(a&s) for a in F)) for s in range(1<<N))
            require(mobius(orig,N)[-1]==1,'original selector coefficient mismatch')
        # Check translations of assignments and induced sign permutations.
        index={c:i for i,c in enumerate(C)}
        for g in range(1<<n):
            perm=tuple(index[tuple(-l if g>>(abs(l)-1)&1 else l for l in c)] for c in C)
            require(len(set(perm))==N,'translation not bijective')
            for x,a in enumerate(F):
                b=sum(1<<perm[i] for i in range(N) if a>>i&1)
                require(b==F[x^g],'translation did not preserve falsification')
        out.append([n,N,(1<<len(F))-1,len(seen),len(odd),d,int(top in odd)])
    return out


def prime_pool(p,n,k):
    return tuple((I,a) for r in range(1,min(n,k)+1)
                 for I in combinations(range(n),r) for a in product(range(p),repeat=r))


def prime_audit():
    out=[]
    for p,n,k in ((2,1,1),(2,2,2),(3,1,1),(3,2,2),(5,1,1)):
        C=prime_pool(p,n,k)
        N=len(C)
        W=tuple(product(range(p),repeat=n))
        index=set(C)
        for g in W:
            require(all((I,tuple((a[j]+g[i])%p for j,i in enumerate(I))) in index
                        for I,a in C),'translation pool not closed')
        F=tuple(sum(1<<i for i,(I,a) in enumerate(C) if tuple(x[j] for j in I)==a)
                for x in W)
        table=tuple(int(any(not(s&a) for a in F)) for s in range(1<<N))
        coeff=mobius(table,N,p)[-1]
        signed=sum(v*(-1 if (N-s.bit_count())%2 else 1) for s,v in enumerate(table))%p
        require(coeff==signed==(-1)**N%p,'prime full coefficient failed')
        out.append([p,n,k,N,1<<N,(1<<N)*len(W),sum(table),coeff])
    return out


def circuits():
    out=[]
    for n,s in ((2,0),(2,1),(3,1),(3,2),(4,1)):
        m=1<<n
        R=A.available(n,s,m)
        hist=[0]*(n+1)
        for v in R:
            d=degree(mobius(tuple(v>>i&1 for i in range(m)),n))
            require(d<=s+1,'binary gate degree bound failed')
            hist[d]+=1
        out.append([n,s,len(R),hist])
    return out


def controls():
    # Maximal degree for AND on n inputs using n-1 gates.
    for n in range(1,9):
        a=mobius(tuple(int(i==(1<<n)-1) for i in range(1<<n)),n)
        require(degree(a)==n and sum(a)==1,'AND degree failed')
    # Asymmetric positive units are always jointly satisfiable; degree zero.
    require(degree(mobius((1,1,1,1),2))==0,'asymmetric control failed')
    # Contradictory sign-invariant unit pair has full coefficient.
    require(mobius((1,1,1,0),2)==(1,0,0,1),'unit pair coefficient failed')
    try:
        mobius((1,0,1),2)
    except ValueError:
        pass
    else:
        raise ValueError('malformed table accepted')
    return 4


def audit():
    result={'polynomials':polynomials(),'prime':prime_audit(),'circuits':circuits(),'controls':controls()}
    print('F038_MRAX_SELECTOR_DEGREE_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
