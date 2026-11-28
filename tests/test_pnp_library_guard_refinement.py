import unittest
from mathos.research.pnp_library_guard_refinement import refine_template,repair,refine_library
from mathos.research.pnp_structural_kernel import Budget
from mathos.research.pnp_library_ablation import independent_replay

class TestGuardRefinement(unittest.TestCase):
    def test_semantic_deletion_repair(self):
        f={"n":3,"axioms":((1,),(-1,2),(2,),(3,)),"steps":((1,),(2,)),"edges":()}
        a,ta,ma=refine_template(f,Budget(),allow_repair=False)
        b,tb,mb=refine_template(f,Budget(),allow_repair=True)
        self.assertFalse(ma)
        self.assertTrue(mb)
        self.assertIn("replay_blocked",[r["status"] for r in ta])
        self.assertIn("repaired",[r["status"] for r in tb])
        self.assertEqual(b["axioms"],((2,),))
        self.assertLess(len(b["axioms"]),len(a["axioms"]))
        self.assertTrue(independent_replay(3,list(b["axioms"])+[(-2,)],list(b["steps"])+[()]))

    def test_lift_nonunit_conflict(self):
        g=((1,2),(-1,2),(1,-2),(-1,-2))
        p=repair(3,g,(3,),Budget())
        self.assertIsNotNone(p)
        self.assertEqual(p[-1],(3,))
        self.assertTrue(independent_replay(3,list(g)+[(-3,)],list(p)+[()]))
        self.assertIsNone(repair(3,((1,2),),(3,),Budget()))

    def test_counterexample_and_bad_input(self):
        f={"n":2,"axioms":((-1,2),(1,)),"steps":((2,),),"edges":()}
        a,t,m=refine_template(f,Budget(),allow_repair=True)
        self.assertTrue(m)
        self.assertEqual(a["axioms"],f["axioms"])
        for row in t:
            self.assertEqual(row["status"],"counterexample")
            model=set(row["model"])
            self.assertNotIn(2,model)
            self.assertTrue(all(model.intersection(c) for c in f["axioms"] if c!=row["removed"]))
        with self.assertRaises(ValueError):
            refine_template({**f,"steps":((-2,),)},Budget(),allow_repair=True)
        lib,records=refine_library((f,),allow_repair=True)
        self.assertEqual(lib,(f,))
        self.assertTrue(records[0]["deletion_minimal"])

if __name__=="__main__":
    unittest.main()
