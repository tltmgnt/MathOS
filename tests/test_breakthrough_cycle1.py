import unittest
from mathos.research import breakthrough_cycle1 as c

class FirstCycle(unittest.TestCase):
    def test_seed_and_scaling(self):
        r=c.ns()
        self.assertEqual(r["algebraic_controls"],15)
        self.assertFalse(r["global_continuation_proved"])
    def test_regularization(self):
        r=c.rh()
        self.assertEqual(r["finite_checks"],12)
        self.assertFalse(r["global_zero_identity_proved"])
    def test_intake_and_no_promotion(self):
        r=c.run()
        self.assertEqual(r["open_obligations"],14)
        self.assertEqual(r["promotion"],"NONE")
        for item in r["results"].values():
            self.assertEqual(item["intake"]["outcome"],"FALSIFIED_CANDIDATE")
            self.assertFalse(item["intake"]["mathematical_proof_established"])
