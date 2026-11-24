import unittest
from unittest.mock import patch

from mathos.research import tga_proctor_replay_bridge as b
from mathos.research import tga_proctor_combined_boundary as p
from mathos.research import tga_proctor_round_boundary as r


class ReplayBridgeTests(unittest.TestCase):
    def test_real_fixtures_and_mirror(self):
        fs=b.cases()
        self.assertEqual(len(fs),86)
        self.assertEqual(sum(not f[5] for f in fs),2)
        with patch.object(p,"replay",side_effect=AssertionError("no legacy replay")):
            for _,n,cs,bs,final,ok,empty in fs:
                got=b.check_shape(n,cs,bs)
                self.assertEqual(got,final if ok else None)
                self.assertEqual(got is not None and () in got,empty)

    def test_annotation_rejects_invalid(self):
        cs=((1,2),(-1,2))
        for bs in (((),),(((2,1,1),),),(((0,1,0),),)):
            with self.assertRaises(ValueError):
                b.annotate(2,cs,bs)
        bs,final=b.annotate(2,cs,(((0,1,1),),))
        self.assertEqual(bs,(((0,1,1,(2,)),),))
        self.assertEqual(final,((2,),))

    def test_lean_export_is_deterministic(self):
        a=b.emit_lean()
        self.assertEqual(a,b.emit_lean())
        self.assertIn("F034_EXECUTABLE_REPLAY_OK cases=86",a)
        self.assertIn("def main : IO Unit",a)
        self.assertIn("def b0 : List Batch",a)


if __name__=="__main__":
    unittest.main()
