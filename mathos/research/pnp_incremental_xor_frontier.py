"""Opt-in incremental native XOR ablation on the unchanged 191-case manifest."""
import argparse
import json
import time
from pathlib import Path
from . import pnp_native_xor_conflict as native
from . import pnp_native_xor_portfolio as portfolio
from . import pnp_incremental_xor_state as inc
from .pnp_native_xor_frontier import manifest,reference,GROUPS
from .pnp_adaptive_frontier import certificate_bytes
from .pnp_failure_synthesis import audit as audit_v13
from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train
from .pnp_outcome_engine import checkpoint

SCHEMA="mathos-pnp-incremental-xor-frontier/1"
TOTAL,SECONDS=100_000,5
ARMS=("native_full","incremental_raw","incremental_pruned","native_portfolio","incremental_portfolio")


def summary(rows):
    out={}
    for g in GROUPS:
        selected=[r for r in rows if r["case"]["group"]==g]
        arms={a:{"sat":0,"unsat":0,"unknown":0,"work_steps":0,"elapsed_ns":0,
                 "certificate_bytes":0} for a in ARMS}
        losses,gains,misses=[],[],[]
        raw_only,pruned_only,native_only,incremental_only=[],[],[],[]
        pruning=[]
        for row in selected:
            records=row["arms"]
            for a,r in records.items():
                s=arms[a]
                s[r["decision"]]+=1
                s["work_steps"]+=r["work_steps"]
                s["elapsed_ns"]+=row["elapsed_ns"][a]
                s["certificate_bytes"]+=certificate_bytes(r)
            n,r,p,b,h=(records[a]["decision"] for a in ARMS)
            i=row["case"]["id"]
            if b!="unknown" and h=="unknown": losses.append(i)
            if b=="unknown" and h!="unknown": gains.append(i)
            if h=="unknown": misses.append(i)
            if r!="unknown" and p=="unknown": raw_only.append(i)
            if r=="unknown" and p!="unknown": pruned_only.append(i)
            if n!="unknown" and r=="unknown": native_only.append(i)
            if n=="unknown" and r!="unknown": incremental_only.append(i)
            if r==p=="unsat":
                a,c=(records[k]["proof"]["certificate"] for k in ("incremental_raw","incremental_pruned"))
                pruning.append({"id":i,"raw_rows":len(a["rows"]),"pruned_rows":len(c["rows"]),
                    "raw_bytes":certificate_bytes(records["incremental_raw"]),
                    "pruned_bytes":certificate_bytes(records["incremental_pruned"])})
        out[g]={"cases":len(selected),"reference_unsat":sum(not r["reference"] for r in selected),
                "arms":arms,"baseline_only":losses,"candidate_only":gains,"unresolved":misses,
                "raw_only":raw_only,"pruned_only":pruned_only,
                "native_only_vs_raw":native_only,"raw_only_vs_native":incremental_only,
                "paired_pruning":pruning}
    return out


def run(source,scheduler,failures,path):
    audit_v13(source,scheduler,failures)
    policy,plan=train(source),failures["selected_plan"]
    r={"schema":SCHEMA,"upstream":[digest(x) for x in (source,scheduler,failures)],
       "total":TOTAL,"seconds":SECONDS,"rows":[],"completion":"running",
       "universal_obligation":"unresolved"}
    checkpoint(path,r)
    for i,c in enumerate(manifest()):
        n,f=c["n"],c["clauses"]
        row={"case":c,"reference":reference(c),"arms":{},"elapsed_ns":{}}
        for arm in ARMS[i%5:]+ARMS[:i%5]:
            start=time.perf_counter_ns()
            if arm=="native_full":
                a=native.attempt(n,f,TOTAL,SECONDS)
            elif arm in ("incremental_raw","incremental_pruned"):
                a=inc.attempt(n,f,TOTAL,SECONDS,prune=arm=="incremental_pruned")
            else:
                a=portfolio.solve(n,f,policy,plan,total=TOTAL,seconds=SECONDS,
                    attempt_fn=inc.attempt if arm=="incremental_portfolio" else None)
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
    if (r["schema"],r["upstream"],r["total"],r["seconds"],r["completion"],
            r["universal_obligation"])!=(SCHEMA,[digest(x) for x in (source,scheduler,failures)],
            TOTAL,SECONDS,"completed","unresolved"):
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
            if arm in ARMS[:3]:
                native.replay(n,f,a,TOTAL)
            else:
                if (a["total_steps"],a["seconds"])!=(TOTAL,SECONDS):
                    raise ValueError("unequal budget")
                portfolio.verify(n,f,policy,plan,a)
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
        raise ValueError("paired native portfolio loss")
    if not any(p["pruned_rows"]<p["raw_rows"] for x in s.values() for p in x["paired_pruning"]):
        raise ValueError("no paired strict source-row pruning")
    # A diagnostic gate, not a claim of dominance or a replacement
    # for the parent native-XOR evidence gate.


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
