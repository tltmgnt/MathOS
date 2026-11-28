"""Theorem T: bounded dynamic Boolean inference and a checked hybrid portfolio.

Multiplication is charged before reduction: deg(p)+1 <= d.
This is a specified restricted dynamic system, not all variants of PC.
"""
from itertools import product
import json
from mathos.research.pnp_overlap_degree import (
    monomials,count_monomials,degree,multiply,polynomials,checker_polynomials,refute,check_degree)
from mathos.research.pnp_overlap_algebraic import frame
from mathos.research.pnp_overlap_obstructions import inputs
from mathos.research.pnp_overlap_semantic import reduce_rows,indices,solve_semantic,check_semantic
from mathos.research.pnp_overlap_certificates import _rank,_relation,_witness_ok
from mathos.research.pnp_overlap_adaptive import _consistent
from mathos.research.pnp_overlap_order import recover_fast,closed_check
from mathos.research.pnp_overlap_recovery import check_recovered
from mathos.research.pnp_overlap_order_bounds import encode
from mathos.research.pnp_overlap_boundary import reduce_3sat
from mathos.research.pnp_overlap_pebbling import chain
from mathos.research.pnp_overlap_quadratic import rm_instance

MAX_DYNAMIC_MONOMIALS=4096
MAX_ORDER=3
MAX_TRACE=2*MAX_DYNAMIC_MONOMIALS**2

def space(h,d):
    if type(d) is not int or not 0<=d<=h+2:
        raise ValueError("invalid dynamic degree")
    if count_monomials(h,d)>MAX_DYNAMIC_MONOMIALS:
        raise ValueError("dynamic monomial budget exceeded")
    return list(monomials(h,d))

def dynamic(domains,rows,d,*,stats=None):
    ds,rs=inputs(domains,rows)
    if type(d) is not int or d<0:
        raise ValueError("nonnegative degree required")
    fr=frame(2*len(ds),rs)
    if fr is None:
        _,bad=reduce_rows(2*len(ds),rs)
        return {"kind":"affine_unsat","dual":indices(bad)}
    a,dirs=fr
    h=len(dirs)
    ms=space(h,d)
    idx={m:i for i,m in enumerate(ms)}
    qs=polynomials(ds,a,dirs)
    basis={}
    lines=[]
    def bits(q):
        return sum(1<<idx[m] for m in q)
    def terms(v):
        while v:
            b=v&-v
            yield ms[b.bit_length()-1]
            v^=b
    def add(v,rule):
        raw=v
        used=[]
        while v:
            p=v.bit_length()-1
            if p not in basis:
                break
            w,j=basis[p]
            v^=w
            used.append(j)
        if not v:
            return False
        j=len(lines)
        lines.append(rule)
        for k in used:
            lines.append(["xor",j,k])
            j=len(lines)-1
        basis[v.bit_length()-1]=(v,j)
        return True
    common={"anchor":a,"directions":dirs,"degree":d}
    def finish():
        if stats is not None:
            stats.clear()
            stats.update({"dimension":h,"monomials":len(ms),"rank":len(basis),"proof_lines":len(lines)})
        if 0 in basis:
            # Last independent insertion is the constant.
            return {"kind":"dynamic_refutation",**common,"lines":lines}
        return {"kind":"dynamic_closed",**common,
                "basis":[sorted(terms(v)) for v,j in basis.values()]}
    for (i,p),q in qs.items():
        if degree(q)<=d:
            add(bits(q),["axiom",i,p])
            if 0 in basis:
                return finish()
    # In degree-ordered echelon form, rows with low pivots span
    # the entire intersection with the space of degree <= d-1.
    while True:
        changed=False
        for p,(v,j) in list(basis.items()):
            if ms[p].bit_count()>=d:
                continue
            q=set(terms(v))
            for k in range(h):
                if add(bits(multiply(q,{1<<k})),["mul",j,k]):
                    changed=True
                    if 0 in basis:
                        return finish()
        if not changed:
            return finish()

def check_dynamic(domains,rows,cert):
    try:
        ds,rs=inputs(domains,rows)
        if not isinstance(cert,dict):
            return False
        kind=cert.get("kind")
        if kind=="affine_unsat":
            return check_semantic(ds,rs,cert)
        key="lines" if kind=="dynamic_refutation" else "basis"
        if kind not in ("dynamic_refutation","dynamic_closed") or set(cert)!={"kind","anchor","directions","degree",key}:
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
        ms=space(h,d)
        qs=checker_polynomials(ds,a,dirs)
        def times(q,k):
            out=set()
            for m in q:
                r=m|(1<<k)
                if r in out:
                    out.remove(r)
                else:
                    out.add(r)
            return out
        if kind=="dynamic_refutation":
            lines=cert["lines"]
            if not isinstance(lines,list) or not 1<=len(lines)<=MAX_TRACE:
                return False
            proved=[]
            for line in lines:
                if not isinstance(line,list) or len(line)!=3 or any(type(v) is not int for v in line[1:]):
                    return False
                op,i,j=line
                if op=="axiom" and (i,j) in qs:
                    q=qs[i,j]
                elif op=="xor" and 0<=i<len(proved) and 0<=j<len(proved):
                    q=proved[i]^proved[j]
                elif op=="mul" and 0<=i<len(proved) and 0<=j<h and degree(proved[i])<d:
                    q=times(proved[i],j)
                else:
                    return False
                if degree(q)>d:
                    return False
                proved.append(q)
            return proved[-1]=={0}
        # Independent echelon checks using sets of actual monomial masks.
        order={m:i for i,m in enumerate(ms)}
        raw=cert["basis"]
        if not isinstance(raw,list) or len(raw)>len(ms):
            return False
        pivots={}
        for row in raw:
            if not isinstance(row,list) or not row or any(type(m) is not int or m not in order for m in row):
                return False
            q=set(row)
            if len(q)!=len(row):
                return False
            p=max(q,key=order.__getitem__)
            if p in pivots:
                return False
            pivots[p]=q
        def contains(q):
            q=set(q)
            while q:
                p=max(q,key=order.__getitem__)
                if p not in pivots:
                    return False
                q^=pivots[p]
            return True
        if contains({0}) or any(not contains(q) for q in qs.values() if degree(q)<=d):
            return False
        return all(contains(times(q,k)) for q in pivots.values() if degree(q)<d for k in range(h))
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def hybrid(domains,rows,order=1,d=2,*,fallback=False):
    """Bounded portfolio on an enriched affine relaxation; optional exact fallback."""
    ds,rs=inputs(domains,rows)
    if type(order) is not int or not 1<=order<=MAX_ORDER or type(d) is not int or d<0 or type(fallback) is not bool:
        raise ValueError("invalid hybrid budget")
    _,bad=reduce_rows(2*len(ds),rs)
    if bad is not None:
        return {"kind":"affine_unsat","dual":indices(bad)}
    current,trace,empty=recover_fast(ds,rs,order)
    if empty is not None:
        return {"kind":"local_unsat","order":order,"trace":trace,"components":empty}
    h=2*len(ds)-_rank(2*len(ds),[m for m,b in current])
    d=min(d,h+2)
    common={"order":order,"trace":trace,"degree":d}
    try:
        s=refute(ds,current,d)
        if s["kind"]=="refutation":
            return {"kind":"static",**common,"proof":s}
        p=dynamic(ds,current,d)
        if p["kind"]=="dynamic_refutation":
            return {"kind":"dynamic",**common,"proof":p}
        if not fallback:
            return {"kind":"inconclusive",**common,"static":s,"dynamic":p}
    except ValueError:
        if not fallback:
            raise
    return {"kind":"fallback",**common,"proof":solve_semantic(ds,current)}

def checked_trace(ds,rs,order,trace):
    """Replay learned affine consequences independently, in original coordinates."""
    if type(order) is not int or not 1<=order<=MAX_ORDER or not isinstance(trace,list) or len(trace)>2*len(ds):
        return None
    current=list(rs)
    w=2*len(ds)
    rel=[_relation(d) for d in ds]
    for step in trace:
        if not isinstance(step,dict) or set(step)!={"components","row"}:
            return None
        ids,row=step["components"],step["row"]
        if not isinstance(ids,list) or not 1<=len(ids)<=order or any(type(i) is not int or not 0<=i<len(ds) for i in ids) or ids!=sorted(set(ids)):
            return None
        if not isinstance(row,list) or len(row)!=2:
            return None
        m,b=row
        if type(m) is not int or m<=0 or m&sum(3<<(2*i) for i in ids)!=m or type(b) is not int or b not in (0,1):
            return None
        found=False
        for values in product(*(sorted(rel[i]) for i in ids)):
            pins=[(1<<(2*i+j),(v>>j)&1) for i,v in zip(ids,values) for j in (0,1)]
            if _consistent(w,current+pins):
                found=True
                x=sum(v<<(2*i) for i,v in zip(ids,values))
                if (m&x).bit_count()%2!=b:
                    return None
        if not found:
            return None
        current.append((m,b))
    return current

def check_hybrid(domains,rows,cert):
    try:
        ds,rs=inputs(domains,rows)
        if not isinstance(cert,dict):
            return False
        kind=cert.get("kind")
        if kind=="affine_unsat":
            return check_semantic(ds,rs,cert)
        if kind=="local_unsat":
            return type(cert.get("order")) is int and 1<=cert["order"]<=MAX_ORDER and check_recovered(ds,rs,cert)
        common={"kind","order","trace","degree"}
        if kind not in ("static","dynamic","inconclusive","fallback"):
            return False
        if set(cert)!=common|({"static","dynamic"} if kind=="inconclusive" else {"proof"}):
            return False
        d=cert["degree"]
        current=checked_trace(ds,rs,cert["order"],cert["trace"])
        if current is None or type(d) is not int or d<0:
            return False
        if not _consistent(2*len(ds),current):
            return False
        if kind=="inconclusive":
            s,p=cert["static"],cert["dynamic"]
            return (closed_check(ds,rs,{"order":cert["order"],"rows":[list(r) for r in current]},cert["order"])
                    and s.get("kind")=="no_refutation" and s.get("degree")==d and check_degree(ds,current,s)
                    and p.get("kind")=="dynamic_closed" and p.get("degree")==d and check_dynamic(ds,current,p))
        p=cert["proof"]
        if kind=="static":
            return p.get("kind")=="refutation" and p.get("degree")==d and check_degree(ds,current,p)
        if kind=="dynamic":
            return p.get("kind")=="dynamic_refutation" and p.get("degree")==d and check_dynamic(ds,current,p)
        if p.get("kind")=="sat":
            return _witness_ok(ds,rs,p["witness"])
        return check_semantic(ds,current,p)
    except (TypeError,ValueError,KeyError,IndexError,AttributeError,OverflowError):
        return False

def dynamic_only_instance():
    return encode([(1,2),(-1,2),(2,3),(3,4),(3,-4)])

def resistant_instance():
    return reduce_3sat([tuple(s*i for s,i in zip(signs,(1,2,3))) for signs in product((1,-1),repeat=3)])

def evidence():
    cases=[]
    ds,rs,q=rm_instance(5)
    for name,(ds,rs),expected in (
            ("affine",chain(7),"local_unsat"),
            ("static",(ds,rs),"static"),
            ("dynamic",dynamic_only_instance(),"dynamic"),
            ("resistant",resistant_instance(),"inconclusive")):
        cert=hybrid(ds,rs)
        assert cert["kind"]==expected and check_hybrid(ds,rs,cert)
        cases.append({"name":name,"blocks":len(ds),"result":expected,"checker_accepted":True,"certificate":cert})
    ds,rs=resistant_instance()
    p=hybrid(ds,rs,fallback=True)
    assert p["kind"]=="fallback" and p["proof"]["kind"]!="sat" and check_hybrid(ds,rs,p)
    return {"scope":"fixed-budget portfolio, not general polynomial-time SAT",
            "cases":cases,"resistant_exact_fallback":p}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
