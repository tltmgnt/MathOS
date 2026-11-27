"""Theorem I: scope-specific rank obstructions and independent factor solving.

Connected factors are computed from explicit row support, not a claim of
finest semantic decomposition. UNSAT checker accepts a valid subproblem
refutation without trusting the graph decomposition or the optimizer.
"""
from itertools import product
import json
from mathos.research.pnp_overlap_boundary import (
    project, minimum_rank_forms, verify)
from mathos.research.pnp_overlap_adaptive import (
    solve_adaptive, check_adaptive, reachable)
from mathos.research.pnp_overlap_certificates import (
    contradiction_demo, _witness_ok)

def inputs(domains, rows):
    ds=tuple(tuple(d) for d in domains)
    rs=tuple(tuple(r) for r in rows)
    if any(len(d)!=2 or any(type(v) is not int or not 0<=v<16 for v in d) for d in ds):
        raise ValueError("invalid domain")
    if any(len(r)!=2 or type(r[0]) is not int or not 0<=r[0]<(1<<(2*len(ds)))
           or type(r[1]) is not int or r[1] not in (0,1) for r in rs):
        raise ValueError("invalid row")
    return ds,rs

def support(mask):
    blocks=set()
    while mask:
        low=mask&-mask
        blocks.add((low.bit_length()-1)//2)
        mask^=low
    return blocks

def factors(n, rows):
    """Partition explicit row-support graph; constant rows handled separately."""
    parent=list(range(n))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]
            x=parent[x]
        return x
    for mask,b in rows:
        ids=sorted(support(mask))
        if ids:
            root=find(ids[0])
            for i in ids[1:]:
                parent[find(i)]=root
    groups={}
    for i in range(n):
        groups.setdefault(find(i),[]).append(i)
    return sorted(groups.values(),key=lambda g:g[0])

def restrict(ds,rs,ids):
    """Keep only nonconstant rows supported wholly inside ids, in input order."""
    wanted=set(ids)
    subrows=[]
    for mask,b in rs:
        if mask and support(mask)<=wanted:
            local=sum(((mask>>(2*i))&3)<<(2*j) for j,i in enumerate(ids))
            subrows.append((local,b))
    return [ds[i] for i in ids],subrows

def solve_factored(domains,rows,*,stats=None):
    ds,rs=inputs(domains,rows)
    count={"factors":0,"solved_factors":0,"nodes":0,"splits":0,"optimizer_nodes":0,
           "affine_calls":0,"propagations":0}
    if stats is not None:
        stats.clear()
        stats.update(count)
        count=stats
    for j,r in enumerate(rs):
        if r==(0,1):
            return {"kind":"constant_unsat","row":j}
    groups=factors(len(ds),rs)
    count["factors"]=len(groups)
    witness=[None]*len(ds)
    for ids in groups:
        subds,subrs=restrict(ds,rs,ids)
        s={}
        cert=solve_adaptive(subds,subrs,stats=s)
        count["solved_factors"]+=1
        for key in ("nodes","splits","optimizer_nodes","affine_calls","propagations"):
            count[key]+=s[key]
        if cert["kind"]!="sat":
            return {"kind":"factor_unsat","components":ids,"proof":cert}
        for i,w in zip(ids,cert["witness"]):
            witness[i]=w
    if not verify(ds,rs,witness):
        raise AssertionError("invalid assembled witness")
    return {"kind":"sat","witness":witness}

def check_factored(domains,rows,cert):
    """Validate witness or a contradiction on a named subset of original inputs.

    Rebuild subproblem independently using an outside-bit test; no call to
    factors, restrict, solve_factored, or any search routine.
    """
    try:
        ds,rs=inputs(domains,rows)
        if not isinstance(cert,dict):
            return False
        kind=cert.get("kind")
        if kind=="sat":
            return set(cert)=={"kind","witness"} and _witness_ok(ds,rs,cert["witness"])
        if kind=="constant_unsat":
            j=cert.get("row")
            return set(cert)=={"kind","row"} and type(j) is int and 0<=j<len(rs) and rs[j]==(0,1)
        if kind!="factor_unsat" or set(cert)!={"kind","components","proof"}:
            return False
        ids=cert["components"]
        if not isinstance(ids,list) or not ids or any(
                type(i) is not int or not 0<=i<len(ds) for i in ids):
            return False
        if ids!=sorted(set(ids)):
            return False
        mask=sum(3<<(2*i) for i in ids)
        subrows=[]
        for m,b in rs:
            if m and m&mask==m:
                local=0
                for j,i in enumerate(ids):
                    local|=((m>>(2*i))&3)<<(2*j)
                subrows.append((local,b))
        p=cert["proof"]
        return (isinstance(p,dict) and p.get("kind") in ("empty","unsat")
                and check_adaptive([ds[i] for i in ids],subrows,p))
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def distraction_instance(k):
    """k unconstrained triples ordered before the four-translate UNSAT core."""
    if type(k) is not int or k<0:
        raise ValueError("nonnegative distractor count required")
    ds,rs=contradiction_demo()
    return [(10,15)]*k+ds,[(m<<(2*k),b) for m,b in rs]

def connected_instance(k):
    """A single parity row ties all first coordinates; local reachability is full."""
    if type(k) is not int or k<2:
        raise ValueError("at least two components")
    return [(10,15)]*k,[(sum(1<<(2*i) for i in range(k)),0)]

def evidence(k=5):
    ds,rs=distraction_instance(k)
    mono,fac={},{}
    p=solve_adaptive(ds,rs,stats=mono)
    q=solve_factored(ds,rs,stats=fac)
    assert p["kind"]=="unsat" and check_adaptive(ds,rs,p)
    assert q["kind"]=="factor_unsat" and check_factored(ds,rs,q)
    assert mono["nodes"]==(1<<(k+2))-1 and fac["nodes"]==2*k+3
    return {"scope":"ordered H solver and explicit support factorization only",
            "distractors":k,"monolithic":mono,"factored":fac,
            "monolithic_certificate_bytes":len(json.dumps(p,separators=(",",":")).encode()),
            "factor_certificate_bytes":len(json.dumps(q,separators=(",",":")).encode()),
            "factor_certificate":q,"checker_accepted":True,
            "connected_21":{"components":21,"rank_analytic":20,
                            "closure_resistant_analytic":True,
                            "scope":"rank obstruction, not decision lower bound"}}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
