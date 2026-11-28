import copy
import itertools
import json
import unittest

from mathos.research.pnp_symbolic_parity import synthesize,verify,decide,verify_decision,parity
from mathos.research.pnp_symbolic_frontier import run,audit,cases,charges
from mathos.research.pnp_inference_complexity import budget
from mathos.research.pnp_structural_kernel import Budget,Exhausted
from mathos.research.pnp_proof_simulation_frontier import run as simulation
from mathos.research.pnp_barrier_frontier import run as barriers
from mathos.research.pnp_hypothesis_obligations import run as hypotheses
from mathos.research.pnp_conjecture_frontier import run as refinement


class TestSymbolicParity(unittest.TestCase):
    def test_exhaustive_small_matrices(self):
        for rows in itertools.product(range(8),repeat=3):
            c=synthesize(3,rows,budget())
            verify(3,rows,c,budget())
            image={sum(parity(a&x)<<i for i,a in enumerate(rows)) for x in range(8)}
            self.assertEqual(len(image),1<<c["rank"])
            self.assertEqual(len(c["checks"]),3-c["rank"])
            for b in range(8):
                p=decide(3,rows,c,b,budget())
                self.assertEqual(p["decision"]=="sat",b in image)
                self.assertTrue(verify_decision(3,rows,b,p,budget()))

    def test_isolated_checks(self):
        # The first three rows sum to zero; fourth adds an independent
        # equation. The global all-row XOR test is not a dependency.
        rows=[3,6,5,7]
        c=synthesize(3,rows,budget())
        self.assertEqual(c["rank"],3)
        self.assertEqual(c["checks"],[7])
        self.assertTrue(verify(3,rows,json.loads(json.dumps(c)),budget()))
        for case in cases():
            n,a=case["n"],case["rows"]
            c=synthesize(n,a,budget())
            self.assertTrue(verify(n,a,c,budget()))
            for j,item in enumerate(c["refinements"]):
                self.assertEqual([parity(h&item["charge"]) for h in c["checks"]],
                                 [int(i==j) for i in range(len(c["checks"]))])
                p=decide(n,a,c,item["charge"],budget())
                self.assertEqual(p["decision"],"unsat")
                self.assertTrue(verify_decision(n,a,item["charge"],p,budget()))

    def test_tampering_and_exhaustion(self):
        rows=[3,6,5,7]
        c=synthesize(3,rows,budget())
        for key,value in (("rank",2),("checks",[15]),("operations",[["xor",0,0]]),
                          ("echelon",[1,2,4,0])):
            q=copy.deepcopy(c)
            q[key]=value
            if q==c:
                continue
            with self.assertRaises(ValueError):
                verify(3,rows,q,budget())
        q=copy.deepcopy(c)
        q["refinements"][0]["charge"]=0
        with self.assertRaises(ValueError):
            verify(3,rows,q,budget())
        with self.assertRaises(ValueError):
            verify_decision(3,rows,1,{"decision":"unsat","dependency":15},budget())
        with self.assertRaises(Exhausted):
            synthesize(3,rows,Budget(max_steps=1))

    def test_pipeline(self):
        s,b=simulation(),barriers()
        h=hypotheses(s,b)
        t=refinement(s,b,h)
        r=run(s,b,h,t)
        self.assertEqual(r["completion"],"completed",r.get("reason"))
        self.assertTrue(audit(s,b,h,t,json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["systems"],16)
        self.assertEqual(r["summary"]["rhs_controls"],128)
        self.assertEqual(r["summary"]["universal_obligations_closed"],0)
        with self.assertRaises(ValueError):
            audit(s,b,h,t,{**r,"records":r["records"][:-1]})
        with self.assertRaises(ValueError):
            audit(s,b,h,t,{**r,"p_equals_np_established":True})


if __name__=="__main__":
    unittest.main()
