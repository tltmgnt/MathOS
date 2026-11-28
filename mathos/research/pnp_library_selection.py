"""Two-epoch offline knowledge selection. Candidate generation never uses evaluation."""
from .pnp_evidence_benchmark import digest
from .pnp_abstraction_frontier import bytesize

BUNDLE=6


def bundles(current, expanded):
    """Deterministic equal-cardinality proposal cohorts, plus abstention."""
    if digest(tuple(expanded[:len(current)]))!=digest(tuple(current)):
        raise ValueError("not an append-only admission")
    new=list(range(len(current),len(expanded)))
    first=new[:BUNDLE]
    compact=sorted(new,key=lambda i:(bytesize(expanded[i]),i))[:BUNDLE]
    short=sorted(new,key=lambda i:(len(expanded[i]["steps"][-1]),
                                  len(expanded[i]["axioms"]),
                                  len(expanded[i]["steps"]),i))[:BUNDLE]
    # Favor nonempty short consequences, distinct from whole-core priority.
    consequences=sorted(new,key=lambda i:(not bool(expanded[i]["steps"][-1]),
                                         expanded[i]["n"],bytesize(expanded[i]),i))[:BUNDLE]
    cohorts={"retain":tuple(current)}
    seen={digest(current)}
    for name,ids in (("first",first),("compact",compact),("short",short),
                     ("consequences",consequences)):
        lib=tuple(current)+tuple(expanded[i] for i in sorted(ids))
        h=digest(lib)
        if h not in seen:
            seen.add(h)
            cohorts[name]=lib
    return cohorts


def choose(rows, cohorts):
    """No discovery loss allowed; accept coverage gain or lower counted work.

    Negative outcomes and counters are experimental observations, not proofs.
    Tie-breaking is deterministic and ignores wall time.
    """
    if "retain" not in cohorts:
        raise ValueError("missing incumbent")
    for row in rows:
        if set(row["arms"])!=set(cohorts):
            raise ValueError("cohort mismatch")
    hits={k:{i for i,r in enumerate(rows) if r["arms"][k]["status"]=="verified"}
          for k in cohorts}
    work={k:sum(r["arms"][k]["work"] for r in rows) for k in cohorts}
    incumbent=hits["retain"]
    eligible=[k for k in cohorts if hits[k]>=incumbent and
              (len(hits[k])>len(incumbent) or work[k]<work["retain"])]
    return min(eligible,key=lambda k:(-len(hits[k]),work[k],len(cohorts[k]),k)) if eligible else "retain"


def union_snapshot(base, pools):
    """Ungated comparator: identical generated candidate pools, digest dedup."""
    out=list(base)
    seen={digest(t) for t in base}
    for pool in pools:
        for t in pool:
            h=digest(t)
            if h not in seen:
                out.append(t)
                seen.add(h)
    return tuple(out)
