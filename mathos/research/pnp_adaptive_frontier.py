"""Paired v12/v14/v16 evaluation; original suite is development evidence."""
import argparse
import json
from pathlib import Path
import time

from .pnp_evidence_benchmark import digest
from .pnp_evidence_scheduler import train, execute, replay
from .pnp_failure_synthesis import audit as audit_v13, fresh_cases
from .pnp_learning_frontier import reference
from .pnp_certified_learning import solve as hybrid, verify_hybrid
from .pnp_adaptive_decision import solve, verify_report
from .pnp_outcome_engine import checkpoint

SEED = 16028
ARMS = ("v12", "v14", "v16")
TOTAL, SECONDS = 100_000, 5
SCHEMA = "mathos-pnp-adaptive-frontier/1"


def suites(failures):
    original = fresh_cases(14014, 24)
    prior = [r["case"] for r in failures["training"]]
    heldout = fresh_cases(SEED, 24)
    # Syntactic disjointness after removing clause/literal order; no claim
    # of disjointness modulo signed renaming or logical equivalence.
    def key(c):
        return c["n"], tuple(sorted(set(tuple(sorted(set(x))) for x in c["clauses"])))
    known = {key(c) for c in original + prior + [r["case"] for r in failures["evaluation"]]}
    if any(key(c) in known for c in heldout) or len({key(c) for c in heldout}) != len(heldout):
        raise ValueError("held-out syntactic overlap")
    return {"original": original, "prior_unresolved": prior, "heldout": heldout}


def certificate_bytes(report):
    # Stored proof payloads only, not the whole search log; duplicates
    # intentionally count if they are stored twice. Input is external.
    def collect(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("proof", "certificate", "reduction", "compact") and v is not None:
                    yield v
                else:
                    yield from collect(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                yield from collect(v)
    return sum(len(json.dumps(x, separators=(",", ":")).encode("utf-8")) for x in collect(report))


def summary(rows):
    out = {}
    for suite in ("original", "prior_unresolved", "heldout"):
        subset = [r for r in rows if r["suite"] == suite]
        a = {arm: {"sat": 0, "unsat": 0, "unknown": 0, "work_steps": 0,
                   "elapsed_ns": 0, "certificate_bytes": 0} for arm in ARMS}
        for row in subset:
            for arm in ARMS:
                r = row["arms"][arm]
                a[arm][r["decision"]] += 1
                a[arm]["work_steps"] += r["work_steps"]
                a[arm]["elapsed_ns"] += row["elapsed_ns"][arm]
                a[arm]["certificate_bytes"] += certificate_bytes(r)
        out[suite] = {"cases": len(subset), "reference_unsat": sum(not r["reference"] for r in subset),
                      "arms": a,
                      "v12_only": [r["case"]["id"] for r in subset if r["arms"]["v12"]["decision"] != "unknown" and r["arms"]["v16"]["decision"] == "unknown"],
                      "v14_only": [r["case"]["id"] for r in subset if r["arms"]["v14"]["decision"] != "unknown" and r["arms"]["v16"]["decision"] == "unknown"],
                      "unresolved": [r["case"]["id"] for r in subset if r["arms"]["v16"]["decision"] == "unknown"],
                      "v14_initial_unknown_baseline_decided": [r["case"]["id"] for r in subset if r["arms"]["v14"]["initial"]["decision"] == "unknown" and r["arms"]["v12"]["decision"] != "unknown"],
                      "v14_learned_clauses": sum(r["arms"]["v14"]["learned_clauses"] for r in subset)}
    return out


def run(source, scheduler, failures, path):
    audit_v13(source, scheduler, failures)
    policy, plan = train(source), failures["selected_plan"]
    r = {"schema": SCHEMA, "upstream": [digest(x) for x in (source, scheduler, failures)],
         "total": TOTAL, "seconds": SECONDS, "seed": SEED, "rows": [],
         "completion": "running", "universal_obligation": "unresolved"}
    checkpoint(path, r)
    for suite, cases in suites(failures).items():
        for i, case in enumerate(cases):
            n, f = case["n"], case["clauses"]
            ref = reference(n, f)
            row = {"suite": suite, "case": case, "reference": ref, "arms": {}, "elapsed_ns": {}}
            for arm in ARMS[i % 3:] + ARMS[:i % 3]:
                start = time.perf_counter_ns()
                if arm == "v12":
                    result = execute(n, f, policy, "learned", TOTAL, SECONDS)
                elif arm == "v14":
                    result = hybrid(n, f, policy, plan, total=TOTAL, seconds=SECONDS)
                else:
                    result = solve(n, f, policy, plan, total=TOTAL, seconds=SECONDS)
                row["elapsed_ns"][arm] = time.perf_counter_ns() - start
                row["arms"][arm] = result
                if result["decision"] != "unknown" and (result["decision"] == "sat") != ref:
                    raise AssertionError("decision contradicts exhaustive reference")
            r["rows"].append(row)
            checkpoint(path, r)
    r["summary"] = summary(r["rows"])
    r["completion"] = "completed"
    checkpoint(path, r)
    return r


def audit(source, scheduler, failures, r):
    audit_v13(source, scheduler, failures)
    policy, plan = train(source), failures["selected_plan"]
    if (r["schema"], r["upstream"], r["total"], r["seconds"], r["seed"], r["completion"], r["universal_obligation"]) != (
            SCHEMA, [digest(x) for x in (source, scheduler, failures)], TOTAL, SECONDS, SEED, "completed", "unresolved"):
        raise ValueError("metadata mismatch")
    expected = [(s, c) for s, cases in suites(failures).items() for c in cases]
    if len(expected) != len(r["rows"]):
        raise ValueError("missing rows")
    for (suite, case), row in zip(expected, r["rows"]):
        n, f = case["n"], case["clauses"]
        if row["suite"] != suite or row["case"] != case or row["reference"] is not reference(n, f):
            raise ValueError("reference or manifest mismatch")
        a = row["arms"]
        if set(a) != set(ARMS) or set(row["elapsed_ns"]) != set(ARMS):
            raise ValueError("missing arm")
        if a["v12"]["arm"] != "learned":
            raise ValueError("wrong baseline")
        replay(n, f, policy, TOTAL, a["v12"])
        h = a["v14"]
        if (h["total_steps"], h["seconds"], h["plan"], h["probe_limit"]) != (TOTAL, SECONDS, plan, 16):
            raise ValueError("wrong hybrid configuration")
        verify_hybrid(n, f, policy, h)
        v = a["v16"]
        if (v["total_steps"], v["seconds"]) != (TOTAL, SECONDS):
            raise ValueError("wrong adaptive configuration")
        verify_report(n, f, policy, plan, v)
        for arm in ARMS:
            elapsed = row["elapsed_ns"][arm]
            if type(elapsed) is not int or elapsed < 0:
                raise ValueError("invalid elapsed time")
            d = a[arm]["decision"]
            if d != "unknown" and (d == "sat") != row["reference"]:
                raise ValueError("reference disagreement")
    if r["summary"] != summary(r["rows"]):
        raise ValueError("summary mismatch")
    return True


def gate(r):
    s = r["summary"]
    original = s["original"]
    v = original["arms"]["v16"]
    if v["sat"] + v["unsat"] < 18 or v["unsat"] < 6:
        raise ValueError("historical coverage or UNSAT target missed")
    if any(x["v12_only"] or x["v14_only"] for x in s.values()):
        raise ValueError("paired regression")
    h = s["heldout"]["arms"]
    if h["v16"]["unknown"] >= min(h["v12"]["unknown"], h["v14"]["unknown"]):
        raise ValueError("held-out strict coverage gain not established")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("benchmark", "scheduler", "failures"):
        p.add_argument("--" + name, required=True, type=Path)
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
    upstream = [read(x) for x in paths]
    if args.checkpoint:
        if args.checkpoint.resolve() in {x.resolve() for x in paths}:
            raise ValueError("cannot overwrite upstream evidence")
        r = run(*upstream, args.checkpoint)
    else:
        r = read(args.audit)
    audit(*upstream, r)
    print(json.dumps(r["summary"], indent=2, sort_keys=True))
    if args.gate:
        gate(r)


if __name__ == "__main__":
    main()
