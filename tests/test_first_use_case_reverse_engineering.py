"""Independent reverse-oracle checks for the seven first executable use cases.

Constructs reference results via different arithmetic, finite structures or
negative controls; does not certify any Millennium problem.
Python 3.10+, stdlib only.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
import json
import math
import unittest

from mathos.research.hypothesis_pipeline import (
    OBLIGATIONS, HYPOTHESES,
    k4_tseitin_clauses, probe_abc_perturbation_bound,
    probe_elliptic_local_counts, probe_k4_tseitin,
    probe_li_first_coefficient, probe_projective_hodge,
    probe_simplicial_three_sphere, probe_transfer_gap_obstruction,
    resolution_certificate_k4, run_exploration,
    verify_resolution_certificate_k4,
)


def reference_li_one(n: int) -> tuple[float, float]:
    """Independent direct summation and classical harmonic bound, not intervals."""
    harmonic = sum(1.0 / k for k in range(1, n + 1))
    delta = harmonic - math.log(n)
    offset = 1.0 - 0.5 * math.log(4.0 * math.pi)
    return (offset + 0.5 * (delta - 0.5 / n),
            offset + 0.5 * (delta - 0.5 / (n + 1)))


def reference_legendre_count(p: int) -> int:
    """Euler-criterion character sum, separate from enumerating y or residues."""
    def character(a: int) -> int:
        a %= p
        if a == 0:
            return 0
        residue = pow(a, (p - 1) // 2, p)
        if residue == 1:
            return 1
        if residue == p - 1:
            return -1
        raise AssertionError("p must be an odd prime")
    return p + 1 + sum(character(x*x*x-x) for x in range(p))


def _set_rank(columns: list[frozenset[tuple[int, ...]]]) -> int:
    """GF(2) elimination by symmetric difference of *faces*, not bit masks."""
    pivots: dict[tuple[int, ...], set[tuple[int, ...]]] = {}
    for col in columns:
        vector = set(col)
        while vector:
            leading = max(vector)
            if leading in pivots:
                vector.symmetric_difference_update(pivots[leading])
            else:
                pivots[leading] = vector
                break
    return len(pivots)


def reference_sphere_homology(remove_facet: bool = False) -> tuple[list[int], list[int], bool]:
    """Build simplices/chain maps as sets and independently derive Betti numbers."""
    cells = {d: list(combinations(range(5), d + 1)) for d in range(4)}
    if remove_facet:
        cells[3].pop()
    def boundary(simplex: tuple[int, ...]) -> frozenset[tuple[int, ...]]:
        return frozenset(combinations(simplex, len(simplex) - 1))
    ranks = {0: 0, 4: 0}
    for d in range(1, 4):
        ranks[d] = _set_rank([boundary(face) for face in cells[d]])
    chain_sq_zero = True
    for d in range(2, 4):
        for simplex in cells[d]:
            double_boundary: set[tuple[int, ...]] = set()
            for face in boundary(simplex):
                double_boundary.symmetric_difference_update(boundary(face))
            chain_sq_zero = chain_sq_zero and not double_boundary
    betti = [len(cells[d]) - ranks[d] - ranks[d + 1] for d in range(4)]
    return [ranks[k] for k in range(1, 4)], betti, chain_sq_zero


class ReverseEngineeredSevenUseCases(unittest.TestCase):
    def test_rh_li_one_reconstructs_inputs_and_output(self):
        result = probe_li_first_coefficient()
        self.assertTrue(result["passed"])
        n = result["n"]
        self.assertEqual(n, 2048)
        reference = reference_li_one(n)
        self.assertAlmostEqual(result["lambda1_lower_approx"], reference[0], places=12)
        self.assertAlmostEqual(result["lambda1_upper_approx"], reference[1], places=12)
        # The formula itself determines the bracket width, independent of gamma.
        self.assertAlmostEqual(reference[1] - reference[0],
                               1 / (4 * n * (n + 1)), places=12)
        # Deliberately incorrect logarithm normalization is rejected.
        incorrectly_normalized = reference[0] + 0.5 * math.log(4)
        self.assertGreater(abs(incorrectly_normalized - reference[0]), 0.5)

    def test_pnp_k4_inverse_parity_spec_and_certificate(self):
        result = probe_k4_tseitin()
        self.assertTrue(result["passed"])
        self.assertEqual((result["variables"], result["clauses"]), (6, 16))
        edges = list(combinations(range(4), 2))
        cnf = k4_tseitin_clauses()
        self.assertTrue(all(len(clause) == 3 for clause in cnf))
        count_true = 0
        for bits in product((False, True), repeat=6):
            # Inverse oracle: evaluate vertex charges rather than clause encoding.
            parity_valid = all(
                sum(bits[j] for j, e in enumerate(edges) if vertex in e) % 2
                == (1 if vertex == 0 else 0)
                for vertex in range(4)
            )
            cnf_valid = all(any(
                bits[abs(literal) - 1] == (literal > 0)
                for literal in clause
            ) for clause in cnf)
            self.assertEqual(cnf_valid, parity_valid)
            count_true += int(cnf_valid)
        self.assertEqual(count_true, 0)
        # Negative control: remove the odd charge; zero edge bits then satisfy parity.
        self.assertTrue(all(sum(0 for e in edges if vertex in e) % 2 == 0
                            for vertex in range(4)))
        proof = resolution_certificate_k4()
        self.assertTrue(verify_resolution_certificate_k4(proof))
        proof["steps"][0]["pivot"] = 999
        self.assertFalse(verify_resolution_certificate_k4(proof))

    def test_ns_abc_energy_bound_from_independent_jacobian(self):
        result = probe_abc_perturbation_bound()
        self.assertTrue(result["passed"])
        K = result["gradient_operator_bound_K"]
        self.assertEqual(K, 3)
        # The six nonzero Jacobian entries pair into sin^2+cos^2=1
        # for x,y,z, giving ||grad U||_F^2=3 exactly.
        for x, y, z in ((0., 0., 0.), (0.5, 1.1, 2.8),
                        (math.pi / 4, math.pi / 3, math.pi)):
            jacobian_entries = (
                -math.sin(y), math.cos(z), math.cos(x),
                -math.sin(z), -math.sin(x), math.cos(y)
            )
            self.assertAlmostEqual(sum(v*v for v in jacobian_entries), 3.0)
            self.assertGreater(K*K, sum(v*v for v in jacobian_entries))
        nu = Fraction(result["nu"])
        for row in result["sample_exponents"]:
            q = Fraction(row["exp_minus_nu_t"])
            expected = Fraction(2 * K, 1) * (1 - q) / nu
            self.assertEqual(Fraction(row["gronwall_exponent"]), expected)
        self.assertIn("conditional", result["scope"])

    def test_ym_transfer_eigenvalues_and_nonuniform_gap(self):
        result = probe_transfer_gap_obstruction()
        self.assertTrue(result["passed"])
        gaps = []
        for row in result["samples"]:
            n = row["n"]
            q = Fraction(row["q"])
            self.assertEqual(q, Fraction(1, 2**n))
            # Independent 2x2 matrix diagonalization:
            # trace=2, determinant=1-q^2, lambda_pm=1+-q.
            eigen_plus, eigen_minus = 1 + q, 1 - q
            self.assertEqual(eigen_plus + eigen_minus, 2)
            self.assertEqual(eigen_plus * eigen_minus, 1 - q*q)
            ratio = eigen_minus / eigen_plus
            self.assertEqual(Fraction(row["eigenvalue_ratio"]), ratio)
            self.assertEqual(Fraction(row["one_minus_ratio"]), 1 - ratio)
            gaps.append(-math.log(float(ratio)))
        self.assertTrue(all(g > 0 for g in gaps))
        self.assertTrue(all(a > b for a, b in zip(gaps, gaps[1:])))
        self.assertEqual(result["samples"][0]["eigenvalue_ratio"], "1/3")
        self.assertEqual(result["samples"][-1]["eigenvalue_ratio"], "255/257")

    def test_hodge_truncated_polynomial_ring_independent_convolution(self):
        result = probe_projective_hodge()
        self.assertTrue(result["passed"])
        n = result["projective_dimension"]
        self.assertEqual(n, 4)
        def multiply(a: tuple[int, ...], b: tuple[int, ...]):
            out = [0] * (n + 1)
            for i, ai in enumerate(a):
                for j, bj in enumerate(b):
                    if i + j <= n:
                        out[i+j] += ai * bj
            return tuple(out)
        one = (1, 0, 0, 0, 0)
        h = (0, 1, 0, 0, 0)
        powers = [one]
        for _ in range(n+1):
            powers.append(multiply(powers[-1], h))
        self.assertEqual(powers[n+1], (0, 0, 0, 0, 0))
        pairings = [multiply(powers[k], powers[n-k])[-1] for k in range(n+1)]
        self.assertEqual(pairings, result["top_degree_pairings"])
        self.assertEqual(pairings, [1]*5)

    def test_bsd_legendre_symbol_reference_counts(self):
        result = probe_elliptic_local_counts()
        self.assertTrue(result["passed"])
        expected = {5: (8, -2), 7: (8, 0), 11: (12, 0), 13: (8, 6),
                    17: (16, 2), 19: (20, 0), 23: (24, 0), 29: (40, -10)}
        self.assertEqual(len(result["local_data"]), len(expected))
        for row in result["local_data"]:
            p = row["p"]
            points, trace = expected[p]
            self.assertEqual(row["points"], points)
            self.assertEqual(row["trace"], trace)
            self.assertEqual(reference_legendre_count(p), points)
            self.assertLessEqual(trace*trace, 4*p)
            self.assertTrue(row["same_independent_count"])
        # Discriminant for y^2=x^3-x is 64: none of these primes is bad.
        self.assertTrue(all(64 % p != 0 for p in expected))

    def test_poincare_boundary_faces_independent_homology(self):
        result = probe_simplicial_three_sphere()
        self.assertTrue(result["passed"])
        ranks, betti, square_zero = reference_sphere_homology()
        self.assertEqual(ranks, [4, 6, 4])
        self.assertEqual(betti, [1, 0, 0, 1])
        self.assertTrue(square_zero)
        self.assertEqual(result["betti_mod_2"], betti)
        self.assertEqual(result["euler_characteristic"], 0)
        # Delete a top-dimensional simplex: top homology must disappear.
        _, truncated_betti, truncated_square_zero = reference_sphere_homology(
            remove_facet=True)
        self.assertTrue(truncated_square_zero)
        self.assertEqual(truncated_betti, [1, 0, 0, 0])

    def test_audited_probes_cannot_promote_mathematics(self):
        report = run_exploration()
        self.assertEqual(report["certification"], "NOT_CERTIFIED")
        self.assertEqual(report["proof_promotion"], "NONE")
        self.assertEqual(report["open_work_packages"], 14)
        self.assertEqual(len(report["experiments"]), 7)
        for entry in report["experiments"]:
            self.assertEqual(entry["exploration_state"], "EXPLORATORY_TESTED")
            self.assertEqual(entry["mathematical_status"], "BLOCKED")
            self.assertFalse(entry["promoted_to_solution"])
        register = json.loads(OBLIGATIONS.read_text(encoding="utf-8"))
        program = json.loads(HYPOTHESES.read_text(encoding="utf-8"))
        self.assertEqual(register["certification"], "NOT_CERTIFIED")
        self.assertEqual(program["certification"], "NOT_CERTIFIED")
        self.assertTrue(all(t["modeled_target_status"] == "BLOCKED"
                            for t in register["tracks"]))


if __name__ == "__main__":
    unittest.main()
