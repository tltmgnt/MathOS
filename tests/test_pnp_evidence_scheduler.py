import copy
import json
import unittest

from mathos.research.pnp_evidence_benchmark import benchmark
from mathos.research.pnp_evidence_scheduler import _fit, train, evaluate, audit, execute, replay
from mathos.research.pnp_unified_portfolio import DEFAULT_PLANS


class TestEvidenceScheduler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=benchmark(random_count=8)
        cls.result=evaluate(cls.source)

    def test_frozen_training_policy(self):
        p=train(self.source)
        self.assertEqual(p["training_cases"],15)
        self.assertEqual({tuple(x["plan"]) for x in p["order"]},set(DEFAULT_PLANS))
        self.assertEqual(sum(x["marginal_training_decisions"] for x in p["order"]),
                         p["training_union_decided"])
        self.assertFalse(any(x.startswith("holdout") for x in p["training_ids"]))
        rows=copy.deepcopy(self.source["rows"])
        for row in rows:
            if row["case"]["group"]=="holdout":
                for entry in row["plans"]:
                    entry["report"]["entries"][0]["work_steps"]=999999
                    entry["report"]["entries"][0]["decision"]="unsat"
        self.assertEqual(_fit(rows),p)
        self.assertEqual(_fit([r for r in rows if r["case"]["group"]!="holdout"]),p)

    def test_holdout_and_replay(self):
        r=self.result
        self.assertEqual(r["completion"],"completed")
        self.assertEqual(audit(self.source,json.loads(json.dumps(r)))["holdout_cases"],4)
        s=r["summary"]
        self.assertEqual(sum(s["paired"].values()),4)
        for row in r["rows"]:
            self.assertEqual(row["case"]["group"],"holdout")
            for arm in ("baseline","learned"):
                a=row[arm]
                self.assertLessEqual(a["work_steps"],r["total_steps_per_case"])
                self.assertTrue(replay(row["case"]["n"],row["case"]["clauses"],r["policy"],
                                       r["total_steps_per_case"],a))
                if a["decision"]!="unknown":
                    self.assertEqual(a["decision"]=="sat",row["reference"])
                    self.assertNotEqual(a["attempts"][-1]["report"]["decision"],"unknown")
                    self.assertTrue(all(x["report"]["decision"]=="unknown" for x in a["attempts"][:-1]))

    def test_tight_budget(self):
        p=self.result["policy"]
        f=[(1,2,3),(-1,-2,-3)]
        for arm in ("baseline","learned"):
            a=execute(3,f,p,arm,1,5)
            self.assertEqual(a["decision"],"unknown")
            self.assertLessEqual(a["work_steps"],1)
            self.assertTrue(replay(3,f,p,1,a))

    def test_tampering(self):
        for field,value in (("source_sha256","0"*64),("p_equals_np_established",True),
                            ("rows",self.result["rows"][:-1])):
            with self.assertRaises(ValueError):
                audit(self.source,{**self.result,field:value})
        r=copy.deepcopy(self.result)
        r["policy"]["order"].reverse()
        with self.assertRaises(ValueError):
            audit(self.source,r)
        r=copy.deepcopy(self.result)
        r["rows"][0]["learned"]["attempts"][0]["quota"]+=1
        with self.assertRaises(ValueError):
            audit(self.source,r)
        r=copy.deepcopy(self.result)
        r["summary"]["paired"]["both_decided"]+=1
        with self.assertRaises(ValueError):
            audit(self.source,r)

    def test_missing_holdout(self):
        with self.assertRaises(ValueError):
            evaluate(benchmark(random_count=0))


if __name__=="__main__":
    unittest.main()
