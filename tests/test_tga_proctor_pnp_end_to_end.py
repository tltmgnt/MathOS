import unittest
from mathos.research import tga_proctor_pnp_end_to_end as e
class EndToEnd(unittest.TestCase):
    def test_cases(self):
        data,r=e.fixtures()
        self.assertEqual(len(data),4181)
        self.assertEqual(r["sat"]+r["unsat"],len(data))
        self.assertEqual(r["empty_domains"],721)
