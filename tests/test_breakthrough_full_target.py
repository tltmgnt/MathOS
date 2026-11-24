import unittest
from mathos.research import breakthrough_full_target as m

class FullTargetTests(unittest.TestCase):
    def test_affine(self):
        for n in range(1,5):
            for a in range(1<<n):
                for b in (0,1):
                    got=m.affine(n,[(a,b)])
                    expected={x for x in range(1<<n) if (x&a).bit_count()%2==b}
                    if got is None:self.assertFalse(expected);continue
                    x,ds=got; seen={x}
                    for v in ds:seen|={y^v for y in seen}
                    self.assertEqual(seen,expected)
    def test_full_target_replay(self):
        r=m.replay()
        self.assertEqual(r["overlap_controls"],1458)
        self.assertEqual(r["adversarial_rank_cases"][-1]["branches"],4096)
        self.assertFalse(r["unrestricted_polynomial_runtime_proved"])
        self.assertEqual(r["promotion"],"NONE")
    def test_bad_inputs(self):
        with self.assertRaises(ValueError):m.solve(2,[],[(0,1,2)])
        with self.assertRaises(ValueError):m.solve(2,[(4,0)],[])
