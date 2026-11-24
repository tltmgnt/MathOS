import unittest
from mathos.research import tga_proctor_pnp as p

class Specialist(unittest.TestCase):
    def test_controls(self):
        self.assertEqual(p.controls()["three_block_domain_instances"],4096)
    def test_scope(self):
        self.assertEqual(len(p.graph(False)["remaining"][0]),4)
        self.assertEqual(p.graph(True)["remaining"],[["affine_encoding","bit_cost","elimination"]])
        self.assertEqual(p.graph(True)["status"],"BLOCKED")
