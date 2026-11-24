import unittest
from fractions import Fraction
from mathos.research.tga_universal_bridges import run

class UniversalBridges(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=run()
    def test_routes(self):
        t=self.r["derived_routes"]
        self.assertEqual(t["HODGE"]["minimal_completion_sets"],[["HODGE.primitive"]])
        self.assertEqual(len(t["NS"]["minimal_completion_sets"]),4)
        self.assertEqual(len(t["NS"]["minimal_blocking_sets"][0]),4)
        self.assertEqual(len(t["BSD.core"]["minimal_completion_sets"][0]),2)
        self.assertEqual(len(t["BSD.refined"]["minimal_completion_sets"][0]),4)
    def test_moments(self):
        for r in self.r["finite_hankel_counterexamples"]:
            self.assertLess(Fraction(r["negative_quadratic_form"]),0)
            self.assertEqual(r["witness_degree"],r["largest_tested_order"]+1)
    def test_scope(self):
        self.assertEqual(self.r["canonical_open_obligations"],14)
        self.assertEqual(self.r["promotion"],"NONE")
        self.assertFalse(self.r["universal_solutions_claimed"])
        self.assertEqual(self.r["derived_routes"]["POINCARE.external"]["minimal_completion_sets"],[[]])
        self.assertEqual(self.r["derived_routes"]["POINCARE.project"]["status"],"BLOCKED")
