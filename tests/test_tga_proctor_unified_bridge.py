import unittest
from mathos.research import tga_proctor_unified_bridge as u


class UnifiedBridgeTests(unittest.TestCase):
    def test_fixtures(self):
        fs=u.cases()
        self.assertEqual(len(fs),53)
        self.assertEqual(sum(f[-1] for f in fs),19)
        for n,f,env,ok in fs:
            self.assertEqual(u.check(n,f,env),ok)

    def test_binding_does_not_trust_envelope(self):
        env=(1,((),),((),False,"EMPTY",None))
        self.assertTrue(u.check(1,((),),env))
        self.assertFalse(u.check(1,((1,),),env))
        self.assertFalse(u.check(2,((),),env))
        self.assertFalse(u.check(1,((),),(1,((),),((),False,"UNKNOWN",None))))

    def test_export(self):
        a=u.emit_lean()
        self.assertEqual(a,u.emit_lean())
        self.assertIn("F034_UNIFIED_REPLAY_OK cases=53",a)
        self.assertIn("boundCheck",a)


if __name__=="__main__":
    unittest.main()
