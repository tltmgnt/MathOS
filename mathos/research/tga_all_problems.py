"""One joint TGA campaign with seven concurrent, bounded research workers."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess

from mathos.proof_analysis.gap_analysis import Claim
from mathos.proof_analysis.tga_engine import minimal_blockers, sorted_sets
from mathos.proof_analysis.tga_level6 import report, replay
from mathos.research.clay_proof_topology import audit_clay_proof_topology, ROUTES_PATH
from mathos.research.hypothesis_pipeline import OBLIGATIONS, ROOT
from mathos.research import millennium_followup_20261124 as round1
from mathos.research import millennium_followup_round2 as round2
from mathos.research import millennium_followup_round3 as round3
from mathos.research import millennium_followup_round4 as round4
from mathos.research.tga_u003 import joint_gap

# These attacks are concrete research directions, not generated or checked proofs.
TRACKS = {
    "Riemann": ("rh", "Prove a noncircular all-zero spectral identity; for a Hankel approach, isolate the exact uniform-in-shift positivity premise.",
                "Try finite positive prefixes with a later negative form; audit multiplicity, convergence and domain assumptions."),
    "P-versus-NP": ("pnp", "Analyze deterministic SAT decision with an explicit input-bit cost model; keep unrestricted separation as a separate route.",
                    "Stress scan-based propagation with adversarial orderings and distinguish 2-SAT from arbitrary CNF."),
    "Navier-Stokes": ("ns", "Seek a global continuation estimate in each unforced domain, or a fully admissible forced breakdown construction.",
                      "Test scaling and local enstrophy bounds; a conditional finite-time estimate is not global control."),
    "Yang-Mills": ("ym", "Prove a regulator-uniform physical correlation gap for a specified gauge action and justify continuum reconstruction.",
                   "Look for vanishing spectral gaps or small low-energy spectral weights despite finite-cutoff estimates."),
    "Hodge": ("hodge", "Compute primitive rational Hodge classes and algebraic cycle images in a specified nontrivial family, then justify the transfer.",
              "Check invariant dimensions, primitive kernels and whether proposed generators are genuinely algebraic."),
    "Birch-Swinnerton-Dyer": ("bsd", "Establish analytic order versus algebraic rank for a specified family; audit Selmer comparison and finiteness separately.",
                            "Compare local traces and twists; local factors alone cannot establish global rank or the refined formula."),
    "Poincare": ("poincare", "Reconstruct the accepted proof, including surgery, comparison maps and extinction; no new prize solution is sought.",
                 "Check the hypotheses needed for width inequalities across surgery; toy recurrence does not verify the Ricci-flow proof."),
}


def graph_from_register(audit):
    spec = json.loads(ROUTES_PATH.read_text(encoding="utf-8"))
    register = json.loads(OBLIGATIONS.read_text(encoding="utf-8"))
    g = {c["claim_id"]: Claim(c["statement"], "open")
         for t in register["tracks"] for c in t["work_packages"]}
    g.update({b["claim_id"]: Claim(b["statement"], "open")
              for b in spec["candidate_bridges"]})
    targets = {}
    for track in audit["targets"]:
        key = track["model_key"]
        names = []
        for route in track["candidate_routes"]:
            node = "ROUTE:" + route["route_id"]
            g[node] = Claim(route["scope"], "derived", (tuple(route["obligations"]),),
                            "Authored route; mathematical sufficiency not established.")
            names.append(node)
        target = "TARGET:" + key
        g[target] = Claim(key + " project research route", "derived", tuple((n,) for n in names))
        targets[key] = target
    g["POINCARE.published"] = Claim("Accepted external theorem", "established_external")
    g["JOINT_REGISTERED_PROJECT"] = Claim(
        "All registered project routes, including refined BSD and Poincare reconstruction",
        "derived", (tuple(targets.values()),))
    # Not the official minimum: the available registered BSD route is stronger.
    g["JOINT_REGISTERED_WITH_EXTERNAL_POINCARE"] = Claim(
        "Registered six active routes (including refined BSD) and published Poincare",
        "derived", (tuple(targets[k] for k in TRACKS if k != "Poincare") + ("POINCARE.published",),))
    return g, targets


def check_factorization(joint, tracks):
    """Separate combinatorial check for an AND of leaf-disjoint track formulas."""
    supports = [set().union(*map(set, p["minimal_completion_sets"])) for p in tracks]
    if any(a & b for i, a in enumerate(supports) for b in supports[i+1:]):
        raise ValueError("track supports overlap; factorized oracle is inapplicable")
    expected = sorted_sets({frozenset().union(*map(frozenset, choice))
                            for choice in product(*(p["minimal_completion_sets"] for p in tracks))})
    if expected != joint["minimal_completion_sets"]:
        raise ValueError("joint completion factorization mismatch")
    expected_blockers = sorted_sets({frozenset(s) for p in tracks for s in p["minimal_blocking_sets"]})
    if expected_blockers != joint["minimal_blocking_sets"]:
        raise ValueError("joint blocker factorization mismatch")
    return {"status": "PASS", "method": "Cartesian product of disjoint completion antichains; union of track blocker antichains",
            "scope": "Project-internal Boolean graph cross-check, not independent scientific review"}


def topology():
    audit = audit_clay_proof_topology()
    g, targets = graph_from_register(audit)
    packets = {}
    for key, target in targets.items():
        p = report(g, target)
        if p.get("finite_oracle", {}).get("status") != "PASS":
            raise ValueError("track oracle did not pass: " + key)
        if p["minimal_completion_sets"] != next(t["minimal_completion_sets"] for t in audit["targets"]
                                                if t["model_key"] == key):
            raise ValueError("registered route mismatch: " + key)
        replay(p)
        packets[key] = p
    joint = report(g, "JOINT_REGISTERED_PROJECT")
    external = report(g, "JOINT_REGISTERED_WITH_EXTERNAL_POINCARE")
    replay(joint)
    replay(external)
    check1 = check_factorization(joint, list(packets.values()))
    check2 = check_factorization(external, [p for k, p in packets.items() if k != "Poincare"])
    return {
        "registered_tracks": packets, "registered_project_joint": joint,
        "registered_external_poincare_joint": external,
        "joint_factorization": {"project": check1, "external_poincare": check2},
        "core_research_model_u003": joint_gap(),
        "registry_source_sha256": audit["source_sha256"],
        "external_claims_as_of": audit["external_claims_as_of"],
        "scope": "Registered stronger BSD/reconstruction model and separate U003 core model; not interchangeable.",
        "mathematical_certification": "NOT_CERTIFIED",
    }


def run_track(key):
    fn, attack, falsifier = TRACKS[key]
    controls = {}
    failures = []
    # No AI credentials, network, or generated code; every track replays real
    # existing bounded computations. A failing round never hides later rounds.
    for name, module in (("round1", round1), ("round2", round2), ("round3", round3), ("round4", round4)):
        try:
            controls[name] = {"status": "PASS", "result": getattr(module, fn)()}
        except Exception as exc:
            controls[name] = {"status": "FAIL", "error_type": type(exc).__name__, "message": str(exc)}
            failures.append(name)
    return {"track": key, "status": "BOUNDED_CONTROLS_PASS" if not failures else "FAILED",
            "controls": controls, "failed_rounds": failures, "next_attack": attack,
            "adversarial_check": falsifier, "new_proof_generated": False,
            "mathematical_certification": "NOT_CERTIFIED"}


def write(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def campaign(out, workers=7):
    if type(workers) is not int or not 1 <= workers <= 7:
        raise ValueError("workers must be 1..7")
    out = Path(out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT / "artifacts"):
        raise ValueError("repository outputs must be under artifacts/")
    out.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    # Snapshot provenance for actual inputs; Git SHA identifies the checkout,
    # not an independent external attestation.
    sources = (Path(__file__), Path(round1.__file__), Path(round2.__file__), Path(round3.__file__), Path(round4.__file__),
               ROOT / "mathos/proof_analysis/tga_engine.py",
               ROOT / "mathos/proof_analysis/tga_level6.py")
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    topo = topology()
    write(out / "joint-topology.json", topo)
    results = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        tasks = {pool.submit(run_track, key): key for key in TRACKS}
        for task in as_completed(tasks):
            key = tasks[task]
            try:
                result = task.result()
            except Exception as exc:
                result = {"track": key, "status": "FAILED", "error_type": type(exc).__name__,
                          "mathematical_certification": "NOT_CERTIFIED"}
            results[key] = result
            write(out / (key + ".json"), result)
    if source_hashes != {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}:
        raise RuntimeError("research sources changed during execution")
    if topo["registry_source_sha256"] != audit_clay_proof_topology()["source_sha256"]:
        raise RuntimeError("protected registry changed during execution")
    failed = [key for key in TRACKS if results[key]["status"] != "BOUNDED_CONTROLS_PASS"]
    summary = {"schema": "mathos.tga.all-problems/1", "source_commit": commit, "workers": workers,
               "track_count": len(results), "tracks": {key: results[key]["status"] for key in TRACKS},
               "failed_tracks": failed, "source_sha256": source_hashes,
               "registry_source_sha256": topo["registry_source_sha256"],
               "artifact_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob("*.json"))},
               "new_millennium_proofs": 0, "live_model_calls": 0, "global_promotion": "NONE",
               "mathematical_certification": "NOT_CERTIFIED", "level_6_certified": False}
    write(out / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=7)
    args = parser.parse_args()
    result = campaign(args.output_dir, args.workers)
    print(json.dumps(result, indent=2))
    return int(bool(result["failed_tracks"]))


if __name__ == "__main__":
    raise SystemExit(main())
