#!/usr/bin/env python3
"""Generate a SHA-256 integrity manifest for MathOS evidence."""

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def git_commit():
    """Return the current Git commit, if available."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def sha256_file(path):
    """Calculate the SHA-256 digest of a file."""
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)

    return digest.hexdigest()


def generate_manifest(evidence_dir, output_file):
    evidence_dir = Path(evidence_dir).resolve()
    output_file = Path(output_file).resolve()

    if not evidence_dir.is_dir():
        raise ValueError(
            f"Evidence directory does not exist: {evidence_dir}"
        )

    records = []

    for path in sorted(evidence_dir.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue

        if path.resolve() == output_file:
            continue

        records.append({
            "path": path.relative_to(evidence_dir).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })

    manifest = {
        "schema_version": "1.0",
        "project": "MathOS",
        "methodology": "TOPO-406",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "git_commit": git_commit(),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID"),
        "hash_algorithm": "SHA-256",
        "evidence_directory": str(evidence_dir),
        "file_count": len(records),
        "files": records,
    }

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Generate MathOS evidence integrity manifest"
    )

    parser.add_argument(
        "--evidence-dir",
        default="evidence/topo406",
    )

    parser.add_argument(
        "--output",
        default="artifacts/topo406-integrity-manifest.json",
    )

    args = parser.parse_args()

    manifest = generate_manifest(
        args.evidence_dir,
        args.output,
    )

    print("MathOS integrity manifest generated")
    print(f"Evidence files: {manifest['file_count']}")
    print(f"Git commit: {manifest['git_commit']}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
