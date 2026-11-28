"""Equal-envelope development comparison. Public synthetic, not blinded holdout."""
import argparse
import json
import os
import resource
import signal
import subprocess
import sys
import time
from itertools import product
from pathlib import Path

from .pnp_structural_kernel import Budget, Exhausted
from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train, execute, replay
from .pnp_certified_learning import solve as hybrid, verify_hybrid
from .pnp_adaptive_decision import solve as adaptive, verify_report
from .pnp_library_frontier import audit as audit_library, baseline, suite, case_key
from .pnp_proof_abstraction import verify_embedding
from .pnp_proof_library import Index, reuse, reconstruct, verify_certificate
from .pnp_unified_discovery_v18 import solve, verify, features

TOTAL, SECONDS, WALL, MEMORY = 100_000, 5, 10, 512 * 1024 * 1024
ARMS = ("v12", "v14", "v15+v12", "v16", "v17+v12", "v18", "v18-no-retrieval")
SEED = 18028


def audit_budget():
    return Budget(seconds=10, max_steps=4_000_000, max_cells=200_000)


def reference(c):
    n, f = c["n"], c["clauses"]
    if c["family"] == "chain":
        # Explicit indexed family; independent linear endpoint reasoning.
        expected = [[1]] + [[-i, i+1] for i in range(1, n)]
        if f[:-1] != expected or f[-1] not in ([n], [-n]):
            raise ValueError("invalid chain")
        return f[-1] == [n]
    if n > 16:
        raise ValueError("reference bound")
    return any(all(any(a[abs(x)-1] == (x > 0) for x in q) for q in f)
               for a in product((False, True), repeat=n))


def cases(source, library_report):
    forbidden = {case_key(x["case"]) for x in source["rows"]}
    for group in ("training", "retrospective", "discovery", "heldout"):
        forbidden.update(case_key(x["case"]) for x in library_report[group])
    fresh = suite(SEED, 8)
    keys = [case_key(c) for c in fresh]
    if len(set(keys)) != len(keys) or set(keys) & forbidden:
        raise ValueError("syntactic development overlap")
    for n in (20, 40, 80):
        for sign in (-1, 1):
            fresh.append({"id": "chain_%d_%s" % (n, "negative" if sign<0 else "positive"),
                          "family": "chain", "n": n,
                          "clauses": [[1]] + [[-i, i+1] for i in range(1, n)] + [[sign*n]]})
    return fresh


def retrieval_arm(n, f, policy, old, lib, arm):
    # Fixed 25% probe; remaining cooperative quota goes to v12.
    q = TOTAL // 4
    start = time.monotonic()
    b = Budget(seconds=SECONDS/4, max_steps=q)
    if arm == "v15+v12":
        r = baseline({"n":n, "clauses":f}, old, b)
        if r["status"] == "verified":
            verify_embedding(n,f,old[r["record"]],r["embedding"],audit_budget())
    else:
        r = reuse(n,f,Index(lib),b)
        if r["status"] == "verified":
            p = reconstruct(n,f,Index(lib),r["transfers"],audit_budget())
            if digest(p) != digest(r["proof"]):
                raise ValueError("retrieval reconstruction mismatch")
            verify_certificate(n,f,p,audit_budget())
    work = b.steps
    fallback = None
    decision = "unsat" if r["status"] == "verified" else "unknown"
    left = SECONDS - (time.monotonic() - start)
    if decision == "unknown" and left > 0 and work < TOTAL:
        fallback = execute(n,f,policy,"learned",TOTAL-work,left)
        replay(n,f,policy,TOTAL-work,fallback)
        decision = fallback["decision"]
    return {"decision":decision,"work_steps":work+(fallback["work_steps"] if fallback else 0),
            "retrieval_work":work,"retrieval":r,"fallback":fallback}


def run_arm(req):
    arm,c,policy,plan,old,lib = (req[k] for k in ("arm","case","policy","plan","old","library"))
    n,f = c["n"],c["clauses"]
    if arm == "v12":
        r=execute(n,f,policy,"learned",TOTAL,SECONDS)
        replay(n,f,policy,TOTAL,r)
    elif arm == "v14":
        r=hybrid(n,f,policy,plan,total=TOTAL,seconds=SECONDS)
        verify_hybrid(n,f,policy,r)
    elif arm == "v16":
        r=adaptive(n,f,policy,plan,total=TOTAL,seconds=SECONDS)
        verify_report(n,f,policy,plan,r)
    elif arm in ("v15+v12","v17+v12"):
        r=retrieval_arm(n,f,policy,old,lib,arm)
    elif arm in ("v18","v18-no-retrieval"):
        r=solve(n,f,policy,plan,lib,total=TOTAL,seconds=SECONDS,retrieval=arm=="v18")
        verify(n,f,policy,plan,lib,r)
    else:
        raise ValueError("invalid arm")
    if not 0<=r["work_steps"]<=TOTAL:
        raise ValueError("reported work outside envelope")
    return r


def worker():
    # Hard process address-space and CPU limits; parent enforces wall time.
    # Linux-only; fail rather than silently running without these controls.
    resource.setrlimit(resource.RLIMIT_AS,(MEMORY,MEMORY))
    resource.setrlimit(resource.RLIMIT_CPU,(WALL,WALL))
    os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    try:
        r=run_arm(json.load(sys.stdin))
    except (MemoryError, Exhausted):
        r={"decision":"unknown","resource_exhausted":True}
    u=resource.getrusage(resource.RUSAGE_SELF)
    print(json.dumps({"result":r,"cpu_seconds":u.ru_utime+u.ru_stime,"max_rss_kib":u.ru_maxrss}))


def isolated(req):
    start=time.monotonic()
    try:
        p=subprocess.run([sys.executable,"-m",__name__ if __name__!="__main__" else
                          "mathos.research.pnp_unified_discovery_frontier_v18","--worker"],
                         input=json.dumps(req),text=True,capture_output=True,timeout=WALL)
    except subprocess.TimeoutExpired:
        return {"result":{"decision":"unknown","timeout":True},"wall_seconds":time.monotonic()-start}
    if p.returncode in (-signal.SIGXCPU,-signal.SIGKILL):
        return {"result":{"decision":"unknown","process_resource_signal":p.returncode},
                "wall_seconds":time.monotonic()-start}
    if p.returncode:
        raise RuntimeError("worker failed: "+p.stderr[-4000:])
    out=json.loads(p.stdout)
    out["wall_seconds"]=time.monotonic()-start
    return out


def main():
    if sys.argv[1:]==["--worker"]:
        worker()
        return
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("benchmark","scheduler","failures","library","checkpoint"):
        p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args()
    paths=(a.benchmark,a.scheduler,a.failures,a.library)
    if a.checkpoint.resolve() in {x.resolve() for x in paths}:
        p.error("cannot overwrite source evidence")
    source,scheduler,failures,lr=(json.loads(x.read_text()) for x in paths)
    audit_library(source,scheduler,failures,lr)
    policy,plan=train(source),failures["selected_plan"]
    old,lib=lr["v15_source_templates"],lr["library"]
    manifest=cases(source,lr)
    report={"schema":"mathos-pnp-v18-development/1","seed":SEED,
            "scope":"public_synthetic_development_not_blind_holdout",
            "upstream":[digest(x) for x in (source,scheduler,failures,lr)],
            "library_sha256":digest(lib),"manifest_sha256":digest(manifest),
            "envelope":{"cpu_cores":1,"address_space_bytes":MEMORY,"wall_seconds":WALL,
                        "cooperative_seconds":SECONDS,"reported_work_steps":TOTAL},
            "completion":"running","rows":[],"universal_obligation":"unresolved"}
    a.checkpoint.parent.mkdir(parents=True,exist_ok=True)
    def save():
        temp=a.checkpoint.with_suffix(".tmp")
        temp.write_text(json.dumps(report,sort_keys=True,indent=2))
        temp.replace(a.checkpoint)
    save()
    for i,c in enumerate(manifest):
        row={"case":c,"features":features(c["n"],c["clauses"]),"reference_sat":reference(c),"arms":{}}
        # Deterministic alternating arm order; no outcomes feed into library.
        for arm in ARMS[i%len(ARMS):]+ARMS[:i%len(ARMS)]:
            req={"arm":arm,"case":c,"policy":policy,"plan":plan,"old":old,"library":lib}
            result=isolated(req)
            d=result["result"]["decision"]
            if d not in ("sat","unsat","unknown") or (d!="unknown" and (d=="sat")!=row["reference_sat"]):
                raise ValueError("false or invalid decision")
            row["arms"][arm]=result
        report["rows"].append(row)
        save()
    if digest(lib)!=report["library_sha256"]:
        raise ValueError("library changed")
    report["summary"]={}
    for family in ("all","random2","random3","chain"):
        rows=[r for r in report["rows"] if family=="all" or r["case"]["family"]==family]
        report["summary"][family]={}
        for arm in ARMS:
            xs=[r["arms"][arm] for r in rows]
            report["summary"][family][arm]={
                **{d:sum(x["result"]["decision"]==d for x in xs) for d in ("sat","unsat","unknown")},
                "wall_seconds":sum(x["wall_seconds"] for x in xs),
                "max_rss_kib":max((x.get("max_rss_kib",0) for x in xs),default=0)}
    report["completion"]="completed"
    save()
    print(json.dumps(report["summary"],sort_keys=True,indent=2))


if __name__=="__main__":
    main()
