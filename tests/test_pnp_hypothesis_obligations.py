import copy
import json
import random
import unittest
from mathos.research.pnp_component_parity import propose,verify
from mathos.research.pnp_hypothesis_obligations import disconnected,run,audit,budget
from mathos.research.pnp_cross_model import prism
from mathos.research.pnp_expander_size import family
from mathos.research.pnp_structural_kernel import brute
from mathos.research.pnp_proof_simulation_frontier import run as simulation
from mathos.research.pnp_barrier_frontier import run as barriers


class TestComponentHypotheses(unittest.TestCase):
    def test_global_even_counterexample(self):
        n,f=disconnected(3,True,True)
        p=propose(n,f,budget())
        self.assertEqual(p["global_rhs"],0)
        self.assertEqual(p["decision"],"unsat")
        self.assertTrue(verify(n,f,p,budget()))
        self.assertEqual(len(p["components"]),2)

    def test_random_renaming(self):
        rng=random.Random(26026)
        for _ in range(30):
            odd=bool(rng.randrange(2))
            n,f,_=prism(3,inconsistent=odd)
            labels=rng.sample(range(1,20),n)
            g=[tuple((1 if x>0 else -1)*labels[abs(x)-1] for x in c) for c in f]
            rng.shuffle(g)
            p=propose(20,g,budget())
            self.assertTrue(verify(20,g,json.loads(json.dumps(p)),budget()))
            self.assertEqual(p["decision"],"unsat" if odd else "sat")
            self.assertEqual(brute(n,f,budget()),not odd)
        for odd in (True,False):
            n,f,_=family(3,odd=odd)
            p=propose(n,f,budget())
            self.assertTrue(verify(n,f,p,budget()))
            self.assertEqual(p["decision"],"unsat" if odd else "sat")

    def test_tamper(self):
        n,f=disconnected(3,True,True)
        p=propose(n,f,budget())
        for key,value in (("global_rhs",1),("components",[]),("decision","sat")):
            with self.assertRaises(ValueError):
                verify(n,f,{**p,key:value},budget())
        q=copy.deepcopy(p)
        q["proof"]["rows"]=list(range(len(q["rows"])))
        with self.assertRaises(ValueError):
            verify(n,f,q,budget())
        self.assertIsNone(propose(n,f[:-1],budget()))

    def test_pipeline(self):
        s,b=simulation(),barriers()
        r=run(s,b)
        self.assertEqual(r["completion"],"completed",r.get("reason"))
        self.assertTrue(audit(s,b,json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["even_global_unsat"],4)
        self.assertEqual(r["summary"]["cases"],16)
        q=copy.deepcopy(r)
        q["obligations"][-1]["status"]="proved"
        with self.assertRaises(ValueError):
            audit(s,b,q)
        q=copy.deepcopy(r)
        q["hypotheses"][0]["counterexample_row"]=0
        with self.assertRaises(ValueError):
            audit(s,b,q)


if __name__=="__main__":
    unittest.main()
