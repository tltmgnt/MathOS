import unittest
from mathos.research import tga_proctor_xor_bridge as b
from mathos.research import tga_proctor_xor_cnf as x
from mathos.research import tga_proctor_replay_bridge as r


class XorBridgeTests(unittest.TestCase):
    def test_fixtures(self):
        fs=b.cases()
        self.assertEqual(len(fs),18)
        self.assertEqual(sum(f[-1] for f in fs),9)
        for n,cs,bs,final,p,expected in fs:
            self.assertEqual(r.check_shape(n,cs,bs),final)
            self.assertEqual(b.check(n,final,p),expected)

    def test_annotation(self):
        cs=x.encode_parity((1,2),0)+x.encode_parity((1,2),1)
        self.assertTrue(b.check(2,cs,b.annotate(2,cs,x.solve(2,cs))))
        with self.assertRaises(ValueError):
            b.annotate(2,cs,dict(status="UNKNOWN"))
        with self.assertRaises(ValueError):
            b.annotate(0,((),),x.solve(0,((),)))

    def test_export(self):
        a=b.emit_lean()
        self.assertEqual(a,b.emit_lean())
        self.assertIn("F034_XOR_REPLAY_OK cases=18",a)
        self.assertIn("checkChainXor",a)


if __name__=="__main__":
    unittest.main()
