import unittest
from mathos.research import tga_proctor_pnp_total_cost as t
class TotalCost(unittest.TestCase):
    def test_controls(self):
        data,r=t.fixtures()
        self.assertEqual(len(data),4183)
        self.assertEqual(r["sat"]+r["unsat"],len(data))
        self.assertEqual(r["repeated_domain_controls"],2)
    def test_empty(self):
        self.assertEqual(t.measured([],[],True,[],1),(0,1,0,2))
