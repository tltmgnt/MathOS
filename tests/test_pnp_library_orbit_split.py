import unittest
from mathos.research.pnp_library_orbit_split import Registry,select
from mathos.research.pnp_structural_kernel import Budget

def case(n,f,family="random2"):
    return {"n":n,"clauses":f,"family":family}

class TestOrbitSplit(unittest.TestCase):
    def test_signed_relabel_and_unused(self):
        r=Registry()
        a=case(2,[(1,2),(-1,2)])
        b=case(7,[(3,-5),(-3,-5),(3,-5),(7,-7)])
        self.assertEqual(r.register(a,Budget(),prior=True),"accepted")
        self.assertEqual(r.register(b,Budget()),"orbit_duplicate")
        self.assertEqual(r.register(case(2,[(1,2),(-1,-2)]),Budget()),"accepted")

    def test_unknown_quarantine_and_support(self):
        r=Registry(cap=1,max_active=5)
        a=case(4,[(1,),(2,),(3,),(4,)])
        self.assertEqual(r.register(a,Budget(),prior=True),"unresolved")
        self.assertEqual(r.register(case(4,[(-1,),(2,),(3,),(-4,)]),Budget()),"unresolved")
        self.assertEqual(r.register(case(6,[tuple(range(1,7))]),Budget()),"outside_support")
        self.assertEqual(len(r.exact),0)

    def test_sampling_failure(self):
        r=Registry()
        with self.assertRaises(ValueError):
            select(r,[case(1,[(1,)])],Budget(),per_family=1)

if __name__=="__main__":
    unittest.main()
