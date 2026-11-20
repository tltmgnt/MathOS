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

    def test_without_observation_only_unverified(self):
        with tempfile.TemporaryDirectory() as temp:
            scenario=create_tect_scenario(report(Path(temp)))
            self.assertEqual(len(scenario["operations"]),2)
            self.assertEqual(scenario["operations"][-1]["data"]["target"],"UNVERIFIED")


if __name__=="__main__":
    unittest.main()
