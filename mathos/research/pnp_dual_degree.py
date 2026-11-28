"""Dual certificates for the v30 bounded Boolean quotient proof system.

A list H of binary linear functionals defines the primal space ker(H).
Verification needs no primal derivation, search history or rank claim.
"""
from .pnp_boolean_lift import _expected_polynomial,polynomial
from .pnp_degree_closure import _input,_mask,verify as verify_closure
from .pnp_unified_portfolio import fingerprint

SCHEMA="mathos-pnp-dual-degree/1"


def _coordinates(n,d):
    return tuple(t for t in range(1<<n) if t.bit_count()<=d)


def _insert(p,basis,b):
    while p:
        b.tick()
        k=p.bit_length()-1
        if k not in basis:
            basis[k]=p
            return
        p^=basis[k]


def _member(p,basis,b):
    while p:
        b.tick()
        k=p.bit_length()-1
        if k not in basis:
            return False
        p^=basis[k]
    return True


def _annihilator(vectors,coords,b):
    B={}
    for p in vectors:
        _insert(p,B,b)
    H=[]
    pivots=sorted(B)
    for j in coords:
        if j in B:
            continue
        h=1<<j
        for k in pivots:
            b.tick()
            if (B[k]&h).bit_count()%2:
                h|=1<<k
        H.append(h)
    return H


def _certificate(n,f,d,H,scope):
    return {"schema":SCHEMA,"input_sha256":fingerprint(n,f),
            "degree":d,"scope":scope,"functionals":H}


def _replay(n,g,steps,b):
    known=[_mask(polynomial(c)) for c in g]
    for op,i,j in steps:
        b.tick()
        if op=="xor":
            p=known[i]^known[j]
        else:
            p=0
            q=known[i]
            while q:
                b.tick()
                t=q&-q
                q^=t
                p^=1<<((t.bit_length()-1)|(1<<j))
        known.append(p)
    return known


def from_closure(n,f,proof,b):
    """Convert verified primal closure into an independent dual certificate."""
    verify_closure(n,f,proof,b)
    if proof["status"]!="closed_no_refutation":
        raise ValueError("refutation has no separating dual space")
    d=proof["degree"]
    nn,g,_=_input(n,f,d)
    known=_replay(nn,g,proof["steps"],b)
    H=_annihilator((known[i] for i in proof["basis"]),_coordinates(nn,d),b)
    return _certificate(n,f,d,H,"dynamic")


def static(n,f,b,*,degree):
    """Separate 1 from the linear span of axioms alone, if possible."""
    nn,g,_=_input(n,f,degree)
    H=_annihilator((_mask(polynomial(c)) for c in g),_coordinates(nn,degree),b)
    if not any(h&1 for h in H):
        return None
    return _certificate(n,f,degree,H,"static")


def _high_constraints(coords,v,d):
    # Q L_v maps the low-degree space into high-degree coordinates.
    # Each row of this map is a mask of low-degree preimages.
    high={}
    for t in coords:
        u=t|(1<<v)
        if u.bit_count()>d:
            high[u]=high.get(u,0)^(1<<t)
    return high.values()


def verify(n,f,r,b,*,require_dynamic=True):
    nn,g,_=_input(n,f,r["degree"])
    d=r["degree"]
    if (r["schema"]!=SCHEMA or r["input_sha256"]!=fingerprint(n,f)
            or r["scope"] not in ("static","dynamic")
            or (require_dynamic and r["scope"]!="dynamic")):
        raise ValueError("invalid dual scope or input")
    coords=_coordinates(nn,d)
    allowed=_mask(coords)
    H=r["functionals"]
    if (not isinstance(H,(list,tuple)) or not 1<=len(H)<=len(coords)
            or any(type(h) is not int or h<=0 or h&~allowed for h in H)
            or not any(h&1 for h in H)):
        raise ValueError("missing separating functional or invalid coordinates")
    b.cells(len(H)*len(coords))
    basis={}
    for h in H:
        _insert(h,basis,b)
    if len(basis)!=len(H):
        raise ValueError("dependent dual basis")
    for c in g:
        p=_mask(_expected_polynomial(c,0,b))
        for h in H:
            b.tick()
            if (p&h).bit_count()%2:
                raise ValueError("axiom not annihilated")
    if r["scope"]=="static":
        return True
    for v in range(nn):
        constraints=basis.copy()
        for q in _high_constraints(coords,v,d):
            _insert(q,constraints,b)
        # h L_v must lie in span(H, rows(Q L_v)). Therefore
        # H p=0 and Q L_v p=0 imply H L_v p=0.
        for h in H:
            pull=0
            for t in coords:
                b.tick()
                u=t|(1<<v)
                if h>>u&1:
                    pull|=1<<t
            if not _member(pull,constraints,b):
                raise ValueError("dual space not closed under eligible multiplication")
    return True
