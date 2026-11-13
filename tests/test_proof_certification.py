import unittest
from mathos.proof_analysis.gap_analysis import Claim, analyze
from mathos.proof_analysis.certification_audit import exhaustive_check, regression, graph_hash


class CertificateTests(unittest.TestCase):
    def setUp(self):
        self.g = {'a': Claim('a', 'open'), 'b': Claim('b', 'open'),
                  't': Claim('t', 'derived', (('a', 'b'),))}

    def test_valid(self):
        self.assertEqual(exhaustive_check(self.g, 't', [['a', 'b']])['assignments_checked'], 4)

    def test_false_completion_rejected(self):
        with self.assertRaises(ValueError):
            exhaustive_check(self.g, 't', [['a']])

    def test_missing_route_rejected(self):
        self.g['t'] = Claim('t', 'derived', (('a',), ('b',)))
        with self.assertRaises(ValueError):
            exhaustive_check(self.g, 't', [['a']])

    def test_superset_rejected(self):
        self.g['t'] = Claim('t', 'derived', (('a',),))
        with self.assertRaises(ValueError):
            exhaustive_check(self.g, 't', [['a'], ['a', 'b']])

    def test_forged_empty_certificate_rejected(self):
        with self.assertRaises(ValueError):
            exhaustive_check(self.g, 't', [[]])

    def test_unknown_leaf_rejected(self):
        with self.assertRaises(ValueError):
            exhaustive_check(self.g, 't', [['fake']])

    def test_cycle_rejected(self):
        self.g['t'] = Claim('t', 'derived', (('t',),))
        with self.assertRaises(ValueError):
            exhaustive_check(self.g, 't', [[]])

    def test_resource_limit_fails_closed(self):
        with self.assertRaises(ValueError):
            exhaustive_check(self.g, 't', [['a', 'b']], max_open=1)

    def test_external_is_assumption_not_new_proof(self):
        self.g['a'] = Claim('unverified externally supplied fact', 'established_external')
        r = analyze(self.g, 't')
        self.assertEqual(r['minimal_completion_sets'], [['b']])
        self.assertEqual(exhaustive_check(self.g, 't', [['b']])['assignments_checked'], 2)

    def test_content_hash_changes(self):
        original = graph_hash(self.g)
        self.g['a'] = Claim('changed statement', 'open')
        self.assertNotEqual(original, graph_hash(self.g))

    def test_seeded_graph_cross_check(self):
        self.assertEqual(regression(cases=1000)['graphs_checked'], 1000)


if __name__ == '__main__':
    unittest.main()
