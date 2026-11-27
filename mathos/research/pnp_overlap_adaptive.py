"""Theorem H: adaptive affine propagation and rank-sensitive search.

UNSAT is certified by a preorder binary tree; a separate checker reconstructs
all propagation steps using augmented rank, not solver or optimizer calls.
"""
from itertools import product
import json
from mathos.research.pnp_overlap_boundary import (
    project, affine_rows, affine_solve, minimum_rank_forms, verify)
from mathos.research.pnp_overlap_certificates import (
    _dual, _dual_ok, _rank, _relation, _rows, _witness_ok)

def point_rows(i,v):
    return [(1<<(2*i),v&1),(2<<(2*i),v>>1)]

def local_rows(i,rel,encode):
    return [(m<<(2*i),b) for m,b in encode(rel)]

def reachable(width,rows,i,rel):
    return {v for v in rel if affine_solve(width,rows+point_rows(i,v)) is not None}

def solve_adaptive(domains, rows, *, stats=None):
    """Return a certificate and counters. Explicit UNSAT proof may be exponential."""
    ds,rows=tuple(domains),list(rows)
    width=2*len(ds)
    if any(type(m) is not int or not 0<=m<(1<<width) or type(b) is not int
           or b not in (0,1) for m,b in rows):
        raise ValueError("invalid affine row")
    rel=[project(*d) for d in ds]
    count={"nodes":0,"splits":0,"propagations":0,"optimizer_nodes":0,
           "affine_calls":0,"max_depth":0,"root_rank":None}
    if stats is not None:
        stats.clear()
        stats.update(count)
        count=stats
    if any(not r for r in rel):
        return {"kind":"empty","index":next(i for i,r in enumerate(rel) if not r)}
    fixed=rows+[row for i,r in enumerate(rel) if len(r)!=3 for row in local_rows(i,r,affine_rows)]
    pending=tuple(i for i,r in enumerate(rel) if len(r)==3)
    stack=[(fixed,pending,0)]
    proof=[]
    while stack:
        current,remaining,depth=stack.pop()
        remaining=list(remaining)
        trace=[]
        count["nodes"]+=1
        count["max_depth"]=max(count["max_depth"],depth)
        while True:
            count["affine_calls"]+=1
            rep=affine_solve(width,current)
            if rep is None:
                proof.append({"trace":trace,"kind":"dual","dual":_dual(current)})
                break
            progressed=False
            for i in remaining:
                count["affine_calls"]+=3
                live=reachable(width,current,i,rel[i])
                if not live:
                    proof.append({"trace":trace,"kind":"empty_local","index":i})
                    progressed=True
                    break
                if len(live)<3:
                    current=current+local_rows(i,live,affine_rows)
                    remaining.remove(i)
                    trace.append(i)
                    count["propagations"]+=1
                    progressed=True
                    break
            else:
                if not remaining:
                    witness=[list(r[(rep>>(2*i))&3]) for i,r in enumerate(rel)]
                    if not verify(ds,rows,witness):
                        raise AssertionError("invalid witness")
                    return {"kind":"sat","witness":witness}
                groups=[tuple(m<<(2*i) for m in (1,2,3)) for i in remaining]
                opt=minimum_rank_forms(width,current,groups)
                count["optimizer_nodes"]+=opt["search_nodes"]
                if depth==0:
                    count["root_rank"]=opt["d"]
                if opt["d"]==0:
                    raise AssertionError("unpropagated fixed form")
                form=opt["forms"][0]
                proof.append({"trace":trace,"kind":"split","form":form})
                count["splits"]+=1
                for b in (1,0):
                    stack.append((current+[(form,b)],tuple(remaining),depth+1))
                break
            if progressed and (not live):
                break
            # A successful propagation restarts the scan and consistency check.
    return {"kind":"unsat","tree":proof}

def _consistent(width,rows):
    return _rank(width,[m for m,b in rows])==_rank(width+1,[m|(b<<width) for m,b in rows])

def check_adaptive(domains,rows,cert):
    """Independent arithmetic checks; no calls to solve_adaptive or optimizer."""
    try:
        ds,rows=tuple(tuple(d) for d in domains),list(tuple(r) for r in rows)
        width=2*len(ds)
        if any(len(d)!=2 or any(type(v) is not int or not 0<=v<16 for v in d) for d in ds):
            return False
        if any(len(r)!=2 or type(r[0]) is not int or not 0<=r[0]<(1<<width)
               or type(r[1]) is not int or r[1] not in (0,1) for r in rows):
            return False
        if not isinstance(cert,dict):
            return False
        rel=[_relation(d) for d in ds]
        kind=cert.get("kind")
        if kind=="empty":
            i=cert.get("index")
            return set(cert)=={"kind","index"} and type(i) is int and 0<=i<len(ds) and not rel[i]
        if any(not r for r in rel):
            return False
        if kind=="sat":
            return set(cert)=={"kind","witness"} and _witness_ok(ds,rows,cert["witness"])
        if kind!="unsat" or set(cert)!={"kind","tree"} or not isinstance(cert["tree"],list):
            return False
        fixed=rows+[row for i,r in enumerate(rel) if len(r)!=3 for row in local_rows(i,r,_rows)]
        pending=tuple(i for i,r in enumerate(rel) if len(r)==3)
        stack=[(fixed,pending)]
        pos=0
        while stack:
            if pos>=len(cert["tree"]):
                return False
            node=cert["tree"][pos]
            pos+=1
            current,remaining=stack.pop()
            remaining=list(remaining)
            if not isinstance(node,dict) or not isinstance(node.get("trace"),list):
                return False
            def live(i):
                return {v for v in rel[i] if _consistent(width,current+point_rows(i,v))}
            for i in node["trace"]:
                if type(i) is not int or i not in remaining or not _consistent(width,current):
                    return False
                r=live(i)
                if len(r) not in (1,2):
                    return False
                current=current+local_rows(i,r,_rows)
                remaining.remove(i)
            nk=node.get("kind")
            if nk=="dual":
                if set(node)!={"trace","kind","dual"} or not _dual_ok(current,node["dual"]):
                    return False
            elif nk=="empty_local":
                i=node.get("index")
                if set(node)!={"trace","kind","index"} or type(i) is not int or i not in remaining or live(i):
                    return False
            elif nk=="split":
                m=node.get("form")
                if set(node)!={"trace","kind","form"} or type(m) is not int or not any(
                        m in (1<<(2*i),2<<(2*i),3<<(2*i)) for i in remaining):
                    return False
                if not all(_consistent(width,current+[(m,b)]) for b in (0,1)):
                    return False
                for b in (1,0):
                    stack.append((current+[(m,b)],tuple(remaining)))
            else:
                return False
        return pos==len(cert["tree"])
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def chain_instance(k):
    """v_0=1, u_(k-1)=0, v_(i+1)=u_i; all blocks impose v implies u."""
    if type(k) is not int or k<2:
        raise ValueError("expected at least two components")
    return [(10,15)]*k,[(2,1),(1<<(2*(k-1)),0)]+[
        ((1<<(2*i))|(2<<(2*(i+1))),0) for i in range(k-1)]

def evidence(k=43):
    ds,rows=chain_instance(k)
    stats={}
    cert=solve_adaptive(ds,rows,stats=stats)
    assert cert["kind"]=="unsat" and check_adaptive(ds,rows,cert)
    static_d=(k-1)//2
    return {"scope":"structured UNSAT chain; no runtime or novelty claim",
            "components":k,"static_rank_analytic":static_d,
            "static_full_leaf_count_analytic":1<<static_d,
            "adaptive_nodes":stats["nodes"],"adaptive_splits":stats["splits"],
            "stats":stats,"certificate_bytes":len(json.dumps(cert,separators=(",",":")).encode()),
            "certificate":cert,"checker_accepted":True}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
