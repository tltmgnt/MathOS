"""Run deterministic RH-Omega reproducibility smoke benchmark (not RH proof)."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mathos.research.rh_omega import audit, run


def benchmark(repetitions: int = 2) -> dict:
    if type(repetitions) is not int or not 1 <= repetitions <= 8:
        raise ValueError("repetitions must be between 1 and 8")
    times = []
    packet_hashes = []
    for _ in range(repetitions):
        start = time.perf_counter()
        packet = run()
        audit(packet)
        times.append(time.perf_counter() - start)
        packet_hashes.append(packet["assurance"]["content_sha256"])
    if len(set(packet_hashes)) != 1:
        raise RuntimeError("RH-Omega deterministic packet changed between runs")
    return {
        "schema": "mathos.rh_omega.benchmark/1",
        "repetitions": repetitions,
        "eight_checks_completed": True,
        "ten_roles_produced": True,
        "packet_sha256": packet_hashes[0],
        "deterministic_across_repetitions": True,
        "duration_seconds": {
            "min": min(times), "median": statistics.median(times),
            "max": max(times),
        },
        "universal_rh_proof_obligations_discharged": 0,
        "independent_formal_rh_replay": False,
        "meaning": "Runtime and consistency only, not proof completeness or novelty",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=int, default=2)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(benchmark(args.repetitions), indent=2,
                         sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
