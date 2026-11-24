import unittest
from mathos.research import tga_proctor_scope_gap as m

class ScopeGap(unittest.TestCase):
    def test_modeled_routes(self):
        g=m.model()
        self.assertEqual([len(x) for x in g["M1"]["minimal_completion_sets"]],[6])
        self.assertEqual([len(x) for x in g["M2"]["minimal_completion_sets"]],[7,7])
        self.assertEqual([len(x) for x in g["M3"]["minimal_completion_sets"]],[10,10])
        self.assertEqual(len(g["M3"]["common_to_all_modeled_routes"]),9)
        self.assertEqual([len(x) for x in g["M4"]["minimal_completion_sets"]],[11,11])
        self.assertTrue(all(r["status"]=="BLOCKED" for r in g.values()))
    def test_observed_boundaries(self):
        r=m.controls()
        self.assertTrue(r["five_variable_identity_rejected"])
        self.assertEqual(r["same_identity_linked_to_distinct_attempts"],["RH.sparse_shift","HODGE.primitive"])
        self.assertTrue(r["changed_free_text_structurally_accepted"])
        self.assertTrue(r["original_checkpoint_unchanged"])
        self.assertFalse(r["model_identity_authenticated"])
        self.assertEqual(len(r["prefix_countermodels"]),6)
    def test_no_promotion(self):
        r=m.run()
        self.assertEqual(r["global_promotion"],"NONE")
        self.assertEqual(r["canonical_open_obligations"],14)
        self.assertFalse(r["educational_validation_established"])
