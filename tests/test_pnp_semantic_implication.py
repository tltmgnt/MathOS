import copy
import itertools
import json
import random
import unittest

from mathos.research.pnp_semantic_implication import closure,replay_closure,transfer,verify_transfer
from mathos.research.pnp_semantic_frontier import control,run,audit
from mathos.research.pnp_knowledge_library import budget
from mathos.research.pnp_evidence_benchmark import benchmark
from mathos.research.pnp_evidence_scheduler import evaluate
from mathos.research.pnp_failure_synthesis import run as failures
from mathos.research.pnp_abstraction_frontier import run as abstraction
from mathos.research.pnp_knowledge_frontier import run as knowledge
from mathos.research.pnp_analogy_frontier import run as analogy


class TestImplication(unittest.TestCase):
    def test_inference_only(self):
        c=control()
        self.assertEqual(c["raw"]["decision"],"unknown")
        self.assertEqual(c["semantic"]["reason"],"template_transfer")
        self.assertTrue(verify_transfer(c["n"],c["clauses"],c["library"],json.loads(json.dumps(c["semantic"]))))

    def test_direct_and_limits(self):
        r=transfer(1,[(1,),(-1,)],{"entries":[]})
        self.assertEqual(r["reason"],"direct_empty_clause")
        self.assertTrue(verify_transfer(1,[(1,),(-1,)],{"entries":[]},r))
        f=[(1,2),(-1,2),(1,-2)]
        a=closure(2,f,budget(),pairs=1)
        self.assertEqual(a["status"],"pair_limit")
        self.assertTrue(replay_closure(2,f,a,budget()))
        a=closure(2,f,budget(),derived=1)
        self.assertEqual(a["status"],"derived_limit")

    def test_every_assignment_preserved(self):
        rng=random.Random(1818)
        for _ in range(120):
            n=rng.randint(1,6)
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),rng.randint(1,n)))
               for _ in range(rng.randint(0,24))]
            c=closure(n,f,budget())
            g=replay_closure(n,f,json.loads(json.dumps(c)),budget())
            def sat(formula,bits):
                return all(any(bits[abs(x)-1]==(x>0) for x in cl) for cl in formula)
            for bits in itertools.product((False,True),repeat=n):
                self.assertEqual(sat(f,bits),sat(g,bits))

    def test_forged_implication(self):
        c=control()
        n,f,lib=c["n"],c["clauses"],c["library"]
        r=c["semantic"]
        for key,value in (("pivot",999),("positive",999),("clause",())):
            x=copy.deepcopy(r)
            x["closure"]["steps"][0][key]=value
            with self.assertRaises(ValueError):
                verify_transfer(n,f,lib,x)
        with self.assertRaises(ValueError):
            verify_transfer(n,f[:-1],lib,r)
        with self.assertRaises(ValueError):
            verify_transfer(n,f,lib,{**r,"reason":"direct_empty_clause"})

    def test_pipeline(self):
        s=benchmark(random_count=4)
        a=evaluate(s)
        f=failures(s,a,count=4)
        t=abstraction(s,a,f,count=4)
        k=knowledge(s,a,f,t,count=4)
        y=analogy(s,a,f,t,k,count=4)
        r=run(s,a,f,t,k,y,count=4)
        self.assertEqual(r["completion"],"completed")
        self.assertTrue(audit(s,a,f,t,k,y,json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["fresh_cases"],4)
        with self.assertRaises(ValueError):
            audit(s,a,f,t,k,y,{**r,"rows":r["rows"][:-1]})


if __name__=="__main__":
    unittest.main()
