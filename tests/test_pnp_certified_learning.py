import copy
import json
import random
import unittest
from mathos.research.pnp_certified_learning import solve,verify_hybrid,verify_lemma,candidates
from mathos.research.pnp_resolution_refutation import propose
from mathos.research.pnp_structural_kernel import Budget,brute,truth
from mathos.research.pnp_evidence_benchmark import benchmark
from mathos.research.pnp_evidence_scheduler import evaluate,train
from mathos.research.pnp_failure_synthesis import run as failures
from mathos.research.pnp_learning_frontier import run,audit


class TestLearning(unittest.TestCase):
    def test_failed_assumption(self):
        f=[(1,2),(1,-2)]
        p=propose(2,f+[(-1,)],Budget())
        lemma={"assumptions":(-1,),"clause":(1,),"proof":p}
        self.assertEqual(verify_lemma(2,f,lemma,Budget()),(1,))
        with self.assertRaises(ValueError):
            verify_lemma(2,f,{**lemma,"clause":(-1,)},Budget())
        with self.assertRaises(ValueError):
            verify_lemma(2,[(1,2)],lemma,Budget())

    def test_pair_lemma(self):
        f=[(1,2)]
        p=propose(2,f+[(-1,),(-2,)],Budget())
        lemma={"assumptions":(-2,-1),"clause":(1,2),"proof":p}
        self.assertEqual(verify_lemma(2,f,lemma,Budget()),(1,2))
        self.assertEqual(len(set(candidates(3,[(1,2,3)],24))),18)

    @classmethod
    def setUpClass(cls):
        cls.source=benchmark(random_count=4)
        cls.scheduler=evaluate(cls.source)
        cls.failures=failures(cls.source,cls.scheduler,count=4)
        cls.policy=train(cls.source)
        cls.plan=cls.failures["selected_plan"]

    def test_random_soundness(self):
        rng=random.Random(1414)
        for _ in range(60):
            n=rng.randint(3,7)
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3))
               for _ in range(rng.randint(1,5*n))]
            a=solve(n,f,self.policy,self.plan,total=12_000)
            self.assertTrue(verify_hybrid(n,f,self.policy,json.loads(json.dumps(a))))
            if a["decision"]!="unknown":
                self.assertEqual(a["decision"]=="sat",brute(n,f,Budget()))
            self.assertLessEqual(a["work_steps"],12_000)

    def test_small_budget_and_tampering(self):
        f=[(1,2,3),(-1,-2,-3)]
        a=solve(3,f,self.policy,self.plan,total=3)
        self.assertEqual(a["decision"],"unknown")
        self.assertIsNotNone(a["final"])
        self.assertTrue(verify_hybrid(3,f,self.policy,a))
        for field,val in (("decision","unsat"),("learned_clauses",1),("work_steps",4),("input_sha256","0"*64)):
            with self.assertRaises(ValueError):
                verify_hybrid(3,f,self.policy,{**a,field:val})
        a=solve(3,f,self.policy,self.plan,total=150)
        self.assertTrue(verify_hybrid(3,f,self.policy,a))

    def test_pipeline(self):
        r=run(self.source,self.scheduler,self.failures,count=6)
        self.assertEqual(r["completion"],"completed")
        self.assertTrue(audit(self.source,self.scheduler,self.failures,json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["cases"],6)
        self.assertFalse(r["p_equals_np_established"])
        forged=copy.deepcopy(r)
        forged["summary"]["hybrid_only"]+=1
        with self.assertRaises(ValueError):
            audit(self.source,self.scheduler,self.failures,forged)
        with self.assertRaises(ValueError):
            run(self.source,self.scheduler,self.failures,seed=self.failures["seed"],count=1)


if __name__=="__main__":
    unittest.main()
