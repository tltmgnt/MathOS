"""Theorem R: bounded-degree static Boolean refutations and dual obstructions.

Degree convention: a squarefree monomial multiplier m on a nonzero violation
polynomial q is admitted iff deg(m)+deg(q)<=d, before reducing their product.
This is NOT dynamic polynomial calculus or an unrestricted degree lower bound.
"""
from itertools import combinations
from math import comb
import json
from mathos.research.pnp_overlap_boundary import project, affine_solve
from mathos.research.pnp_overlap_algebraic import frame
from mathos.research.pnp_overlap_obstructions import inputs
from mathos.research.pnp_overlap_semantic import reduce_rows, indices, check_semantic
from mathos.research.pnp_overlap_certificates import _rank, _relation
from mathos.research.pnp_overlap_order_bounds import two_cycles, encode
from mathos.research.pnp_overlap_quadratic import rm_instance

MAX_MATRIX_BITS=20_000_000
MAX_MONOMIALS=100_000

def monomials(h,d):
    for s in range(min(h,d)+1):
        for js in combinations(range(h),s):
            yield sum(1<<j for j in js)

def count_monomials(h,d):
    return sum(comb(h,s) for s in range(min(h,d)+1)) if d>=0 else 0

def degree(q):
    return max((m.bit_count() for m in q),default=-1)

def multiply(a,b):
    out=set()
    for x in a:
        for y in b:
            out.symmetric_difference_update({x|y})
    return out

def polynomials(ds,a,dirs):
    """Forbidden-point indicators, in affine coefficient coordinates."""
    def form(j,constant):
        return ({0} if constant else set()) | {1<<k for k,v in enumerate(dirs) if v>>j&1}
    out={}
    for i,d in enumerate(ds):
        for p in sorted(set(range(4))-set(project(*d))):
            q=multiply(form(2*i,1^(p&1)^(a>>(2*i)&1)),
                       form(2*i+1,1^(p>>1)^(a>>(2*i+1)&1)))
            if q:
                out[i,p]=q
    return out

def validate_budget(h,d,qs):
    if type(d) is not int or d<0 or d>h+2:
        raise ValueError("degree must lie between zero and h+2")
    M=count_monomials(h,d)
    S=sum(count_monomials(h,d-degree(q)) for q in qs.values())
    if M>MAX_MONOMIALS or M*max(1,S)>MAX_MATRIX_BITS:
        raise ValueError("static matrix exceeds explicit budget")
    return M,S

def columns(h,d,qs):
    for (i,p),q in qs.items():
        for m in monomials(h,d-degree(q)):
            yield [i,p,m],multiply({m},q)

def refute(domains,rows,d,*,stats=None):
    ds,rs=inputs(domains,rows)
    if type(d) is not int or d<0:
        raise ValueError("nonnegative degree required")
    fr=frame(2*len(ds),rs)
    if fr is None:
        _,bad=reduce_rows(2*len(ds),rs)
        return {"kind":"affine_unsat","dual":indices(bad)}
    a,dirs=fr
    h=len(dirs)
    qs=polynomials(ds,a,dirs)
    M,S=validate_budget(h,d,qs)
    if stats is not None:
        stats.clear()
        stats.update({"dimension":h,"monomials":M,"columns":S,"degree":d})
    ms=list(monomials(h,d))
    idx={m:j for j,m in enumerate(ms)}
    tags=[]
    masks=[]
    pivots={}
    for tag,q in columns(h,d,qs):
        v=sum(1<<idx[m] for m in q)
        proof=1<<len(tags)
        tags.append(tag)
        masks.append(v)
        while v:
            j=v.bit_length()-1
            if j not in pivots:
                pivots[j]=(v,proof)
                break
            w,p=pivots[j]
            v^=w
            proof^=p
    target=1
    proof=0
    common={"anchor":a,"directions":dirs,"degree":d}
    while target:
        j=target.bit_length()-1
        if j not in pivots:
            # A separating functional lambda: lambda(column)=0, lambda(1)=1.
            dual=affine_solve(M,[(v,0) for v in masks]+[(1,1)])
            if dual is None:
                raise AssertionError("missing span separator")
            return {"kind":"no_refutation",**common,
                    "functional":[m for j,m in enumerate(ms) if dual>>j&1]}
        v,p=pivots[j]
        target^=v
        proof^=p
    return {"kind":"refutation",**common,"terms":[tag for j,tag in enumerate(tags) if proof>>j&1]}

def checker_polynomials(ds,a,dirs):
    """Independently reconstruct quadratic coefficients by finite differences."""
    out={}
    h=len(dirs)
    for i,d in enumerate(ds):
        def value(x,p):
            return int((x>>(2*i))&3==p)
        for p in sorted(set(range(4))-_relation(d)):
            q=set()
            zero=value(a,p)
            singles=[value(a^v,p) for v in dirs]
            if zero:
                q.add(0)
            for j,s in enumerate(singles):
                if s^zero:
                    q.add(1<<j)
            for j in range(h):
                for k in range(j):
                    if value(a^dirs[j]^dirs[k],p)^singles[j]^singles[k]^zero:
                        q.add((1<<j)|(1<<k))
            if q:
                out[i,p]=q
    return out

def check_degree(domains,rows,cert):
    """Separate verification of an identity or a separating functional."""
    try:
        ds,rs=inputs(domains,rows)
        if not isinstance(cert,dict):
            return False
        kind=cert.get("kind")
        if kind=="affine_unsat":
            return check_semantic(ds,rs,cert)
        key="terms" if kind=="refutation" else "functional"
        if kind not in ("refutation","no_refutation") or set(cert)!={"kind","anchor","directions","degree",key}:
            return False
        a,dirs,d=cert["anchor"],cert["directions"],cert["degree"]
        w=2*len(ds)
        if type(a) is not int or not 0<=a<1<<w or not isinstance(dirs,list):
            return False
        if any(type(v) is not int or not 0<v<1<<w for v in dirs):
            return False
        h=len(dirs)
        if h!=w-_rank(w,[m for m,b in rs]) or _rank(w,dirs)!=h:
            return False
        if any((a&m).bit_count()%2!=b for m,b in rs) or any((v&m).bit_count()%2 for v in dirs for m,b in rs):
            return False
        if type(d) is not int or not 0<=d<=h+2 or count_monomials(h,d)>MAX_MONOMIALS:
            return False
        qs=checker_polynomials(ds,a,dirs)
        validate_budget(h,d,qs)
        def shifted(q,m):
            result=set()
            for v in q:
                r=v|m
                if r in result:
                    result.remove(r)
                else:
                    result.add(r)
            return result
        if kind=="refutation":
            ts=cert["terms"]
            if not isinstance(ts,list) or not ts:
                return False
            seen=set()
            result=set()
            for term in ts:
                if not isinstance(term,list) or len(term)!=3 or any(type(v) is not int for v in term):
                    return False
                i,p,m=term
                if (i,p) not in qs or not 0<=m<1<<h or m.bit_count()+degree(qs[i,p])>d or tuple(term) in seen:
                    return False
                seen.add(tuple(term))
                result.symmetric_difference_update(shifted(qs[i,p],m))
            return result=={0}
        fs=cert["functional"]
        if not isinstance(fs,list) or any(type(m) is not int or not 0<=m<1<<h or m.bit_count()>d for m in fs):
            return False
        functional=set(fs)
        if 0 not in functional or len(functional)!=len(fs):
            return False
        return all(len(functional&shifted(q,m))%2==0
                   for q in qs.values() for m in monomials(h,d-degree(q)))
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def separation():
    ds,rs=encode(two_cycles(3,3))
    lo=refute(ds,rs,2)
    hi=refute(ds,rs,3)
    assert lo["kind"]=="no_refutation" and hi["kind"]=="refutation"
    assert check_degree(ds,rs,lo) and check_degree(ds,rs,hi)
    return {"blocks":len(ds),"minimum_static_degree":3,"lower":lo,"upper":hi}

def evidence():
    sep=separation()
    cases=[]
    for m in (3,5,7):
        ds,rs,q=rm_instance(m)
        stats={}
        cert=refute(ds,rs,2,stats=stats)
        assert cert["kind"]=="refutation" and check_degree(ds,rs,cert)
        cases.append({"blocks":len(ds),"recovery_order_lower":q["minimum_order_lower"],
                      "degree_upper":2,"stats":stats,"proof_terms":len(cert["terms"]),
                      "certificate":cert,"checker_accepted":True})
    return {"scope":"static Boolean monomial-multiple degree, not dynamic PC",
            "strict_separation":sep,"rm_cases":cases}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
