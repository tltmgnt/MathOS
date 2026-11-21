"""Reproducible baseline of MathOS's *authored* proof-route gap analyzer.

Times and peak allocations are instrumented (tracemalloc), environment-specific
software metrics. No mathematical theorem or claim is certified by this program.
No repository evidence, registry, or proof-state file is modified.
"""
from __future__ import annotations

import argparse
import gc
import json
from itertools import product
from pathlib import Path
import platform
import statistics
import sys
from time import perf_counter
import tracemalloc

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathos.proof_analysis.gap_analysis import Claim, analyze
from mathos.proof_analysis.certification_audit import exhaustive_check


KINDS = ("chain", "shared", "alternatives", "binary_choices")


def fixture(kind: str, size: int):
    """Return a synthetic directed acyclic graph and independently specified answer."""
    if kind not in KINDS or type(size) is not int:
        raise ValueError("unknown fixture or noninteger size")
    if kind == "binary_choices":
        if not 1 <= size <= 10:
            raise ValueError("binary choice layers must be 1..10")
        graph = {}
        branches = []
        for i in range(size):
            a, b, node = f"a{i}", f"b{i}", f"choice{i}"
            graph[a] = Claim(a, "open")
            graph[b] = Claim(b, "open")
            graph[node] = Claim(node, "derived", ((a,), (b,)))
            branches.append(node)
        graph["target"] = Claim("target", "derived", (tuple(branches),))
        expected = [sorted(picks) for picks in product(
            *((f"a{i}", f"b{i}") for i in range(size))
        )]
    else:
        if not 3 <= size <= 500:
            raise ValueError("graph size must be 3..500")
        if kind == "chain":
            graph = {"x": Claim("x", "open")}
            parent = "x"
            for i in range(size - 1):
                name = "target" if i == size - 2 else f"step{i}"
                graph[name] = Claim(name, "derived", ((parent,),))
                parent = name
            expected = [["x"]]
        elif kind == "shared":
            graph = {"x": Claim("x", "open")}
            branch_names = []
            for i in range(size - 2):
                name = f"branch{i}"
                graph[name] = Claim(name, "derived", (("x",),))
                branch_names.append(name)
            graph["target"] = Claim("target", "derived", (tuple(branch_names),))
            expected = [["x"]]
        else:
            leaves = [f"leaf{i}" for i in range(size - 1)]
            graph = {name: Claim(name, "open") for name in leaves}
            graph["target"] = Claim("target", "derived", tuple((name,) for name in leaves))
            expected = [[name] for name in sorted(leaves)]
    expected.sort(key=lambda row: (len(row), row))
    return graph, expected


def benchmark(sizes=(10, 30, 100, 500), layers=(4, 6, 8), repeats=3):
    if type(repeats) is not int or not 1 <= repeats <= 5:
        raise ValueError("repeats must be 1..5")
    if not sizes or not layers:
        raise ValueError("nonempty sizes and layers required")
    cases = [(kind, n) for kind in KINDS[:-1] for n in sizes]
    cases += [("binary_choices", n) for n in layers]
    rows = []
    for kind, size in cases:
        graph, expected = fixture(kind, size)
        times, peaks = [], []
        failure = None
        for _ in range(repeats):
            gc.collect()
            tracemalloc.start()
            begin = perf_counter()
            try:
                result = analyze(graph, "target")
            except RecursionError:
                # Deep linear dependency chains can exceed Python's call stack.
                # Keep this a visible benchmark failure rather than hiding it.
                failure = "RECURSION_LIMIT"
            finally:
                elapsed_ms = (perf_counter() - begin) * 1000
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
            times.append(elapsed_ms)
            peaks.append(peak)
            if failure:
                break
            if result["minimal_completion_sets"] != expected:
                raise AssertionError(f"incorrect completion sets: {kind}/{size}")
            if result["status"] != "BLOCKED":
                raise AssertionError("synthetic fixture unexpectedly closed")
        open_count = sum(item.state == "open" for item in graph.values())
        checked = "not_run_analysis_failed" if failure else "not_run_open_leaf_limit"
        if not failure and open_count <= 10:
            audit = exhaustive_check(graph, "target", expected)
            checked = f"pass_{audit['assignments_checked']}_assignments"
        rows.append({
            "fixture": kind, "parameter": size,
            "status": failure or "ANALYZED",
            "nodes": len(graph), "open_leaves": open_count,
            "minimal_completion_set_count": None if failure else len(expected),
            "fixture_expected_sets_match": not bool(failure),
            "exhaustive_boolean_crosscheck": checked,
            "instrumented_wall_ms": {
                "min": round(min(times), 4),
                "median": round(statistics.median(times), 4),
                "max": round(max(times), 4),
            },
            "tracemalloc_peak_bytes": {
                "min": min(peaks), "median": int(statistics.median(peaks)),
                "max": max(peaks),
            },
        })
    return {
        "schema": "mathos.tga.proof_gap_benchmark/1",
        "scope": "Author-modeled AND/OR completion-set software only",
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "repeats_per_case": repeats,
        "cases": rows,
        "failed_cases": [f"{row['fixture']}:{row['parameter']}:{row['status']}"
                         for row in rows if row["status"] != "ANALYZED"],
        "mathematical_theorem_certified": False,
        "lean_kernel_checked": False,
        "interpretation": (
            "Wall times include tracemalloc instrumentation; graph fixtures are "
            "synthetic, output-size growth can be exponential, and this benchmark "
            "does not establish proof completeness or competitive performance."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+", default=[10, 30, 100, 500])
    parser.add_argument("--layers", type=int, nargs="+", default=[4, 6, 8])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = benchmark(tuple(args.sizes), tuple(args.layers), args.repeats)
    output = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
