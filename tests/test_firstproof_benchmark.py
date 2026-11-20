import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'firstproof_benchmark.py'


class FirstProofAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'p1.txt').write_text('Prove 1 + 1 = 2\n')
        self.problem_sha = hashlib.sha256((self.root / 'p1.txt').read_bytes()).hexdigest()
        self.manifest = {'schema_version': 'mathos_firstproof_benchmark/1',
                         'benchmark_id': 'firstproof-public-replay-test',
                         'source_url': 'https://1stproof.org/',
                         'problems': [{'id': 'p1', 'path': 'p1.txt', 'sha256': self.problem_sha}]}
        self.save_manifest()

    def save_manifest(self):
        (self.root / 'manifest.json').write_text(json.dumps(self.manifest))

    def cmd(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True, cwd=self.root)

    def run_once(self, output='run.json'):
        return self.cmd('run', '--manifest', 'manifest.json', '--output', output,
                        '--timeout', '5', '--', sys.executable, '-c',
                        'import sys; sys.stdout.write(sys.stdin.read())')

    def test_one_attempt_and_reproducibility(self):
        a = self.run_once()
        self.assertEqual(a.returncode, 0, a.stderr)
        self.assertEqual(self.run_once().returncode, 2)  # no overwrite
        self.assertEqual(self.run_once('second.json').returncode, 0)
        self.assertEqual((self.root / 'run.json').read_bytes(), (self.root / 'second.json').read_bytes())
        report = json.loads((self.root / 'run.json').read_text())
        self.assertEqual(report['results'][0]['solution_utf8'], 'Prove 1 + 1 = 2\n')
        self.assertFalse(report['authoritative'])

    def test_rejects_modified_input(self):
        (self.root / 'p1.txt').write_text('altered')
        response = self.run_once()
        self.assertEqual(response.returncode, 2)
        self.assertIn('hash mismatch', response.stderr)

    def test_rejects_traversal_and_symlink(self):
        self.manifest['problems'][0]['path'] = '../outside.txt'
        self.save_manifest()
        self.assertEqual(self.run_once().returncode, 2)
        self.manifest['problems'][0]['path'] = 'link.txt'
        self.save_manifest()
        (self.root / 'link.txt').symlink_to(self.root / 'p1.txt')
        self.assertEqual(self.run_once().returncode, 2)

    def test_manual_grading_separate_and_frozen(self):
        self.assertEqual(self.run_once().returncode, 0)
        grades = {'reviewer': 'independent-mathematician', 'scores': [
            {'problem_id': 'p1', 'correctness': 4, 'exposition': 3, 'attribution': 2, 'notes': 'example'}]}
        (self.root / 'grades.json').write_text(json.dumps(grades))
        p = self.cmd('grade', '--run', 'run.json', '--grades', 'grades.json', '--output', 'review.json')
        self.assertEqual(p.returncode, 0, p.stderr)
        review = json.loads((self.root / 'review.json').read_text())
        self.assertEqual(review['run_sha256'], hashlib.sha256((self.root / 'run.json').read_bytes()).hexdigest())
        self.assertFalse(review['firstproof_certified'])
        grades['scores'][0]['correctness'] = 6
        (self.root / 'grades.json').write_text(json.dumps(grades))
        self.assertEqual(self.cmd('grade', '--run', 'run.json', '--grades', 'grades.json', '--output', 'bad.json').returncode, 2)

    def test_runner_failure_recorded_not_graded(self):
        p = self.cmd('run', '--manifest', 'manifest.json', '--output', 'fail.json',
                     '--', sys.executable, '-c', 'raise SystemExit(3)')
        self.assertEqual(p.returncode, 0, p.stderr)
        report = json.loads((self.root / 'fail.json').read_text())
        self.assertEqual(report['results'][0]['status'], 'runner_error')
        self.assertEqual(report['results'][0]['exit_code'], 3)


if __name__ == '__main__':
    unittest.main()

class HardeningTests(unittest.TestCase):
    setUp = FirstProofAdapterTests.setUp
    save_manifest = FirstProofAdapterTests.save_manifest
    cmd = FirstProofAdapterTests.cmd
    run_once = FirstProofAdapterTests.run_once

    def test_verify_run_and_review(self):
        self.assertEqual(self.run_once().returncode, 0)
        grades = {'reviewer':'reviewer','scores':[{'problem_id':'p1','correctness':2,'exposition':2,'attribution':2,'notes':'review'}]}
        (self.root/'grades.json').write_text(json.dumps(grades))
        self.assertEqual(self.cmd('grade','--run','run.json','--grades','grades.json','--output','review.json').returncode,0)
        self.assertEqual(self.cmd('verify','--manifest','manifest.json','--run','run.json','--review','review.json').returncode,0)
        run = json.loads((self.root/'run.json').read_text())
        run['results'][0]['solution_utf8'] = 'tampered'
        (self.root/'run.json').write_text(json.dumps(run))
        p = self.cmd('verify','--manifest','manifest.json','--run','run.json','--review','review.json')
        self.assertEqual(p.returncode, 2)
        self.assertIn('mismatch',p.stderr)

    def test_rejects_duplicate_json_keys(self):
        (self.root/'manifest.json').write_text('{"schema_version":"bad","schema_version":"duplicate"}')
        self.assertEqual(self.run_once().returncode, 2)

    def test_invalid_utf8_runner_output(self):
        p=self.cmd('run','--manifest','manifest.json','--output','badutf.json','--',sys.executable,'-c',
                   'import sys; sys.stdout.buffer.write(b"\\xff")')
        self.assertEqual(p.returncode,0,p.stderr)
        result=json.loads((self.root/'badutf.json').read_text())['results'][0]
        self.assertEqual(result['status'],'invalid_utf8_output')

    def test_output_limit(self):
        p=self.cmd('run','--manifest','manifest.json','--output','large.json','--',sys.executable,'-c',
                   'import sys; sys.stdout.write("a"*2200000)')
        self.assertEqual(p.returncode,0,p.stderr)
        result=json.loads((self.root/'large.json').read_text())['results'][0]
        self.assertEqual(result['status'],'output_limit_exceeded')

    def test_unreviewed_failure_is_not_success(self):
        p=self.cmd('run','--manifest','manifest.json','--output','failure.json','--',sys.executable,'-c',
                   'raise SystemExit(4)')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(self.cmd('verify','--manifest','manifest.json','--run','failure.json').returncode,0)
