"""Linear-size parity systems separating bounded derived width from XOR algebra.

A first-step obstruction applies only to resolution from the given CNF
axioms without extra inference rules, extension axioms or preprocessing.
"""
from collections import Counter
from itertools import combinations, product
from .pnp_structural_kernel import validate, normalize
from .pnp_algebra_frontier import xor_block
from .pnp_unified_portfolio import fingerprint

MAX_RINGS=64


def prism(m,*,inconsistent=True):
    """Two m-cycles joined by m rungs. Edge variables, vertex XOR equations."""
    if type(m) is not int or not 3<=m<=MAX_RINGS or type(inconsistent) is not bool:
        raise ValueError("invalid prism parameters")
    edges=[(side*m+i,side*m+(i+1)%m) for side in range(2) for i in range(m)]
    edges.extend((i,m+i) for i in range(m))
    incident=[[] for _ in range(2*m)]
    for i,(u,v) in enumerate(edges,1):
        incident[u].append(i)
        incident[v].append(i)
    rows=tuple((tuple(sorted(vs)),int(inconsistent and i==0))
               for i,vs in enumerate(incident))
    f=tuple(c for vs,rhs in rows for c in xor_block(vs,rhs))
    return 3*m,f,rows


def propose(n,clauses,budget):
    """Recognize exact ternary parity blocks on linear scopes.

    Returns a first-step width obstruction and a full-row XOR identity.
    An even identity alone does NOT certify satisfiability.
    """
    nn,f,mapping=normalize(n,clauses)
    groups={}
    for c in f:
        budget.tick(1+len(c))
        if len(c)!=3:
            return None
        key=tuple(sorted(abs(x) for x in c))
        groups.setdefault(key,set()).add(c)
    if not groups:
        return None
    rows=[]
    for key,block in sorted(groups.items()):
        for rhs in (0,1):
            budget.tick(4)
            expected={tuple(sorted(c)) for c in xor_block(key,rhs)}
            if expected==block:
                rows.append((key,rhs))
                break
        else:
            return None
    counts=Counter(v for vs,_ in rows for v in vs)
    if set(counts)!=set(range(1,nn+1)) or any(x!=2 for x in counts.values()):
        return None
    # A repeated variable pair would be a pair of scopes sharing >=2.
    pairs=set()
    for vs,_ in rows:
        for pair in combinations(vs,2):
            budget.tick()
            if pair in pairs:
                return None
            pairs.add(pair)
    return {"schema":"mathos-pnp-parity-width-separation/1",
            "input_sha256":fingerprint(n,clauses),"normalized_n":nn,
            "new_to_old":mapping,"rows":rows,
            "first_derived_width_lower":4,
            "xor_rhs":sum(rhs for _,rhs in rows)%2,
            "scope":"resolution from original CNF axioms with derived width at most three"}


def verify(n,clauses,r,budget):
    """Independent check of truth tables, scope intersections and XOR sum.

    Scope pair linearity uses a pair index, rather than enumerating all
    clause pairs. Local truth tables have exactly eight assignments.
    """
    nn,f,mapping=normalize(n,clauses)
    if (r["schema"]!="mathos-pnp-parity-width-separation/1" or
            r["input_sha256"]!=fingerprint(n,clauses) or r["normalized_n"]!=nn or
            tuple(r["new_to_old"])!=mapping or r["first_derived_width_lower"]!=4 or
            r["scope"]!="resolution from original CNF axioms with derived width at most three"):
        raise ValueError("invalid separation metadata")
    groups={}
    for c in f:
        budget.tick(1+len(c))
        if len(c)!=3:
            raise ValueError("nonternary input")
        groups.setdefault(tuple(sorted(abs(x) for x in c)),[]).append(c)
    seen=set()
    pair_owner={}
    incidence=Counter()
    xor_variables=set()
    parity=0
    for raw,rhs in r["rows"]:
        vs=tuple(raw)
        if (len(vs)!=3 or any(type(v) is not int or not 1<=v<=nn for v in vs) or
                vs!=tuple(sorted(set(vs))) or vs not in groups or vs in seen or
                type(rhs) is not int or rhs not in (0,1)):
            raise ValueError("invalid parity row")
        seen.add(vs)
        for bits in product((False,True),repeat=3):
            budget.tick(1+3*len(groups[vs]))
            assignment=dict(zip(vs,bits))
            satisfies=all(any(assignment[abs(x)]==(x>0) for x in c) for c in groups[vs])
            if satisfies!=(sum(bits)%2==rhs):
                raise ValueError("parity block not equivalent")
        for pair in combinations(vs,2):
            budget.tick()
            if pair in pair_owner:
                raise ValueError("scopes are not linear")
            pair_owner[pair]=vs
        incidence.update(vs)
        xor_variables.symmetric_difference_update(vs)
        parity^=rhs
    if (not seen or seen!=set(groups) or set(incidence)!=set(range(1,nn+1)) or
            any(x!=2 for x in incidence.values()) or xor_variables or
            type(r["xor_rhs"]) is not int or r["xor_rhs"]!=parity):
        raise ValueError("incomplete scope cover or invalid XOR identity")
    return True


def first_step_width(n,clauses,budget):
    """Finite pair enumeration for small reference tests; None if no resolvent."""
    _,f,_=normalize(n,clauses)
    width=None
    for i,a in enumerate(f):
        for c in f[i+1:]:
            budget.tick(1+len(a)+len(c))
            p=[x for x in a if -x in c]
            if len(p)==1:
                x=p[0]
                size=len((set(a)-{x})|(set(c)-{-x}))
                width=size if width is None else min(width,size)
    return width
