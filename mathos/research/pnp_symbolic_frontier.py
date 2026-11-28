"""Audit symbolic compatibility synthesis beyond finite charge enumeration."""
import argparse
import json
import random
from pathlib import Path

from .pnp_symbolic_parity import synthesize,verify,decide,verify_decision,parity
from .pnp_cross_model import prism
from .pnp_growing_width import family as torus
from .pnp_expander_size import family as expander
from .pnp_conjecture_frontier import audit as audit_v27
from .pnp_evidence_benchmark import digest
from .pnp_inference_complexity import budget
from .pnp_outcome_engine import checkpoint
from .pnp_outcome_registry import decompose
from .pnp_structural_kernel import Exhausted

SCHEMA="mathos-pnp-symbolic-frontier/1"
SEED=28028


def _mask(vs):
    return sum(1<<(v-1) for v in vs)


def cases():
    result=[("empty",0,[]),("zero_rows",3,[0,0]),
            ("duplicate",3,[3,3,5]),("non_graph",3,[3,6,5,7])]
    n,_,r=prism(3)
    rows=[_mask(vs) for vs,_ in r]
    result.append(("prism",n,rows))
    result.append(("disconnected_prism",2*n,rows+[a<<n for a in rows]))
    for s in (3,6,8):
        n,_,r=torus(s)
        result.append((f"torus_{s}",n,[_mask(vs) for vs,_ in r]))
    for s in (3,6):
        n,_,r=expander(s)
        result.append((f"expander_{s}",n,[_mask(vs) for vs,_ in r]))
    rng=random.Random(SEED)
    for j,(n,m) in enumerate(((8,12),(16,24),(32,48),(64,96),(96,128))):
        independent=[rng.getrandbits(n) for _ in range(m//2)]
        rows=independent+[rng.choice(independent)^rng.choice(independent) for _ in range(m-len(independent))]
        rng.shuffle(rows)
        result.append((f"mixed_{j}",n,rows))
    return [{"id":name,"n":n,"rows":rows} for name,n,rows in result]


def charges(case):
    n,rows=case["n"],case["rows"]
    m=len(rows)
    rng=random.Random(SEED+int(digest(case)[:8],16))
    # Four known attainable RHS, four arbitrary RHS, frozen without
    # using the generated check basis.
    attainable=[sum(parity(a&x)<<i for i,a in enumerate(rows))
                for x in (rng.getrandbits(n) for _ in range(4))]
    return attainable+[rng.getrandbits(m) for _ in range(4)]


def summary(records):
    return {"systems":len(records),
            "derived_checks":sum(len(r["criterion"]["checks"]) for r in records),
            "isolated_counterexamples":sum(len(r["criterion"]["refinements"]) for r in records),
            "max_rows":max((len(r["case"]["rows"]) for r in records),default=0),
            "max_columns":max((r["case"]["n"] for r in records),default=0),
            "max_symbolic_rhs_bits":max((len(r["case"]["rows"]) for r in records),default=0),
            "rhs_controls":sum(len(r["decisions"]) for r in records),
            "sat":sum(p["proof"]["decision"]=="sat" for r in records for p in r["decisions"]),
            "unsat":sum(p["proof"]["decision"]=="unsat" for r in records for p in r["decisions"]),
            "universal_obligations_closed":0,"barriers_overcome":0}


def run(simulation,barriers,hypotheses,refinement,*,checkpoint_path=None):
    inputs=(simulation,barriers,hypotheses,refinement)
    audit_v27(*inputs)
    r={"schema":SCHEMA,"upstream":[digest(x) for x in inputs],"records":[],
       "completion":"running","universal_obligation":"unresolved",
       "p_equals_np_established":False,"p_not_equals_np_established":False,
       "novel_theorem_verified":False,"barriers":barriers["dossier"]["barriers"],
       "objectives":[decompose(x) for x in ("E01","E02","E07","E12","E19")],
       "scope":"explicit GF(2) systems; exact all-RHS criterion via invertible row operations"}
    def save():
        if checkpoint_path:
            checkpoint(checkpoint_path,r)
    try:
        for case in cases():
            n,rows=case["n"],case["rows"]
            c=synthesize(n,rows,budget())
            verify(n,rows,c,budget())
            decisions=[]
            for b in charges(case):
                p=decide(n,rows,c,b,budget())
                verify_decision(n,rows,b,p,budget())
                decisions.append({"charge":b,"proof":p})
            r["records"].append({"case":case,"criterion":c,"decisions":decisions})
            save()
        r["completion"]="completed"
    except Exhausted as e:
        r["completion"],r["reason"]="resource_exhausted",str(e)
    except (ValueError,AssertionError) as e:
        r["completion"],r["reason"]="diagnostic_required",str(e)
    r["summary"]=summary(r["records"])
    save()
    return r


def audit(simulation,barriers,hypotheses,refinement,r):
    inputs=(simulation,barriers,hypotheses,refinement)
    audit_v27(*inputs)
    if (r["schema"]!=SCHEMA or r["upstream"]!=[digest(x) for x in inputs]
            or r["completion"]!="completed" or r["universal_obligation"]!="unresolved"
            or r["barriers"]!=barriers["dossier"]["barriers"]
            or any(r[x] is not False for x in ("p_equals_np_established","p_not_equals_np_established","novel_theorem_verified"))
            or digest(r["objectives"])!=digest([decompose(x) for x in ("E01","E02","E07","E12","E19")])
            or r["scope"]!="explicit GF(2) systems; exact all-RHS criterion via invertible row operations"):
        raise ValueError("invalid governance")
    expected=cases()
    if len(expected)!=len(r["records"]):
        raise ValueError("missing systems")
    for case,row in zip(expected,r["records"]):
        if row["case"]!=case:
            raise ValueError("system mismatch")
        n,rows=case["n"],case["rows"]
        c=row["criterion"]
        verify(n,rows,c,budget())
        expected_charges=charges(case)
        if [x["charge"] for x in row["decisions"]]!=expected_charges:
            raise ValueError("RHS mismatch")
        for x in row["decisions"]:
            b,p=x["charge"],x["proof"]
            verify_decision(n,rows,b,p,budget())
            if (p["decision"]=="sat")!=all(parity(h&b)==0 for h in c["checks"]):
                raise ValueError("criterion disagrees with witness")
    if r["summary"]!=summary(r["records"]):
        raise ValueError("aggregate mismatch")
    return True


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    names=("simulation","barriers","hypotheses","refinement")
    for name in names:
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--checkpoint",type=Path)
    p.add_argument("--audit",type=Path)
    a=p.parse_args(argv)
    def read(path):
        if path.stat().st_size>32_000_000:
            raise ValueError("oversized report")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        paths=tuple(getattr(a,k) for k in names)
        if a.checkpoint and a.checkpoint.resolve() in {x.resolve() for x in paths}:
            raise ValueError("cannot overwrite upstream")
        inputs=tuple(read(x) for x in paths)
        if a.audit:
            audit(*inputs,read(a.audit))
            print(json.dumps({"status":"replayed","universal_obligation":"unresolved"}))
            return 0
        r=run(*inputs,checkpoint_path=a.checkpoint)
        print(json.dumps(r,indent=2,sort_keys=True))
        return int(r["completion"]!="completed")
    except (OSError,ValueError,KeyError,TypeError,Exhausted) as e:
        p.error(str(e))


if __name__=="__main__":
    raise SystemExit(main())
