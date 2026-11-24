import unittest
from mathos.research import millennium_followup_round3 as m

class Round3(unittest.TestCase):
    def test_rh(self): self.assertEqual(m.rh()['cases'],32)
    def test_pnp(self): self.assertEqual(m.pnp()['cases'],49)
    def test_ns(self): self.assertEqual(m.ns()['young_controls'],7)
    def test_ym(self): self.assertEqual(m.ym()['sharp_endpoints'],9)
    def test_hodge(self): self.assertEqual(m.hodge()['primitive_dimension'],10)
    def test_bsd(self): self.assertEqual(m.bsd()['collisions'],0)
    def test_poincare(self): self.assertEqual(m.poincare()['conditional_jump_factor'],1)
    def test_no_promotion(self): self.assertEqual(m.run()['globally_proved'],0)
