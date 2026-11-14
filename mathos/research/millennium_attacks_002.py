"""Research attempt 002: exact nonlinear ABC Navier--Stokes and 3-CNF refutations.

The ABC field is on the periodic torus (not finite-energy R^3).
A resolution refutation is a certificate for one easy unsatisfiable 3-CNF family,
NOT a lower bound for general 3-SAT or a result about P vs NP.
Only Python standard-library arithmetic is used; Fourier coefficients are
half-integer complex numbers represented exactly by binary floating point.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import product
import json

from mathos.research.millennium_attacks_001 import parity_cycle_2cnf

Mode = tuple[int, int, int]
Vector = tuple[complex, complex, complex]
VectorField = dict[Mode, Vector]
ScalarField = dict[Mode, complex]
Clause3 = tuple[int, ...]

ZERO = (0j, 0j, 0j)


def _compress_vector(data: dict[Mode, Vector]) -> VectorField:
    return {k: v for k, v in data.items() if any(c != 0 for c in v)}


def _compress_scalar(data: dict[Mode, complex]) -> ScalarField:
    return {k: v for k, v in data.items() if v != 0}


def abc_modes() -> VectorField:
    """A=B=C=1 ABC Beltrami field as exact Fourier coefficients."""
    field: dict[Mode, list[complex]] = defaultdict(lambda: [0j, 0j, 0j])

    def sin(component: int, axis: int) -> None:
        positive = tuple(int(j == axis) for j in range(3))
        negative = tuple(-z for z in positive)
        field[positive][component] -= 0.5j
        field[negative][component] += 0.5j

    def cos(component: int, axis: int) -> None:
        positive = tuple(int(j == axis) for j in range(3))
        negative = tuple(-z for z in positive)
        field[positive][component] += 0.5
        field[negative][component] += 0.5

    sin(0, 2)  # sin z
    cos(0, 1)  # cos y
    sin(1, 0)  # sin x
    cos(1, 2)  # cos z
    sin(2, 1)  # sin y
    cos(2, 0)  # cos x
    return {k: tuple(v) for k, v in field.items()}


def divergence(field: VectorField) -> ScalarField:
    return _compress_scalar({k: 1j * sum(k[j] * v[j] for j in range(3))
                             for k, v in field.items()})


def curl(field: VectorField) -> VectorField:
    answer = {}
    for k, v in field.items():
        answer[k] = (
            1j * (k[1] * v[2] - k[2] * v[1]),
            1j * (k[2] * v[0] - k[0] * v[2]),
            1j * (k[0] * v[1] - k[1] * v[0]),
        )
    return _compress_vector(answer)


def laplacian(field: VectorField) -> VectorField:
    return _compress_vector({k: tuple(-sum(q * q for q in k) * v[j]
                                      for j in range(3)) for k, v in field.items()})


def convection(field: VectorField) -> VectorField:
    """Exact Fourier coefficients of (u dot grad)u, not a linearization."""
    out: dict[Mode, list[complex]] = defaultdict(lambda: [0j, 0j, 0j])
    for p, vp in field.items():
        for q, vq in field.items():
            k = tuple(p[j] + q[j] for j in range(3))
            scalar = 1j * sum(vp[j] * q[j] for j in range(3))
            for j in range(3):
                out[k][j] += scalar * vq[j]
    return _compress_vector({k: tuple(v) for k, v in out.items()})


def half_squared_speed(field: VectorField) -> ScalarField:
    """Fourier coefficients of pointwise (u dot u)/2 (no conjugation)."""
    out: dict[Mode, complex] = defaultdict(complex)
    for p, vp in field.items():
        for q, vq in field.items():
            k = tuple(p[j] + q[j] for j in range(3))
            out[k] += 0.5 * sum(vp[j] * vq[j] for j in range(3))
    return _compress_scalar(out)


def gradient(field: ScalarField) -> VectorField:
    return _compress_vector({k: tuple(1j * k[j] * v for j in range(3))
                             for k, v in field.items()})


def negative_vector(field: VectorField) -> VectorField:
    return {k: tuple(-v for v in coeffs) for k, coeffs in field.items()}


def abc_identities() -> dict[str, object]:
    """Symbolically check div U=0, curl U=U, Delta U=-U,
    (U dot grad)U=grad(|U|^2/2), yielding exact nonlinear NS solution
    u(t)=exp(-nu*t)U, p(t)=-exp(-2nu*t)|U|^2/2, for any nu>0.
    """
    field = abc_modes()
    energy = half_squared_speed(field)
    velocity_mean_square = 2 * energy.get((0, 0, 0), 0)
    nonlinearity = convection(field)
    return {
        "divergence_zero": not divergence(field),
        "curl_equals_velocity": curl(field) == field,
        "laplacian_equals_negative_velocity": laplacian(field) == negative_vector(field),
        "convection_equals_pressure_gradient_cancelled": nonlinearity == gradient(energy),
        "convection_nonzero": bool(nonlinearity),
        "mean_squared_speed": velocity_mean_square.real,
        "velocity_modes": len(field),
        "nonlinear_modes": len(nonlinearity),
    }


def _canonical(clause: tuple[int, ...]) -> Clause3:
    if any(type(x) is not int or x == 0 for x in clause):
        raise ValueError("nonzero integer literals required")
    result = tuple(sorted(set(clause)))
    if any(-x in result for x in result):
        raise ValueError("tautological clauses are excluded from the certificate")
    return result


def lift_parity_cycle_3cnf(n: int) -> tuple[Clause3, ...]:
    """Lift each (a OR b) to (a OR b OR z) AND (a OR b OR not z).

    Uses 2*n fresh auxiliaries. Each pair is pointwise equivalent to a OR b,
    *regardless of the fresh variable's assignment*. All clauses size three.
    """
    base = parity_cycle_2cnf(n)
    result = []
    for j, (a, b) in enumerate(base):
        z = n + j + 1
        result.extend((_canonical((a, b, z)), _canonical((a, b, -z))))
    return tuple(result)


def _resolve(left: Clause3, right: Clause3, pivot: int) -> Clause3:
    if type(pivot) is not int or pivot <= 0:
        raise ValueError("positive integer pivot required")
    if pivot in left and -pivot in right:
        return _canonical(tuple(x for x in left if x != pivot) +
                          tuple(x for x in right if x != -pivot))
    if -pivot in left and pivot in right:
        return _canonical(tuple(x for x in left if x != -pivot) +
                          tuple(x for x in right if x != pivot))
    raise ValueError("parents lack a complementary pivot")


def resolution_refutation(n: int) -> dict[str, object]:
    """Construct an O(n)-step resolution proof ending with empty clause."""
    initial = lift_parity_cycle_3cnf(n)
    known: list[Clause3] = list(initial)
    steps: list[dict[str, object]] = []

    def add(left: int, right: int, pivot: int) -> int:
        derived = _resolve(known[left], known[right], pivot)
        steps.append({"left": left, "right": right, "pivot": pivot,
                      "clause": list(derived)})
        known.append(derived)
        return len(known) - 1

    binary_indices: list[int] = []
    for j in range(2 * n):
        binary_indices.append(add(2 * j, 2 * j + 1, n + j + 1))

    forward = binary_indices[0]    # (-1, 2)
    backward = binary_indices[1]   # (1, -2)
    for i in range(2, n):
        forward = add(forward, binary_indices[2 * (i - 1)], i)
        backward = add(backward, binary_indices[2 * (i - 1) + 1], i)

    positive = add(backward, binary_indices[2 * n - 2], n)
    negative = add(forward, binary_indices[2 * n - 1], n)
    final = add(positive, negative, 1)
    assert known[final] == ()
    return {"original_variables": n, "total_variables": 3 * n,
            "initial_clauses": [list(c) for c in initial], "steps": steps,
            "last_clause_index": final}


def verify_resolution_refutation(proof: dict[str, object]) -> bool:
    """Independently replay resolution steps and demand a derived empty clause."""
    if type(proof) is not dict or type(proof.get("original_variables")) is not int:
        return False
    n = proof["original_variables"]
    if n < 3 or proof.get("total_variables") != 3 * n:
        return False
    if type(proof.get("initial_clauses")) is not list or type(proof.get("steps")) is not list:
        return False
    if proof["initial_clauses"] != [list(c) for c in lift_parity_cycle_3cnf(n)]:
        return False
    known: list[Clause3] = list(lift_parity_cycle_3cnf(n))
    try:
        for step in proof["steps"]:
            left, right, pivot = step["left"], step["right"], step["pivot"]
            if any(type(x) is not int for x in (left, right, pivot)):
                return False
            if left < 0 or right < 0 or left >= len(known) or right >= len(known):
                return False
            derived = _resolve(known[left], known[right], pivot)
            if step["clause"] != list(derived):
                return False
            known.append(derived)
    except (ValueError, KeyError, TypeError, IndexError):
        return False
    return proof.get("last_clause_index") == len(known) - 1 and known[-1] == ()


def brute_force_3cnf_unsat(n: int) -> bool:
    """Independent exhaustive check for n<=4 (up to 12 variables)."""
    if type(n) is not int or n < 3 or n > 4:
        raise ValueError("exhaustive check supported for n=3 or 4")
    clauses = lift_parity_cycle_3cnf(n)
    for assignment in product((False, True), repeat=3 * n):
        if all(any(assignment[abs(lit) - 1] == (lit > 0) for lit in clause)
               for clause in clauses):
            return False
    return True


def research_report() -> dict:
    abc = abc_identities()
    sizes = (3, 4, 6, 8, 12, 20)
    return {
        "research_attempt": "millennium-attacks-002",
        "certification": "NOT_CERTIFIED",
        "navier_stokes": {
            "domain": "3D flat torus, periodic boundary conditions",
            "object": "exact smooth unforced nonlinear Navier-Stokes Beltrami solution",
            "identities": abc,
            "solution": "u=exp(-nu*t)*U, p=-exp(-2*nu*t)*|U|^2/2",
            "not_proved": "global regularity for arbitrary R3 initial data",
        },
        "p_vs_np": {
            "family": "3-CNF parity cycles from fresh-variable clause lifting",
            "no_lower_bound_claim": True,
            "proofs": [
                {"n": n, "variables": 3 * n, "clauses": 4 * n,
                 "resolution_steps": len(resolution_refutation(n)["steps"]),
                 "refutation_verified": verify_resolution_refutation(resolution_refutation(n))}
                for n in sizes
            ],
            "not_proved": "general 3-SAT hardness, P vs NP, or unrestricted lower bounds",
        },
    }


def main() -> None:
    print(json.dumps(research_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
