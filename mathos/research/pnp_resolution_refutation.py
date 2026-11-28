"""Bounded proof-producing Davis-Putnam refutation with independent replay.

Unlike v4, permits controlled clause growth. A missed refutation, SAT
residual, or resource limit yields unknown, not a SAT decision.
"""
from .pnp_structural_kernel import normalize, Exhausted

STRATEGIES=("min_product","min_degree","ascending")
MAX_WIDTH=12
MAX_RECORDS=50_000


def _options(width,records,strategy):
    if (type(width) is not int or not 1<=width<=MAX_WIDTH or
            type(records) is not int or not 1<=records<=MAX_RECORDS or
            strategy not in STRATEGIES):
        raise ValueError("invalid refutation options")


def propose(n,clauses,budget,*,width=6,records=4096,strategy="min_product"):
    """Generate a trimmed resolution DAG; only the empty clause is credited.

    Width and record limits apply to derived clauses (input axioms may be
    wider). Any oversize non-tautological resolvent stops this attempt.
    """
    _options(width,records,strategy)
    nn,f,mapping=normalize(n,clauses)
    live={frozenset(c):i for i,c in enumerate(f)}
    derived=[]
    if len(live)>records:
        raise Exhausted("initial clause count exceeds record cap")

    def finish(root):
        needed=set()
        todo=[root]
        while todo:
            i=todo.pop()
            budget.tick()
            if i<len(f) or i in needed:
                continue
            needed.add(i)
            item=derived[i-len(f)]
            todo.extend((item["positive"],item["negative"]))
        remap={old:len(f)+j for j,old in enumerate(sorted(needed))}
        def ref(i):
            return i if i<len(f) else remap[i]
        steps=[]
        for i in sorted(needed):
            t=derived[i-len(f)]
            steps.append({**t,"positive":ref(t["positive"]),"negative":ref(t["negative"])})
        return {"schema":"mathos-pnp-resolution-dag/1","normalized_n":nn,
                "new_to_old":mapping,"width_cap":width,"record_cap":records,
                "strategy":strategy,"steps":steps,"root":ref(root)}

    while live:
        budget.cells(len(f)+len(derived))
        if frozenset() in live:
            return finish(live[frozenset()])
        occ={}
        for c in live:
            budget.tick(1+len(c))
            for x in c:
                v=abs(x)
                if v not in occ:
                    occ[v]=[[],[]]
                occ[v][int(x<0)].append(c)
        if not occ:
            break
        def score(v):
            p,q=occ[v]
            if strategy=="ascending":
                return (v,)
            if strategy=="min_degree":
                return (len({abs(x) for c in p+q for x in c}-{v}),len(p)*len(q),v)
            return (len(p)*len(q),len(p)+len(q),v)
        v=min(occ,key=score)
        pos,neg=occ[v]
        kept={c:i for c,i in live.items() if v not in c and -v not in c}
        for a in sorted(pos,key=lambda c:tuple(sorted(c))):
            for b in sorted(neg,key=lambda c:tuple(sorted(c))):
                budget.tick(1+len(a)+len(b))
                resolvent=(a-{v})|(b-{-v})
                if any(-x in resolvent for x in resolvent) or resolvent in kept:
                    continue
                if len(resolvent)>width:
                    raise Exhausted("derived width cap")
                if len(f)+len(derived)>=records:
                    raise Exhausted("resolution record cap")
                i=len(f)+len(derived)
                derived.append({"positive":live[a],"negative":live[b],"pivot":v,
                                "clause":tuple(sorted(resolvent))})
                kept[resolvent]=i
                budget.cells(len(f)+len(derived))
                if not resolvent:
                    return finish(i)
        live=kept
    return None


def verify(n,clauses,proof,budget):
    """Check each resolution inference, backward references and empty root.

    Neither elimination order nor search completeness is trusted.
    """
    nn,f,mapping=normalize(n,clauses)
    width,records,strategy=(proof[k] for k in ("width_cap","record_cap","strategy"))
    _options(width,records,strategy)
    if (proof["schema"]!="mathos-pnp-resolution-dag/1" or
            type(proof["normalized_n"]) is not int or proof["normalized_n"]!=nn or
            tuple(proof["new_to_old"])!=mapping or len(f)+len(proof["steps"])>records):
        raise ValueError("invalid resolution metadata")
    known=list(f)
    for step in proof["steps"]:
        p,q,v=step["positive"],step["negative"],step["pivot"]
        if (any(type(x) is not int for x in (p,q,v)) or
                not 0<=p<len(known) or not 0<=q<len(known) or not 1<=v<=nn):
            raise ValueError("invalid parent reference or pivot")
        a,b=known[p],known[q]
        budget.tick(1+len(a)+len(b))
        if v not in a or -v not in b:
            raise ValueError("missing complementary pivot")
        expected=tuple(sorted({x for x in a if x!=v}|{x for x in b if x!=-v}))
        actual=tuple(step["clause"])
        if (any(type(x) is not int for x in actual) or actual!=expected or
                len(actual)>width or any(-x in actual for x in actual)):
            raise ValueError("incorrect resolvent")
        known.append(actual)
        budget.cells(len(known))
    root=proof["root"]
    if type(root) is not int or not 0<=root<len(known) or known[root]!=():
        raise ValueError("root is not an empty clause")
    return True
