"""Breakthrough-focused queue and fail-closed candidate metadata intake.

No mathematical proof checking, status promotion, or external identity authentication.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ("statement", "hypotheses", "definitions", "source_locators",
            "proof_or_gap", "implication_to_claim", "unproved_dependencies",
            "adversarial_findings", "formal_status", "novelty_status", "review_status")
OUTCOMES = {"UNRESOLVED", "FALSIFIED_CANDIDATE", "SCOPED_RESULT_CANDIDATE", "PROOF_CANDIDATE"}


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def build_queue(plan, register, routes):
    if plan.get("status") != "RESEARCH_ONLY" or plan.get("promotion") != "NONE":
        raise ValueError("research-only policy")
    if register.get("certification") != "NOT_CERTIFIED":
        raise ValueError("canonical status changed; human review required")
    canonical = {}
    for track in register["tracks"]:
        for work in track["work_packages"]:
            cid = work["claim_id"]
            if cid in canonical or work["graph_state"] != "open":
                raise ValueError("canonical obligations changed; human review required")
            canonical[cid] = track["track_id"]
    route_map = {r["route_id"]: set(r["obligations"]) for r in routes["routes"]}
    seen = set()
    tracks = set()
    for task in plan["tracks"]:
        tid = task["track"]
        if tid in tracks or task["route"] not in route_map:
            raise ValueError("duplicate track or unknown route")
        tracks.add(tid)
        if not all(isinstance(task.get(k), str) and task[k].strip() for k in ("attack", "falsify", "exit")):
            raise ValueError("empty research strategy")
        for cid in task["claims"]:
            if cid in seen or canonical.get(cid) != tid or cid not in route_map[task["route"]]:
                raise ValueError("duplicate, unrelated or unregistered claim")
            seen.add(cid)
    if seen != set(canonical) or len(seen) != 14 or len(tracks) != 7:
        raise ValueError("canonical obligation coverage mismatch")
    focus = plan["focus_policy"]
    active = [focus["primary"], focus["challenger"]]
    if len(set(active)) != 2 or not set(active) <= seen or len({canonical[c] for c in active}) != 2:
        raise ValueError("invalid active focus")
    if focus["max_active_tracks"] != 2 or focus["review_after_attempts"] != 3:
        raise ValueError("invalid focus budget")
    return {"status": "RESEARCH_ONLY", "promotion": "NONE",
            "open_obligations": len(seen), "active_claims": active,
            "queued_claims": sorted(seen - set(active)), "tracks": plan["tracks"],
            "mathematical_proof_established": False, "external_review_verified": False}


def intake(packet, queue):
    if not isinstance(packet, dict):
        raise ValueError("candidate packet must be an object")
    if packet.get("claim_id") not in queue["active_claims"]:
        raise ValueError("claim is not active")
    outcome = packet.get("outcome")
    if outcome not in OUTCOMES or packet.get("promotion") != "NONE":
        raise ValueError("invalid outcome or attempted promotion")
    for key in REQUIRED:
        value = packet.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("missing candidate field: " + key)
    if packet["formal_status"] not in ("NOT_CHECKED", "SCOPED_ARTIFACT_REPORTED"):
        raise ValueError("formal status must not assert unchecked certification")
    if packet["novelty_status"] not in ("NOT_CHECKED", "REVIEW_REQUESTED"):
        raise ValueError("novelty status must not assert acceptance")
    if packet["review_status"] not in ("NOT_REVIEWED", "REVIEW_REQUESTED"):
        raise ValueError("review status must not assert independent acceptance")
    if outcome == "PROOF_CANDIDATE" and packet.get("evidence_kind") != "MATHEMATICAL_ARGUMENT":
        raise ValueError("bounded tests cannot substitute for a proof argument")
    return {"status": "METADATA_ACCEPTED_FOR_REVIEW", "claim_id": packet["claim_id"],
            "outcome": outcome, "promotion": "NONE",
            "mathematical_proof_established": False, "external_review_verified": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate", type=Path)
    args = p.parse_args()
    paths = ["docs/research/BREAKTHROUGH_FOCUS.v1.json",
             "docs/proof-analysis/OBLIGATIONS.v1.json", "docs/research/CLAY_PROOF_ROUTES.v1.json"]
    queue = build_queue(*(load(path) for path in paths))
    queue["source_sha256"] = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}
    if args.candidate:
        queue["intake"] = intake(json.loads(args.candidate.read_text(encoding="utf-8")), queue)
    print(json.dumps(queue, indent=2))


if __name__ == "__main__":
    main()
