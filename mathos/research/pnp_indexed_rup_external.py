"""Indexed RUP cost ablation on frozen external cases and new UNSAT controls."""
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from . import pnp_external_satlib as corpus
from . import pnp_adaptive_decision as v16
from . import pnp_conflict_learning as cdcl
from . import pnp_affine_projected_portfolio as projected
from . import pnp_native_xor_portfolio as native
from . import pnp_incremental_xor_state as incremental
from . import pnp_external_satlib_reference as refs
from . import pnp_indexed_rup as indexed
from . import pnp_indexed_rup_portfolio as candidate
from . import pnp_coloring_portfolio as baseline
from .pnp_coloring_external import manifest as old_manifest
from .pnp_adaptive_frontier import certificate_bytes
from .pnp_failure_synthesis import audit as audit_v13
from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train
from .pnp_outcome_engine import checkpoint
from .pnp_structural_kernel import Budget, Exhausted

SCHEMA="mathos-pnp-indexed-rup-external/1"
ARMS=("baseline","cdcl","indexed_full","candidate","glucose4")
TOTAL,SECONDS=100_000,5
REPLAY_STEPS,REPLAY_SECONDS=20_000_000,15
MAX_REPORT_BYTES=128_000_000


def manifest():
    m=old_manifest()
    extra=json.loads(Path(__file__).with_name("pnp_indexed_rup_heldout.json").read_text(encoding="utf-8"))
    return dict(m,cases=m["cases"]+extra,indexed_selection="next eight uuf50 blob IDs after original eight")


def worker():
    inp=json.load(sys.stdin)
    n,f,arm=inp["n"],inp["clauses"],inp["arm"]
    policy,plan=inp["policy"],inp["plan"]
    start=time.perf_counter_ns()
    if arm=="glucose4":
        a=corpus.glucose(n,f)
    elif arm=="cdcl":
        a=cdcl.attempt(n,f,TOTAL,SECONDS)
    elif arm=="indexed_full":
        a=indexed.attempt(n,f,TOTAL,SECONDS)
    elif arm=="baseline":
        a=baseline.solve(n,f,policy,plan,total=TOTAL,seconds=SECONDS)
    elif arm=="candidate":
        a=candidate.solve(n,f,policy,plan,total=TOTAL,seconds=SECONDS)
    elif arm=="incremental":
        a=native.solve(n,f,policy,plan,total=TOTAL,seconds=SECONDS,attempt_fn=incremental.attempt)
    else:
        a={"v16":v16,"projected":projected,"native":native}[arm].solve(
            n,f,policy,plan,total=TOTAL,seconds=SECONDS)
    print(json.dumps({"payload":a,"solver_ns":time.perf_counter_ns()-start},
                     separators=(",",":")))


def replay(n,f,arm,p,policy,plan):
    if arm=="glucose4":
        return corpus.verify_external(n,f,p,Budget(seconds=REPLAY_SECONDS,
                   max_steps=REPLAY_STEPS,max_cells=200_000))
    if arm=="cdcl":
        return cdcl.replay(n,f,p,TOTAL)
    if arm=="indexed_full":
        return indexed.replay(n,f,p,TOTAL)
    if (p["total_steps"],p["seconds"])!=(TOTAL,SECONDS):
        raise ValueError("budget mismatch")
    if arm=="v16":
        return v16.verify_report(n,f,policy,plan,p)
    return {"projected":projected,"native":native,"incremental":native,"candidate":candidate,"baseline":baseline}[arm].verify(n,f,policy,plan,p)


def measure(n,f,arm,policy,plan):
    data=json.dumps({"n":n,"clauses":f,"arm":arm,"policy":policy,"plan":plan})
    start=time.perf_counter_ns()
    try:
        proc=subprocess.run([sys.executable,"-m",__name__ if __name__!="__main__" else
                             "mathos.research.pnp_indexed_rup_external","--worker"],
                            input=data,text=True,capture_output=True,timeout=SECONDS)
    except subprocess.TimeoutExpired:
        return {"status":"wall_timeout","decision":"unknown","claimed":"unknown",
                "payload":None,"wall_ns":time.perf_counter_ns()-start,
                "solver_ns":None,"replay_ns":None}
    wall=time.perf_counter_ns()-start
    if proc.returncode:
        raise RuntimeError("solver worker failed: "+proc.stderr[-3000:])
    if len(proc.stdout)>MAX_REPORT_BYTES:
        raise RuntimeError("worker output cap")
    obj=json.loads(proc.stdout)
    p=obj["payload"]
    claim=p["decision"]
    start=time.perf_counter_ns()
    try:
        replay(n,f,arm,p,policy,plan)
        status="replayed" if claim!="unknown" else "solver_unknown"
        decision=claim
    except Exhausted:
        status,decision="replay_exhausted","unknown"
    return {"status":status,"decision":decision,"claimed":claim,"payload":p,
            "wall_ns":wall,"solver_ns":obj["solver_ns"],
            "replay_ns":time.perf_counter_ns()-start}


def summary(rows):
    out={}
    for row in rows:
        c=row["case"]
        s=out.setdefault(c["group"],{"selected":0,"parse_rejected":0,"arms":{
           a:{"sat":0,"unsat":0,"unknown":0,"claimed_sat":0,"claimed_unsat":0,
              "wall_timeout":0,"replay_exhausted":0,"wall_ns":0,
              "solver_ns":0,"replay_ns":0,"certificate_bytes":0,
              "work_steps":None if a=="glucose4" else 0} for a in ARMS}})
        s["selected"]+=1
        s.setdefault("independent_reference",0)
        if row.get("reference") and row["reference"]["decision"] is not None:
            s["independent_reference"]+=1
        if row["parse_error"] is not None:
            s["parse_rejected"]+=1
            continue
        s.setdefault("diagnostic",[])
        if row.get("diagnostic") is not None:
            d=row["diagnostic"]
            s["diagnostic"].append(dict(path=c["path"],search=d["search_steps"],slow=d["slow_steps"],fast=d["fast_steps"],proof_found=d["proof"] is not None))
        s.setdefault("paired_losses",[])
        s.setdefault("paired_gains",[])
        base,can=(row["arms"][a]["decision"] for a in ("baseline","candidate"))
        if base!="unknown" and can=="unknown": s["paired_losses"].append(c["path"])
        if base=="unknown" and can!="unknown": s["paired_gains"].append(c["path"])
        for arm,r in row["arms"].items():
            a=s["arms"][arm]
            a[r["decision"]]+=1
            for d in ("sat","unsat"):
                a["claimed_"+d]+=r["claimed"]==d
            for k in ("wall_timeout","replay_exhausted"):
                a[k]+=r["status"]==k
            for k in ("wall_ns","solver_ns","replay_ns"):
                a[k]+=r[k] or 0
            if r["payload"] is not None:
                a["certificate_bytes"]+=certificate_bytes(r["payload"])
                if arm!="glucose4":
                    a["work_steps"]+=r["payload"]["work_steps"]
    return out


def run(root,source,scheduler,failures,path):
    import pysat
    audit_v13(source,scheduler,failures)
    policy,plan=train(source),failures["selected_plan"]
    m=manifest()
    r={"schema":SCHEMA,"manifest":m,"upstream":[digest(x) for x in (source,scheduler,failures)],
       "total":TOTAL,"seconds":SECONDS,"replay_steps":REPLAY_STEPS,
       "replay_seconds":REPLAY_SECONDS,"environment":{"python":sys.version,
          "platform":platform.platform(),"python_sat":pysat.__version__},
       "rows":[],"completion":"running","universal_obligation":"unresolved"}
    checkpoint(path,r)
    for i,c in enumerate(m["cases"]):
        data=corpus.read_case(root,c) # mismatch is a hard failure
        row={"case":c,"parse_error":None,"n":None,"m":None,"reference":None,"arms":{},"diagnostic":None}
        try:
            n,f=corpus.parse_dimacs(data)
        except (ValueError,Exhausted) as e:
            row["parse_error"]=str(e)
        else:
            ref=refs.reference(c["group"],n,f)
            if ref["decision"] not in (None,c["expected"]):
                raise ValueError("independent reference disagreement")
            row.update(n=n,m=len(f),reference=ref)
            for arm in ARMS[i%len(ARMS):]+ARMS[:i%len(ARMS)]:
                a=measure(n,f,arm,policy,plan)
                if a["claimed"] not in ("unknown",c["expected"]):
                    raise AssertionError("external reference disagreement: "+c["path"]+" "+arm)
                row["arms"][arm]=a
            if c["group"] in ("uuf50","uuf50_heldout"):
                row["diagnostic"]=indexed.profile(n,f)
        r["rows"].append(row)
        checkpoint(path,r)
    r["summary"]=summary(r["rows"])
    r["completion"]="completed"
    checkpoint(path,r)
    return r


def audit(root,source,scheduler,failures,r):
    audit_v13(source,scheduler,failures)
    policy,plan=train(source),failures["selected_plan"]
    m=manifest()
    if (r["schema"],r["manifest"],r["upstream"],r["total"],r["seconds"],
        r["replay_steps"],r["replay_seconds"],r["completion"],r["universal_obligation"])!=(
        SCHEMA,m,[digest(x) for x in (source,scheduler,failures)],TOTAL,SECONDS,
        REPLAY_STEPS,REPLAY_SECONDS,"completed","unresolved"):
        raise ValueError("report binding")
    if len(r["rows"])!=len(m["cases"]):
        raise ValueError("missing external cases")
    for c,row in zip(m["cases"],r["rows"]):
        if row["case"]!=c:
            raise ValueError("manifest mismatch")
        data=corpus.read_case(root,c)
        try:
            n,f=corpus.parse_dimacs(data)
        except (ValueError,Exhausted) as e:
            if row["parse_error"]!=str(e) or row["arms"] or row["n"] is not None or row["m"] is not None or row["reference"] is not None:
                raise ValueError("parse rejection mismatch")
            continue
        if (row["parse_error"] is not None or row["n"]!=n or row["m"]!=len(f)
                or set(row["arms"])!=set(ARMS)):
            raise ValueError("external case mismatch")
        ref=refs.reference(c["group"],n,f)
        if row["reference"]!=ref or ref["decision"] not in (None,c["expected"]):
            raise ValueError("independent reference mismatch")
        if c["group"] in ("uuf50","uuf50_heldout"):
            d=row["diagnostic"]
            indexed.audit_profile(n,f,d,TOTAL)
            if d["proof"] is not None and d["proof"]["decision"]!=c["expected"]:
                raise ValueError("diagnostic reference disagreement")
        elif row["diagnostic"] is not None:
            raise ValueError("unexpected diagnostic")
        for arm,a in row["arms"].items():
            p,status=a["payload"],a["status"]
            if a["claimed"] not in ("unknown",c["expected"]) or a["decision"] not in ("unknown",c["expected"]):
                raise ValueError("external reference disagreement")
            if type(a["wall_ns"]) is not int or a["wall_ns"]<0:
                raise ValueError("invalid wall observation")
            if status=="wall_timeout":
                if (p is not None or a["claimed"]!="unknown" or a["decision"]!="unknown"
                        or a["solver_ns"] is not None or a["replay_ns"] is not None):
                    raise ValueError("invalid timeout")
                continue
            for k in ("solver_ns","replay_ns"):
                if type(a[k]) is not int or a[k]<0:
                    raise ValueError("invalid timing")
            if p is None or p["decision"]!=a["claimed"]:
                raise ValueError("claim mismatch")
            if status=="replay_exhausted":
                if a["decision"]!="unknown":
                    raise ValueError("uncredited proof")
                # Replay exhaustion is observational, not a math claim.
                # Try again; a successful later replay does not alter
                # the original run's credited coverage.
                try:
                    replay(n,f,arm,p,policy,plan)
                except Exhausted:
                    pass
            elif status in ("replayed","solver_unknown"):
                if a["decision"]!=a["claimed"] or (status=="replayed")!=(a["decision"]!="unknown"):
                    raise ValueError("decision accounting")
                replay(n,f,arm,p,policy,plan)
            else:
                raise ValueError("unknown status")
    if r["summary"]!=summary(r["rows"]):
        raise ValueError("summary mismatch")
    return True


def gate(r):
    if sum(x["selected"] for x in r["summary"].values())!=48:
        raise ValueError("external denominator changed")
    if sum(x["selected"]-x["parse_rejected"] for x in r["summary"].values())==0:
        raise ValueError("no parsable external instances")
    if any(x.get("paired_losses") for x in r["summary"].values()):
        raise ValueError("paired coloring baseline loss")
    if not r["summary"]["uuf50"].get("paired_gains"):
        raise ValueError("no development UNSAT coverage gain")
    # Held-out misses are reported, not replaced or retuned.


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--worker",action="store_true")
    p.add_argument("--corpus",type=Path)
    for name in ("benchmark","scheduler","failures"):
        p.add_argument("--"+name,type=Path)
    mode=p.add_mutually_exclusive_group()
    mode.add_argument("--checkpoint",type=Path)
    mode.add_argument("--audit",type=Path)
    p.add_argument("--gate",action="store_true")
    a=p.parse_args()
    if a.worker:
        worker()
        return
    if not all((a.corpus,a.benchmark,a.scheduler,a.failures,a.checkpoint or a.audit)):
        p.error("corpus, three upstream files and checkpoint or audit required")
    paths=[a.benchmark,a.scheduler,a.failures]
    def read(p):
        if p.stat().st_size>MAX_REPORT_BYTES:
            raise ValueError("report size cap")
        return json.loads(p.read_text(encoding="utf-8"))
    upstream=[read(p) for p in paths]
    if a.checkpoint:
        if a.checkpoint.resolve() in {p.resolve() for p in paths}:
            raise ValueError("cannot overwrite upstream")
        r=run(a.corpus,*upstream,a.checkpoint)
    else:
        r=read(a.audit)
    audit(a.corpus,*upstream,r)
    print(json.dumps(r["summary"],indent=2,sort_keys=True))
    if a.gate:
        gate(r)


if __name__=="__main__":
    main()
