import unittest
from mathos.research import tga_proctor_pnp_full_cost as c
class FullCost(unittest.TestCase):
    def test_fixtures(self):
        data,r=c.fixtures()
        self.assertEqual(r["systems"],4184)
        self.assertEqual(r["empty_domains"],722)
        self.assertEqual(r["duplicate_domain_controls"],3)
        self.assertEqual(r["sat"]+r["unsat"],len(data))
    def test_empty(self):
        self.assertEqual(c.stats((),(),True,(),1),(0,0,0,0,1,5))
