import unittest
from mathos.research import breakthrough_cycle5 as m

class FifthCycle(unittest.TestCase):
    def test_mixed_projection(self):
        r=m.pnp()
        self.assertEqual(r["cases"][-1]["minimum_projected_clauses"],1093)
        self.assertFalse(r["general_sat_lower_bound_proved"])
    def test_localization(self):
        r=m.bsd()
        self.assertEqual(len(r["ordinary_local_certificates"]),5)
        self.assertFalse(r["kato_nonvanishing_established"])
        self.assertFalse(r["odd_primary_sha_finiteness_established"])
    def test_intake(self):
        r=m.run()
        self.assertEqual(r["open_obligations"],14)
        self.assertEqual(r["promotion"],"NONE")
        for v in r["results"].values():
            self.assertFalse(v["intake"]["mathematical_proof_established"])
