"""Pinned Lean kernel replay of independently typed finite TECT-X deductions.

Checks a tracked Lean proof against a separately authored theorem-type
contract, prints transitive axioms, and refuses non-pinned toolchains.
A successful replay establishes ONLY the stated finite F2 graph propositions.
It does NOT validate author-supplied proof routes or prove RH/BSD/Selmer.

Lean evaluates code during checking. Execute only in a disposable,
network-isolated environment with no secrets and audited toolchain supply.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any

from mathos.research.tect_x_thematic_gate import ROOT, evaluate_register
from mathos.research.tect_x_intelligent_proof_verifier import (
    CASES_PATH, verify_cases,
)

MANIFEST_PATH = ROOT / "docs/research/TECT_X_FORMAL_CERTIFICATES.v1.json"
LEAN_VERSION = "4.14.0"
CERTIFICATE_ID = "TECTX-F2-CHAIN-001"
SOURCE = "formal/TECTXFiniteTopology.lean"
CONTRACT = "formal/TECTXFiniteTopologyContract.lean"
THEOREMS = (
    "MathOS.TECTX.square_cycle_iff",
    "MathOS.TECTX.path_cycle_iff",
    "MathOS.TECTX.triangle_boundary_squared_zero",
    "MathOS.TECTX.triangle_kernel_is_face_image",
)
VERSION_RE = re.compile(r"^Lean \(version ([^, )]+)", re.MULTILINE)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_manifest(raw: Any, root: Path = ROOT) -> dict[str, Any]:
    """Static provenance and scope validation. No statement is proved here."""
    failures: list[str] = []
    result: dict[str, Any] = {
        "schema_version": "1.0",
        "certificate_id": CERTIFICATE_ID,
        "source_audit_passed": False,
        "kernel_checked": False,
        "semantic_link_to_conjecture_verified": False,
        "independent_human_review_completed": False,
        "closed_conjecture_obligations": [],
        "formal_status": "NOT_RUN",
        "failures": failures,
    }
    if not isinstance(raw, dict):
        failures.append("manifest must be an object")
        return result
    if raw.get("schema_version") != "1.0":
        failures.append("schema_version must be 1.0")
    backend = raw.get("backend")
    if not isinstance(backend, dict) or backend != {
        "system": "Lean",
        "version": LEAN_VERSION,
        "toolchain": "leanprover/lean4:v4.14.0",
        "standard_library": "Init",
        "network_required_for_check": False,
    }:
        failures.append("toolchain is not the approved pinned Lean/Init environment")
    if raw.get("trust_boundary") is None or not isinstance(raw.get("trust_boundary"), str):
        failures.append("an explicit trust boundary is required")
    certificate = raw.get("certificate")
    if not isinstance(certificate, dict):
        failures.append("certificate must be an object")
        return result
    if certificate.get("id") != CERTIFICATE_ID:
        failures.append("unsupported certificate id")
    if certificate.get("source") != SOURCE or certificate.get("independent_contract") != CONTRACT:
        failures.append("source and independently checked contract paths must be canonical")
    if certificate.get("proof_language") != "Lean 4":
        failures.append("proof_language must be Lean 4")
    if certificate.get("theorem_names") != list(THEOREMS):
        failures.append("theorem declarations must exactly match the independently typed contract")
    if certificate.get("permitted_transitive_axioms") != []:
        failures.append("transitive axioms are not allowed for this finite proof")
    if not isinstance(certificate.get("explicit_model_assumptions"), list) or len(certificate["explicit_model_assumptions"]) < 4:
        failures.append("explicit mathematical model assumptions are required")
    if certificate.get("external_review") != "NOT_PERFORMED":
        failures.append("external human review must not be self-certified")
    if certificate.get("formal_claim_status") != "PENDING_ACTUAL_KERNEL_REPLAY":
        failures.append("static manifest cannot claim a completed kernel replay")
    if certificate.get("closes_mathematical_obligation_ids") != []:
        failures.append("finite graph certificates cannot close open conjecture obligations")
    for key in ("proof_of_rh", "proof_of_bsd", "proof_of_selmer_infinitude"):
        if certificate.get(key) is not False:
            failures.append(f"unsupported conjecture proof claim: {key}")

    try:
        originals = {}
        for path in (SOURCE, CONTRACT):
            originals[path] = (root / path).read_bytes()
            result[path + "_sha256"] = _sha(originals[path])
        ctext = originals[CONTRACT].decode("utf-8")
        stext = originals[SOURCE].decode("utf-8")
        if "import TECTXFiniteTopology" not in ctext or "import Init" not in stext:
            failures.append("separate proof module and independent Init contract imports required")
        for name in THEOREMS:
            if ctext.count("#print axioms " + name) != 1:
                failures.append(f"missing or repeated transitive axiom command for {name}")
        if "#print axioms" not in ctext:
            failures.append("explicit axiom audit absent")
        # Static text screening is defense in depth; the real gate is the
        # kernel and an unambiguous no-axiom report for the imported theorems.
        for forbidden in ("sorry", "admit", "axiom ", "unsafe ", "native_decide", "decide +native", "#eval"):
            if forbidden in stext or forbidden in ctext:
                failures.append(f"prohibited source token: {forbidden}")
    except (OSError, UnicodeError) as exc:
        failures.append(f"cannot read trusted formal source files: {exc}")

    try:
        thematic = json.loads((root / "docs/research/TECT_X_THEMATIC_REGISTER.v1.json").read_text(encoding="utf-8"))
        t = evaluate_register(thematic, root)
        if not t["ok"]:
            failures.append("thematic evidence gate failed")
        cases = json.loads((root / CASES_PATH).read_text(encoding="utf-8"))
        graph = verify_cases(cases, root)
        if not graph["ok"] or graph["scientific_certification"]:
            failures.append("TGA proof gaps not safely blocked")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        failures.append(f"cannot validate independent TGA and research status: {exc}")

    result["source_audit_passed"] = not failures
    return result


def _extract_axiom_reports(stdout: str) -> dict[str, list[str]]:
    """Parse each named Lean #print axioms result once, disallow ambiguity."""
    found: dict[str, list[str]] = {}
    for name in THEOREMS:
        hits = [line.strip() for line in stdout.splitlines() if f"'{name}' " in line
                and ("does not depend on any axioms" in line or "depends on axioms:" in line)]
        if len(hits) != 1:
            raise ValueError(f"missing or ambiguous Lean axiom report: {name}")
        line = hits[0]
        if f"'{name}' does not depend on any axioms" in line:
            found[name] = []
            continue
        match = re.search(r"depends on axioms:\s*\[([^\]]*)\]", line)
        if match is None:
            raise ValueError(f"unparseable transitive axioms for {name}")
        used = [v.strip() for v in match.group(1).split(",") if v.strip()]
        if len(used) != len(set(used)):
            raise ValueError(f"duplicated transitive axiom name for {name}")
        if used:
            raise ValueError(f"unapproved transitive axioms for {name}: {used}")
        # Even the empty [...] form is unexpected: the canonical Lean output
        # says 'does not depend on any axioms'.
        raise ValueError(f"unexpected axiom report format for {name}")
    return found


def run_kernel(root: Path = ROOT, executable: str = "lean",
               artifact_dir: Path | None = None) -> dict[str, Any]:
    """Compile source and an independent type contract under pinned Lean."""
    version = subprocess.run(
        [executable, "--version"], capture_output=True, text=True,
        timeout=20, check=False,
    )
    match = VERSION_RE.search(version.stdout)
    if version.returncode or not match or match.group(1) != LEAN_VERSION:
        raise ValueError("pinned Lean 4.14.0 toolchain required")
    originals = {name: (root / name).read_bytes() for name in (SOURCE, CONTRACT)}
    with tempfile.TemporaryDirectory(prefix="mathos-tectx-lean-") as temp:
        work = Path(temp)
        for name, data in originals.items():
            (work / Path(name).name).write_bytes(data)
        env = os.environ.copy()
        env["LEAN_PATH"] = str(work)
        build = subprocess.run(
            [executable, "-o", str(work / "TECTXFiniteTopology.olean"),
             str(work / "TECTXFiniteTopology.lean")],
            cwd=work, env=env, capture_output=True, text=True,
            timeout=120, check=False,
        )
        if build.returncode or "warning:" in build.stdout + build.stderr:
            raise ValueError("Lean rejected formal proof module: " + (build.stdout + build.stderr)[-2400:])
        probe = subprocess.run(
            [executable, str(work / "TECTXFiniteTopologyContract.lean")],
            cwd=work, env=env, capture_output=True, text=True,
            timeout=120, check=False,
        )
        if probe.returncode or "warning:" in probe.stdout + probe.stderr:
            raise ValueError("Lean rejected independent theorem-type contract: " + (probe.stdout + probe.stderr)[-2400:])
        verified_axioms = _extract_axiom_reports(probe.stdout)
        if not (work / "TECTXFiniteTopology.olean").is_file():
            raise ValueError("Lean did not create the expected compiled proof module")
        for name, original in originals.items():
            if (root / name).read_bytes() != original:
                raise ValueError("formal source changed while checking")
            if (work / Path(name).name).read_bytes() != original:
                raise ValueError("source changed inside verification directory")
        if artifact_dir is not None:
            artifact_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(work / "TECTXFiniteTopology.olean",
                            artifact_dir / "TECTXFiniteTopology.olean")

    return {
        "formal_status": "LEAN_KERNEL_CHECKED_FINITE_F2_DEDUCTIONS_ONLY",
        "kernel_checked": True,
        "independent_type_contract_checked": True,
        "exact_lean_version": version.stdout.strip().splitlines()[0],
        "trusted_toolchain_id": "leanprover/lean4:v4.14.0",
        "verified_theorems": list(THEOREMS),
        "transitive_axioms": verified_axioms,
        "verified_scope": "Only the four concrete finite F2 graph chain lemmas",
        "semantic_link_to_conjecture_verified": False,
        "independent_human_review_completed": False,
        "closed_conjecture_obligations": [],
        "source_sha256": _sha(originals[SOURCE]),
        "independent_contract_sha256": _sha(originals[CONTRACT]),
    }


def audit(*, root: Path = ROOT, check_kernel: bool = False,
          executable: str = "lean", artifact_dir: Path | None = None) -> dict[str, Any]:
    raw = json.loads((root / "docs/research/TECT_X_FORMAL_CERTIFICATES.v1.json").read_text(encoding="utf-8"))
    report = validate_manifest(raw, root)
    if not report["source_audit_passed"]:
        return report
    if check_kernel:
        try:
            report.update(run_kernel(root=root, executable=executable,
                                     artifact_dir=artifact_dir))
        except (OSError, subprocess.SubprocessError, ValueError, UnicodeError) as exc:
            report["failures"].append(f"Lean verification failed: {exc}")
            report["formal_status"] = "KERNEL_CHECK_FAILED"
            report["kernel_checked"] = False
    report["ok"] = report["source_audit_passed"] and (not check_kernel or report["kernel_checked"])
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-lean", action="store_true", help="actually run the pinned Lean kernel and independent contract")
    parser.add_argument("--lean", default="lean", help="path to the pinned Lean executable")
    parser.add_argument("--report", type=Path, help="write deterministic JSON assurance status")
    parser.add_argument("--artifact-dir", type=Path, help="preserve a compiled .olean only after successful kernel replay")
    args = parser.parse_args(argv)
    try:
        report = audit(check_kernel=args.check_lean,
                       executable=args.lean, artifact_dir=args.artifact_dir)
    except (OSError, ValueError, TypeError) as exc:
        report = {
            "ok": False, "formal_status": "INVALID_INPUT", "kernel_checked": False,
            "closed_conjecture_obligations": [], "failures": [str(exc)]
        }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
