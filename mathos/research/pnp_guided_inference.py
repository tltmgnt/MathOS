"""Multi-wave resolution with proof-depth bounds and certified retrieval views.

Short-first parent scheduling is a heuristic for exposing low-width
premises. Subsumption removes redundant clauses from the retrieval view,
not from the original proof provenance. No completeness claim is made.
"""
from collections import defaultdict
from .pnp_semantic_implication import _base
from .pnp_structural_kernel import Exhausted
from .pnp_unified_portfolio import fingerprint
from .pnp_knowledge_library import budget
from .pnp_analogy import query_strengthened, verify_query_strengthened

MAX_ROUNDS=4
MAX_WIDTH=4
MAX_DERIVED=256
MAX_PAIRS=20_000
ORDERS=("fifo","short_first")


def _options(rounds,width,derived,pairs,order):
    for x,lo,hi in ((rounds,1,MAX_ROUNDS),(width,1,MAX_WIDTH),
                    (derived,1,MAX_DERIVED),(pairs,1,MAX_PAIRS)):
        if type(x) is not int or not lo<=x<=hi:
            raise ValueError("invalid inference limits")
    if order not in ORDERS:
        raise ValueError("invalid parent order")


def derive(n,clauses,b,*,rounds=3,width=MAX_WIDTH,derived=MAX_DERIVED,
           pairs=MAX_PAIRS,order="short_first"):
    """Only complementary pairs from prior waves are considered.

    Wave d considers pairs whose maximum parent depth is d-1. A pair
    is considered at most once; accepted clauses have their first
    discovered proof depth. The caps are shared across all waves.
    """
    _options(rounds,width,derived,pairs,order)
    base=_base(n,clauses)
    known=list(base)
    unique=set(base)
    depths=[0]*len(base)
    steps=[]
    examined=0
    literals=sum(map(len,base))
    status="round_limit"
    try:
        if () in unique:
            status="empty_clause"
        else:
            for wave in range(1,rounds+1):
                size=len(known)
                if not any(d==wave-1 for d in depths):
                    status="no_new_wave"
                    break
                index=defaultdict(list)
                for i,c in enumerate(known):
                    b.tick(1+len(c))
                    for x in c:
                        index[x].append(i)
                key=lambda i:(len(known[i]),i) if order=="short_first" else (i,)
                parent_order=sorted(range(size),key=key)
                for i in parent_order:
                    a=known[i]
                    neighbors=set()
                    for x in a:
                        for j in index.get(-x,()):
                            b.tick()
                            if key(i)<key(j) and max(depths[i],depths[j])==wave-1:
                                neighbors.add(j)
                    b.cells(len(neighbors)+literals+len(known))
                    for j in sorted(neighbors,key=key):
                        if examined>=pairs:
                            status="pair_limit"
                            break
                        c=known[j]
                        b.tick(1+len(a)+len(c))
                        examined+=1
                        pivots=[x for x in a if -x in c]
                        if len(pivots)!=1:
                            continue
                        x=pivots[0]
                        d=tuple(sorted((set(a)-{x})|(set(c)-{-x})))
                        if len(d)>width or d in unique:
                            continue
                        if len(known)>=20_000 or literals+len(d)>100_000:
                            status="dimension_limit"
                            break
                        b.cells(literals+len(d)+len(known)+1)
                        steps.append({"positive":i if x>0 else j,"negative":j if x>0 else i,
                                      "pivot":abs(x),"clause":d,"depth":wave})
                        known.append(d)
                        depths.append(wave)
                        unique.add(d)
                        literals+=len(d)
                        if not d:
                            status="empty_clause"
                            break
                        if len(steps)>=derived:
                            status="derived_limit"
                            break
                    if status!="round_limit":
                        break
                if status!="round_limit":
                    break
                if len(known)==size:
                    status="no_new_wave"
                    break
    except Exhausted:
        status="resource_exhausted"
    return {"schema":"mathos-pnp-multi-wave/1","input_sha256":fingerprint(n,clauses),
            "rounds":rounds,"width":width,"derived_limit":derived,"pair_limit":pairs,
            "order":order,"steps":steps,"pairs_examined":examined,"status":status,
            "work_steps":b.steps}


def replay(n,clauses,r,b):
    """Reconstruct each consequent from strictly earlier proof records."""
    _options(r["rounds"],r["width"],r["derived_limit"],r["pair_limit"],r["order"])
    if (r["schema"]!="mathos-pnp-multi-wave/1" or r["input_sha256"]!=fingerprint(n,clauses)
            or len(r["steps"])>r["derived_limit"] or r["status"] not in
            ("round_limit","no_new_wave","empty_clause","pair_limit","derived_limit","dimension_limit","resource_exhausted")
            or type(r["pairs_examined"]) is not int or not len(r["steps"])<=r["pairs_examined"]<=r["pair_limit"]
            or type(r["work_steps"]) is not int or r["work_steps"]<0):
        raise ValueError("invalid multi-wave metadata")
    known=list(_base(n,clauses))
    unique=set(known)
    depths=[0]*len(known)
    last=0
    for s in r["steps"]:
        p,q,v,d=s["positive"],s["negative"],s["pivot"],s["depth"]
        if (any(type(x) is not int for x in (p,q,v,d)) or not 0<=p<len(known) or
                not 0<=q<len(known) or p==q or not 1<=v<=n or
                d!=max(depths[p],depths[q])+1 or not max(1,last)<=d<=r["rounds"]):
            raise ValueError("invalid parent reference or proof depth")
        a,c=known[p],known[q]
        b.tick(1+len(a)+len(c))
        if v not in a or -v not in c:
            raise ValueError("invalid pivot polarity")
        expected=tuple(sorted({x for x in a if x!=v}|{x for x in c if x!=-v}))
        actual=tuple(s["clause"])
        if (any(type(x) is not int for x in actual) or actual!=expected or
                len(actual)>r["width"] or any(-x in actual for x in actual) or actual in unique):
            raise ValueError("incorrect resolvent")
        known.append(actual)
        unique.add(actual)
        depths.append(d)
        last=d
        b.cells(len(known))
    if len(known)>20_000 or sum(map(len,known))>100_000:
        raise ValueError("augmented input too large")
    if (r["status"]=="empty_clause")!=(() in unique):
        raise ValueError("empty-clause status mismatch")
    return tuple(known)


def compact_view(formula,b):
    """Select an equivalent subformula by explicit subsumption witnesses.

    A smaller retained clause implies each dropped clause. If the view
    budget expires, return the identity view instead of partial evidence.
    """
    kept=[]
    dropped=[]
    sets=[set(c) for c in formula]
    try:
        for i in sorted(range(len(formula)),key=lambda i:(len(formula[i]),i)):
            witness=None
            for j in kept:
                b.tick(1+len(formula[j]))
                if sets[j]<=sets[i]:
                    witness=j
                    break
            if witness is None:
                kept.append(i)
            else:
                dropped.append((i,witness))
        status="compacted"
    except Exhausted:
        kept=list(range(len(formula)))
        dropped=[]
        status="identity_fallback"
    return {"kept":sorted(kept),"dropped":sorted(dropped),"status":status,"work_steps":b.steps}


def verify_view(formula,r,b):
    kept=r["kept"]
    if (r["status"] not in ("compacted","identity_fallback") or
            type(r["work_steps"]) is not int or r["work_steps"]<0 or
            any(type(i) is not int or not 0<=i<len(formula) for i in kept) or
            list(kept)!=sorted(set(kept))):
        raise ValueError("invalid retained index set")
    retained=set(kept)
    seen=set(retained)
    for pair in r["dropped"]:
        if len(pair)!=2:
            raise ValueError("invalid subsumption record")
        i,j=pair
        if (any(type(x) is not int for x in pair) or not 0<=i<len(formula) or
                i in seen or j not in retained):
            raise ValueError("invalid dropped clause or witness")
        b.tick(1+len(formula[i])+len(formula[j]))
        if not set(formula[j])<=set(formula[i]):
            raise ValueError("subsumption witness does not imply dropped clause")
        seen.add(i)
    if len(seen)!=len(formula) or (r["status"]=="identity_fallback" and r["dropped"]):
        raise ValueError("incomplete equivalent view")
    return tuple(formula[i] for i in kept)


def investigate(n,clauses,lib,*,rounds=3,width=MAX_WIDTH,derived=MAX_DERIVED,
                pairs=MAX_PAIRS,order="short_first"):
    """Compare full versus compact retrieval on exactly the same proof DAG."""
    c=derive(n,clauses,budget(),rounds=rounds,width=width,derived=derived,pairs=pairs,order=order)
    f=replay(n,clauses,c,budget())
    view=compact_view(f,budget())
    g=verify_view(f,view,budget())
    direct=() in f
    full=None if direct else query_strengthened(n,f,lib)
    compact=None if direct else query_strengthened(n,g,lib)
    result={"schema":"mathos-pnp-guided-transfer/1","inference":c,"view":view,
            "full_query":full,"compact_query":compact,"full_size":len(f),"compact_size":len(g),
            "full_decision":"unsat" if direct else full["decision"],
            "compact_decision":"unsat" if direct else compact["decision"],
            "direct_refutation":direct}
    verify_investigation(n,clauses,lib,result)
    return result


def verify_investigation(n,clauses,lib,r):
    if r["schema"]!="mathos-pnp-guided-transfer/1":
        raise ValueError("invalid investigation schema")
    f=replay(n,clauses,r["inference"],budget())
    g=verify_view(f,r["view"],budget())
    direct=() in f
    if (r["direct_refutation"] is not direct or r["full_size"]!=len(f) or r["compact_size"]!=len(g)):
        raise ValueError("investigation size or status mismatch")
    for label,formula in (("full",f),("compact",g)):
        q=r[label+"_query"]
        if direct:
            if q is not None:
                raise ValueError("unexpected query after direct refutation")
            d="unsat"
        else:
            if q is None or q["limit"]!=4096:
                raise ValueError("missing or misconfigured query")
            verify_query_strengthened(n,formula,lib,q)
            d=q["decision"]
        if r[label+"_decision"]!=d:
            raise ValueError("investigation conclusion mismatch")
    return True
