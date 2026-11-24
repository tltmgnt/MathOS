import unittest
from mathos.research import tga_proctor701 as p
class Tests(unittest.TestCase):
    def test_symbolic(self):
        for t in p.contracts().values():
            self.assertTrue(p.symbolic(t)["identity"])
            self.assertIn(t["statement"],p.source(t,p.proposal(t,"induction_distribute")))
    def test_substitution(self):
        t=p.contracts()["odd_sum"];q=p.proposal(t,"induction_distribute")
        for patch in ({"target":"even_sum"},{"contract_sha256":"0"*64},{"method":"unknown"},{"code":"rfl"}):
            with self.assertRaises(ValueError):p.validate(dict(q,**patch),t)
        bad=dict(t,statement="theorem candidate : True")
        with self.assertRaises(ValueError):p.source(bad,p.proposal(bad,"induction_distribute"))
    def test_counterexample(self):
        r=p.symbolic(dict(p.contracts()["odd_sum"],b=2))
        self.assertFalse(r["identity"])
        self.assertEqual(r["counterexample"],{"n":1,"recurrence":2,"polynomial":1})
    def test_repair_and_scope(self):
        t=p.contracts()["odd_sum"];b=p.Offline()
        self.assertEqual(b.choose(t,[])[0]["method"],"reflexivity")
        self.assertEqual(b.choose(t,[{"status":"REJECTED_OR_UNVERIFIED"}])[0]["method"],"induction_distribute")
        self.assertEqual(p.gap("odd_sum",False)["minimal_completion_sets"],[["proof"]])
        self.assertEqual(p.gap("odd_sum",True)["minimal_completion_sets"],[[]])
