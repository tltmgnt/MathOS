"""Certified restricted resolution obstructions and constructive escape families.

The depth bound concerns binary resolution DAGs using original clauses as
axioms, not all proof systems or SAT algorithms. The width bound concerns
derived clauses, including when wider input axioms are permitted.
"""
from .pnp_structural_kernel import normalize, validate
from .pnp_resolution_refutation import verify as verify_resolution
from .pnp_unified_portfolio import fingerprint

MAX_CHAIN=256
MAX_CUBE=9


def _size(n,limit,lo=1):
    if type(n) is not int or not lo<=n<=limit:
        raise ValueError("invalid family size")


def chain(n):
    _size(n,MAX_CHAIN)
    return ((1,),)+tuple((-i,i+1) for i in range(1,n))+((-n,),)


def cube(k):
    _size(k,MAX_CUBE,2)
    return tuple(tuple(i+1 if mask>>i&1 else -(i+1) for i in range(k))
                 for mask in range(1<<k))


def chain_certificate(n):
    """Deleting clause j admits x_i=true exactly for i<=j.

    The n+1 original clauses are necessary for every sound refutation
    whose only axioms are these clauses.
    """
    f=chain(n)
    return {"schema":"mathos-pnp-chain-depth/1","n":n,"input_sha256":fingerprint(n,f),
            "clause_count":n+1,"prefix_witnesses":list(range(n+1)),
            "minimum_depth":n.bit_length(),
            "scope":"binary resolution refutation depth from original axioms"}


def verify_chain(n,clauses,r,b):
    f=validate(n,clauses)
    if f!=chain(n) or r["schema"]!="mathos-pnp-chain-depth/1" or r["n"]!=n or r["input_sha256"]!=fingerprint(n,f):
        raise ValueError("chain input mismatch")
    if (r["clause_count"]!=n+1 or r["prefix_witnesses"]!=list(range(n+1)) or
            r["minimum_depth"]!=n.bit_length() or
            r["scope"]!="binary resolution refutation depth from original axioms"):
        raise ValueError("chain bound mismatch")
    # Independent truth replay of all n+1 deletion witnesses.
    for j in r["prefix_witnesses"]:
        for i,c in enumerate(f):
            b.tick(1+len(c))
            sat=any((abs(x)<=j)==(x>0) for x in c)
            if sat!=(i!=j):
                raise ValueError("invalid deletion witness")
    return True


def balanced_proof(n,b):
    """Balanced resolution over consecutive clause intervals, width <=2."""
    f=chain(n)
    nn,axioms,mapping=normalize(n,f)
    indices={c:i for i,c in enumerate(axioms)}
    known=list(axioms)
    steps=[]
    depths=[0]*len(known)
    def combine(lo,hi):
        b.tick()
        if hi-lo==1:
            return indices[tuple(sorted(f[lo]))]
        mid=(lo+hi)//2
        p,q=combine(lo,mid),combine(mid,hi)
        pivot=mid
        a,c=known[p],known[q]
        if pivot not in a or -pivot not in c:
            raise AssertionError("invalid balanced interval pivot")
        d=tuple(sorted((set(a)-{pivot})|(set(c)-{-pivot})))
        i=len(known)
        known.append(d)
        depths.append(1+max(depths[p],depths[q]))
        steps.append({"positive":p,"negative":q,"pivot":pivot,"clause":d})
        return i
    root=combine(0,len(f))
    p={"schema":"mathos-pnp-resolution-dag/1","normalized_n":nn,"new_to_old":mapping,
       "width_cap":2,"record_cap":len(known),"strategy":"ascending","steps":steps,"root":root}
    verify_resolution(n,f,p,b)
    return p


def depth_support(n,clauses,proof,b):
    """Independently replay and measure the reachable axiom support of a DAG."""
    verify_resolution(n,clauses,proof,b)
    _,f,_=normalize(n,clauses)
    base=len(f)
    depths=[0]*base
    for s in proof["steps"]:
        b.tick()
        depths.append(1+max(depths[s["positive"]],depths[s["negative"]]))
    root=proof["root"]
    seen=set()
    todo=[root]
    while todo:
        i=todo.pop()
        b.tick()
        if i in seen:
            continue
        seen.add(i)
        if i>=base:
            s=proof["steps"][i-base]
            todo.extend((s["positive"],s["negative"]))
    support=sum(i<base for i in seen)
    d=depths[root]
    # Every binary derivation of depth d has at most 2**d distinct axiom
    # ancestors. Avoid constructing giant integers for arbitrary DAG depth.
    if (support-1).bit_length()>d:
        raise ValueError("binary proof support exceeds depth capacity")
    return {"depth":d,"axiom_support":support,"derived_steps":len(proof["steps"]),
            "maximum_derived_width":max((len(s["clause"]) for s in proof["steps"]),default=0)}


def cube_certificate(k):
    f=cube(k)
    return {"schema":"mathos-pnp-cube-width/1","k":k,"input_sha256":fingerprint(k,f),
            "clause_count":1<<k,"minimum_first_derived_width":k-1,
            "scope":"first non-tautological resolution inference from full-width cube axioms"}


def verify_cube(k,clauses,r,b):
    f=validate(k,clauses)
    if f!=cube(k) or r!=cube_certificate(k):
        raise ValueError("cube certificate mismatch")
    # Each full-width clause has a unique falsifying assignment; the
    # complete sign cube covers all 2**k assignments.
    masks=set()
    for c in f:
        b.tick(1+len(c))
        if len(c)!=k or {abs(x) for x in c}!=set(range(1,k+1)):
            raise ValueError("invalid cube axiom")
        masks.add(tuple(x<0 for x in c))
    if len(masks)!=(1<<k):
        raise ValueError("incomplete blocking cube")
    # In any non-tautological resolvent, parents differ in sign only
    # at the pivot; every other variable survives. This finite check
    # enumerates pairs for the supported dimension limit.
    for i,a in enumerate(f):
        for c in f[i+1:]:
            b.tick(1+k)
            opposites=sum(x==-y for x,y in zip(a,c))
            if opposites==1:
                v=next(abs(x) for x,y in zip(a,c) if x==-y)
                d={x for x in a+c if abs(x)!=v}
                if len(d)!=k-1 or any(-x in d for x in d):
                    raise ValueError("incorrect first-step width bound")
            elif opposites<1:
                raise ValueError("duplicate cube axiom")
    return True
