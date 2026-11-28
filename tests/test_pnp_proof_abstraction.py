import copy
import json
import random
import unittest

from mathos.research.pnp_proof_abstraction import compress,verify_template,verify_embedding,find_embedding
from mathos.research.pnp_resolution_refutation import propose
from mathos.research.pnp_structural_kernel import Budget,brute
from mathos.research.pnp_evidence_benchmark import benchmark
from mathos.research.pnp_evidence_scheduler import evaluate
from mathos.research.pnp_failure_synthesis import run as failures
from mathos.research.pnp_abstraction_frontier import run,audit,variants


class TestAbstraction(unittest.TestCase):
    def test_support_and_reuse(self):
        f=[(2,),(-2,4),(-4,),(7,8)]
        c=compress(8,f,propose(8,f,Budget()),Budget())
        t=c["template"]
        self.assertEqual(t["n"],2)
        self.assertEqual(len(t["axioms"]),3)
        self.assertEqual(tuple(c["source_embedding"]),(2,4))
        self.assertTrue(verify_embedding(8,f,t,(2,4),Budget()))
        n,g,e=variants(t)
        self.assertTrue(verify_embedding(n,g,t,e,Budget()))
        a=find_embedding(n,g,t,Budget())
        self.assertEqual(a["status"],"matched")
        self.assertTrue(verify_embedding(n,g,t,a["embedding"],Budget()))
        self.assertFalse(brute(n,g,Budget()))
        self.assertNotEqual(find_embedding(3,[(1,2,3)],t,Budget())["status"],"matched")

    def test_empty_clause_and_forgery(self):
        f=[(),(1,2)]
        c=compress(2,f,propose(2,f,Budget()),Budget())
        t=c["template"]
        self.assertEqual(t["n"],0)
        self.assertTrue(verify_embedding(0,[()],t,(),Budget()))
        with self.assertRaises(ValueError):
            verify_embedding(0,[],t,(),Budget())
        f=[(1,),(-1,2),(-2,)]
        t=compress(2,f,propose(2,f,Budget()),Budget())["template"]
        with self.assertRaises(ValueError):
            verify_embedding(2,f,t,(1,1),Budget())
        with self.assertRaises(ValueError):
            verify_embedding(2,[(1,),(-2,)],t,(1,2),Budget())
        with self.assertRaises(ValueError):
            verify_template({**t,"root":0},Budget())
        with self.assertRaises(ValueError):
            verify_template({**t,"steps":[(999,0,1)]},Budget())

    def test_random_refutations(self):
        rng=random.Random(1515)
        seen=0
        for _ in range(100):
            n=rng.randint(3,7)
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),3))
               for _ in range(6*n)]
            p=propose(n,f,Budget(),width=8)
            if p is None:
                continue
            seen+=1
            c=compress(n,f,p,Budget())
            t=c["template"]
            self.assertTrue(verify_embedding(n,f,t,c["source_embedding"],Budget()))
            m,g,e=variants(t)
            self.assertTrue(verify_embedding(m,g,t,e,Budget()))
            self.assertFalse(brute(m,g,Budget()))
        self.assertGreater(seen,0)

    def test_pipeline(self):
        s=benchmark(random_count=4)
        a=evaluate(s)
        f=failures(s,a,count=4)
        r=run(s,a,f,count=4)
        self.assertEqual(r["completion"],"completed")
        self.assertTrue(audit(s,a,f,json.loads(json.dumps(r))))
        x=copy.deepcopy(r)
        x["summary"]["fresh_matches"]+=1
        with self.assertRaises(ValueError):
            audit(s,a,f,x)


if __name__=="__main__":
    unittest.main()
