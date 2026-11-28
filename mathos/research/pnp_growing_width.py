"""Torus Tseitin width lower bound: checked structural premises, algebraic escape.

The documented proof uses minimum vertex-equation support and balanced
edge cuts. The verifier checks the premises, not a search for a refutation
or a full formalization of the mathematical lower-bound argument.
"""
from collections import Counter
from itertools import product
from .pnp_structural_kernel import validate
from .pnp_algebra_frontier import xor_block
from .pnp_unified_portfolio import fingerprint

MAX_SIDE=16


def _side(s):
    if type(s) is not int or not 3<=s<=MAX_SIDE:
        raise ValueError("side outside supported range")


def torus(s):
    _side(s)
    # Edge IDs are one-based. At each vertex emit right and down edges.
    edges=[]
    for r in range(s):
        for c in range(s):
            v=r*s+c
            edges.extend(((v,r*s+(c+1)%s),(v,((r+1)%s)*s+c)))
    return tuple(edges)


def family(s,*,odd=True):
    if type(odd) is not bool:
        raise ValueError("invalid parity control")
    edges=torus(s)
    incident=[[] for _ in range(s*s)]
    for i,(u,v) in enumerate(edges,1):
        incident[u].append(i)
        incident[v].append(i)
    rows=tuple((tuple(sorted(vs)),int(odd and j==0)) for j,vs in enumerate(incident))
    f=tuple(c for vs,rhs in rows for c in xor_block(vs,rhs))
    return len(edges),f,rows


def cut_size(edges,vertices,b):
    selected=set(vertices)
    result=0
    for u,v in edges:
        b.tick()
        result+=(u in selected)!=(v in selected)
    return result


def balanced_cut(s,vertices,b):
    """Check a supplied balanced cut against the proved 2s bound.

    Case witness is mixed rows, full/empty rows, or a set (possibly
    complemented) with neither full rows nor full columns.
    """
    edges=torus(s)
    vertices=set(vertices)
    v=s*s
    if (any(type(i) is not int or not 0<=i<v for i in vertices) or
            not v<3*len(vertices)<=2*v):
        raise ValueError("cut not in support interval")
    rows=[sum(r*s+c in vertices for c in range(s)) for r in range(s)]
    b.tick(v)
    if all(0<x<s for x in rows):
        mode="all_rows_mixed"
        lower=2*s
    elif 0 in rows and s in rows:
        mode="full_and_empty_rows"
        lower=2*s
    else:
        if s in rows:
            vertices=set(range(v))-vertices
            rows=[s-x for x in rows]
        if s in rows or 0 not in rows:
            raise AssertionError("row classification failed")
        # Every nonempty row and nonempty column is mixed. The number
        # of occupied cells is at most R*C and at least s^2/3.
        columns=[sum(r*s+c in vertices for r in range(s)) for c in range(s)]
        b.tick(v)
        if s in columns:
            raise AssertionError("empty row prevents full columns")
        R=sum(x>0 for x in rows)
        C=sum(x>0 for x in columns)
        if len(vertices)>R*C or 3*len(vertices)<v or R+C<s:
            raise AssertionError("balanced occupancy inequality failed")
        mode="mixed_rows_and_columns"
        lower=2*(R+C)
    actual=cut_size(edges,vertices,b)
    if actual<lower or lower<2*s:
        raise AssertionError("cut witness contradicts lower bound")
    return {"mode":mode,"size":actual,"certified_lower":lower}


def certificate(s,n,f,b,*,odd=True):
    expected_n,expected_f,rows=family(s,odd=odd)
    if n!=expected_n or validate(n,f)!=expected_f:
        raise ValueError("not the declared torus family")
    r={"schema":"mathos-pnp-torus-width/1","side":s,"odd":odd,
       "input_sha256":fingerprint(n,f),"vertices":s*s,"edges":n,
       "rows":rows,"total_rhs":int(odd),
       "balanced_cut_lower":2*s,
       "resolution_width_lower":2*s if odd else None,
       "scope":"resolution refutation from original CNF axioms, no extension variables"}
    verify(s,n,f,r,b)
    return r


def verify(s,n,clauses,r,b):
    """Check torus incidence, exact local truth tables and odd-charge premise.

    The arbitrary-size balanced cut and support-measure proof is in the
    mathematical specification. No bound is credited on the SAT twin.
    """
    _side(s)
    f=validate(n,clauses)
    odd=r["odd"]
    if (type(odd) is not bool or r["schema"]!="mathos-pnp-torus-width/1" or
            r["side"]!=s or n!=2*s*s or r["vertices"]!=s*s or r["edges"]!=n or
            r["input_sha256"]!=fingerprint(n,f) or r["balanced_cut_lower"]!=2*s or
            r["resolution_width_lower"]!=(2*s if odd else None) or
            r["scope"]!="resolution refutation from original CNF axioms, no extension variables"):
        raise ValueError("invalid torus metadata")
    # Independently reconstruct the four incident edge IDs from each
    # vertex coordinate: outgoing right/down, incoming left/up.
    expected=[]
    for row in range(s):
        for col in range(s):
            v=row*s+col
            left=row*s+(col-1)%s
            up=((row-1)%s)*s+col
            expected.append(tuple(sorted((2*v+1,2*v+2,2*left+1,2*up+2))))
    groups={}
    for c in f:
        b.tick(1+len(c))
        key=tuple(sorted(abs(x) for x in c))
        if len(c)!=4 or len(set(key))!=4:
            raise ValueError("invalid local clause")
        groups.setdefault(key,[]).append(c)
    if len(expected)!=len(set(expected)) or set(groups)!=set(expected) or len(r["rows"])!=s*s:
        raise ValueError("incomplete torus scope cover")
    count=Counter()
    parity=0
    for i,(raw,rhs) in enumerate(r["rows"]):
        vs=tuple(raw)
        if (any(type(x) is not int for x in vs) or vs!=expected[i] or
                type(rhs) is not int or rhs!=int(odd and i==0) or len(groups[vs])!=8):
            raise ValueError("invalid incidence row")
        for bits in product((False,True),repeat=4):
            b.tick(1+4*len(groups[vs]))
            a=dict(zip(vs,bits))
            holds=all(any(a[abs(x)]==(x>0) for x in c) for c in groups[vs])
            if holds!=(sum(bits)%2==rhs):
                raise ValueError("incorrect local parity relation")
        count.update(vs)
        parity^=rhs
    if (set(count)!=set(range(1,n+1)) or any(x!=2 for x in count.values()) or
            type(r["total_rhs"]) is not int or r["total_rhs"]!=parity or parity!=int(odd)):
        raise ValueError("invalid global parity identity")
    return True
