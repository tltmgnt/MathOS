import copy
import itertools
import json
import random
import unittest
from mathos.research.pnp_boolean_lift import polynomial,propose,verify
from mathos.research.pnp_boolean_lift_frontier import cases,attempt,verify_attempt,run,audit
from mathos.research.pnp_inference_complexity import budget
from mathos.research.pnp_structural_kernel import brute,Budget,Exhausted
from mathos.research.pnp_proof_simulation_frontier import run as simulation
from mathos.research.pnp_barrier_frontier import run as barriers
from mathos.research.pnp_hypothesis_obligations import run as hypotheses
from mathos.research.pnp_conjecture_frontier import run as refinement
from mathos.research.pnp_symbolic_frontier import run as symbolic


class TestBooleanLift(unittest.TestCase):
    def test_clause_polynomial(self):
        for signs in itertools.product((-1,0,1),repeat=4):
            c=tuple((i+1)*s for i,s in enumerate(signs) if s)
            p=polynomial(c)
            for x in range(16):
                self.assertEqual(sum((x&a)==a for a in p)%2,
                    int(not any(bool(x>>(abs(v)-1)&1)==(v>0) for v in c)))

    def test_strict_refinement(self):
        c=cases()[0]
        n,f=c["n"],c["clauses"]
        self.assertFalse(brute(n,f,budget()))
        p=propose(n,f,budget())
        self.assertEqual(p["decision"],"unknown")
        self.assertTrue(p["inconsistent_products"])
        q=propose(n,f,budget(),mode="multiply",degree=4)
        self.assertEqual(q["decision"],"unsat")
        for a in (p,q):
            self.assertTrue(verify(n,f,json.loads(json.dumps(a)),budget()))
        for key,value in (("rows",[]),("sources",[]),("decision","sat"),("rhs",0)):
            bad=copy.deepcopy(q)
            bad[key]=value
            with self.assertRaises(ValueError):
                verify(n,f,bad,budget())

    def test_random_soundness(self):
        rng=random.Random(29029)
        for _ in range(100):
            n=rng.randint(1,5)
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),rng.randint(0,min(n,3))))
               for _ in range(rng.randrange(16))]
            ref=brute(n,f,budget())
            for mode,d in (("base",3),("multiply",4)):
                a=propose(n,f,budget(),mode=mode,degree=d)
                self.assertTrue(verify(n,f,a,budget()))
                if a["decision"]!="unknown":
                    self.assertEqual(a["decision"]=="sat",ref)
        with self.assertRaises(Exhausted):
            propose(3,[(1,2,3)],budget(),degree=2)
        with self.assertRaises(Exhausted):
            propose(3,[(1,2,3)],Budget(max_steps=1))
        c=cases()[0]
        a={"mode":"base","degree":3,"status":"resource_exhausted","decision":"unsat",
           "proof":None,"observed_work":1}
        with self.assertRaises(ValueError):
            verify_attempt(c,a,"base",3)

    def test_pipeline(self):
        s,b=simulation(),barriers()
        h=hypotheses(s,b)
        t=refinement(s,b,h)
        y=symbolic(s,b,h,t)
        r=run(s,b,h,t,y)
        self.assertEqual(r["completion"],"completed",r.get("reason"))
        self.assertTrue(audit(s,b,h,t,y,json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["fresh_cases"],24)
        self.assertGreaterEqual(r["summary"]["all"]["multiply_only"],1)
        with self.assertRaises(ValueError):
            audit(s,b,h,t,y,{**r,"rows":r["rows"][:-1]})
        with self.assertRaises(ValueError):
            audit(s,b,h,t,y,{**r,"p_equals_np_established":True})


if __name__=="__main__":
    unittest.main()
