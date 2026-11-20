#!/usr/bin/env python3
"""Offline, non-authoritative public research-math replay harness (stdlib only)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

SCHEMA = 'mathos_firstproof_benchmark/1'
HEX = re.compile(r'^[0-9a-f]{64}$')
ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$')
MAX_INPUT = 1024 * 1024
MAX_OUTPUT = 2 * 1024 * 1024


def encoded(obj):
    return (json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                       allow_nan=False) + '\n').encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_keys(value, keys, where):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError(f'{where}: expected exact fields {sorted(keys)}')


def load_json_bytes(data):
    def no_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    return json.loads(data.decode('utf-8'), object_pairs_hook=no_duplicates,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f'nonfinite JSON constant: {value}')))


def regular_file(path, limit):
    """Refuse symlinks and non-regular sources, and limit memory consumption."""
    if path.is_symlink():
        raise ValueError(f'symlink forbidden: {path}')
    with path.open('rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError(f'not a regular file: {path}')
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f'file exceeds {limit} bytes: {path}')
    return data


def checked_file(root, relative, expected):
    if not isinstance(relative, str) or not relative or '\\' in relative:
        raise ValueError('invalid relative file path')
    p = Path(relative)
    if p.is_absolute() or any(part in ('', '.', '..') for part in relative.split('/')):
        raise ValueError('unsafe file path')
    root = root.resolve(strict=True)
    path = root.joinpath(*relative.split('/'))
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != root):
        raise ValueError('symlink in file path')
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError('file escapes input directory')
    contents = regular_file(path, MAX_INPUT)
    if not isinstance(expected, str) or not HEX.fullmatch(expected) or digest(contents) != expected:
        raise ValueError(f'file hash mismatch: {relative}')
    return contents


def load_manifest(path):
    manifest = load_json_bytes(regular_file(path, MAX_INPUT))
    check_keys(manifest, ('schema_version', 'benchmark_id', 'source_url', 'problems'), 'manifest')
    if manifest['schema_version'] != SCHEMA or not isinstance(manifest['benchmark_id'], str) or not ID.fullmatch(manifest['benchmark_id']):
        raise ValueError('invalid schema or benchmark_id')
    if not isinstance(manifest['source_url'], str) or not manifest['source_url'].startswith('https://'):
        raise ValueError('source_url must be https')
    if not isinstance(manifest['problems'], list) or not 0 < len(manifest['problems']) <= 100:
        raise ValueError('problems must number 1..100')
    ids, texts = [], []
    for index, problem in enumerate(manifest['problems']):
        check_keys(problem, ('id', 'path', 'sha256'), f'problem[{index}]')
        if not isinstance(problem['id'], str) or not ID.fullmatch(problem['id']):
            raise ValueError('invalid problem ID')
        ids.append(problem['id'])
        texts.append(checked_file(path.parent, problem['path'], problem['sha256']))
    if ids != sorted(set(ids)):
        raise ValueError('problem IDs must be unique and sorted')
    return manifest, texts


def write_new(output, payload):
    if output.exists() or output.is_symlink():
        raise ValueError('output exists (will not overwrite)')
    parent = output.parent.resolve(strict=True)
    if not parent.is_dir():
        raise ValueError('output parent is not a directory')
    fd, temp = tempfile.mkstemp(prefix='.firstproof-', dir=parent)
    try:
        with os.fdopen(fd, 'wb') as fh:
            fh.write(encoded(payload))
            fh.flush()
            os.fsync(fh.fileno())
        os.link(temp, output)  # Exclusive, never silently replace an existing result.
    finally:
        os.unlink(temp)


def execute(command, contents, timeout):
    # Temporary streams bound memory usage even when a runner emits unbounded output.
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            child = subprocess.run(command, input=contents, stdout=out, stderr=err,
                                   timeout=timeout, check=False)
            status = 'completed' if child.returncode == 0 else 'runner_error'
            exit_code = child.returncode
        except subprocess.TimeoutExpired:
            status, exit_code = 'timeout', None
        out.seek(0)
        stdout = out.read(MAX_OUTPUT + 1)
        err.seek(0)
        stderr = err.read(MAX_OUTPUT + 1)
    if len(stdout) > MAX_OUTPUT or len(stderr) > MAX_OUTPUT:
        # Files were truncated for recording; never represent truncated results as full proof.
        return {'status': 'output_limit_exceeded', 'exit_code': exit_code,
                'stdout_sha256': None, 'stderr_sha256': None,
                'solution_utf8': '', 'stderr_utf8': 'runner exceeded output capture limit'}
    try:
        solution, errors = stdout.decode('utf-8'), stderr.decode('utf-8')
    except UnicodeDecodeError:
        return {'status': 'invalid_utf8_output', 'exit_code': exit_code,
                'stdout_sha256': digest(stdout), 'stderr_sha256': digest(stderr),
                'solution_utf8': '', 'stderr_utf8': 'runner output is not valid UTF-8'}
    return {'status': status, 'exit_code': exit_code,
            'stdout_sha256': digest(stdout), 'stderr_sha256': digest(stderr),
            'solution_utf8': solution, 'stderr_utf8': errors}


def validate_run(report):
    check_keys(report, ('schema_version', 'benchmark_id', 'source_manifest_sha256', 'runner_argv',
                        'timeout_seconds', 'evaluation_mode', 'authoritative', 'firstproof_certified', 'results'), 'run')
    if report['schema_version'] != 'mathos_firstproof_run/1' or report['authoritative'] is not False or report['firstproof_certified'] is not False or report['evaluation_mode'] != 'public_replay_ungraded':
        raise ValueError('invalid run authority or evaluation markers')
    if not isinstance(report['source_manifest_sha256'], str) or not HEX.fullmatch(report['source_manifest_sha256']):
        raise ValueError('invalid source manifest digest')
    if not isinstance(report['runner_argv'], list) or not report['runner_argv'] or not all(isinstance(x, str) and x for x in report['runner_argv']):
        raise ValueError('invalid runner argv')
    if type(report['timeout_seconds']) is not int or not 1 <= report['timeout_seconds'] <= 86400:
        raise ValueError('invalid timeout')
    if not isinstance(report['results'], list) or not 0 < len(report['results']) <= 100:
        raise ValueError('invalid results')
    ids = []
    for r in report['results']:
        check_keys(r, ('problem_id', 'input_sha256', 'status', 'exit_code', 'stdout_sha256',
                       'stderr_sha256', 'solution_utf8', 'stderr_utf8'), 'result')
        if not isinstance(r['problem_id'], str) or not ID.fullmatch(r['problem_id']):
            raise ValueError('invalid result ID')
        ids.append(r['problem_id'])
        if not isinstance(r['input_sha256'], str) or not HEX.fullmatch(r['input_sha256']):
            raise ValueError('invalid input digest')
        if r['status'] not in ('completed', 'runner_error', 'timeout', 'output_limit_exceeded', 'invalid_utf8_output'):
            raise ValueError('invalid result status')
        if r['exit_code'] is not None and type(r['exit_code']) is not int:
            raise ValueError('invalid exit code')
        for field, text_field in (('stdout_sha256', 'solution_utf8'), ('stderr_sha256', 'stderr_utf8')):
            if not isinstance(r[text_field], str):
                raise ValueError('invalid text output')
            if r['status'] in ('output_limit_exceeded', 'invalid_utf8_output'):
                continue
            if not isinstance(r[field], str) or digest(r[text_field].encode('utf-8')) != r[field]:
                raise ValueError(f'result {r["problem_id"]}: {field} mismatch')
    if ids != sorted(set(ids)):
        raise ValueError('run results must have unique sorted IDs')


def run(args):
    manifest_path = Path(args.manifest)
    manifest, texts = load_manifest(manifest_path)
    if not 1 <= args.timeout <= 86400:
        raise ValueError('timeout must be 1..86400 seconds')
    command = args.command[1:] if args.command and args.command[0] == '--' else args.command
    if not command:
        raise ValueError('missing runner command')
    # One process execution per problem; no shell and no retries.
    records = [{'problem_id': p['id'], 'input_sha256': p['sha256'],
                **execute(command, contents, args.timeout)}
               for p, contents in zip(manifest['problems'], texts)]
    report = {'schema_version': 'mathos_firstproof_run/1', 'benchmark_id': manifest['benchmark_id'],
              'source_manifest_sha256': digest(regular_file(manifest_path, MAX_INPUT)),
              'runner_argv': command, 'timeout_seconds': args.timeout,
              'evaluation_mode': 'public_replay_ungraded', 'authoritative': False,
              'firstproof_certified': False, 'results': records}
    validate_run(report)
    write_new(Path(args.output), report)
    print(f'Wrote {args.output}; {len(records)} attempts; ungraded, non-authoritative')


def grade(args):
    run_bytes = regular_file(Path(args.run), 4 * 1024 * 1024)
    report = load_json_bytes(run_bytes)
    validate_run(report)
    grades = load_json_bytes(regular_file(Path(args.grades), MAX_INPUT))
    check_keys(grades, ('reviewer', 'scores'), 'grades')
    if not isinstance(grades['reviewer'], str) or not grades['reviewer'].strip():
        raise ValueError('reviewer required')
    if not isinstance(grades['scores'], list):
        raise ValueError('scores must be a list')
    ids = []
    for score in grades['scores']:
        check_keys(score, ('problem_id', 'correctness', 'exposition', 'attribution', 'notes'), 'score')
        ids.append(score['problem_id'])
        for key in ('correctness', 'exposition', 'attribution'):
            if type(score[key]) is not int or not 0 <= score[key] <= 5:
                raise ValueError('scores must be integers from 0 to 5')
        if not isinstance(score['notes'], str):
            raise ValueError('notes must be text')
    if ids != [r['problem_id'] for r in report['results']]:
        raise ValueError('grades must be in run order and contain exactly one per problem')
    output = {'schema_version': 'mathos_firstproof_review/1',
              'run_sha256': digest(run_bytes), 'benchmark_id': report['benchmark_id'],
              'reviewer': grades['reviewer'], 'scoring_scale': 'local_0_to_5_not_official_firstproof',
              'authoritative': False, 'firstproof_certified': False, 'scores': grades['scores']}
    write_new(Path(args.output), output)
    print(f'Wrote {args.output}; locally reviewed, not an official First Proof score')


def verify(args):
    run_bytes = regular_file(Path(args.run), 4 * 1024 * 1024)
    report = load_json_bytes(run_bytes)
    validate_run(report)
    manifest_path = Path(args.manifest)
    manifest_bytes = regular_file(manifest_path, MAX_INPUT)
    manifest, _ = load_manifest(manifest_path)
    if digest(manifest_bytes) != report['source_manifest_sha256'] or manifest['benchmark_id'] != report['benchmark_id']:
        raise ValueError('run no longer matches benchmark manifest')
    for problem, result in zip(manifest['problems'], report['results']):
        if problem['id'] != result['problem_id'] or problem['sha256'] != result['input_sha256']:
            raise ValueError('run input identity mismatch')
    if args.review:
        review = load_json_bytes(regular_file(Path(args.review), MAX_INPUT))
        check_keys(review, ('schema_version', 'run_sha256', 'benchmark_id', 'reviewer',
                            'scoring_scale', 'authoritative', 'firstproof_certified', 'scores'), 'review')
        if review['schema_version'] != 'mathos_firstproof_review/1' or review['run_sha256'] != digest(run_bytes) or review['benchmark_id'] != report['benchmark_id'] or review['scoring_scale'] != 'local_0_to_5_not_official_firstproof' or review['authoritative'] is not False or review['firstproof_certified'] is not False:
            raise ValueError('review does not match run or has invalid authority markers')
        if not isinstance(review['reviewer'], str) or not review['reviewer'].strip():
            raise ValueError('reviewer missing')
        scores = review['scores']
        if not isinstance(scores, list) or [s.get('problem_id') for s in scores if isinstance(s, dict)] != [r['problem_id'] for r in report['results']]:
            raise ValueError('review scores incomplete or out of order')
        for score in scores:
            check_keys(score, ('problem_id', 'correctness', 'exposition', 'attribution', 'notes'), 'score')
            if not isinstance(score['notes'], str) or any(type(score[k]) is not int or not 0 <= score[k] <= 5 for k in ('correctness', 'exposition', 'attribution')):
                raise ValueError('invalid review scores')
    print('Verified matching input hashes, run artifact, and optional local review; no mathematical authority granted')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='operation', required=True)
    runner = commands.add_parser('run', help='replay published problem snapshots')
    runner.add_argument('--manifest', required=True)
    runner.add_argument('--output', required=True)
    runner.add_argument('--timeout', type=int, default=300)
    runner.add_argument('command', nargs=argparse.REMAINDER)
    grader = commands.add_parser('grade', help='bind manual grades to frozen run')
    grader.add_argument('--run', required=True)
    grader.add_argument('--grades', required=True)
    grader.add_argument('--output', required=True)
    verifier = commands.add_parser('verify', help='verify run identity and optional review')
    verifier.add_argument('--manifest', required=True)
    verifier.add_argument('--run', required=True)
    verifier.add_argument('--review')
    args = parser.parse_args()
    try:
        {'run': run, 'grade': grade, 'verify': verify}[args.operation](args)
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        parser.exit(2, f'error: {exc}\n')


if __name__ == '__main__':
    main()
