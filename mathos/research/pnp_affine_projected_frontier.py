"""Frozen matched comparison for affine-coordinate CDCL."""
import argparse
import json
import random
import time
from pathlib import Path
from . import pnp_affine_projected as projected
from . import pnp_affine_projected_portfolio as candidate
from . import pnp_xor_portfolio as baseline
from . import pnp_xor_subsystem as xor
from .pnp_xor_frontier import manifest as old_manifest, reference as old_reference, GROUPS as OLD_GROUPS, graph_case, encode
from .pnp_conflict_frontier import bitset20
from .pnp_adaptive_frontier import certificate_bytes
from .pnp_failure_synthesis import audit as audit_v13
from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train
from .pnp_outcome_engine import checkpoint

SCHEMA="mathos-pnp-affine-projected-frontier/1"
SEED=192106
TOTAL,SECONDS=100_000,5
ARMS=("xor_portfolio","xor_full","projected_full","candidate")
GROUPS=(*OLD_GROUPS,"new_graph_mixed","lifted_random")


def lifted(n,f,seed):
    # z=0, and two copies per variable constrained by 3-XOR.
    # Randomly distribute original occurrences across the copies.
    rng=random.Random(seed)
    z=n+1
    clauses=[[-z]]
    for v in range(1,n+1):
        for j in (1,2):
            clauses.extend(encode([v,z,v+j*n+1],0))
    for c in f:
        clauses.append([(1 if x>0 else -1)*(abs(x)+(j*n+1 if j else 0))
                        for x in c for j in [rng.randrange(3)]])
    rng.shuffle(clauses)
    return clauses


def manifest():
    rows=list(old_manifest())
    for k in (24,40,56):
        for bad in (False,True):
            c=graph_case(k,bad,True)
            rows.append(dict(c,group="new_graph_mixed",kind="new_graph"))
    rng=random.Random(SEED)
    for i in range(12):
        n=18 if i<6 else 20
        f=[[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
           for _ in range(round(n*(4.0+.15*(i%6))))]
        rows.append({"id":f"lifted_{i:02d}","group":"lifted_random","kind":"lifted",
                     "n":3*n+1,"base_n":n,"base":f,"lift_seed":SEED+i,
                     "clauses":lifted(n,f,SEED+i)})
    return rows


def reference(c):
    if c["kind"]=="new_graph":
        k,bad=c["vertices"],c["bad"]
        if k not in (24,40,56) or type(bad) is not bool or c!=dict(graph_case(k,bad,True),group="new_graph_mixed",kind="new_graph"):
            raise ValueError("invalid graph reference")
        return not bad
    if c["kind"]=="lifted":
        n,f=c["base_n"],c["base"]
        if c["n"]!=3*n+1 or c["clauses"]!=lifted(n,f,c["lift_seed"]):
            raise ValueError("invalid lifted reference")
        # Restriction z=0 identifies copies with base variables;
        # every base assignment extends, every lifted model restricts.
        return bitset20(n,f)
    return old_reference(c)


def summarize(rows):
    out={}
    for g in GROUPS:
        subset=[r for r in rows if r["case"]["group"]==g]
        arms={a:{"sat":0,"unsat":0,"unknown":0,"work_steps":0,
                 "elapsed_ns":0,"certificate_bytes":0} for a in ARMS}
        routes={"attempted":0,"lifted":0,"dual":0,"projected_rup":0,"exhausted":0,"fallback":0}
        losses,gains,misses,standalone,projection_gains=[],[],[],[],[]
        for row in subset:
            records=row["arms"]
            for a,r in records.items():
                s=arms[a]
                s[r["decision"]]+=1
                s["work_steps"]+=r["work_steps"]
                s["elapsed_ns"]+=row["elapsed_ns"][a]
                s["certificate_bytes"]+=certificate_bytes(r)
            r=records["candidate"]
            a=r["projected"]
            routes["attempted"]+=a is not None
            routes["fallback"]+=r["fallback"] is not None
            if a:
                routes["exhausted"]+=a["status"]=="resource_exhausted"
                if a["proof"] is not None:
                    routes[a["proof"]["kind"]]+=1
            b,x,p,h=(records[a]["decision"] for a in ARMS)
            i=row["case"]["id"]
            if b!="unknown" and h=="unknown": losses.append(i)
            if b=="unknown" and h!="unknown": gains.append(i)
            if h=="unknown": misses.append(i)
            if p!="unknown" and h=="unknown": standalone.append(i)
            if p!="unknown" and x=="unknown": projection_gains.append(i)
        out[g]={"cases":len(subset),"reference_unsat":sum(not r["reference"] for r in subset),
                "arms":arms,"routes":routes,"baseline_only":losses,"candidate_only":gains,
                "unresolved":misses,"projected_full_only":standalone,
                "projection_only_vs_xor":projection_gains}
    return out


def run(source,scheduler,failures,path):
    audit_v13(source,scheduler,failures)
    policy,plan=train(source),failures["selected_plan"]
    r={"schema":SCHEMA,"upstream":[digest(x) for x in (source,scheduler,failures)],
       "seed":SEED,"total":TOTAL,"seconds":SECONDS,"rows":[],
       "completion":"running","universal_obligation":"unresolved"}
    checkpoint(path,r)
    for i,c in enumerate(manifest()):
        n,f=c["n"],c["clauses"]
        row={"case":c,"reference":reference(c),"arms":{},"elapsed_ns":{}}
        for arm in ARMS[i%4:]+ARMS[:i%4]:
            start=time.perf_counter_ns()
            if arm in ("xor_full","projected_full"):
                engine=xor if arm=="xor_full" else projected
                a=engine.attempt(n,f,TOTAL,SECONDS)
            else:
                engine=baseline if arm=="xor_portfolio" else candidate
                a=engine.solve(n,f,policy,plan,total=TOTAL,seconds=SECONDS)
            row["elapsed_ns"][arm]=time.perf_counter_ns()-start
            row["arms"][arm]=a
            if a["decision"]!="unknown" and (a["decision"]=="sat")!=row["reference"]:
                raise AssertionError("reference disagreement")
        r["rows"].append(row)
        checkpoint(path,r)
    r["summary"]=summarize(r["rows"])
    r["completion"]="completed"
    checkpoint(path,r)
    return r


def audit(source,scheduler,failures,r):
    audit_v13(source,scheduler,failures)
    policy,plan=train(source),failures["selected_plan"]
    if (r["schema"],r["upstream"],r["seed"],r["total"],r["seconds"],
            r["completion"],r["universal_obligation"])!=(
            SCHEMA,[digest(x) for x in (source,scheduler,failures)],SEED,TOTAL,SECONDS,
            "completed","unresolved"):
        raise ValueError("report binding")
    cases=manifest()
    if len(cases)!=len(r["rows"]):
        raise ValueError("missing cases")
    for c,row in zip(cases,r["rows"]):
        n,f=c["n"],c["clauses"]
        if (row["case"]!=c or row["reference"] is not reference(c)
                or set(row["arms"])!=set(ARMS) or set(row["elapsed_ns"])!=set(ARMS)):
            raise ValueError("manifest mismatch")
        for arm,a in row["arms"].items():
            if arm in ("xor_full","projected_full"):
                (xor if arm=="xor_full" else projected).replay(n,f,a,TOTAL)
            else:
                if (a["total_steps"],a["seconds"])!=(TOTAL,SECONDS):
                    raise ValueError("unequal budget")
                (baseline if arm=="xor_portfolio" else candidate).verify(n,f,policy,plan,a)
            if a["decision"]!="unknown" and (a["decision"]=="sat")!=row["reference"]:
                raise ValueError("incorrect decision")
            t=row["elapsed_ns"][arm]
            if type(t) is not int or t<0:
                raise ValueError("invalid runtime")
    if r["summary"]!=summarize(r["rows"]):
        raise ValueError("summary mismatch")
    return True


def gate(r):
    s=r["summary"]
    if any(x["baseline_only"] for x in s.values()):
        raise ValueError("paired XOR baseline loss")
    if any(s[g]["unresolved"] for g in OLD_GROUPS):
        raise ValueError("archived coverage loss")
    if not {"graph_32_0_1","graph_48_0_1","graph_64_0_1"}<=set(s["graph_mixed"]["projection_only_vs_xor"]):
        raise ValueError("three standalone affine mixed SAT misses not recovered")
    if s["lifted_random"]["routes"]["projected_rup"]==0:
        raise ValueError("no integrated projected UNSAT proof credited")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("benchmark","scheduler","failures"):
        p.add_argument("--"+name,type=Path,required=True)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checkpoint",type=Path)
    mode.add_argument("--audit",type=Path)
    p.add_argument("--gate",action="store_true")
    a=p.parse_args()
    paths=[a.benchmark,a.scheduler,a.failures]
    def read(p):
        if p.stat().st_size>128_000_000:
            raise ValueError("evidence size limit")
        return json.loads(p.read_text(encoding="utf-8"))
    upstream=[read(p) for p in paths]
    if a.checkpoint:
        if a.checkpoint.resolve() in {p.resolve() for p in paths}:
            raise ValueError("cannot overwrite upstream")
        r=run(*upstream,a.checkpoint)
    else:
        r=read(a.audit)
    audit(*upstream,r)
    print(json.dumps(r["summary"],indent=2,sort_keys=True))
    if a.gate:
        gate(r)


if __name__=="__main__":
    main()
