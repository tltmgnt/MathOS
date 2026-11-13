import json
import math
import tempfile
import unittest
from pathlib import Path
from mathos.r3b import (
    Observation, REQUIRED_METADATA, advantage, factorial_design, holm_adjust,
    interaction, paired_comparison, replication_fidelity, replication_resistance,
    write_record, FIDELITY_DIMENSIONS,
)


class R3BTests(unittest.TestCase):
    def test_direction_and_zero_denominators(self):
        self.assertEqual(advantage(2, 4, higher_is_better=False)['advantage'], 2)
        self.assertEqual(advantage(2, 4)['advantage'], -2)
        self.assertIsNone(advantage(0, 0)['relative_advantage_pct'])
        self.assertIsNone(advantage(-1, 2)['relative_separation_loss_pct'])
        self.assertEqual(interaction(10, 4, 5, 1), 2)

    def test_fidelity_and_resistance(self):
        scores = dict.fromkeys(FIDELITY_DIMENSIONS, .8)
        self.assertAlmostEqual(replication_fidelity(scores, dict.fromkeys(scores, .2)), .8)
        self.assertAlmostEqual(replication_resistance(.8, .8, .8, {'rf': .4, 'nrp': .3, 'if': .3}), .2)
        for invalid in [math.nan, math.inf, -.1, 1.1, True]:
            with self.assertRaises(ValueError):
                replication_resistance(invalid, 1, 1, {'rf': 1, 'nrp': 0, 'if': 0})
        with self.assertRaises(ValueError):
            replication_fidelity(scores, dict.fromkeys(scores, .1))

    def test_paired_statistics(self):
        a, b = {'a': 2, 'b': 4, 'c': 6}, {'a': 1, 'b': 3, 'c': 5}
        report = paired_comparison(a, b)
        self.assertEqual(report['ci95'], [1, 1])
        self.assertEqual(report, paired_comparison(a, b))
        self.assertEqual(paired_comparison(a, b, higher_is_better=False)['mean_difference'], -1)
        with self.assertRaises(ValueError):
            paired_comparison(a, {'a': 1, 'b': 2})
        self.assertEqual(holm_adjust({'a': .01, 'b': .04}), {'a': .02, 'b': .04})

    def test_design_and_audit(self):
        self.assertEqual(len(set(factorial_design())), 16)
        row = Observation('B6', 'task1', 0, 'adversarial', {'success': 0})
        metadata = dict.fromkeys(REQUIRED_METADATA, 'documented')
        metadata.update(scenario='A', dataset_split='adversarial')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'result.json'
            record = write_record(path, [row], metadata)
            self.assertEqual(json.loads(path.read_text()), record)
            with self.assertRaises(ValueError):
                write_record(path, [row, row], metadata)
            with self.assertRaises(ValueError):
                write_record(path, [row], {})
        with self.assertRaises(ValueError):
            Observation('B0', 'x', 0, 'complete', {'utility': math.nan})


class MatchedRunnerTests(unittest.TestCase):
    def test_inputs_are_isolated_and_budgets_matched(self):
        from mathos.r3b import BASELINES, run_matched
        calls = []
        class Adapter:
            def evaluate(self, task, *, seed, budget):
                calls.append((task['value'], seed, budget['steps']))
                task['value'] = 999
                budget['steps'] = 0
                return {'success': 1}
        rows = run_matched(dict.fromkeys(BASELINES, Adapter()),
                           [{'task_id': 'x', 'condition': 'complete', 'input': {'value': 1}}],
                           trials=2, seed=42, budget={'steps': 10})
        self.assertEqual(len(rows), 14)
        self.assertEqual(calls, [(1, 42, 10)]*7+[(1, 43, 10)]*7)
