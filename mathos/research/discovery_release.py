"""Build and check a bounded MathOS replay packet, not a scientific certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

from mathos.research import lean_first, lean_benchmark

ROOT = Path(__file__).resolve().parents[2]
PAYLOADS = ("kernel.json", "benchmark.json", "replay.json", "status.json")
EXPECTED = {"explicit_proof_baseline": 3, "reflexivity_baseline": 0, "placeholder_control": 0}


def read_json(path):
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("duplicate JSON key: " + key)
            obj[key] = value
        return obj
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def verify_packet(directory):
    """Verify fixed file inventory and byte integrity only; not authenticity."""
    directory = Path(directory)
    entries = {p.name: p for p in directory.iterdir()}
    if set(entries) != {*PAYLOADS, "manifest.json"}:
        raise ValueError("unexpected or missing packet files")
    if any(p.is_symlink() or not p.is_file() for p in entries.values()):
        raise ValueError("packet entries must be regular files")
    manifest = read_json(entries["manifest.json"])
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("unsupported manifest schema")
    commit = manifest.get("source_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("invalid source commit")
    hashes = manifest.get("sha256")
    if not isinstance(hashes, dict) or set(hashes) != set(PAYLOADS):
        raise ValueError("invalid payload inventory")
    for name in PAYLOADS:
        if hashes[name] != digest(entries[name]):
            raise ValueError("digest mismatch: " + name)
    return {"integrity": "PASS", "source_commit": commit,
            "external_validation_established": False,
            "scientific_certification": "NOT_ESTABLISHED"}


def summarize(kernel, benchmark, replay, portfolio, review):
    claims = kernel["claims"]
    if not claims or kernel["checked_count"] != len(claims) or any(
        c["formal_result"]["status"] != "KERNEL_CHECKED_SCOPE_ONLY" for c in claims
    ):
        raise ValueError("registered kernel checks incomplete")
    actual = {name: row["checked"] for name, row in benchmark["results"].items()}
    if actual != EXPECTED or any(row["total"] != 3 for row in benchmark["results"].values()):
        raise ValueError("benchmark smoke controls changed or failed")
    if replay.get("reproduced") is not True or replay.get("original_sha256") != benchmark["sha256"]:
        raise ValueError("benchmark replay failed")
    return {
        "registered_kernel_checks": len(claims),
        "registered_claim_ids": [c["claim_id"] for c in claims],
        "coverage_scope": "Lean-first registry only, not all MathOS claims",
        "benchmark_smoke_checked": actual,
        "benchmark_smoke_tasks_per_system": 3,
        "benchmark_scope": "handwritten smoke controls, not a comparative system evaluation",
        "benchmark_replay": "PASS",
        "portfolio_external_reproduction_reported": portfolio["external_independent_reproduction_completed"],
        "sat1_review_entries_reported": len(review["reviews"]),
        "independence_authenticated_by_this_tool": False,
        "level_5_certified": False,
        "level_6_certified": False,
        "remaining_gates": [
            "Human-authenticated independent replication and statement-fidelity review",
            "Prespecified held-out comparative evaluation with uncertainty and negative results",
            "Prior-art and novelty assessment of a scoped mathematical contribution",
            "Versioned archival release and sustained external research use"
        ],
        "millennium_prize_solution_certified": False,
    }


def build(directory, lean="lean"):
    directory = Path(directory).resolve()
    if git("status", "--porcelain", "--untracked-files=normal"):
        raise ValueError("use a clean source checkout and an output directory outside it")
    commit = git("rev-parse", "HEAD")
    directory.mkdir(parents=True, exist_ok=False)
    kernel = lean_first.audit_registry(verify_lean=True, lean=lean)
    spec = read_json(ROOT / "benchmarks/lean/smoke.json")
    benchmark = lean_benchmark.run(spec, lean)
    replay = lean_benchmark.replay(benchmark, lean)
    portfolio = read_json(ROOT / "docs/portfolio/STATUS.json")
    review = read_json(ROOT / "docs/research/papers/SAT1_INDEPENDENT_REVIEW_REGISTER.v1.json")
    status = summarize(kernel, benchmark, replay, portfolio, review)
    for name, value in zip(PAYLOADS, (kernel, benchmark, replay, status)):
        write_json(directory / name, value)
    if git("rev-parse", "HEAD") != commit or git("status", "--porcelain", "--untracked-files=no"):
        raise ValueError("tracked source changed during replay")
    write_json(directory / "manifest.json", {
        "schema_version": 1, "source_commit": commit,
        "python": sys.version, "platform": platform.platform(),
        "lean": kernel["lean_version"],
        "sha256": {name: digest(directory / name) for name in PAYLOADS},
        "scope": "internal bounded replay, not independent scientific validation",
    })
    return verify_packet(directory)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("build", "verify"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--lean", default="lean")
    args = parser.parse_args()
    try:
        result = build(args.directory, args.lean) if args.operation == "build" else verify_packet(args.directory)
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"Replay packet failed: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
