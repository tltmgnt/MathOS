import copy
import itertools
import json
import random
import unittest
from mathos.research.pnp_proof_simulation import pad,restrict,project,lift_padding,simulation,verify_simulation,verify_padding,actual_width
from mathos.research.pnp_resolution_refutation import propose,verify
from mathos.research.pnp_proof_simulation_frontier import run,audit,budget
from mathos.research.pnp_inference_obstructions import chain,balanced_proof
from mathos.research.pnp_structural_kernel import brute


class TestSimulation(unittest.TestCase):
    def test_padding_and_sparse_labels(self):
        for n,f in ((0,[()]),(8,[(2,),(-2,7),(-7,),(5,8)]),(3,chain(3))):
            p=propose(n,f,budget(),width=8)
            self.assertIsNotNone(p)
            r=simulation(n,f,p,budget())
            self.assertTrue(verify_simulation(n,f,json.loads(json.dumps(r)),budget()))
            z,g=pad(n,f)
            self.assertTrue(verify_padding(n,f,g,budget()))
            with self.assertRaises(ValueError):
                verify_padding(n,f,g[:-1],budget())

    def test_general_restrictions(self):
        rng=random.Random(24024)
        checked=0
        for _ in range(100):
            n=rng.randint(2,6)
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,n+1),rng.randint(1,min(3,n))))
               for _ in range(5*n)]
            p=propose(n,f,budget(),width=8)
            if p is None:
                continue
            checked+=1
            for _ in range(4):
                fixed=[(v,bool(rng.randrange(2))) for v in rng.sample(range(1,n+1),rng.randrange(n+1))]
                g,q=project(n,f,p,fixed,budget())
                self.assertTrue(verify(n,g,json.loads(json.dumps(q)),budget()))
                self.assertLessEqual(len(q["steps"]),len(p["steps"]))
                self.assertLessEqual(actual_width(q),actual_width(p))
                self.assertFalse(brute(n,g,budget()))
        self.assertGreater(checked,0)

    def test_tampering(self):
        n=3
        f=chain(n)
        r=simulation(n,f,balanced_proof(n,budget()),budget())
        x=copy.deepcopy(r)
        x["lifted"]["steps"][0]["pivot"]=999
        with self.assertRaises(ValueError):
            verify_simulation(n,f,x,budget())
        with self.assertRaises(ValueError):
            verify_simulation(n,f,{**r,"projections":r["projections"][:-1]},budget())
        with self.assertRaises(ValueError):
            project(n,f,r["source_proof"],[(1,True),(1,False)],budget())

    def test_pipeline(self):
        r=run()
        self.assertEqual(r["completion"],"completed",r.get("reason"))
        self.assertTrue(audit(json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["simulation_controls"],6)
        self.assertEqual(r["summary"]["restriction_branches"],12)
        self.assertEqual(r["summary"]["parity_escapes"],10)
        with self.assertRaises(ValueError):
            audit({**r,"escapes":r["escapes"][:-1]})
        x=copy.deepcopy(r)
        x["escapes"][0]["constant_cnf"]=[]
        with self.assertRaises(ValueError):
            audit(x)


if __name__=="__main__":
    unittest.main()
