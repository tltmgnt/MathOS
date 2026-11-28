"""Matched frozen v16 / Hall-first comparisons on public stress and scaling cases."""
import argparse
import json
from pathlib import Path
import random
import time
from itertools import combinations

from . import pnp_adaptive_decision as adaptive
from . import pnp_hall_portfolio as candidate
from .pnp_adaptive_frontier import certificate_bytes
from .pnp_v16_stress import manifest as stress, reference as stress_reference, pigeon, bitset_reference
from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train
from .pnp_failure_synthesis import audit as audit_v13
from .pnp_outcome_engine import checkpoint

SCHEMA = "mathos-pnp-hall-frontier/1"
SEED = 181902
TOTAL, SECONDS = 100_000, 5
ARMS = ("v16", "hall_first")
GROUPS = ("retrospective", "scaled_random", "structural", "new_pigeon", "mixed")


def manifest():
    cases = list(stress())
    for p, h in ((6,6), (7,6), (8,8), (9,8), (12,11), (12,12)):
        cases.append({"id": f"pigeon_{p}_{h}", "group": "new_pigeon",
                      "kind": "pigeon", "n": p*h, "pigeons": p, "holes": h,
                      "clauses": pigeon(p, h)})
    f = [[1,2], [3,4], [5,6], [7,8],
         [-1,-3], [-1,-5], [-3,-5], [-2,-4], [-2,-6], [-4,-6]]
    cases.append({"id": "local_deficiency", "group": "new_pigeon",
                  "kind": "enumerate", "n": 8, "clauses": f})
    rng = random.Random(SEED)
    for i in range(12):
        n = 9 if i < 6 else 12
        groups = [list(range(j+1,j+4)) for j in range(0,n,3)]
        f = groups + [[-a,-b] for a,b in combinations(range(1,n+1),2)
                      if (a-1)//3 != (b-1)//3 and rng.random() < .35]
        if i % 2:
            f += [[v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3)]
                  for _ in range(n)]
        rng.shuffle(f)
        cases.append({"id": f"mixed_{i:02d}", "group": "mixed",
                      "kind": "enumerate", "n": n, "clauses": f})
    return cases


def reference(c):
    return stress_reference(c)


def summary(rows):
    out = {}
    for group in GROUPS:
        selected = [r for r in rows if r["case"]["group"] == group]
        arms = {a: {"sat": 0, "unsat": 0, "unknown": 0, "work_steps": 0,
                    "elapsed_ns": 0, "certificate_bytes": 0} for a in ARMS}
        route = {"skipped": 0, "replayed": 0, "unrecognized": 0, "resource_exhausted": 0,
                 "fallback_attempts": 0}
        losses, gains, unresolved = [], [], []
        for row in selected:
            records = row["arms"]
            for arm in ARMS:
                r = records[arm]
                a = arms[arm]
                a[r["decision"]] += 1
                a["work_steps"] += r["work_steps"]
                a["elapsed_ns"] += row["elapsed_ns"][arm]
                a["certificate_bytes"] += certificate_bytes(r)
            r = records["hall_first"]
            route[r["hall"]["status"] if r["hall"] else "skipped"] += 1
            route["fallback_attempts"] += r["fallback"] is not None
            b, h = records["v16"]["decision"], r["decision"]
            ident = row["case"]["id"]
            if b != "unknown" and h == "unknown":
                losses.append(ident)
            if b == "unknown" and h != "unknown":
                gains.append(ident)
            if h == "unknown":
                unresolved.append(ident)
        out[group] = {"cases": len(selected), "reference_unsat": sum(not x["reference"] for x in selected),
                      "arms": arms, "routes": route, "baseline_only": losses,
                      "candidate_only": gains, "unresolved": unresolved}
    return out


def run(source, scheduler, failures, path):
    audit_v13(source, scheduler, failures)
    policy, plan = train(source), failures["selected_plan"]
    r = {"schema": SCHEMA, "upstream": [digest(x) for x in (source, scheduler, failures)],
         "total": TOTAL, "seconds": SECONDS, "seed": SEED,
         "completion": "running", "universal_obligation": "unresolved", "rows": []}
    checkpoint(path, r)
    for i, c in enumerate(manifest()):
        n, f = c["n"], c["clauses"]
        row = {"case": c, "reference": reference(c), "arms": {}, "elapsed_ns": {}}
        for arm in (ARMS if i % 2 == 0 else ARMS[::-1]):
            start = time.perf_counter_ns()
            engine = adaptive if arm == "v16" else candidate
            record = engine.solve(n, f, policy, plan, total=TOTAL, seconds=SECONDS)
            row["elapsed_ns"][arm] = time.perf_counter_ns() - start
            row["arms"][arm] = record
            if record["decision"] != "unknown" and (record["decision"] == "sat") != row["reference"]:
                raise AssertionError("incorrect decision")
        r["rows"].append(row)
        checkpoint(path, r)
    r["summary"] = summary(r["rows"])
    r["completion"] = "completed"
    checkpoint(path, r)
    return r


def audit(source, scheduler, failures, r):
    audit_v13(source, scheduler, failures)
    policy, plan = train(source), failures["selected_plan"]
    if (r["schema"], r["upstream"], r["total"], r["seconds"], r["seed"],
            r["completion"], r["universal_obligation"]) != (
            SCHEMA, [digest(x) for x in (source, scheduler, failures)], TOTAL, SECONDS,
            SEED, "completed", "unresolved"):
        raise ValueError("report binding")
    cases = manifest()
    if len(cases) != len(r["rows"]):
        raise ValueError("missing cases")
    for c, row in zip(cases, r["rows"]):
        n, f = c["n"], c["clauses"]
        if (row["case"] != c or row["reference"] is not reference(c)
                or set(row["arms"]) != set(ARMS) or set(row["elapsed_ns"]) != set(ARMS)):
            raise ValueError("case or reference mismatch")
        for arm, record in row["arms"].items():
            if (record["total_steps"], record["seconds"]) != (TOTAL, SECONDS):
                raise ValueError("unequal budget")
            if arm == "v16":
                adaptive.verify_report(n, f, policy, plan, record)
            else:
                candidate.verify(n, f, policy, plan, record)
            d = record["decision"]
            if d != "unknown" and (d == "sat") != row["reference"]:
                raise ValueError("reference disagreement")
            elapsed = row["elapsed_ns"][arm]
            if type(elapsed) is not int or elapsed < 0:
                raise ValueError("invalid observed runtime")
    if r["summary"] != summary(r["rows"]):
        raise ValueError("summary mismatch")
    return True


def gate(r):
    s = r["summary"]
    if any(g["baseline_only"] for g in s.values()):
        raise ValueError("paired v16 loss")
    for group in ("retrospective", "scaled_random", "structural", "new_pigeon"):
        if s[group]["unresolved"]:
            raise ValueError("required coverage missed in " + group)
    if not {"pigeon_5_4", "pigeon_5_5", "pigeon_6_5"} <= set(s["structural"]["candidate_only"]):
        raise ValueError("previous structural gain not reproduced")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("benchmark", "scheduler", "failures"):
        p.add_argument("--"+name, type=Path, required=True)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checkpoint", type=Path)
    mode.add_argument("--audit", type=Path)
    p.add_argument("--gate", action="store_true")
    a = p.parse_args()
    paths = [a.benchmark, a.scheduler, a.failures]
    def read(path):
        if path.stat().st_size > 128_000_000:
            raise ValueError("evidence size limit")
        return json.loads(path.read_text(encoding="utf-8"))
    upstream = [read(x) for x in paths]
    if a.checkpoint:
        if a.checkpoint.resolve() in {x.resolve() for x in paths}:
            raise ValueError("cannot overwrite upstream")
        r = run(*upstream, a.checkpoint)
    else:
        r = read(a.audit)
    audit(*upstream, r)
    print(json.dumps(r["summary"], indent=2, sort_keys=True))
    if a.gate:
        gate(r)


if __name__ == "__main__":
    main()
