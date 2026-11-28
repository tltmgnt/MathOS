import copy
import itertools
import json
import random
import unittest

from mathos.research.pnp_analogy import find_strengthening,query_strengthened,verify_query_strengthened
from mathos.research.pnp_knowledge_library import build,budget,verify_strengthening
from mathos.research.pnp_knowledge_frontier import strengthening_control,run as knowledge
from mathos.research.pnp_evidence_benchmark import benchmark
from mathos.research.pnp_evidence_scheduler import evaluate
from mathos.research.pnp_failure_synthesis import run as failures
from mathos.research.pnp_abstraction_frontier import run as abstraction
from mathos.research.pnp_analogy_frontier import run,audit
from mathos.research.pnp_structural_kernel import brute


class TestAnalogy(unittest.TestCase):
    def test_automatic_and_padding(self):
        c=strengthening_control()
        t=c["template"]
        for n,f in ((c["n"],c["clauses"]),(2,[(1,),(-1,)]),(3,[()] )):
            a=find_strengthening(n,f,t,budget())
            self.assertEqual(a["status"],"matched")
            self.assertTrue(verify_strengthening(n,f,t,a["embedding"],a["witnesses"],budget()))
            self.assertFalse(brute(n,f,budget()))
        self.assertEqual(find_strengthening(2,[(1,)],t,budget())["status"],"not_found")
        self.assertEqual(find_strengthening(2,[(1,),(-1,)],t,budget(),limit=1)["status"],"candidate_limit")

    def test_small_exhaustive_reference(self):
        # Independent enumeration of all signed injections for two variables.
        t=strengthening_control()["template"]
        rng=random.Random(1717)
        choices=[(1,),(-1,),(2,),(-2,),(3,),(-3,)]
        choices += [tuple(a*s for a,s in zip(v,bits))
                    for v in itertools.combinations(range(1,4),2)
                    for bits in itertools.product((-1,1),repeat=2)]
        for _ in range(150):
            f=rng.sample(choices,rng.randrange(len(choices)+1))
            def check(e):
                return all(any(set(q)<={e[x-1] if x>0 else -e[-x-1] for x in c} for q in f)
                           for c in t["axioms"])
            expected=any(check(tuple(a*s for a,s in zip(v,bits)))
                         for v in itertools.permutations(range(1,4),2)
                         for bits in itertools.product((-1,1),repeat=2))
            a=find_strengthening(3,f,t,budget())
            self.assertEqual(a["status"]=="matched",expected)
            if expected:
                self.assertFalse(brute(3,f,budget()))

    def test_tampering(self):
        c=strengthening_control()
        lib=build([c["template"]])
        n,f=c["n"],c["clauses"]
        r=query_strengthened(n,f,lib)
        self.assertEqual(r["decision"],"unsat")
        self.assertTrue(verify_query_strengthened(n,f,lib,json.loads(json.dumps(r))))
        x=copy.deepcopy(r)
        x["attempts"][0]["witnesses"][0]=(999,)
        with self.assertRaises(ValueError):
            verify_query_strengthened(n,f,lib,x)
        with self.assertRaises(ValueError):
            verify_query_strengthened(n,f,lib,{**r,"decision":"unknown"})

    def test_pipeline(self):
        s=benchmark(random_count=4)
        a=evaluate(s)
        f=failures(s,a,count=4)
        t=abstraction(s,a,f,count=4)
        k=knowledge(s,a,f,t,count=4)
        r=run(s,a,f,t,k,count=4)
        self.assertEqual(r["completion"],"completed")
        self.assertTrue(audit(s,a,f,t,k,json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["fresh_cases"],4)
        with self.assertRaises(ValueError):
            audit(s,a,f,t,k,{**r,"rows":r["rows"][:-1]})


if __name__=="__main__":
    unittest.main()
