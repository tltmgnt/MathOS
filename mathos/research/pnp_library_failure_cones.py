"""Offline resolution-cone abstraction from observed retrieval failures."""
from .pnp_resolution_refutation import propose, verify
from .pnp_proof_abstraction import compress, verify_embedding
from .pnp_proof_library import fragments, canonical_structure, verify_certificate
from .pnp_library_canonical import canonical
from .pnp_library_ablation import independent_replay
from .pnp_structural_kernel import Exhausted, Budget
from .pnp_evidence_benchmark import digest

CAP=12


def discover(case,budget):
    """Offline only. No reference SAT label or evaluation target is used."""
    n,f=case["n"],case["clauses"]
    try:
        proof=propose(n,f,budget,width=8,records=8192,strategy="min_product")
        if proof is None:
            return {"status":"not_found"}
        verify(n,f,proof,budget)
        compressed=compress(n,f,proof,budget)
        return {"status":"verified","dag":proof,"compressed":compressed}
    except Exhausted:
        return {"status":"resource_exhausted"}


def source_cones(case,result,budget):
    """Rebuild from independently checked DAG and checked source embedding."""
    if result["status"]!="verified":
        return []
    n,f=case["n"],case["clauses"]
    verify(n,f,result["dag"],budget)
    c=compress(n,f,result["dag"],budget)
    if digest(c)!=digest(result["compressed"]):
        raise ValueError("compressed source mismatch")
    verify_embedding(n,f,c["template"],c["source_embedding"],budget)
    out=list(fragments(c["template"],budget))
    for t in out:
        verify_certificate(t["n"],t["axioms"],t["steps"],budget,contradiction=False)
        goal=t["steps"][-1]
        independent_replay(t["n"],list(t["axioms"])+[(-x,) for x in goal],
                           list(t["steps"])+[()])
    # Prefer reusable short nonempty conclusions, then refutation cores,
    # with identical ordering in failure and success cohorts.
    out.sort(key=lambda t:(not bool(t["steps"][-1]),len(t["steps"][-1]),
                           len(t["axioms"]),len(t["steps"]),digest(t)))
    return out


def key(t,budget):
    c=canonical(t,budget)
    if c["status"]=="exact":
        return ("orbit",c["key"])
    return ("structure",canonical_structure(t,budget))


def candidate_pool(base,rows,budget,*,missed):
    """Deterministic bounded pool, disjoint from base by checked structure."""
    seen={key(t,budget) for t in base}
    out=[]
    for row in rows:
        if (row["baseline"]["status"]!="verified")!=missed:
            continue
        c,r=row["case"],row["resolution"]
        for t in source_cones(c,r,budget):
            k=key(t,budget)
            if k in seen:
                continue
            seen.add(k)
            out.append({"source_sha256":digest(c),"dag_sha256":digest(r["dag"]),
                        "template":t})
            if len(out)>=CAP:
                return out
    return out


def matched_snapshots(base,rows,budget):
    failure=candidate_pool(base,rows,budget,missed=True)
    success=candidate_pool(base,rows,budget,missed=False)
    count=min(len(failure),len(success))
    pools={"failure":failure,"success":success}
    libs={"base":tuple(base)}
    for k,v in pools.items():
        libs[k]=tuple(base)+tuple(r["template"] for r in v[:count])
    return libs,pools,count
