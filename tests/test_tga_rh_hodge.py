import unittest
from mathos.research import tga_rh_hodge as m

class RHAndHodge(unittest.TestCase):
    def test_xi(self):
        r=m.xi_moments()
        self.assertTrue(r["unshifted_2x2_positive"])
        self.assertTrue(r["shifted_2x2_positive"])
        self.assertFalse(r["all_order_positivity_proved"])
    def test_tensor(self):
        r=m.determinant_tensor_controls()
        self.assertEqual(r["cases"][-1]["permutation_pairs_checked"],14400)
        self.assertFalse(r["determinant_class_algebraicity_proved"])
