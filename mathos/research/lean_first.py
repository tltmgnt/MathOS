"""Lean-first, fail-closed verification gate for explicitly registered subresults.

Python may discover or propose arguments; only a pinned Lean replay may mark
an exact formal proposition KERNEL_CHECKED_SCOPE_ONLY. No result here certifies
the informal research claim, an external review, or an open conjecture.

The v1 registry deliberately supports self-contained Lean files importing at
most Init. Enlarging the trusted import closure requires a separate audit.
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
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "docs/research/LEAN_FIRST_CLAIMS.v1.json"
LEAN_VERSION = "4.14.0"
ALLOWED_AXIOMS = frozenset({"propext", "Classical.choice", "Quot.sound"})
POLICY = {
    "allowed_axioms": sorted(ALLOWED_AXIOMS),
    "automatic_claim_promotion": False,
    "informal_statement_fidelity": "REQUIRES_INDEPENDENT_REVIEW",
}
CLAIM_KEYS = {
    "claim_id", "source", "theorem", "expected_type", "research_claim",
    "scope", "limitations", "statement_review", "external_review",
    "proves_open_problem",
}
SOURCE_RE = re.compile(r"formal/[A-Za-z][A-Za-z0-9_]*\.lean\Z")
NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*\Z")
ID_RE = re.compile(r"[A-Z][A-Z0-9_]{1,39}\Z")
VERSION_RE = re.compile(r"^Lean \(version 4\.14\.0(?:,|\))")


def _keys(value: object, expected: set[str], label: str) -> dict:
    if type(value) is not dict or set(value) != expected:
        raise ValueError(f"{label}: expected fields {sorted(expected)}")
    return value


def _registry(path: Path) -> list[dict]:
    document = _keys(
        json.loads(path.read_text(encoding="utf-8")),
        {"schema_version", "lean_version", "policy", "claims"},
        "Lean-first registry",
    )
    if (document["schema_version"] != 1 or
            document["lean_version"] != LEAN_VERSION or
            document["policy"] != POLICY):
        raise ValueError("Lean-first registry has a changed toolchain or trust policy")
    claims = document["claims"]
    if type(claims) is not list or not claims or len(claims) > 40:
        raise ValueError("Lean-first registry must contain 1 to 40 claims")
    seen_ids: set[str] = set()
    seen_theorems: set[str] = set()
    for claim in claims:
        _keys(claim, CLAIM_KEYS, "claim")
        claim_id, theorem, source = (
            claim["claim_id"], claim["theorem"], claim["source"]
        )
        if (type(claim_id) is not str or not ID_RE.fullmatch(claim_id) or
                claim_id in seen_ids):
            raise ValueError("unsafe or duplicate claim id")
        if (type(theorem) is not str or not NAME_RE.fullmatch(theorem) or
                theorem in seen_theorems):
            raise ValueError("unsafe or duplicate theorem name")
        if type(source) is not str or not SOURCE_RE.fullmatch(source):
            raise ValueError("Lean file must be a direct, named formal/*.lean source")
        for field in ("research_claim", "scope", "limitations"):
            text = claim[field]
            if type(text) is not str or not 30 <= len(text.strip()) <= 3000:
                raise ValueError(f"{claim_id}: missing substantive {field}")
        lean_type = claim["expected_type"]
        if (type(lean_type) is not str or not 15 <= len(lean_type) <= 4000 or
                any(piece in lean_type for piece in ("\r", "\n", "#", "--", "/-", "-/"))):
            raise ValueError(f"{claim_id}: unsafe expected Lean proposition")
        if (claim["statement_review"] != "PENDING" or
                claim["external_review"] != "PENDING" or
                claim["proves_open_problem"] is not False):
            raise ValueError(f"{claim_id}: unearned research or review status")
        seen_ids.add(claim_id)
        seen_theorems.add(theorem)
    return claims


def _source(root: Path, relative_path: str) -> tuple[Path, bytes]:
    path = root / relative_path
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"missing or symlinked Lean source: {relative_path}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Lean source escapes repository root")
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    # v1 pins the whole logical import closure to the Lean 4.14.0 core.
    imports = re.findall(r"(?m)^\s*import\s+([^\r\n]+)", text)
    if imports not in ([], ["Init"]):
        raise ValueError(f"{relative_path}: only the pinned Init import is supported")
    return path, raw


def _lean_executable(explicit: str | None) -> tuple[str, str]:
    lean = explicit or shutil.which("lean")
    if not lean:
        raise RuntimeError("Lean is unavailable; no kernel verification took place")
    try:
        version = subprocess.run(
            [lean, "--version"], capture_output=True, text=True,
            timeout=15, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("could not inspect Lean toolchain") from exc
    if version.returncode or not VERSION_RE.match(version.stdout):
        raise RuntimeError("verification requires the exact Lean 4.14.0 release")
    return lean, version.stdout.strip().splitlines()[0]


def _parse_axioms(output: str, theorem: str) -> list[str]:
    pattern = re.compile(
        rf"'{re.escape(theorem)}' (?:does not depend on any axioms|"
        rf"depends on axioms: \[([^\]]*)\])"
    )
    matches = list(pattern.finditer(output))
    if not matches:
        raise RuntimeError(f"Lean omitted the transitive axiom report for {theorem}")
    # Earlier source directives may also print axioms. Our appended audit is
    # last; this must be its report, not a message from the original source.
    match = matches[-1]
    if match.group(1) is None:
        return []
    names = [part.strip() for part in match.group(1).split(",")]
    if len(names) != len(set(names)) or any(name not in ALLOWED_AXIOMS for name in names):
        raise RuntimeError(f"{theorem} depends on unapproved or malformed axioms: {names}")
    return sorted(names)


def _replay(lean: str, root: Path, claim: dict, original: bytes) -> dict:
    theorem = claim["theorem"]
    # The example forces the named proof to inhabit the explicitly registered
    # proposition. Compilation alone would not establish this link.
    witness = (
        "\n\n-- Independently checked MathOS claim-to-proposition witness.\n"
        f"example : {claim['expected_type']} := by\n"
        f"  exact {theorem}\n"
        f"#print axioms {theorem}\n"
    )
    with TemporaryDirectory(prefix="mathos-lean-claim-") as directory:
        source = Path(directory) / "MathOSClaimAudit.lean"
        # Lean imports must precede ordinary commands such as set_option.
        body = original.decode("utf-8")
        if body.startswith("import Init\n"):
            body = "import Init\nset_option warningAsError true\n" + body[len("import Init\n"):]
        else:
            body = "set_option warningAsError true\n" + body
        source.write_text(body + witness, encoding="utf-8")
        try:
            replay = subprocess.run(
                [lean, str(source)], cwd=root, capture_output=True,
                text=True, timeout=120, check=False,
                env={key: value for key, value in os.environ.items()
                     if key != "LEAN_PATH"},
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError(f"{claim['claim_id']}: Lean replay failed") from exc
        if replay.returncode:
            raise RuntimeError(
                f"{claim['claim_id']}: Lean rejected the proposition or proof: "
                + (replay.stdout + replay.stderr)[-2500:]
            )
        axioms = _parse_axioms(replay.stdout, theorem)
        return {
            "status": "KERNEL_CHECKED_SCOPE_ONLY",
            "transitive_axioms": axioms,
            "audit_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        }


def audit_registry(
    registry_path: Path = DEFAULT_REGISTRY, *, root: Path = ROOT,
    verify_lean: bool = False, lean: str | None = None,
) -> dict:
    """Inspect metadata without Lean, or fail closed on any failed kernel replay."""
    root = root.resolve()
    original_manifest = registry_path.read_bytes()
    claims = _registry(registry_path)
    tool = _lean_executable(lean) if verify_lean else None
    result_claims = []
    for claim in claims:
        path, original = _source(root, claim["source"])
        checked = _replay(tool[0], root, claim, original) if tool else {
            "status": "NOT_RUN",
            "transitive_axioms": None,
            "audit_source_sha256": None,
        }
        if path.read_bytes() != original:
            raise RuntimeError("Lean source changed during claim audit")
        result_claims.append({
            "claim_id": claim["claim_id"],
            "theorem": claim["theorem"],
            "expected_type": claim["expected_type"],
            "source": claim["source"],
            "source_sha256": hashlib.sha256(original).hexdigest(),
            "research_claim": claim["research_claim"],
            "scope": claim["scope"],
            "limitations": claim["limitations"],
            "formal_result": checked,
            "statement_fidelity": "NOT_INDEPENDENTLY_REVIEWED",
            "external_mathematical_review": "NOT_PERFORMED",
            "proves_open_problem": False,
            "automatic_claim_promotion": False,
        })
    if registry_path.read_bytes() != original_manifest:
        raise RuntimeError("claim registry changed during verification")
    return {
        "schema_version": 1,
        "lean_version": tool[1] if tool else LEAN_VERSION + " (not run)",
        "registry_sha256": hashlib.sha256(original_manifest).hexdigest(),
        "checked_count": len(result_claims) if tool else 0,
        "claims": result_claims,
        "canonical_proof_certification": "NOT_CERTIFIED",
        "informal_statement_fidelity": "REQUIRES_INDEPENDENT_REVIEW",
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("inspect", "verify"))
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--lean", type=str, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        report = audit_registry(
            args.registry, verify_lean=args.action == "verify", lean=args.lean
        )
    except (ValueError, RuntimeError, OSError, UnicodeError) as exc:
        parser.exit(1, f"Lean-first gate failed: {exc}\n")
    serialized = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
