"""v17.1 frozen-library factorial ablation and independent certificate audit."""
import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
from time import perf_counter, process_time

from .pnp_library_frontier import audit as audit_v17, suite, case_key
from .pnp_abstraction_frontier import bytesize
from .pnp_evidence_benchmark import digest
from .pnp_proof_library import Index, reuse
from .pnp_structural_kernel import Budget, Exhausted

NEW_SEED = 17103
STEPS = 4_000_000
ARMS = tuple((library, sub, comp) for library in ("original","expanded")
             for sub in (False,True) for comp in (False,True))


def name(arm):
    l,s,c = arm
    return l + ("_sub" if s else "_exact") + ("_compose" if c else "_core")


def independent_replay(n, formula, proof):
    """Separate checker: simplify residual clauses under unit assumptions.
    No MathOS normalization, RUP implementation, template or search calls.
    """
    def parse(c):
        if any(type(x) is not int or not 0<abs(x)<=n for x in c):
            raise ValueError("invalid literal")
        return frozenset(c)
    if type(n) is not int or not 0<=n<=512 or len(formula)>20000 or len(proof)>4096:
        raise ValueError("invalid dimensions")
    known = [parse(c) for c in formula]
    known = [c for c in known if not any(-x in c for x in c)]
    for raw in proof:
        c = parse(raw)
        if tuple(sorted(c)) != tuple(raw) or any(-x in c for x in c):
            raise ValueError("invalid derived clause")
        residual = known + [frozenset((-x,)) for x in c]
        while frozenset() not in residual:
            unit = next((next(iter(a)) for a in residual if len(a)==1),None)
            if unit is None:
                raise ValueError("independent RUP rejected addition")
            residual = [a-{-unit} for a in residual if unit not in a]
        known.append(c)
    if frozenset() not in known:
        raise ValueError("missing contradiction")
    return True


def oracle(n, formula):
    if not 0<=n<=14:
        raise ValueError("oracle size cap")
    for bits in product((False,True),repeat=n):
        if all(any(bits[abs(x)-1] == (x>0) for x in c) for c in formula):
            return True
    return False


def evaluate(case, indexes):
    n,f=case["n"],case["clauses"]
    outcomes={}
    # Rotate deterministic arm order by case hash, independent of labels.
    offset=int(case_key(case)[:8],16)%len(ARMS)
    for arm in ARMS[offset:]+ARMS[:offset]:
        library,sub,comp=arm
        b=Budget(seconds=15,max_steps=STEPS,max_cells=100000)
        start,cpu=perf_counter(),process_time()
        result=reuse(n,f,indexes[library],b,subsumption=sub,compose=comp,shared_replay=True)
        result.update(search_replay_work=b.steps,wall_seconds=perf_counter()-start,
                      cpu_seconds=process_time()-cpu)
        if result["status"]=="verified":
            start=perf_counter()
            independent_replay(n,f,result["proof"])
            result.update(independent_check_seconds=perf_counter()-start,
                          proof_bytes=bytesize(result["proof"]),
                          recipe_bytes=bytesize(result["transfers"]))
        outcomes[name(arm)]=result
    sat=oracle(n,f)
    if sat and any(r["status"]=="verified" for r in outcomes.values()):
        raise AssertionError("false refutation")
    return {"case":case,"reference_sat":sat,"arms":outcomes}


def summary(rows):
    out={"cases":len(rows),"unsat":sum(not r["reference_sat"] for r in rows),"arms":{}}
    for arm in ARMS:
        k=name(arm)
        results=[r["arms"][k] for r in rows]
        verified=[r for r in results if r["status"]=="verified"]
        out["arms"][k]={"verified":len(verified),"statuses":dict(Counter(r["status"] for r in results)),
                         "work":sum(r["search_replay_work"] for r in results),
                         "wall_seconds":sum(r["wall_seconds"] for r in results),
                         "cpu_seconds":sum(r["cpu_seconds"] for r in results),
                         "proof_bytes":sum(r["proof_bytes"] for r in verified),
                         "recipe_bytes":sum(r["recipe_bytes"] for r in verified),
                         "independent_check_seconds":sum(r["independent_check_seconds"] for r in verified)}
    # Matched-pair contrasts, holding two factors constant.
    contrasts={}
    for a in ARMS:
        for axis in range(3):
            b=list(a)
            if axis==0 and a[0]=="original":
                b[0]="expanded"
            elif axis>0 and not a[axis]:
                b[axis]=True
            else:
                continue
            ka,kb=name(a),name(tuple(b))
            pairs=[(r["arms"][ka]["status"]=="verified",r["arms"][kb]["status"]=="verified") for r in rows]
            contrasts[ka+" -> "+kb]={"gain":sum(not x and y for x,y in pairs),
                                      "loss":sum(x and not y for x,y in pairs),
                                      "both":sum(x and y for x,y in pairs)}
    out["contrasts"]=contrasts
    return out


def run(source,scheduler,failures,v17):
    audit_v17(source,scheduler,failures,v17)
    if failures["seed"]==NEW_SEED:
        raise ValueError("upstream seed overlap")
    indexes={"original":Index(v17["original_library"]),"expanded":Index(v17["library"])}
    frozen={k:digest(v.templates) for k,v in indexes.items()}
    retrospective=[r["case"] for r in v17["heldout"]]
    fresh=suite(NEW_SEED,24)
    seen={case_key(r["case"]) for r in v17["training"]+v17["discovery"]+v17["heldout"]+v17["retrospective"]}
    seen.update(case_key(r["case"]) for r in failures["training"]+failures["evaluation"])
    seen.update(case_key(r["case"]) for r in source["rows"])
    keys={case_key(c) for c in fresh}
    if len(keys)!=len(fresh) or keys & seen:
        raise ValueError("duplicate input")
    rows=[evaluate(c,indexes) for c in fresh]
    historical=[evaluate(c,indexes) for c in retrospective]
    if frozen!={k:digest(v.templates) for k,v in indexes.items()}:
        raise AssertionError("library mutated")
    return {"schema":"mathos-pnp-library-ablation/1","seed":NEW_SEED,
            "upstream":[digest(x) for x in (source,scheduler,failures,v17)],
            "libraries":frozen,"step_cap":STEPS,"fresh":rows,"retrospective":historical,
            "summary":{"fresh":summary(rows),"random2":summary([r for r in rows if r["case"]["family"]=="random2"]),
                       "random3":summary([r for r in rows if r["case"]["family"]=="random3"]),
                       "retrospective":summary(historical)},
            "universal_obligation":"unresolved","novel_theorem_verified":False,
            "p_equals_np_established":False,"p_not_equals_np_established":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("benchmark","scheduler","failures","v17","checkpoint"):
        p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args()
    paths=(a.benchmark,a.scheduler,a.failures,a.v17)
    if a.checkpoint.resolve() in {x.resolve() for x in paths}:
        p.error("cannot overwrite input")
    result=run(*(json.loads(x.read_text()) for x in paths))
    a.checkpoint.write_text(json.dumps(result,indent=2,sort_keys=True))
    print(json.dumps(result["summary"],indent=2))


if __name__=="__main__":
    main()
