import unittest
from mathos.research import tga_proctor_bit_cells as c
class Cells(unittest.TestCase):
    def test_packets(self):
        data,r=c.fixtures()
        self.assertEqual(r["wire_packets"],4184)
        self.assertEqual(r["mask_pairs"],341)
        self.assertEqual(r["memory_cases"],196)
        source,n=c.eval_source(data)
        self.assertEqual(n,4721)
        self.assertIn("ProctorGF2.writeCell",source)
