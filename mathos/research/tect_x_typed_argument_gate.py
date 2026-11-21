"""Typed mathematical argument certificates for TECT-X (Lean 4.14).

Accepts repository-reviewed Lean formalizations and a separately authored
exact-goal reference file. Checks candidate proof terms against that formal
goal using the Lean kernel, with a strict zero-transitive-axiom policy.

It cannot independently interpret arbitrary natural language mathematics,
prove that a reference proposition captures its informal statement, or
validate a user-authored research proof-route implication. Those are
explicit unresolved semantic bridges, even after a successful kernel run.

Executing Lean source can execute metaprograms. This runner is for reviewed
repository-controlled source only, in disposable environments without secrets.
Do not offer it as a safe arbitrary code-execution service.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
from typing import Any

from mathos.research.tect_x_thematic_gate import ROOT

MANIFEST = ROOT / "docs/research/TECT_X_TYPED_ARGUMENTS.v1.json"
PIN = "4.14.0"
MAX_BUNDLES = 12
MAX_LEAN_FILE_BYTES = 65536
REGISTRY_SCOPE = "REPOSITORY_REVIEWED_LEAN_FORMALIZATIONS_ONLY"
NAME_RE = re.compile(r"[A-Z][A-Za-z0-9_]{0,63}\.lean\Z")
ID_RE = re.compile(r"[a-z][a-z0-9-]{0,50}\Z")
THEOREM_RE = re.compile(r"MathOS\.TECTX\.(?:Arguments|Contracts)\.[a-z][A-Za-z0-9_]*\Z")
VERSION = re.compile(r"^Lean \(version ([^, )]+)", re.MULTILINE)
SOURCE_KEYS = {
    "id", "source", "contract", "candidate_theorem", "contract_theorem",
    "informal_claim", "explicit_hypotheses", "formal_scope", "semantic_gap",
    "review_status", "conjecture_implication"
}
TOP_KEYS = {
    "schema_version", "system", "backend", "validation_scope",
    "meaning_of_pass", "scientific_claim_certification",
    "language_to_formal_statement_review", "independent_expert_review",
    "closed_research_obligations", "bundles",
}
FORBIDDEN = re.compile(
    r"\b(?:sorry|admit|axiom|opaque|unsafe|run_tac|elab|macro_rules|"
    r"native_decide|initialize|set_option\s+autoImplicit)\b|"
    r"#(?:eval|reduce|check_failure)\b"
)


def _sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _safe_source_path(value: Any, prefix: str) -> str:
    if not isinstance(value, str) or "\\" in value or value.startswith("/"):
        raise ValueError("invalid or unsafe formal path")
    p = PurePosixPath(value)
    if (p.as_posix() != value or len(p.parts) != 3 or
            p.parts[:2] != ("formal", prefix) or
            not NAME_RE.fullmatch(p.name) or
            any(part in {".", ".."} for part in value.split("/"))):
        raise ValueError("formal sources must be safe paths under formal/" + prefix)
    return value


def _required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 3000:
        raise ValueError(f"{label} is missing or exceeds its text limit")
    return value


def validate_manifest(raw: Any, root: Path = ROOT) -> dict[str, Any]:
    """Validate manifest/provenance without asserting any formal verification."""
    if not isinstance(raw, dict) or set(raw) != TOP_KEYS:
        raise ValueError("invalid top-level proof registry schema")
    if (raw["schema_version"] != "1.0" or raw["system"] != "TECT-X independent typed argument gate" or
            raw["backend"] != {
                "name": "Lean", "version": PIN, "stdlib": "Init",
                "require_zero_transitive_axioms": True,
            } or raw["validation_scope"] != REGISTRY_SCOPE):
        raise ValueError("unsupported schema, toolchain or validation scope")
    _required_text(raw["meaning_of_pass"], "meaning_of_pass")
    if (raw["scientific_claim_certification"] is not False or
            raw["language_to_formal_statement_review"] != "NOT_PERFORMED" or
            raw["independent_expert_review"] != "NOT_PERFORMED" or
            raw["closed_research_obligations"] != []):
        raise ValueError("unreviewed mathematical claims cannot be promoted")

    bundles = raw["bundles"]
    if not isinstance(bundles, list) or not 1 <= len(bundles) <= MAX_BUNDLES:
        raise ValueError("proof bundle count is outside review limits")
    ids: set[str] = set()
    paths: set[str] = set()
    theorems: set[str] = set()
    results: list[dict[str, Any]] = []
    for bundle in bundles:
        if not isinstance(bundle, dict) or set(bundle) != SOURCE_KEYS:
            raise ValueError("invalid proof bundle schema")
        bundle_id = bundle["id"]
        if not isinstance(bundle_id, str) or not ID_RE.fullmatch(bundle_id) or bundle_id in ids:
            raise ValueError("invalid or duplicate bundle id")
        ids.add(bundle_id)
        src = _safe_source_path(bundle["source"], "tectx_arguments")
        contract = _safe_source_path(bundle["contract"], "tectx_contracts")
        if src in paths or contract in paths:
            raise ValueError("the same source file cannot be assigned to multiple bundles")
        paths.update((src, contract))
        theorem = bundle["candidate_theorem"]
        contract_theorem = bundle["contract_theorem"]
        if (not isinstance(theorem, str) or not THEOREM_RE.fullmatch(theorem) or
                not theorem.startswith("MathOS.TECTX.Arguments.") or
                not isinstance(contract_theorem, str) or
                not THEOREM_RE.fullmatch(contract_theorem) or
                not contract_theorem.startswith("MathOS.TECTX.Contracts.") or
                theorem in theorems or contract_theorem in theorems):
            raise ValueError("invalid or duplicate Lean theorem name")
        theorems.update((theorem, contract_theorem))
        for field in ("informal_claim", "formal_scope", "semantic_gap"):
            _required_text(bundle[field], field)
        hypotheses = bundle["explicit_hypotheses"]
        if (not isinstance(hypotheses, list) or not hypotheses or
                len(hypotheses) > 20):
            raise ValueError("formal hypotheses must be explained explicitly")
        for item in hypotheses:
            _required_text(item, "formal hypothesis")
        if (bundle["review_status"] != "NOT_REVIEWED" or
                bundle["conjecture_implication"] != "NONE"):
            raise ValueError("cannot self-certify statement faithfulness or a research result")
        try:
            sbytes = (root / src).read_bytes()
            cbytes = (root / contract).read_bytes()
        except OSError as exc:
            raise ValueError(f"missing argument/contract file for {bundle_id}: {exc}") from exc
        if any(len(data) > MAX_LEAN_FILE_BYTES for data in (sbytes, cbytes)):
            raise ValueError("proof file exceeds the trusted source size bound")
        try:
            source_text, contract_text = sbytes.decode("utf-8"), cbytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("formal files must use UTF-8") from exc
        if (source_text.splitlines()[0].strip() != "import Init" or
                contract_text.splitlines()[0].strip() != "import " + PurePosixPath(src).stem):
            raise ValueError("proof and contract must have pinned, distinct imports")
        # Prevent unlisted extra imports: the trusted environment is core Init
        # plus exactly the candidate module. This is defense-in-depth, NOT a
        # security sandbox or a general Lean parser.
        if len(re.findall(r"(?m)^\s*import\s+", source_text)) != 1:
            raise ValueError("proof source must import Init only")
        if len(re.findall(r"(?m)^\s*import\s+", contract_text)) != 1:
            raise ValueError("proof contract must import candidate module only")
        if FORBIDDEN.search(source_text) or FORBIDDEN.search(contract_text):
            raise ValueError("disallowed proof bypass or metaprogram token in reviewed source")
        if "set_option warningAsError true" not in source_text or "set_option warningAsError true" not in contract_text:
            raise ValueError("warningAsError required for the proof and contract")
        for name in (theorem, contract_theorem):
            if contract_text.count("#print axioms " + name) != 1:
                raise ValueError(f"exactly one transitive axiom report is required for {name}")
        if contract_text.count("#print axioms ") != 2:
            raise ValueError("proof contract must audit exactly the declared pair of theorem names")
        results.append({
            "id": bundle_id, "source": src, "contract": contract,
            "candidate_theorem": theorem, "contract_theorem": contract_theorem,
            "informal_claim": bundle["informal_claim"],
            "explicit_hypotheses": hypotheses,
            "formal_scope": bundle["formal_scope"],
            "source_sha256": _sha(sbytes), "contract_sha256": _sha(cbytes),
            "statement_faithfulness": "UNREVIEWED",
            "semantic_gap": bundle["semantic_gap"],
            "mathematical_verification": "NOT_RUN",
            "kernel_checked": False,
        })
    return {
        "ok": True,
        "schema_version": "1.0",
        "validation_scope": REGISTRY_SCOPE,
        "kernel_checked": False,
        "semantic_faithfulness_certified": False,
        "independent_expert_review_completed": False,
        "scientific_claim_certification": False,
        "closed_research_obligations": [],
        "gaps": [
            {
                "id": "GAP.LANGUAGE_TO_FORMAL_REFERENCE",
                "status": "OPEN_REQUIRES_INDEPENDENT_SEMANTIC_REVIEW",
                "description": "No kernel can establish correspondence to unrestricted human-language intent without an independently justified interpretation.",
            },
            {
                "id": "GAP.AUTHORED_PROOF_ROUTE_SUFFICIENCY",
                "status": "OPEN_REQUIRES_MATHEMATICAL_PROOF",
                "description": "A checked local deduction does not validate all upstream/downstream edges in a TGA proof-obligation model.",
            },
            {
                "id": "GAP.EXTERNAL_REPRODUCTION",
                "status": "NOT_INDEPENDENTLY_REPLAYED",
                "description": "In-repository CI is not independent external proof review or attested supply-chain provenance.",
            },
        ],
        "bundles": results,
        "formal_status": "SOURCE_CONTRACT_VALIDATED_KERNEL_NOT_RUN",
    }


def _axiom_report(output: str, theorem: str) -> list[str]:
    matches = [
        line.strip() for line in output.splitlines()
        if f"'{theorem}' " in line and
        ("does not depend on any axioms" in line or "depends on axioms:" in line)
    ]
    if len(matches) != 1 or f"'{theorem}' does not depend on any axioms" not in matches[0]:
        raise ValueError(f"missing, ambiguous or nonempty transitive axioms for {theorem}")
    return []


def _replay_one(source: bytes, contract: bytes, *, source_module: str,
                candidate_theorem: str, contract_theorem: str,
                lean: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="mathos-tectx-typed-proof-") as temp:
        root = Path(temp)
        source_path = root / (source_module + ".lean")
        contract_path = root / (source_module + "Contract.lean")
        source_path.write_bytes(source)
        contract_path.write_bytes(contract)
        env = os.environ.copy()
        env["LEAN_PATH"] = str(root)
        compiler = subprocess.run(
            [lean, "-o", str(root / (source_module + ".olean")), str(source_path)],
            cwd=root, env=env, capture_output=True, text=True,
            timeout=120, check=False,
        )
        if compiler.returncode or "warning:" in compiler.stdout + compiler.stderr:
            raise ValueError("Lean rejected proof source: " + (compiler.stdout + compiler.stderr)[-2000:])
        contract_check = subprocess.run(
            [lean, str(contract_path)], cwd=root, env=env,
            capture_output=True, text=True, timeout=120, check=False,
        )
        if contract_check.returncode or "warning:" in contract_check.stdout + contract_check.stderr:
            raise ValueError("independent formal goal contract failed: " +
                             (contract_check.stdout + contract_check.stderr)[-2000:])
        axioms = {
            candidate_theorem: _axiom_report(contract_check.stdout, candidate_theorem),
            contract_theorem: _axiom_report(contract_check.stdout, contract_theorem),
        }
        if source_path.read_bytes() != source or contract_path.read_bytes() != contract:
            raise ValueError("formal files changed during kernel replay")
        if not (root / (source_module + ".olean")).is_file():
            raise ValueError("proof module kernel compilation produced no .olean")
        return {"transitive_axioms": axioms, "contract_kernel_checked": True}


def replay(raw: Any, *, root: Path = ROOT, check_lean: bool = False,
           lean: str = "lean") -> dict[str, Any]:
    """Formal correctness relative to exact typed reference, not English."""
    report = validate_manifest(raw, root)
    if not check_lean:
        return report
    try:
        version = subprocess.run(
            [lean, "--version"], capture_output=True, text=True,
            timeout=20, check=False,
        )
        match = VERSION.search(version.stdout)
        if version.returncode or not match or match.group(1) != PIN:
            raise ValueError("Lean 4.14.0 is required")
        for bundle in report["bundles"]:
            sb = (root / bundle["source"]).read_bytes()
            cb = (root / bundle["contract"]).read_bytes()
            if _sha(sb) != bundle["source_sha256"] or _sha(cb) != bundle["contract_sha256"]:
                raise ValueError("source changed after validation")
            checked = _replay_one(
                sb, cb, source_module=Path(bundle["source"]).stem,
                candidate_theorem=bundle["candidate_theorem"],
                contract_theorem=bundle["contract_theorem"], lean=lean,
            )
            if (_sha((root / bundle["source"]).read_bytes()) != bundle["source_sha256"] or
                    _sha((root / bundle["contract"]).read_bytes()) != bundle["contract_sha256"]):
                raise ValueError("source changed during proof replay")
            bundle.update({
                "mathematical_verification": "KERNEL_CHECKED_EXACT_FORMAL_GOAL",
                "kernel_checked": True,
                **checked,
            })
        report["kernel_checked"] = True
        report["lean_version"] = version.stdout.strip().splitlines()[0]
        report["formal_status"] = "LEAN_KERNEL_CHECKED_TYPED_DEDUCTIONS_ONLY"
    except (OSError, ValueError, subprocess.SubprocessError, UnicodeError) as exc:
        report["ok"] = False
        report["kernel_checked"] = False
        report["formal_status"] = "KERNEL_CHECK_FAILED"
        report["failure"] = str(exc)
        # A batch can only be certified when every formal bundle passes.
        # Prior local successes are retained as diagnostics, not promoted.
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--check-lean", action="store_true")
    parser.add_argument("--lean", default="lean")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.manifest.stat().st_size > 131072:
            raise ValueError("registry exceeds size bound")
        raw = json.loads(args.manifest.read_text(encoding="utf-8"))
        report = replay(raw, check_lean=args.check_lean, lean=args.lean)
    except (OSError, ValueError, TypeError, KeyError, IndexError, RecursionError) as exc:
        report = {
            "ok": False, "kernel_checked": False, "formal_status": "INVALID_INPUT",
            "semantic_faithfulness_certified": False,
            "closed_research_obligations": [], "failure": str(exc),
        }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
