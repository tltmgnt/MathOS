"""Matched software fixtures; no discovery or superiority claim."""
import argparse
import gc
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
from time import perf_counter
import tracemalloc

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.tga_gap_benchmark import fixture
from mathos.proof_analysis.gap_analysis import analyze, analyze_legacy


def benchmark():
    rows = []
    for kind, size in (("chain", 100), ("shared", 100), ("alternatives", 100),
                       ("binary_choices", 4), ("binary_choices", 8)):
        graph, expected = fixture(kind, size)
        result = {"fixture": kind, "size": size, "completion_sets": len(expected)}
        measurements = {"legacy": [], "incremental": []}
        for trial in range(3):
            pair = [("legacy", analyze_legacy), ("incremental", analyze)]
            if trial % 2:
                pair.reverse()
            for name, fn in pair:
                gc.collect()
                tracemalloc.start()
                begin = perf_counter()
                try:
                    actual = fn(graph, "target")
                finally:
                    elapsed = perf_counter() - begin
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                if actual["minimal_completion_sets"] != expected:
                    raise ValueError("incorrect result: " + kind + "/" + name)
                measurements[name].append({"seconds": elapsed, "peak_bytes": peak})
        for name, trials in measurements.items():
            result[name] = {"trials": trials, "median_seconds": statistics.median(t["seconds"] for t in trials),
                            "median_peak_bytes": statistics.median(t["peak_bytes"] for t in trials)}
        rows.append(result)
    return {"source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "python": sys.version, "platform": platform.platform(), "cases": rows,
            "scope": "Synthetic fixtures; tracemalloc-instrumented; no independent validation or performance threshold",
            "mathematical_certification": "NOT_CERTIFIED"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(benchmark(), indent=2) + "\n", encoding="utf-8")
