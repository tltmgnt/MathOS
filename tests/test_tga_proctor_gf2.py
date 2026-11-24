import unittest
from mathos.research import tga_proctor_gf2 as g
class GF2(unittest.TestCase):
    def test_controls(self):
        r=g.controls()
        self.assertEqual(r["linearity_checks"],29791)
        self.assertEqual(r["pivot_tail_checks"],8192)
        self.assertEqual(r["contradictory_three_row_certificates"],256)
    def test_scope(self):
        self.assertEqual(g.graph(True,True)["remaining"],[["bit_cost","implementation_refinement","solver_iteration"]])
        self.assertEqual(g.graph(True,True)["status"],"BLOCKED")
