import unittest
from mathos.research import tga_proctor_tree_decomposition as t


class TreeTests(unittest.TestCase):
    def test_controls(self):
        r=t.controls()
        self.assertEqual(r["cases"],35)
        self.assertEqual(r["chain_candidates"],252)
        self.assertGreater(r["unsat"],0)

    def test_running_intersection(self):
        with self.assertRaisesRegex(ValueError,"running intersection"):
            t.solve(2,(),((1,), (2,), (1,)),((0,1),(1,2)))

    def test_invalid_tree(self):
        for edges in (((0,1),(1,2),(2,0)),((0,1),),((0,1),(1,0))):
            with self.assertRaises(ValueError):
                t.solve(3,(),((1,),(2,),(3,)),edges)

    def test_coverage(self):
        with self.assertRaisesRegex(ValueError,"uncovered"):
            t.solve(3,((1,2,3),),((1,2),(2,3)),((0,1),))

    def test_unsat_table_tampering(self):
        cs=((1,1,1),(-1,-1,-1))
        bags=((1,),)
        r=t.solve(1,cs,bags,())
        self.assertFalse(r["sat"])
        self.assertTrue(t.verify(1,cs,bags,(),r))
        self.assertFalse(t.verify(1,cs,bags,(),{**r,"tables":(((True,),),)}))

    def test_empty_bag_and_isolates(self):
        r=t.solve(3,(),((),),())
        self.assertTrue(r["sat"])
        self.assertEqual(r["witness"],(False,False,False))


if __name__=="__main__":
    unittest.main()
