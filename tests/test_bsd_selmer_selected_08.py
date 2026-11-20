"""Tests use SYNTHETIC fixtures; they are not measured PARI rank certificates."""
import base64
import hashlib
from pathlib import Path
import tempfile
import unittest

from mathos.research.bsd_selmer_selected_08 import (
    curve_parameters, parse_gp_output, verify_run, report, create_tect_scenario,
)


class BSDSelmer08Tests(unittest.TestCase):
    def test_exact_model_parameters(self):
        self.assertEqual(curve_parameters(0)["discriminant"],37)
        self.assertEqual(curve_parameters(1)["discriminant"],389)
        self.assertEqual(curve_parameters(2)["discriminant"],5077)
        self.assertEqual(curve_parameters(3)["discriminant"],43669)
        self.assertEqual(curve_parameters(2)["a2"],3)
        self.assertEqual(curve_parameters(2)["a4"],-4)

    def test_parse_example_record_and_reject_forged_output(self):
        # Not an observed CAS output, only a synthetic parser fixture!
        good="GP output\nMATHOS08|2|3|3|0|0|3|3\n"
        res=parse_gp_output(good, 2)
        self.assertEqual(res["two_selmer_dim"],3)
        self.assertEqual(res["rank_upper"],3)
        for bad in (
            "MATHOS08|2|3|2|0|0|2|3",
            "MATHOS08|2|3|3|1|0|4|3",
            "MATHOS08|2|3|3|0|0|4|3",
            "MATHOS08|2|3|3|0|0|3|3\nMATHOS08|2|3|3|0|0|3|3",
            "MATHOS08|3|3|3|0|0|3|3",
        ):
            with self.assertRaises(ValueError, msg=bad):
                parse_gp_output(bad,2)

    def test_failed_job_can_never_be_cited_as_selmer_certificate(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"u2.gp.log").write_text("MATHOS08|2|3|3|0|0|3|3\n")
            (root/"u2.exit").write_text("124\n")
            result=verify_run(root,2)
            self.assertEqual(result["result"],"INCONCLUSIVE")
            self.assertIs(result["two_selmer_certified"],False)
            self.assertEqual(verify_run(root,3)["result"],"NOT_RUN")

    def test_synthetic_fixture_not_promoted_to_infinite_theorem(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"u2.gp.log").write_text("MATHOS08|2|3|3|0|0|3|3\n")
            (root/"u2.exit").write_text("0\n")
            data=report(root)
            self.assertEqual(data["number_of_successful_computations"],1)
            self.assertTrue(data["observations"][2]["rank_3_exact_from_run"])
            self.assertIs(data["infinite_uniform_upper_bound_of_three_proved"],False)
            self.assertIs(data["mathematical_novelty_established"],False)
            self.assertIs(data["BSD_proved"],False)
            scenario=create_tect_scenario(data)
            self.assertEqual(
                [x["data"].get("target") for x in scenario["operations"]
                 if x["op"]=="transition"],
                ["UNVERIFIED","SUPPORTED"]
            )
            receipt=scenario["operations"][2]["data"]
            payload=base64.b64decode(receipt["content_base64"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(),receipt["sha256"])
            # This is a parser fixture and cannot be treated as independent run data.


    def test_observed_pinned_evidence_is_scoped_and_internally_consistent(self):
        import json
        from pathlib import Path
        path = (Path(__file__).resolve().parents[1]
                / "docs/research/papers/BSD_SELMER_08_COMPUTED_EVIDENCE.v1.json")
        observed = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(observed["workflow_run_id"],44654855201)
        self.assertEqual(observed["cas_version"],"pari-gp 2.17.3-1")
        self.assertEqual(observed["canonical_tect_observed_claim_state"],"SUPPORTED")
        self.assertIs(observed["canonical_tect_runtime_executed"],True)
        self.assertIs(observed["external_human_peer_review"],False)
        self.assertIs(observed["proven_infinite_subset_of_24Z_with_uniform_selmer_2_rank_at_most_3"],False)
        self.assertIs(observed["original_mathos_parameter_set_24Z_all_have_rank_at_most_3"],False)
        values={int(x["u"]):x for x in observed["observed_certificates"]}
        self.assertEqual(set(values),{0,1,2,3,24,-24})
        for u,r in ((0,1),(1,2),(2,3),(3,3),(24,4),(-24,4)):
            c=values[u]
            self.assertEqual(c["rank_lower"],c["rank_upper"])
            self.assertEqual(c["rank_upper"],c["selmer_2_dimension"])
            self.assertEqual(c["rank_upper"],r)
            self.assertEqual(c["points_returned"],r)
            self.assertEqual(c["solver_exit_code"],0)
            self.assertEqual(len(c["stdout_sha256"]),64)
        self.assertIs(observed["exact_rank3_over_infinite_subset_proved"],False)
        self.assertIs(observed["BSD_proved"],False)

    def test_without_observation_only_unverified(self):
        with tempfile.TemporaryDirectory() as temp:
            scenario=create_tect_scenario(report(Path(temp)))
            self.assertEqual(len(scenario["operations"]),2)
            self.assertEqual(scenario["operations"][-1]["data"]["target"],"UNVERIFIED")


if __name__=="__main__":
    unittest.main()
