import unittest
from mathos.research.pnp_library_selection import bundles, choose, union_snapshot, BUNDLE
from mathos.research.pnp_evidence_benchmark import digest

class TestSelection(unittest.TestCase):
    def test_bundles_and_union(self):
        t=lambda i: {"n":1,"axioms":((1,),),"steps":((1,),)*i,"edges":()}
        base=(t(1),)
        expanded=base+tuple(t(i) for i in range(2,14))
        c=bundles(base,expanded)
        self.assertEqual(c["retain"],base)
        self.assertTrue(all(len(x)<=len(base)+BUNDLE for x in c.values()))
        self.assertEqual(digest(base),digest((t(1),)))
        self.assertEqual(union_snapshot(base,[expanded,expanded]),expanded)
        with self.assertRaises(ValueError):
            bundles(base,expanded[1:])

    def test_selection_no_loss_and_abstain(self):
        cohorts={"retain":(1,),"gain":(1,2),"loss":(1,3),"cheap":(1,4)}
        def row(*hits):
            return {"arms":{k:{"status":"verified" if k in hits else "not_found",
                               "work":1 if k=="loss" else 2 if k=="cheap" else 10}
                            for k in cohorts}}
        rows=[row("retain","gain","cheap"),row("gain","loss"),row("loss")]
        self.assertEqual(choose(rows,cohorts),"gain")
        self.assertEqual(choose(rows[:1],cohorts),"cheap")
        self.assertEqual(choose([{"arms":{"retain":{"status":"verified","work":1},
                                        "gain":{"status":"verified","work":2}}}],
                                {"retain":(1,),"gain":(1,2)}),"retain")

if __name__=="__main__":
    unittest.main()
