import unittest
from itertools import product
from copy import deepcopy
from mathos.research.pnp_overlap_boundary import project
from mathos.research.pnp_overlap_recovery import recover, solve_recovered, check_recovered, hierarchy_instance, evidence

class RecoveryTests(unittest.TestCase):
    def test_exhaustive_decisions(self):
        for ds in ([(10,15),(15,10)],[(15,15),(10,15)],[(0,15),(10,15)]):
            for rs in product([(m,b) for m in range(16) for b in (0,1)],repeat=2):
                expected=any(all(((u|(v<<2))&m).bit_count()%2==b for m,b in rs)
                             for u,v in product(project(*ds[0]),project(*ds[1])))
                cert=solve_recovered(ds,rs,2)
                self.assertEqual(cert["kind"]=="sat",expected)
                self.assertTrue(check_recovered(ds,rs,cert))

    def test_exact_small_consequences(self):
        ds=[(10,15),(15,10)]
        for rs in product([(m,b) for m in range(16) for b in (0,1)],repeat=2):
            original={u|(v<<2) for u,v in product(project(*ds[0]),project(*ds[1]))
                      if all(((u|(v<<2))&m).bit_count()%2==b for m,b in rs)}
            current,trace,empty=recover(ds,rs,2)
            self.assertTrue(all(all((x&m).bit_count()%2==b for m,b in current) for x in original))
            if empty is not None:
                self.assertFalse(original)

    def test_hierarchy(self):
        for r in (1,2,3):
            ds,rs=hierarchy_instance(r)
            current,trace,empty=recover(ds,rs,r)
            self.assertEqual((current,trace,empty),(rs,[],None))
            cert=solve_recovered(ds,rs,r+1)
            self.assertEqual(cert["kind"],"local_unsat")
            self.assertTrue(cert["trace"])
            self.assertTrue(check_recovered(ds,rs,cert))

    def test_pair_affine_recovery(self):
        # Same outputs, opposite implications force equality.
        ds=[(10,15),(15,10)]
        rs=[(5,0),(10,0)]
        self.assertEqual(recover(ds,rs,1),(rs,[],None))
        current,trace,empty=recover(ds,rs,2)
        self.assertIsNone(empty)
        self.assertTrue(trace)
        self.assertTrue(all(any(m==x and b==0 for m,b in current) for x in (3,) )
                        or any(m==12 and b==0 for m,b in current)
                        or all((x&3)==0 or (x&3)==3 for x in range(16)
                               if all((x&m).bit_count()%2==b for m,b in current)))
        self.assertTrue(check_recovered(ds,rs,solve_recovered(ds,rs,2)))

    def test_mutations(self):
        ds,rs=hierarchy_instance(2)
        cert=solve_recovered(ds,rs,3)
        for mutate in (lambda c:c.update(order=1),
                       lambda c:c["trace"][0]["row"].__setitem__(1,1-c["trace"][0]["row"][1]),
                       lambda c:c["trace"][0]["row"].__setitem__(0,0),
                       lambda c:c["trace"][0]["components"].append(999),
                       lambda c:c.update(components=[]),
                       lambda c:c.update(trace=[])):
            bad=deepcopy(cert)
            mutate(bad)
            self.assertFalse(check_recovered(ds,rs,bad))
        self.assertFalse(check_recovered(ds,[],cert))

    def test_degenerate_and_fallback(self):
        for ds,rs in (([],[]),([],[(0,1)]),([(0,15)],[])):
            self.assertTrue(check_recovered(ds,rs,solve_recovered(ds,rs)))
        ds,rs=hierarchy_instance(1)
        cert=solve_recovered(ds,rs,1)
        self.assertEqual(cert["kind"],"derived_unsat")
        self.assertTrue(check_recovered(ds,rs,cert))
        with self.assertRaises(ValueError):
            recover(ds,rs,0)

    def test_evidence(self):
        self.assertEqual(len(evidence()["cases"]),3)
