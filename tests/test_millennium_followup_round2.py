import unittest
from mathos.research import millennium_followup_round2 as m

class Round2(unittest.TestCase):
    def test_rh(self): self.assertEqual(len(m.rh()),6)
    def test_pnp(self): self.assertEqual(len(m.pnp()),5)
    def test_ns(self): self.assertEqual(m.ns()['positive_threshold'],'A > 46 nu')
    def test_ym(self): self.assertEqual(len(m.ym()),12)
    def test_hodge(self): self.assertEqual([x['primitive_dimension'] for x in m.hodge()],[1,2,5,14,42])
    def test_bsd(self): self.assertEqual(len(m.bsd()),4)
    def test_poincare(self): self.assertEqual(m.poincare()['forcing_limit'],'2')
    def test_no_promotion(self): self.assertEqual(m.run()['globally_proved'],0)
