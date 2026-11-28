import copy
import itertools
import json
import random
import unittest

from mathos.research.pnp_guided_inference import derive,replay,compact_view,verify_view,investigate,verify_investigation
from mathos.research.pnp_guided_frontier import control_results,run,audit
from mathos.research.pnp_knowledge_library import budget
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_evidence_benchmark import benchmark
from mathos.research.pnp_evidence_scheduler import evaluate
from mathos.research.pnp_failure_synthesis import run as failures
from mathos.research.pnp_abstraction_frontier import run as abstraction
from mathos.research.pnp_knowledge_frontier import run as knowledge
from mathos.research.pnp_analogy_frontier import run as analogy
from mathos.research.pnp_semantic_frontier import run as semantic


class TestGuidedInference(unittest.TestCase):
    def test_multi_wave_controls(self):
        rows=control_results()
        self.assertEqual(len(rows),2)
        for row in rows:
            self.assertEqual(row["single"]["decision"],"unknown")
            self.assertEqual(row["multi"]["compact_decision"],"unsat")
            self.assertGreater(max(s["depth"] for s in row["multi"]["inference"]["steps"]),1)

    def test_assignment_equivalence(self):
        rng=random.Random(1919)
        for _ in range(100):
            n=rng.randint(1,6)
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),rng.randint(1,n)))
               for _ in range(rng.randrange(20))]
            for order in ("fifo","short_first"):
                a=derive(n,f,budget(),order=order)
                g=replay(n,f,json.loads(json.dumps(a)),budget())
                v=compact_view(g,budget())
                h=verify_view(g,json.loads(json.dumps(v)),budget())
                def sat(formula,bits):
                    return all(any(bits[abs(x)-1]==(x>0) for x in c) for c in formula)
                for bits in itertools.product((False,True),repeat=n):
                    self.assertEqual(sat(f,bits),sat(g,bits))
                    self.assertEqual(sat(g,bits),sat(h,bits))

    def test_forgery_and_caps(self):
        n=3
        f=[(1,),(-1,2),(-2,3),(1,2,3)]
        r=derive(n,f,budget())
        self.assertTrue(r["steps"])
        for key,value in (("depth",4),("pivot",999),("positive",999),("clause",())):
            x=copy.deepcopy(r)
            x["steps"][0][key]=value
            with self.assertRaises(ValueError):
                replay(n,f,x,budget())
        a=derive(n,f,Budget(max_steps=1))
        self.assertEqual(a["status"],"resource_exhausted")
        g=replay(n,f,a,budget())
        v=compact_view(g,Budget(max_steps=1))
        self.assertEqual(v["status"],"identity_fallback")
        self.assertEqual(verify_view(g,v,budget()),g)
        v=compact_view(g,budget())
        self.assertTrue(v["dropped"])
        with self.assertRaises(ValueError):
            verify_view(g,{**v,"dropped":[]},budget())
        a=derive(n,f,budget(),derived=1)
        self.assertLessEqual(len(a["steps"]),1)

    def test_pipeline(self):
        s=benchmark(random_count=4)
        a=evaluate(s)
        f=failures(s,a,count=4)
        t=abstraction(s,a,f,count=4)
        k=knowledge(s,a,f,t,count=4)
        y=analogy(s,a,f,t,k,count=4)
        z=semantic(s,a,f,t,k,y,count=4)
        r=run(s,a,f,t,k,y,z,count=4)
        self.assertEqual(r["completion"],"completed")
        self.assertTrue(audit(s,a,f,t,k,y,z,json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["cases"],4)
        with self.assertRaises(ValueError):
            audit(s,a,f,t,k,y,z,{**r,"rows":r["rows"][:-1]})


if __name__=="__main__":
    unittest.main()
