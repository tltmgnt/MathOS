import unittest
from copy import deepcopy
from itertools import product
from mathos.research.pnp_overlap_boundary import project, minimum_rank_forms
from mathos.research.pnp_overlap_adaptive import reachable, solve_adaptive, check_adaptive
from mathos.research.pnp_overlap_obstructions import (
    solve_factored, check_factored, factors, distraction_instance, connected_instance, evidence)

class Obstructions(unittest.TestCase):
    def test_exhaustive_factor_solver(self):
        for ds in ([(10,15),(15,10)],[(15,15),(10,15)],[(0,15),(10,15)]):
            for rows in product([(m,b) for m in range(16) for b in (0,1)],repeat=2):
                expected=any(all(((u|(v<<2))&m).bit_count()%2==b for m,b in rows)
                             for u,v in product(project(*ds[0]),project(*ds[1])))
                cert=solve_factored(ds,rows)
                self.assertEqual(cert["kind"]=="sat",expected)
                self.assertTrue(check_factored(ds,rows,cert))

    def test_order_obstruction(self):
        for k in range(5):
            ds,rows=distraction_instance(k)
            stats={}
            cert=solve_adaptive(ds,rows,stats=stats)
            self.assertEqual((stats["nodes"],stats["splits"],stats["root_rank"]),
                             ((1<<(k+2))-1,(1<<(k+1))-1,k+1))
            self.assertTrue(check_adaptive(ds,rows,cert))
            fac={}
            cert=solve_factored(ds,rows,stats=fac)
            self.assertEqual((fac["factors"],fac["nodes"],fac["splits"]),(k+1,2*k+3,k+1))
            self.assertEqual(cert["components"],list(range(k,k+4)))
            self.assertTrue(check_factored(ds,rows,cert))

    def test_connected_irreducible_rank(self):
        for k in range(2,8):
            ds,rows=connected_instance(k)
            self.assertEqual(factors(k,rows),[list(range(k))])
            self.assertTrue(all(len(reachable(2*k,rows,i,project(*d)))==3
                                for i,d in enumerate(ds)))
            opt=minimum_rank_forms(2*k,rows,[(1<<(2*i),2<<(2*i),3<<(2*i)) for i in range(k)])
            self.assertEqual(opt["d"],k-1)
        ds,rows=connected_instance(21)
        self.assertTrue(all(len(reachable(42,rows,i,project(*d)))==3 for i,d in enumerate(ds)))

    def test_independent_rank(self):
        for k in range(6):
            self.assertEqual(minimum_rank_forms(2*k,[],[(1<<(2*i),2<<(2*i),3<<(2*i))
                                                      for i in range(k)])["d"],k)

    def test_certificate_mutations_and_constants(self):
        ds,rows=distraction_instance(2)
        cert=solve_factored(ds,rows)
        for mutate in (lambda c:c["components"].pop(),lambda c:c["components"].reverse(),
                       lambda c:c["components"].append(99),lambda c:c.update(proof={"kind":"sat","witness":[]}),
                       lambda c:c["proof"]["tree"].pop()):
            bad=deepcopy(cert)
            mutate(bad)
            self.assertFalse(check_factored(ds,rows,bad))
        self.assertFalse(check_factored(ds,[],cert))
        for ds,rows in (([],[]),([],[(0,1)]),([(0,15)],[]),([(10,15)],[(0,0)])):
            self.assertTrue(check_factored(ds,rows,solve_factored(ds,rows)))
        self.assertFalse(check_factored([],[(0,0)],{"kind":"constant_unsat","row":0}))

    def test_evidence(self):
        r=evidence()
        self.assertEqual((r["monolithic"]["nodes"],r["factored"]["nodes"]),(127,13))
        self.assertTrue(r["checker_accepted"])
