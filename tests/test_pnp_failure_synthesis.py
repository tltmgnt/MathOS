import copy
import itertools
import random
import json
import unittest

from mathos.research.pnp_resolution_refutation import propose,verify,STRATEGIES
from mathos.research.pnp_failure_synthesis import run,audit,minimize_unsat,fresh_cases
from mathos.research.pnp_evidence_benchmark import benchmark
from mathos.research.pnp_evidence_scheduler import evaluate
from mathos.research.pnp_structural_kernel import Budget,brute,Exhausted


class TestRefutation(unittest.TestCase):
    def test_all_binary_relations(self):
        choices=[(1,),(-1,),(2,),(-2,)]+list(itertools.product((-1,1),(-2,2)))
        for mask in range(256):
            f=[c for i,c in enumerate(choices) if mask>>i&1]
            p=propose(2,f,Budget())
            self.assertEqual(p is not None,not brute(2,f,Budget()))
            if p is not None:
                self.assertTrue(verify(2,f,json.loads(json.dumps(p)),Budget()))

    def test_random_soundness(self):
        rng=random.Random(1313)
        for _ in range(120):
            n=rng.randint(3,7)
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3))
               for _ in range(rng.randint(1,5*n))]
            expected=brute(n,f,Budget())
            for strategy in STRATEGIES:
                p=propose(n,f,Budget(),width=7,strategy=strategy)
                self.assertEqual(p is not None,not expected)
                if p is not None:
                    self.assertTrue(verify(n,f,p,Budget()))

    def test_forgery_and_limits(self):
        f=[(1,),(-1,2),(-2,)]
        p=propose(2,f,Budget())
        for forged in ({**p,"root":0},{**p,"steps":[]},
                       {**p,"steps":[{**p["steps"][0],"pivot":99}]+p["steps"][1:]}):
            with self.assertRaises(ValueError):
                verify(2,f,forged,Budget())
        with self.assertRaises(Exhausted):
            propose(2,f,Budget(),records=1)
        self.assertIsNone(propose(2,[(1,2)],Budget()))

    def test_minimization(self):
        r=minimize_unsat(3,[(1,),(-1,),(2,3)],10000)
        self.assertTrue(r["deletion_minimal"])
        self.assertEqual(len(r["clauses"]),2)
        self.assertFalse(brute(r["n"],r["clauses"],Budget()))
        for i in range(len(r["clauses"])):
            self.assertTrue(brute(r["n"],r["clauses"][:i]+r["clauses"][i+1:],Budget()))


class TestFailureSynthesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=benchmark(random_count=4)
        cls.scheduler=evaluate(cls.source)
        cls.r=run(cls.source,cls.scheduler,count=6)
    def test_pipeline(self):
        self.assertEqual(self.r["completion"],"completed")
        self.assertTrue(audit(self.source,self.scheduler,json.loads(json.dumps(self.r))))
        self.assertEqual(self.r["summary"]["fresh_cases"],6)
        self.assertFalse(self.r["p_not_equals_np_established"])
        self.assertEqual(fresh_cases(count=6),fresh_cases(count=6))
    def test_tamper(self):
        for field,val in (("source_sha256","0"*64),("evaluation",[]),("p_equals_np_established",True)):
            with self.assertRaises(ValueError):
                audit(self.source,self.scheduler,{**self.r,field:val})
        r=copy.deepcopy(self.r)
        r["summary"]["fresh_cases"]+=1
        with self.assertRaises(ValueError):
            audit(self.source,self.scheduler,r)


if __name__=="__main__":
    unittest.main()
