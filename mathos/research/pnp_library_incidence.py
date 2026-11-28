"""Necessary signed-incidence filters for subsumption guard retrieval.

For guards at the minimum known-clause width, a stronger witness must
have equal width and therefore be the exact signed image. Distinct
tight guards map to distinct witnesses, preserving pair signatures.
"""
from collections import Counter
from itertools import combinations

from .pnp_proof_abstraction import _original_clauses
from .pnp_proof_library import find, mapped, reconstruct, verify_certificate
from .pnp_structural_kernel import Exhausted

PAIR_CAP=4096


def pair_histogram(clauses,budget):
    """Return None rather than reject if the optional pair cap is exceeded."""
    if len(clauses)*(len(clauses)-1)//2>PAIR_CAP:
        return None
    sets=[]
    for c in sorted(clauses):
        budget.tick(1+len(c))
        s=frozenset(c)
        sets.append((s,frozenset(-x for x in s)))
    out=Counter()
    for (a,_),(b,nb) in combinations(sets,2):
        budget.tick()
        out[(len(a&b),len(a&nb))]+=1
    budget.cells(len(out))
    return out


class IncidenceFilter:
    """One snapshot cache, rebuilt immediately after a productive transfer."""
    def __init__(self,index):
        self.index=index
        self.guard_hist={}
        self.stats={k:0 for k in ("considered","width_rejected","count_rejected",
                                  "pair_rejected","matched_searches","snapshots",
                                  "pair_checks","pair_cap_skips","filter_work")}
        self.invalidate()

    def invalidate(self):
        self.width=None
        self.tight=()
        self.hist=None
        self.hist_ready=False

    def allows(self,i,known,budget):
        start=budget.steps
        self.stats["considered"]+=1
        try:
            budget.tick()
            if self.width is None:
                budget.tick(1+len(known))
                self.width=min(map(len,known),default=513)
                self.tight=tuple(sorted(c for c in known if len(c)==self.width))
                self.stats["snapshots"]+=1
            f=self.index.templates[i]
            guards={tuple(sorted(set(c))) for c in f["axioms"]}
            budget.tick(1+len(guards))
            if any(len(c)<self.width for c in guards):
                self.stats["width_rejected"]+=1
                return False
            tight=tuple(sorted(c for c in guards if len(c)==self.width))
            if len(tight)>len(self.tight):
                self.stats["count_rejected"]+=1
                return False
            if len(tight)>=2:
                self.stats["pair_checks"]+=1
                key=(i,self.width)
                if key not in self.guard_hist:
                    self.guard_hist[key]=pair_histogram(tight,budget)
                if not self.hist_ready:
                    self.hist=pair_histogram(self.tight,budget)
                    self.hist_ready=True
                need=self.guard_hist[key]
                if need is None or self.hist is None:
                    self.stats["pair_cap_skips"]+=1
                else:
                    budget.tick(1+len(need))
                    if any(v>self.hist[k] for k,v in need.items()):
                        self.stats["pair_rejected"]+=1
                        return False
            self.stats["matched_searches"]+=1
            return True
        finally:
            self.stats["filter_work"]+=budget.steps-start


def indexed_reuse(n,formula,index,budget,*,rounds=4,max_transfers=32):
    """Identical v17 ordering and matcher; only necessary filters added."""
    known=set(_original_clauses(n,formula))
    transfers=[]
    examined=0
    gate=IncidenceFilter(index)
    def result(status):
        return {"status":status,"examined":examined,"incidence":gate.stats}
    try:
        for _ in range(rounds):
            changed=False
            for i in index.retrieve(known):
                if not gate.allows(i,known,budget):
                    continue
                f=index.templates[i]
                examined+=1
                e=find(f,n,known,budget,subsumption=True)
                if e is None:
                    continue
                part=[mapped(c,e) for c in f["steps"]]
                verify_certificate(n,sorted(known),part,budget,contradiction=False)
                transfers.append((i,e))
                known.update(part)
                gate.invalidate()
                changed=True
                if () in known:
                    proof=reconstruct(n,formula,index,transfers,budget)
                    return {**result("verified"),"transfers":transfers,"proof":proof}
                if len(transfers)>=max_transfers:
                    return result("transfer_limit")
            if not changed:
                break
    except Exhausted:
        return result("resource_exhausted")
    return result("not_found")
