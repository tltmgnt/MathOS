import unittest
from mathos.research import tga_proctor_gf2_global as g
class Global(unittest.TestCase):
    def test_fixtures(self):
        self.assertEqual(len(g.fixtures()),5054)
        self.assertEqual(g.prior_controls()["unsat"],1916)
