import unittest
from mathos.research import tga_u003 as m

class U003(unittest.TestCase):
    def test_persistent_witness(self):
        r=m.shifted_witness()
        self.assertEqual(len(r["synthetic_shift_controls"]),31)
        self.assertFalse(r["RH_proved"])
    def test_orientation(self):
        r=m.orientation()
        self.assertEqual(r["alternating_coefficient"],"-1/2")
        self.assertEqual(r["permutation_checks"],576)
        self.assertFalse(r["universal_hodge_proved"])
    def test_scope(self):
        r=m.run()
        self.assertEqual(r["promotion"],"NONE")
        self.assertEqual(r["canonical_open_obligations"],14)
