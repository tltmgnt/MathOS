import unittest
from fractions import Fraction as F
from mathos.research import breakthrough_cycle3 as m

class ThirdCycle(unittest.TestCase):
    def test_momentum_controls(self):
        r=m.ns()
        self.assertEqual(r["scaling_checks"],8)
        self.assertEqual(r["moment_checks"],4)
        self.assertFalse(r["pde_solution_established"])
    def test_weil_coupling(self):
        r=m.rh()
        self.assertGreater(F(r["constant_vector_rayleigh_lower"]),F(r["prior_local_floor"]))
        self.assertFalse(r["global_positivity_proved"])
    def test_intake(self):
        r=m.run()
        self.assertEqual(r["open_obligations"],14)
        self.assertEqual(r["promotion"],"NONE")
        for result in r["results"].values():
            self.assertEqual(result["intake"]["outcome"],"SCOPED_RESULT_CANDIDATE")
            self.assertFalse(result["intake"]["mathematical_proof_established"])
