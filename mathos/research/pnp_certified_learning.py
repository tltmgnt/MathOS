"""Certified failed-assumption lemmas and a bidirectional portfolio.

A resolution refutation of F plus assumptions implies their blocking
clause in F. Learned clauses are local to this input, never transferred
to unrelated formulas without a new proof.
"""
from itertools import combinations, product

from .pnp_structural_kernel import Budget, Exhausted, normalize, validate
from .pnp_resolution_refutation import propose, verify, STRATEGIES
from .pnp_evidence_scheduler import execute, replay
from .pnp_unified_portfolio import fingerprint

MAX_PROBES=24
MAX_TOTAL=2_000_000
RECORDS=8192


def _options(plan,total,seconds,probes):
    if (not isinstance(plan,(tuple,list)) or len(plan)!=2 or plan[0] not in STRATEGIES or
            type(plan[1]) is not int or not 1<=plan[1]<=12 or
            type(total) is not int or not 3<=total<=MAX_TOTAL or
            type(seconds) not in (int,float) or not 0<seconds<=60 or
            type(probes) is not int or not 0<=probes<=MAX_PROBES):
        raise ValueError("invalid hybrid options")


def candidates(n,f,limit):
    _,nf,mapping=normalize(n,f)
    counts={v:0 for v in mapping}
    for c in nf:
        for x in c:
            counts[mapping[abs(x)-1]]+=1
    vs=sorted(counts,key=lambda v:(-counts[v],v))[:8]
    out=[(s*v,) for v in vs for s in (1,-1)]
    out.extend(tuple(sorted(s*v for s,v in zip(signs,pair)))
               for pair in combinations(vs,2) for signs in product((1,-1),repeat=2))
    return out[:limit]


def verify_lemma(n,f,lemma,budget):
    """Replay refutation under assumptions; check exact negated conjunction."""
    assumptions=tuple(lemma["assumptions"])
    if (not 1<=len(assumptions)<=2 or
            any(type(x) is not int or not 0<abs(x)<=n for x in assumptions) or
            len({abs(x) for x in assumptions})!=len(assumptions) or
            tuple(sorted(assumptions))!=assumptions):
        raise ValueError("invalid assumption conjunction")
    clause=tuple(lemma["clause"])
    if any(type(x) is not int for x in clause) or clause!=tuple(sorted(-x for x in assumptions)):
        raise ValueError("incorrect blocking clause")
    verify(n,tuple(f)+tuple((x,) for x in assumptions),lemma["proof"],budget)
    return clause


def _resolve(n,f,plan,quota,seconds):
    b=Budget(seconds=seconds,max_steps=quota,max_cells=50_000)
    try:
        proof=propose(n,f,b,strategy=plan[0],width=plan[1],records=RECORDS)
        if proof is not None:
            verify(n,f,proof,b)
        status="refuted" if proof is not None else "unrecognized"
    except Exhausted:
        proof,status=None,"resource_exhausted"
    return {"quota":quota,"work_steps":b.steps,"status":status,"proof":proof}


def _check_resolution(n,f,plan,a):
    if (type(a["quota"]) is not int or a["quota"]<1 or
            type(a["work_steps"]) is not int or not 0<=a["work_steps"]<=a["quota"] or
            a["status"] not in ("refuted","unrecognized","resource_exhausted")):
        raise ValueError("invalid resolution attempt")
    p=a["proof"]
    if a["status"]=="refuted":
        if p is None or (p["strategy"],p["width_cap"])!=tuple(plan) or p["record_cap"]!=RECORDS:
            raise ValueError("resolution plan mismatch")
        verify(n,f,p,Budget(seconds=10,max_steps=4_000_000,max_cells=50_000))
    elif p is not None:
        raise ValueError("uncredited resolution proof")


def solve(n,clauses,policy,plan,*,total=100_000,seconds=5,probes=16):
    """Run learned scheduler, refutation, failed-assumption probes, scheduler.

    Fixed non-borrowing phase ceilings; each subrun has its own deadline,
    with allocated time fractions summing to seconds. The work totals
    exclude independent external audit and ordinary Python overhead.
    """
    _options(plan,total,seconds,probes)
    f=validate(n,clauses)
    first=total//3
    second=total//3
    remaining=total-first-second
    # Reserve half the final phase for a fresh scheduler attempt.
    learning=remaining//2 if probes else 0
    last=remaining-learning
    report={"schema":"mathos-pnp-certified-learning/1","input_sha256":fingerprint(n,f),
            "plan":list(plan),"total_steps":total,"seconds":seconds,"probe_limit":probes,
            "initial":execute(n,f,policy,"learned",first,seconds/3),
            "refutation":None,"probes":[],"final":None}
    decision=report["initial"]["decision"]
    if decision=="unknown":
        a=_resolve(n,f,plan,second,seconds/3)
        report["refutation"]=a
        if a["status"]=="refuted":
            decision="unsat"
    extended=list(f)
    if decision=="unknown":
        choices=candidates(n,f,probes)
        quota=learning//len(choices) if choices else 0
        if quota:
            for assumptions in choices:
                a=_resolve(n,tuple(extended)+tuple((x,) for x in assumptions),
                           plan,quota,seconds/(6*len(choices)))
                lemma=None
                if a["status"]=="refuted":
                    lemma={"assumptions":assumptions,"clause":tuple(sorted(-x for x in assumptions)),
                           "proof":a["proof"]}
                    # Exact blocking clause follows from the replayed proof.
                    extended.append(lemma["clause"])
                report["probes"].append({"assumptions":assumptions,"attempt":a,"lemma":lemma})
        report["final"]=execute(n,extended,policy,"learned",last,seconds/6 if probes else seconds/3)
        decision=report["final"]["decision"]
    report["decision"]=decision
    report["learned_clauses"]=len(extended)-len(f)
    report["work_steps"]=report["initial"]["work_steps"]+(
        report["refutation"]["work_steps"] if report["refutation"] else 0)+sum(
        p["attempt"]["work_steps"] for p in report["probes"])+(
        report["final"]["work_steps"] if report["final"] else 0)
    verify_hybrid(n,f,policy,report)
    return report


def verify_hybrid(n,clauses,policy,r):
    """Independently replay the original-input proof chain and final verdict."""
    f=validate(n,clauses)
    plan,total,seconds,probes=(r[x] for x in ("plan","total_steps","seconds","probe_limit"))
    _options(plan,total,seconds,probes)
    if r["schema"]!="mathos-pnp-certified-learning/1" or r["input_sha256"]!=fingerprint(n,f):
        raise ValueError("input binding mismatch")
    first=second=total//3
    remaining=total-first-second
    learning=remaining//2 if probes else 0
    last=remaining-learning
    initial=r["initial"]
    if initial["arm"]!="learned":
        raise ValueError("incorrect initial arm")
    replay(n,f,policy,first,initial)
    decision=initial["decision"]
    work=initial["work_steps"]
    a=r["refutation"]
    if decision=="unknown":
        if a is None or a["quota"]!=second:
            raise ValueError("missing refutation phase")
        _check_resolution(n,f,plan,a)
        work+=a["work_steps"]
        if a["status"]=="refuted":
            decision="unsat"
    elif a is not None:
        raise ValueError("unexpected refutation phase")
    extended=list(f)
    if decision=="unknown":
        choices=candidates(n,f,probes)
        quota=learning//len(choices) if choices else 0
        if len(r["probes"])!=(len(choices) if quota else 0):
            raise ValueError("probe coverage mismatch")
        for assumptions,p in zip(choices,r["probes"]):
            a=p["attempt"]
            if tuple(p["assumptions"])!=assumptions or a["quota"]!=quota:
                raise ValueError("probe schedule mismatch")
            _check_resolution(n,tuple(extended)+tuple((x,) for x in assumptions),plan,a)
            work+=a["work_steps"]
            lemma=p["lemma"]
            if a["status"]=="refuted":
                if (lemma is None or tuple(lemma["assumptions"])!=assumptions or
                        lemma["proof"]!=a["proof"]):
                    raise ValueError("lemma provenance mismatch")
                extended.append(verify_lemma(n,extended,lemma,Budget(seconds=10,max_steps=4_000_000,max_cells=50_000)))
            elif lemma is not None:
                raise ValueError("unproved learned clause")
        final=r["final"]
        if final is None or final["arm"]!="learned":
            raise ValueError("missing final phase")
        replay(n,extended,policy,last,final)
        decision=final["decision"]
        work+=final["work_steps"]
    elif r["probes"] or r["final"] is not None:
        raise ValueError("unexpected learning phase")
    if (r["decision"]!=decision or type(r["work_steps"]) is not int or r["work_steps"]!=work or work>total or
            type(r["learned_clauses"]) is not int or r["learned_clauses"]!=len(extended)-len(f)):
        raise ValueError("hybrid conclusion or accounting mismatch")
    return True
