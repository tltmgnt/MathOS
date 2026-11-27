"""Theorem K: bounded-order joint affine recovery and strict order hierarchy.

Retain original nonlinear domains. Only add consequences justified by
joint local reachability. Verification uses independent augmented rank.
"""
from itertools import combinations, product
import json
from mathos.research.pnp_overlap_boundary import project, affine_solve, independent_forms
from mathos.research.pnp_overlap_adaptive import point_rows, _consistent
from mathos.research.pnp_overlap_certificates import _relation, _witness_ok
from mathos.research.pnp_overlap_obstructions import inputs
from mathos.research.pnp_overlap_semantic import solve_semantic, check_semantic

def _subsets(n,order):
    for size in range(1,min(n,order)+1):
        yield from combinations(range(n),size)

def _live(width,rows,rel,ids,consistent):
    """Packed local points, with exactly the indicated local restrictions."""
    result=[]
    for values in product(*(sorted(rel[i]) for i in ids)):
        pins=[row for i,v in zip(ids,values) for row in point_rows(i,v)]
        if consistent(width,rows+pins):
            result.append(sum(v<<(2*j) for j,v in enumerate(values)))
    return result

def _global(local,ids):
    return sum(((local>>(2*j))&3)<<(2*i) for j,i in enumerate(ids))

def recover(domains,rows,order,*,stats=None):
    """Return strengthened rows, justification trace and optional empty subset."""
    ds,rs=inputs(domains,rows)
    if type(order) is not int or order<1:
        raise ValueError("positive recovery order required")
    width=2*len(ds)
    current=list(rs)
    rel=[project(*d) for d in ds]
    trace=[]
    count={"rounds":0,"subset_checks":0,"tuple_checks":0,"added_rows":0}
    if stats is not None:
        stats.clear()
        stats.update(count)
        count=stats
    def consistent(w,rs):
        count["tuple_checks"]+=1
        return affine_solve(w,rs) is not None
    if affine_solve(width,current) is None:
        return current,trace,None
    while True:
        count["rounds"]+=1
        changed=False
        for ids in _subsets(len(ds),order):
            count["subset_checks"]+=1
            live=_live(width,current,rel,ids,consistent)
            if not live:
                return current,trace,list(ids)
            for local in range(1,1<<(2*len(ids))):
                rhs=(local&live[0]).bit_count()%2
                if any((local&v).bit_count()%2!=rhs for v in live):
                    continue
                mask=_global(local,ids)
                if independent_forms(width,current,[mask]):
                    current.append((mask,rhs))
                    trace.append({"components":list(ids),"row":[mask,rhs]})
                    count["added_rows"]+=1
                    changed=True
                    break
            if changed:
                break
        if not changed:
            return current,trace,None

def solve_recovered(domains,rows,order=2,*,stats=None):
    ds,rs=inputs(domains,rows)
    current,trace,empty=recover(ds,rs,order,stats=stats)
    if empty is not None:
        return {"kind":"local_unsat","order":order,"trace":trace,"components":empty}
    proof=solve_semantic(ds,current)
    if proof["kind"]=="sat":
        if not _witness_ok(ds,rs,proof["witness"]):
            raise AssertionError("invalid original witness")
        return {"kind":"sat","order":order,"trace":trace,"witness":proof["witness"]}
    return {"kind":"derived_unsat","order":order,"trace":trace,"proof":proof}

def check_recovered(domains,rows,cert):
    """Check each derived equation against original local relations and prior rows.

    The verifier need not establish that recovery reached a fixed point.
    Claimed order is an upper bound on scope, not a minimum-order certificate.
    """
    try:
        ds,rs=inputs(domains,rows)
        if not isinstance(cert,dict):
            return False
        order=cert.get("order")
        trace=cert.get("trace")
        if type(order) is not int or order<1 or not isinstance(trace,list):
            return False
        width=2*len(ds)
        rel=[_relation(d) for d in ds]
        current=list(rs)
        def good_ids(ids):
            return (isinstance(ids,list) and 1<=len(ids)<=order and
                    all(type(i) is int and 0<=i<len(ds) for i in ids) and
                    ids==sorted(set(ids)))
        def live(ids):
            # Independently check original pinning equations by augmented rank.
            out=[]
            for vals in product(*(sorted(rel[i]) for i in ids)):
                pins=[]
                packed=0
                for i,v in zip(ids,vals):
                    pins.extend(((1<<(2*i),v&1),(1<<(2*i+1),v>>1)))
                    packed|=v<<(2*i)
                if _consistent(width,current+pins):
                    out.append(packed)
            return out
        for step in trace:
            if not isinstance(step,dict) or set(step)!={"components","row"}:
                return False
            ids,row=step["components"],step["row"]
            if not good_ids(ids) or not isinstance(row,list) or len(row)!=2:
                return False
            m,b=row
            if type(m) is not int or m<=0 or m&sum(3<<(2*i) for i in ids)!=m or type(b) is not int or b not in (0,1):
                return False
            vals=live(ids)
            if not vals or any((m&v).bit_count()%2!=b for v in vals):
                return False
            current.append((m,b))
        kind=cert.get("kind")
        common={"kind","order","trace"}
        if kind=="sat":
            return set(cert)==common|{"witness"} and _witness_ok(ds,rs,cert["witness"])
        if kind=="local_unsat":
            ids=cert.get("components")
            return set(cert)==common|{"components"} and good_ids(ids) and not live(ids)
        if kind=="derived_unsat":
            p=cert.get("proof")
            return (set(cert)==common|{"proof"} and isinstance(p,dict)
                    and p.get("kind") in ("affine_unsat","derived_unsat")
                    and check_semantic(ds,current,p))
        return False
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def hierarchy_instance(r):
    """Two implication paths x -> not x and not x -> x, each r+1 edges.

    Each edge is a local implication triple v implies u. Occurrence
    consistency is expressed solely by affine rows on output coordinates.
    """
    if type(r) is not int or r<1:
        raise ValueError("positive hierarchy order required")
    paths=[[(0,0)]+[(j,0) for j in range(1,r+1)]+[(0,1)],
           [(0,1)]+[(j,0) for j in range(r+1,2*r+1)]+[(0,0)]]
    ds=[]
    rows=[]
    reps={}
    for path in paths:
        for antecedent,consequent in zip(path,path[1:]):
            i=len(ds)
            ds.append((10,15))
            for pos,(var,neg) in enumerate((consequent,antecedent)):
                coord=2*i+pos
                if var in reps:
                    j,old=reps[var]
                    rows.append(((1<<coord)|(1<<j),neg^old))
                else:
                    reps[var]=(coord,neg)
    return ds,rows

def evidence():
    cases=[]
    for r in (1,2,3):
        ds,rs=hierarchy_instance(r)
        weak,strong={},{}
        current,trace,empty=recover(ds,rs,r,stats=weak)
        assert not trace and empty is None and current==rs
        cert=solve_recovered(ds,rs,r+1,stats=strong)
        assert cert["kind"]=="local_unsat" and check_recovered(ds,rs,cert)
        cases.append({"weaker_order":r,"stronger_order":r+1,"blocks":len(ds),
                      "weak":weak,"strong":strong,"certificate":cert,
                      "certificate_bytes":len(json.dumps(cert,separators=(",",":")).encode()),
                      "checker_accepted":True})
    return {"scope":"bounded-order affine recovery only; no SAT lower bound or novelty claim","cases":cases}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
