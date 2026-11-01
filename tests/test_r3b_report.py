import json
from pathlib import Path
import tempfile
import unittest
from mathos.r3b import Observation, REQUIRED_METADATA, write_record
from mathos.r3b_report import compare_record, load_record, main


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'record.json'
        self.metadata = dict.fromkeys(REQUIRED_METADATA, 'documented')
        self.metadata.update(scenario='A', dataset_split='development')
        self.rows = [Observation(name, task, trial, 'complete', {'loss': value})
                     for trial in range(3) for task in ('a', 'b')
                     for name, value in [('B6', 1+trial), ('B5', 3+trial)]]
        write_record(self.path, self.rows, self.metadata)

    def test_trial_aggregation_and_loss_direction(self):
        result = compare_record(self.path, 'loss', higher_is_better=False)
        self.assertEqual(result['comparison']['n'], 3)
        self.assertEqual(result['tasks_per_trial'], 2)
        self.assertEqual(result['comparison']['mean_difference'], 2)
        self.assertEqual(result['comparison']['ci95'], [2, 2])
        self.assertEqual(result, compare_record(self.path, 'loss', higher_is_better=False))

    def test_tampering_is_rejected(self):
        payload = json.loads(self.path.read_text())
        payload['observations'][0]['metrics']['loss'] = 99
        self.path.write_text(json.dumps(payload))
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            load_record(self.path)

    def test_missing_pairs_and_unequal_trial_coverage_are_rejected(self):
        write_record(self.path, self.rows[:-1], self.metadata)
        with self.assertRaisesRegex(ValueError, 'coverage'):
            compare_record(self.path, 'loss')
        write_record(self.path, self.rows[:-2], self.metadata)
        with self.assertRaisesRegex(ValueError, 'coverage'):
            compare_record(self.path, 'loss')

    def test_cli_writes_report_and_preserves_source(self):
        output = self.path.with_name('report.json')
        source = self.path.read_bytes()
        main([str(self.path), '--metric', 'loss', '--lower-is-better', '--output', str(output)])
        self.assertEqual(json.loads(output.read_text())['integration']['advantage'], 2)
        self.assertEqual(source, self.path.read_bytes())
        with self.assertRaises(SystemExit):
            main([str(self.path), '--metric', 'loss', '--output', str(self.path)])

    def test_missing_metric_and_single_trial_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Metric missing'):
            compare_record(self.path, 'unknown')
        write_record(self.path, self.rows[:4], self.metadata)
        with self.assertRaisesRegex(ValueError, 'At least two'):
            compare_record(self.path, 'loss')
