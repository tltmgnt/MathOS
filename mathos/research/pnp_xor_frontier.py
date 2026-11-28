"""Fixed public partial-XOR evaluation, including mixed and signed parity controls."""
import argparse
import json
import random
import time
from itertools import product
from pathlib import Path
from . import pnp_xor_subsystem as xor
from . import pnp_xor_portfolio as candidate
from . import pnp_conflict_portfolio as baseline
from .pnp_conflict_frontier import manifest as old_manifest, reference as old_reference, bitset20, GROUPS as OLD_GROUPS
from .pnp_adaptive_frontier import certificate_bytes
from .pnp_failure_synthesis import audit as audit_v13
from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train
from .pnp_outcome_engine import checkpoint

SCHEMA="mathos-pnp-xor-frontier/1"
SEED=192004
TOTAL,SECONDS=100_000,5
ARMS=("conflict","xor_full","candidate")
GROUPS=(*OLD_GROUPS,"graph_parity","graph_mixed","small_mixed")


def encode(vs,rhs):
    return [[-v if bit else v for v,bit in zip(vs,bits)]
            for bits in product((0,1),repeat=len(vs)) if sum(bits)%2!=rhs]


def graph_case(k,bad,mixed):
    # Connected cubic graph: cycle plus antipodal perfect matching.
    # Variables label edges; equations are XOR of incident edge values.
    edges=[(i,(i+1)%k) for i in range(k)]+[(i,i+k//2) for i in range(k//2)]
    scopes=[[] for _ in range(k)]
    for v,(a,b) in enumerate(edges,1):
        scopes[a].append(v)
        scopes[b].append(v)
    n=len(edges)
    rng=random.Random(SEED+10*k+int(mixed))
    # Signed witness, not all-zero in the original variable coordinates.
    witness=[rng.randrange(2) for _ in range(n)]
    # Make at least one negative literal in each added non-affine clause.
    f=[]
    for i,vs in enumerate(scopes):
        rhs=sum(witness[v-1] for v in vs)%2
        f.extend(encode(vs,rhs ^ int(bad and i==k-1)))
    if mixed:
        used={tuple(sorted(vs)) for vs in scopes}
        for _ in range(k//2):
            vs=sorted(rng.sample(range(1,n+1),3))
            while tuple(vs) in used:
                vs=sorted(rng.sample(range(1,n+1),3))
            used.add(tuple(vs))
            c=[v if rng.randrange(2) else -v for v in vs]
            # Make the added clause true on the zero-free Gaussian model
            # only in the zero coordinate control; here a planted signed
            # witness is used, not supplied to the solver.
            if not any(bool(witness[abs(x)-1])==(x>0) for x in c):
                c[0]=-c[0]
            f.append(c)
    rng.shuffle(f)
    return {"id":f"graph_{k}_{int(bad)}_{int(mixed)}",
            "group":"graph_mixed" if mixed else "graph_parity",
            "kind":"graph","n":n,"vertices":k,"bad":bad,"mixed":mixed,
            "clauses":f}


def manifest():
    rows=list(old_manifest())
    for k in (20,32,48,64):
        for bad in (False,True):
            for mixed in (False,True):
                rows.append(graph_case(k,bad,mixed))
    rng=random.Random(SEED)
    for i in range(8):
        n=12
        f=[]
        for _ in range(5):
            f.extend(encode(sorted(rng.sample(range(1,n+1),3)),rng.randrange(2)))
        f.extend([[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
                  for _ in range(18)])
        rows.append({"id":f"xor_mixed_{i}","group":"small_mixed",
                     "kind":"bitset20","n":n,"clauses":f})
    return rows


def reference(c):
    if c["kind"]=="graph":
        k,bad,mixed=c["vertices"],c["bad"],c["mixed"]
        if k not in (20,32,48,64) or type(bad) is not bool or type(mixed) is not bool or c!=graph_case(k,bad,mixed):
            raise ValueError("invalid graph reference")
        # Each edge occurs twice in the XOR of vertex equations; bad
        # flips exactly one RHS. Otherwise the constructed signed witness
        # also satisfies every appended clause.
        return not bad
    return old_reference(c)


def summarize(rows):
    out={}
    for g in GROUPS:
        selected=[r for r in rows if r["case"]["group"]==g]
        arms={a:{"sat":0,"unsat":0,"unknown":0,"work_steps":0,
                 "elapsed_ns":0,"certificate_bytes":0} for a in ARMS}
        routes={"attempted":0,"credited":0,"fallback_attempted":0,"exhausted":0}
        losses,gains,misses,standalone=[],[],[],[]
        for row in selected:
            records=row["arms"]
            for a,r in records.items():
                x=arms[a]
                x[r["decision"]]+=1
                x["work_steps"]+=r["work_steps"]
                x["elapsed_ns"]+=row["elapsed_ns"][a]
                x["certificate_bytes"]+=certificate_bytes(r)
            r=records["candidate"]
            a=r["xor"]
            routes["attempted"]+=a is not None
            routes["credited"]+=a is not None and a["decision"]!="unknown"
            routes["exhausted"]+=a is not None and a["status"]=="resource_exhausted"
            routes["fallback_attempted"]+=r["fallback"] is not None
            b,h,s=(records[x]["decision"] for x in ("conflict","candidate","xor_full"))
            i=row["case"]["id"]
            if b!="unknown" and h=="unknown": losses.append(i)
            if b=="unknown" and h!="unknown": gains.append(i)
            if h=="unknown": misses.append(i)
            if s!="unknown" and h=="unknown": standalone.append(i)
        out[g]={"cases":len(selected),"reference_unsat":sum(not r["reference"] for r in selected),
                "arms":arms,"candidate_xor":routes,"baseline_only":losses,
                "candidate_only":gains,"unresolved":misses,"xor_full_only":standalone}
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
        for arm in ARMS[i%3:]+ARMS[:i%3]:
            start=time.perf_counter_ns()
            if arm=="xor_full":
                a=xor.attempt(n,f,TOTAL,SECONDS)
            else:
                engine=baseline if arm=="conflict" else candidate
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
            if arm=="xor_full":
                xor.replay(n,f,a,TOTAL)
            else:
                if (a["total_steps"],a["seconds"])!=(TOTAL,SECONDS):
                    raise ValueError("unequal budget")
                (baseline if arm=="conflict" else candidate).verify(n,f,policy,plan,a)
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
        raise ValueError("paired conflict baseline loss")
    if any(s[g]["unresolved"] for g in OLD_GROUPS):
        raise ValueError("archived coverage loss")
    if not any(s[g]["candidate_only"] for g in ("graph_parity","graph_mixed")):
        raise ValueError("no strict algebraic coverage gain")


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
