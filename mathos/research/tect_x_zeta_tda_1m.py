"""TECT-X: auditable 1,000,000 zeta-function variants and bounded TDA.

Four mathematically distinct, explicitly parameterized families are counted:
  250,000 Hurwitz zeta(s,a) functions,
  250,000 spectral zeta functions of unweighted cycle graphs C_n,
  250,000 Ihara graph zeta functions of cycle graphs C_n,
  250,000 Artin-Mazur zeta functions of k-symbol full shifts.

This is a deterministic finite experiment. It does NOT evaluate zero sets,
prove RH or BSD, discover a new functional equation, or verify 1 million
independent number-theoretic conjectures.

Within-family Vietoris--Rips Betti_0/Betti_1 computations use 128-point
subsamples and explicitly chosen feature embeddings; they are not full
million-point persistent-homology computations. H0-death scales of the full
ordered feature clouds are evaluated in O(N) via monotone-chain property.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import math
import hashlib
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.special import polygamma
from scipy.spatial.distance import pdist, squareform

FAMILIES = (
    "hurwitz",
    "cycle_spectral",
    "cycle_ihara",
    "full_shift_dynamical",
)
RADII = (0.03, 0.06, 0.12, 0.18, 0.25, 0.4, 0.55)


def parameter_features(per_family: int):
    if type(per_family) is not int or not 2 <= per_family <= 250_000:
        raise ValueError("per_family must be an integer from 2 to 250000")
    j = np.arange(per_family, dtype=np.int64)
    alpha = 1.0 + (j + 0.5) / per_family
    hurwitz = np.column_stack((polygamma(1, alpha), -polygamma(2, alpha) / 2.0))

    n = j + 3  # cycle lengths n >= 3
    nf = n.astype(np.float64)
    spectral1 = (nf**2 - 1.0) / 12.0
    spectral2 = (nf**4 + 10.0 * nf**2 - 11.0) / 720.0
    cycle_spectral = np.column_stack((np.log(spectral1), np.log(spectral2)))

    # Z_Cn(u) = (1-u^n)^(-2). The probes u_n=exp(-tau/n) deliberately
    # induce complete aliasing for tau = 1, 2. Not fixed-u evaluations!
    ihara_log1 = float(-2.0 * np.log(-np.expm1(-1.0)))
    ihara_log2 = float(-2.0 * np.log(-np.expm1(-2.0)))
    cycle_ihara = np.tile([ihara_log1, ihara_log2], (per_family, 1))

    k = j + 2  # k-symbol full shift with zeta 1/(1-k u)
    logk = np.log(k.astype(np.float64))
    full_shift = np.column_stack((logk, 2.0 * logk))

    return {
        "hurwitz": hurwitz,
        "cycle_spectral": cycle_spectral,
        "cycle_ihara": cycle_ihara,
        "full_shift_dynamical": full_shift,
    }


def norm_features(x: np.ndarray) -> np.ndarray:
    mn, mx = np.min(x, axis=0), np.max(x, axis=0)
    d = mx - mn
    return np.divide(x - mn, d, out=np.zeros_like(x), where=d > 1.e-13)


def monotone_h0_deaths(x: np.ndarray) -> np.ndarray:
    """H0 death scales of an ordered coordinatewise-monotone 2D cloud.

    In such a cloud, the Euclidean MST is the consecutive-neighbor path:
    across each cut between i and i+1, every spanning edge is at least
    as long as (i, i+1) in both coordinates. The N-1 path lengths are
    therefore exactly the finite degree-0 Rips death scales.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != 2:
        raise ValueError("expect Nx2 cloud")
    dx = np.diff(x, axis=0)
    if not (np.all(dx >= -1.e-13) or np.all(dx <= 1.e-13)):
        # The direction must agree coordinatewise across all points,
        # not merely be monotone within each coordinate independently.
        raise ValueError("embedding is not monotone in a common direction")
    return np.linalg.norm(dx, axis=1)


def rips_betti01(points: np.ndarray, radius: float) -> dict:
    """Exact combinatorial F2 Betti 0/1 for a 2-skeleton VR at radius.

    Distances are floating point. Once the adjacency graph is defined, the
    boundary ranks and Betti numbers are exact integer/GF(2) computations.
    This is a fixed-radius Betti audit, not a complete persistence diagram.
    """
    pts = np.asarray(points, dtype=np.float64)
    if pts.ndim != 2 or pts.shape[1] != 2 or not 1 <= len(pts) <= 128:
        raise ValueError("require 1..128 point cloud in R2")
    if not np.isfinite(pts).all() or not np.isfinite(radius) or radius < 0:
        raise ValueError("invalid point cloud or radius")
    n = len(pts)
    if n == 1:
        return {"components": 1, "betti1": 0, "vertices": 1, "edges": 0, "triangles": 0}
    dist = squareform(pdist(pts))
    adjacency = (dist <= radius + 1.e-12)
    np.fill_diagonal(adjacency, False)
    parent = list(range(n))

    def root(i):
        while i != parent[i]:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    edge_index = {}
    for i in range(n):
        for j in np.flatnonzero(adjacency[i, i + 1:]) + i + 1:
            j = int(j)
            ra, rb = root(i), root(j)
            if ra != rb:
                parent[ra] = rb
            edge_index[(i, j)] = len(edge_index)
    e = len(edge_index)
    comps = len(set(root(i) for i in range(n)))
    pivots = {}
    triangles = 0
    for i in range(n):
        later = (np.flatnonzero(adjacency[i, i + 1:]) + i + 1).tolist()
        for pos, j in enumerate(later):
            for k in later[pos + 1:]:
                if adjacency[j, k]:
                    triangles += 1
                    col = ((1 << edge_index[(i, j)]) ^
                           (1 << edge_index[(i, k)]) ^
                           (1 << edge_index[(j, k)]))
                    while col:
                        pivot = col.bit_length() - 1
                        if pivot in pivots:
                            col ^= pivots[pivot]
                        else:
                            pivots[pivot] = col
                            break
    b1 = e - n + comps - len(pivots)
    if b1 < 0:
        raise AssertionError("negative Betti1 from boundary calculation")
    return {"components": comps, "betti1": b1,
            "vertices": n, "edges": e, "triangles": triangles}


def circle_control(n: int = 128) -> np.ndarray:
    theta = 2 * np.pi * np.arange(n, dtype=np.float64) / n
    return np.column_stack((0.5 + 0.5 * np.cos(theta),
                            0.5 + 0.5 * np.sin(theta)))


def _csv_manifest(features: dict, per_family: int, out: Path):
    # gzip timestamp zero + no embedded original filename => stable SHA256
    # for identical software, platform and floating-point library versions.
    with out.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", compresslevel=6, mtime=0) as z:
            with io.TextIOWrapper(z, encoding="utf-8", newline="") as stream:
                w = csv.writer(stream, lineterminator="\n")
                w.writerow(("variant_id", "family", "parameter", "feature_1", "feature_2"))
                for family in FAMILIES:
                    cloud = features[family]
                    for i in range(per_family):
                        parameter = (
                            f"{2*per_family+2*i+1}/{2*per_family}"
                            if family == "hurwitz" else str(i + (2 if family == "full_shift_dynamical" else 3))
                        )
                        w.writerow((f"{family}:{i:06d}", family, parameter,
                                    format(float(cloud[i, 0]), ".16g"),
                                    format(float(cloud[i, 1]), ".16g")))
    digest = hashlib.sha256()
    with out.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def audit(per_family: int = 250_000, sample_size: int = 128,
          save_data: Path | None = None) -> dict:
    if type(sample_size) is not int or not 2 <= sample_size <= 128 or sample_size > per_family:
        raise ValueError("sample_size outside 2..min(128,per_family)")
    t0 = perf_counter()
    features = parameter_features(per_family)
    assert sum(len(v) for v in features.values()) == 4 * per_family
    x = np.linspace(0, per_family - 1, sample_size).round().astype(np.int64)
    per_family_summaries = {}
    calibration = {}
    for family, full in features.items():
        if family == "hurwitz":
            assert np.all(np.diff(full, axis=0) < 0)
        if family == "cycle_spectral":
            assert np.all(np.diff(full, axis=0) > 0)
        if family == "full_shift_dynamical":
            assert np.all(np.diff(full, axis=0) > 0)
        normalized = norm_features(full)
        if family == "cycle_ihara":
            assert np.all(full == full[0])
            # The N distinct graph zeta functions map to ONE measured
            # observation under adaptive probes u_n=e^{-tau/n}.
            unique_sample = normalized[[0]]
            h0_max = 0.0
            h0_med = 0.0
        else:
            deaths = monotone_h0_deaths(normalized)
            h0_max = float(np.max(deaths))
            h0_med = float(np.median(deaths))
            unique_sample = normalized[x]
        bets = {str(r): rips_betti01(unique_sample, r) for r in RADII}
        per_family_summaries[family] = {
            "count": per_family,
            "distinct_zeta_functions_by_construction": per_family,
            "sample_unique_feature_points": len(unique_sample),
            "normalized_h0_max_death_full_cloud": h0_max,
            "normalized_h0_median_death_full_cloud": h0_med,
            "feature_min": full.min(axis=0).tolist(),
            "feature_max": full.max(axis=0).tolist(),
            "rips_sample_betti_by_scale": bets,
            "any_sample_h1": any(v["betti1"] > 0 for v in bets.values()),
        }
        if family == "cycle_ihara":
            per_family_summaries[family]["normalization_alias"] = (
                "Every C_n yields the same pair of log Ihara values "
                "at variant-dependent probes u_n=exp(-1/n), exp(-2/n); "
                "this does not mean the Ihara zeta functions are equal."
            )
    control = circle_control(sample_size)
    calibration["circle_positive_control"] = {
        str(r): rips_betti01(control, r) for r in RADII
    }
    line = np.column_stack((np.linspace(0, 1, sample_size),
                            np.linspace(0, 1, sample_size)))
    calibration["line_negative_control"] = {
        str(r): rips_betti01(line, r) for r in RADII
    }
    # Fixed-seed permutation-null sensitivity: scramble ONLY the second
    # descriptor coordinate among the same selected functions, destroying
    # their zeta-derived parameter pairing. This is a diagnostic, not
    # evidence of intrinsic arithmetic topology.
    shuffle = {}
    for family in ("hurwitz", "cycle_spectral", "full_shift_dynamical"):
        base = norm_features(features[family])[x]
        b1s = []
        for seed in range(101, 113):
            permuted = base.copy()
            permuted[:, 1] = base[np.random.default_rng(seed).permutation(len(base)), 1]
            b1s.append(int(rips_betti01(permuted, 0.12)["betti1"]))
        shuffle[family] = {
            "permutations": len(b1s),
            "radius": 0.12,
            "betti1_values": b1s,
            "nonzero_h1_count": sum(t > 0 for t in b1s),
            "interpretation": "Feature-pairing-breaking negative control; not alternative zeta functions",
        }
    if not any(v["betti1"] == 1 for v in calibration["circle_positive_control"].values()):
        raise AssertionError("TDA positive control failed to detect circle H1")
    if any(v["betti1"] != 0 for v in calibration["line_negative_control"].values()):
        raise AssertionError("TDA negative control produced phantom circle")

    # Graph-spectral -> Riemann bridge. These are classical exact
    # special-value identities, not conjectures discovered by clustering.
    # Delta(C_n) has eigenvalues 4*sin(pi*j/n)^2, 1 <= j < n.
    # (2*pi/n)^2 Z_Delta(1) = 2*zeta(2)*(1-1/n^2).
    # (2*pi/n)^4 Z_Delta(2) = 2*zeta(4)*(1+10/n^2-11/n^4).
    # Independently compare spectral sums for the first 30 cycles.
    for n in range(3, min(per_family + 3, 33)):
        eigen = 4.0 * np.sin(np.pi * np.arange(1, n) / n) ** 2
        zz1 = np.sum(eigen**(-1))
        zz2 = np.sum(eigen**(-2))
        assert np.isclose(zz1, (n*n-1)/12, rtol=1e-10, atol=1e-10)
        assert np.isclose(zz2, (n**4+10*n*n-11)/720, rtol=1e-10, atol=1e-10)

    n_last = per_family + 2
    spectral_riemann_bridge = {
        "hurwitz_anchor": "zeta(s,1)=Riemann zeta(s)",
        "cycle_limit_s1": "lim_(n→∞)(2π/n)^2 Z_Delta,Cn(1) = 2*zeta(2) = π²/3",
        "cycle_limit_s2": "lim_(n→∞)(2π/n)^4 Z_Delta,Cn(2) = 2*zeta(4) = π⁴/45",
        "s1_exact_relative_error": "-1/n²",
        "s2_exact_relative_error": "+10/n²-11/n⁴",
        "largest_cycle_n": n_last,
        "largest_cycle_absolute_relative_error_s1": 1.0/(n_last*n_last),
        "largest_cycle_absolute_relative_error_s2": 10.0/(n_last*n_last)-11.0/(n_last**4),
        "verification": "Exact closed-form expressions plus finite independent eigenvalue checks; no general theorem inferred from numerics",
    }

    sha256 = None
    if save_data is not None:
        save_data.parent.mkdir(parents=True, exist_ok=True)
        sha256 = _csv_manifest(features, per_family, save_data)
    report = {
        "research_track": "ResearchOS-TECT-X-ZETA-TDA-ONE-MILLION",
        "status": "BOUNDED_NUMERICAL_TOPOLOGICAL_AUDIT_NOT_CERTIFIED",
        "count_total": 4 * per_family,
        "count_per_family": per_family,
        "sample_size_per_family_for_betti01": sample_size,
        "fixed_radii": list(RADII),
        "families": per_family_summaries,
        "tda_controls": calibration,
        "feature_permutation_sensitivity": shuffle,
        "cross_zeta_link": {
            "common_graph": "unweighted cycle C_n",
            "ihara_formula": "Z_Cn(u)=(1-u^n)^(-2)",
            "first_nonconstant_ihara_taylor_degree": "n",
            "cycle_spectral_zeta_at_1": "(n^2-1)/12",
            "cycle_spectral_zeta_at_2": "(n^4+10n^2-11)/720",
            "underlying_cycle_graph_betti1": 1,
            "nonbacktracking_dynamical_bridge": "Ihara(C_n,u)=Artin-Mazur zeta of the two oriented nonbacktracking n-cycles",
            "riemann_bridge": spectral_riemann_bridge,
            "relationship": "Both distinct graph-zeta constructions encode n, but feature-point-cloud H1 does not equal graph H1."
        },
        "hurwitz_normalization": "zeta(s,a) for a=1+(i+1/2)/N, s=2,3; polygamma double precision",
        "full_shift_normalization": "Artin-Mazur zeta_k(u)=1/(1-k*u), k=i+2; features log(k),2log(k)",
        "cycle_spectral_normalization": "Finite Laplacian spectral zeta_Cn(s) at s=1,2; log features",
        "ihara_normalization": "log(Z_Cn(exp(-1/n))), log(Z_Cn(exp(-2/n))); intentionally nonidentifying probe",
        "computation": {
            "tda_method": "finite-radius Vietoris-Rips degree-0 and degree-1 Betti numbers of 2-skeleton, GF(2), at <=128 sample points",
            "full_data_H0": "computed analytically from consecutive-neighbor MST for monotone descriptor curves",
            "numeric_precision": "IEEE 754 float64, no interval certification",
            "dataset_sha256": sha256,
            "dataset_compressed_csv": str(save_data.name) if save_data else None,
            "runtime_seconds": round(perf_counter()-t0, 4),
        },
        "limitations": [
            "1 million distinct members of four parameterized families, not 1 million verified zero sets",
            "Only real special values or normalized probes; no evaluation or isolation of complex zeros",
            "Point-cloud Vietoris-Rips topology depends on feature embedding, scale, and subsampling",
            "Family feature spaces are not a shared invariant metric across unrelated zeta constructions",
            "All C_n graph Betti_1 are 1, which is not a claim about descriptor-cloud Betti_1",
            "No Riemann hypothesis, BSD, Selmer-group, or spectral correspondence proof",
            "No claim of mathematical novelty or external mathematical review",
        ],
        "rh_proof": False,
        "bsd_proof": False,
        "new_functional_equation_proved": False,
        "independent_math_review": False,
    }
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-family", type=int, default=250_000)
    parser.add_argument("--sample-size", type=int, default=128)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--dataset", type=Path)
    args = parser.parse_args(argv)
    result = audit(args.per_family, args.sample_size, args.dataset)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "total_variants": result["count_total"],
        "per_family": result["count_per_family"],
        "tda_sample_size": result["sample_size_per_family_for_betti01"],
        "sample_any_h1": {k: v["any_sample_h1"] for k, v in result["families"].items()},
        "circle_positive_control_h1_detected": any(
            v["betti1"] > 0 for v in result["tda_controls"]["circle_positive_control"].values()
        ),
        "runtime_seconds": result["computation"]["runtime_seconds"],
        "status": result["status"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

