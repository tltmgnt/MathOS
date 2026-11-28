import copy
import itertools
import json
import random
import unittest

from mathos.research.pnp_degree_closure import derive,verify,adaptive,verify_adaptive
from mathos.research.pnp_degree_frontier import run,audit
from mathos.research.pnp_inference_complexity import budget
from mathos.research.pnp_structural_kernel import brute,Budget,Exhausted
from mathos.research.pnp_proof_simulation_frontier import run as simulation
from mathos.research.pnp_barrier_frontier import run as barriers
from mathos.research.pnp_hypothesis_obligations import run as hypotheses
from mathos.research.pnp_conjecture_frontier import run as refinement
from mathos.research.pnp_symbolic_frontier import run as symbolic
from mathos.research.pnp_boolean_lift_frontier import run as lifting


class TestDegreeClosure(unittest.TestCase):
    def test_exhaustive_two_variables(self):
        pool=[tuple((i+1)*s for i,s in enumerate(signs) if s)
              for signs in itertools.product((-1,0,1),repeat=2)]
        for mask in range(1<<len(pool)):
            f=[c for i,c in enumerate(pool) if mask>>i&1]
            r=derive(2,f,budget(),degree=2)
            self.assertTrue(verify(2,f,r,budget()))
            self.assertEqual(r["status"]=="refuted",not brute(2,f,budget()))

    def test_random_full_degree(self):
        rng=random.Random(30030)
        for _ in range(80):
            n=rng.randint(1,4)
            f=[tuple(v if rng.randrange(2) else -v
                for v in rng.sample(range(1,n+1),rng.randint(1,min(n,3))))
                for _ in range(rng.randrange(15))]
            a=adaptive(n,f,budget)
            self.assertTrue(verify_adaptive(n,f,json.loads(json.dumps(a)),budget))
            self.assertNotEqual(a[-1]["status"],"resource_exhausted")
            self.assertEqual(a[-1]["status"]=="refuted",not brute(n,f,budget()))

    def test_closed_space_and_tamper(self):
        f=[(1,2)]
        r=derive(2,f,budget(),degree=2)
        self.assertEqual(r["status"],"closed_no_refutation")
        self.assertTrue(verify(2,f,r,budget()))
        with self.assertRaises(ValueError):
            verify(2,f,{**r,"basis":[]},budget())
        f=[(1,),(-1,2),(-2,)]
        r=derive(2,f,budget(),degree=2)
        self.assertEqual(r["status"],"refuted")
        with self.assertRaises(ValueError):
            verify(2,f,{**r,"root":None},budget())
        q=copy.deepcopy(r)
        q["steps"][0]=["mul",999,0]
        with self.assertRaises(ValueError):
            verify(2,f,q,budget())
        with self.assertRaises(Exhausted):
            derive(2,f,budget(),degree=1)
        with self.assertRaises(Exhausted):
            derive(2,f,Budget(max_steps=1),degree=2)

    def test_pipeline(self):
        s,b=simulation(),barriers()
        h=hypotheses(s,b)
        t=refinement(s,b,h)
        y=symbolic(s,b,h,t)
        l=lifting(s,b,h,t,y)
        r=run(s,b,h,t,y,l)
        self.assertEqual(r["completion"],"completed",r.get("reason"))
        self.assertTrue(audit(s,b,h,t,y,l,json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["cases"],30)
        self.assertGreater(r["summary"]["closed_spaces"],0)
        with self.assertRaises(ValueError):
            audit(s,b,h,t,y,l,{**r,"rows":r["rows"][:-1]})
        with self.assertRaises(ValueError):
            audit(s,b,h,t,y,l,{**r,"p_not_equals_np_established":True})


if __name__=="__main__":
    unittest.main()
