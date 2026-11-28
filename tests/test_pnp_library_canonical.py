import random
import unittest
from mathos.research.pnp_library_canonical import canonical,compact,witness,verify_equivalence
from mathos.research.pnp_proof_library import mapped
from mathos.research.pnp_structural_kernel import Budget

def renamed(f,e):
    return {"n":f["n"],"axioms":tuple(sorted(mapped(c,e) for c in f["axioms"])),
            "steps":tuple(mapped(c,e) for c in f["steps"]),"edges":()}

class TestCanonical(unittest.TestCase):
    def test_signed_orbits(self):
        rng=random.Random(171171)
        for n in (2,3,5,7,9):
            f={"n":n,"axioms":tuple((-i,i+1) for i in range(1,n)),
               "steps":((1,n),),"edges":()}
            a=canonical(f,Budget())
            self.assertEqual(a["status"],"exact")
            for _ in range(8):
                e=list(range(1,n+1))
                rng.shuffle(e)
                e=[x*rng.choice((-1,1)) for x in e]
                g=renamed(f,e)
                b=canonical(g,Budget())
                self.assertEqual(a["key"],b["key"])
                self.assertTrue(verify_equivalence(f,g,witness(a["embedding"],b["embedding"]),Budget()))

    def test_cap_and_distinct_goal(self):
        f={"n":5,"axioms":tuple((i,) for i in range(1,6)),
           "steps":((),),"edges":()}
        self.assertEqual(canonical(f,Budget(),cap=10)["status"],"unknown")
        g={"n":2,"axioms":((1,2),(-1,2)),"steps":((2,),),"edges":()}
        h={**g,"steps":((1,),)}
        self.assertNotEqual(canonical(g,Budget())["key"],canonical(h,Budget())["key"])
        with self.assertRaises(ValueError):
            verify_equivalence(g,h,(1,2),Budget())

    def test_compaction_and_unknown(self):
        f={"n":2,"axioms":((-1,2),(1,2)),"steps":((2,),),"edges":()}
        g=renamed(f,(-2,1))
        out,d=compact((f,g),Budget())
        self.assertEqual(out,(f,))
        self.assertEqual(d[1]["status"],"duplicate")
        self.assertTrue(verify_equivalence(g,f,d[1]["embedding"],Budget()))
        # Symmetric, valid tautology-free guard/conclusion with a tiny cap.
        h={"n":3,"axioms":((1,2,3),),"steps":((1,2,3),),"edges":()}
        out,d=compact((h,h),Budget(),cap=1)
        self.assertEqual(len(out),2)
        self.assertEqual(d[0]["canonical"],"unknown")
        with self.assertRaises(ValueError):
            compact((f,{**f,"steps":((1,),)}),Budget())

if __name__=="__main__":
    unittest.main()
