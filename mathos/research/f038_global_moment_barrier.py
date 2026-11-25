"""F038: exact global low-order violation moments are not a universal
SAT invariant, even with all but the highest moment supplied by an oracle.

The tested score is deterministic and polynomial for fixed order.
The independent histogram enumerator is a finite fixture oracle only.
"""
from itertools import combinations, product
from math import comb
from mathos.research.f037_log_backdoor import normalize, restrict, satisfies


def variables(f):
    return tuple(sorted({abs(l) for c in f for l in c}))


def signature(f, vs, r):
    """M_j = sum_x binom(number of violated clauses on x, j).

    Compute by summing exact falsifying-subcube intersection sizes.
    Keep clause occurrences, including duplicate clauses.
    """
    n=len(vs)
    assert set(variables(f))<=set(vs) and len(set(vs))==n
    out=[]
    for j in range(r+1):
        total=0
        for rows in combinations(f,j):
            bits={}
            ok=True
            for c in rows:
                for l in c:
                    v,b=abs(l),l<0
                    if v in bits and bits[v]!=b:
                        ok=False
                        break
                    bits[v]=b
                if not ok:
                    break
            if ok:
                total+=1<<(n-len(bits))
        out.append(total)
    return tuple(out)


def score(s):
    return sum((-1)**j*m for j,m in enumerate(s))


def choose(f,v,r):
    vs=tuple(w for w in variables(f) if w!=v)
    a=signature(restrict(f,{v:False}),vs,r)
    b=signature(restrict(f,{v:True}),vs,r)
    return score(b)>score(a),a,b


def switch_formula(p,good):
    """Connected cubic prism with one subdivided edge and selector stub.

    Edge variables begin at 2; variable 1 is the designated selector.
    Every vertex imposes one parity equation of width three.
    """
    assert p>=3
    edges=[(i,(i+1)%p) for i in range(p)]
    edges.extend((p+i,p+(i+1)%p) for i in range(p))
    edges.extend((i,p+i) for i in range(p))
    u,v=edges.pop(0)
    root=2*p
    edges.extend(((u,root),(root,v)))
    n=2*p+1
    inc=[[] for _ in range(n)]
    for i,(u,v) in enumerate(edges,2):
        inc[u].append(i)
        inc[v].append(i)
    inc[root].append(1)
    f=[]
    for u,s in enumerate(inc):
        assert len(s)==3
        charge=int(good and u==root)
        for bits in product((False,True),repeat=3):
            if sum(bits)%2!=charge:
                f.append(tuple(-v if b else v for v,b in zip(s,bits)))
    w={v:False for v in range(1,len(edges)+2)}
    w[1]=good
    f=normalize(f)
    assert satisfies(f,w)
    return f,w,n,tuple(edges)


def histogram_formula(f,vs,n):
    # Enumerate original clause truth values independently of the
    # parity system. Intended only for small bounded tests.
    pos={v:1<<i for i,v in enumerate(vs)}
    rows=[]
    for c in f:
        a=sum(pos[l] for l in c if l>0)
        b=sum(pos[-l] for l in c if l<0)
        rows.append((a,b))
    hist=[0]*(n+1)
    for x in range(1<<len(vs)):
        j=sum((x&a)==0 and (x&b)==b for a,b in rows)
        hist[j]+=1
    return tuple(hist)


def histogram_syndrome(n,edges,odd):
    # Each edge column toggles precisely its two endpoints.
    columns=[(1<<u)|(1<<v) for u,v in edges]
    hist=[0]*(n+1)
    # The root charge is flipped on the wrong selector branch.
    for a in range(1<<len(edges)):
        s=(1<<(n-1)) if odd else 0
        for i,c in enumerate(columns):
            if a&(1<<i):
                s^=c
        hist[s.bit_count()]+=1
    return tuple(hist)


def moments(hist,r):
    return tuple(sum(count*comb(j,k) for j,count in enumerate(hist) if j>=k)
                 for k in range(r+1))


def audit():
    exact=0
    direct=0
    for p in (3,4,5,6):
        for good in (False,True):
            f,w,n,edges=switch_formula(p,good)
            vs=tuple(range(2,len(edges)+2))
            hs=[]
            for b in (False,True):
                g=restrict(f,{1:b})
                odd=b!=good
                scale=1<<(len(edges)-n+1)
                predicted=tuple(scale*comb(n,j) if j%2==odd else 0
                                for j in range(n+1))
                observed=histogram_syndrome(n,edges,odd)
                assert predicted==observed
                if p<=4:
                    assert histogram_formula(g,vs,n)==observed
                    direct+=1
                assert signature(g,vs,3)==moments(observed,3)
                hs.append(observed)
                exact+=1
            assert moments(hs[0],n-1)==moments(hs[1],n-1)
            assert moments(hs[0],n)!=moments(hs[1],n)
            assert (hs[0][0]>0)==(not good)
            assert (hs[1][0]>0)==good
            b,a,c=choose(f,1,3)
            assert a==c and b is False
            assert (b!=good)==good
            print(f"prism={p} correct={good} variables={len(w)} clauses={len(f)} equal_orders=0..{n-1} selected={b}")
    # Empty and tautological rows: all and no assignments violate them.
    assert signature(((),),(1,2),1)==(4,4)
    assert signature(((1,-1),),(1,2),1)==(4,0)
    assert exact==16 and direct==8
    print("F038_GLOBAL_MOMENT_BARRIER_OK formulas=8 branches=16 direct_histograms=8 max_variables=20 maximum_equal_order=12")


if __name__=="__main__":
    audit()
