import unittest
from mathos.research.pnp_library_failure_cones import discover,source_cones,matched_snapshots
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_proof_library import Index,reuse
from mathos.research.pnp_library_ablation import independent_replay

class TestFailureCones(unittest.TestCase):
    def test_checked_source_and_forgery(self):
        c={"n":2,"clauses":[[1,2],[1,-2],[-1,2],[-1,-2]]}
        r=discover(c,Budget())
        self.assertEqual(r["status"],"verified")
        self.assertTrue(source_cones(c,r,Budget()))
        broken={**r,"compressed":{**r["compressed"],"source_embedding":(1,1)}}
        with self.assertRaises(ValueError):
            source_cones(c,broken,Budget())
        self.assertEqual(discover({"n":2,"clauses":[[1,2]]},Budget())["status"],"not_found")
        self.assertEqual(discover(c,Budget(max_steps=1))["status"],"resource_exhausted")

    def test_matched_cohorts_and_transfer(self):
        c={"n":2,"clauses":[[1,2],[1,-2],[-1,2],[-1,-2]]}
        r=discover(c,Budget())
        rows=[{"case":c,"baseline":{"status":status},"resolution":r}
              for status in ("verified","not_found")]
        libs,pools,k=matched_snapshots((),rows,Budget())
        self.assertGreater(k,0)
        self.assertEqual(len(libs["failure"]),len(libs["success"]))
        self.assertEqual(libs["base"],())
        self.assertEqual(libs["failure"],libs["success"])
        for name in ("failure","success"):
            result=reuse(2,c["clauses"],Index(libs[name]),Budget())
            self.assertEqual(result["status"],"verified")
            independent_replay(2,c["clauses"],result["proof"])
        libs,_,k=matched_snapshots((),rows[:1],Budget())
        self.assertEqual(k,0)
        self.assertEqual(libs["failure"],())

if __name__=="__main__":
    unittest.main()
