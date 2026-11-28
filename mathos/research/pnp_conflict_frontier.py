"""Frozen comparison of Hall, standalone CDCL and candidate portfolio."""
import argparse
import json
from pathlib import Path
import random
import time
from itertools import product

from . import pnp_conflict_learning as cdcl
from . import pnp_conflict_portfolio as candidate
from . import pnp_hall_portfolio as baseline
from .pnp_hall_frontier import manifest as prior_manifest, reference as prior_reference
from .pnp_adaptive_frontier import certificate_bytes
from .pnp_failure_synthesis import audit as audit_v13, fresh_cases
from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train
from .pnp_outcome_engine import checkpoint
from .pnp_structural_kernel import validate

SCHEMA = "mathos-pnp-conflict-frontier/1"
SEED = 191903
TOTAL, SECONDS = 100_000, 5
ARMS = ("hall", "cdcl_full", "candidate")
GROUPS = ("retrospective","scaled_random","structural","new_pigeon","mixed",
          "archived_holdout","random_transition","parity_cycle")


def parity_cycle(k,bad):
    # Even cycle of x_i XOR x_{i+1} XOR z = rhs.
    # XOR all equations: every variable occurs an even number of times.
    # SAT when all rhs=0 (zero model); UNSAT when exactly one rhs=1.
    z = k+1
    f = []
    for i in range(1,k+1):
        v = (i, i%k+1, z)
        rhs = int(bad and i==k)
        for a in product((0,1),repeat=3):
            if sum(a)%2 != rhs:
                f.append([x if not bit else -x for x,bit in zip(v,a)])
    return f


def manifest():
    rows = list(prior_manifest())
    for c in fresh_cases(16028,24):
        rows.append(dict(c,id="archived_"+c["id"],group="archived_holdout",kind="enumerate"))
    rng = random.Random(SEED)
    for n in (18,20):
        for i in range(12):
            m = round(n*(3.8+0.1*i))
            f = [[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
                 for _ in range(m)]
            rows.append({"id":f"transition_{n}_{i}","group":"random_transition",
                         "kind":"bitset20","n":n,"clauses":f})
    for k in (18,24,32,48):
        for bad in (False,True):
            rows.append({"id":f"parity_{k}_{int(bad)}","group":"parity_cycle",
                         "kind":"parity","n":k+1,"bad":bad,"clauses":parity_cycle(k,bad)})
    return rows


def bitset20(n, clauses):
    f = validate(n,clauses)
    if n>20:
        raise ValueError("reference dimension")
    size = 1<<n
    mask = (1<<size)-1
    positives = []
    for v in range(n):
        stride = 1<<v
        pattern = ((1<<stride)-1)<<stride
        span = stride*2
        while span < size:
            pattern |= pattern<<span
            span *= 2
        positives.append(pattern)
    models = mask
    for c in f:
        sat = 0
        for x in c:
            a = positives[abs(x)-1]
            sat |= a if x>0 else mask^a
        models &= sat
        if not models:
            return False
    return bool(models)


def reference(c):
    if c["kind"] == "bitset20":
        return bitset20(c["n"],c["clauses"])
    if c["kind"] == "parity":
        k,bad = c["n"]-1,c["bad"]
        if k<4 or k%2 or type(bad) is not bool or c["clauses"]!=parity_cycle(k,bad):
            raise ValueError("invalid parity reference")
        return not bad
    return prior_reference(c)


def summary(rows):
    out = {}
    for group in GROUPS:
        selected = [r for r in rows if r["case"]["group"]==group]
        arms = {a:{"sat":0,"unsat":0,"unknown":0,"work_steps":0,
                   "elapsed_ns":0,"certificate_bytes":0} for a in ARMS}
        routes = {"attempted":0,"credited":0,"conflicts_credited":0,
                  "nonchronological_jumps_credited":0,"fallback_attempted":0}
        losses,gains,unresolved,full_only = [],[],[],[]
        for row in selected:
            records = row["arms"]
            for arm in ARMS:
                a,r = arms[arm],records[arm]
                a[r["decision"]] += 1
                a["work_steps"] += r["work_steps"]
                a["elapsed_ns"] += row["elapsed_ns"][arm]
                a["certificate_bytes"] += certificate_bytes(r)
            r = records["candidate"]
            a = r["cdcl"]
            routes["attempted"] += a is not None
            routes["fallback_attempted"] += r["fallback"] is not None
            if a and a["proof"] is not None:
                routes["credited"] += 1
                routes["conflicts_credited"] += a["proof"]["conflicts"]
                routes["nonchronological_jumps_credited"] += a["proof"]["nonchronological_jumps"]
            h,c,d = (records[x]["decision"] for x in ARMS)
            ident = row["case"]["id"]
            if h!="unknown" and d=="unknown": losses.append(ident)
            if h=="unknown" and d!="unknown": gains.append(ident)
            if c!="unknown" and d=="unknown": full_only.append(ident)
            if d=="unknown": unresolved.append(ident)
        out[group] = {"cases":len(selected),"reference_unsat":sum(not r["reference"] for r in selected),
                      "arms":arms,"candidate_cdcl":routes,"baseline_only":losses,
                      "candidate_only":gains,"cdcl_full_only":full_only,"unresolved":unresolved}
    return out


def run(source,scheduler,failures,path):
    audit_v13(source,scheduler,failures)
    policy,plan = train(source),failures["selected_plan"]
    r = {"schema":SCHEMA,"upstream":[digest(x) for x in (source,scheduler,failures)],
         "seed":SEED,"total":TOTAL,"seconds":SECONDS,"rows":[],
         "completion":"running","universal_obligation":"unresolved"}
    checkpoint(path,r)
    for i,c in enumerate(manifest()):
        n,f = c["n"],c["clauses"]
        row = {"case":c,"reference":reference(c),"arms":{},"elapsed_ns":{}}
        for arm in ARMS[i%3:]+ARMS[:i%3]:
            start = time.perf_counter_ns()
            if arm=="cdcl_full":
                a = cdcl.attempt(n,f,TOTAL,SECONDS)
            else:
                engine = baseline if arm=="hall" else candidate
                a = engine.solve(n,f,policy,plan,total=TOTAL,seconds=SECONDS)
            row["elapsed_ns"][arm] = time.perf_counter_ns()-start
            row["arms"][arm] = a
            if a["decision"]!="unknown" and (a["decision"]=="sat")!=row["reference"]:
                raise AssertionError("reference disagreement")
        r["rows"].append(row)
        checkpoint(path,r)
    r["summary"] = summary(r["rows"])
    r["completion"] = "completed"
    checkpoint(path,r)
    return r


def audit(source,scheduler,failures,r):
    audit_v13(source,scheduler,failures)
    policy,plan = train(source),failures["selected_plan"]
    if (r["schema"],r["upstream"],r["seed"],r["total"],r["seconds"],
            r["completion"],r["universal_obligation"]) != (
            SCHEMA,[digest(x) for x in (source,scheduler,failures)],SEED,TOTAL,SECONDS,
            "completed","unresolved"):
        raise ValueError("report binding")
    cases = manifest()
    if len(cases)!=len(r["rows"]):
        raise ValueError("missing cases")
    for c,row in zip(cases,r["rows"]):
        n,f = c["n"],c["clauses"]
        if (row["case"]!=c or row["reference"] is not reference(c)
                or set(row["arms"])!=set(ARMS) or set(row["elapsed_ns"])!=set(ARMS)):
            raise ValueError("manifest mismatch")
        for arm,a in row["arms"].items():
            if arm=="cdcl_full":
                cdcl.replay(n,f,a,TOTAL)
            else:
                if (a["total_steps"],a["seconds"])!=(TOTAL,SECONDS):
                    raise ValueError("unequal budget")
                (baseline if arm=="hall" else candidate).verify(n,f,policy,plan,a)
            if a["decision"]!="unknown" and (a["decision"]=="sat")!=row["reference"]:
                raise ValueError("incorrect decision")
            elapsed = row["elapsed_ns"][arm]
            if type(elapsed) is not int or elapsed<0:
                raise ValueError("invalid timing")
    if r["summary"]!=summary(r["rows"]):
        raise ValueError("summary mismatch")
    return True


def gate(r):
    s = r["summary"]
    if any(x["baseline_only"] for x in s.values()):
        raise ValueError("paired Hall regression")
    if any(s[g]["unresolved"] for g in GROUPS[:6]):
        raise ValueError("archived coverage regression")
    if not any(s[g]["candidate_only"] for g in GROUPS[6:]):
        raise ValueError("no new coverage gain")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("benchmark","scheduler","failures"):
        p.add_argument("--"+name,type=Path,required=True)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checkpoint",type=Path)
    mode.add_argument("--audit",type=Path)
    p.add_argument("--gate",action="store_true")
    a = p.parse_args()
    paths = [a.benchmark,a.scheduler,a.failures]
    def read(p):
        if p.stat().st_size>128_000_000:
            raise ValueError("evidence size limit")
        return json.loads(p.read_text(encoding="utf-8"))
    upstream = [read(p) for p in paths]
    if a.checkpoint:
        if a.checkpoint.resolve() in {p.resolve() for p in paths}:
            raise ValueError("cannot overwrite upstream")
        r = run(*upstream,a.checkpoint)
    else:
        r = read(a.audit)
    audit(*upstream,r)
    print(json.dumps(r["summary"],indent=2,sort_keys=True))
    if a.gate:
        gate(r)


if __name__=="__main__":
    main()
