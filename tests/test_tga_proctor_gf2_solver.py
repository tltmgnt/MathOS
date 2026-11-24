import unittest
from mathos.research import tga_proctor_gf2_solver as s

class Solver(unittest.TestCase):
    def test_exhaustive(self):
        r=s.controls()
        self.assertEqual(r["total_cases"],31+341+4681+4369)
        self.assertEqual(r["tampered_certificates_or_witnesses_rejected"],3)
    def test_zero_columns_and_free_variables(self):
        self.assertEqual(s.certificate_solver(0,[])["witness"],0)
        self.assertEqual(s.certificate_solver(0,[(0,1)])["certificate"],[0])
        self.assertEqual(s.certificate_solver(3,[(2,1)])["witness"],2)
        with self.assertRaises(ValueError):s.certificate_solver(2,[(4,0)])
    def test_scope(self):
        self.assertEqual(s.graph(True,True,True)["remaining"],
            [["bit_cost","certificate_generation_formal","implementation_refinement"]])
        self.assertEqual(s.graph(True,True,True)["status"],"BLOCKED")
