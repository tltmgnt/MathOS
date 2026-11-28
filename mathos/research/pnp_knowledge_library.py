"""Verified contradiction library with bounded subsumption and retrieval.

Only checked resolution templates enter the library. Index filters are
necessary conditions for EXACT signed inclusion, not SAT criteria.
Strengthened premise reuse has a separate verifier and search mode.
"""
from collections import Counter
from .pnp_structural_kernel import normalize, validate, Budget, Exhausted
from .pnp_proof_abstraction import verify_template, verify_embedding, find_embedding
from .pnp_evidence_benchmark import digest

MAX_TEMPLATES=32
MATCH_LIMIT=4096


def budget():
    return Budget(seconds=10,max_steps=2_000_000,max_cells=100_000)


def signature(t):
    return {"variables":t["n"],"widths":[[w,c] for w,c in sorted(Counter(map(len,t["axioms"])).items())]}


def _order(t):
    return (t["n"],len(t["axioms"]),len(t["steps"]),digest(t))


def _eligible(sig,n,widths):
    return sig["variables"]<=n and all(widths[w]>=c for w,c in sig["widths"])


def _templates(ts):
    if not isinstance(ts,(list,tuple)) or len(ts)>MAX_TEMPLATES:
        raise ValueError("invalid library size")
    for t in ts:
        verify_template(t,budget())
    return sorted(ts,key=_order)


def build(templates):
    """Keep earlier sufficient templates; record checked subsumption witnesses.

    A template is redundant if an already retained contradiction embeds
    in its axiom set. The bounded search may miss redundancy. No claim
    of minimum library size or canonicalization under signed renaming.
    """
    ordered=_templates(templates)
    retained=[]
    dispositions=[]
    for t in ordered:
        tid=digest(t)
        found=None
        counts=Counter(map(len,t["axioms"]))
        for e in retained:
            if not _eligible(e["signature"],t["n"],counts):
                continue
            try:
                a=find_embedding(t["n"],t["axioms"],e["template"],budget(),limit=MATCH_LIMIT)
            except Exhausted:
                continue
            if a["status"]=="matched":
                found={"template_id":tid,"status":"covered","by":e["id"],"embedding":a["embedding"]}
                break
        if found is None:
            retained.append({"id":tid,"signature":signature(t),"template":t})
            found={"template_id":tid,"status":"retained"}
        dispositions.append(found)
    lib={"schema":"mathos-pnp-knowledge-library/1","entries":retained,"dispositions":dispositions,
         "input_ids":[digest(t) for t in ordered]}
    verify_library(templates,lib)
    return lib


def verify_library(templates,lib):
    ordered=_templates(templates)
    if (lib["schema"]!="mathos-pnp-knowledge-library/1" or
            lib["input_ids"]!=[digest(t) for t in ordered] or
            len(lib["dispositions"])!=len(ordered)):
        raise ValueError("library provenance mismatch")
    entries=iter(lib["entries"])
    retained={}
    for t,d in zip(ordered,lib["dispositions"]):
        tid=digest(t)
        if d["template_id"]!=tid:
            raise ValueError("disposition mismatch")
        if d["status"]=="retained":
            e=next(entries,None)
            if (e is None or e["id"]!=tid or tid in retained or
                    digest(e["template"])!=tid or e["signature"]!=signature(t)):
                raise ValueError("retained template mismatch")
            retained[tid]=e["template"]
        elif d["status"]=="covered":
            if d["by"] not in retained:
                raise ValueError("invalid coverage dependency")
            verify_embedding(t["n"],t["axioms"],retained[d["by"]],d["embedding"],budget())
        else:
            raise ValueError("invalid library disposition")
    if next(entries,None) is not None:
        raise ValueError("unexpected retained entry")
    return True


def _target(n,f):
    nn,nf,mapping=normalize(n,f)
    return nn,{tuple(sorted(mapping[abs(x)-1] if x>0 else -mapping[abs(x)-1] for x in c)) for c in nf}


def _mapped(c,embedding):
    return {embedding[x-1] if x>0 else -embedding[-x-1] for x in c}


def verify_strengthening(n,f,t,embedding,witnesses,b):
    """A target subclause of each mapped axiom entails that axiom."""
    ax=verify_template(t,b)
    if (len(embedding)!=t["n"] or any(type(x) is not int or not 0<abs(x)<=n for x in embedding)
            or len({abs(x) for x in embedding})!=len(embedding) or len(witnesses)!=len(ax)):
        raise ValueError("invalid strengthening witness")
    _,target=_target(n,f)
    for c,raw in zip(ax,witnesses):
        q=tuple(raw)
        b.tick(1+len(c)+len(q))
        if (any(type(x) is not int for x in q) or q not in target or
                not set(q)<=_mapped(c,embedding)):
            raise ValueError("target clause does not strengthen mapped axiom")
    return True


def strengthen(n,f,t,embedding,b):
    """Find premise witnesses for a supplied embedding, not the embedding itself."""
    ax=verify_template(t,b)
    if (len(embedding)!=t["n"] or any(type(x) is not int or not 0<abs(x)<=n for x in embedding)
            or len({abs(x) for x in embedding})!=len(embedding)):
        raise ValueError("invalid signed injection")
    _,target=_target(n,f)
    ordered=sorted(target,key=lambda c:(len(c),c))
    witnesses=[]
    for c in ax:
        mapped=_mapped(c,embedding)
        found=None
        for q in ordered:
            b.tick(1+len(q))
            if set(q)<=mapped:
                found=q
                break
        if found is None:
            return None
        witnesses.append(found)
    verify_strengthening(n,f,t,embedding,witnesses,b)
    return witnesses


def query(n,f,lib,*,indexed=True,limit=MATCH_LIMIT):
    """Compare exact-inclusion retrieval with/without necessary filters.

    Each matching attempt gets an identical separate cooperative budget.
    Counts exclude external replay and index construction. No match is
    unknown, never a SAT decision. Candidate limit is per template.
    """
    if type(indexed) is not bool or type(limit) is not int or not 1<=limit<=MATCH_LIMIT:
        raise ValueError("invalid query options")
    nn,target=_target(n,f)
    counts=Counter(map(len,target))
    attempts=[]
    match=None
    skipped=[]
    for e in lib["entries"]:
        t=e["template"]
        if e["id"]!=digest(t) or e["signature"]!=signature(t):
            raise ValueError("invalid indexed entry")
        if indexed and not _eligible(e["signature"],nn,counts):
            skipped.append(e["id"])
            continue
        b=budget()
        try:
            a=find_embedding(n,f,t,b,limit=limit)
        except Exhausted:
            a={"status":"resource_exhausted","embedding":None,"candidates":None}
        attempts.append({"id":e["id"],**a,"work_steps":b.steps})
        if a["status"]=="matched":
            verify_embedding(n,f,t,a["embedding"],budget())
            match={"id":e["id"],"embedding":a["embedding"]}
            break
    return {"decision":"unsat" if match is not None else "unknown","match":match,
            "indexed":indexed,"limit":limit,"attempts":attempts,"skipped":skipped,
            "work_steps":sum(a["work_steps"] for a in attempts)}


def verify_query(n,f,lib,r):
    """Replay the credited match and checked skip conditions, not failed search."""
    nn,target=_target(n,f)
    counts=Counter(map(len,target))
    if type(r["indexed"]) is not bool or type(r["limit"]) is not int or not 1<=r["limit"]<=MATCH_LIMIT:
        raise ValueError("invalid query configuration")
    attempts=iter(r["attempts"])
    skipped=iter(r["skipped"])
    used=0
    match=None
    for e in lib["entries"]:
        t=e["template"]
        if e["id"]!=digest(t) or e["signature"]!=signature(t):
            raise ValueError("invalid query index")
        if r["indexed"] and not _eligible(e["signature"],nn,counts):
            if next(skipped,None)!=e["id"]:
                raise ValueError("skip mismatch")
            continue
        a=next(attempts,None)
        if (a is None or a["id"]!=e["id"] or a["status"] not in
                ("matched","not_found","candidate_limit","resource_exhausted") or
                type(a["work_steps"]) is not int or not 0<=a["work_steps"]<=2_000_000):
            raise ValueError("attempt metadata mismatch")
        used+=a["work_steps"]
        if a["status"]=="resource_exhausted":
            if a["candidates"] is not None:
                raise ValueError("exhaustion metadata mismatch")
        elif type(a["candidates"]) is not int or not 0<=a["candidates"]<=r["limit"]:
            raise ValueError("invalid candidate count")
        if a["status"]=="matched":
            verify_embedding(n,f,t,a["embedding"],budget())
            match={"id":e["id"],"embedding":a["embedding"]}
            break
        if a["embedding"] is not None:
            raise ValueError("uncredited embedding")
    if (next(attempts,None) is not None or next(skipped,None) is not None or
            digest(r["match"])!=digest(match) or r["work_steps"]!=used or
            r["decision"]!=("unsat" if match is not None else "unknown")):
        raise ValueError("query conclusion mismatch")
    return True
