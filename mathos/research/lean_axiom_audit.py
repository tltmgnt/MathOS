"""Pinned Lean SAT1 transitive axiom audit.

Compilation alone does not expose transitive sorryAx/custom-axiom dependencies.
Require #print axioms MathOS.satSupport_certificate and reject every axiom
other than Lean's three standard logical axioms. This audits proof dependencies,
NOT informal statement faithfulness or external expert independence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from mathos.research.theorem_assurance import SAT_LEAN

TARGET = "MathOS.satSupport_certificate"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
NO_AXIOMS = re.compile(
    r"['`]?MathOS\.satSupport_certificate['`]?\s+does not depend on any axioms"
)
AXIOMS = re.compile(
    r"['`]?MathOS\.satSupport_certificate['`]?\s+depends on axioms:\s*\[([^\]]*)\]"
)


def parse_axiom_output(output: str) -> tuple[str, ...]:
    no_axioms = list(NO_AXIOMS.finditer(output))
    axioms = list(AXIOMS.finditer(output))
    if len(no_axioms) + len(axioms) != 1:
        raise ValueError("Lean output has no single unambiguous SAT1 axiom report")
    if no_axioms:
        return ()
    names = [name.strip() for name in axioms[0].group(1).split(",")]
    if len(names) != len(set(names)) or any(name not in ALLOWED for name in names):
        raise ValueError("theorem relies on a nonstandard or malformed axiom")
    return tuple(sorted(names))


def audit_axioms(source_path: Path = SAT_LEAN, *,
                 output_dir: Path | None = None) -> dict:
    original = source_path.read_bytes()
    src = original.decode("utf-8")
    if src.count("#print axioms MathOS.satSupport_certificate") != 1:
        raise ValueError("source must print the exact theorem's axiom dependencies")
    lean = shutil.which("lean")
    if lean is None:
        raise RuntimeError("pinned Lean 4.14.0 not found")
    ver = subprocess.run(
        [lean, "--version"], capture_output=True, text=True,
        timeout=15, check=False,
    )
    if ver.returncode or not ver.stdout.startswith("Lean (version 4.14.0"):
        raise RuntimeError("independent axiom audit requires pinned Lean 4.14.0")
    replay = subprocess.run(
        [lean, str(source_path)], capture_output=True, text=True,
        timeout=90, check=False,
    )
    if replay.returncode:
        raise RuntimeError("Lean theorem compilation failed")
    used = parse_axiom_output(replay.stdout)
    if source_path.read_bytes() != original:
        raise RuntimeError("proof source changed during Lean axiom audit")
    result = {
        "schema_version": "1.0.0",
        "theorem": TARGET,
        "formal_axiom_audit": "PASSED_WITH_ONLY_STANDARD_LEAN_AXIOMS",
        "transitive_axioms": list(used),
        "lean_version": ver.stdout.strip().splitlines()[0],
        "source_sha256": hashlib.sha256(original).hexdigest(),
        "proves_clay_problem": False,
        "proof_statement_faithfulness_externally_reviewed": False,
        "expert_independence_confirmed": False,
    }
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "sat1_axiom_audit.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/external-review"))
    args = parser.parse_args(argv)
    print(json.dumps(audit_axioms(output_dir=args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
