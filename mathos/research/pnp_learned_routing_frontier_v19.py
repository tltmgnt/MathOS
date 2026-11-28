"""Public development comparison with frozen, separately audited calibration."""
import argparse
import json
import math
import os
import resource
import signal
import subprocess
import sys
import time
from pathlib import Path

from .pnp_structural_kernel import Exhausted
from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train
from .pnp_library_frontier import suite, case_key
from .pnp_unified_discovery_v18 import features
from .pnp_unified_discovery_frontier_v18 import (
    TOTAL, SECONDS, WALL, MEMORY, reference, audit_report as audit_v18,
    run_arm as old_run, replay_arm as old_replay,
)
from .pnp_learned_routing_v19 import fit, solve, verify

SEED = 19029
ARMS = ("v16", "v18", "v18-no-retrieval", "v19-gate")
SCHEMA = "mathos-pnp-v19-routing-development/1"
ENVELOPE = {"cpu_cores": 1, "address_space_bytes": MEMORY, "wall_seconds": WALL,
            "cooperative_seconds": SECONDS, "reported_work_steps": TOTAL}


def manifest(source, lr, calibration):
    forbidden = {case_key(r["case"]) for r in source["rows"]}
    for split in ("training", "retrospective", "discovery", "heldout"):
        forbidden.update(case_key(r["case"]) for r in lr[split])
    forbidden.update(case_key(r["case"]) for r in calibration["rows"])
    cases = suite(SEED, 12)
    for n in (24, 48, 96):
        for sign in (-1, 1):
            cases.append({"id": f"chain_{n}_{sign}", "family": "chain", "n": n,
                          "clauses": [[1]] + [[-i,i+1] for i in range(1,n)] + [[sign*n]]})
    keys = [case_key(c) for c in cases]
    if len(set(keys)) != len(keys) or set(keys) & forbidden:
        raise ValueError("evaluation overlaps calibration or library data")
    return cases


def worker():
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))
    resource.setrlimit(resource.RLIMIT_CPU, (WALL, WALL))
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    req = json.load(sys.stdin)
    try:
        if req["arm"] == "v19-gate":
            c = req["case"]
            r = solve(c["n"], c["clauses"], req["policy"], req["plan"],
                      req["library"], req["gate"], total=TOTAL, seconds=SECONDS)
        else:
            r = old_run(req)
    except (MemoryError, Exhausted):
        r = {"decision": "unknown", "resource_exhausted": True}
    u = resource.getrusage(resource.RUSAGE_SELF)
    print(json.dumps({"result": r, "cpu_seconds": u.ru_utime+u.ru_stime,
                      "max_rss_kib": u.ru_maxrss}))


def isolated(req):
    start = time.monotonic()
    try:
        p = subprocess.run([sys.executable, "-m",
              "mathos.research.pnp_learned_routing_frontier_v19", "--worker"],
              input=json.dumps(req), text=True, capture_output=True, timeout=WALL)
        if p.returncode in (-signal.SIGXCPU, -signal.SIGKILL):
            out = {"result": {"decision": "unknown", "process_resource_signal": p.returncode}}
        elif p.returncode:
            raise RuntimeError("worker failed: " + p.stderr[-4000:])
        else:
            out = json.loads(p.stdout)
    except subprocess.TimeoutExpired:
        out = {"result": {"decision": "unknown", "timeout": True}}
    out["wall_seconds"] = time.monotonic()-start
    return out


def replay(arm, c, policy, plan, old, lib, gate, r):
    if arm != "v19-gate" or any(k in r for k in (
            "resource_exhausted", "timeout", "process_resource_signal")):
        # V18's replay helper validates exhausted records before dispatch.
        old_replay(arm, c, policy, plan, old, lib, r)
    else:
        if (r["total_steps"], r["seconds"]) != (TOTAL, SECONDS):
            raise ValueError("v19 configuration mismatch")
        verify(c["n"], c["clauses"], policy, plan, lib, gate, r)


def summarize(rows):
    summary = {}
    for family in ("all", "random2", "random3", "chain"):
        group = [r for r in rows if family == "all" or r["case"]["family"] == family]
        arms = {}
        for arm in ARMS:
            xs = [r["arms"][arm] for r in group]
            arms[arm] = {d: sum(x["result"]["decision"] == d for x in xs)
                         for d in ("sat", "unsat", "unknown")}
            arms[arm].update(wall_seconds=sum(x["wall_seconds"] for x in xs),
                             max_rss_kib=max((x.get("max_rss_kib",0) for x in xs),default=0))
        paired = {}
        for arm in ARMS[1:]:
            pairs = [(r["arms"]["v16"]["result"]["decision"],
                      r["arms"][arm]["result"]["decision"]) for r in group]
            paired[arm] = {"wins": sum(a=="unknown" and b!="unknown" for a,b in pairs),
                           "losses": sum(a!="unknown" and b=="unknown" for a,b in pairs)}
        choices = [r["arms"]["v19-gate"]["result"].get("route","exhausted") for r in group]
        summary[family] = {"arms": arms, "versus_v16": paired,
                           "gate_routes": {k: choices.count(k) for k in
                                            ("adaptive","integrated","exhausted")}}
    return summary


def context(source, scheduler, failures, lr, calibration):
    audit_v18(source, scheduler, failures, lr, calibration)
    lib = lr["library"]
    return train(source), failures["selected_plan"], lr["v15_source_templates"], lib, fit(calibration, lib)


def header(source, scheduler, failures, lr, calibration, gate, cases):
    return {"schema": SCHEMA, "scope": "public_development_not_blind_holdout",
            "seed": SEED, "upstream": [digest(x) for x in (source,scheduler,failures,lr,calibration)],
            "gate": gate, "gate_sha256": digest(gate), "manifest_sha256": digest(cases),
            "envelope": ENVELOPE, "universal_obligation": "unresolved"}


def audit(source, scheduler, failures, lr, calibration, report):
    policy,plan,old,lib,gate = context(source,scheduler,failures,lr,calibration)
    cases = manifest(source,lr,calibration)
    expected = header(source,scheduler,failures,lr,calibration,gate,cases)
    if any(report.get(k) != v for k,v in expected.items()) or report["completion"] != "completed":
        raise ValueError("report provenance mismatch")
    if [r["case"] for r in report["rows"]] != cases:
        raise ValueError("manifest mismatch")
    for row in report["rows"]:
        c = row["case"]
        ref = reference(c)
        if row["reference_sat"] is not ref or set(row["arms"]) != set(ARMS):
            raise ValueError("row mismatch")
        for arm,x in row["arms"].items():
            if not math.isfinite(x["wall_seconds"]) or x["wall_seconds"] < 0:
                raise ValueError("invalid time observation")
            r = x["result"]
            replay(arm,c,policy,plan,old,lib,gate,r)
            d = r["decision"]
            if d not in ("sat","unsat","unknown") or (d!="unknown" and (d=="sat") != ref):
                raise ValueError("false decision")
    if report["summary"] != summarize(report["rows"]):
        raise ValueError("aggregate mismatch")
    return True


def main():
    if sys.argv[1:] == ["--worker"]:
        worker()
        return
    p = argparse.ArgumentParser(description=__doc__)
    for k in ("benchmark","scheduler","failures","library","calibration"):
        p.add_argument("--"+k,type=Path,required=True)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checkpoint",type=Path)
    mode.add_argument("--audit",type=Path)
    a = p.parse_args()
    paths = (a.benchmark,a.scheduler,a.failures,a.library,a.calibration)
    inputs = tuple(json.loads(x.read_text()) for x in paths)
    if a.audit:
        audit(*inputs,json.loads(a.audit.read_text()))
        print(json.dumps({"status":"positive_claims_and_frozen_gate_replayed"}))
        return
    if a.checkpoint.resolve() in {x.resolve() for x in paths}:
        p.error("cannot overwrite evidence inputs")
    source,scheduler,failures,lr,calibration = inputs
    policy,plan,old,lib,gate = context(*inputs)
    cases = manifest(source,lr,calibration)
    report = {**header(*inputs,gate,cases),"completion":"running","rows":[]}
    frozen = digest(gate),digest(lib)
    a.checkpoint.parent.mkdir(parents=True,exist_ok=True)
    def save():
        temp = a.checkpoint.with_suffix(".tmp")
        temp.write_text(json.dumps(report,sort_keys=True,indent=2))
        temp.replace(a.checkpoint)
    save()
    for i,c in enumerate(cases):
        ref = reference(c)
        row = {"case":c,"reference_sat":ref,"arms":{}}
        for arm in ARMS[i%len(ARMS):]+ARMS[:i%len(ARMS)]:
            result = isolated({"arm":arm,"case":c,"policy":policy,"plan":plan,
                               "old":old,"library":lib,"gate":gate})
            d = result["result"]["decision"]
            if d not in ("sat","unsat","unknown") or (d!="unknown" and (d=="sat")!=ref):
                raise ValueError("false decision")
            row["arms"][arm] = result
        report["rows"].append(row)
        save()
    if (digest(gate),digest(lib)) != frozen:
        raise ValueError("frozen gate or library mutated")
    report["summary"] = summarize(report["rows"])
    report["completion"] = "completed"
    save()
    print(json.dumps({"gate":gate,"summary":report["summary"]},sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
