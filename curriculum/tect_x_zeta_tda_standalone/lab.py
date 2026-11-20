"""Standalone lab: finite cycle-zeta identities and Vietoris--Rips homology.

Only Python 3.11+ standard-library modules are used. This program computes
FINITE graph and point-cloud examples; it does not search for Riemann zeta
zeros and does not prove or disprove RH, BSD, or any Selmer conjecture.

Usage: python lab.py [--radius 1.0]
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import combinations
import json
import math
from typing import Sequence


def _graph_size(n: int) -> None:
    if type(n) is not int or not 3 <= n <= 10_000:
        raise ValueError("cycle size n must be an exact integer in 3..10000")


def cycle_spectral_zeta(n: int, s: int) -> float:
    """Direct nonzero cycle-Laplacian eigenvalue sum, s in {1,2}."""
    _graph_size(n)
    if type(s) is not int or s not in (1, 2):
        raise ValueError("spectral exponent must be 1 or 2")
    return math.fsum(
        (4.0 * math.sin(math.pi * j / n) ** 2) ** (-s)
        for j in range(1, n)
    )


def cycle_spectral_closed(n: int, s: int) -> Fraction:
    """Exact known formulas for a cycle C_n; standard finite identities."""
    _graph_size(n)
    if type(s) is not int or s not in (1, 2):
        raise ValueError("spectral exponent must be 1 or 2")
    if s == 1:
        return Fraction(n * n - 1, 12)
    return Fraction(n**4 + 10 * n * n - 11, 720)


def cycle_ihara(n: int, u: float) -> float:
    """(1-u**n)**-2 for an undirected cycle, evaluated for 0<u<1."""
    _graph_size(n)
    if not isinstance(u, (int, float)) or isinstance(u, bool):
        raise ValueError("u must be a real number in (0,1)")
    u = float(u)
    if not math.isfinite(u) or not 0.0 < u < 1.0:
        raise ValueError("u must be a finite real in (0,1)")
    return (1.0 - u**n) ** -2


def cycle_ihara_adaptive(t: float) -> float:
    """The exact-in-n adaptive-probe value, (1-exp(-t))**-2."""
    if not isinstance(t, (int, float)) or isinstance(t, bool):
        raise ValueError("t must be positive and finite")
    t = float(t)
    if not math.isfinite(t) or not t > 0:
        raise ValueError("t must be positive and finite")
    return (-math.expm1(-t)) ** -2


def rank_f2_bitvectors(vectors: Sequence[int]) -> int:
    """Column rank over F_2 using integer-bitset Gaussian elimination."""
    pivots: dict[int, int] = {}
    for vector in vectors:
        if type(vector) is not int or vector < 0:
            raise ValueError("bit vectors must be nonnegative exact integers")
        v = vector
        while v:
            bit = v.bit_length() - 1
            if bit in pivots:
                v ^= pivots[bit]
            else:
                pivots[bit] = v
                break
    return len(pivots)


def rips_betti01(
    points: Sequence[tuple[float, float]], radius: float
) -> dict[str, int]:
    """Betti_0 and Betti_1 for a finite 2D VR 2-skeleton at distance <= r.

    Boundary matrix ranks over F_2 are exact for the combinatorial complex.
    Distance comparisons use Python float64 and are NOT certified intervals.
    Intended for classroom point clouds of at most 25 distinct points.
    """
    if not isinstance(radius, (int, float)) or isinstance(radius, bool):
        raise ValueError("radius must be nonnegative and finite")
    r = float(radius)
    if not math.isfinite(r) or r < 0:
        raise ValueError("radius must be nonnegative and finite")
    n = len(points)
    if not 1 <= n <= 25:
        raise ValueError("point cloud must contain between 1 and 25 points")
    coordinates = []
    for point in points:
        if len(point) != 2:
            raise ValueError("every point must have exactly two coordinates")
        a, b = point
        if any(not isinstance(v, (int, float)) or isinstance(v, bool) for v in (a, b)):
            raise ValueError("point coordinates must be numbers")
        x, y = float(a), float(b)
        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError("point coordinates must be finite")
        coordinates.append((x, y))
    if len(set(coordinates)) != n:
        raise ValueError("point coordinates must be distinct")

    r2 = r * r
    edges: list[tuple[int, int]] = []
    for i, j in combinations(range(n), 2):
        dx = coordinates[i][0] - coordinates[j][0]
        dy = coordinates[i][1] - coordinates[j][1]
        if dx * dx + dy * dy <= r2:
            edges.append((i, j))
    edge_index = {edge: k for k, edge in enumerate(edges)}
    edge_set = set(edges)

    rank_d1 = rank_f2_bitvectors([(1 << i) | (1 << j) for i, j in edges])
    triangle_columns = []
    for i, j, k in combinations(range(n), 3):
        if (i, j) in edge_set and (i, k) in edge_set and (j, k) in edge_set:
            triangle_columns.append(
                (1 << edge_index[(i, j)])
                | (1 << edge_index[(i, k)])
                | (1 << edge_index[(j, k)])
            )
    rank_d2 = rank_f2_bitvectors(triangle_columns)
    beta0 = n - rank_d1
    beta1 = len(edges) - rank_d1 - rank_d2
    if beta0 < 1 or beta1 < 0:
        raise ArithmeticError("invalid chain-complex rank result")
    return {
        "vertices": n,
        "edges": len(edges),
        "triangles": len(triangle_columns),
        "rank_boundary_1": rank_d1,
        "rank_boundary_2": rank_d2,
        "betti_0": beta0,
        "betti_1": beta1,
    }


SQUARE = ((0, 0), (1, 0), (1, 1), (0, 1))
LINE = ((0, 0), (1, 0), (2, 0), (3, 0))


def demo(radius: float = 1.0) -> dict:
    """Return a serializable bounded learning report with no theorem promotion."""
    graphs = []
    for n in (3, 4, 5):
        exact1 = cycle_spectral_closed(n, 1)
        exact2 = cycle_spectral_closed(n, 2)
        direct1 = cycle_spectral_zeta(n, 1)
        direct2 = cycle_spectral_zeta(n, 2)
        if not math.isclose(direct1, float(exact1), rel_tol=1e-11):
            raise ArithmeticError("spectral s=1 identity check failed")
        if not math.isclose(direct2, float(exact2), rel_tol=1e-11):
            raise ArithmeticError("spectral s=2 identity check failed")
        graphs.append({
            "cycle_size": n,
            "spectral_s1_exact": str(exact1),
            "spectral_s2_exact": str(exact2),
            "spectral_s1_numeric": direct1,
            "spectral_s2_numeric": direct2,
            "graph_betti_1": 1,
        })
    fixed_u = 0.5
    adaptive_t = 1
    aliases = [
        {"n": n, "ihara_fixed_probe": cycle_ihara(n, fixed_u),
         "ihara_adaptive_probe": cycle_ihara(n, math.exp(-adaptive_t / n))}
        for n in (3, 4, 5)
    ]
    return {
        "status": "BOUNDED_EDUCATIONAL_DEMO_NOT_RH_PROOF",
        "graphs": graphs,
        "fixed_u": fixed_u,
        "adaptive_t": adaptive_t,
        "adaptive_formula_n_independent": cycle_ihara_adaptive(adaptive_t),
        "ihara_probes": aliases,
        "square_at_radius": rips_betti01(SQUARE, radius),
        "square_filled_at_sqrt2": rips_betti01(SQUARE, math.sqrt(2)),
        "line_at_radius_one": rips_betti01(LINE, 1.0),
        "distance_precision": "Python IEEE-754 float; threshold equality is not interval-certified",
        "rh_proved": False,
        "bsd_proved": False,
        "selmer_infinitude_proved": False,
        "genuine_riemann_zero_count": 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radius", type=float, default=1.0)
    args = parser.parse_args(argv)
    print(json.dumps(demo(args.radius), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
