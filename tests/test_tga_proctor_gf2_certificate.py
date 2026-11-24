import unittest
from mathos.research import tga_proctor_gf2_certificate as c
class Certificate(unittest.TestCase):
    def test_dual(self):
        r=c.controls()
        self.assertEqual(r["total"],5054)
        self.assertEqual(r["three_row_minimal_certificate"],[0,1,2])
    def test_scope(self):
        self.assertEqual(c.graph(True,True)["remaining"],[["bit_cost","implementation_refinement"]])
        self.assertEqual(c.graph(True,True)["status"],"BLOCKED")
