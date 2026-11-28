import copy
import json
import unittest
from mathos.research.pnp_evidence_benchmark import manifest,digest,benchmark,audit,DEFAULT_PLANS


class TestEvidenceBenchmark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=benchmark(random_count=4)

    def test_manifest(self):
        a=manifest(123,4)
        self.assertEqual(a,manifest(123,4))
        self.assertNotEqual(digest(a),digest(manifest(124,4)))
        self.assertEqual(len(a),15)
        self.assertEqual(len({c["id"] for c in a}),len(a))

    def test_replay(self):
        r=self.report
        self.assertEqual(r["completion"],"completed")
        self.assertEqual(audit(json.loads(json.dumps(r)))["cases"],15)
        m=r["metrics"]
        self.assertEqual(m["cases"],15)
        self.assertGreater(m["portfolio_union_decided"],0)
        self.assertEqual(m["portfolio_union_decided"]+m["portfolio_union_unknown"],15)
        self.assertEqual(len(m["plans"]),len(DEFAULT_PLANS))
        for p in m["plans"].values():
            self.assertEqual(p["decided"]+p["unknown"],15)
            self.assertEqual(p["sat"]+p["unsat"],p["decided"])
            self.assertEqual(p["coverage_without_plan"]+p["unique"],m["portfolio_union_decided"])

    def test_tampering(self):
        for key,val in (("manifest_sha256","0"*64),("p_equals_np_established",True),
                        ("rows",self.report["rows"][:-1]),("seed",1)):
            with self.assertRaises(ValueError):
                audit({**self.report,key:val})
        r=copy.deepcopy(self.report)
        r["rows"][0]["reference"]=not r["rows"][0]["reference"]
        with self.assertRaises(ValueError):
            audit(r)
        r=copy.deepcopy(self.report)
        r["metrics"]["portfolio_union_decided"]+=1
        with self.assertRaises(ValueError):
            audit(r)

    def test_exhaustion_is_not_unsat(self):
        r=benchmark(random_count=0,steps=1)
        self.assertEqual(r["completion"],"completed")
        self.assertTrue(audit(r)["complete"])
        exhausted=0
        for row in r["rows"]:
            for plan in row["plans"]:
                e=plan["report"]["entries"][0]
                if e["status"]=="resource_exhausted":
                    exhausted+=1
                    self.assertEqual(e["decision"],"unknown")
                    self.assertIsNone(e["proof"])
                elif e["decision"]!="unknown":
                    self.assertEqual(e["decision"]=="sat",row["reference"])
        self.assertGreater(exhausted,0)


if __name__=="__main__":
    unittest.main()
