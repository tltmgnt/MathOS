"""Independent reference witnesses for two frozen external SATLIB strata.

No calls to MathOS search, Gaussian elimination, or the XOR extractor.
"""
from collections import defaultdict
from itertools import product


def exact_count(n,clauses):
    if not 0<=n<=20:
        raise ValueError("exhaustive reference dimension")
    size=1<<n
    all_bits=(1<<size)-1
    values=[]
    for v in range(n):
        stride=1<<v
        bits=((1<<stride)-1)<<stride
        span=2*stride
        while span<size:
            bits|=bits<<span
            span*=2
        values.append(bits)
    live=all_bits
    for c in clauses:
        allowed=0
        for x in c:
            a=values[abs(x)-1]
            allowed|=a if x>0 else all_bits^a
        live&=allowed
        if not live:
            break
    return live.bit_count()


def parity_sum(n,clauses):
    """Check the direct sum of all local parity truth tables, no elimination."""
    groups=defaultdict(list)
    for c in clauses:
        vs=tuple(sorted({abs(x) for x in c}))
        if len(c)!=3 or len(vs)!=3 or not all(1<=v<=n for v in vs):
            raise ValueError("non-ternary parity source")
        groups[vs].append(c)
    odd=set()
    rhs=0
    for vs,cs in sorted(groups.items()):
        if len(cs)!=4:
            raise ValueError("not a four-clause parity block")
        allowed=set()
        for bits in product((False,True),repeat=3):
            a=dict(zip(vs,bits))
            if all(any(a[abs(x)]==(x>0) for x in c) for c in cs):
                allowed.add(bits)
        parities={sum(bits)%2 for bits in allowed}
        if len(allowed)!=4 or len(parities)!=1:
            raise ValueError("block is not exact parity")
        rhs^=next(iter(parities))
        odd.symmetric_difference_update(vs)
    if odd or rhs!=1:
        raise ValueError("direct parity sum is not contradictory")
    return len(groups)


def reference(group,n,clauses):
    if group=="uf20":
        count=exact_count(n,clauses)
        return {"method":"exhaustive_model_count","decision":"sat" if count else "unsat",
                "models":count}
    if group=="dubois":
        return {"method":"direct_parity_sum","decision":"unsat",
                "equations":parity_sum(n,clauses)}
    return {"method":"published_label_only","decision":None}
