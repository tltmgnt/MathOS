"""Offline audit of external-study packages; never certifies scientific validity."""
import argparse
import hashlib
import json
from pathlib import Path

DOMAINS = {"mathematics", "computational", "experimental", "operations"}


def audit(root):
    root = Path(root).resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    require(manifest.get("schema_version") == 1, "unsupported schema_version")
    require(manifest.get("domain") in DOMAINS, "unsupported domain")
    require(manifest.get("data_origin") == "external_observations", "external observations required")
    for key in ("claim", "scope", "source_commit", "operator", "independence_disclosure",
                "comparator", "primary_metric", "acceptance_rule", "sample_size_rationale",
                "assignment", "missing_data_policy", "limitations"):
        require(isinstance(manifest.get(key), str) and bool(manifest[key].strip()), "missing " + key)
    commit = manifest.get("source_commit", "")
    require(isinstance(commit, str) and len(commit) == 40 and
            all(c in "0123456789abcdef" for c in commit), "source_commit must be a full lowercase SHA")
    artifacts = manifest.get("artifacts", [])
    if not isinstance(artifacts, list):
        errors.append("artifacts must be a list")
        artifacts = []
    required = {"preregistration", "reference", "observations", "analysis", "replication_report"}
    roles, seen = set(), set()
    for item in artifacts:
        if not isinstance(item, dict):
            errors.append("invalid artifact record")
            continue
        role, name, digest = (item.get(k) for k in ("role", "path", "sha256"))
        if not isinstance(role, str) or not isinstance(name, str) or not name:
            errors.append("artifact role and path required")
            continue
        roles.add(role)
        require(name not in seen, "duplicate artifact path: " + name)
        seen.add(name)
        path = (root / name).resolve()
        if Path(name).is_absolute() or not path.is_relative_to(root):
            errors.append("artifact escapes package: " + name)
            continue
        if not path.is_file():
            errors.append("missing artifact: " + name)
            continue
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, "digest mismatch: " + name)
    require(required <= roles, "missing artifact roles: " + ", ".join(sorted(required - roles)))
    return {"status": "package_complete_pending_external_review" if not errors else "incomplete_or_invalid",
            "errors": errors, "external_validation_established": False,
            "limitations": ["Hashes check package integrity, not authenticity or truth.",
                            "Identity, independence, preregistration timing, methods and conclusions require human external review."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.package)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
