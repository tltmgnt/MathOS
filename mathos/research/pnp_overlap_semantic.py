"""Theorem J: canonical affine factorization with original-row provenance."""
from itertools import product
import json
from mathos.research.pnp_overlap_obstructions import inputs, factors, restrict, support
from mathos.research.pnp_overlap_adaptive import solve_adaptive, check_adaptive
from mathos.research.pnp_overlap_certificates import _rank, _witness_ok, contradiction_demo

def reduce_rows(width, rows):
    """RREF of coefficient rows with RHS and provenance; detect 0=1."""
    work=[(m,b,1<<i) for i,(m,b) in enumerate(rows)]
    n=0
    for j in range(width):
        pivot=next((i for i in range(n,len(work)) if (work[i][0]>>j)&1),None)
        if pivot is None:
            continue
        work[n],work[pivot]=work[pivot],work[n]
        a,c,w=work[n]
        for i,(m,b,v) in enumerate(work):
            if i!=n and (m>>j)&1:
                work[i]=(m^a,b^c,v^w)
        n+=1
    for m,b,w in work[n:]:
        if b:
            return None,w
    return work[:n],None

def indices(mask):
    return [i for i in range(mask.bit_length()) if (mask>>i)&1]

def solve_semantic(domains,rows,*,stats=None):
    ds,rs=inputs(domains,rows)
    width=2*len(ds)
    count={"explicit_factors":len(factors(len(ds),rs)),"canonical_factors":None,
           "nodes":0,"splits":0,"optimizer_nodes":0,"affine_calls":0,"propagations":0}
    if stats is not None:
        stats.clear()
        stats.update(count)
        count=stats
    reduced,bad=reduce_rows(width,rs)
    if bad is not None:
        return {"kind":"affine_unsat","dual":indices(bad)}
    canon=[(m,b) for m,b,w in reduced]
    groups=factors(len(ds),canon)
    count["canonical_factors"]=len(groups)
    witness=[None]*len(ds)
    for ids in groups:
        subds,subrows=restrict(ds,canon,ids)
        s={}
        p=solve_adaptive(subds,subrows,stats=s)
        for key in ("nodes","splits","optimizer_nodes","affine_calls","propagations"):
            count[key]+=s[key]
        if p["kind"]!="sat":
            return {"kind":"derived_unsat","components":ids,
                    "rows":[[m,b,indices(w)] for m,b,w in reduced if support(m)<=set(ids)],
                    "proof":p}
        for i,w in zip(ids,p["witness"]):
            witness[i]=w
    if not _witness_ok(ds,rs,witness):
        raise AssertionError("invalid witness")
    return {"kind":"sat","witness":witness}

def row_sum(rows,refs):
    if not isinstance(refs,list) or not refs or any(type(i) is not int or not 0<=i<len(rows) for i in refs):
        raise ValueError("invalid references")
    if len(set(refs))!=len(refs):
        raise ValueError("duplicate references")
    m=b=0
    for i in refs:
        a,c=rows[i]
        m^=a
        b^=c
    return m,b

def check_semantic(domains,rows,cert):
    """Verify original-row consequences and subproblem refutation directly."""
    try:
        ds,rs=inputs(domains,rows)
        if not isinstance(cert,dict):
            return False
        kind=cert.get("kind")
        if kind=="sat":
            return set(cert)=={"kind","witness"} and _witness_ok(ds,rs,cert["witness"])
        if kind=="affine_unsat":
            return set(cert)=={"kind","dual"} and row_sum(rs,cert["dual"])==(0,1)
        if kind!="derived_unsat" or set(cert)!={"kind","components","rows","proof"}:
            return False
        ids=cert["components"]
        if not isinstance(ids,list) or not ids or any(type(i) is not int or not 0<=i<len(ds) for i in ids):
            return False
        if ids!=sorted(set(ids)) or not isinstance(cert["rows"],list):
            return False
        allowed=sum(3<<(2*i) for i in ids)
        local=[]
        for item in cert["rows"]:
            if not isinstance(item,list) or len(item)!=3:
                return False
            m,b,refs=item
            if type(m) is not int or m<=0 or m&allowed!=m or type(b) is not int or b not in (0,1):
                return False
            if row_sum(rs,refs)!=(m,b):
                return False
            local.append((sum(((m>>(2*i))&3)<<(2*j) for j,i in enumerate(ids)),b))
        p=cert["proof"]
        return isinstance(p,dict) and p.get("kind") in ("empty","unsat") and check_adaptive([ds[i] for i in ids],local,p)
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def hidden_instance(k):
    """Mix each independent two-block equality with one core row."""
    if type(k) is not int or k<0:
        raise ValueError("nonnegative factor count required")
    ds,rs=contradiction_demo()
    core=[(m<<(4*k),b) for m,b in rs]
    anchor,rhs=core[0]
    mixed=[((1<<(4*i))^(1<<(4*i+2))^anchor,rhs) for i in range(k)]
    return [(10,15)]*(2*k)+ds,mixed+core

def evidence(k=5):
    ds,rs=hidden_instance(k)
    a,b={},{}
    p=solve_adaptive(ds,rs,stats=a)
    q=solve_semantic(ds,rs,stats=b)
    assert p["kind"]=="unsat" and check_adaptive(ds,rs,p)
    assert q["kind"]=="derived_unsat" and check_semantic(ds,rs,q)
    assert (b["explicit_factors"],b["canonical_factors"])==(1,k+1)
    assert a["nodes"]==(1<<(k+2))-1 and b["nodes"]==2*k+3
    return {"scope":"structured row-mixing control; no runtime or novelty claim",
            "components":len(ds),"hidden_sat_factors":k,"monolithic":a,"semantic":b,
            "monolithic_certificate_bytes":len(json.dumps(p,separators=(",",":")).encode()),
            "semantic_certificate_bytes":len(json.dumps(q,separators=(",",":")).encode()),
            "checker_accepted":True,"certificate":q}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
