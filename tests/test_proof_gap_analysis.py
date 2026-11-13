import unittest
from mathos.proof_analysis.gap_analysis import Claim, analyze, models


class GapTests(unittest.TestCase):
    def test_shared_dependency_deduplicated(self):
        g = {'x': Claim('x', 'open'), 'a': Claim('a', 'derived', (('x',),)),
             'b': Claim('b', 'derived', (('x',),)),
             't': Claim('t', 'derived', (('a', 'b'),))}
        self.assertEqual(analyze(g, 't')['minimal_completion_sets'], [['x']])

    def test_alternative_routes_and_superset_elimination(self):
        g = {k: Claim(k, 'open') for k in ['a', 'b', 'c']}
        g['t'] = Claim('t', 'derived', (('a',), ('a', 'b'), ('b', 'c')))
        r = analyze(g, 't')
        self.assertEqual(r['minimal_completion_sets'], [['a'], ['b', 'c']])
        self.assertEqual(r['common_to_all_modeled_routes'], [])

    def test_cycle_rejected_even_in_unused_route(self):
        g = {'e': Claim('external', 'established_external'),
             't': Claim('t', 'derived', (('e',), ('t',)))}
        with self.assertRaisesRegex(ValueError, 'cycle'):
            analyze(g, 't')

    def test_missing_dependency(self):
        with self.assertRaisesRegex(ValueError, 'Missing'):
            analyze({'t': Claim('t', 'derived', (('missing',),))}, 't')

    def test_empty_proof_cannot_certify(self):
        with self.assertRaises(ValueError):
            analyze({'t': Claim('t', 'derived', ((),))}, 't')

    def test_external_route_can_close(self):
        g = {'e': Claim('e', 'established_external'), 'x': Claim('x', 'open'),
             't': Claim('t', 'derived', (('e',), ('x',)))}
        self.assertEqual(analyze(g, 't')['minimal_completion_sets'], [[]])

    def test_seven_attempts_blocked_poincare_external(self):
        for g in models().values():
            self.assertEqual(analyze(g, 'target')['status'], 'BLOCKED')
        self.assertEqual(analyze(models()['Poincare'], 'published')['minimal_completion_sets'], [[]])

    def test_sat_expansion_with_exact_coefficients(self):
        polynomial = {frozenset(): 1}
        for m in range(1, 9):
            x, y = 2*m-2, 2*m-1
            factor = {frozenset([x]): 1, frozenset([y]): 1, frozenset([x, y]): -1}
            expanded = {}
            for a, ca in polynomial.items():
                for b, cb in factor.items():
                    key = a | b
                    expanded[key] = expanded.get(key, 0) + ca*cb
            polynomial = {k: v for k, v in expanded.items() if v}
            self.assertEqual(len(polynomial), 3**m)


if __name__ == '__main__':
    unittest.main()
