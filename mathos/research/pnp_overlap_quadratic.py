"""Theorem Q: punctured dual-code construction and quadratic UNSAT proofs.

Generic transformation is polynomial; the external AG-code supplier is not
implemented. Reed-Muller is the self-contained executable code family.
"""
import json
from mathos.research.pnp_overlap_order import insert, annihilator
from mathos.research.pnp_overlap_certificates import _rank, _relation
from mathos.research.pnp_overlap_obstructions import inputs

def rm_basis(m,r):
    if type(m) is not int or type(r) is not int or not 2<=m<=10 or not 0<=r<m:
        raise ValueError("Reed-Muller control outside budget")
    n=1<<m
    return [sum(1<<x for x in range(n) if x&s==s)
            for s in range(n) if s.bit_count()<=r]

def shorten(basis,n):
    bit=1<<(n-1)
    one=next((v for v in basis if v&bit),None)
    if one is None:
        raise ValueError("puncture coordinate must be nonzero in both codes")
    return [v^(one if v&bit else 0) for v in basis if v!=one],one

def interleave(u,v,c):
    return sum(((u>>i&1)|((v>>i&1)<<1))<<(2*i) for i in range(c))

def transform(n,generator):
    if type(n) is not int or n<3:
        raise ValueError("invalid code length")
    g=list(generator)
    if any(type(v) is not int or not 0<v<1<<n for v in g) or _rank(n,g)!=len(g):
        raise ValueError("independent binary basis required")
    basis={}
    for v in g:
        insert(basis,v)
    dual=list(annihilator(n,basis))
    u,a=shorten(g,n)
    v,b=shorten(dual,n)
    c=n-1
    mask=(1<<c)-1
    dirs=[interleave(x&mask,0,c) for x in u]+[interleave(0,y&mask,c) for y in v]
    anchor=interleave((a&mask)^mask,b&mask,c)
    span={}
    for d in dirs:
        insert(span,d)
    rows=[(r,(r&anchor).bit_count()%2) for r in annihilator(2*c,span)]
    return [(10,15)]*c,rows,{"anchor":anchor,"directions":dirs}

def violation_parity(x,c):
    even=sum(1<<(2*i) for i in range(c))
    return (((x>>1)&~x&even).bit_count()&1)

def check_quadratic(domains,rows,cert):
    """Verify odd violation parity on an entire affine space, in polynomial time."""
    try:
        ds,rs=inputs(domains,rows)
        c=len(ds)
        if any(_relation(d)!={0,1,3} for d in ds):
            return False
        if not isinstance(cert,dict) or set(cert)!={"anchor","directions"}:
            return False
        a,dirs=cert["anchor"],cert["directions"]
        w=2*c
        if type(a) is not int or not 0<=a<1<<w or not isinstance(dirs,list):
            return False
        if any(type(d) is not int or not 0<d<1<<w for d in dirs):
            return False
        if len(dirs)!=w-_rank(w,[m for m,b in rs]) or _rank(w,dirs)!=len(dirs):
            return False
        if any((a&m).bit_count()%2!=b for m,b in rs) or any(
                (d&m).bit_count()%2 for d in dirs for m,b in rs):
            return False
        if violation_parity(a,c)!=1:
            return False
        if any(violation_parity(a^d,c)!=1 for d in dirs):
            return False
        return all(violation_parity(a^d^e,c)==1
                   for i,d in enumerate(dirs) for e in dirs[:i])
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def rm_instance(m):
    if type(m) is not int or not 3<=m<=8:
        raise ValueError("executable control requires 3<=m<=8")
    r=(m-1)//2
    ds,rs,cert=transform(1<<m,rm_basis(m,r))
    return ds,rs,{"m":m,"minimum_order_lower":(1<<min(m-r,r+1))-1,"quadratic":cert}

def check_rm(domains,rows,cert):
    """Verify exact coefficient row space using the two punctured RM bases.

    Distance follows from the classical Reed-Muller distance theorem, not
    enumeration or a claim to certify arbitrary code distance in polynomial time.
    """
    try:
        ds,rs=inputs(domains,rows)
        if not isinstance(cert,dict) or set(cert)!={"m","minimum_order_lower","quadratic"}:
            return False
        m=cert["m"]
        if type(m) is not int or not 3<=m<=8:
            return False
        c=(1<<m)-1
        r=(m-1)//2
        if len(ds)!=c or type(cert["minimum_order_lower"]) is not int or cert["minimum_order_lower"]!=(1<<min(m-r,r+1))-1:
            return False
        if not check_quadratic(ds,rs,cert["quadratic"]):
            return False
        # Independent direct monomial evaluation of the punctured row space.
        expected=[]
        for side,degree in ((0,m-r-1),(1,r)):
            for s in range(1<<m):
                if s.bit_count()<=degree:
                    expected.append(sum(1<<(2*x+side) for x in range(c) if x&s==s))
        actual=[a for a,b in rs]
        rank=_rank(2*c,expected)
        return rank==_rank(2*c,actual)==_rank(2*c,expected+actual)
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def evidence():
    cases=[]
    for m in (3,5,7):
        ds,rs,cert=rm_instance(m)
        assert check_rm(ds,rs,cert)
        h=len(cert["quadratic"]["directions"])
        cases.append({"blocks":len(ds),"affine_dimension":h,"affine_points_log2":h,
                      "minimum_order_lower":cert["minimum_order_lower"],
                      "quadratic_checks":1+h+h*(h-1)//2,
                      "checker_accepted":True,"certificate":cert})
    return {"scope":"RM executable controls; AG asymptotic supplier is external",
            "cases":cases,"ag_family":{"binary_length":"42*8^(level+1)",
            "minimum_order_lower":"N/18-1","affine_dimension":"N-2",
            "supplier_implemented":False}}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
