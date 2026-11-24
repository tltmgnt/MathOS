import unittest
from mathos.research import tga_proctor_unrestricted_scope as s


class ScopeTests(unittest.TestCase):
    def test_exhaustive_controls(self):
        r = s.controls()
        self.assertEqual(r["affine"],52)
        self.assertEqual(r["signed_clause_checks"],64)
        self.assertEqual(r["formulas"],26)
        self.assertGreater(r["unsat"],0)

    def test_shared_variables(self):
        cnf=((1,1,1),(-1,-1,-1))
        result=s.solve(1,cnf)
        self.assertFalse(result["sat"])
        self.assertTrue(s.verify(1,cnf,result))
        self.assertFalse(s.verify(1,cnf,{"sat":True,"witness":(True,)}))

    def test_invalid_input(self):
        for n,cs in ((-1,()),(1,((1,1),)),(1,((0,1,1),)),
                     (1,((2,1,1),)),(1,((True,1,1),))):
            with self.assertRaises(ValueError):
                s.compile_cnf(n,cs)

    def test_empty(self):
        r=s.solve(0,())
        self.assertTrue(r["sat"])
        self.assertEqual(r["witness"],())
        self.assertTrue(s.verify(0,(),r))


if __name__ == "__main__":
    unittest.main()
