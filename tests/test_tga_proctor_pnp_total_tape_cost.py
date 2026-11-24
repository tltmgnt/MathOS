import unittest
from mathos.research.tga_proctor_pnp_total_tape_cost import fixtures,solve,budget,input_size


class TotalTapeCostTests(unittest.TestCase):
    def test_controls(self):
        _, counts=fixtures()
        self.assertEqual(counts["systems"],4187)
        self.assertEqual(counts["sat"]+counts["unsat"],4187)
        self.assertEqual(counts["total_sum"],sum(counts[k+"_sum"] for k in
            ("preprocess","affine","lifting","construction","copying")))

    def test_empty(self):
        result=solve([],[])
        self.assertEqual(result["wire"],[True])
        self.assertEqual(result["total"],7)
        self.assertEqual(result["lifting"],0)

    def test_large_domain_and_invalid_input(self):
        ds=[[(False,False)]*100+[(True,True)]]
        rs=[([True],True)]
        result=solve(ds,rs)
        self.assertEqual(result["wire"],[True,True,True])
        self.assertEqual(result["lifting"],4*101+4)
        self.assertLessEqual(result["total"],budget(1,1,101,2))
        S=input_size(1,1,101)
        self.assertEqual(budget(S,S,S,S),8*S**3+26*S**2+55*S+7)
        with self.assertRaises(ValueError):
            solve(ds,[([],True)])
