import unittest
from mathos.research import breakthrough_cycle2 as m

class SecondCycle(unittest.TestCase):
    def test_scalar_balances(self):
        r=m.ns()
        self.assertEqual(r["balance_cases"],15)
        self.assertFalse(r["navier_stokes_solution_established"])
    def test_local_weil_bound(self):
        r=m.rh()
        self.assertEqual(r["reported_floor"],"2/5")
        self.assertTrue(r["partial_gt_7"])
        self.assertFalse(r["global_weil_positivity_proved"])
    def test_gluing_controls(self):
        self.assertEqual([x["psd"] for x in m.rh()["schur_controls"]],[True,True,False,True,False])
    def test_intake(self):
        r=m.run()
        self.assertEqual(r["open_obligations"],14)
        self.assertEqual(r["promotion"],"NONE")
        self.assertEqual(r["results"]["NS-B002"]["intake"]["outcome"],"FALSIFIED_CANDIDATE")
        self.assertEqual(r["results"]["RH-B002"]["intake"]["outcome"],"SCOPED_RESULT_CANDIDATE")
        for item in r["results"].values():
            self.assertFalse(item["intake"]["mathematical_proof_established"])
