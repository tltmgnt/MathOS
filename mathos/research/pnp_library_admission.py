"""Offline admission of checked portfolio consequences; immutable library snapshots."""
from .pnp_proof_abstraction import _original_clauses
from .pnp_proof_library import (Index, mapped, variables, verify_certificate,
                                canonical_structure)
from .pnp_schema_portfolio import verify as verify_portfolio
from .pnp_library_ablation import independent_replay
from .pnp_evidence_benchmark import digest

MAX_NEW=24
MAX_PREFIX=64
MAX_GUARDS=48


def fragments(n,formula,proof,budget):
    """Extract bounded RUP prefixes, including nonempty consequences.

    Greedy guard deletion accepts only successful RUP replay; neither
    global minimality nor all semantic consequences are claimed.
    """
    verify_certificate(n,formula,proof,budget)
    independent_replay(n,formula,proof)
    original=tuple(sorted(_original_clauses(n,formula)))
    if len(original)>MAX_GUARDS or len(proof)>MAX_PREFIX:
        return []
    roots=[]
    seen=set(original)
    for j,c in enumerate(proof):
        c=tuple(c)
        if c not in seen and 0<len(c)<=2 and len(roots)<2:
            roots.append(j)
        seen.add(c)
    if proof and not proof[-1]:
        roots.append(len(proof)-1)
    out=[]
    for j in roots:
        steps=tuple(tuple(c) for c in proof[:j+1])
        guards=list(original)
        for c in original:
            budget.tick()
            trial=[a for a in guards if a!=c]
            try:
                verify_certificate(n,trial,steps,budget,contradiction=False)
            except ValueError:
                continue
            guards=trial
        active=variables(guards+list(steps))
        if len(active)>9:
            continue
        label={v:i+1 for i,v in enumerate(active)}
        def dense(c):
            return tuple(sorted(label[abs(x)] if x>0 else -label[abs(x)] for x in c))
        t={"n":len(active),"axioms":tuple(sorted(map(dense,guards))),
           "steps":tuple(map(dense,steps)),"edges":()}
        record={"template":t,"embedding":tuple(active),"root":j}
        verify_fragment(n,formula,proof,record,budget)
        out.append(record)
    return out


def verify_fragment(n,formula,proof,record,budget):
    """Bind a fragment to its source prefix and check its standalone entailment."""
    t,e,j=record["template"],record["embedding"],record["root"]
    if (type(t["n"]) is not int or not 0<=t["n"]<=9 or len(e)!=t["n"]
            or any(type(x) is not int or not 0<x<=n for x in e)
            or tuple(e)!=tuple(sorted(set(e))) or type(j) is not int
            or not 0<=j<len(proof) or not 1<=len(t["steps"])<=MAX_PREFIX
            or len(t["axioms"])>MAX_GUARDS or t["edges"] not in ((),[])):
        raise ValueError("invalid fragment metadata")
    verify_certificate(t["n"],t["axioms"],t["steps"],budget,contradiction=False)
    known=set(_original_clauses(n,formula))
    if any(mapped(c,e) not in known for c in t["axioms"]):
        raise ValueError("guard not present in training source")
    if [mapped(c,e) for c in t["steps"]]!=[tuple(c) for c in proof[:j+1]]:
        raise ValueError("fragment not a source prefix")
    goal=t["steps"][-1]
    if len(goal)>2:
        raise ValueError("unsupported conclusion")
    # Independently establish guard entails goal by refuting guard + negated goal.
    independent_replay(t["n"],list(t["axioms"])+[(-x,) for x in goal],
                       list(t["steps"])+[()])
    return True


def admit(base,training,budget):
    """Reconstruct verified training proofs; append at most MAX_NEW fragments.

    The original library is preserved; new entries never influence training.
    Return provenance per admitted entry and a frozen tuple.
    """
    before=digest(base)
    index=Index(base)
    keys={canonical_structure(t,budget) for t in base}
    library=list(base)
    lineage=[]
    for row in training:
        if len(lineage)>=MAX_NEW:
            break
        c,r=row["case"],row["result"]
        if r["status"]!="verified":
            continue
        proof=verify_portfolio(c["n"],c["clauses"],index,r["recipe"],budget)
        if digest(proof)!=digest(r["proof"]):
            raise ValueError("source proof mismatch")
        for record in fragments(c["n"],c["clauses"],proof,budget):
            t=record["template"]
            key=canonical_structure(t,budget)
            if key in keys:
                continue
            keys.add(key)
            library.append(t)
            lineage.append({"source_sha256":digest(c),"source_proof_sha256":digest(proof),
                            "library_id":len(library)-1,"fragment":record})
            if len(lineage)>=MAX_NEW:
                break
    if digest(base)!=before:
        raise AssertionError("base mutated")
    return tuple(library),lineage
