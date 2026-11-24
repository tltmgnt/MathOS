import unittest
from mathos.research import tga_proctor_factor_decomposition as f


class FactorTests(unittest.TestCase):
    def test_controls(self):
        r=f.controls()
        self.assertEqual(r["cases"],74)
        self.assertGreater(r["unsat"],0)

    def test_partition_and_separator(self):
        cs=((1,2,3),(-1,4,5))
        self.assertEqual(len(f.partition(cs,{})[1]),1)
        for bit in (False,True):
            bad,parts=f.partition(cs,{1:bit})
            self.assertIsNone(bad)
            self.assertEqual(len(parts),1)
            self.assertEqual(parts[0].variables,(4,5) if bit else (2,3))
        cs=((1,2,3),(1,4,5))
        self.assertEqual(len(f.partition(cs,{1:False})[1]),2)

    def test_glue_and_unused(self):
        cs=((1,1,1),(-4,-4,-4))
        r=f.solve(6,cs)
        self.assertEqual(r["max_components"],2)
        self.assertTrue(f.verify(6,cs,(),r))
        self.assertTrue(r["witness"][0])
        self.assertFalse(r["witness"][3])

    def test_false_clause_and_dual(self):
        cs=((1,1,1),(-1,-1,-1))
        r=f.solve(1,cs,(1,))
        self.assertEqual(r["failures"],(("clause",0),("clause",1)))
        self.assertFalse(f.verify(1,cs,(1,),{**r,"failures":r["failures"][::-1]}))
        q=f.solve(1,cs)
        self.assertTrue(f.verify(1,cs,(),q))
        tag,j,duals=q["failures"][0]
        tampered=(tuple(False for _ in duals[0]),)+duals[1:]
        self.assertFalse(f.verify(1,cs,(),{**q,"failures":((tag,j,tampered),)}))

    def test_invalid_separator(self):
        for sep in ((0,),(2,),(1,1),(True,)):
            with self.assertRaises(ValueError):
                f.solve(1,(),sep)


if __name__=="__main__":
    unittest.main()
