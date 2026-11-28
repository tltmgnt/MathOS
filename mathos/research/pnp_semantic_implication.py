"""Certified one-round semantic implication closure and template transfer.

Resolution-derived clauses are consequences of the original CNF. This
bounded inference layer is deliberately not a complete SAT solver.
"""
from .pnp_structural_kernel import normalize, Exhausted
from .pnp_unified_portfolio import fingerprint
from .pnp_analogy import query_strengthened, verify_query_strengthened
from .pnp_knowledge_library import budget
from .pnp_evidence_benchmark import digest

MAX_WIDTH=4
MAX_DERIVED=256
MAX_PAIRS=20_000


def _options(width,derived,pairs):
    for x,lo,hi in ((width,1,MAX_WIDTH),(derived,1,MAX_DERIVED),(pairs,1,MAX_PAIRS)):
        if type(x) is not int or not lo<=x<=hi:
            raise ValueError("invalid implication limit")


def _base(n,clauses):
    _,f,m=normalize(n,clauses)
    return tuple(tuple(sorted(m[abs(x)-1] if x>0 else -m[-x-1] for x in c)) for c in f)


def closure(n,clauses,b,*,width=MAX_WIDTH,derived=MAX_DERIVED,pairs=MAX_PAIRS):
    """One wave of resolution on ORIGINAL axioms only, in fixed order.

    The record cap is an accepted-clause limit; the pair cap counts all
    examined unordered pairs, including those without complementary literals.
    Width/size skips are not mathematical impossibility claims.
    """
    _options(width,derived,pairs)
    base=_base(n,clauses)
    known=set(base)
    sets=[set(c) for c in base]
    steps=[]
    tried=0
    status="complete_wave"
    occurrences=sum(map(len,base))
    if () in known:
        status="empty_clause"
    else:
        try:
            for i,a in enumerate(sets):
                if status!="complete_wave":
                    break
                for j in range(i+1,len(sets)):
                    if tried>=pairs:
                        status="pair_limit"
                        break
                    c=sets[j]
                    b.tick(1+len(a)+len(c))
                    tried+=1
                    pivots=sorted(x for x in a if -x in c)
                    # Two or more complementary pairs always give tautologies.
                    if len(pivots)!=1:
                        continue
                    x=pivots[0]
                    d=tuple(sorted((a-{x})|(c-{-x})))
                    if len(d)>width or d in known:
                        continue
                    if len(base)+len(steps)>=20_000 or occurrences+len(d)>100_000:
                        status="dimension_limit"
                        break
                    b.cells(occurrences+len(d))
                    steps.append({"positive":i if x>0 else j,
                                  "negative":j if x>0 else i,
                                  "pivot":abs(x),"clause":d})
                    known.add(d)
                    occurrences+=len(d)
                    if not d:
                        status="empty_clause"
                        break
                    if len(steps)>=derived:
                        status="derived_limit"
                        break
        except Exhausted:
            status="resource_exhausted"
    return {"schema":"mathos-pnp-implication-wave/1","input_sha256":fingerprint(n,clauses),
            "width":width,"derived_limit":derived,"pair_limit":pairs,
            "steps":steps,"pairs_examined":tried,"status":status,"work_steps":b.steps}


def replay_closure(n,clauses,r,b):
    """Check every credited inference independently, not completeness of search."""
    _options(r["width"],r["derived_limit"],r["pair_limit"])
    if (r["schema"]!="mathos-pnp-implication-wave/1" or
            r["input_sha256"]!=fingerprint(n,clauses) or
            len(r["steps"])>r["derived_limit"] or
            r["status"] not in ("complete_wave","empty_clause","pair_limit","derived_limit",
                                "dimension_limit","resource_exhausted") or
            type(r["pairs_examined"]) is not int or not 0<=r["pairs_examined"]<=r["pair_limit"] or
            type(r["work_steps"]) is not int or r["work_steps"]<0):
        raise ValueError("invalid closure metadata")
    base=_base(n,clauses)
    known=set(base)
    result=list(base)
    for s in r["steps"]:
        p,q,v=s["positive"],s["negative"],s["pivot"]
        if (any(type(x) is not int for x in (p,q,v)) or not 0<=p<len(base) or
                not 0<=q<len(base) or p==q or not 1<=v<=n):
            raise ValueError("invalid original parent or pivot")
        a,c=base[p],base[q]
        b.tick(1+len(a)+len(c))
        if v not in a or -v not in c:
            raise ValueError("incorrect premise polarity")
        d=tuple(sorted({x for x in a if x!=v}|{x for x in c if x!=-v}))
        actual=tuple(s["clause"])
        if (any(type(x) is not int for x in actual) or actual!=d or len(d)>r["width"] or
                any(-x in d for x in d) or d in known):
            raise ValueError("invalid or repeated derived clause")
        known.add(d)
        result.append(d)
    if len(result)>20_000 or sum(map(len,result))>100_000:
        raise ValueError("augmented formula exceeds dimensions")
    if (r["status"]=="empty_clause")!=(() in known):
        raise ValueError("contradiction status mismatch")
    return tuple(result)


def transfer(n,clauses,lib,*,width=MAX_WIDTH,derived=MAX_DERIVED,pairs=MAX_PAIRS):
    c=closure(n,clauses,budget(),width=width,derived=derived,pairs=pairs)
    augmented=replay_closure(n,clauses,c,budget())
    result=None
    if () in augmented:
        decision,reason="unsat","direct_empty_clause"
    else:
        result=query_strengthened(n,augmented,lib)
        decision=result["decision"]
        reason="template_transfer" if decision=="unsat" else "unknown"
    r={"schema":"mathos-pnp-semantic-transfer/1","closure":c,"query":result,
       "decision":decision,"reason":reason}
    verify_transfer(n,clauses,lib,r)
    return r


def verify_transfer(n,clauses,lib,r):
    if r["schema"]!="mathos-pnp-semantic-transfer/1":
        raise ValueError("invalid transfer schema")
    augmented=replay_closure(n,clauses,r["closure"],budget())
    if () in augmented:
        if r["query"] is not None:
            raise ValueError("unexpected query after direct refutation")
        decision,reason="unsat","direct_empty_clause"
    else:
        if r["query"] is None:
            raise ValueError("missing transfer query")
        verify_query_strengthened(n,augmented,lib,r["query"])
        decision=r["query"]["decision"]
        reason="template_transfer" if decision=="unsat" else "unknown"
    if r["decision"]!=decision or r["reason"]!=reason:
        raise ValueError("invalid transfer verdict")
    return True
