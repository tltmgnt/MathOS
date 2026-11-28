import unittest
from mathos.research.pnp_library_ablation import independent_replay, oracle, summary, ARMS, name


class TestAblation(unittest.TestCase):
    def test_checker(self):
        f=[(1,),(-1,2),(-2,)]
        self.assertTrue(independent_replay(2,f,[(2,),()]))
        self.assertFalse(oracle(2,f))
        for proof in ([(1,-1),()],[(True,),()],[(3,),()]):
            with self.assertRaises(ValueError):
                independent_replay(2,f,proof)
        with self.assertRaises(ValueError):
            independent_replay(2,[(1,2)],[()])
        with self.assertRaises(ValueError):
            independent_replay(2,[(1,)], [(-1,),()])
        with self.assertRaises(ValueError):
            independent_replay(2,[(1,)],[(1,)])
        self.assertTrue(oracle(2,[(1,2)]))

    def test_summary(self):
        s=summary([])
        self.assertEqual(len(s["arms"]),8)
        self.assertEqual(len(s["contrasts"]),12)
        self.assertEqual(s["unsat"],0)
