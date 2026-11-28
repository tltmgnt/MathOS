import json
import unittest
from mathos.research import pnp_external_satlib as c
from mathos.research.pnp_external_satlib_frontier import ARMS,summary
from mathos.research.pnp_structural_kernel import Budget,Exhausted


def budget():
    return Budget(seconds=5,max_steps=100000,max_cells=200000)


class ExternalTests(unittest.TestCase):
    def test_strict_dimacs(self):
        self.assertEqual(c.parse_dimacs(b"c demo\np cnf 3 3\n1 -2\n3 0 2 0\n0\n%\n0\n"),
                         (3,[[1,-2,3],[2],[]]))
        for data in (b"1 0",b"p cnf 1 1\n2 0",b"p cnf 2 2\n1\n2 0",
                     b"p cnf 1 1\n1",b"p cnf 1 0\np cnf 1 0",
                     b"p cnf 1 1\n%\n0",b"p cnf 1 0\n1 0"):
            with self.assertRaises(ValueError):
                c.parse_dimacs(data)

    def test_drup_and_mutations(self):
        f=[[1,2],[1,-2],[-1,2],[-1,-2]]
        p=["1 0","d 1 2 0","0"]
        self.assertTrue(c.verify_drup(2,f,p,budget()))
        self.assertTrue(c.verify_drup(2,f,["1 0"],budget()))
        for bad in (["0"],["1 0","3 0"],["1"],["1 0 2 0"],["2 0","-2 0"]):
            # The last proof is valid on the full four-clause formula,
            # but not on this satisfiable prefix.
            with self.assertRaises(ValueError):
                c.verify_drup(2,f[:-1],bad,budget())
        with self.assertRaises(Exhausted):
            c.verify_drup(2,f,p,Budget(seconds=5,max_steps=1))

    def test_manifest(self):
        m=c.manifest()
        rows=m["cases"]
        self.assertEqual(len(rows),32)
        self.assertEqual(len({r["path"] for r in rows}),32)
        self.assertEqual(len({r["blob"] for r in rows}),32)
        self.assertEqual(sum(r["expected"]=="sat" for r in rows),16)

    def test_real_glucose(self):
        for f in ([[1,2]],[[1,2],[1,-2],[-1,2],[-1,-2]],[[1],[-1]]):
            r=c.glucose(2,f)
            self.assertEqual(r["decision"],"sat" if len(f)==1 else "unsat")
            self.assertTrue(c.verify_external(2,f,json.loads(json.dumps(r)),budget()))

    def test_summary_rejection(self):
        s=summary([{"case":{"group":"test"},"parse_error":"clause count mismatch","arms":{}}])
        self.assertEqual(s["test"]["selected"],1)
        self.assertEqual(s["test"]["parse_rejected"],1)
        self.assertEqual(set(s["test"]["arms"]),set(ARMS))


if __name__=="__main__":
    unittest.main()
