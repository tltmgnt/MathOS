"""Seven-engine Millennium Ω research workflow with a fail-closed TECT gate.

Reuses the canonical seven-hypothesis probes and proof-obligation register.
Six deterministic Ω agents produce *research records*, never mathematical
theorems. No model inference or external proof verification is performed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from mathos.research.clay_alignment import TARGETS_PATH
from mathos.research.hypothesis_pipeline import (
    HYPOTHESES, OBLIGATIONS, run_exploration,
)

# Stable public engine names; all seven are distinct even when their bounded
# experiments are delegated to MathOS's existing hypothesis pipeline.
ENGINES = {
    "bsd": "Birch-Swinnerton-Dyer",
    "hodge": "Hodge",
    "navier_stokes": "Navier-Stokes",
    "p_vs_np": "P-versus-NP",
    "poincare": "Poincare",
    "riemann": "Riemann",
    "yang_mills": "Yang-Mills",
}
STAGES = (
    "discovery", "conjecture", "derivation",
    "falsification", "verification", "evidence",
)
SCHEMA = "mathos.millennium_omega/1"
RESEARCH_ONLY = "RESEARCH_ONLY"
EXTERNAL = "ESTABLISHED_EXTERNALLY_ONLY"
OPEN = "NOT_ESTABLISHED"


class AssuranceError(ValueError):
    """TECT rejected a malformed, unsupported, or promoted claim."""


def _require(ok: bool, reason: str) -> None:
    if not ok:
        raise AssuranceError(reason)


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _agents(experiment: dict[str, Any], hypothesis: dict[str, Any]) -> list[dict]:
    """Six explicit, bounded, deterministic stage contracts.

    'Verification' verifies only the bounded probe returned by the existing
    pipeline. A proof checker is *never* inferred from a successful probe.
    """
    probe = experiment["probe_result"]
    return [
        {
            "stage": "discovery",
            "finding": hypothesis["use_case"],
            "proof_claim": False,
        },
        {
            "stage": "conjecture",
            "candidate": hypothesis["hypothesis"],
            "state": "UNPROVEN_HYPOTHESIS",
            "proof_claim": False,
        },
        {
            "stage": "derivation",
            "method": experiment["probe"],
            "scope": probe["scope"],
            "state": "FINITE_OR_CONDITIONAL_CHECK_ONLY",
            "proof_claim": False,
        },
        {
            "stage": "falsification",
            "falsifier": hypothesis["falsifier"],
            "executed_general_falsification": False,
            "proof_claim": False,
        },
        {
            "stage": "verification",
            "bounded_probe_passed": probe["passed"] is True,
            "lean_global_theorem_checked": False,
            "coq_global_theorem_checked": False,
            "independent_review": False,
            "proof_claim": False,
        },
        {
            "stage": "evidence",
            "source": hypothesis["source"],
            "probe_sha256": _digest(probe),
            "state": "SCOPED_RESEARCH_EVIDENCE",
            "proof_claim": False,
        },
    ]


def audit_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """TECT acceptance gate: reject promotions, missing stages and altered packets.

    Metadata governance only; hash integrity is not independent mathematical
    verification and cannot authorize a status change.
    """
    _require(type(packet) is dict, "packet must be a JSON object")
    expected_keys = {
        "schema", "certification", "external_poincare", "source_sha256",
        "engines", "proof_promotion", "assurance",
    }
    _require(set(packet) == expected_keys, "unexpected packet fields")
    _require(packet["schema"] == SCHEMA, "schema mismatch")
    _require(packet["certification"] == "NOT_CERTIFIED", "proof promotion denied")
    _require(packet["proof_promotion"] == "NONE", "proof promotion denied")
    _require(packet["external_poincare"] == EXTERNAL, "external scope corrupted")
    _require(
        type(packet["source_sha256"]) is dict
        and set(packet["source_sha256"]) == {"register", "hypotheses", "targets"}
        and all(type(s) is str and len(s) == 64 and
                all(c in "0123456789abcdef" for c in s)
                for s in packet["source_sha256"].values()),
        "invalid source fingerprints",
    )
    engines = packet["engines"]
    _require(type(engines) is list and len(engines) == 7, "seven engines required")
    seen = set()
    for engine in engines:
        _require(type(engine) is dict, "engine record must be an object")
        _require(
            set(engine) == {
                "engine", "model_key", "clay_status", "external_solution",
                "mathos_proof_status", "certification", "hypothesis_id",
                "probe", "probe_result", "missing_global_step",
                "obligations", "agents", "accepted_scope",
            },
            "engine schema mismatch",
        )
        key = engine["engine"]
        _require(
            type(key) is str and key in ENGINES and key not in seen,
            "unknown or duplicate engine",
        )
        seen.add(key)
        model = ENGINES[key]
        _require(engine["model_key"] == model, "engine/model mismatch")
        _require(engine["mathos_proof_status"] == "BLOCKED", "global proof promotion denied")
        _require(engine["certification"] == "NOT_CERTIFIED", "certification denied")
        _require(engine["accepted_scope"] == RESEARCH_ONLY, "unsafe acceptance scope")
        _require(
            engine["external_solution"] == (EXTERNAL if key == "poincare" else OPEN),
            "misclassified external solution",
        )
        _require(
            engine["clay_status"] == (
                "SOLVED_EXTERNALLY" if key == "poincare" else
                engine["clay_status"]
            ) and (
                key == "poincare" or engine["clay_status"] in {"UNSOLVED", "ACTIVE"}
            ),
            "official status invariant failed",
        )
        _require(
            type(engine["hypothesis_id"]) is str and bool(engine["hypothesis_id"])
            and type(engine["probe"]) is str and bool(engine["probe"])
            and type(engine["missing_global_step"]) is str
            and bool(engine["missing_global_step"]),
            "missing research traceability",
        )
        _require(
            type(engine["obligations"]) is list and bool(engine["obligations"])
            and len(engine["obligations"]) == len(set(engine["obligations"]))
            and all(type(x) is str and bool(x) for x in engine["obligations"]),
            "missing or duplicate obligations",
        )
        result = engine["probe_result"]
        _require(
            type(result) is dict and result.get("passed") is True
            and type(result.get("scope")) is str
            and bool(result["scope"]),
            "bounded probe failed or has no scope",
        )
        stages = engine["agents"]
        _require(
            type(stages) is list and len(stages) == len(STAGES)
            and all(type(s) is dict and s.get("stage") == stage
                    and s.get("proof_claim") is False
                    for s, stage in zip(stages, STAGES)),
            "invalid agent trace or attempted proof claim",
        )
        _require(
            stages[1].get("state") == "UNPROVEN_HYPOTHESIS"
            and stages[2].get("state") == "FINITE_OR_CONDITIONAL_CHECK_ONLY"
            and stages[3].get("executed_general_falsification") is False
            and stages[4].get("bounded_probe_passed") is True
            and stages[4].get("lean_global_theorem_checked") is False
            and stages[4].get("coq_global_theorem_checked") is False
            and stages[4].get("independent_review") is False
            and stages[5].get("state") == "SCOPED_RESEARCH_EVIDENCE"
            and stages[5].get("probe_sha256") == _digest(result),
            "unsubstantiated agent evidence",
        )
    _require(seen == set(ENGINES), "missing engine")
    assurance = packet["assurance"]
    _require(
        type(assurance) is dict and
        set(assurance) == {"decision", "global_proof_accepted", "content_sha256"}
        and assurance["decision"] == RESEARCH_ONLY
        and assurance["global_proof_accepted"] is False,
        "TECT policy violation",
    )
    content = {key: value for key, value in packet.items() if key != "assurance"}
    _require(
        assurance["content_sha256"] == _digest(content),
        "record content changed after assurance fingerprint",
    )
    return {
        "decision": RESEARCH_ONLY,
        "global_proof_accepted": False,
        "structurally_valid_engines": len(seen),
        "fingerprint_valid": True,
        "meaning": "Schema/policy/integrity checks, not a mathematical proof",
    }


def run_framework(
    *, register_path: Path = OBLIGATIONS,
    hypothesis_path: Path = HYPOTHESES,
    targets_path: Path = TARGETS_PATH,
) -> dict[str, Any]:
    """Run all seven bounded engines; never modify a canonical register."""
    # The existing checked pipeline rejects tampered obligations, misaligned
    # probe mappings, invented novelty and false certification.
    exploration = run_exploration(
        register_path=register_path, hypothesis_path=hypothesis_path,
    )
    register = json.loads(register_path.read_text(encoding="utf-8"))
    hypotheses = json.loads(hypothesis_path.read_text(encoding="utf-8"))
    targets = json.loads(targets_path.read_text(encoding="utf-8"))
    _require(exploration.get("certification") == "NOT_CERTIFIED", "unsafe source result")
    _require(exploration.get("all_probes_passed") is True, "probe failure")
    by_model = {e["model_key"]: e for e in exploration["experiments"]}
    by_hypothesis = {e["model_key"]: e for e in hypotheses["experiments"]}
    by_track = {t["model_key"]: t for t in register["tracks"]}
    by_target = {t["model_key"]: t for t in targets["targets"]}
    _require(
        all(len(mapping) == 7 and set(mapping) == set(ENGINES.values())
            for mapping in (by_model, by_hypothesis, by_track, by_target)),
        "canonical coverage mismatch",
    )
    _require(
        register["external_result"]["claim_id"] == "POINCARE.published"
        and register["external_result"]["graph_state"] == "established_external"
        and register["external_result"]["verification"] == "accepted_external_not_replayed",
        "Poincare external recognition mismatch",
    )
    results = []
    for key, model in ENGINES.items():
        experiment = by_model[model]
        hypothesis = by_hypothesis[model]
        track = by_track[model]
        target = by_target[model]
        obligations = track["work_packages"]
        _require(
            track["modeled_target_status"] == "BLOCKED"
            and all(
                p["graph_state"] == "open"
                and p["formal_check"] == "not_performed"
                and p["review_verdict"] == "not_reviewed"
                for p in obligations
            ), f"{key}: canonical obligations were promoted",
        )
        _require(
            (target["clay_status"] == "SOLVED_EXTERNALLY") == (key == "poincare")
            and (key == "poincare" or target["clay_status"] in {"UNSOLVED", "ACTIVE"}),
            f"{key}: unsupported Clay status",
        )
        results.append({
            "engine": key,
            "model_key": model,
            "clay_status": target["clay_status"],
            "external_solution": EXTERNAL if key == "poincare" else OPEN,
            "mathos_proof_status": "BLOCKED",
            "certification": "NOT_CERTIFIED",
            "hypothesis_id": experiment["hypothesis_id"],
            "probe": experiment["probe"],
            "probe_result": experiment["probe_result"],
            "missing_global_step": experiment["missing_global_step"],
            "obligations": [p["claim_id"] for p in obligations],
            "agents": _agents(experiment, hypothesis),
            "accepted_scope": RESEARCH_ONLY,
        })
    packet = {
        "schema": SCHEMA,
        "certification": "NOT_CERTIFIED",
        "external_poincare": EXTERNAL,
        "source_sha256": {
            "register": _sha(register_path),
            "hypotheses": _sha(hypothesis_path),
            "targets": _sha(targets_path),
        },
        "engines": results,
        "proof_promotion": "NONE",
    }
    packet["assurance"] = {
        "decision": RESEARCH_ONLY,
        "global_proof_accepted": False,
        "content_sha256": _digest(packet),
    }
    audit_packet(packet)
    return packet


def run_engine(
    engine: str, *, register_path: Path = OBLIGATIONS,
    hypothesis_path: Path = HYPOTHESES,
    targets_path: Path = TARGETS_PATH,
) -> dict[str, Any]:
    """Return one engine record after evaluating all safety gates."""
    _require(engine in ENGINES, f"unknown engine: {engine}")
    packet = run_framework(
        register_path=register_path,
        hypothesis_path=hypothesis_path,
        targets_path=targets_path,
    )
    return next(item for item in packet["engines"] if item["engine"] == engine)
