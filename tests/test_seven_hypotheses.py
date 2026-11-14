"""End-to-end checks for all seven blocked-but-explorable hypothesis tracks."""
from __future__ import annotations

import copy
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest

from mathos.research.hypothesis_pipeline import (
    HYPOTHESES, OBLIGATIONS, EXPECTED_PROBES,
    _gf2_rank, k4_tseitin_clauses, probe_abc_perturbation_bound,
    probe_elliptic_local_counts, probe_k4_tseitin,
    probe_li_first_coefficient, probe_projective_hodge,
    probe_simplicial_three_sphere, probe_transfer_gap_obstruction,
    resolution_certificate_k4, run_exploration,
    verify_resolution_certificate_k4,
)


class SevenHypothesisCoverageTests(unittest.TestCase):
    def test_all_seven_tracks_execute_without_promotion(self):
        report = run_exploration()
        self.assertEqual(report["certification"], "NOT_CERTIFIED")
        self.assertEqual(report["proof_promotion"], "NONE")
        self.assertTrue(report["allow_blocked_exploration"])
        self.assertTrue(report["all_probes_passed"])
        self.assertEqual(report["open_work_packages"], 14)
        self.assertEqual(len(report["experiments"]), 7)
        self.assertEqual({x["model_key"] for x in report["experiments"]},
                         set(EXPECTED_PROBES))
        for experiment in report["experiments"]:
            self.assertEqual(experiment["exploration_state"], "EXPLORATORY_TESTED")
            self.assertEqual(experiment["mathematical_status"], "BLOCKED")
            self.assertEqual(experiment["certification"], "NOT_CERTIFIED")
            self.assertFalse(experiment["promoted_to_solution"])
            self.assertTrue(experiment["probe_result"]["passed"])
            self.assertTrue(experiment["next_lemma"])
            self.assertTrue(experiment["missing_global_step"])

    def test_source_register_remains_byte_identical(self):
        before = OBLIGATIONS.read_bytes()
        run_exploration()
        self.assertEqual(before, OBLIGATIONS.read_bytes())

    def test_external_poincare_status_stays_external(self):
        data = json.loads(OBLIGATIONS.read_text())
        self.assertEqual(data["certification"], "NOT_CERTIFIED")
        self.assertEqual(data["external_result"]["graph_state"], "established_external")
        self.assertEqual(run_exploration()["external_poincare"],
                         "ESTABLISHED_EXTERNALLY_ONLY")
        self.assertTrue(all(x["modeled_target_status"] == "BLOCKED"
                            for x in data["tracks"]))

    def _tampered_run(self, modify_register=None, modify_hypotheses=None):
        with tempfile.TemporaryDirectory() as tmp:
            rp, hp = Path(tmp) / "register.json", Path(tmp) / "hypotheses.json"
            record = json.loads(OBLIGATIONS.read_text())
            program = json.loads(HYPOTHESES.read_text())
            if modify_register:
                modify_register(record)
            if modify_hypotheses:
                modify_hypotheses(program)
            rp.write_text(json.dumps(record), encoding="utf-8")
            hp.write_text(json.dumps(program), encoding="utf-8")
            return run_exploration(rp, hp)

    def test_reject_certification_promotion_in_register(self):
        with self.assertRaises(ValueError):
            self._tampered_run(modify_register=lambda r: r.update(certification="CERTIFIED"))

    def test_reject_closed_math_obligation(self):
        def mutate(record):
            record["tracks"][0]["work_packages"][0]["graph_state"] = "closed"
        with self.assertRaises(ValueError):
            self._tampered_run(modify_register=mutate)

    def test_reject_wrong_probe_mapping(self):
        def mutate(program):
            program["experiments"][0]["bounded_probe"] = "k4_tseitin"
        with self.assertRaises(ValueError):
            self._tampered_run(modify_hypotheses=mutate)

    def test_reject_fake_novelty_and_duplicate_tracks(self):
        def novelty(program):
            program["experiments"][0]["novelty_claim"] = True
        with self.assertRaises(ValueError):
            self._tampered_run(modify_hypotheses=novelty)
        def duplicate(program):
            program["experiments"][1]["model_key"] = program["experiments"][0]["model_key"]
        with self.assertRaises(ValueError):
            self._tampered_run(modify_hypotheses=duplicate)


class BoundedMathematicalProbesTests(unittest.TestCase):
    def test_li_one_positive_but_only_finite_numerical_check(self):
        result = probe_li_first_coefficient()
        self.assertTrue(result["passed"])
        self.assertGreater(result["lambda1_lower_approx"], 0.02)
        self.assertLess(result["lambda1_upper_approx"], 0.03)
        self.assertIn("not certified intervals", result["scope"])

    def test_k4_parity_unsatisfiability_and_replay(self):
        result = probe_k4_tseitin()
        self.assertTrue(result["passed"])
        self.assertEqual(result["variables"], 6)
        self.assertEqual(result["clauses"], 16)
        self.assertEqual(result["satisfying_assignments"], 0)
        self.assertTrue(result["refutation_verified"])
        self.assertGreater(result["resolution_steps"], 0)
        self.assertTrue(all(len(c) == 3 for c in k4_tseitin_clauses()))

    def test_k4_certificate_rejects_tampering(self):
        valid = resolution_certificate_k4()
        self.assertTrue(verify_resolution_certificate_k4(valid))
        for tamper in ("wrong_pivot", "future_parent", "wrong_resolvent",
                       "missing_last", "delete_step"):
            trial = copy.deepcopy(valid)
            if tamper == "wrong_pivot":
                trial["steps"][0]["pivot"] = 999
            elif tamper == "future_parent":
                trial["steps"][0]["left"] = 2000
            elif tamper == "wrong_resolvent":
                trial["steps"][0]["clause"] = [100]
            elif tamper == "missing_last":
                trial["last"] = 0
            else:
                trial["steps"].pop()
            with self.subTest(tamper=tamper):
                self.assertFalse(verify_resolution_certificate_k4(trial))

    def test_navier_stokes_conditional_energy_exponent(self):
        result = probe_abc_perturbation_bound()
        self.assertTrue(result["passed"])
        self.assertEqual(result["gradient_operator_bound_K"], 3)
        self.assertEqual(
            [Fraction(v["gronwall_exponent"]) for v in result["sample_exponents"]],
            [Fraction(0), Fraction(3), Fraction(9, 2), Fraction(21, 4)],
        )

    def test_regulated_transfer_gap_has_no_uniform_limit(self):
        result = probe_transfer_gap_obstruction()
        self.assertTrue(result["passed"])
        differences = [Fraction(x["one_minus_ratio"]) for x in result["samples"]]
        self.assertTrue(all(a > b > 0 for a, b in zip(differences, differences[1:])))

    def test_projective_space_cycle_ring(self):
        result = probe_projective_hodge()
        self.assertTrue(result["passed"])
        self.assertEqual(result["top_degree_pairings"], [1] * 5)
        self.assertEqual(result["h_to_n_plus_one"], "0")

    def test_elliptic_curve_exact_point_counts(self):
        result = probe_elliptic_local_counts()
        self.assertTrue(result["passed"])
        counts = {entry["p"]: entry["points"] for entry in result["local_data"]}
        self.assertEqual(counts[5], 8)
        self.assertEqual(counts[7], 8)
        self.assertTrue(all(e["hasse_bound"] for e in result["local_data"]))

    def test_boundary_of_four_simplex_homology(self):
        result = probe_simplicial_three_sphere()
        self.assertTrue(result["passed"])
        self.assertEqual(result["simplices"], {"0": 5, "1": 10, "2": 10, "3": 5})
        self.assertEqual(result["betti_mod_2"], [1, 0, 0, 1])
        self.assertTrue(result["boundary_squared_zero"])
        self.assertEqual(_gf2_rank([0, 0, 0]), 0)
        self.assertEqual(_gf2_rank([1, 2, 3]), 2)


if __name__ == "__main__":
    unittest.main()
