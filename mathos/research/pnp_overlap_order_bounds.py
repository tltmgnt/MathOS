"""Theorem M: polynomial recovery-order bounds for signed implication networks.

Inputs are explicit signed-literal implications, without self-variable edges.
No claim to extract such a representation from arbitrary overlap instances.
"""
from collections import deque
import json

def validated(edges):
    es=tuple(tuple(e) for e in edges)
    if any(len(e)!=2 or any(type(x) is not int or x==0 for x in e)
           or abs(e[0])==abs(e[1]) for e in es):
        raise ValueError("expected signed nonzero literals on distinct variables")
    return es

def encode(edges):
    """One implication block per edge; enforce signed occurrence consistency."""
    es=validated(edges)
    ds,rows,reps=[],[],{}
    for i,(a,b) in enumerate(es):
        ds.append((10,15))
        for pos,lit in enumerate((b,a)):
            coord=2*i+pos
            var,neg=abs(lit),int(lit<0)
            if var in reps:
                j,old=reps[var]
                rows.append(((1<<coord)|(1<<j),neg^old))
            else:
                reps[var]=(coord,neg)
    return ds,rows

def _graphs(es):
    und,directed={},{}
    for i,(a,b) in enumerate(es):
        u,v=abs(a),abs(b)
        und.setdefault(u,[]).append((v,i))
        und.setdefault(v,[]).append((u,i))
        for x in (a,-a,b,-b):
            directed.setdefault(x,[])
        directed[a].append((b,i))
        directed[-b].append((-a,i))
    return und,directed

def _path(graph,start,end,skip=None):
    pred={start:None}
    queue=deque([start])
    while queue:
        u=queue.popleft()
        if u==end:
            path=[]
            while pred[u] is not None:
                v,i=pred[u]
                path.append([v,u,i])
                u=v
            return list(reversed(path))
        for v,i in graph.get(u,()):
            if i!=skip and v not in pred:
                pred[v]=(u,i)
                queue.append(v)
    return None

def girth(edges):
    """Shortest cycle in undirected multigraph, counting parallel edges."""
    es=validated(edges)
    und,_=_graphs(es)
    best=None
    for i,(a,b) in enumerate(es):
        path=_path(und,abs(a),abs(b),skip=i)
        if path is not None:
            length=len(path)+1
            best=length if best is None else min(best,length)
    return best

def predict(edges):
    """Bounds on r*; None denotes satisfiable (infinite threshold)."""
    es=validated(edges)
    _,graph=_graphs(es)
    best=None
    for x in sorted(v for v in graph if v>0):
        p,q=_path(graph,x,-x),_path(graph,-x,x)
        if p is None or q is None:
            continue
        bound=max(len({e[2] for e in p}),len({e[2] for e in q}))
        if best is None or bound<best[0]:
            best=(bound,x,p,q)
    if best is None:
        return {"kind":"sat","lower":None,"upper":None}
    upper,x,p,q=best
    lower=girth(es)
    if lower is None or lower>upper:
        raise AssertionError("graph-bound invariant")
    return {"kind":"unsat","lower":lower,"upper":upper,"variable":x,"paths":[p,q]}

def check_prediction(edges,cert):
    """Check claimed bounds without invoking recovery or SAT search.

    Recompute the lower graph bound; verify signed path edges directly.
    For SAT use the standard no-mutually-reachable-complements criterion.
    The checker does not certify that a noncoincident interval is exact.
    """
    try:
        es=validated(edges)
        if not isinstance(cert,dict):
            return False
        if cert.get("kind")=="sat":
            if set(cert)!={"kind","lower","upper"} or cert["lower"] is not None or cert["upper"] is not None:
                return False
            _,graph=_graphs(es)
            def reachable(x):
                seen={x}
                todo=[x]
                while todo:
                    for y,_ in graph[todo.pop()]:
                        if y not in seen:
                            seen.add(y)
                            todo.append(y)
                return seen
            return not any(-x in reachable(x) and x in reachable(-x) for x in graph if x>0)
        if cert.get("kind")!="unsat" or set(cert)!={"kind","lower","upper","variable","paths"}:
            return False
        lo,hi,x=cert["lower"],cert["upper"],cert["variable"]
        if any(type(v) is not int for v in (lo,hi,x)) or not 1<=lo<=hi<=len(es) or x<=0:
            return False
        if girth(es)!=lo:
            return False
        paths=cert["paths"]
        if not isinstance(paths,list) or len(paths)!=2:
            return False
        for path,start,end in zip(paths,(x,-x),(-x,x)):
            if not isinstance(path,list) or not path:
                return False
            at=start
            used=set()
            for step in path:
                if not isinstance(step,list) or len(step)!=3 or any(type(v) is not int for v in step):
                    return False
                a,b,i=step
                if a!=at or not 0<=i<len(es):
                    return False
                u,v=es[i]
                if (a,b) not in ((u,v),(-v,-u)):
                    return False
                at=b
                used.add(i)
            if at!=end or len(used)>hi:
                return False
        return True
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def two_cycles(p,q):
    """Two contradictory paths of lengths p,q (at least 2)."""
    if any(type(v) is not int or v<2 for v in (p,q)):
        raise ValueError("path lengths must be at least two")
    a=[1]+list(range(2,p+1))+[-1]
    b=[-1]+list(range(p+1,p+q))+[1]
    return list(zip(a,a[1:]))+list(zip(b,b[1:]))

def evidence():
    from mathos.research.pnp_overlap_order import minimum_order,check_minimum
    cases=[]
    for p,q in ((2,2),(2,3),(3,3),(4,4)):
        es=two_cycles(p,q)
        cert=predict(es)
        ds,rs=encode(es)
        actual=minimum_order(ds,rs)
        assert check_prediction(es,cert) and check_minimum(ds,rs,actual)
        assert cert["lower"]<=actual["minimum"]<=cert["upper"]
        cases.append({"paths":[p,q],"bounds":[cert["lower"],cert["upper"]],
                      "minimum":actual["minimum"],"checker_accepted":True})
    es=two_cycles(21,21)
    cert=predict(es)
    assert check_prediction(es,cert) and cert["lower"]==cert["upper"]==21
    return {"scope":"signed implication networks only; no SAT hardness or novelty claim",
            "small_exact_controls":cases,"large":{"blocks":len(es),"bounds":[21,21],
            "minimum_analytic":21,"hierarchy_run":False,"certificate":cert}}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
