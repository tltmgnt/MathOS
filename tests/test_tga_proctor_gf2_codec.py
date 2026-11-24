import unittest
from mathos.research import tga_proctor_gf2_codec as c
class Codec(unittest.TestCase):
    def test_controls(self):
        r=c.controls()
        self.assertEqual(r["codec_cases"],2044)
        self.assertEqual(r["parity_pairs"],5461)
        self.assertEqual(r["systems"],5054)
        self.assertEqual(r["dual_certificates"],1916)
    def test_truncation(self):
        self.assertEqual(c.encode(c.decode(3,13)),5)
        self.assertEqual(c.decode(0,99),[])
