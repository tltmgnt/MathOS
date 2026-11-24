import unittest
from mathos.research import breakthrough_cycle4 as m

class FourthCycle(unittest.TestCase):
    def test_projection(self):
        r=m.pnp()
        self.assertEqual(r["cases"][-1]["projected_clauses"],2048)
        self.assertFalse(r["general_sat_lower_bound_proved"])
    def test_rank_certificate(self):
        r=m.bsd()
        self.assertEqual(r["analytic_rank"],2)
        self.assertEqual(r["monsky_nullity"],2)
        self.assertGreater(r["analytic_certificate"]["completed_second_derivative_lower"],0)
        self.assertFalse(r["all_prime_sha_finiteness_proved"])
    def test_intake(self):
        r=m.run()
        self.assertEqual(r["open_obligations"],14)
        self.assertEqual(r["promotion"],"NONE")
        for v in r["results"].values():
            self.assertFalse(v["intake"]["mathematical_proof_established"])
