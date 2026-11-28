"""Unified UNSAT portfolio with a shared cooperative budget and checked handoff."""
import time
from .pnp_structural_kernel import Budget, Exhausted, validate
from .pnp_proof_abstraction import _original_clauses
from .pnp_proof_library import find, mapped, verify_certificate, reuse, reconstruct
from .pnp_composite_paths import propose as composite, verify_recipe


def checked_prefix(n,formula,index,transfers,budget):
    """Check partial template transfers, without requiring an empty conclusion."""
    if not isinstance(transfers,(tuple,list)) or len(transfers)>32:
        raise ValueError("invalid transfer count")
    known=set(_original_clauses(n,formula))
    proof=[]
    for i,e in transfers:
        budget.tick()
        if type(i) is not int or not 0<=i<len(index.templates):
            raise ValueError("invalid template")
        f=index.templates[i]
        if (len(e)!=f["n"] or any(type(x) is not int or not 0<abs(x)<=n for x in e)
                or len({abs(x) for x in e})!=len(e)):
            raise ValueError("invalid embedding")
        for a in f["axioms"]:
            target=set(mapped(a,e))
            found=False
            for c in sorted(known):
                budget.tick(1+len(c))
                if set(c)<=target:
                    found=True
                    break
            if not found:
                raise ValueError("missing guard")
        part=[mapped(c,e) for c in f["steps"]]
        verify_certificate(n,sorted(known),part,budget,contradiction=False)
        if not set(part)-known:
            raise ValueError("nonproductive transfer")
        proof.extend(part)
        known.update(part)
    return proof


def verify(n,formula,index,recipe,budget):
    if recipe.get("schema")!="mathos-pnp-schema-portfolio/1":
        raise ValueError("invalid schema")
    kind=recipe["kind"]
    if kind=="composite":
        if recipe["transfers"]:
            raise ValueError("unexpected prefix")
        proof=verify_recipe(n,formula,recipe["tail"],budget)
    elif kind=="library":
        if recipe["tail"] is not None:
            raise ValueError("unexpected tail")
        proof=reconstruct(n,formula,index,recipe["transfers"],budget)
    elif kind=="handoff":
        if not recipe["transfers"] or recipe["tail"] is None:
            raise ValueError("missing handoff")
        prefix=checked_prefix(n,formula,index,recipe["transfers"],budget)
        if () in prefix:
            raise ValueError("prefix already refutes")
        proof=prefix+verify_recipe(n,list(formula)+prefix,recipe["tail"],budget)
    else:
        raise ValueError("unknown proof route")
    verify_certificate(n,formula,proof,budget)
    return proof


def handoff(n,formula,index,budget,*,max_transfers=12):
    """Transfer short consequences, then try the parameterized route.

    No target SAT solver, no library mutation, and no credit for a partial proof.
    """
    known=set(_original_clauses(n,formula))
    transfers=[]
    prefix=[]
    try:
        for _ in range(2):
            changed=False
            ids=index.retrieve(known)
            ids.sort(key=lambda i:(len(index.templates[i]["steps"][-1]),
                                  len(index.templates[i]["steps"]),i))
            for i in ids:
                budget.tick()
                f=index.templates[i]
                if len(f["steps"][-1])>2:
                    continue
                e=find(f,n,known,budget,subsumption=True,limit=1024)
                if e is None:
                    continue
                part=[mapped(c,e) for c in f["steps"]]
                verify_certificate(n,sorted(known),part,budget,contradiction=False)
                known.update(part)
                transfers.append((i,e))
                prefix.extend(part)
                changed=True
                if () in known:
                    return {"status":"verified","recipe":{"schema":"mathos-pnp-schema-portfolio/1",
                            "kind":"library","transfers":transfers,"tail":None}}
                tail=composite(n,list(formula)+prefix,budget)
                if tail["status"]=="verified":
                    return {"status":"verified","recipe":{"schema":"mathos-pnp-schema-portfolio/1",
                            "kind":"handoff","transfers":transfers,"tail":tail["recipe"]}}
                if tail["status"]=="resource_exhausted":
                    return {"status":"resource_exhausted"}
                if len(transfers)>=max_transfers:
                    return {"status":"transfer_limit"}
            if not changed:
                break
    except Exhausted:
        return {"status":"resource_exhausted"}
    return {"status":"not_found"}


def solve(n,formula,index,budget,*,cooperate=True):
    """Cheap schema first; optionally hand off fragments; fall back to retrieval.

    All routes share a deadline and cooperative quota, including final replay.
    Reserve half of remaining ticks for final replay on candidate success.
    """
    validate(n,formula)
    attempts=[]
    order=("composite","handoff","library") if cooperate else ("composite","library")
    for i,route in enumerate(order):
        left=budget.max_steps-budget.steps
        seconds=budget.deadline-time.monotonic()
        if left<2 or seconds<=0:
            break
        # Fixed fractions of remaining quota, not a learned policy.
        divisor=8 if route=="composite" else 3 if route=="handoff" else 2
        quota=max(1,left//divisor)
        child=Budget(seconds=max(0.000001,seconds/divisor),max_steps=quota,
                     max_cells=budget.max_cells)
        try:
            if route=="composite":
                r=composite(n,formula,child)
                if r["status"]=="verified":
                    r={"status":"verified","recipe":{"schema":"mathos-pnp-schema-portfolio/1",
                       "kind":"composite","transfers":[],"tail":r["recipe"]}}
            elif route=="handoff":
                r=handoff(n,formula,index,child)
            else:
                r=reuse(n,formula,index,child,shared_replay=True)
                if r["status"]=="verified":
                    r={"status":"verified","recipe":{"schema":"mathos-pnp-schema-portfolio/1",
                       "kind":"library","transfers":r["transfers"],"tail":None}}
            budget.tick(child.steps)
        except Exhausted:
            return {"status":"resource_exhausted","attempts":attempts}
        attempts.append({"route":route,"status":r["status"],"quota":quota,"work":child.steps})
        if r["status"]=="verified":
            try:
                proof=verify(n,formula,index,r["recipe"],budget)
            except Exhausted:
                return {"status":"resource_exhausted","attempts":attempts}
            return {"status":"verified","attempts":attempts,"recipe":r["recipe"],"proof":proof}
    return {"status":"not_found","attempts":attempts}
