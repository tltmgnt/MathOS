"""Theorem N: affine-dimension bounds and algebraic obstruction certificates."""
from itertools import combinations, product
import json
from mathos.research.pnp_overlap_boundary import project, affine_solve, independent_forms
from mathos.research.pnp_overlap_order import annihilator, insert, local_hull, global_mask
from mathos.research.pnp_overlap_obstructions import inputs
from mathos.research.pnp_overlap_semantic import reduce_rows, indices, check_semantic
from mathos.research.pnp_overlap_certificates import _rank, _relation, _witness_ok
from mathos.research.pnp_overlap_recovery import check_recovered

def frame(width,rows):
    reduced,bad=reduce_rows(width,rows)
    if bad is not None:
        return None
    basis={}
    for m,b,w in reduced:
        insert(basis,m)
    return affine_solve(width,rows),list(annihilator(width,basis))

def points(anchor,directions):
    """Enumerate the affine space in Gray-code order, with constant point storage."""
    x=anchor
    yield x
    for j in range(1,1<<len(directions)):
        x^=directions[(j&-j).bit_length()-1]
        yield x

def value(x,i):
    return (x>>(2*i))&3

def packed(x,ids):
    return sum(value(x,i)<<(2*j) for j,i in enumerate(ids))

def initial_closed(anchor,directions,rel,order):
    """Generator-side closure test via streamed points, not local tuple search."""
    for s in range(1,min(order,len(rel))+1):
        for ids in combinations(range(len(rel)),s):
            target={}
            for v in directions:
                insert(target,packed(v,ids))
            first=None
            diffs={}
            for x in points(anchor,directions):
                if not all(value(x,i) in rel[i] for i in ids):
                    continue
                p=packed(x,ids)
                if first is None:
                    first=p
                else:
                    insert(diffs,p^first)
                if len(diffs)==len(target):
                    break
            if first is None or len(diffs)!=len(target):
                return False
    return True

def core_unsat(anchor,directions,rel,ids):
    return all(any(value(x,i) not in rel[i] for i in ids) for x in points(anchor,directions))

def bounds(domains,rows,lower_cap=2,*,max_dimension=16):
    """Return SAT or checked-bound data. Refuse unbudgeted affine enumeration.

    Lower bound tests only the original relaxation, not its full closure.
    Upper core is deletion-minimal, not necessarily minimum cardinality.
    """
    ds,rs=inputs(domains,rows)
    if type(lower_cap) is not int or lower_cap<0 or type(max_dimension) is not int or max_dimension<0:
        raise ValueError("invalid enumeration budget")
    width=2*len(ds)
    fr=frame(width,rs)
    if fr is None:
        _,bad=reduce_rows(width,rs)
        return {"kind":"affine_unsat","dual":indices(bad)}
    a,dirs=fr
    if len(dirs)>max_dimension:
        raise ValueError("affine dimension exceeds explicit enumeration budget")
    rel=[project(*d) for d in ds]
    core=set()
    for x in points(a,dirs):
        i=next((i for i,r in enumerate(rel) if value(x,i) not in r),None)
        if i is None:
            return {"kind":"sat","witness":[list(r[value(x,i)]) for i,r in enumerate(rel)]}
        core.add(i)
    core=sorted(core)
    for i in core[:]:
        trial=[j for j in core if j!=i]
        if core_unsat(a,dirs,rel,trial):
            core=trial
    low=1
    for r in range(1,min(lower_cap,len(core)-1)+1):
        if not initial_closed(a,dirs,rel,r):
            break
        low=r+1
    return {"kind":"bounds","anchor":a,"directions":dirs,"lower":low,
            "upper":len(core),"core":core}

def _checker_points(a,dirs):
    for bits in product((0,1),repeat=len(dirs)):
        x=a
        for v,b in zip(dirs,bits):
            if b:
                x^=v
        yield x

def check_bounds(domains,rows,cert,*,max_dimension=16):
    """Independent frame/rank/coverage verification; does not call bounds."""
    try:
        ds,rs=inputs(domains,rows)
        width=2*len(ds)
        if not isinstance(cert,dict) or type(max_dimension) is not int or max_dimension<0:
            return False
        if cert.get("kind")=="sat":
            return set(cert)=={"kind","witness"} and _witness_ok(ds,rs,cert["witness"])
        if cert.get("kind")=="affine_unsat":
            return check_semantic(ds,rs,cert)
        if cert.get("kind")!="bounds" or set(cert)!={"kind","anchor","directions","lower","upper","core"}:
            return False
        a,dirs,lo,hi,core=(cert[k] for k in ("anchor","directions","lower","upper","core"))
        if type(a) is not int or not 0<=a<1<<width or not isinstance(dirs,list):
            return False
        if len(dirs)>max_dimension or any(type(v) is not int or not 0<v<1<<width for v in dirs):
            return False
        if any((a&m).bit_count()%2!=b for m,b in rs):
            return False
        if any((v&m).bit_count()%2 for v in dirs for m,b in rs):
            return False
        if len(dirs)!=width-_rank(width,[m for m,b in rs]) or _rank(width,dirs)!=len(dirs):
            return False
        if type(lo) is not int or type(hi) is not int or not 1<=lo<=hi<=len(ds):
            return False
        if not isinstance(core,list) or len(core)!=hi or any(type(i) is not int or not 0<=i<len(ds) for i in core):
            return False
        if core!=sorted(set(core)):
            return False
        rel=[_relation(d) for d in ds]
        if any(all(value(x,i) in rel[i] for i in core) for x in _checker_points(a,dirs)):
            return False
        # Verify the original affine space is closed below the claimed lower bound.
        for s in range(1,lo):
            for ids in combinations(range(len(ds)),s):
                target=_rank(2*s,[packed(v,ids) for v in dirs])
                first=None
                diffs=[]
                for x in _checker_points(a,dirs):
                    if not all(value(x,i) in rel[i] for i in ids):
                        continue
                    p=packed(x,ids)
                    if first is None:
                        first=p
                    elif _rank(2*s,diffs+[p^first])>len(diffs):
                        diffs.append(p^first)
                    if len(diffs)==target:
                        break
                if first is None or len(diffs)!=target:
                    return False
        return True
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def gf4_mul(a,b):
    p=0
    while b:
        if b&1:
            p^=a
        b>>=1
        a<<=1
        if a&4:
            a^=7
    return p

def projective_instance(m=3):
    """All projective directions over GF(4), each requiring nonzero dot product."""
    if type(m) is not int or not 2<=m<=3:
        raise ValueError("bounded control uses dimension two or three over GF(4)")
    vectors=[v for v in product(range(4),repeat=m) if next((x for x in v if x),0)==1]
    c=len(vectors)
    a=sum(2<<(2*i) for i in range(c))
    dirs=[]
    for j in range(m):
        for bit in (1,2):
            dirs.append(sum(gf4_mul(v[j],bit)<<(2*i) for i,v in enumerate(vectors)))
    basis={}
    for v in dirs:
        insert(basis,v)
    rows=[(f,(f&a).bit_count()%2) for f in annihilator(2*c,basis)]
    return [(10,15)]*c,rows,vectors

def pencil_proof(domains,rows,vectors):
    """Use four of the five directions in the first two-dimensional pencil."""
    ds,rs=inputs(domains,rows)
    chosen=[i for i,v in enumerate(vectors) if all(x==0 for x in v[2:])]
    if len(chosen)!=5:
        raise AssertionError("expected five pencil directions")
    ids=tuple(chosen[:4])
    last=chosen[4]
    current=list(rs)
    rel=[project(*d) for d in ds]
    trace=[]
    for _ in range(2*len(ds)+1):
        if not any(affine_solve(2*len(ds),current+[(1<<(2*last),v&1),(2<<(2*last),v>>1)]) is not None
                   for v in rel[last]):
            return {"kind":"local_unsat","order":4,"trace":trace,"components":[last]}
        anchor,basis,dim=local_hull(2*len(ds),current,rel,ids,
                                    {"tuple_checks":0,"full_hull_shortcuts":0})
        if anchor is None:
            return {"kind":"local_unsat","order":4,"trace":trace,"components":list(ids)}
        for form in annihilator(8,basis):
            mask=global_mask(form,ids)
            if independent_forms(2*len(ds),current,[mask]):
                rhs=(form&anchor).bit_count()%2
                current.append((mask,rhs))
                trace.append({"components":list(ids),"row":[mask,rhs]})
                break
        else:
            raise AssertionError("pencil did not force final direction")
    raise AssertionError("rank termination")

def evidence():
    ds,rs,vs=projective_instance(3)
    cert=bounds(ds,rs,3)
    upper=pencil_proof(ds,rs,vs)
    assert check_bounds(ds,rs,cert) and check_recovered(ds,rs,upper)
    assert cert["lower"]==4 and upper["order"]==4
    return {"scope":"algebraic control in NP-complete overlap model, not a general SAT lower bound",
            "blocks":len(ds),"affine_dimension":len(cert["directions"]),
            "affine_points":1<<len(cert["directions"]),
            "core_upper":cert["upper"],"exact_minimum":4,
            "lower_certificate":cert,"upper_certificate":upper,"checker_accepted":True}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
