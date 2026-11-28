import copy
import itertools
import json
import unittest
from mathos.research.pnp_dual_degree import from_closure,static,verify
from mathos.research.pnp_degree_closure import derive
from mathos.research.pnp_dual_degree_frontier import cases,tetrahedron,run,audit
from mathos.research.pnp_resolution_algebra import lift,verify as verify_lift
from mathos.research.pnp_resolution_refutation import propose
from mathos.research.pnp_inference_complexity import budget


class TestDualDegree(unittest.TestCase):
    def test_exhaustive_two_variables(self):
        pool=[tuple((i+1)*s for i,s in enumerate(signs) if s)
              for signs in itertools.product((-1,0,1),repeat=2)]
        count=0
        for mask in range(1<<len(pool)):
            f=[c for i,c in enumerate(pool) if mask>>i&1]
            p=derive(2,f,budget(),degree=2)
            if p["status"]=="closed_no_refutation":
                h=from_closure(2,f,p,budget())
                self.assertTrue(verify(2,f,json.loads(json.dumps(h)),budget()))
                count+=1
        self.assertGreater(count,0)

    def test_static_gap(self):
        c=next(c for c in cases() if c["id"]=="static_gap")
        n,f=c["n"],c["clauses"]
        h=static(n,f,budget(),degree=2)
        self.assertTrue(verify(n,f,h,budget(),require_dynamic=False))
        with self.assertRaises(ValueError):
            verify(n,f,{**h,"scope":"dynamic"},budget())
        self.assertEqual(derive(n,f,budget(),degree=2)["status"],"refuted")

    def test_dual_tampering(self):
        f=[(1,2)]
        p=derive(2,f,budget(),degree=2)
        h=from_closure(2,f,p,budget())
        for key,value in (("functionals",[]),("functionals",[1]),("input_sha256","wrong")):
            with self.assertRaises(ValueError):
                verify(2,f,{**h,key:value},budget())
        with self.assertRaises(ValueError):
            verify(2,f,{**h,"scope":"static"},budget())

    def test_simulation(self):
        for n,f in ((0,[()]),(3,[(1,),(-1,2),(-2,3),(-3,)]),
                    (6,tetrahedron(True)["clauses"])):
            p=propose(n,f,budget(),width=8)
            r=lift(n,f,p,budget())
            self.assertTrue(verify_lift(n,f,json.loads(json.dumps(r)),budget()))
            q=copy.deepcopy(r)
            q["width"]+=1
            with self.assertRaises(ValueError):
                verify_lift(n,f,q,budget())

    def test_pipeline(self):
        r=run()
        self.assertEqual(r["completion"],"completed",r.get("reason"))
        self.assertTrue(audit(json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["cases"],23)
        self.assertEqual(r["summary"]["resolution_simulations"],4)
        self.assertEqual(r["summary"]["cross_model_separations"],1)
        self.assertEqual(r["summary"]["static_gap_controls"],1)
        with self.assertRaises(ValueError):
            audit({**r,"rows":r["rows"][:-1]})
        with self.assertRaises(ValueError):
            audit({**r,"p_not_equals_np_established":True})


if __name__=="__main__":
    unittest.main()
