import unittest
from mathos.research import tga_proctor_gf2_cost as c
class Cost(unittest.TestCase):
    def test_controls(self):
        r=c.controls()
        self.assertEqual(r["systems"],5054)
        self.assertEqual(r["collisions"],4448)
    def test_empty(self):
        self.assertEqual(c.mirror(0,[]),((True,0),(0,0,0,0,0)))
        self.assertEqual(c.mirror(0,[(0,1)]),((False,1),(1,0,1,0,0)))
