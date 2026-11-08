"""Repository-native report generation, isolated from the caller's working directory."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import unittest

from . import gap_analysis, certification_audit, adversarial_analysis


def result_contracts(findings):
    return [{
        'claim': f.tested_claim,
        'evidence': [{'description': f.reasoning,
                      'source': 'mathos/proof_analysis/adversarial_analysis.py'}],
        'assumptions': [f.evidence_kind, 'The tested shortcut has exactly the stated scope; transfer to a Millennium Problem is not assumed.'],
        'method': 'Exact fixed witness and authored argument: ' + f.outcome,
        'uncertainty': 'No novelty assessment, formal proof replay, or independent external mathematical review.',
        'limitations': [f.limitation],
        'counterexamples': [json.dumps(f.witness, sort_keys=True)],
        'transfer_conditions': ['A separate theorem must justify transfer from this witness or abstraction to the intended mathematical setting.'],
        'verification_plan': f.next_obligation,
        'human_review_required': True,
    } for f in findings]


def run(output_dir, run_tests=False):
    output = Path(output_dir).resolve()
    repo = Path(__file__).resolve().parents[2]
    test_record = {'status': 'NOT_RUN', 'tests_run': None}
    test_log = ''
    if run_tests:
        tests = repo / 'tests'
        if not tests.is_dir():
            raise ValueError('Repository tests unavailable; run without --run-tests or use a source checkout')
        suite = unittest.defaultTestLoader.discover(str(tests), pattern='test_proof_*.py')
        log = io.StringIO()
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
        test_log = log.getvalue()
        test_record = {'status': 'PASS' if result.wasSuccessful() and result.testsRun else 'FAIL',
                       'tests_run': result.testsRun, 'failures': len(result.failures),
                       'errors': len(result.errors), 'skipped': len(result.skipped)}
        if test_record['status'] != 'PASS':
            raise RuntimeError('Proof-analysis tests failed; no new reports written\n' + test_log)
    output.mkdir(parents=True, exist_ok=True)
    with contextlib.redirect_stdout(io.StringIO()):
        gap_analysis.main(output)
        certification_audit.main(output)
        adversarial_analysis.main(output)
    findings = [attack() for attack in adversarial_analysis.ATTACKS]
    (output / 'result_contracts.json').write_text(json.dumps(result_contracts(findings), indent=2)+'\n', encoding='utf-8')
    record = {'tests': test_record, 'scope': 'Boolean graph checks and seven scoped witnesses only.',
              'new_millennium_proofs': 0, 'overall_mathematical_certification': 'NOT_CERTIFIED'}
    (output / 'verification_run.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    (output / 'test_run.txt').write_text(test_log or 'Tests not requested in this run.\n', encoding='utf-8')
    sources = sorted(Path(__file__).parent.glob('*.py')) + sorted((repo/'tests').glob('test_proof_*.py'))
    report_names = ['results.json', 'results.md', 'certification_audit.json',
                    'adversarial_results.json', 'adversarial_results.md',
                    'result_contracts.json', 'verification_run.json', 'test_run.txt']
    manifest = {
        'scope': 'Content identification only; not signatures or mathematical certification.',
        'sources': {str(p.relative_to(repo)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'reports': {name: hashlib.sha256((output/name).read_bytes()).hexdigest() for name in report_names}}
    (output/'SHA256SUMS.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return {'output_dir': str(output), **record}
