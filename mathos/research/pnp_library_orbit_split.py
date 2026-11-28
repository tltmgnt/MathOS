"""Strict signed-orbit exclusion for normalized whole CNFs.

Unused variables, duplicate clauses and tautologies are ignored. An exact
canonical key is required for every accepted case; unresolved buckets
are quarantined, never assumed disjoint.
"""
from collections import Counter
from .pnp_structural_kernel import normalize
from .pnp_library_canonical import canonical, signature, witness, verify_equivalence
from .pnp_evidence_benchmark import digest


def shape(case,budget):
    n,clauses,_=normalize(case["n"],case["clauses"])
    f={"n":n,"axioms":clauses,"steps":((),),"edges":()}
    _,_,groups=signature(f,budget)
    bucket=(n,tuple(sorted(Counter(map(len,clauses)).items())),
            tuple((len(g),sum(len(s)==2 for _,s in g)) for g in groups))
    return f,bucket


class Registry:
    def __init__(self,*,max_active=9,cap=8192):
        self.max_active=max_active
        self.cap=cap
        self.exact={}
        self.quarantine=set()
        self.counts=Counter()

    def register(self,case,budget,*,prior=False):
        f,bucket=shape(case,budget)
        if f["n"]>self.max_active:
            status="outside_support"
        else:
            c=canonical(f,budget,cap=self.cap)
            if c["status"]!="exact":
                self.quarantine.add(bucket)
                status="unresolved"
            elif c["key"] in self.exact:
                old,embedding=self.exact[c["key"]]
                verify_equivalence(f,old,witness(c["embedding"],embedding),budget)
                status="orbit_duplicate"
            elif not prior and bucket in self.quarantine:
                status="quarantined"
            else:
                self.exact[c["key"]]=(f,c["embedding"])
                status="accepted"
        self.counts[status]+=1
        return status

    def fingerprint(self):
        return digest({"exact":sorted(self.exact),"quarantine":sorted(self.quarantine),
                       "max_active":self.max_active,"cap":self.cap})


def select(registry,candidates,budget,*,per_family=24):
    """Deterministic label-free rejection sampling; fail on short strata."""
    families=("random2","random3","mixed1234")
    counts=Counter()
    reasons=Counter()
    chosen=[]
    for c in candidates:
        f=c["family"]
        if f not in families:
            raise ValueError("unexpected family")
        if counts[f]>=per_family:
            continue
        status=registry.register(c,budget)
        reasons[status]+=1
        if status=="accepted":
            chosen.append(c)
            counts[f]+=1
    if any(counts[f]!=per_family for f in families):
        raise ValueError("insufficient orbit-disjoint cases")
    return chosen,dict(reasons)
