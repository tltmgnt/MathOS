"""Fail-closed offline research evidence lineage audit.

This checks only declared graph links and bytes. It never proves mathematics,
authenticates a reviewer, or establishes independent scientific validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat

KINDS = ("source", "analysis", "verification", "review", "export")
PREDECESSOR = {
    "source": None,
    "analysis": "source",
    "verification": "analysis",
    "review": "verification",
    "export": "review",
}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
IDENT = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
MAX_MANIFEST = 1_048_576
MAX_ARTIFACT = 32 * 1024 * 1024


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _safe_file(root: Path, name: str, maximum: int) -> bytes:
    if (not isinstance(name, str) or not name or len(name) > 256 or
            "\\" in name or Path(name).is_absolute()):
        raise ValueError("unsafe artifact path")
    parts = Path(name).parts
    if not parts or any(part in {".", ".."} for part in parts):
        raise ValueError("unsafe artifact path")
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("symlinks forbidden")
    if not path.is_relative_to(root):
        raise ValueError("artifact outside root")
    try:
        metadata = path.stat()
    except OSError as exc:
        raise ValueError("missing artifact") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError("artifact is not a regular file")
    if metadata.st_size > maximum:
        raise ValueError("artifact size limit exceeded")
    data = path.read_bytes()
    if len(data) > maximum:
        raise ValueError("artifact size limit exceeded")
    return data


def audit(root: Path) -> dict:
    """Return a descriptive, non-authoritative report without modifying inputs."""
    root = Path(root).absolute()
    errors: list[str] = []
    report = {
        "schema_version": "research_evidence_audit/1",
        "status": "incomplete_or_invalid",
        "errors": errors,
        "missing_roles": [],
        "unresolved_roles": [],
        "structural_lineage_complete": False,
        "mathematical_truth_verified": False,
        "external_validation_established": False,
        "human_review_authenticated": False,
        "limitations": [
            "Hashes attest byte consistency only, not source authenticity.",
            "Modelled links do not establish logical implication or proof correctness.",
            "Reviewer identity, independence, novelty and subject expertise require outside verification.",
        ],
    }
    try:
        raw = _safe_file(root, "manifest.json", MAX_MANIFEST)
        manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
        if not isinstance(manifest, dict):
            raise ValueError("manifest must be an object")
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append("manifest: " + str(exc))
        return report

    if set(manifest) != {"schema_version", "claim_id", "source_commit", "scope", "records"}:
        errors.append("manifest must have exactly the five contracted fields")
    if manifest.get("schema_version") != "research_evidence_manifest/1":
        errors.append("unsupported schema")
    if not isinstance(manifest.get("claim_id"), str) or not IDENT.fullmatch(manifest["claim_id"]):
        errors.append("invalid claim_id")
    if not isinstance(manifest.get("source_commit"), str) or not COMMIT.fullmatch(manifest["source_commit"]):
        errors.append("invalid source_commit")
    if not isinstance(manifest.get("scope"), str) or not manifest["scope"].strip():
        errors.append("missing scope")

    records = manifest.get("records")
    if not isinstance(records, list):
        errors.append("records must be a list")
        return report
    by_kind = {}
    all_paths = set()
    for index, record in enumerate(records):
        prefix = "records[" + str(index) + "]"
        if not isinstance(record, dict) or set(record) != {"kind", "state", "path", "sha256", "depends_on"}:
            errors.append(prefix + ": invalid record fields")
            continue
        kind = record["kind"]
        if kind not in KINDS:
            errors.append(prefix + ": unknown kind")
            continue
        if kind in by_kind:
            errors.append(prefix + ": duplicate kind")
            continue
        by_kind[kind] = record
        predecessor = PREDECESSOR[kind]
        required = [] if predecessor is None else [predecessor]
        if record["depends_on"] != required:
            errors.append(prefix + ": missing or invalid predecessor dependency")
        if record["state"] not in {"recorded", "pending"}:
            errors.append(prefix + ": invalid state")
            continue
        if record["state"] == "pending":
            if record["path"] is not None or record["sha256"] is not None:
                errors.append(prefix + ": pending record cannot claim artifact")
            continue
        path, digest = record["path"], record["sha256"]
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            errors.append(prefix + ": invalid sha256")
            continue
        if not isinstance(path, str) or path in all_paths or path == "manifest.json":
            errors.append(prefix + ": duplicate or invalid path")
            continue
        all_paths.add(path)
        try:
            data = _safe_file(root, path, MAX_ARTIFACT)
            if hashlib.sha256(data).hexdigest() != digest:
                errors.append(prefix + ": digest mismatch")
        except (OSError, ValueError) as exc:
            errors.append(prefix + ": " + str(exc))

    report["missing_roles"] = sorted(set(KINDS) - set(by_kind))
    report["unresolved_roles"] = sorted(
        kind for kind, record in by_kind.items() if record.get("state") != "recorded"
    )
    if report["missing_roles"]:
        errors.append("missing required roles: " + ", ".join(report["missing_roles"]))
    # A recorded downstream step cannot have an unfinished upstream prerequisite.
    for kind in KINDS[1:]:
        record = by_kind.get(kind)
        predecessor = by_kind.get(PREDECESSOR[kind])
        if record and record.get("state") == "recorded" and (
            not predecessor or predecessor.get("state") != "recorded"
        ):
            errors.append(kind + ": recorded downstream with pending prerequisite")
    if not errors:
        report["status"] = (
            "lineage_packet_structurally_complete" if not report["unresolved_roles"]
            else "lineage_packet_structurally_valid_with_gaps"
        )
        report["structural_lineage_complete"] = not report["unresolved_roles"]
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="directory containing manifest.json and local evidence")
    args = parser.parse_args()
    result = audit(args.package)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
