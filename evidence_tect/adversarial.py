#!/usr/bin/env python3
"""Execute adversarial controls against a copy of actual claim evidence."""
import argparse
import copy
import json
from pathlib import Path
import shutil
import tempfile
import check
import validate_polynomials as polynomial

ROOT = Path(__file__).resolve().parents[1]
CLAIM = 'bounded-polynomial-multiply'


def rejected(fn, reason):
    try:
        fn()
    except ValueError as exc:
        if reason not in str(exc):
            raise RuntimeError(f'wrong rejection: {exc}; expected {reason}') from exc
    else:
        raise RuntimeError(f'attack escaped: {reason}')


def run():
    register = json.loads((ROOT / 'evidence_tect/register.json').read_text())
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for record in register['evidence'] + register['reviews']:
            path = Path(record['artifact_path'])
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
        check.check(register, root)
        index = next(i for i,c in enumerate(register['claims']) if c['id'] == CLAIM)
        evidence = next(e for e in register['evidence'] if e['claim_id'] == CLAIM and e['kind'] == 'validation')
        artifact = root / evidence['artifact_path']

        def fresh():
            return copy.deepcopy(register)

        def extra(r, **kw):
            e = dict(evidence, id='adversarial-fixture')
            e.update(kw)
            r['evidence'].append(e)

        original = artifact.read_bytes()
        artifact.write_bytes(original + b'\npoisoned')
        rejected(lambda: check.check(register, root), 'artifact digest mismatch')
        artifact.write_bytes(original)
        results['tampered_artifact'] = 'PASS'

        bad = fresh()
        next(e for e in bad['evidence'] if e['id'] == evidence['id'])['artifact_path'] = '../outside'
        rejected(lambda: check.check(bad, root), 'unsafe artifact path')
        results['path_traversal'] = 'PASS'

        bad = fresh()
        extra(bad, kind='contradiction', result='PASS')
        rejected(lambda: check.check(bad, root), 'UNRESOLVED_CONTRADICTION')
        results['contradiction_injection'] = 'PASS'

        bad = fresh()
        extra(bad, kind='attack', result='FAIL', attack_class='source_poisoning')
        rejected(lambda: check.check(bad, root), 'UNRESOLVED_FAILED_EVIDENCE')
        results['failed_attack_not_ignored'] = 'PASS'

        bad = fresh()
        bad['claims'][index]['state'] = 'ADVERSARIAL_TEST'
        bad['evidence'] = [e for e in bad['evidence'] if e['claim_id'] != CLAIM or e['kind'] != 'attack']
        for attack in sorted(check.ATTACKS):
            extra(bad, id='wrong-scope-'+attack, kind='attack', result='PASS',
                  attack_class=attack, scope='unrelated scope')
        rejected(lambda: check.check(bad, root), 'ATTACK_COVERAGE_MISSING')
        results['out_of_scope_attacks'] = 'PASS'

        bad = fresh()
        next(e for e in bad['evidence'] if e['id'] == evidence['id'])['claim_version'] += 1
        rejected(lambda: check.check(bad, root), 'stale evidence version')
        results['stale_claim_version'] = 'PASS'

        bad = fresh()
        next(e for e in bad['evidence'] if e['id'] == evidence['id'])['expires_at'] = '2000-01-01T00:00:00Z'
        rejected(lambda: check.check(bad, root), 'expired/future evidence')
        results['expired_evidence'] = 'PASS'

        bad = fresh()
        bad['claims'][index]['state'] = 'REPRODUCED'
        rejected(lambda: check.check(bad, root), 'EXTERNAL_REPRODUCTION_NOT_AUTHENTICATED')
        results['unauthenticated_reproduction'] = 'PASS'

        bad = fresh()
        bad['deployment_authorized'] = True
        rejected(lambda: check.check(bad, root), 'policy and external scope')
        results['unauthorized_deployment'] = 'PASS'

        model = root / 'mutant/model.cpp'
        model.parent.mkdir()
        source = polynomial.MODEL.read_text()
        old = 'c[i+j]+=a[i]*b[j]'
        if source.count(old) != 1:
            raise RuntimeError('mutation target drift')
        model.write_text(source.replace(old, 'c[i+j]-=a[i]*b[j]'))
        original_model = polynomial.MODEL
        try:
            polynomial.MODEL = model
            rejected(polynomial.run, 'wrong product')
        finally:
            polynomial.MODEL = original_model
        results['compiled_arithmetic_mutant'] = 'PASS'
        check.check(register, root)
    return {'claim_id': CLAIM, 'result': 'PASS', 'controls': results,
            'attack_classes': sorted(check.ATTACKS),
            'external_independent_reproduction': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = run()
    if args.check and report != json.loads((ROOT / 'evidence_tect/adversarial-validation.json').read_text()):
        raise SystemExit('adversarial evidence report mismatch')
    print(json.dumps(report, indent=2))
