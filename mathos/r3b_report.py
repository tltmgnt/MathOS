"""Verify and analyze an Ω-R3B record: python -m mathos.r3b_report --help."""
import argparse
import hashlib
import hmac
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

from .r3b import Observation, REQUIRED_METADATA, advantage, paired_comparison


def load_record(path):
    """Verify a record's canonical digest before accepting its observations."""
    def reject_constant(value):
        raise ValueError('Non-finite JSON number: '+value)

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: '+key)
            result[key] = value
        return result

    payload = json.loads(Path(path).read_text(encoding='utf-8'),
                         parse_constant=reject_constant, object_pairs_hook=unique_object)
    if not isinstance(payload, dict):
        raise ValueError('Record must be an object')
    digest = payload.pop('sha256', None)
    if not isinstance(digest, str):
        raise ValueError('Missing SHA-256 digest')
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'), allow_nan=False)
    actual = hashlib.sha256(canonical.encode()).hexdigest()
    if not hmac.compare_digest(actual, digest):
        raise ValueError('Record digest mismatch')
    if payload.get('schema_version') != '1.0':
        raise ValueError('Unsupported schema version')
    metadata = payload.get('metadata')
    if not isinstance(metadata, dict) or REQUIRED_METADATA - metadata.keys():
        raise ValueError('Incomplete metadata')
    if metadata['scenario'] not in {'A', 'B', 'C', 'D'}:
        raise ValueError('Unknown scenario')
    rows = [Observation(**row) for row in payload['observations']]
    keys = [(r.implementation, r.task_id, r.trial, r.condition) for r in rows]
    if not rows or len(set(keys)) != len(keys):
        raise ValueError('Empty or duplicate observations')
    return rows, metadata, digest


def compare_record(path, metric, *, reference='B6', comparator='B5',
                   higher_is_better=True, seed=0, resamples=2000):
    """Equal-weight task means within trials; paired bootstrap across trials.

    The operator must establish that trials are independent. This analysis cannot
    infer independence from a trial identifier or establish superiority by itself.
    """
    if reference == comparator:
        raise ValueError('Choose distinct implementations')
    rows, metadata, digest = load_record(path)
    selected = {name: {} for name in (reference, comparator)}
    for row in rows:
        if row.implementation in selected:
            if metric not in row.metrics:
                raise ValueError('Metric missing from a selected observation: '+metric)
            selected[row.implementation][(row.trial, row.task_id, row.condition)] = row.metrics[metric]
    first, second = selected[reference], selected[comparator]
    if not first or first.keys() != second.keys():
        raise ValueError('Selected implementations must have identical nonempty task/trial/condition coverage')
    coverage = defaultdict(set)
    for trial, task, condition in first:
        coverage[trial].add((task, condition))
    if any(tasks != next(iter(coverage.values())) for tasks in coverage.values()):
        raise ValueError('Task/condition coverage must match across trials')
    units = {}
    for name, values in selected.items():
        grouped = defaultdict(list)
        for (trial, _, _), value in values.items():
            grouped[trial].append(value)
        units[name] = {trial: mean(values) for trial, values in grouped.items()}
    stats = paired_comparison(units[reference], units[comparator],
                              higher_is_better=higher_is_better, seed=seed, resamples=resamples)
    return {'schema_version': '1.0', 'status': 'descriptive_analysis_not_superiority_claim',
            'source_sha256': digest, 'dataset_version': metadata['dataset_version'],
            'metric': metric, 'reference': reference, 'comparator': comparator,
            'higher_is_better': higher_is_better,
            'aggregation': 'equal_weight_task_mean_within_trial',
            'independence': 'operator_must_verify',
            'tasks_per_trial': len(next(iter(coverage.values()))),
            'reference_mean': mean(units[reference].values()),
            'comparator_mean': mean(units[comparator].values()),
            'comparison': stats,
            'integration': advantage(mean(units[reference].values()),
                                     mean(units[comparator].values()),
                                     higher_is_better=higher_is_better)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path)
    parser.add_argument('--metric', required=True)
    parser.add_argument('--reference', default='B6')
    parser.add_argument('--comparator', default='B5')
    parser.add_argument('--lower-is-better', action='store_true')
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--resamples', type=int, default=2000)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    if args.output and args.output.resolve() == args.record.resolve():
        parser.error('Output must not overwrite the input record')
    try:
        report = compare_record(args.record, args.metric, reference=args.reference,
                                comparator=args.comparator, higher_is_better=not args.lower_is_better,
                                seed=args.seed, resamples=args.resamples)
        rendered = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+'\n'
        if args.output:
            args.output.write_text(rendered, encoding='utf-8')
        else:
            print(rendered, end='')
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
