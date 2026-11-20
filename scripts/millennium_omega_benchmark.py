"""Reproducible scoped smoke benchmark, not a mathematical score."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

# Also support direct execution from the repository root without installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathos.millennium_omega import audit_packet, run_framework


def benchmark(runs: int = 3) -> dict:
    if not (1 <= runs <= 20):
        raise ValueError("runs must be 1..20")
    elapsed = []
    fingerprints = []
    for _ in range(runs):
        start = time.perf_counter()
        packet = run_framework()
        audit_packet(packet)
        elapsed.append(time.perf_counter() - start)
        fingerprints.append(packet["assurance"]["content_sha256"])
    if len(set(fingerprints)) != 1:
        raise RuntimeError("nondeterministic research packet")
    return {
        "schema": "mathos.millennium_omega.benchmark/1",
        "runs": runs,
        "engine_count": 7,
        "agent_stage_count_per_engine": 6,
        "all_scopes": "RESEARCH_ONLY",
        "globally_proved_problems": 0,
        "packet_sha256": fingerprints[0],
        "elapsed_seconds": {
            "minimum": min(elapsed),
            "median": statistics.median(elapsed),
            "maximum": max(elapsed),
        },
        "note": "Environment-dependent runtime, not performance superiority or proof evidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(benchmark(args.runs), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
