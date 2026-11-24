import unittest
from mathos.research import breakthrough_cycle6 as m

class SixthCycle(unittest.TestCase):
    def test_use_case(self):
        r=m.pnp()
        self.assertEqual(r["exhaustive_cases"],3375)
        self.assertTrue(r["use_case_completed"])
        self.assertFalse(r["general_sat_runtime_proved"])
    def test_hecke_value(self):
        r=m.bsd()
        self.assertEqual(r["certificate"]["valuation_at_5"],2)
        self.assertTrue(r["sha_5_primary_trivial_under_CLS_theorem"])
        self.assertFalse(r["all_prime_sha_finiteness_proved"])
    def test_intake(self):
        r=m.run()
        self.assertEqual(r["open_obligations"],14)
        self.assertEqual(r["promotion"],"NONE")
        for v in r["results"].values():self.assertFalse(v["intake"]["external_review_verified"])
