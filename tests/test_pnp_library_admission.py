import unittest
from mathos.research.pnp_library_admission import fragments, verify_fragment, admit
from mathos.research.pnp_schema_portfolio import solve
from mathos.research.pnp_proof_library import Index, reuse
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_library_ablation import independent_replay


class TestAdmission(unittest.TestCase):
    def test_prefix_and_forgery(self):
        f=[(1,),(-1,2),(-2,)]
        proof=[(1,),(2,),()]
        records=fragments(2,f,proof,Budget())
        self.assertTrue(records)
        for record in records:
            self.assertTrue(verify_fragment(2,f,proof,record,Budget()))
            with self.assertRaises(ValueError):
                verify_fragment(2,f,proof,{**record,"embedding":(0,)*len(record["embedding"])},Budget())
        with self.assertRaises(ValueError):
            fragments(2,[(1,2)],[()],Budget())

    def test_offline_reuse(self):
        f=[(3,),(-3,1,2),(-3,1,-2),(-3,-1,2),(-3,-1,-2)]
        source={"id":"training","n":3,"clauses":f}
        r=solve(3,f,Index([]),Budget())
        self.assertEqual(r["status"],"verified")
        base=()
        lib,records=admit(base,[{"case":source,"result":r}],Budget(seconds=30,max_steps=5_000_000))
        self.assertTrue(records)
        self.assertEqual(base,())
        # Signed and permuted source with an extra irrelevant clause.
        target=[(-4,), (4,-2,3),(4,-2,-3),(4,2,3),(4,2,-3),(1,)]
        result=reuse(4,target,Index(lib),Budget(),shared_replay=True)
        self.assertEqual(result["status"],"verified")
        self.assertTrue(independent_replay(4,target,result["proof"]))
        forged={**r,"proof":[()]}
        with self.assertRaises(ValueError):
            admit(base,[{"case":source,"result":forged}],Budget())


if __name__=="__main__":
    unittest.main()
