"""Matched-budget stress experiment and allocation ablation for frozen v16.

This is an evaluation, not a replacement solver. Unknown never means UNSAT.
"""
import argparse
from itertools import combinations
import json
from pathlib import Path
import random
import time

from . import pnp_adaptive_decision as adaptive
from .pnp_adaptive_frontier import certificate_bytes
from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train, execute, replay
from .pnp_failure_synthesis import audit as audit_v13, fresh_cases
from .pnp_outcome_engine import checkpoint
from .pnp_structural_kernel import Budget, Exhausted, validate

SCHEMA = "mathos-pnp-v16-stress/1"
SEED = 161702
TOTAL = 100_000
SECONDS = 5
ARMS = ("v12_full", "v12_third", "search_full", "search_initial", "v16")


def chain(n, inconsistent):
    f = [[1]] + [[-i, i + 1] for i in range(1, n)]
    if inconsistent:
        f.append([-n])
    return f


def pigeon(pigeons, holes):
    def v(p, h):
        return p * holes + h + 1
    return ([[v(p, h) for h in range(holes)] for p in range(pigeons)] +
            [[-v(p, h), -v(q, h)] for h in range(holes)
             for p, q in combinations(range(pigeons), 2)])


def manifest():
    cases = [dict(c, group="retrospective", kind="enumerate") for c in fresh_cases(14014, 24)]
    rng = random.Random(SEED)
    for n in (10, 12, 14, 16):
        for i in range(4):
            f = [[v if rng.randrange(2) else -v for v in rng.sample(range(1, n + 1), 3)]
                 for _ in range(4 * n + rng.randint(0, n))]
            cases.append({"id": f"random_{n}_{i}", "group": "scaled_random",
                          "kind": "enumerate", "n": n, "clauses": f})
    for n in (32, 64, 65, 96):
        for bad in (False, True):
            cases.append({"id": f"chain_{n}_{int(bad)}", "group": "structural",
                          "kind": "chain", "n": n, "inconsistent": bad,
                          "clauses": chain(n, bad)})
    for p, h in ((3, 3), (4, 3), (4, 4), (5, 4), (5, 5), (6, 5)):
        cases.append({"id": f"pigeon_{p}_{h}", "group": "structural",
                      "kind": "pigeon", "n": p * h, "pigeons": p, "holes": h,
                      "clauses": pigeon(p, h)})
    return cases


def bitset_reference(n, clauses):
    """Independent exhaustive truth table, bit i represents assignment i."""
    f = validate(n, clauses)
    if n > 16:
        raise ValueError("reference limited to 16 variables")
    all_bits = (1 << (1 << n)) - 1
    positive = []
    for v in range(n):
        stride = 1 << v
        block = (1 << stride) - 1
        repeat = all_bits // ((1 << (2 * stride)) - 1)
        positive.append((block << stride) * repeat)
    models = all_bits
    for c in f:
        bits = 0
        for x in c:
            a = positive[abs(x) - 1]
            bits |= a if x > 0 else all_bits ^ a
        models &= bits
        if not models:
            return False
    return bool(models)


def reference(case):
    n, f, kind = case["n"], case["clauses"], case["kind"]
    if kind == "enumerate":
        return bitset_reference(n, f)
    if kind == "chain":
        # Unit 1 implies each successive unit by induction; all true is
        # a model unless a contradictory final negative unit is present.
        bad = case["inconsistent"]
        if type(bad) is not bool or f != chain(n, bad):
            raise ValueError("invalid chain reference")
        return not bad
    if kind == "pigeon":
        # At least one hole per pigeon, at most one pigeon per hole.
        # Injection iff p <= h; choose distinct holes for SAT.
        p, h = case["pigeons"], case["holes"]
        if n != p * h or f != pigeon(p, h):
            raise ValueError("invalid pigeon reference")
        return p <= h
    raise ValueError("unknown reference family")


def limits(arm, f):
    if arm == "v12_third":
        return TOTAL // 3, SECONDS / 3
    if arm == "search_initial":
        q = adaptive.quota("search", TOTAL, 0, adaptive._features(f))
        return q, SECONDS * q / TOTAL
    return TOTAL, SECONDS


def search_only(n, f, total, seconds):
    b = Budget(seconds=seconds, max_steps=total, max_cells=200_000)
    try:
        p = adaptive.search(n, f, b)
        adaptive.verify_search(n, f, p, b)
        return {"decision": p["decision"], "proof": p, "work_steps": b.steps,
                "status": "replayed"}
    except Exhausted as exc:
        return {"decision": "unknown", "proof": None, "work_steps": b.steps,
                "status": "resource_exhausted", "reason": str(exc)}


def attempt(arm, n, f, policy, plan):
    total, seconds = limits(arm, f)
    start = time.perf_counter_ns()
    if arm.startswith("v12_"):
        record = execute(n, f, policy, "learned", total, seconds)
    elif arm.startswith("search_"):
        record = search_only(n, f, total, seconds)
    elif arm == "v16":
        record = adaptive.solve(n, f, policy, plan, total=total, seconds=seconds)
    else:
        raise ValueError("invalid arm")
    return {"record": record, "elapsed_ns": time.perf_counter_ns() - start,
            "quota": total, "seconds": seconds}


def verify_attempt(arm, n, f, policy, plan, a):
    total, seconds = limits(arm, f)
    r = a["record"]
    if (a["quota"], a["seconds"]) != (total, seconds) or (
            type(a["elapsed_ns"]) is not int or a["elapsed_ns"] < 0 or
            type(r["work_steps"]) is not int or not 0 <= r["work_steps"] <= total):
        raise ValueError("invalid budget or observed work")
    if arm.startswith("v12_"):
        if r["arm"] != "learned":
            raise ValueError("wrong scheduler arm")
        replay(n, f, policy, total, r)
    elif arm.startswith("search_"):
        p = r["proof"]
        if r["status"] == "replayed":
            if p is None or p["decision"] != r["decision"]:
                raise ValueError("missing search proof")
            adaptive.verify_search(n, f, p, adaptive._audit_budget())
        elif r["status"] != "resource_exhausted" or p is not None or r["decision"] != "unknown":
            raise ValueError("invalid exhausted search")
    elif arm == "v16":
        if (r["total_steps"], r["seconds"]) != (total, seconds):
            raise ValueError("wrong adaptive budget")
        adaptive.verify_report(n, f, policy, plan, r)
    else:
        raise ValueError("invalid arm")


def summarize(rows):
    out = {}
    for group in ("retrospective", "scaled_random", "structural"):
        selected = [r for r in rows if r["case"]["group"] == group]
        arms = {a: {"sat": 0, "unsat": 0, "unknown": 0, "work_steps": 0,
                    "elapsed_ns": 0, "certificate_bytes": 0} for a in ARMS}
        stages = {s: {"attempted": 0, "exhausted": 0, "decided": 0, "lemmas": 0}
                  for s in adaptive.STAGES}
        starvation, adaptive_only, search_only_ids, baseline_only, unresolved = [], [], [], [], []
        for row in selected:
            records = {a: row["arms"][a]["record"] for a in ARMS}
            for a, r in records.items():
                x = arms[a]
                x[r["decision"]] += 1
                x["work_steps"] += r["work_steps"]
                x["elapsed_ns"] += row["arms"][a]["elapsed_ns"]
                x["certificate_bytes"] += certificate_bytes(r)
            for attempt in records["v16"]["attempts"]:
                stage = stages[attempt["stage"]]
                stage["attempted"] += 1
                stage["exhausted"] += attempt["status"] == "resource_exhausted"
                payload = attempt["payload"]
                stage["decided"] += payload is not None and payload["decision"] != "unknown"
                stage["lemmas"] += attempt["stage"] == "learn" and payload is not None
            known = {a: r["decision"] != "unknown" for a, r in records.items()}
            ident = row["case"]["id"]
            if known["v12_full"] and not known["v12_third"]:
                starvation.append(ident)
            if known["v16"] and not known["search_full"]:
                adaptive_only.append(ident)
            if known["search_full"] and not known["v16"]:
                search_only_ids.append(ident)
            if known["v12_full"] and not known["v16"]:
                baseline_only.append(ident)
            if not known["v16"]:
                unresolved.append(ident)
        out[group] = {"cases": len(selected), "reference_unsat": sum(not r["reference"] for r in selected),
                      "arms": arms, "v16_stages": stages,
                      "v12_full_only_vs_third": starvation,
                      "v16_only_vs_full_search": adaptive_only,
                      "full_search_only_vs_v16": search_only_ids,
                      "v12_full_only_vs_v16": baseline_only, "v16_unresolved": unresolved}
    return out


def run(source, scheduler, failures, path):
    audit_v13(source, scheduler, failures)
    policy, plan = train(source), failures["selected_plan"]
    r = {"schema": SCHEMA, "upstream": [digest(x) for x in (source, scheduler, failures)],
         "seed": SEED, "total": TOTAL, "seconds": SECONDS, "rows": [],
         "completion": "running", "universal_obligation": "unresolved"}
    checkpoint(path, r)
    for i, c in enumerate(manifest()):
        n, f = c["n"], c["clauses"]
        row = {"case": c, "reference": reference(c), "arms": {}}
        for arm in ARMS[i % len(ARMS):] + ARMS[:i % len(ARMS)]:
            a = attempt(arm, n, f, policy, plan)
            verify_attempt(arm, n, f, policy, plan, a)
            d = a["record"]["decision"]
            if d != "unknown" and (d == "sat") != row["reference"]:
                raise AssertionError("incorrect decision")
            row["arms"][arm] = a
        r["rows"].append(row)
        checkpoint(path, r)
    r["summary"] = summarize(r["rows"])
    r["completion"] = "completed"
    checkpoint(path, r)
    return r


def audit(source, scheduler, failures, r):
    audit_v13(source, scheduler, failures)
    policy, plan = train(source), failures["selected_plan"]
    if (r["schema"], r["upstream"], r["seed"], r["total"], r["seconds"],
            r["completion"], r["universal_obligation"]) != (
            SCHEMA, [digest(x) for x in (source, scheduler, failures)], SEED, TOTAL,
            SECONDS, "completed", "unresolved"):
        raise ValueError("invalid report binding")
    cases = manifest()
    if len(cases) != len(r["rows"]):
        raise ValueError("missing cases")
    for c, row in zip(cases, r["rows"]):
        if row["case"] != c or row["reference"] is not reference(c) or set(row["arms"]) != set(ARMS):
            raise ValueError("case or reference mismatch")
        for arm, a in row["arms"].items():
            verify_attempt(arm, c["n"], c["clauses"], policy, plan, a)
            d = a["record"]["decision"]
            if d != "unknown" and (d == "sat") != row["reference"]:
                raise ValueError("reference disagreement")
    if r["summary"] != summarize(r["rows"]):
        raise ValueError("summary mismatch")
    return True


def gate(r):
    # Existing original coverage is non-negotiable; stress misses are
    # explicitly retained for research, never silently promoted to success.
    original = r["summary"]["retrospective"]
    if original["arms"]["v16"]["unknown"] != 0 or original["v12_full_only_vs_v16"]:
        raise ValueError("v16 original regression")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("benchmark", "scheduler", "failures"):
        p.add_argument("--" + name, type=Path, required=True)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checkpoint", type=Path)
    mode.add_argument("--audit", type=Path)
    p.add_argument("--gate", action="store_true")
    args = p.parse_args()
    paths = [args.benchmark, args.scheduler, args.failures]
    def read(path):
        if path.stat().st_size > 128_000_000:
            raise ValueError("evidence size limit")
        return json.loads(path.read_text(encoding="utf-8"))
    inputs = [read(x) for x in paths]
    if args.checkpoint:
        if args.checkpoint.resolve() in {x.resolve() for x in paths}:
            raise ValueError("cannot overwrite upstream")
        r = run(*inputs, args.checkpoint)
    else:
        r = read(args.audit)
    audit(*inputs, r)
    print(json.dumps(r["summary"], indent=2, sort_keys=True))
    if args.gate:
        gate(r)


if __name__ == "__main__":
    main()
