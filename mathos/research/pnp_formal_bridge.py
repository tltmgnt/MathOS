"""Independent Lean check of the fixed two-variable unsigned-primal boundary.

Not a verifier of arbitrary generated source, Python correctness or P vs NP.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

SOURCE = Path(__file__).resolve().parents[2] / "formal" / "PnpConvergenceBoundary.lean"
LEAN_VERSION = "4.14.0"
THEOREMS = ("samePrimal", "satWitness", "unsatAll", "unsignedGraphInsufficient")


def check_boundary(executable="lean"):
    source = SOURCE.read_bytes()
    try:
        version = subprocess.run([executable, "--version"], capture_output=True,
                                 text=True, timeout=20)
        match = re.search(r"Lean \(version ([^, )]+)", version.stdout)
        if version.returncode or not match or match.group(1) != LEAN_VERSION:
            raise ValueError("Lean 4.14.0 required")
        checked = subprocess.run([executable, "-DwarningAsError=true", str(SOURCE)],
                                 capture_output=True, text=True, timeout=90)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("Lean unavailable or timed out") from exc
    diagnostics = checked.stdout + checked.stderr
    lines = {line.strip() for line in diagnostics.splitlines()}
    if checked.returncode or any(
        f"'PnpConvergenceBoundary.{name}' does not depend on any axioms" not in lines
        for name in THEOREMS
    ):
        raise ValueError("Lean rejected proof or axiom policy: " + diagnostics[:2000])
    if SOURCE.read_bytes() != source:
        raise ValueError("proof source changed during verification")
    return {"schema": "mathos-pnp-convergence-lean/1", "lean_version": LEAN_VERSION,
            "source_sha256": hashlib.sha256(source).hexdigest(), "theorems": THEOREMS,
            "lean_kernel_checked": True, "axioms": [],
            "verified_scope": "concrete two-variable CNF pair has identical unsigned primal adjacency and opposite satisfiability",
            "python_implementation_verified": False, "universal_obligation": "unresolved",
            "p_equals_np_established": False, "p_not_equals_np_established": False}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lean", default="lean")
    a = p.parse_args(argv)
    try:
        r = check_boundary(a.lean)
    except (OSError, ValueError) as exc:
        p.exit(1, str(exc) + "\n")
    print(json.dumps(r, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
