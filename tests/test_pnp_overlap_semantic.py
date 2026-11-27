import unittest
from itertools import product
from copy import deepcopy
from mathos.research.pnp_overlap_boundary import project
from mathos.research.pnp_overlap_obstructions import factors
from mathos.research.pnp_overlap_semantic import reduce_rows, indices, row_sum, solve_semantic, check_semantic, hidden_instance, evidence

class SemanticTests(unittest.TestCase):
    def test_rref_and_provenance(self):
        for rs in product([(m,b) for m in range(16) for b in (0,1)],repeat=2):
            reduced,bad=reduce_rows(4,rs)
            models={x for x in range(16) if all((x&m).bit_count()%2==b for m,b in rs)}
            if bad is not None:
                self.assertFalse(models)
                self.assertEqual(row_sum(rs,indices(bad)),(0,1))
            else:
                self.assertEqual(models,{x for x in range(16) if all((x&m).bit_count()%2==b for m,b,w in reduced)})
                self.assertEqual([(m,b) for m,b,w in reduced],[(m,b) for m,b,w in reduce_rows(4,rs[::-1])[0]])
                for m,b,w in reduced:
                    self.assertEqual(row_sum(rs,indices(w)),(m,b))

    def test_exhaustive_solver(self):
        for ds in ([(10,15),(15,10)],[(15,15),(10,15)],[(0,15),(10,15)]):
            for rs in product([(m,b) for m in range(16) for b in (0,1)],repeat=2):
                expected=any(all(((u|(v<<2))&m).bit_count()%2==b for m,b in rs)
                             for u,v in product(project(*ds[0]),project(*ds[1])))
                p=solve_semantic(ds,rs)
                self.assertEqual(p["kind"]=="sat",expected)
                self.assertTrue(check_semantic(ds,rs,p))

    def test_finest_affine_partition(self):
        # Two-block affine relation is a product iff each projected combination occurs.
        for rs in product([(m,b) for m in range(16) for b in (0,1)],repeat=2):
            reduced,bad=reduce_rows(4,rs)
            if bad is not None:
                continue
            models={x for x in range(16) if all((x&m).bit_count()%2==b for m,b in rs)}
            cart={a|b<<2 for a,b in product({x&3 for x in models},{x>>2 for x in models})}
            self.assertEqual(len(factors(2,[(m,b) for m,b,w in reduced]))==2,models==cart)

    def test_hidden_factors(self):
        for k in range(5):
            r=evidence(k)
            self.assertEqual((r["monolithic"]["nodes"],r["semantic"]["nodes"]),((1<<(k+2))-1,2*k+3))
        ds,rs=hidden_instance(21)
        stats={}
        cert=solve_semantic(ds,rs,stats=stats)
        self.assertTrue(check_semantic(ds,rs,cert))
        self.assertEqual((stats["explicit_factors"],stats["canonical_factors"],stats["nodes"]),(1,22,45))

    def test_mutations(self):
        ds,rs=hidden_instance(2)
        cert=solve_semantic(ds,rs)
        for change in (lambda c:c["rows"][0][2].append(c["rows"][0][2][0]),
                       lambda c:c["rows"][0].__setitem__(1,1-c["rows"][0][1]),
                       lambda c:c["rows"][0].__setitem__(0,1),
                       lambda c:c["components"].reverse(),
                       lambda c:c["proof"]["tree"].pop()):
            bad=deepcopy(cert)
            change(bad)
            self.assertFalse(check_semantic(ds,rs,bad))
        self.assertFalse(check_semantic(ds,[],cert))
        self.assertTrue(check_semantic([],[],solve_semantic([],[])))
        self.assertTrue(check_semantic([],[(0,1)],solve_semantic([],[(0,1)])))

    def test_evidence(self):
        r=evidence()
        self.assertEqual((r["monolithic"]["nodes"],r["semantic"]["nodes"]),(127,13))
