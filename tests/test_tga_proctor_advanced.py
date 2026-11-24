import copy
import unittest
from mathos.research import tga_proctor_advanced as p

class Advanced(unittest.TestCase):
    def test_labs(self):
        r=p.plan()
        self.assertEqual(set(r["labs"]),set(p.TRACKS))
        self.assertFalse(r["formal_kernel_verified"])
        self.assertFalse(r["learner_outcomes_measured"])
        self.assertEqual(r["global_promotion"],"NONE")
    def test_refinement(self):
        r=p.dynamic_graph()
        self.assertTrue(r["cycle_rejected"])
        self.assertFalse(r["canonical_graph_modified"])
    def test_adaptation(self):
        s={m[0]:8 for m in p.MODULES};c={k:8 for k in p.CAP}
        self.assertTrue(p.remediation(s,c,True)["threshold_met"])
        self.assertFalse(p.remediation(s,c,False)["threshold_met"])
        s["M4"]=0;s["M1"]=2
        r=p.remediation(s,c,True)
        self.assertEqual([x["module"] for x in r["module_remediation"]],["M4","M1"])
        self.assertFalse(r["completion_awarded"])
        s["M1"]=True
        with self.assertRaises(ValueError):p.remediation(s,c,True)
    def test_ledger(self):
        key=b"x"*32  # test fixture key, never a deployed key
        l=p.seal([{"scope":"finite","value":"-1"},{"scope":"finite","value":"3"}],key)
        head,count=l["head"],l["count"]
        self.assertTrue(p.verify_ledger(l,key,head,count))
        for mutate in (
            lambda x:x["entries"][0]["payload"].update(value="0"),
            lambda x:x["entries"].reverse(),
            lambda x:x["entries"].pop(),
            lambda x:x.update(head="0"*64),
        ):
            t=copy.deepcopy(l);mutate(t)
            self.assertFalse(p.verify_ledger(t,key,head,count))
        self.assertFalse(p.verify_ledger(l,b"y"*32,head,count))
        shorter=p.seal([{"scope":"finite","value":"-1"}],key)
        self.assertFalse(p.verify_ledger(shorter,key,head,count))
