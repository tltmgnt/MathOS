import copy
import json
import unittest
from mathos.research.pnp_conjecture_refinement import (grammar,training,holdout,predict,reference,
    refine,verify_refinement,certify,verify_case,first_counterexample,build)
from mathos.research.pnp_conjecture_frontier import run,audit
from mathos.research.pnp_proof_simulation_frontier import run as simulation
from mathos.research.pnp_barrier_frontier import run as barriers
from mathos.research.pnp_hypothesis_obligations import run as hypotheses


class TestConjectureRefinement(unittest.TestCase):
    def test_finite_domain(self):
        cases=list(training())
        self.assertEqual(len(cases),sum(4**k for k in range(1,7)))
        self.assertEqual(len(set(cases)),len(cases))
        self.assertEqual(len(grammar()),11)
        for p in grammar()[:-1]:
            case,i=first_counterexample(p)
            self.assertIsNotNone(case)
            self.assertEqual(cases[i-1],case)
            self.assertTrue(predict(p,case))
            self.assertFalse(reference(case))
            self.assertTrue(all(predict(p,c)==reference(c) for c in cases[:i-1]))
        self.assertEqual(first_counterexample(("component",)),(None,len(cases)))

    def test_refinement_and_tamper(self):
        r=refine()
        self.assertEqual(r["selected"],("component",))
        self.assertTrue(verify_refinement(json.loads(json.dumps(r))))
        self.assertEqual(sum(len(x["eliminated"]) for x in r["rounds"]),10)
        q=copy.deepcopy(r)
        q["rounds"][0]["examined"]+=1
        with self.assertRaises(ValueError):
            verify_refinement(q)
        q=copy.deepcopy(r)
        q["rounds"][0]["proof"]["global_rhs"]=1
        with self.assertRaises(ValueError):
            verify_refinement(q)
        q=copy.deepcopy(r)
        q["rounds"].pop()
        with self.assertRaises(ValueError):
            verify_refinement(q)

    def test_held_out(self):
        cases=holdout()
        self.assertEqual(len(cases),24)
        self.assertTrue(all(len(c)>6 and all(m>=5 for m,_ in c) for c in cases))
        for case in cases:
            p=certify(case)
            self.assertTrue(verify_case(case,json.loads(json.dumps(p))))
            self.assertEqual(predict(("component",),case),p["decision"]=="sat")
        self.assertEqual(sum(predict(("global",),c)==reference(c) for c in cases),12)

    def test_pipeline(self):
        s,b=simulation(),barriers()
        h=hypotheses(s,b)
        r=run(s,b,h)
        self.assertEqual(r["completion"],"completed",r.get("reason"))
        self.assertTrue(audit(s,b,h,json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["refined_correct"],24)
        self.assertEqual(r["summary"]["baseline_correct"],12)
        self.assertEqual(r["summary"]["universal_obligations_closed"],0)
        q=copy.deepcopy(r)
        q["holdout"][0]["prediction"]=False
        with self.assertRaises(ValueError):
            audit(s,b,h,q)
        with self.assertRaises(ValueError):
            audit(s,b,h,{**r,"holdout":r["holdout"][:-1]})


if __name__=="__main__":
    unittest.main()
