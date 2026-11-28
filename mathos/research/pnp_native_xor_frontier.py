"""Frozen comparison of native Gaussian explanations and affine projection."""
import argparse
import json
import random
import time
from pathlib import Path
from . import pnp_native_xor_conflict as native
from . import pnp_native_xor_portfolio as candidate
from . import pnp_affine_projected_portfolio as baseline
from . import pnp_affine_projected as projected
from .pnp_affine_projected_frontier import manifest as old_manifest, reference as old_reference, GROUPS as OLD_GROUPS
from .pnp_xor_frontier import encode
from .pnp_conflict_frontier import bitset20
from .pnp_adaptive_frontier import certificate_bytes
from .pnp_failure_synthesis import audit as audit_v13
from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train
from .pnp_outcome_engine import checkpoint

SCHEMA="mathos-pnp-native-xor-frontier/1"
SEED=192208
TOTAL,SECONDS=100_000,5
ARMS=("projected_portfolio","projected_full","native_full","candidate")
GROUPS=(*OLD_GROUPS,"hidden_copies","native_controls")


def hidden(n,f,seed):
    rng=random.Random(seed)
    g=[]
    for v in range(1,n+1):
        # Both coordinates are the parity of the same two latent bits.
        g.extend(encode([v,2*n+v,3*n+v],0))
        g.extend(encode([n+v,2*n+v,3*n+v],0))
    for c in f:
        g.append([(1 if x>0 else -1)*(abs(x)+rng.randrange(2)*n) for x in c])
    rng.shuffle(g)
    return g


def control(k,bad):
    e,t=4*k+1,4*k+2
    f=[[-e],[-t]]
    for i in range(k):
        a,b,c,d=range(4*i+1,4*i+5)
        f.extend(encode([a,b,c],0))
        f.extend(encode([a,b,d],0))
    # Both residual units are induced by non-affine ternary clauses.
    # Ordinary root propagation fixes c=false and d=bad, but neither
    # shared latent bit. Elimination must derive the conflict if bad.
    f.append([-3,e,t])
    f.append([4 if bad else -4,e,t])
    rng=random.Random(SEED+k)
    rng.shuffle(f)
    return f


def manifest():
    rows=list(old_manifest())
    rng=random.Random(SEED)
    for i in range(12):
        n=16 if i<6 else 18
        f=[[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
           for _ in range(round(n*(4.1+.14*(i%6))))]
        rows.append({"id":f"hidden_{i:02d}","group":"hidden_copies","kind":"hidden",
                     "n":4*n,"base_n":n,"base":f,"seed":SEED+i,
                     "clauses":hidden(n,f,SEED+i)})
    for k in (5,8,12,20):
        for bad in (False,True):
            rows.append({"id":f"native_{k}_{int(bad)}","group":"native_controls",
                         "kind":"native_control","n":4*k+2,"blocks":k,"bad":bad,
                         "clauses":control(k,bad)})
    return rows


def reference(c):
    if c["kind"]=="hidden":
        n=c["base_n"]
        if c["n"]!=4*n or c["clauses"]!=hidden(n,c["base"],c["seed"]):
            raise ValueError("invalid hidden-copy reference")
        # Every model restricts to the base; every base model extends
        # by picking the first latent bit equal to it and second zero.
        return bitset20(n,c["base"])
    if c["kind"]=="native_control":
        k,bad=c["blocks"],c["bad"]
        if k not in (5,8,12,20) or type(bad) is not bool or c["n"]!=4*k+2 or c["clauses"]!=control(k,bad):
            raise ValueError("invalid control reference")
        # All zero is a witness for SAT; UNSAT follows from equality
        # of the first pair and their opposite residual unit assignments.
        return not bad
    return old_reference(c)


def summary(rows):
    out={}
    for g in GROUPS:
        subset=[r for r in rows if r["case"]["group"]==g]
        arms={a:{"sat":0,"unsat":0,"unknown":0,"work_steps":0,
                 "elapsed_ns":0,"certificate_bytes":0} for a in ARMS}
        routes={"attempted":0,"credited":0,"xor_proof_unsat":0,"xor_events_credited":0,
                "xor_units_credited":0,"xor_conflicts_credited":0,"fallback":0}
        standalone={"xor_proof_unsat":0,"xor_events_credited":0}
        losses,gains,misses,native_only,projection_only=[],[],[],[],[]
        for row in subset:
            records=row["arms"]
            for a,r in records.items():
                s=arms[a]
                s[r["decision"]]+=1
                s["work_steps"]+=r["work_steps"]
                s["elapsed_ns"]+=row["elapsed_ns"][a]
                s["certificate_bytes"]+=certificate_bytes(r)
            r=records["candidate"]
            a=r["native"]
            routes["attempted"]+=a is not None
            routes["fallback"]+=r["fallback"] is not None
            if a and a["proof"] is not None:
                p=a["proof"]
                routes["credited"]+=1
                routes["xor_proof_unsat"]+=p["decision"]=="unsat" and p["xor_events"]>0
                for k in ("xor_events","xor_units","xor_conflicts"):
                    routes[k+"_credited"]+=p[k]
            p=records["native_full"]["proof"]
            if p:
                standalone["xor_events_credited"]+=p["xor_events"]
                standalone["xor_proof_unsat"]+=p["decision"]=="unsat" and p["xor_events"]>0
            b,p,n,h=(records[a]["decision"] for a in ARMS)
            i=row["case"]["id"]
            if b!="unknown" and h=="unknown": losses.append(i)
            if b=="unknown" and h!="unknown": gains.append(i)
            if h=="unknown": misses.append(i)
            if n!="unknown" and p=="unknown": native_only.append(i)
            if p!="unknown" and n=="unknown": projection_only.append(i)
        out[g]={"cases":len(subset),"reference_unsat":sum(not r["reference"] for r in subset),
                "arms":arms,"routes":routes,"standalone_native":standalone,"baseline_only":losses,
                "candidate_only":gains,"unresolved":misses,"native_only_vs_projection":native_only,
                "projection_only_vs_native":projection_only}
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
            if arm in ("projected_full","native_full"):
                a=(projected if arm=="projected_full" else native).attempt(n,f,TOTAL,SECONDS)
            else:
                a=(baseline if arm=="projected_portfolio" else candidate).solve(n,f,policy,plan,total=TOTAL,seconds=SECONDS)
            row["elapsed_ns"][arm]=time.perf_counter_ns()-start
            row["arms"][arm]=a
            if a["decision"]!="unknown" and (a["decision"]=="sat")!=row["reference"]:
                raise AssertionError("reference disagreement")
        r["rows"].append(row)
        checkpoint(path,r)
    r["summary"]=summary(r["rows"])
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
            if arm in ("projected_full","native_full"):
                (projected if arm=="projected_full" else native).replay(n,f,a,TOTAL)
            else:
                if (a["total_steps"],a["seconds"])!=(TOTAL,SECONDS):
                    raise ValueError("unequal budget")
                (baseline if arm=="projected_portfolio" else candidate).verify(n,f,policy,plan,a)
            if a["decision"]!="unknown" and (a["decision"]=="sat")!=row["reference"]:
                raise ValueError("incorrect decision")
            t=row["elapsed_ns"][arm]
            if type(t) is not int or t<0:
                raise ValueError("invalid runtime")
    if r["summary"]!=summary(r["rows"]):
        raise ValueError("summary mismatch")
    return True


def gate(r):
    s=r["summary"]
    if any(x["baseline_only"] for x in s.values()):
        raise ValueError("paired projected baseline loss")
    if any(s[g]["unresolved"] for g in OLD_GROUPS):
        raise ValueError("archived coverage loss")
    if s["native_controls"]["routes"]["xor_proof_unsat"]==0:
        raise ValueError("no integrated native XOR explanation proof")
    # Research gate for evidence and preservation, not a superiority
    # claim. All new misses and paired gains are reported separately.


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
