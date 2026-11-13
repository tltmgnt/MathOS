import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from mathos.proof_analysis.runner import run, result_contracts
from mathos.proof_analysis.adversarial_analysis import ATTACKS


class RunnerTests(unittest.TestCase):
    def test_cli_reports_and_scope(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'evidence'
            proc=subprocess.run([sys.executable,'-m','mathos.proof_analysis','--output-dir',str(out)],
                                capture_output=True,text=True,check=True)
            self.assertIn('Reports written',proc.stdout)
            status=json.loads((out/'verification_run.json').read_text())
            self.assertEqual(status['tests']['status'],'NOT_RUN')
            self.assertEqual(status['overall_mathematical_certification'],'NOT_CERTIFIED')
            manifest=json.loads((out/'SHA256SUMS.json').read_text())
            import hashlib
            for name,digest in manifest['reports'].items():
                self.assertEqual(hashlib.sha256((out/name).read_bytes()).hexdigest(),digest)

    def test_no_cwd_mutation(self):
        before=Path.cwd()
        with tempfile.TemporaryDirectory() as temp:
            run(temp)
            self.assertEqual(Path.cwd(),before)

    def test_contract_fields_match_repository_schema(self):
        schema=json.loads((Path(__file__).resolve().parents[1]/'result-contract.json').read_text())
        contracts=result_contracts([f() for f in ATTACKS])
        self.assertEqual(len(contracts),7)
        for c in contracts:
            self.assertTrue(set(schema['required'])<=c.keys())
            self.assertTrue(c.keys()<=schema['properties'].keys())
            self.assertTrue(c['human_review_required'])
            self.assertTrue(c['limitations'])

    def test_failed_tests_do_not_write_reports(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch('mathos.proof_analysis.runner.unittest.defaultTestLoader.discover',return_value=unittest.TestSuite()):
                with self.assertRaisesRegex(RuntimeError,'failed'):
                    run(temp,run_tests=True)
            self.assertEqual(list(Path(temp).iterdir()),[])
