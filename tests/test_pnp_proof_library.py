import copy
import random
import unittest

from mathos.research.pnp_proof_abstraction import compress
from mathos.research.pnp_resolution_refutation import propose
from mathos.research.pnp_structural_kernel import Budget, brute, Exhausted
from mathos.research.pnp_proof_library import (
    Index, build, fragments, canonical_structure, mapped, find, refine,
    reconstruct, reuse, verify_certificate)


def template(n,f):
    return compress(n,f,propose(n,f,Budget(),width=8),Budget())["template"]


class TestProofLibrary(unittest.TestCase):
    def test_signed_subsumption_and_adversarial(self):
        t=template(3,[(1,2),(-1,3),(-2,),(-3,)])
        lib,_=build([t],Budget())
        index=Index(lib)
        f=[(-1,), (1,-3), (3,), (2,)]
        r=reuse(3,f,index,Budget())
        self.assertEqual(r["status"],"verified")
        self.assertEqual(reconstruct(3,f,index,r["transfers"],Budget()),r["proof"])
        i,e=r["transfers"][0]
        with self.assertRaises(ValueError):
            reconstruct(3,f,index,[(i,[1]*len(e))],Budget())
        with self.assertRaises(ValueError):
            verify_certificate(2,[(1,2)],[()],Budget())
        with self.assertRaises(ValueError):
            verify_certificate(2,[(1,)],[(-1,)],Budget())
        with self.assertRaises(ValueError):
            reconstruct(3,[(1,2,3)],index,r["transfers"],Budget())

    def test_canonical_signed_orbit(self):
        t=template(3,[(1,),(-1,2),(-2,3),(-3,)])
        f=list(fragments(t,Budget()))[-1]
        e=(-3,1,-2)
        g={**f,"axioms":tuple(mapped(c,e) for c in reversed(f["axioms"])),
           "steps":tuple(mapped(c,e) for c in f["steps"]),
           "edges":tuple((mapped(b,e),mapped(a,e),mapped(c,e),abs(e[v-1]))
                         for a,b,c,v in reversed(f["edges"]))}
        self.assertEqual(canonical_structure(f,Budget()),canonical_structure(g,Budget()))

    def test_composition(self):
        # Independently checked fragments, then a contradiction fragment.
        a={"n":3,"axioms":((1,),(-1,2),(-2,3)),"steps":((2,),(3,)),"edges":()}
        b={"n":2,"axioms":((1,),(-1,2),(-2,)),"steps":((2,),()),"edges":()}
        for x in (a,b):
            verify_certificate(x["n"],x["axioms"],x["steps"],Budget(),contradiction=False)
        f=[(1,),(-1,2),(-2,3),(-3,4),(-4,)]
        index=Index([a,b])
        r=reuse(4,f,index,Budget(),rounds=5)
        self.assertEqual(r["status"],"verified")
        self.assertGreater(len(r["transfers"]),1)
        self.assertEqual(reconstruct(4,f,index,r["transfers"],Budget()),r["proof"])

    def test_refinement_witnesses(self):
        f=list(fragments(template(2,[(1,),(-1,2),(-2,)]),Budget()))[-1]
        g,evidence=refine(f,Budget())
        self.assertEqual(g["axioms"],f["axioms"])
        for row in evidence:
            self.assertEqual(row["status"],"counterexample")
            self.assertTrue(all(set(row["model"]).intersection(c) for c in row["candidate_axioms"]))
            self.assertFalse(set(row["model"]).intersection(f["steps"][-1]))

    def test_random_soundness(self):
        rng=random.Random(1717)
        lib,_=build([template(3,[(1,),(-1,2),(-2,3),(-3,)])],Budget())
        index=Index(lib)
        for _ in range(80):
            f=[tuple(v if rng.randrange(2) else -v for v in rng.sample(range(1,5),rng.randint(1,3)))
               for _ in range(10)]
            r=reuse(4,f,index,Budget())
            if r["status"]=="verified":
                self.assertFalse(brute(4,f,Budget()))
                self.assertEqual(reconstruct(4,f,index,r["transfers"],Budget()),r["proof"])
        self.assertNotEqual(reuse(4,[(1,2,3,4)],index,Budget(max_steps=1))["status"],"verified")

    def test_invalid_certificate(self):
        for addition in [(True,), (0,), (3,), (1,-1), (1,1)]:
            with self.assertRaises(ValueError):
                verify_certificate(2,[(1,)],[addition],Budget(),contradiction=False)
        with self.assertRaises(Exhausted):
            verify_certificate(2,[(1,),(-1,)],[()],Budget(max_steps=1))


if __name__=="__main__":
    unittest.main()
