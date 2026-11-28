"""Barrier-aware evaluation of a fixed hypothesis grammar, not an autonomous theorem prover."""
import argparse
import json
from itertools import combinations
from pathlib import Path

from .pnp_component_parity import propose,verify
from .pnp_cross_model import prism
from .pnp_proof_simulation_frontier import run as simulation_run,audit as simulation_audit
from .pnp_barrier_frontier import run as barrier_run,audit as barrier_audit
from .pnp_certificate_routes import propose as semantic,verify as verify_semantic
from .pnp_dual_bounds import converge,verify_bounds
from .pnp_structural_kernel import primal,normalize,brute,Exhausted
from .pnp_inference_complexity import budget
from .pnp_evidence_benchmark import digest
from .pnp_outcome_registry import decompose
from .pnp_outcome_engine import checkpoint

SCHEMA="mathos-pnp-hypothesis-obligations/1"

# These are explicit statements, not claims discovered from a finite sample.
GRAMMAR=(
    ("H26.1","Even global XOR charge suffices for SAT in every recognized graph-parity CNF.",
     "refuted","component_evenness"),
    ("H26.2","Every recognized graph-parity CNF is SAT iff every graph component has even charge.",
     "documented_scoped_theorem","component_evenness"),
    ("H26.3","Unsigned primal graph determines satisfiability.",
     "refuted","graph_twins"),
    ("H26.4","Every SAT-preserving polynomial transformation preserves exponential resolution lower bounds.",
     "refuted_by_documented_family","simulation_escape"),
    ("H26.5","There is a uniform polynomial-time SAT-preserving transformation to certified logarithmic width.",
     "unresolved","U04"),
    ("H26.6","A lower bound for ordinary resolution implies a lower bound for every deterministic SAT algorithm.",
     "invalid_inference_rule","simulation_escape"),
)

# These statuses are deliberately conservative. Conditional implications
# and scoped counterexamples cannot close universal obligations.
NODES=(
    ("U01","Uniform representation and correctness for arbitrary encoded CNFs",(),"unresolved"),
    ("U02","Polynomial bit complexity including all transformations and recognition",(),"unresolved"),
    ("U03","Output size polynomial and certified width <= c log2(output size), fixed c",(),"unresolved"),
    ("U04","Construct a single total transformation satisfying U01-U03",("U01","U02","U03"),"unresolved"),
    ("U05","Prove general SAT decision via elimination on certified logarithmic width",("U04",),"conditional_implication_only"),
    ("L01","Prove an algorithm-independent lower bound or justify a universal simulation into a restricted model",(),"unresolved"),
    ("L02","Prove the simulation has polynomial overhead and includes every polynomial-time SAT decider",("L01",),"unresolved"),
    ("L03","Transfer a superpolynomial bound through that simulation",("L02",),"conditional_implication_only"),
    ("F01","Independently formalize the exact universal theorem",(),"unresolved"),
    ("E01","P=NP",("U05","F01"),"unresolved"),
    ("E02","P!=NP",("L03","F01"),"unresolved"),
)


def obligations():
    return [{"id":i,"statement":s,"depends_on":list(d),"status":t} for i,s,d,t in NODES]


def disconnected(m,odd_left,odd_right):
    n,f,_=prism(m,inconsistent=odd_left)
    k,g,_=prism(m,inconsistent=odd_right)
    shifted=tuple(tuple(x+n if x>0 else x-n for x in c) for c in g)
    return n+k,tuple(f)+shifted


def parity_cases():
    result=[]
    for m in (3,6,12,24):
        for a,b in ((False,False),(True,False),(False,True),(True,True)):
            result.append((m,a,b,*disconnected(m,a,b)))
    return result


def graph_twins():
    f=tuple(combinations(range(1,9),2))
    return 8,f,f+((-1,),(-2,))


def graph_control():
    n,f,g=graph_twins()
    graph=primal(n,f,budget())
    if graph!=primal(n,g,budget()):
        raise AssertionError("graph mismatch")
    bounds=converge(graph,budget())
    verify_bounds(graph,bounds,budget())
    proofs=[semantic(n,c,"two_sat",budget()) for c in (f,g)]
    for c,p in zip((f,g),proofs):
        verify_semantic(n,c,p,budget())
    return {"bounds":bounds,"proofs":proofs}


def verify_graph(a):
    n,f,g=graph_twins()
    graph=primal(n,f,budget())
    if graph!=primal(n,g,budget()):
        raise ValueError("different graphs")
    verify_bounds(graph,a["bounds"],budget())
    if a["bounds"]["lower"]!=7 or a["bounds"]["upper"]!=7 or len(a["proofs"])!=2:
        raise ValueError("missing exact graph bound or decisions")
    for c,p,sat in zip((f,g),a["proofs"],(True,False)):
        verify_semantic(n,c,p,budget())
        if p["route"]!="two_sat" or (not p["clauses"])!=sat:
            raise ValueError("incorrect decision")
    return True


def hypotheses(rows):
    counterexample=next(i for i,r in enumerate(rows) if r["proof"]["global_rhs"]==0 and r["proof"]["decision"]=="unsat")
    out=[]
    for i,s,t,e in GRAMMAR:
        item={"id":i,"statement":s,"status":t,"evidence":e}
        if i=="H26.1":
            item["counterexample_row"]=counterexample
        if i=="H26.5":
            item["missing"]=["U01","U02","U03","U04","F01"]
        if i=="H26.6":
            item["missing"]=["L01","L02","F01"]
        out.append(item)
    return out


def run(simulation,barriers,*,checkpoint_path=None):
    simulation_audit(simulation)
    barrier_audit(barriers)
    r={"schema":SCHEMA,"upstream":[digest(simulation),digest(barriers)],"rows":[],
       "obligations":obligations(),"barriers":barriers["dossier"]["barriers"],
       "registry":[decompose(x) for x in ("E01","E02","E07","E08","E09","E12","E19")],
       "completion":"running","universal_obligation":"unresolved",
       "p_equals_np_established":False,"p_not_equals_np_established":False,"novel_theorem_verified":False}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        r["graph_control"]=graph_control()
        for m,a,b,n,f in parity_cases():
            p=propose(n,f,budget())
            if p is None:
                raise AssertionError("recognition failed")
            verify(n,f,p,budget())
            if (p["decision"]=="unsat")!=(a or b):
                raise AssertionError("component decision mismatch")
            r["rows"].append({"m":m,"odd_left":a,"odd_right":b,"proof":p})
            save()
        r["hypotheses"]=hypotheses(r["rows"])
        r["completion"]="completed"
    except Exhausted as e:
        r["completion"],r["reason"]="resource_exhausted",str(e)
    except (ValueError,AssertionError) as e:
        r["completion"],r["reason"]="diagnostic_required",str(e)
    r["summary"]=summary(r)
    save()
    return r


def summary(r):
    return {"cases":len(r["rows"]),
            "sat":sum(x["proof"]["decision"]=="sat" for x in r["rows"]),
            "unsat":sum(x["proof"]["decision"]=="unsat" for x in r["rows"]),
            "even_global_unsat":sum(x["proof"]["global_rhs"]==0 and x["proof"]["decision"]=="unsat" for x in r["rows"]),
            "hypotheses":len(r.get("hypotheses",[])),
            "unresolved_roots":2,"barriers_overcome":0}


def audit(simulation,barriers,r):
    simulation_audit(simulation)
    barrier_audit(barriers)
    if (r["schema"]!=SCHEMA or r["upstream"]!=[digest(simulation),digest(barriers)]
            or r["completion"]!="completed" or r["universal_obligation"]!="unresolved"
            or r["obligations"]!=obligations() or r["barriers"]!=barriers["dossier"]["barriers"]
            or digest(r["registry"])!=digest([decompose(x) for x in ("E01","E02","E07","E08","E09","E12","E19")])
            or any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))):
        raise ValueError("invalid hypothesis governance")
    verify_graph(r["graph_control"])
    cases=parity_cases()
    if len(r["rows"])!=len(cases):
        raise ValueError("incomplete component cases")
    for row,(m,a,b,n,f) in zip(r["rows"],cases):
        if (row["m"],row["odd_left"],row["odd_right"])!=(m,a,b):
            raise ValueError("case mismatch")
        p=row["proof"]
        verify(n,f,p,budget())
        if (p["decision"]=="unsat")!=(a or b) or p["global_rhs"]!=int(a^b) or len(p["components"])!=2:
            raise ValueError("invalid component verdict")
    if r["hypotheses"]!=hypotheses(r["rows"]) or r["summary"]!=summary(r):
        raise ValueError("hypothesis or summary mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--simulation",type=Path)
    p.add_argument("--barriers",type=Path)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    a=p.parse_args(argv)
    def read(path):
        if path.stat().st_size>32_000_000:
            raise ValueError("oversized input")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        if bool(a.simulation)!=bool(a.barriers):
            raise ValueError("provide both upstream reports or neither")
        if a.checkpoint and any(a.checkpoint.resolve()==x.resolve() for x in (a.simulation,a.barriers) if x):
            raise ValueError("cannot overwrite upstream")
        s,b=(read(a.simulation),read(a.barriers)) if a.simulation else (simulation_run(),barrier_run())
        if a.audit:
            if not a.simulation:
                raise ValueError("audit requires exact upstream reports")
            audit(s,b,read(a.audit))
            print(json.dumps({"status":"replayed","universal_obligation":"unresolved"}))
            return 0
        r=run(s,b,checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return int(r["completion"]!="completed")
    except (OSError,ValueError,KeyError,TypeError,Exhausted) as e:
        p.error(str(e))


if __name__=="__main__":
    raise SystemExit(main())
