"""Offline audit of external-study packages; never certifies scientific validity."""
import argparse
import hashlib
import json
from pathlib import Path

DOMAINS = {"mathematics", "computational", "experimental", "operations"}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit(root):
    root = Path(root).resolve()
    errors = []
    def report():
        return {"status": "package_complete_pending_external_review" if not errors else "incomplete_or_invalid",
                "errors": errors, "external_validation_established": False,
                "limitations": ["Hashes check package integrity, not authenticity or truth.",
                                "Identity, independence, preregistration timing, methods and conclusions require human external review."]}
    try:
        manifest_path = (root / "manifest.json").resolve()
        if not manifest_path.is_relative_to(root):
            raise ValueError("manifest escapes package")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
        if not isinstance(manifest, dict):
            raise ValueError("manifest must be an object")
    except (OSError, ValueError, RuntimeError) as exc:
        errors.append("invalid manifest: " + str(exc))
        return report()
    def require(condition, message):
        if not condition:
            errors.append(message)
    require(type(manifest.get("schema_version")) is int and manifest["schema_version"] == 1, "unsupported schema_version")
    domain = manifest.get("domain")
    require(isinstance(domain, str) and domain in DOMAINS, "unsupported domain")
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
        if not isinstance(role, str) or not role.strip() or not isinstance(name, str) or not name.strip():
            errors.append("artifact role and path required")
            continue
        roles.add(role)
        require(name not in seen, "duplicate artifact path: " + name)
        seen.add(name)
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            errors.append("invalid sha256: " + name)
            continue
        try:
            path = (root / name).resolve()
        except (OSError, ValueError, RuntimeError) as exc:
            errors.append("invalid artifact path: " + str(exc))
            continue
        if Path(name).is_absolute() or not path.is_relative_to(root):
            errors.append("artifact escapes package: " + name)
            continue
        try:
            if not path.is_file():
                errors.append("missing artifact: " + name)
                continue
            require(_digest(path) == digest, "digest mismatch: " + name)
        except (OSError, ValueError) as exc:
            errors.append("unreadable artifact: " + name + ": " + str(exc))
    require(required <= roles, "missing artifact roles: " + ", ".join(sorted(required - roles)))
    return report()


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
