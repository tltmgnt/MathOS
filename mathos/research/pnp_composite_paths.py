"""Compose certified unit consequences, clause reduction, and implication paths."""
from collections import defaultdict, deque

from .pnp_structural_kernel import validate, Exhausted
from .pnp_proof_library import verify_certificate
from .pnp_implication_paths import propose as paths, verify_paths


def original(n,formula,budget):
    out=[]
    for raw in validate(n,formula):
        budget.tick(1+len(raw))
        s=set(raw)
        out.append(None if any(-x in s for x in s) else tuple(sorted(s)))
    return out


def prefix(n,formula,budget):
    """Event-driven unit propagation; record original clause indices."""
    cs=original(n,formula,budget)
    watch=defaultdict(list)
    remaining={}
    ready=deque()
    for i,c in enumerate(cs):
        if c is None:
            continue
        remaining[i]=set(c)
        for x in c:
            watch[x].append(i)
        if len(c)<=1:
            ready.append(i)
    known=set()
    trace=[]
    while ready:
        i=ready.popleft()
        budget.tick()
        c=remaining[i]
        if any(x in known for x in c):
            continue
        if not c:
            return trace+[i],known,True
        if len(c)!=1:
            continue
        x=next(iter(c))
        if x in known:
            continue
        # Opposing assignments would have reduced this clause to empty.
        if -x in known:
            raise AssertionError("stale propagation state")
        known.add(x)
        trace.append(i)
        for j in watch[-x]:
            budget.tick()
            r=remaining[j]
            r.discard(-x)
            if len(r)<=1:
                ready.append(j)
    return trace,known,False


def verify_prefix(n,formula,trace,budget):
    """Replay unit or conflict steps from the named original clause only."""
    cs=original(n,formula,budget)
    if not isinstance(trace,(tuple,list)) or len(trace)>n+1:
        raise ValueError("bad unit trace")
    known=set()
    proof=[]
    for j,i in enumerate(trace):
        if type(i) is not int or not 0<=i<len(cs) or cs[i] is None:
            raise ValueError("bad unit premise")
        c=cs[i]
        budget.tick(1+len(c))
        if any(x in known for x in c):
            raise ValueError("already satisfied premise")
        residual=tuple(x for x in c if -x not in known)
        if len(residual)>1:
            raise ValueError("premise not unit")
        if not residual and j!=len(trace)-1:
            raise ValueError("trailing conflict records")
        proof.append(residual)
        if residual:
            known.add(residual[0])
    return proof,known


def reductions(n,formula,known,budget):
    """All novel binary residuals; each is justified by known unit facts."""
    cs=original(n,formula,budget)
    present={c for c in cs if c is not None}
    out=[]
    for i,c in enumerate(cs):
        if c is None:
            continue
        budget.tick(1+len(c))
        if any(x in known for x in c):
            continue
        r=tuple(x for x in c if -x not in known)
        if len(r)==2 and r not in present:
            present.add(r)
            out.append((i,r))
    return out


def verify_recipe(n,formula,recipe,budget):
    if recipe.get("schema")!="mathos-pnp-composite-units-paths/1":
        raise ValueError("wrong recipe schema")
    units,known=verify_prefix(n,formula,recipe["units"],budget)
    kind=recipe["kind"]
    records=recipe["reductions"]
    if not isinstance(records,(list,tuple)) or len(records)>len(formula):
        raise ValueError("bad reduction count")
    if kind=="unit":
        if not units or units[-1]!=() or records or recipe["paths"] is not None:
            raise ValueError("invalid unit-only proof")
        proof=units
    elif kind=="paths":
        if () in units:
            raise ValueError("prefix already refutes")
        cs=original(n,formula,budget)
        binary=[]
        for record in records:
            if not isinstance(record,(list,tuple)) or len(record)!=2:
                raise ValueError("bad reduction record")
            i,r=record
            if type(i) is not int or not 0<=i<len(cs) or cs[i] is None:
                raise ValueError("bad reduction premise")
            c=cs[i]
            budget.tick(1+len(c))
            if (not isinstance(r,(list,tuple)) or len(r)!=2 or
                    any(type(x) is not int or not 0<abs(x)<=n for x in r) or
                    any(x in known for x in c) or
                    tuple(r)!=tuple(x for x in c if -x not in known)):
                raise ValueError("invalid residual binary clause")
            binary.append(tuple(r))
        # The augmented formula is only original premises plus verified consequences.
        tail=verify_paths(n,list(formula)+units+binary,recipe["paths"],budget)
        proof=units+binary+tail
    else:
        raise ValueError("unknown proof kind")
    verify_certificate(n,formula,proof,budget)
    return proof


def propose(n,formula,budget,*,compose=True):
    try:
        trace,known,conflict=prefix(n,formula,budget)
        if conflict:
            recipe={"schema":"mathos-pnp-composite-units-paths/1","kind":"unit",
                    "units":trace,"reductions":[],"paths":None}
        elif compose:
            units=[(x,) for x in sorted(known)]
            red=reductions(n,formula,known,budget)
            r=paths(n,list(formula)+units+[c for _,c in red],budget)
            if r["status"]!="verified":
                return {"status":r["status"]}
            recipe={"schema":"mathos-pnp-composite-units-paths/1","kind":"paths",
                    "units":trace,"reductions":red,"paths":r["certificate"]}
        else:
            return {"status":"not_found"}
        proof=verify_recipe(n,formula,recipe,budget)
        return {"status":"verified","recipe":recipe,"proof":proof}
    except Exhausted:
        return {"status":"resource_exhausted"}
