import itertools
import json
import random
import tempfile
from pathlib import Path
import unittest

from mathos.research.pnp_structural_kernel import Budget, brute, truth
from mathos.research.pnp_triple_parity import block, propose, verify, signed_family
from mathos.research.pnp_asymptotic_frontier import run, probe


class TestTripleParity(unittest.TestCase):
    def test_all_local_blocks_and_assignments(self):
        for bits in itertools.product((False, True), repeat=3):
            f = block((1,2,3), bits)
            a = propose(3, f, Budget())
            self.assertTrue(verify(3, f, a, Budget()))
            for values in itertools.product((False, True), repeat=3):
                self.assertEqual(truth(f, values), truth(a["binary_clauses"], values))
                self.assertEqual(truth(f, values),
                                 values == bits or values == tuple(not b for b in bits))

    def test_overlapping_random_blocks(self):
        rng = random.Random(601)
        for _ in range(150):
            n = rng.randint(3, 8)
            keys = list(itertools.combinations(range(1,n+1),3))
            f = []
            for key in rng.sample(keys, rng.randint(1, min(8,len(keys)))):
                f.extend(block(key, tuple(bool(rng.randrange(2)) for _ in key)))
            a = propose(n, f, Budget())
            self.assertTrue(verify(n, f, json.loads(json.dumps(a)), Budget()))
            self.assertEqual(a["decision_certificate"]["kind"] == "sat_witness", brute(n, f, Budget()))

    def test_out_of_scope_and_tampering(self):
        f = block((1,2,3), (True,False,False))
        self.assertIsNone(propose(3, f[:-1], Budget()))
        self.assertIsNone(propose(3, f+[[1]], Budget()))
        noncomplementary = [tuple(-i if x else i for i,x in enumerate(bits,1))
                            for bits in itertools.product((False,True),repeat=3)
                            if bits not in ((False,False,False),(False,False,True))]
        self.assertIsNone(propose(3, noncomplementary, Budget()))
        a = propose(3, f, Budget())
        for forged in ({**a,"blocks":[]}, {**a,"binary_clauses":[]},
                       {**a,"blocks":[{"variables":[1,2,3],"parities":[False,False]}]},
                       {**a,"clauses":[[]]}):
            with self.assertRaises(ValueError):
                verify(3,f,forged,Budget())

    def test_family_and_v5_gap(self):
        for n in (4,6,8,16):
            reports = probe(n,1,Budget(seconds=30,max_steps=20_000_000))
            self.assertEqual([r["sat"] for r in reports],[True,False])
            self.assertEqual(reports[0]["v5_routes"],[])
            for r in reports:
                self.assertEqual(r["exact_treewidth"],n-1)
                self.assertEqual(r["constant_output_width"],0)
                self.assertTrue(r["v6_certificate_replayed"])
            self.assertLessEqual(reports[0]["binary_clauses"], n*(n-1))

    def test_checkpoint_and_governance(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"report.json"
            r = run(Budget(seconds=30,max_steps=20_000_000),sizes=(4,8),
                    target={"n":3,"clauses":block((1,2,3),(False,True,False))},
                    checkpoint_path=path)
            self.assertEqual(r["completion"],"scoped_family_research_completed")
            self.assertEqual(r["target_result"]["status"],"certificate_replayed")
            self.assertEqual(json.loads(path.read_text())["universal_obligation"],"unresolved")
            self.assertFalse(r["p_equals_np_established"])
            self.assertFalse(r["p_not_equals_np_established"])
            self.assertEqual(r["formal_verification"],"not_performed")
            exhausted = run(Budget(max_steps=1),sizes=(4,),checkpoint_path=path)
            self.assertEqual(exhausted["completion"],"resource_exhausted")


if __name__ == "__main__":
    unittest.main()
