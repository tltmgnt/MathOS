"""Fail-closed RH proof-obligation registry. Validates claims, NOT mathematical truth.

Machine-readable records document gaps and evidence; no JSON attestation or
CI success constitutes a formal proof. An external trusted kernel is needed
to establish a FORMALLY_VERIFIED mathematical claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

STATUSES = frozenset({
    "EXPERIMENTAL", "CONJECTURED", "CONDITIONAL", "PROVED", "FORMALLY_VERIFIED"
})
GATES = ("G1", "G2", "G3", "G4", "G5", "G6")
REQUIRED = {
    "G1": "density", "G2": "admissibility", "G3": "continuity",
    "G4": "arithmetic_support", "G5": "global_transfer",
    "G6": "independent_verification",
}
DEFAULT_REGISTRY = Path(__file__).resolve().parents[2] / "docs/research/rh_proof_obligations.json"


class ProofBoundaryError(ValueError):
    """A registry violates the evidence firewall."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofBoundaryError(message)


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(registry: dict) -> dict:
    """Check schema, traceability, dependencies and fail-closed promotions.

    Does not parse or prove mathematical statements. An external checker must
    independently attest any proof, and this registry intentionally contains
    no way to self-promote a global RH conclusion by editing statuses alone.
    """
    _require(isinstance(registry, dict), "registry must be an object")
    _require(registry.get("schema") == "mathos.rh.proof_obligations/1", "bad schema")
    _require(registry.get("global_claim") == "RH", "global claim must be RH")
    _require(registry.get("global_claim_status") == "OPEN",
             "RH cannot be promoted by a registry status edit")
    claims = registry.get("claims")
    _require(isinstance(claims, list) and len(claims) >= 7, "missing claims")
    by_id = {}
    for claim in claims:
        _require(isinstance(claim, dict), "claim must be object")
        cid = claim.get("id")
        _require(_nonempty(cid) and cid not in by_id, "duplicate/empty claim id")
        by_id[cid] = claim
        _require(claim.get("status") in STATUSES, f"{cid}: invalid status")
        for field in ("statement", "topology", "assumptions", "discharge"):
            _require(_nonempty(claim.get(field)), f"{cid}: missing {field}")
        deps = claim.get("dependencies")
        _require(isinstance(deps, list) and all(_nonempty(x) for x in deps)
                 and len(deps) == len(set(deps)), f"{cid}: bad dependencies")
        evidence = claim.get("evidence")
        _require(isinstance(evidence, list), f"{cid}: evidence must be list")
        for ev in evidence:
            _require(isinstance(ev, dict) and _nonempty(ev.get("path"))
                     and _nonempty(ev.get("role")), f"{cid}: bad evidence reference")
        if claim["status"] in {"PROVED", "FORMALLY_VERIFIED"}:
            # Registry metadata is not a proof or an oracle. Keep this initial
            # research registry fail-closed until a separately reviewed trusted
            # kernel integration can establish authenticity and scope.
            raise ProofBoundaryError(f"{cid}: proof promotion requires independently "
                                     "implemented trusted-kernel integration")
        if claim["status"] == "CONDITIONAL":
            _require(bool(deps), f"{cid}: conditional claim needs dependencies")
    for gate, kind in REQUIRED.items():
        _require(gate in by_id and by_id[gate].get("kind") == kind,
                 f"missing or misclassified gate {gate}")
    _require("BASELINE" in by_id
             and by_id["BASELINE"].get("kind") == "finite_comparison",
             "missing finite baseline")
    for cid, claim in by_id.items():
        for dep in claim["dependencies"]:
            _require(dep in by_id and dep != cid, f"{cid}: unknown/self dependency {dep}")
    visited, visiting = set(), set()

    def visit(cid: str) -> None:
        _require(cid not in visiting, f"dependency cycle at {cid}")
        if cid in visited:
            return
        visiting.add(cid)
        for dep in by_id[cid]["dependencies"]:
            visit(dep)
        visiting.remove(cid)
        visited.add(cid)

    for cid in by_id:
        visit(cid)
    _require(set(by_id["G5"]["dependencies"]) >= {"G1", "G2", "G3", "G4"},
             "global transfer must depend on density, admissibility, continuity, arithmetic")
    _require("G5" in by_id["G6"]["dependencies"],
             "independent verification must depend on global transfer")
    _require("BASELINE" not in by_id["G5"]["dependencies"],
             "finite baseline cannot discharge global transfer")
    _require(all(by_id[x]["status"] not in {"PROVED", "FORMALLY_VERIFIED"}
                 for x in GATES), "global gate prematurely promoted")
    return {
        "schema": registry["schema"],
        "global_claim": "RH",
        "global_claim_status": "OPEN",
        "gate_statuses": {g: by_id[g]["status"] for g in GATES},
        "unresolved_gates": [g for g in GATES
                             if by_id[g]["status"] not in {"PROVED", "FORMALLY_VERIFIED"}],
        "finite_baseline_is_global_proof": False,
        "registry_sha256": hashlib.sha256(
            json.dumps(registry, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "checks_only_metadata_not_mathematical_truth": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = validate(json.loads(args.registry.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ProofBoundaryError) as exc:
        parser.exit(1, f"RH proof firewall FAILED: {exc}\n")
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
