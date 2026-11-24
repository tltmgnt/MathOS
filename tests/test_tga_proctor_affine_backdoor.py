import unittest
from mathos.research import tga_proctor_affine_backdoor as b


class BackdoorTests(unittest.TestCase):
    def test_controls(self):
        r=b.controls()
        self.assertEqual(r["cases"],103)
        self.assertEqual(r["star"]["cover_size"],1)
        self.assertEqual(r["dense_cover"],11)
        self.assertGreater(r["unsat"],0)

    def test_compression(self):
        cs=((1,2,2),(2,1,1),(1,-1,2),(2,2,2))
        _,rows,stats=b.compress(2,cs)
        self.assertEqual(rows,((0,(1,2)),(3,(2,))))
        self.assertEqual(stats,dict(tautologies=1,duplicate_clauses=1,repeated_literals=4))

    def test_unit_dual(self):
        cs=((1,1,1),(-1,-1,-1))
        r=b.solve(1,cs)
        self.assertFalse(r["sat"])
        self.assertEqual(r["cover"],())
        self.assertEqual(r["failures"],(("units",0,1),))
        self.assertTrue(b.verify(1,cs,r))
        self.assertFalse(b.verify(1,cs,{**r,"failures":(("units",0,0),)}))

    def test_false_branch(self):
        cs=((1,2,2),(1,-2,-2),(-1,2,2),(-1,-2,-2),(1,1,1))
        r=b.solve(2,cs)
        self.assertFalse(r["sat"])
        self.assertTrue(b.verify(2,cs,r))
        self.assertFalse(b.verify(2,cs,{**r,"cover":(1,1)}))
        self.assertFalse(b.verify(2,cs,{**r,"failures":r["failures"][:-1]}))

    def test_invalid_formula(self):
        for n,cs in ((-1,()),(1,((1,1,0),)),(1,((2,2,2),))):
            with self.assertRaises(ValueError):
                b.solve(n,cs)

    def test_empty_and_tautology(self):
        for n,cs in ((0,()),(2,((1,-1,2),))):
            r=b.solve(n,cs)
            self.assertTrue(r["sat"])
            self.assertEqual(r["cover"],())
            self.assertTrue(b.verify(n,cs,r))


if __name__=="__main__":
    unittest.main()
