"""Static monomial-multiple GF(2) relaxation audit, not PC closure.

Use square-free Boolean monomials (x^2=x). Enumerate all products
m*p of each original clause polynomial p by monomials m of degree
at most d; retain products of reduced degree <= d. Row-reduce their
coefficient vectors exactly over GF(2). The constant monomial is
fixed to one. A span containing 1 certifies UNSAT.
"""
from itertools import combinations, product

def php():
    f = [tuple((3*i+j+1, True) for j in range(3)) for i in range(4)]
    f += [((3*i+j+1, False), (3*k+j+1, False))
          for j in range(3) for i,k in combinations(range(4),2)]
    return f

def polynomial(c):
    p={0}
    for v,b in c:
        q=set()
        for a in p:
            q.symmetric_difference_update({a | (1 << (v-1))})
            if b:
                q.symmetric_difference_update({a})
        p=q
    return p

def span_test(f,n,d):
    mons=[sum(1<<v for v in vs) for j in range(d+1)
          for vs in combinations(range(n),j)]
    index={m:i for i,m in enumerate(mons)}
    basis={}
    rows=0
    for c in f:
        p=polynomial(c)
        for m in mons:
            q=set()
            for a in p:
                q.symmetric_difference_update({a|m})
            if any(t.bit_count()>d for t in q):
                continue
            r=sum(1<<index[t] for t in q)
            rows+=1
            while r:
                if r==1:
                    return len(mons),rows,len(basis),True
                k=r.bit_length()-1
                if k not in basis:
                    basis[k]=r
                    break
                r^=basis[k]
    return len(mons),rows,len(basis),False

def satisfiable(f,n):
    return any(all(any(bits[v-1]==b for v,b in c) for c in f)
               for bits in product((False,True),repeat=n))

if __name__=="__main__":
    f=php()
    assert len(f)==22 and not satisfiable(f,12)
    expected={2:(79,204,18,False),3:(299,1472,178,False),
              4:(794,6224,709,False),5:(1586,17672,1581,False),
              6:(2510,34945,2508,True)}
    for d,e in expected.items():
        actual=span_test(f,12,d)
        assert actual==e,(d,actual,e)
        print(d,*actual)
    print("F035_STATIC_LIFT_AUDIT_OK assignments=4096 degrees=5 first_refutation_degree=6")
