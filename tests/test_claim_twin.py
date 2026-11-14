"""Adversarial tests for the exact finite-claim digital twin.

These tests verify the narrow certificate protocol. They do not demonstrate
originality, formal kernel checking, or any Millennium theorem.
"""
from __future__ import annotations

import copy
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest

from mathos.research.claim_twin import (
    MANIFEST, PINNED, STATUS, _digest, _json_canonical,
    build_candidates, main, verify_candidates,
)
from mathos.research.clay_alignment import TARGETS_PATH
from mathos.research.hypothesis_pipeline import HYPOTHESES, OBLIGATIONS


class BoundedDigitalTwinTests(unittest.TestCase):
    def test_all_seven_exact_claims_are_certified_only_within_scope(self):
        result = verify_candidates(build_candidates())
        self.assertEqual(result["bounded_certificates_verified"], 7)
        self.assertEqual(result["certification"], "NOT_CERTIFIED")
        self.assertEqual(result["canonical_proof_promotion"], "NONE")
        self.assertEqual(result["full_millennium_solutions_certified"], 0)
        self.assertEqual(result["open_millennium_obligations"], 14)
        self.assertFalse(result["cryptographically_signed"])
        self.assertEqual({x["model_key"] for x in result["witness_attestations"]},
                         set(PINNED))
        for item in result["witness_attestations"]:
            self.assertEqual(item["bounded_certificate_status"], STATUS)
            self.assertEqual(item["scope"], "FINITE_EXACT_MODEL_ONLY")
            self.assertEqual(item["official_problem_certification"], "NOT_CERTIFIED")
            self.assertEqual(item["canonical_mathematical_state"], "BLOCKED")
            self.assertFalse(item["global_proof_completed"])
            self.assertFalse(item["formal_kernel_check"])
            self.assertFalse(item["independent_expert_review"])
            self.assertTrue(item["checker_method"])
            self.assertEqual(len(item["witness_sha256"]), 64)

    def test_one_track_does_not_award_other_claims(self):
        cases = build_candidates("Poincare")
        result = verify_candidates(cases, track="Poincare")
        self.assertEqual(result["bounded_certificates_verified"], 1)
        self.assertEqual(result["witness_attestations"][0]["model_key"], "Poincare")
        self.assertEqual(result["full_millennium_solutions_certified"], 0)
        self.assertEqual(result["certification"], "NOT_CERTIFIED")

    def test_harmonic_numerator_corruption_rejected(self):
        candidate = build_candidates("Riemann")
        self.assertEqual(Fraction(candidate[0]["witness"]["numerator"],
                                  candidate[0]["witness"]["denominator"]),
                         sum((Fraction(1, k) for k in range(1, 17)), Fraction(0)))
        candidate[0]["witness"]["numerator"] += 1
        with self.assertRaises(ValueError):
            verify_candidates(candidate, track="Riemann")

    def test_sat_resolution_forged_pivot_and_empty_step_rejected(self):
        for change in ("pivot", "last", "step", "future_parent"):
            candidate = build_candidates("P-versus-NP")
            proof = candidate[0]["witness"]["resolution"]
            if change == "pivot":
                proof["steps"][0]["pivot"] = 999
            elif change == "last":
                proof["last"] = -1
            elif change == "step":
                proof["steps"].pop()
            else:
                proof["steps"][0]["left"] = 999
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    verify_candidates(candidate, track="P-versus-NP")

    def test_ns_forged_universal_regular_case_rejected(self):
        candidate = build_candidates("Navier-Stokes")
        candidate[0]["statement"] = "All 3D Navier-Stokes solutions are smooth"
        with self.assertRaisesRegex(ValueError, "broader claim"):
            verify_candidates(candidate, track="Navier-Stokes")

    def test_ns_forged_conditional_arithmetic_rejected(self):
        candidate = build_candidates("Navier-Stokes")
        candidate[0]["witness"]["exponents"][1] = "4"
        with self.assertRaises(ValueError):
            verify_candidates(candidate, track="Navier-Stokes")

    def test_ym_noncanonical_and_wrong_ratio_rejected(self):
        for wrong in ("2/6", "1/2"):
            candidate = build_candidates("Yang-Mills")
            candidate[0]["witness"]["ratios"][0] = wrong
            with self.subTest(wrong=wrong):
                with self.assertRaises(ValueError):
                    verify_candidates(candidate, track="Yang-Mills")

    def test_hodge_wrong_ring_relation_rejected(self):
        candidate = build_candidates("Hodge")
        candidate[0]["witness"]["h5"] = 1
        with self.assertRaises(ValueError):
            verify_candidates(candidate, track="Hodge")
        candidate = build_candidates("Hodge")
        candidate[0]["witness"]["top_pairings"][2] = 0
        with self.assertRaises(ValueError):
            verify_candidates(candidate, track="Hodge")

    def test_bsd_wrong_point_count_rejected(self):
        candidate = build_candidates("Birch-Swinnerton-Dyer")
        self.assertEqual(candidate[0]["witness"]["point_counts"][:3], [8, 8, 12])
        candidate[0]["witness"]["point_counts"][0] = 9
        with self.assertRaises(ValueError):
            verify_candidates(candidate, track="Birch-Swinnerton-Dyer")

    def test_poincare_wrong_mod2_rank_rejected(self):
        candidate = build_candidates("Poincare")
        self.assertEqual(candidate[0]["witness"]["boundary_ranks"], [4, 6, 4])
        self.assertEqual(candidate[0]["witness"]["betti_mod2"], [1, 0, 0, 1])
        candidate[0]["witness"]["boundary_ranks"][1] = 5
        with self.assertRaises(ValueError):
            verify_candidates(candidate, track="Poincare")

    def test_extra_ai_generated_certification_fields_rejected(self):
        candidate = build_candidates("Riemann")
        candidate[0]["proof_completed"] = True
        with self.assertRaisesRegex(ValueError, "extra keys"):
            verify_candidates(candidate, track="Riemann")
        candidate = build_candidates("Riemann")
        candidate[0]["witness"]["mathematical_theorem_proved"] = True
        with self.assertRaisesRegex(ValueError, "extra keys"):
            verify_candidates(candidate, track="Riemann")

    def test_unknown_duplicate_and_missing_track_rejected(self):
        with self.assertRaises(ValueError):
            verify_candidates(build_candidates()[:6])
        candidate = build_candidates()
        candidate[1] = copy.deepcopy(candidate[0])
        with self.assertRaises(ValueError):
            verify_candidates(candidate)
        with self.assertRaises(ValueError):
            build_candidates("Goldbach")
        with self.assertRaises(ValueError):
            verify_candidates([], track="Goldbach")

    def _mutated_sources(self, manifest_edit=None, register_edit=None):
        with tempfile.TemporaryDirectory() as temp:
            man = json.loads(MANIFEST.read_text())
            reg = json.loads(OBLIGATIONS.read_text())
            if manifest_edit:
                manifest_edit(man)
            if register_edit:
                register_edit(reg)
            p = Path(temp)
            m, r = p / "manifest.json", p / "register.json"
            m.write_text(json.dumps(man))
            r.write_text(json.dumps(reg))
            return verify_candidates(
                build_candidates("Riemann"), track="Riemann",
                manifest_path=m, register_path=r
            )

    def test_reject_manifest_full_problem_promotion(self):
        with self.assertRaises(ValueError):
            self._mutated_sources(manifest_edit=lambda m:
                m["claims"][0].update(complete_millennium_problem=True))

    def test_reject_manifest_statement_tampering(self):
        with self.assertRaises(ValueError):
            self._mutated_sources(manifest_edit=lambda m:
                m["claims"][0].update(statement="RH has been proved"))

    def test_reject_changed_canonical_math_status(self):
        with self.assertRaises(ValueError):
            self._mutated_sources(register_edit=lambda r:
                r["tracks"][0]["work_packages"][0].update(graph_state="closed"))

    def test_source_hashes_and_deterministic_report(self):
        paths = (MANIFEST, OBLIGATIONS, TARGETS_PATH, HYPOTHESES)
        old = [p.read_bytes() for p in paths]
        x, y = (verify_candidates(build_candidates()) for _ in range(2))
        self.assertEqual(x, y)
        self.assertEqual(old, [p.read_bytes() for p in paths])
        self.assertEqual(x["report_sha256"], _digest(_json_canonical({
            k: v for k, v in x.items() if k != "report_sha256"
        })))
        self.assertEqual(x["source_sha256"]["claim_manifest"], _digest(old[0]))

    def test_cli_generates_exact_scope_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            main(["--output-dir", tmp])
            report = json.loads((Path(tmp) / "bounded_claim_certificates.json").read_text())
            self.assertEqual(report["bounded_certificates_verified"], 7)
            self.assertEqual(report["certification"], "NOT_CERTIFIED")

    def test_cli_verifies_untrusted_input_without_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "candidates.json"
            file.write_text(json.dumps(build_candidates("P-versus-NP")))
            out = Path(tmp) / "verified"
            main(["--input", str(file), "--track", "P-versus-NP",
                  "--output-dir", str(out)])
            result = json.loads((out / "bounded_claim_certificates.json").read_text())
            self.assertEqual(result["bounded_certificates_verified"], 1)
            self.assertEqual(result["certification"], "NOT_CERTIFIED")
            file.write_text(json.dumps([dict(build_candidates("P-versus-NP")[0],
                                          status="CERTIFIED_CLAY")]))
            with self.assertRaises(ValueError):
                main(["--input", str(file), "--track", "P-versus-NP",
                      "--output-dir", str(out)])

    def test_no_signature_claim_and_no_global_promotion(self):
        output = verify_candidates(build_candidates("Yang-Mills"),
                                   track="Yang-Mills")
        self.assertEqual(output["full_millennium_solutions_certified"], 0)
        self.assertFalse(output["cryptographically_signed"])
        self.assertIn("not a Clay proof", output["bounded_status_definition"])
        self.assertEqual(output["witness_attestations"][0]
                         ["official_problem_certification"], "NOT_CERTIFIED")


if __name__ == "__main__":
    unittest.main()
