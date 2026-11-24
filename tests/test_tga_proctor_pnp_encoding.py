import unittest
from mathos.research import tga_proctor_pnp_encoding as e
class Encoding(unittest.TestCase):
    def test_controls(self):
        r=e.controls()
        self.assertEqual(r["domain_cases"],4096)
        self.assertEqual(r["sat"],2121)
        self.assertEqual(r["bitmask_pairs"],5461)
    def test_local(self):
        self.assertEqual(e.domain_rows([[],[(1,1)],[(0,0),(1,1)],[(0,1)]]),[(0,1),(2,1),(8,0)])
