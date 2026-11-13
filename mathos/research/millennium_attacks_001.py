"""Research attack 001: an energy-only PDE barrier and a SAT local-rule barrier.

These are bounded counterexamples to *proposed proof methods*, not solutions of
Navier--Stokes or P versus NP. Uses Python 3.10+ standard library only.

Run: python -m mathos.research.millennium_attacks_001
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
import json


def _positive_rational(value: Fraction | int, name: str) -> Fraction:
    if type(value) not in (int, Fraction):
        raise TypeError(f"{name} must be an int or Fraction")
    result = Fraction(value)
    if result <= 0:
        raise ValueError(f"{name} must be positive")
    return result


def stokes_normalized_l4l6_fourth_power(
    scale: int,
    *,
    viscosity: Fraction | int = 1,
    horizon: Fraction | int = 1,
) -> Fraction:
    """Exact ||u_scale||_{L^4(0,T;L^6)}^4 / ||U(0)||_{L^6}^4.

    Let G(t,x)=s^(-3/2) exp(-|x|^2/s), s=1+4*viscosity*t,
    U=(-d_y G,d_x G,0), and
    u_scale(t,x)=scale^(3/2)*U(scale^2*t,scale*x).

    The exact ratio is scale^2/(24*viscosity)
      * (1-(1+4*viscosity*scale^2*T)^(-6)).
    u_scale solves the *linear heat/Stokes* system, NOT nonlinear NS.
    """
    if type(scale) is not int or scale < 1:
        raise ValueError("scale must be a positive integer")
    nu = _positive_rational(viscosity, "viscosity")
    duration = _positive_rational(horizon, "horizon")
    s = 1 + 4 * nu * scale * scale * duration
    return Fraction(scale * scale, 1) / (24 * nu) * (1 - s ** (-6))


def stokes_lower_bound_fourth_power(
    scale: int,
    *,
    viscosity: Fraction | int = 1,
    horizon: Fraction | int = 1,
) -> Fraction:
    """Exact uniform-in-scale lower bound for scales >= 1.

    The result is normalized by ||U(0)||_6^4, just as the quantity above.
    """
    if type(scale) is not int or scale < 1:
        raise ValueError("scale must be a positive integer")
    nu = _positive_rational(viscosity, "viscosity")
    duration = _positive_rational(horizon, "horizon")
    floor = 1 - (1 + 4 * nu * duration) ** (-6)
    return Fraction(scale * scale, 1) * floor / (24 * nu)


def stokes_initial_l2_scale_exponent() -> Fraction:
    """L2 initial norm exponent under u_lambda=lambda^(3/2) U(lambda*x)."""
    return Fraction(3, 2) - Fraction(3, 2)


def stokes_mixed_l4_l6_scale_exponent() -> Fraction:
    """Mixed spacetime norm exponent under heat scaling, for large horizons."""
    return Fraction(3, 2) - Fraction(3, 6) - Fraction(2, 4)


Clause = tuple[int, int]
CNF = tuple[Clause, ...]


def parity_cycle_2cnf(n: int) -> CNF:
    """Unsatisfiable equality chain with one inequality closing the cycle.

    x1=x2=...=xn, x1!=xn. For n>=3 all 2*n clauses have length two,
    every variable occurs with both signs, and unit/pure simplification stalls.
    """
    if type(n) is not int or n < 3:
        raise ValueError("n must be at least three")
    clauses: list[Clause] = []
    for x in range(1, n):
        y = x + 1
        clauses.extend(((-x, y), (x, -y)))
    clauses.extend(((1, n), (-1, -n)))
    return tuple(clauses)


def _check_cnf(clauses: CNF, n: int) -> None:
    if type(n) is not int or n < 1:
        raise ValueError("n must be positive")
    for clause in clauses:
        if len(clause) != 2:
            raise ValueError("only 2-CNF clauses are supported")
        for literal in clause:
            if type(literal) is not int or literal == 0 or abs(literal) > n:
                raise ValueError("literal outside 1..n")


def unit_pure_status(clauses: CNF, n: int) -> str:
    """Run only unit propagation and pure-literal elimination.

    Returns 'sat', 'unsat' or 'stalled'; 'stalled' is NOT a SAT answer.
    """
    _check_cnf(clauses, n)
    remaining: list[tuple[int, ...]] = [
        tuple(dict.fromkeys(clause))
        for clause in clauses
        if not any(-lit in clause for lit in clause)
    ]
    while True:
        if not remaining:
            return "sat"
        if any(not clause for clause in remaining):
            return "unsat"
        units = [clause[0] for clause in remaining if len(clause) == 1]
        if units:
            chosen = units[0]
        else:
            signs = {lit for clause in remaining for lit in clause}
            pures = sorted((lit for lit in signs if -lit not in signs),
                           key=lambda lit: (abs(lit), lit))
            if not pures:
                return "stalled"
            chosen = pures[0]
        remaining = [tuple(l for l in clause if l != -chosen)
                     for clause in remaining if chosen not in clause]


def two_sat_satisfiable(clauses: CNF, n: int) -> bool:
    """Exact polynomial-time implication-reachability 2-SAT test.

    A 2-CNF is unsatisfiable iff, for some variable x, both x=>not x
    and not x=>x have paths in the implication graph.
    """
    _check_cnf(clauses, n)
    graph: list[list[int]] = [[] for _ in range(2 * n)]

    def node(literal: int) -> int:
        return 2 * (abs(literal) - 1) + (0 if literal > 0 else 1)

    for left, right in clauses:
        graph[node(-left)].append(node(right))
        graph[node(-right)].append(node(left))

    def can_reach(start: int, end: int) -> bool:
        visited = {start}
        pending = [start]
        while pending:
            current = pending.pop()
            if current == end:
                return True
            for dest in graph[current]:
                if dest not in visited:
                    visited.add(dest)
                    pending.append(dest)
        return False

    return not any(can_reach(2 * i, 2 * i + 1)
                   and can_reach(2 * i + 1, 2 * i)
                   for i in range(n))


def brute_force_satisfiable(clauses: CNF, n: int) -> bool:
    """Small-n independent baseline; deliberate n<=14 resource limit."""
    _check_cnf(clauses, n)
    if n > 14:
        raise ValueError("brute-force baseline limited to 14 variables")
    for assignment in product((False, True), repeat=n):
        if all((assignment[abs(a) - 1] == (a > 0)) or
               (assignment[abs(b) - 1] == (b > 0))
               for a, b in clauses):
            return True
    return False


def experiment_report() -> dict:
    """Finite exact examples only; the analytic infinite-family arguments
    are written separately in the accompanying mathematical note.
    """
    ns_scales = (1, 2, 4, 8, 16, 32)
    sat_sizes = (3, 4, 6, 8, 10)
    return {
        "experiment": "millennium-attacks-001",
        "certification": "NOT_CERTIFIED",
        "navier_stokes": {
            "object": "smooth divergence-free *linear Stokes heat flows*",
            "finding": "L2 initial energy alone does not bound critical L4_t L6_x",
            "not_proved": "any nonlinear Navier-Stokes breakdown or global regularity",
            "L2_initial_scaling_exponent": str(stokes_initial_l2_scale_exponent()),
            "mixed_norm_scaling_exponent": str(stokes_mixed_l4_l6_scale_exponent()),
            "normalized_L4L6_fourth_powers": [
                {"scale": scale,
                 "exact_ratio": str(stokes_normalized_l4l6_fourth_power(scale)),
                 "exact_lower_bound": str(stokes_lower_bound_fourth_power(scale))}
                for scale in ns_scales
            ],
        },
        "p_vs_np": {
            "object": "unsatisfiable 2-CNF parity cycles",
            "finding": "unit and pure-literal simplification do not decide all 2-CNF",
            "not_proved": "any lower bound for general SAT or P != NP",
            "cases": [
                {
                    "variables": n,
                    "clauses": len(parity_cycle_2cnf(n)),
                    "unit_pure": unit_pure_status(parity_cycle_2cnf(n), n),
                    "two_sat_satisfiable": two_sat_satisfiable(parity_cycle_2cnf(n), n),
                    "brute_force_satisfiable": brute_force_satisfiable(parity_cycle_2cnf(n), n),
                }
                for n in sat_sizes
            ],
        },
    }


def main() -> None:
    print(json.dumps(experiment_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
