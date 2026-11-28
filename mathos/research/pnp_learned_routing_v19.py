"""Frozen, coverage-first routing learned from paired, replayed calibration.

This module selects a producer; it introduces no new inference rule.
A gate prediction, retrieval miss, or exhaustion is never a proof.
"""
from .pnp_structural_kernel import validate
from .pnp_evidence_benchmark import digest
from .pnp_unified_portfolio import fingerprint
from .pnp_evidence_scheduler import _limits
from .pnp_adaptive_decision import solve as adaptive, verify_report
from .pnp_unified_discovery_v18 import solve as integrated, verify as verify_integrated, features

SCHEMA = "mathos-pnp-learned-routing/1"
GATE_SCHEMA = "mathos-pnp-frozen-gate/1"
BUCKETS = ("small_simple", "small_general", "large_simple", "large_general")
MIN_PAIRS = 3


def bucket(info):
    return ("small" if info["active"] <= 16 else "large") + (
        "_simple" if info["width"] <= 2 or info["horn"] else "_general")


def _decision(row, arm):
    d = row["arms"][arm]["result"]["decision"]
    if d not in ("sat", "unsat", "unknown"):
        raise ValueError("invalid calibration decision")
    if d != "unknown" and (d == "sat") is not row["reference_sat"]:
        raise ValueError("calibration false verdict")
    return d


def fit(calibration, library):
    """Caller must independently audit calibration before fitting.

    Only coverage wins/losses select a route. Timings and reported work
    are not training labels. Sparse/tied buckets default to full v16.
    """
    if (calibration["schema"] != "mathos-pnp-v18-development/1"
            or calibration["completion"] != "completed"
            or calibration["library_sha256"] != digest(library)
            or calibration["universal_obligation"] != "unresolved"):
        raise ValueError("invalid calibration provenance")
    counts = {k: {"pairs": 0, "wins": 0, "losses": 0} for k in BUCKETS}
    seen = set()
    for row in calibration["rows"]:
        c = row["case"]
        key = fingerprint(c["n"], validate(c["n"], c["clauses"]))
        if key in seen or type(row["reference_sat"]) is not bool:
            raise ValueError("invalid calibration row")
        seen.add(key)
        info = features(c["n"], c["clauses"])
        if row["features"] != info:
            raise ValueError("calibration feature mismatch")
        a, b = _decision(row, "v16"), _decision(row, "v18")
        stats = counts[bucket(info)]
        stats["pairs"] += 1
        stats["wins"] += a == "unknown" and b != "unknown"
        stats["losses"] += a != "unknown" and b == "unknown"
    return {"schema": GATE_SCHEMA, "calibration_sha256": digest(calibration),
            "library_sha256": digest(library), "buckets": counts,
            "minimum_pairs": MIN_PAIRS, "rule": "positive_paired_coverage_no_losses"}


def validate_gate(gate, library):
    if (not isinstance(gate, dict) or set(gate) != {
            "schema", "calibration_sha256", "library_sha256", "buckets",
            "minimum_pairs", "rule"}
            or gate["schema"] != GATE_SCHEMA or gate["library_sha256"] != digest(library)
            or gate["minimum_pairs"] != MIN_PAIRS
            or gate["rule"] != "positive_paired_coverage_no_losses"
            or not isinstance(gate["calibration_sha256"], str)
            or len(gate["calibration_sha256"]) != 64
            or any(c not in "0123456789abcdef" for c in gate["calibration_sha256"])
            or not isinstance(gate["buckets"], dict)
            or set(gate["buckets"]) != set(BUCKETS)):
        raise ValueError("invalid gate")
    for stats in gate["buckets"].values():
        if (not isinstance(stats, dict) or set(stats) != {"pairs", "wins", "losses"}
                or any(type(v) is not int or v < 0 for v in stats.values())
                or stats["wins"] + stats["losses"] > stats["pairs"]):
            raise ValueError("invalid gate counts")


def select(info, gate, library):
    s = gate["buckets"][bucket(info)]
    return ("integrated" if library and s["pairs"] >= MIN_PAIRS
            and s["wins"] > 0 and s["losses"] == 0 else "adaptive")


def solve(n, clauses, policy, plan, library, gate, *, total=100_000, seconds=5):
    _limits(total, seconds)
    validate_gate(gate, library)
    f = validate(n, clauses)
    info = features(n, f)
    route = select(info, gate, library)
    if route == "adaptive":
        # Full v16 allowance, without v18's up-front retrieval reservation.
        payload = adaptive(n, f, policy, plan, total=total, seconds=seconds)
    else:
        payload = integrated(n, f, policy, plan, library, total=total,
                             seconds=seconds, retrieval=True)
    r = {"schema": SCHEMA, "input_sha256": fingerprint(n, f),
         "gate_sha256": digest(gate), "library_sha256": digest(library),
         "features": info, "bucket": bucket(info), "route": route,
         "total_steps": total, "seconds": seconds,
         "decision": payload["decision"], "work_steps": payload["work_steps"],
         "payload": payload, "universal_obligation": "unresolved"}
    verify(n, f, policy, plan, library, gate, r)
    return r


def verify(n, clauses, policy, plan, library, gate, r):
    _limits(r["total_steps"], r["seconds"])
    validate_gate(gate, library)
    f = validate(n, clauses)
    info = features(n, f)
    route = select(info, gate, library)
    if (r["schema"] != SCHEMA or r["input_sha256"] != fingerprint(n, f)
            or r["gate_sha256"] != digest(gate) or r["library_sha256"] != digest(library)
            or r["features"] != info or r["bucket"] != bucket(info) or r["route"] != route
            or r["universal_obligation"] != "unresolved"):
        raise ValueError("routing metadata mismatch")
    p = r["payload"]
    if (p["total_steps"], p["seconds"], p["decision"], p["work_steps"]) != (
            r["total_steps"], r["seconds"], r["decision"], r["work_steps"]):
        raise ValueError("payload accounting mismatch")
    if type(r["work_steps"]) is not int or not 0 <= r["work_steps"] <= r["total_steps"]:
        raise ValueError("work envelope")
    if route == "adaptive":
        verify_report(n, f, policy, plan, p)
    else:
        if p["retrieval"] is not True:
            raise ValueError("retrieval configuration mismatch")
        verify_integrated(n, f, policy, plan, library, p)
    return True
