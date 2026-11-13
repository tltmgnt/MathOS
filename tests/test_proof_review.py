import random
import unittest
from copy import deepcopy

from mathos.proof_review import (benchmark, completion_sets, dependency_metrics,
                                exhaustive_sets, graph_digest, review_comparison,
                                review_packet, validate)


def example():
    return {'A': {'state': 'open'}, 'B': {'state': 'open'}, 'C': {'state': 'open'},
            'T': {'state': 'derived', 'routes': [['A', 'B'], ['A', 'C']]}}


class ProofReviewTests(unittest.TestCase):
    def test_alternative_routes_and_shared_obligations(self):
        packet = review_packet(example(), 'T')
        self.assertEqual(packet['completion_sets'], [['A', 'B'], ['A', 'C']])
        self.assertEqual(packet['shared_obligations'], ['A'])

    def test_external_and_absorption(self):
        graph = example()
        graph['B'] = {'state': 'established_external'}
        self.assertEqual(completion_sets(graph, 'T'), [frozenset({'A'})])
        self.assertEqual(completion_sets(graph, 'B'), [frozenset()])

    def test_invalid_inputs(self):
        invalid = [
            {'T': {'state': 'derived', 'routes': [['T']]}},
            {'T': {'state': 'derived', 'routes': [['missing']]}},
            {'T': {'state': 'derived', 'routes': [[]]}},
            {'T': {'state': 'open', 'routes': []}},
            {'T': {'state': 'unknown'}},
        ]
        for graph in invalid:
            with self.subTest(graph=graph), self.assertRaises(ValueError):
                validate(graph, 'T')

    def test_shared_dependencies_and_deep_graph(self):
        graph = {'L': {'state': 'open'}}
        for i in range(1200):
            graph[str(i)] = {'state': 'derived', 'routes': [['L' if i == 0 else str(i-1)]]}
        self.assertEqual(completion_sets(graph, '1199'), [frozenset({'L'})])

    def test_seeded_graphs_against_independent_boolean_oracle(self):
        rng = random.Random(173)
        for trial in range(150):
            graph = {f'L{i}': {'state': 'open'} for i in range(rng.randint(1, 7))}
            graph['E'] = {'state': 'established_external'}
            for i in range(rng.randint(1, 7)):
                names = list(graph)
                graph[f'D{i}'] = {'state': 'derived', 'routes': [
                    rng.sample(names, rng.randint(1, min(3, len(names))))
                    for _ in range(rng.randint(1, 3))]}
            target = list(graph)[-1]
            with self.subTest(trial=trial):
                self.assertEqual(set(completion_sets(graph, target)), set(exhaustive_sets(graph, target)))

    def test_dependency_misses_and_spurious_edges(self):
        truth, candidate = example(), example()
        candidate['T']['routes'] = [['A'], ['B', 'C']]
        candidate['B'] = {'state': 'derived', 'routes': [['C']]}
        report = dependency_metrics(truth, candidate)
        self.assertEqual(report['spurious'], [('B', 'C')])
        candidate = example()
        candidate['T']['routes'] = [['A', 'B']]
        self.assertEqual(dependency_metrics(truth, candidate)['missed'], [('T', 'C')])
        empty = {'A': {'state': 'open'}}
        self.assertIsNone(dependency_metrics(empty, empty)['recall'])

    def test_benchmark_measurements_and_limits(self):
        report = benchmark(example(), 'T', repeats=2)
        self.assertTrue(report['correctness_agreement'])
        for values in report['measurements'].values():
            self.assertEqual(len(values['elapsed_ns']), 2)
            self.assertTrue(all(v > 0 for v in values['python_peak_bytes']))
        graph = {str(i): {'state': 'open'} for i in range(17)}
        with self.assertRaises(ValueError):
            exhaustive_sets(graph, '0')

    def test_review_time_cannot_hide_missed_findings(self):
        base = {'reviewer_id': 'synthetic-test', 'case_id': 'case',
                'graph_sha256': graph_digest(example()), 'expected_issue_ids': ['a', 'b']}
        rows = [{**base, 'condition': 'baseline', 'order': 1, 'seconds': 100,
                 'found_issue_ids': ['a', 'b']},
                {**base, 'condition': 'assisted', 'order': 2, 'seconds': 60,
                 'found_issue_ids': ['a', 'false-positive']}]
        report = review_comparison(rows)
        self.assertEqual(report['pairs'][0]['seconds_saved'], 40)
        self.assertEqual(report['pairs'][0]['scores']['assisted']['missed'], ['b'])
        self.assertEqual(report['pairs'][0]['scores']['assisted']['spurious'], ['false-positive'])
        for mutation in ('missing', 'duplicate', 'digest', 'time', 'truth', 'order'):
            bad = deepcopy(rows)
            if mutation == 'missing': bad.pop()
            if mutation == 'duplicate': bad.append(bad[0])
            if mutation == 'digest': bad[1]['graph_sha256'] = 'a' * 64
            if mutation == 'time': bad[1]['seconds'] = float('nan')
            if mutation == 'truth': bad[1]['expected_issue_ids'] = []
            if mutation == 'order': bad[1]['order'] = 1
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                review_comparison(bad)


if __name__ == '__main__':
    unittest.main()
