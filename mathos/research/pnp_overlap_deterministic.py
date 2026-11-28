"""Theorem P: deterministic greedy block distance and affine exclusion.

Polynomial-size output and polynomial working storage, exponential worst-case
construction time. No random seed, and no claim of efficient explicit codes.
"""
from itertools import combinations, product
from math import comb
import json
from mathos.research.pnp_overlap_order import insert, annihilator
from mathos.research.pnp_overlap_asymptotic import check_obstruction

def conditions(c,h,t):
    """Exact integer sufficient conditions; no floating-point estimates."""
    if any(type(x) is not int for x in (c,h,t)) or not (
            1<=t<c and 2*t<=h<=2*c and h%2==0):
        return False
    volume=sum(comb(c-1,s)*3**s for s in range(t))
    return 2*volume < 1<<h and (1<<h)*3**c < 4**c

def forbidden_sums(pairs,t):
    """All sums using at most t-1 prior blocks, at most one nonzero form each.

    Stream with repetition; membership, not multiplicity, matters.
    """
    yield 0
    for s in range(1,min(t-1,len(pairs))+1):
        for chosen in combinations(pairs,s):
            for values in product(*((a,b,a^b) for a,b in chosen)):
                v=0
                for x in values:
                    v^=x
                yield v

def greedy_pairs(c,h,t,stats):
    """First h columns are systematic; extend by lexicographic pairs."""
    pairs=[(1<<j,1<<(j+1)) for j in range(0,h,2)]
    while len(pairs)<c:
        def available(v,other=None):
            for w in forbidden_sums(pairs,t):
                stats["sum_terms_checked"]+=1
                if v==w or (other is not None and v^other==w):
                    return False
            return True
        def choose(other=None):
            for v in range(1<<h):
                stats["column_candidates"]+=1
                if available(v,other):
                    return v
            raise AssertionError("volume condition violated")
        a=choose()
        b=choose(a)
        pairs.append((a,b))
    return pairs

def evaluate(x,pair):
    a,b=pair
    return ((x&a).bit_count()&1) | (((x&b).bit_count()&1)<<1)

def greedy_anchor(pairs,h,stats):
    """Choose most frequent forbidden value among surviving coefficients."""
    forbidden=[]
    remaining=1<<h
    stats["survivors"]=[remaining]
    anchor=0
    for i,pair in enumerate(pairs):
        counts=[0,0,0,0]
        if remaining:
            for x in range(1<<h):
                stats["coefficient_visits"]+=1
                if any(evaluate(x,p)==q for p,q in zip(pairs,forbidden)):
                    continue
                counts[evaluate(x,pair)]+=1
        if sum(counts)!=remaining:
            raise AssertionError("survivor accounting mismatch")
        q=max(range(4),key=counts.__getitem__)  # smallest maximizing value
        forbidden.append(q)
        anchor|=(q^2)<<(2*i)  # local triple excludes value 2
        remaining-=counts[q]
        stats["survivors"].append(remaining)
    if remaining:
        raise AssertionError("exclusion condition violated")
    return anchor

def construct(c,h,t,*,max_dimension=16,max_sum_terms=10000,stats=None):
    """Deterministic constructor; explicit budgets limit executable controls."""
    if any(type(x) is not int or x<1 for x in (max_dimension,max_sum_terms)):
        raise ValueError("positive resource budgets required")
    if not conditions(c,h,t):
        raise ValueError("sufficient construction conditions not met")
    if h>max_dimension or sum(comb(c-1,s)*3**s for s in range(t))>max_sum_terms:
        raise ValueError("construction exceeds explicit enumeration budget")
    count={"column_candidates":0,"sum_terms_checked":0,"coefficient_visits":0}
    if stats is not None:
        stats.clear()
        stats.update(count)
        count=stats
    pairs=greedy_pairs(c,h,t,count)
    anchor=greedy_anchor(pairs,h,count)
    dirs=[sum((((a>>j)&1)|(((b>>j)&1)<<1))<<(2*i)
              for i,(a,b) in enumerate(pairs)) for j in range(h)]
    basis={}
    for v in dirs:
        insert(basis,v)
    if len(basis)!=h:
        raise AssertionError("systematic rank lost")
    rows=[(m,(m&anchor).bit_count()%2) for m in annihilator(2*c,basis)]
    cert={"anchor":anchor,"directions":dirs,"closed_order":t,"minimum_order_lower":t+1}
    return [(10,15)]*c,rows,cert

def family(n,**kwargs):
    if type(n) is not int or n<1:
        raise ValueError("positive integer scale required")
    return construct(64*n,16*n,n,**kwargs)

def evidence():
    cases=[]
    for c,h,t in ((24,8,2),(64,16,2)):
        stats={}
        ds,rs,cert=construct(c,h,t,stats=stats)
        assert check_obstruction(ds,rs,cert)
        cases.append({"blocks":c,"dimension":h,"checked_order":t,
                      "minimum_order_lower":t+1,"affine_points":1<<h,
                      "projection_subsets":comb(c,t),"stats":stats,
                      "checker_accepted":True,"domains":ds,"rows":rs,"certificate":cert})
    return {"scope":"deterministic finite controls, exponential construction bound",
            "family":{"blocks":"64n","dimension":"16n","minimum_order_lower":"n+1",
                      "construction_time":"O(2^(22n) poly(n))","space":"poly(n)"},
            "cases":cases}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
