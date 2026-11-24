import unittest
from mathos.research import tga_proctor_capacity_bridge as b
from mathos.research import tga_proctor_capacity as c
from mathos.research import tga_proctor_replay_bridge as r


class CapacityBridgeTests(unittest.TestCase):
    def test_actual_and_tampered_fixtures(self):
        fs=b.cases()
        self.assertEqual(len(fs),17)
        self.assertEqual(sum(f[-1] for f in fs),7)
        for n,cs,bs,final,cert,expected in fs:
            self.assertEqual(r.check_shape(n,cs,bs),final)
            self.assertEqual(b.check(n,final,cert),expected)

    def test_annotation_rejects_unverified(self):
        n,cs=c.php(2,2)
        proof=c.solve(n,cs,2)
        self.assertTrue(b.check(n,cs,b.annotate(n,cs,proof)))
        with self.assertRaises(ValueError):
            b.annotate(n,cs,dict(status="UNKNOWN"))

    def test_deterministic_export(self):
        a=b.emit_lean()
        self.assertEqual(a,b.emit_lean())
        self.assertIn("F034_CAPACITY_REPLAY_OK cases=17",a)
        self.assertIn("checkChainCapacity",a)


if __name__=="__main__":
    unittest.main()
