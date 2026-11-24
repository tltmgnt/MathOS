import unittest
from mathos.research import tga_proctor_gf2_checker as c
class Checker(unittest.TestCase):
    def test_fixture_transport(self):
        data,r=c.fixtures()
        self.assertEqual(r["projected_cases"],3441)
        self.assertEqual(r["empty_domain_cases"],721)
        self.assertEqual(r["sat"]+r["unsat"],len(data))
        self.assertEqual(c.bits(3,5),[1,0,1])
        with self.assertRaises(ValueError):c.bits(2,4)
    def test_bad_certificate(self):
        with self.assertRaises(ValueError):
            c.encode([[(0,0),(1,1)]],[(1,0),(1,1)],{"sat":False,"xor_certificate":[0]})
