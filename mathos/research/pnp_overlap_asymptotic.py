"""Theorem O: probabilistic linear-order obstructions, bounded reproducible controls.

The existence proof is asymptotic; finite sampling/checking is not an explicit
polynomial-time construction or a general SAT lower bound.
"""
from itertools import combinations, product
from math import comb
from random import Random
import json
from mathos.research.pnp_overlap_order import insert, annihilator
from mathos.research.pnp_overlap_algebraic import points
from mathos.research.pnp_overlap_certificates import _rank, _relation
from mathos.research.pnp_overlap_obstructions import inputs

def probability_bound(n):
    """Integer-arithmetic validation of the three union-bound constants."""
    if type(n) is not int or n<1:
        raise ValueError("positive integer scale required")
    assert 67**64 < 32*64**64
    assert 8*3**8 < 4**8
    return {"blocks":64*n,"dimension":16*n,"closed_order":n,
            "minimum_order_lower":n+1,
            "bad_probability_upper_terms":[5*n,8*n,112*n],
            "interpretation":"strict upper bound sum of 2**(-exponent)"}

def projection_basis(directions,ids):
    basis={}
    for v in directions:
        insert(basis,sum(((v>>(2*i))&3)<<(2*j) for j,i in enumerate(ids)))
    return basis

def has_full_projections(c,directions,t):
    # Surjectivity on all t-subsets implies it for smaller subsets.
    return all(len(projection_basis(directions,ids))==2*t
               for ids in combinations(range(c),t))

def all_excluded(c,anchor,directions):
    # Every local relation excludes binary 10. A point is disallowed
    # iff some odd-position bit is one and its preceding bit is zero.
    mask=sum(1<<(2*i) for i in range(c))
    return all(((x>>1)&~x&mask)!=0 for x in points(anchor,directions))

def sample(c,h,t,*,seed=20261127,max_trials=64):
    """Bounded seed search; may fail. Limit dimensions and local subset count."""
    if any(type(x) is not int for x in (c,h,t,seed,max_trials)):
        raise ValueError("integer parameters required")
    if not 1<=t<=c<=128 or not 2*t<=h<=min(2*c,16) or not 1<=max_trials<=128:
        raise ValueError("outside finite-control budget")
    if comb(c,t)>10000:
        raise ValueError("subset budget exceeded")
    rng=Random(seed)
    for trial in range(1,max_trials+1):
        dirs=[rng.getrandbits(2*c) for _ in range(h)]
        a=rng.getrandbits(2*c)
        basis={}
        for v in dirs:
            insert(basis,v)
        if len(basis)!=h or not has_full_projections(c,dirs,t):
            continue
        if not all_excluded(c,a,dirs):
            continue
        rows=[(m,(m&a).bit_count()%2) for m in annihilator(2*c,basis)]
        cert={"anchor":a,"directions":dirs,"closed_order":t,
              "minimum_order_lower":t+1}
        return [(10,15)]*c,rows,cert,trial
    raise ValueError("no qualifying sample within trial budget")

def check_obstruction(domains,rows,cert):
    """Separate rank and point checker, not the sampling or recovery routine."""
    try:
        ds,rs=inputs(domains,rows)
        c=len(ds)
        width=2*c
        if not isinstance(cert,dict) or set(cert)!={"anchor","directions","closed_order","minimum_order_lower"}:
            return False
        a,dirs,t,lower=(cert[k] for k in ("anchor","directions","closed_order","minimum_order_lower"))
        if type(a) is not int or not 0<=a<1<<width or not isinstance(dirs,list):
            return False
        if type(t) is not int or type(lower) is not int or not 1<=t<c<=128 or lower!=t+1:
            return False
        if len(dirs)>16 or comb(c,t)>10000 or any(type(v) is not int or not 0<v<1<<width for v in dirs):
            return False
        if any((a&m).bit_count()%2!=b for m,b in rs):
            return False
        if any((v&m).bit_count()%2 for v in dirs for m,b in rs):
            return False
        if _rank(width,dirs)!=len(dirs) or len(dirs)!=width-_rank(width,[m for m,b in rs]):
            return False
        rel=[_relation(d) for d in ds]
        if any(len(r)<3 for r in rel):
            return False
        for ids in combinations(range(c),t):
            mask=sum(3<<(2*i) for i in ids)
            if _rank(width,[v&mask for v in dirs])!=2*t:
                return False
        # Independent binary assignment enumeration; do not assume a particular
        # forbidden local value, or trust the generator's Gray-code scan.
        for bits in product((0,1),repeat=len(dirs)):
            x=a
            for bit,v in zip(bits,dirs):
                if bit:
                    x^=v
            if all((x>>(2*i))&3 in r for i,r in enumerate(rel)):
                return False
        return True
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def evidence():
    ds,rs,cert,trial=sample(64,16,2)
    assert check_obstruction(ds,rs,cert)
    return {"scope":"finite sample and nonconstructive existence proof; no general SAT lower bound",
            "finite":{"blocks":len(ds),"dimension":len(cert["directions"]),
                      "affine_points":1<<len(cert["directions"]),
                      "full_projection_subsets":comb(len(ds),2),
                      "minimum_order_lower":cert["minimum_order_lower"],
                      "trial":trial,"seed":20261127,"checker_accepted":True,
                      "domains":ds,"rows":rs,"certificate":cert},
            "asymptotic":[probability_bound(n) for n in (1,4,16,64)]}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
