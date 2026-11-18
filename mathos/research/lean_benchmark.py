"""Check trusted Lean candidates against fixed tasks and replay the resulting record."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory

ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
NO_AXIOMS = "'MathOSBenchmarkCandidate' does not depend on any axioms"
AXIOMS = re.compile(r"'MathOSBenchmarkCandidate' depends on axioms: \[([^\]]*)\]")


def digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()


def audit(output):
    lines = {line.strip() for line in output.splitlines()}
    if any(line.endswith(NO_AXIOMS) for line in lines):
        return []
    for line in sorted(lines):
        match = AXIOMS.search(line)
        if match:
            return sorted(axiom.strip() for axiom in match[1].split(","))
    return None


def validate(spec):
    if not isinstance(spec, dict) or spec.get("schema") != 1:
        raise ValueError("Expected benchmark schema 1")
    version = spec.get("lean_version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Specify an exact Lean release")
    tasks = spec.get("tasks")
    systems = spec.get("systems")
    if not isinstance(tasks, dict) or not tasks or not isinstance(systems, dict) or not systems:
        raise ValueError("At least one task and system are required")
    if any(not isinstance(statement, str) or not statement.strip() for statement in tasks.values()):
        raise ValueError("Every task requires a Lean proposition")
    for submissions in systems.values():
        if not isinstance(submissions, dict) or submissions.keys() - tasks.keys():
            raise ValueError("Every submission must refer to a defined task")
        if any(not isinstance(script, str) or not script.strip() for script in submissions.values()):
            raise ValueError("Every submitted proof requires a tactic script")


def check(lean, workdir, statement, tactics):
    body = "\n".join("  " + line for line in tactics.splitlines())
    source = (
        "set_option warningAsError true\n"
        "set_option maxHeartbeats 200000\n"
        f"theorem MathOSBenchmarkCandidate : ({statement}) := by\n{body}\n"
        "#print axioms MathOSBenchmarkCandidate\n"
    )
    (workdir / "Candidate.lean").write_text(source, encoding="utf-8")
    record = {"source_sha256": sha256(source.encode()).hexdigest()}
    try:
        result = subprocess.run([lean, "Candidate.lean"], cwd=workdir, capture_output=True,
                                text=True, timeout=20, env={
                                    key: value for key, value in os.environ.items()
                                    if key != "LEAN_PATH"
                                })
    except subprocess.TimeoutExpired:
        return dict(record, outcome="timeout")
    output = result.stdout + result.stderr
    axioms = audit(output)
    if result.returncode != 0:
        return dict(record, outcome="lean_error", diagnostics=output)
    if axioms is None or set(axioms) - ALLOWED_AXIOMS:
        return dict(record, outcome="axiom_policy_failure", axioms=axioms, diagnostics=output)
    return dict(record, outcome="checked", axioms=axioms)


def run(spec, lean="lean"):
    validate(spec)
    executable = shutil.which(lean)
    if executable is None:
        raise ValueError("Lean executable not found")
    executable = os.path.abspath(executable)
    version = subprocess.run([executable, "--version"], capture_output=True, text=True,
                             check=True, timeout=20).stdout.strip()
    match = re.match(r"Lean \(version ([^, )]+)", version)
    if match is None or match[1] != spec["lean_version"]:
        raise ValueError(f"Unexpected Lean version: {version}")
    results = {}
    with TemporaryDirectory(prefix="mathos-lean-") as directory:
        for name, submissions in sorted(spec["systems"].items()):
            trials = {}
            for task, statement in sorted(spec["tasks"].items()):
                if task not in submissions:
                    trials[task] = {"outcome": "missing"}
                    continue
                with TemporaryDirectory(dir=directory) as trial:
                    trials[task] = check(executable, Path(trial), statement, submissions[task])
            results[name] = {
                "checked": sum(row["outcome"] == "checked" for row in trials.values()),
                "total": len(trials),
                "trials": trials,
            }
    payload = {"schema": 1, "benchmark": spec, "toolchain": version, "results": results}
    return dict(payload, sha256=digest(payload))


def comparable(results):
    return {
        system: {
            task: {key: value for key, value in record.items() if key != "diagnostics"}
            for task, record in report["trials"].items()
        }
        for system, report in results.items()
    }


def replay(bundle, lean="lean"):
    payload = {key: value for key, value in bundle.items() if key != "sha256"}
    if bundle.get("sha256") != digest(payload) or payload.get("schema") != 1:
        raise ValueError("Invalid run bundle or checksum")
    rerun = run(payload["benchmark"], lean)
    return {
        "reproduced": rerun["toolchain"] == payload["toolchain"]
        and comparable(rerun["results"]) == comparable(payload["results"]),
        "original_sha256": bundle["sha256"],
        "rerun_sha256": rerun["sha256"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("run", "replay"))
    parser.add_argument("input", type=Path)
    parser.add_argument("--lean", default="lean")
    args = parser.parse_args()
    try:
        value = json.loads(args.input.read_text(encoding="utf-8"))
        result = run(value, args.lean) if args.operation == "run" else replay(value, args.lean)
    except (ValueError, OSError, subprocess.SubprocessError, TypeError, KeyError, AttributeError) as error:
        parser.exit(2, f"{error}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(result.get("reproduced") is False)


if __name__ == "__main__":
    raise SystemExit(main())
