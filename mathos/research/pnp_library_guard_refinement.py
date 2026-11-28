"""Counterexample-guided guard weakening with bounded proof repair."""
from .pnp_proof_library import counterexample,verify_certificate,clause,mapped
from .pnp_library_ablation import independent_replay
from .pnp_resolution_refutation import propose,verify
from .pnp_structural_kernel import Budget,Exhausted
from .pnp_evidence_benchmark import digest

REFINE_STEPS=4_000_000


def check_entailment(n,guards,steps,budget):
    verify_certificate(n,guards,steps,budget,contradiction=False)
    goal=steps[-1]
    independent_replay(n,list(guards)+[(-x,) for x in goal],list(steps)+[()])


def repair(n,guards,goal,budget):
    """Lift a checked resolution refutation of guards + negated goal.

    Tautological lifted clauses need not be emitted. All remaining clauses
    and the final goal are checked by RUP against the weaker guard.
    """
    try:
        verify_certificate(n,guards,[goal],budget,contradiction=False)
        return (goal,)
    except ValueError:
        pass
    augmented=list(guards)+[(-x,) for x in goal]
    dag=propose(n,augmented,budget,width=8,records=8192)
    if dag is None:
        return None
    verify(n,augmented,dag,budget)
    steps=[]
    seen=set(guards)
    for s in dag["steps"]:
        budget.tick()
        c=clause(set(mapped(s["clause"],dag["new_to_old"]))|set(goal))
        if any(-x in c for x in c) or c in seen:
            continue
        seen.add(c)
        steps.append(c)
    if not steps or steps[-1]!=goal:
        steps.append(goal)
    check_entailment(n,guards,tuple(steps),budget)
    if len(steps)>64:
        return None
    return tuple(steps)


def refine_template(f,budget,*,allow_repair):
    """Greedy deletion, preserving original goal and variable numbering."""
    n=f["n"]
    guards=tuple(tuple(c) for c in f["axioms"])
    steps=tuple(tuple(c) for c in f["steps"])
    goal=steps[-1]
    check_entailment(n,guards,steps,budget)
    trace=[]
    for c in tuple(guards):
        trial=tuple(a for a in guards if a!=c)
        model=counterexample(n,trial,goal,budget)
        if model is not None:
            trace.append({"removed":c,"status":"counterexample","model":model})
            continue
        try:
            check_entailment(n,trial,steps,budget)
            new_steps=steps
            status="replay"
        except ValueError:
            if not allow_repair:
                trace.append({"removed":c,"status":"replay_blocked"})
                continue
            new_steps=repair(n,trial,goal,budget)
            if new_steps is None:
                trace.append({"removed":c,"status":"repair_blocked"})
                continue
            status="repaired"
        guards,steps=trial,new_steps
        trace.append({"removed":c,"status":status})
    out={**f,"axioms":guards,"steps":steps,
         "edges":f["edges"] if guards==tuple(tuple(c) for c in f["axioms"]) else ()}
    check_entailment(n,guards,steps,budget)
    # Counterexamples for rejected deletions remain valid as other guards
    # are removed. A blocked proof search is not a minimality witness.
    minimal=all(r["status"] in ("counterexample","replay","repaired") for r in trace)
    return out,trace,minimal


def refine_library(library,*,allow_repair):
    frozen=digest(library)
    out=[]
    records=[]
    for i,f in enumerate(library):
        b=Budget(seconds=60,max_steps=REFINE_STEPS,max_cells=100000)
        try:
            g,trace,minimal=refine_template(f,b,allow_repair=allow_repair)
            record={"id":i,"status":"checked","trace":trace,"deletion_minimal":minimal}
        except Exhausted:
            g=f
            record={"id":i,"status":"resource_exhausted","trace":[],"deletion_minimal":False}
        out.append(g)
        records.append({**record,"source_sha256":digest(f),"result_sha256":digest(g),
                        "work":b.steps})
    if frozen!=digest(library):
        raise AssertionError("source mutation")
    return tuple(out),records
