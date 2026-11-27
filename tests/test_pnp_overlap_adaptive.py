import unittest
from itertools import product
from copy import deepcopy
from mathos.research.pnp_overlap_boundary import project, minimum_rank_forms
from mathos.research.pnp_overlap_adaptive import solve_adaptive, check_adaptive, chain_instance, evidence
from mathos.research.pnp_overlap_certificates import contradiction_demo

class AdaptiveTests(unittest.TestCase):
    def test_exhaustive(self):
        for ds in ([(10,15),(15,10)],[(15,15),(10,15)],[(0,15),(10,15)]):
            for rows in product([(m,b) for m in range(16) for b in (0,1)],repeat=2):
                expected=any(all(((u|(v<<2))&m).bit_count()%2==b for m,b in rows)
                             for u,v in product(project(*ds[0]),project(*ds[1])))
                cert=solve_adaptive(ds,rows)
                self.assertEqual(cert["kind"]=="sat",expected)
                self.assertTrue(check_adaptive(ds,rows,cert))

    def test_chain_optimum_small(self):
        for k in range(2,9):
            ds,rows=chain_instance(k)
            opt=minimum_rank_forms(2*k,rows,[(1<<(2*i),2<<(2*i),3<<(2*i)) for i in range(k)])
            self.assertEqual(opt["d"],(k-1)//2)
            stats={}
            cert=solve_adaptive(ds,rows,stats=stats)
            self.assertEqual((cert["kind"],stats["nodes"],stats["splits"]),("unsat",1,0))
            self.assertTrue(check_adaptive(ds,rows,cert))

    def test_large_chain_and_mutations(self):
        ds,rows=chain_instance(43)
        r=evidence()
        self.assertEqual((r["static_rank_analytic"],r["static_full_leaf_count_analytic"]), (21,2097152))
        self.assertEqual((r["adaptive_nodes"],r["adaptive_splits"]),(1,0))
        cert=r["certificate"]
        for mutate in (lambda c:c["tree"][0]["trace"].pop(0),
                       lambda c:c["tree"][0]["trace"].append(999),
                       lambda c:c["tree"].append(deepcopy(c["tree"][0])),
                       lambda c:c["tree"][0].update(index=999)):
            bad=deepcopy(cert)
            mutate(bad)
            self.assertFalse(check_adaptive(ds,rows,bad))

    def test_branch_coverage(self):
        ds,rows=contradiction_demo()
        cert=solve_adaptive(ds,rows)
        self.assertEqual(cert["kind"],"unsat")
        self.assertEqual(cert["tree"][0]["kind"],"split")
        self.assertTrue(check_adaptive(ds,rows,cert))
        for mutate in (lambda c:c["tree"].pop(),
                       lambda c:c["tree"][0].update(form=0),
                       lambda c:c["tree"].append(deepcopy(c["tree"][-1]))):
            bad=deepcopy(cert)
            mutate(bad)
            self.assertFalse(check_adaptive(ds,rows,bad))

    def test_early_and_malformed(self):
        for ds,rows in (([],[]),([],[(0,1)]),([(0,15)],[])):
            cert=solve_adaptive(ds,rows)
            self.assertTrue(check_adaptive(ds,rows,cert))
            self.assertFalse(check_adaptive(ds,rows,{}))
        self.assertFalse(check_adaptive([],[(0,1)],{"kind":"unsat","tree":[{"kind":"dual","trace":[],"dual":[]}]}))
