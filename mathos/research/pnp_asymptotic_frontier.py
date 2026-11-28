"""Asymptotic family research: scoped theorem obligations and finite probes."""
import argparse
import json
from itertools import combinations
from pathlib import Path

from .pnp_certificate_routes import ROUTES, propose as old_propose
from .pnp_structural_kernel import Budget, Exhausted, normalize, brute
from .pnp_outcome_engine import checkpoint
from .pnp_outcome_registry import decompose
from .pnp_triple_parity import signed_family, propose, verify

THEOREM_SCOPE = {
    "T01": {"claim": "Every finite conjunction of supported signed triple blocks is pointwise equivalent to its pair parity constraints.",
            "status": "lean_source_available_not_checked_by_this_run",
            "lean": "PnpTripleParity.allBlocks"},
    "T02": {"claim": "The supported triple-block reduction has at most four binary clauses per six input clauses and polynomial total decision overhead.",
            "status": "mathematical_argument_not_formally_checked"},
    "T03": {"claim": "For each n>=4, the complete signed triple family with seed x1=true, all others=false is SAT but unrecognized by every v5 route.",
            "status": "mathematical_argument_not_formally_checked"},
    "T04": {"claim": "The complete family has primal width n-1 and normalized input proxy N=n+24*C(n,3); for fixed c, n-1>c*log2(N) eventually.",
            "status": "mathematical_argument_not_formally_checked"},
    "T05": {"claim": "For each n>=4, changing the first parity on triple (1,2,4) contradicts the parity on (1,2,3).",
            "status": "mathematical_argument_not_formally_checked"},
}


def probe(n, c, budget):
    result = []
    for inconsistent in (False, True):
        f = signed_family(n, inconsistent=inconsistent)
        nn, normalized, mapping = normalize(n, f)
        artifact = propose(n, f, budget)
        if artifact is None:
            raise AssertionError("supported family was not recognized")
        try:
            verify(n, f, artifact, budget)
        except ValueError as exc:
            raise AssertionError("triple certificate rejected") from exc
        sat = artifact["decision_certificate"]["kind"] == "sat_witness"
        if sat == inconsistent:
            raise AssertionError("family decision mismatch")
        if n <= 8 and brute(nn, normalized, budget) != sat:
            raise AssertionError("reference decision mismatch")
        covered = []
        for route in ROUTES:
            old = old_propose(nn, normalized, route, budget)
            if old is not None:
                from .pnp_certificate_routes import verify as old_verify
                old_verify(nn, normalized, old, budget)
                covered.append(route)
        if not inconsistent and covered:
            raise AssertionError("unexpected v5 coverage of family")
        # Every triple appears, which gives the complete graph; verify the
        # edge set directly. Clique and any ordering both certify n-1.
        edges = set()
        for clause in normalized:
            budget.tick(1 + len(clause))
            edges.update(combinations(sorted(abs(x) for x in clause), 2))
        if nn != n or len(edges) != n*(n-1)//2:
            raise AssertionError("complete graph premise not met")
        size = n + len(normalized) + sum(map(len, normalized))
        if size != n + 24*(n*(n-1)*(n-2)//6):
            raise AssertionError("family size identity mismatch")
        threshold = (size**c).bit_length()-1
        result.append({"variables": n, "input_clauses": len(normalized),
                       "binary_clauses": len(artifact["binary_clauses"]),
                       "input_size_proxy": size, "exact_treewidth": n-1,
                       "threshold": threshold, "gap": n-1-threshold,
                       "sat": sat, "v5_routes": covered,
                       "v6_certificate_replayed": True, "constant_output_width": 0,
                       "certificate_kind": artifact["decision_certificate"]["kind"],
                       "artifact": artifact})
    return result


def run(budget, *, sizes=(4, 6, 8, 12, 16, 24), c=1, target=None, checkpoint_path=None):
    if (not isinstance(sizes, (list, tuple)) or not 1 <= len(sizes) <= 21 or
            any(type(n) is not int or not 4 <= n <= 24 for n in sizes) or
            len(set(sizes)) != len(sizes)):
        raise ValueError("unique sizes in 4..24 required")
    if type(c) is not int or not 1 <= c <= 16:
        raise ValueError("fixed c must be in 1..16")
    r = {"schema": "mathos-pnp-asymptotic-frontier/1",
         "plans": [decompose("E01"), decompose("E02")], "theorem_obligations": THEOREM_SCOPE,
         "universal_obligation": "unresolved", "formal_verification": "not_performed",
         "p_equals_np_established": False, "p_not_equals_np_established": False,
         "completion": "documented_unresolved_obligations", "probes": [],
         "restart": {"sizes": sizes, "c": c, "target": target}}
    try:
        if checkpoint_path:
            checkpoint(checkpoint_path, r)
        for n in sizes:
            r["probes"].extend(probe(n, c, budget))
            if checkpoint_path:
                checkpoint(checkpoint_path, r)
        if target is not None:
            artifact = propose(target["n"], target["clauses"], budget)
            if artifact is not None:
                verify(target["n"], target["clauses"], artifact, budget)
            r["target_result"] = {"status": "certificate_replayed" if artifact else "unrecognized",
                                  "artifact": artifact}
        r["completion"] = "scoped_family_research_completed"
    except Exhausted as exc:
        r["completion"], r["reason"] = "resource_exhausted", str(exc)
    except AssertionError as exc:
        r["completion"], r["reason"] = "diagnostic_required", str(exc)
    r["work_steps"] = budget.steps
    if checkpoint_path:
        checkpoint(checkpoint_path, r)
    return r


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sizes", nargs="+", type=int, default=[4,6,8,12,16,24])
    p.add_argument("--c", type=int, default=1)
    p.add_argument("--input", type=Path)
    p.add_argument("--resume", type=Path)
    p.add_argument("--checkpoint", type=Path)
    p.add_argument("--seconds", type=float, default=60)
    p.add_argument("--max-steps", type=int, default=40_000_000)
    p.add_argument("--max-cells", type=int, default=200_000)
    a = p.parse_args(argv)
    if a.input and a.resume:
        p.error("choose input or resume")
    def read(path):
        if path.stat().st_size > 4_000_000:
            raise ValueError("input exceeds 4 MB")
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        opts = read(a.resume)["restart"] if a.resume else {
            "sizes": a.sizes, "c": a.c, "target": read(a.input) if a.input else None}
        r = run(Budget(a.seconds, a.max_steps, a.max_cells), checkpoint_path=a.checkpoint, **opts)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.error(str(exc))
    print(json.dumps(r, indent=2, sort_keys=True))
    return int(r["completion"] != "scoped_family_research_completed")


if __name__ == "__main__":
    raise SystemExit(main())
