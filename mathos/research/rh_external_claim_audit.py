"""Audit a pinned *headline* of the November 2026 external RH Lean claim.

This checks small upstream source files against exact Git blob IDs and confirms
the declared target is Mathlib's RiemannHypothesis. It does NOT download or
replay the 175,187-module proof, nor upgrade MathOS's RH status.

python -m mathos.research.rh_external_claim_audit --fetch-pinned
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs/research/RH_EXTERNAL_CLAIM_2026.v1.json"
SCHEMA = "mathos.rh.external_claim_audit/1"
MIRROR_COMMIT = "7cbf7a0c32fca1badf05931879a37c3f8a2b03b4"
MATHLIB_COMMIT = "0df444a360eaa60ab8c11dca51a86af692955474"
MAX_SOURCE_BYTES = 80_000
SHA1 = {
    "src/Main.lean": "dbd5db70bc11b35f18fa5751216ab335321e7bfc",
    "src/Statements.lean": "1cd1bce93344065936b2b392b23306254e0785ef",
    "src/Supplements/Kernels/MainTheorems.lean": "6a542d7ce969a791fd12ce575f587e6bc29044bf",
    "lean-toolchain": "a8afa7d1b02d96f0671eba854a8dc4b416beb473",
    "lakefile.toml": "07e85dc8afcf28b4885a8f092154c8b74c8cf800",
    "Mathlib/NumberTheory/LSeries/RiemannZeta.lean":
        "3c92195fce20df7fda41cfd823b3266f83cf3070",
}
THEOREMS = (
    "riemannHypothesis",
    "riemannZeta_eq_zero_re",
    "LFunction_ne_zero_of_half_lt_re",
    "LFunction_eq_zero_re",
    "LFunction_eq_zero_re_of_isPrimitive",
)
STANDARD_AXIOMS = ("propext", "Classical.choice", "Quot.sound")
MIT_SOURCE = "https://math.mit.edu/~drew/grh/"


class AuditError(ValueError):
    """Invalid provenance, inconsistent claim or unsupported promotion."""


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise AuditError(reason)


def git_blob_sha1(data: bytes) -> str:
    """Calculate the Git object ID of bytes, rather than a plain-file SHA."""
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def validate_manifest(m: dict) -> dict:
    """Validate an immutable snapshot; not a third-party live status feed."""
    require(type(m) is dict and set(m) == {
        "schema", "source", "pinned_blob_sha1", "third_party_report", "policy"
    } and m["schema"] == SCHEMA, "unrecognized external-claim schema")
    source = m["source"]
    require(
        source == {
            "claimant": "Levent Alpöge (with Claude)",
            "announcement_date": "2026-11-20",
            "announcement_url": "https://alpo.ge/remark.pdf",
            "source_archive_sha256":
                "9631b4f020199e580ba86178cb56c6e9b09f690c2369a80dc4334aa93f49c7fc",
            "mirror_repository": "CocoSgt/riemann-hypothesis-lean",
            "mirror_commit": MIRROR_COMMIT,
            "lean_version": "leanprover/lean4:v4.33.1",
            "mathlib_commit": MATHLIB_COMMIT,
        }, "unapproved source/provenance change")
    require(m["pinned_blob_sha1"] == SHA1, "upstream blob pin changed")
    require(m["third_party_report"] == {
        "observer": "Andrew Sutherland (MIT)",
        "url": MIT_SOURCE,
        "as_of_utc": "2026-11-20T19:45:00Z",
        "headline_modules_compiled": 175187,
        "leanchecker_all_modules": "reported_pass",
        "nanoda_export": "reported_accept",
        "headline_theorem_axioms": list(STANDARD_AXIOMS),
        "full_lake_comparator": "in_progress_at_snapshot",
        "sandboxed_rebuild": "not_reported_at_snapshot",
    }, "third-party snapshot modified without manual review")
    require(m["policy"] == {
        "official_cmi_status": "UNSOLVED_AT_SNAPSHOT",
        "mathos_global_claim_status": "OPEN",
        "mathematically_independently_reviewed_by_mathos": False,
        "full_proof_replayed_by_this_tool": False,
        "automatic_promotion": False,
        "audit_scope": "PINNED_HEADLINE_SOURCE_AND_EXTERNAL_REPORT_ONLY",
    }, "attempted independent-review or mathematical-status promotion")
    return {
        "snapshot_valid": True,
        "external_claim_is_not_mathos_proof": True,
        "third_party_replay_is_reported_not_locally_performed": True,
    }


def inspect_headlines(source_text: dict[str, str]) -> dict:
    """Check the *literal headlines and pinned dependency wiring* only.

    Textual matches alone do not establish the semantic correctness of an
    imported theorem; a full trusted kernel replay remains outside this tool.
    """
    require(set(source_text) == set(SHA1), "missing or extra source files")
    main = source_text["src/Main.lean"]
    statements = source_text["src/Statements.lean"]
    bridge = source_text["src/Supplements/Kernels/MainTheorems.lean"]
    mathlib = source_text["Mathlib/NumberTheory/LSeries/RiemannZeta.lean"]
    toolchain = source_text["lean-toolchain"]
    lake = source_text["lakefile.toml"]

    require(toolchain.strip() == "leanprover/lean4:v4.33.1",
            "unexpected Lean toolchain")
    require(MATHLIB_COMMIT in lake and 'name = "mathlib"' in lake,
            "mathlib revision not pinned in Lake config")
    require(main.startswith("import Statements\n"), "headline source does not import Statements")
    for theorem in THEOREMS:
        require(len(re.findall(
            r"(?m)^theorem " + re.escape(theorem) + r"\s*:", main
        )) == 1, f"missing or duplicated headline theorem: {theorem}")
    require(re.search(
        r"(?m)^theorem riemannHypothesis\s*:\s*RiemannHypothesis\s*:=\s*rhOfAll\s*$",
        main,
    ) is not None, "headline does not target the declared Mathlib RH statement")
    require(
        re.search(
            r"(?m)^theorem rhOfAll\s*:\s*RiemannHypothesis\s*:=\s*"
            r"Formalism\.VW\.rh_of_every allChi\s*$", bridge,
        ) is not None, "headline proof-reference chain missing")
    require("theorem allChi : UpperTheory.EveryCharacter :="
            " UpperTheory.FinalTheorems.everyCharacter" in bridge,
            "expected upstream all-character theorem reference missing")
    require("import Mathlib" in statements, "statements do not import Mathlib")
    for name in THEOREMS[1:]:
        # Only the four custom proposition names appear in Statements.
        _ = name
    for name in (
        "RiemannZetaZerosOnLine", "DirichletLNonvanishingRightOfHalf",
        "DirichletLZerosOnLine", "PrimitiveDirichletLZerosOnLine",
    ):
        require(re.search(
            r"(?m)^def " + re.escape(name) + r"\s*:\s*Prop\s*:=", statements
        ) is not None, f"missing custom target definition {name}")
    require(re.search(r"(?m)^def RiemannHypothesis\s*:\s*Prop\s*:=", mathlib)
            is not None, "Mathlib RH proposition absent")
    require(re.search(
        r"∀\s*\(s\s*:\s*ℂ\).*riemannZeta s = 0.*"
        r"s ≠ 1.*s\.re = 1 / 2",
        mathlib,
    ) is not None, "Mathlib RiemannHypothesis zero-location statement not found")
    return {
        "headline_theorems_found": list(THEOREMS),
        "riemann_target_is_mathlib_definition": True,
        "source_references_trace_to_imports_only": True,
        "transitive_proof_checked_by_this_tool": False,
        "kernel_compilation_checked_by_this_tool": False,
    }


def url_for(path: str) -> str:
    require(path in SHA1, "refusing unapproved source path")
    if path.startswith("Mathlib/"):
        return ("https://raw.githubusercontent.com/leanprover-community/mathlib4/"
                + MATHLIB_COMMIT + "/" + path)
    return ("https://raw.githubusercontent.com/CocoSgt/riemann-hypothesis-lean/"
            + MIRROR_COMMIT + "/" + path)


def read_pinned_sources(*, opener=None) -> dict[str, bytes]:
    """Fetch only six fixed small source files; never execute downloaded code."""
    opener = opener or urlopen
    result = {}
    for path, expected in SHA1.items():
        request = Request(url_for(path), headers={
            "User-Agent": "MathOS-RH-External-Source-Audit/1"
        })
        with opener(request, timeout=25) as response:
            data = response.read(MAX_SOURCE_BYTES + 1)
        require(len(data) <= MAX_SOURCE_BYTES, f"{path}: oversized upstream source")
        require(git_blob_sha1(data) == expected,
                f"{path}: upstream bytes mismatch pinned Git blob")
        result[path] = data
    return result


def make_report(*, manifest_path: Path = MANIFEST, fetch_pinned: bool = False,
                opener=None) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    source_inspection = None
    if fetch_pinned:
        raw = read_pinned_sources(opener=opener)
        source_inspection = inspect_headlines(
            {path: data.decode("utf-8") for path, data in raw.items()}
        )
    return {
        "schema": SCHEMA,
        "external_source_date": "2026-11-20",
        "third_party_observer": "Andrew Sutherland (MIT)",
        "observer_source": MIT_SOURCE,
        "independent_kernel_evidence_snapshot": {
            "leanchecker_all_modules": "REPORTED_PASS",
            "nanoda_export": "REPORTED_ACCEPT",
            "axioms": list(STANDARD_AXIOMS),
            "module_count": 175187,
            "comparator": "IN_PROGRESS_AT_SNAPSHOT",
            "this_script_verified_external_kernel_logs": False,
        },
        "pinned_source_fetch_completed": fetch_pinned,
        "source_inspection": source_inspection,
        "clay_classification_at_snapshot": "UNSOLVED",
        "mathos_rh_proof_obligations_changed": False,
        "mathos_certification": "NOT_CERTIFIED",
        "independent_full_proof_replayed_by_mathos": False,
        "mathematical_consensus_or_prize_eligibility_established": False,
        "scope": "PINNED_HEADLINE_SOURCE_AUDIT_NOT_GLOBAL_PROOF_VERIFICATION",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-pinned", action="store_true",
                        help="check live bytes at pinned commits; no code execution")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = make_report(fetch_pinned=args.fetch_pinned)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(1, f"EXTERNAL RH CLAIM AUDIT FAILED: {exc}\n")
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
