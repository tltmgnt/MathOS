import unittest
from mathos.research import tga_proctor_gf2_highest as h
class Highest(unittest.TestCase):
    def test_trace(self):
        r=h.controls()
        self.assertEqual(r["systems"],5054)
        self.assertEqual(r["unsat"],1916)
    def test_three_row_conflict(self):
        self.assertEqual(h.trace(2,[(1,1),(2,1),(3,1)])[:2],(False,7))
