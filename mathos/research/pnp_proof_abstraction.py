"""Compact resolution proofs and checked reuse under signed variable injection.

Templates are contradictions of a conjunction of explicit axioms, not
unconditional clauses or proof of a complexity lower bound.
"""
from .pnp_structural_kernel import normalize, validate, Exhausted
from .pnp_resolution_refutation import verify as verify_resolution

MAX_RECORDS=50_000
MAX_MATCH=4096


def _ancestors(steps,root,base,budget):
    seen=set()
    todo=[root]
    while todo:
        i=todo.pop()
        budget.tick()
        if i not in seen:
            seen.add(i)
            if i>=base:
                todo.extend(steps[i-base][:2])
    return seen


def compress(n,clauses,proof,budget):
    """Verify v13 proof, hash-cons equal clauses, prune, omit derived payloads."""
    verify_resolution(n,clauses,proof,budget)
    _,f,mapping=normalize(n,clauses)
    base=len(f)
    old_steps=[(s["positive"],s["negative"],s["pivot"]) for s in proof["steps"]]
    needed=_ancestors(old_steps,proof["root"],base,budget)
    # Only use input axioms already in the dependency cone.
    axioms=[f[i] for i in sorted(needed) if i<base]
    by_clause={c:i for i,c in enumerate(axioms)}
    remap={i:by_clause[f[i]] for i in needed if i<base}
    steps=[]
    for i,s in enumerate(proof["steps"],base):
        if i not in needed:
            continue
        budget.tick(1+len(s["clause"]))
        c=tuple(s["clause"])
        if c not in by_clause:
            by_clause[c]=len(axioms)+len(steps)
            steps.append((remap[s["positive"]],remap[s["negative"]],s["pivot"]))
        remap[i]=by_clause[c]
    root=remap[proof["root"]]
    used=_ancestors(steps,root,len(axioms),budget)
    ax=[c for i,c in enumerate(axioms) if i in used]
    ids={i:j for j,i in enumerate(sorted(used))}
    active=sorted({abs(x) for c in ax for x in c})
    labels={v:i+1 for i,v in enumerate(active)}
    def lit(x):
        return labels[abs(x)] if x>0 else -labels[abs(x)]
    template={"schema":"mathos-pnp-compact-resolution/1","n":len(active),
              "axioms":[tuple(sorted(lit(x) for x in c)) for c in ax],
              "steps":[(ids[p],ids[q],labels[v]) for i,(p,q,v) in enumerate(steps,len(axioms)) if i in used],
              "root":ids[root]}
    embedding=tuple(mapping[v-1] for v in active)
    verify_embedding(n,clauses,template,embedding,budget)
    return {"template":template,"source_embedding":embedding}


def verify_template(t,budget):
    """Reconstruct derived clauses from parent references and pivots."""
    n=t["n"]
    if t["schema"]!="mathos-pnp-compact-resolution/1":
        raise ValueError("invalid template schema")
    ax=validate(n,t["axioms"])
    if (len(ax)+len(t["steps"])>MAX_RECORDS or
            any(tuple(sorted(set(c)))!=c or any(-x in c for x in c) for c in ax) or
            len(set(ax))!=len(ax) or {abs(x) for c in ax for x in c}!=set(range(1,n+1))):
        raise ValueError("invalid template axioms")
    known=list(ax)
    unique=set(ax)
    steps=[]
    for raw in t["steps"]:
        if len(raw)!=3:
            raise ValueError("invalid compact inference")
        p,q,v=raw
        if (any(type(x) is not int for x in raw) or not 0<=p<len(known) or
                not 0<=q<len(known) or not 1<=v<=n):
            raise ValueError("invalid compact parent or pivot")
        a,b=known[p],known[q]
        budget.tick(1+len(a)+len(b))
        if v not in a or -v not in b:
            raise ValueError("invalid resolution polarity")
        c=tuple(sorted((set(a)-{v})|(set(b)-{-v})))
        if any(-x in c for x in c) or c in unique:
            raise ValueError("tautological or duplicate derived clause")
        unique.add(c)
        known.append(c)
        steps.append((p,q,v))
        budget.cells(len(known))
    root=t["root"]
    if type(root) is not int or not 0<=root<len(known) or known[root]!=():
        raise ValueError("template root is not empty")
    if _ancestors(steps,root,len(ax),budget)!=set(range(len(known))):
        raise ValueError("unused template records")
    return ax


def _original_clauses(n,f):
    _,nf,mapping=normalize(n,f)
    return {tuple(sorted(mapping[abs(x)-1] if x>0 else -mapping[abs(x)-1] for x in c)) for c in nf}


def _mapped(c,embedding):
    return tuple(sorted(embedding[x-1] if x>0 else -embedding[-x-1] for x in c))


def verify_embedding(n,clauses,t,embedding,budget):
    """Signed injective substitution + target axiom inclusion implies UNSAT."""
    ax=verify_template(t,budget)
    if (len(embedding)!=t["n"] or any(type(x) is not int or not 0<abs(x)<=n for x in embedding) or
            len({abs(x) for x in embedding})!=len(embedding)):
        raise ValueError("invalid signed injection")
    target=_original_clauses(n,clauses)
    for c in ax:
        budget.tick(1+len(c))
        if _mapped(c,embedding) not in target:
            raise ValueError("target missing embedded axiom")
    return True


def find_embedding(n,clauses,t,budget,*,limit=MAX_MATCH):
    """Bounded deterministic matching; absence of a match proves nothing.

    Match variables in decreasing template occurrence order, with partial
    clause support checks. No use of target reference decisions.
    """
    if type(limit) is not int or not 1<=limit<=MAX_MATCH:
        raise ValueError("invalid match limit")
    ax=verify_template(t,budget)
    target=_original_clauses(n,clauses)
    by_width={}
    for c in sorted(target):
        by_width.setdefault(len(c),[]).append(set(c))
    if any(len(c) not in by_width for c in ax):
        return {"status":"not_found","embedding":None,"candidates":0}
    variables=sorted({abs(x) for c in target for x in c})
    order=sorted(range(1,t["n"]+1),key=lambda v:(-sum(v in c or -v in c for c in ax),v))
    assigned={}
    used=set()
    attempts=0
    limited=False
    def possible():
        for c in ax:
            fixed={assigned[abs(x)] if x>0 else -assigned[abs(x)] for x in c if abs(x) in assigned}
            ok=False
            for other in by_width[len(c)]:
                budget.tick(1+len(c))
                if fixed<=other and not ({abs(x) for x in other-fixed}&used):
                    ok=True
                    break
            if not ok:
                return False
        return True
    def visit(i):
        nonlocal attempts,limited
        if i==len(order):
            return tuple(assigned[v] for v in range(1,t["n"]+1))
        v=order[i]
        for u in variables:
            if u in used:
                continue
            for x in (u,-u):
                if attempts>=limit:
                    limited=True
                    return None
                attempts+=1
                budget.tick()
                assigned[v]=x
                used.add(u)
                result=visit(i+1) if possible() else None
                used.remove(u)
                del assigned[v]
                if result is not None:
                    return result
                if limited:
                    return None
        return None
    embedding=visit(0)
    if embedding is not None:
        verify_embedding(n,clauses,t,embedding,budget)
    return {"status":"matched" if embedding is not None else ("candidate_limit" if limited else "not_found"),
            "embedding":embedding,"candidates":attempts}
