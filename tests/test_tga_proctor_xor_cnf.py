import unittest
from unittest.mock import patch

from mathos.research import tga_proctor_xor_cnf as x


class XorCNFTests(unittest.TestCase):
    def test_controls(self):
        r = x.controls()
        self.assertEqual(r["random_cases"], 3000)
        self.assertEqual(r["certified_unsat"] + r["unknown"], 3000)
        self.assertGreater(r["certified_unsat"], 0)
        self.assertEqual(len(r["graphs"]), 16)
        self.assertFalse(r["complete_cnf_solver"])

    def test_widths_and_missing_pattern(self):
        for w in range(1,6):
            vs = tuple(range(1,w+1))
            for b in (0,1):
                cs = x.encode_parity(vs,b)
                self.assertEqual(x.detect(w,cs), ((vs,b,tuple(range(len(cs)))),))
                self.assertEqual(x.solve(w,cs)["status"], "UNKNOWN")
                self.assertEqual(x.detect(w,cs[:-1]), ())
        self.assertEqual(x.detect(6,x.encode_parity(tuple(range(1,7)),0)), ())

    def test_duplicate_tautology_and_sparse_ids(self):
        n = 2**100
        vs = (7,n)
        cs = x.encode_parity(vs,0) + x.encode_parity(vs,1)
        padded = tuple(c+(c[-1],) for c in cs) + (cs[0], (7,-7,n))
        out = x.solve(n,padded)
        self.assertEqual(out["status"], "UNSAT")
        self.assertEqual(out["affine_variables"], 2)
        self.assertTrue(x.verify(n,padded,out))

    def test_three_row_dual_and_tamper(self):
        cs = x.encode_parity((1,2),0) + x.encode_parity((2,3),0) + x.encode_parity((1,3),1)
        out = x.solve(3,cs)
        self.assertEqual(out["status"], "UNSAT")
        tag, blocks = out["certificate"]
        self.assertEqual(len(blocks), 3)
        vs,b,ix = blocks[0]
        with patch.object(x,"detect",side_effect=AssertionError("no detector")), \
             patch.object(x,"_signature",side_effect=AssertionError("no signature")), \
             patch.object(x,"certificate_solver",side_effect=AssertionError("no solver")), \
             patch.object(x,"verify_result",side_effect=AssertionError("no affine replay")):
            self.assertTrue(x.verify(3,cs,out))
            for bad in (blocks[:-1], blocks+(blocks[0],),
                        ((vs,1-b,ix),)+blocks[1:],
                        ((vs,b,ix[:-1]),)+blocks[1:],
                        ((vs,b,(ix[0],ix[0])),)+blocks[1:],
                        ((vs,b,(ix[0],99)),)+blocks[1:],
                        ((vs[::-1],b,ix),)+blocks[1:]):
                self.assertFalse(x.verify(3,cs,{**out,"certificate":(tag,bad)}))

    def test_empty_and_incomplete(self):
        self.assertTrue(x.verify(0,((),),x.solve(0,((),))))
        self.assertFalse(x.verify(1,((1,),),{"status":"UNSAT","certificate":("empty",0)}))
        self.assertEqual(x.solve(0,())["status"],"UNKNOWN")
        # Two contradictory width-six parity systems are outside the detector.
        vs = tuple(range(1,7))
        cs = x.encode_parity(vs,0) + x.encode_parity(vs,1)
        self.assertFalse(x._brute(cs))
        self.assertEqual(x.solve(6,cs)["status"],"UNKNOWN")
        self.assertFalse(x.verify(6,cs,x.solve(6,cs)))

    def test_invalid(self):
        for cs in (((0,),), ((True,),), ((2,),)):
            with self.assertRaises(ValueError):
                x.solve(1,cs)


if __name__ == "__main__":
    unittest.main()
