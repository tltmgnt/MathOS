import unittest
from mathos.research import tga_proctor_tape_solver as t
class Tape(unittest.TestCase):
    def test_controls(self):
        data,r=t.fixtures()
        self.assertEqual(r["systems"],5054)
        self.assertEqual(r["unsat"],1916)
        self.assertEqual(t.eval_source(data)[1],5054)
    def test_zero(self):
        self.assertEqual(t.mirror_tape(0,[]),((True,[]),0))
        self.assertEqual(t.mirror_tape(0,[(0,1)]),((False,[1]),6))
