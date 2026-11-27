"""Theorem L: exact recovery threshold, streaming affine hull, and certificates."""
from itertools import combinations, product
import json
from mathos.research.pnp_overlap_boundary import project, affine_solve, independent_forms
from mathos.research.pnp_overlap_recovery import check_recovered, hierarchy_instance
from mathos.research.pnp_overlap_obstructions import inputs
from mathos.research.pnp_overlap_semantic import reduce_rows, indices, check_semantic
from mathos.research.pnp_overlap_certificates import _rank, _relation, _witness_ok
from mathos.research.pnp_overlap_adaptive import _consistent

def subsets(c,r):
    for s in range(1,min(c,r)+1):
        yield from combinations(range(c),s)

def global_mask(mask,ids):
    return sum(((mask>>(2*j))&3)<<(2*i) for j,i in enumerate(ids))

def pins(ids,values):
    return [(1<<(2*i+j),(v>>j)&1) for i,v in zip(ids,values) for j in (0,1)]

def insert(basis,m):
    while m:
        p=m.bit_length()-1
        if p not in basis:
            basis[p]=m
            return
        m^=basis[p]

def local_hull(width,current,rel,ids,count):
    """Anchor and difference basis; stop if the entire affine projection is spanned."""
    coords=[1<<(2*i+j) for i in ids for j in (0,1)]
    dim=len(independent_forms(width,current,coords))
    origin=None
    basis={}
    for values in product(*(sorted(rel[i]) for i in ids)):
        count["tuple_checks"]+=1
        if affine_solve(width,current+pins(ids,values)) is None:
            continue
        point=sum(v<<(2*j) for j,v in enumerate(values))
        if origin is None:
            origin=point
        else:
            insert(basis,origin^point)
        if len(basis)==dim:
            count["full_hull_shortcuts"]+=1
            break
    return origin,basis,dim

def annihilator(width,basis):
    """Basis for the nullspace of the difference matrix, by free columns."""
    reduced,bad=reduce_rows(width,[(m,0) for m in basis.values()])
    if bad is not None:
        raise AssertionError("homogeneous system inconsistent")
    pivots={(m&-m).bit_length()-1 for m,b,w in reduced}
    free=[j for j in range(width) if j not in pivots]
    rows=[(m,b) for m,b,w in reduced]
    for j in free:
        v=affine_solve(width,rows+[(1<<i,int(i==j)) for i in free])
        if v is None:
            raise AssertionError("invalid nullspace construction")
        yield v

def recover_fast(domains,rows,order,*,stats=None):
    ds,rs=inputs(domains,rows)
    if type(order) is not int or order<0:
        raise ValueError("nonnegative order required")
    width=2*len(ds)
    current=list(rs)
    rel=[project(*d) for d in ds]
    trace=[]
    count={"rounds":0,"subset_checks":0,"tuple_checks":0,"added_rows":0,"full_hull_shortcuts":0}
    if stats is not None:
        stats.clear()
        stats.update(count)
        count=stats
    if affine_solve(width,current) is None:
        return current,trace,None
    while True:
        count["rounds"]+=1
        changed=False
        for ids in subsets(len(ds),order):
            count["subset_checks"]+=1
            anchor,basis,dim=local_hull(width,current,rel,ids,count)
            if anchor is None:
                return current,trace,list(ids)
            if len(basis)==dim:
                continue
            for form in annihilator(2*len(ids),basis):
                mask=global_mask(form,ids)
                if independent_forms(width,current,[mask]):
                    rhs=(form&anchor).bit_count()%2
                    current.append((mask,rhs))
                    trace.append({"components":list(ids),"row":[mask,rhs]})
                    count["added_rows"]+=1
                    changed=True
                    break
            if changed:
                break
            raise AssertionError("strict hull shrinkage must yield a new row")
        if not changed:
            return current,trace,None

def minimum_order(domains,rows,*,stats=None):
    """0 = inconsistent original affine system; None = satisfiable.

    Exponential search then binary search; lower certificate is a closed
    consistent affine subspace of the original relaxation at order r*-1.
    """
    ds,rs=inputs(domains,rows)
    c=len(ds)
    report={"probes":[],"tuple_checks":0}
    if stats is not None:
        stats.clear()
        stats.update(report)
        report=stats
    _,bad=reduce_rows(2*c,rs)
    if bad is not None:
        return {"minimum":0,"upper":{"kind":"affine_unsat","dual":indices(bad)},"lower":None}
    cache={0:(list(rs),[],None)}
    def probe(r):
        if r not in cache:
            s={}
            cache[r]=recover_fast(ds,rs,r,stats=s)
            report["probes"].append(r)
            report["tuple_checks"]+=s["tuple_checks"]
        return cache[r][2] is not None
    lo=0
    hi=min(1,c)
    while hi<c and not probe(hi):
        lo=hi
        hi=min(c,2*hi)
    if not probe(hi):
        # Full-order non-detection implies a full locally allowed tuple exists.
        rel=[project(*d) for d in ds]
        current=cache[hi][0]
        for values in product(*(sorted(r) for r in rel)):
            report["tuple_checks"]+=1
            if affine_solve(2*c,current+pins(range(c),values)) is not None:
                return {"minimum":None,"witness":[list(r[v]) for r,v in zip(rel,values)]}
        raise AssertionError("full-order non-detection without witness")
    while hi-lo>1:
        mid=(hi+lo)//2
        if probe(mid):
            hi=mid
        else:
            lo=mid
    _,trace,empty=cache[hi]
    return {"minimum":hi,"upper":{"kind":"local_unsat","order":hi,"trace":trace,"components":empty},
            "lower":{"order":lo,"rows":[list(r) for r in cache[lo][0]]}}

def closed_check(ds,rs,lower,order):
    """Independent check of a nonempty closed affine subspace; no solver calls."""
    if not isinstance(lower,dict) or set(lower)!={"order","rows"} or type(lower["order"]) is not int or lower["order"]!=order:
        return False
    if not isinstance(lower["rows"],list) or any(not isinstance(r,list) for r in lower["rows"]):
        return False
    _,current=inputs(ds,lower["rows"])
    current=list(current)
    width=2*len(ds)
    if not _consistent(width,current):
        return False
    augmented=[m|(b<<width) for m,b in current]
    rank=_rank(width+1,augmented)
    if any(_rank(width+1,augmented+[m|(b<<width)])!=rank for m,b in rs):
        return False
    base=[m for m,b in current]
    base_rank=_rank(width,base)
    rel=[_relation(d) for d in ds]
    for ids in subsets(len(ds),order):
        columns=[1<<(2*i+j) for i in ids for j in (0,1)]
        target=_rank(width,base+columns)-base_rank
        anchor=None
        diffs=[]
        for values in product(*(sorted(rel[i]) for i in ids)):
            fixed=[(1<<(2*i+j),(v>>j)&1) for i,v in zip(ids,values) for j in (0,1)]
            if not _consistent(width,current+fixed):
                continue
            p=sum(v<<(2*j) for j,v in enumerate(values))
            if anchor is None:
                anchor=p
            else:
                v=anchor^p
                if _rank(2*len(ids),diffs+[v])>len(diffs):
                    diffs.append(v)
            if len(diffs)==target:
                break
        if anchor is None or len(diffs)!=target:
            return False
    return True

def check_minimum(domains,rows,cert):
    try:
        ds,rs=inputs(domains,rows)
        if not isinstance(cert,dict) or "minimum" not in cert:
            return False
        r=cert["minimum"]
        if r is None:
            return set(cert)=={"minimum","witness"} and _witness_ok(ds,rs,cert["witness"])
        if type(r) is not int or not 0<=r<=len(ds) or set(cert)!={"minimum","upper","lower"}:
            return False
        upper=cert["upper"]
        if not isinstance(upper,dict):
            return False
        if r==0:
            return cert["lower"] is None and upper.get("kind")=="affine_unsat" and check_semantic(ds,rs,upper)
        return (upper.get("kind")=="local_unsat" and upper.get("order")==r
                and check_recovered(ds,rs,upper) and closed_check(ds,rs,cert["lower"],r-1))
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def evidence():
    cases=[]
    for r in (1,2,3):
        ds,rs=hierarchy_instance(r)
        stats={}
        cert=minimum_order(ds,rs,stats=stats)
        assert cert["minimum"]==r+1 and check_minimum(ds,rs,cert)
        cases.append({"blocks":len(ds),"minimum":cert["minimum"],"stats":stats,
                      "certificate_bytes":len(json.dumps(cert,separators=(",",":")).encode()),
                      "certificate":cert,"checker_accepted":True})
    return {"scope":"minimum order of the specified closure, not SAT complexity measure","cases":cases}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
