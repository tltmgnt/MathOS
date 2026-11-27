import unittest
from copy import deepcopy
from itertools import product
from mathos.research.pnp_overlap_boundary import project, parity_gap_instance
from mathos.research.pnp_overlap_certificates import certify, check, contradiction_demo, evidence

class Certificates(unittest.TestCase):
    def test_exhaustive(self):
        for ds in ([(10,15),(15,10)],[(15,15),(10,15)],[(0,15),(10,15)]):
            for rows in product([(m,b) for m in range(16) for b in range(2)],repeat=2):
                expected=any(all(((u|(v<<2))&m).bit_count()%2==b for m,b in rows)
                             for u,v in product(project(*ds[0]),project(*ds[1])))
                cert=certify(ds,rows)
                self.assertTrue(check(ds,rows,cert))
                self.assertEqual(cert["kind"]=="sat",expected)

    def test_complete_unsat(self):
        ds,rows=contradiction_demo()
        cert=certify(ds,rows)
        self.assertEqual((cert["kind"],cert["d"],len(cert["leaves"])),("ranked_unsat",1,2))
        self.assertTrue(check(ds,rows,cert))
        for mutate in (
            lambda c:c["leaves"].pop(),
            lambda c:c["leaves"].append(deepcopy(c["leaves"][0])),
            lambda c:c["leaves"].reverse(),
            lambda c:c["leaves"][0].update(dual=[]),
            lambda c:c["leaves"][0]["dual"].append(c["leaves"][0]["dual"][0]),
            lambda c:c["leaves"][0].update(rep=1<<8),
            lambda c:c.update(d=0),
            lambda c:c.update(lower=[]),
            lambda c:c["lower"].append(0),
            lambda c:c.update(forms=[0]*4),
            lambda c:c.update(basis=[0]),
        ):
            bad=deepcopy(cert)
            mutate(bad)
            self.assertFalse(check(ds,rows,bad))
        self.assertFalse(check(ds,rows[:-1],cert))

    def test_sat_and_zero_rank(self):
        ds,rows=parity_gap_instance(21)
        cert=certify(ds,rows)
        self.assertEqual((cert["kind"],cert["d"],len(cert["lower"])),("sat",1,1))
        self.assertTrue(check(ds,rows,cert))
        cert["witness"][0]=[0,2,0]
        self.assertFalse(check(ds,rows,cert))
        cert=certify([(10,15)],[(1,0)])
        self.assertEqual(cert["d"],0)
        self.assertTrue(check([(10,15)],[(1,0)],cert))
        self.assertTrue(check([],[],certify([],[])))

    def test_deeper_lower_tree(self):
        ds=[(10,15)]*3
        cert=certify(ds,[])
        self.assertEqual(cert["d"],3)
        self.assertEqual(len(cert["lower"]),13)
        self.assertTrue(check(ds,[],cert))
        bad=deepcopy(cert)
        bad["lower"][1]=bad["lower"][0]
        self.assertFalse(check(ds,[],bad))
        bad=deepcopy(cert)
        bad["lower"].pop()
        self.assertFalse(check(ds,[],bad))

    def test_early_unsat_and_malformed(self):
        for ds,rows,kind in (([(0,15)],[],"empty"),([],[(0,1)],"affine_unsat")):
            cert=certify(ds,rows)
            self.assertEqual(cert["kind"],kind)
            self.assertTrue(check(ds,rows,cert))
            self.assertFalse(check(ds,rows,{}))
        self.assertFalse(check([],[(0,1)],{"kind":"affine_unsat","dual":[0,0,0]}))
        self.assertFalse(check([(16,1)],[],{"kind":"empty","index":0}))
        self.assertFalse(check([],[(1,1)],{"kind":"affine_unsat","dual":[0]}))

    def test_evidence(self):
        self.assertTrue(all(c["checker_accepted"] for c in evidence()["cases"].values()))
