"""Bounded proof-route analysis and comparative evaluation; no truth oracle.

Run: python -m mathos.proof_review graph.json --repeats 5
Graph edges are authored sufficient routes, not verified mathematical inference.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
from itertools import product
import json
import math
from pathlib import Path
from statistics import median
from time import perf_counter_ns
import tracemalloc


def graph_digest(graph):
    return hashlib.sha256(json.dumps(graph, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def validate(graph, target):
    if not isinstance(graph, dict) or not graph or target not in graph:
        raise ValueError('Nonempty graph and existing target required')
    for name, node in graph.items():
        if not isinstance(name, str) or not name.strip() or not isinstance(node, dict):
            raise ValueError('Named claim objects required')
        state = node.get('state')
        if state not in {'open', 'established_external', 'derived'}:
            raise ValueError('Unknown claim state')
        if state != 'derived':
            if 'routes' in node:
                raise ValueError('Leaves cannot declare routes')
            continue
        routes = node.get('routes')
        if not isinstance(routes, list) or not routes:
            raise ValueError('Derived claims require nonempty routes')
        for route in routes:
            if not isinstance(route, list) or not route:
                raise ValueError('Routes must be nonempty lists')
            if any(not isinstance(dep, str) or dep not in graph for dep in route):
                raise ValueError('Missing or invalid dependency')
    # Iterative DFS handles shared dependencies and rejects cycles anywhere.
    colors, order = {}, []
    for root in graph:
        if colors.get(root) == 2:
            continue
        stack = [(root, False)]
        while stack:
            name, leaving = stack.pop()
            if leaving:
                colors[name] = 2
                order.append(name)
                continue
            if colors.get(name) == 1:
                raise ValueError('Cyclic dependency graph')
            if colors.get(name) == 2:
                continue
            colors[name] = 1
            stack.append((name, True))
            for route in graph[name].get('routes', []):
                for dep in route:
                    stack.append((dep, False))
    return order


def _minimal(sets):
    kept = []
    for item in sorted(set(sets), key=lambda s: (len(s), tuple(sorted(s)))):
        if not any(previous <= item for previous in kept):
            kept.append(item)
    return kept


def completion_sets(graph, target):
    """Enumerate inclusion-minimal sufficient open-leaf sets in a finite DAG.

    Output size and intermediate products may be exponential. External claims
    are assumptions; this function does not establish their mathematical truth.
    """
    values = {}
    for name in validate(graph, target):
        node = graph[name]
        if node['state'] == 'open':
            values[name] = [frozenset({name})]
        elif node['state'] == 'established_external':
            values[name] = [frozenset()]
        else:
            alternatives = []
            for route in node['routes']:
                combined = [frozenset()]
                for dep in route:
                    combined = _minimal(a | b for a in combined for b in values[dep])
                alternatives.extend(combined)
            values[name] = _minimal(alternatives)
    return values[target]


def exhaustive_sets(graph, target, max_leaves=16):
    """Separate Boolean assignment baseline, capped to bound enumeration."""
    order = validate(graph, target)
    leaves = sorted(k for k, n in graph.items() if n['state'] == 'open')
    if len(leaves) > max_leaves:
        raise ValueError('Exhaustive baseline leaf limit exceeded')
    satisfying = []
    for bits in product((False, True), repeat=len(leaves)):
        assignment = dict(zip(leaves, bits))
        values = {}
        for name in order:
            node = graph[name]
            if node['state'] == 'open':
                values[name] = assignment[name]
            elif node['state'] == 'established_external':
                values[name] = True
            else:
                values[name] = any(all(values[d] for d in r) for r in node['routes'])
        if values[target]:
            satisfying.append(frozenset(k for k in leaves if assignment[k]))
    # Deliberately independent minimization from the optimized analyzer.
    return sorted((s for s in satisfying if not any(t < s for t in satisfying)),
                  key=lambda s: (len(s), tuple(sorted(s))))


def edge_set(graph):
    """Structural edge coverage only; route grouping is not captured by edges."""
    validate(graph, next(iter(graph), None))
    return {(name, dep) for name, node in graph.items()
            for route in node.get('routes', []) for dep in route}


def dependency_metrics(reference, candidate):
    expected, actual = edge_set(reference), edge_set(candidate)
    missed, spurious = expected - actual, actual - expected
    return {'expected_edges': len(expected), 'detected_edges': len(actual),
            'missed': sorted(missed), 'spurious': sorted(spurious),
            'recall': len(expected & actual) / len(expected) if expected else None,
            'precision': len(expected & actual) / len(actual) if actual else None,
            'scope': 'authored_reference_edges_not_mathematical_truth'}


def review_packet(graph, target):
    sets = completion_sets(graph, target)
    common = set.intersection(*(set(s) for s in sets)) if sets else set()
    return {'graph_sha256': graph_digest(graph), 'target': target,
            'completion_sets': [sorted(s) for s in sets],
            'shared_obligations': sorted(common),
            'claims': [{**deepcopy(v), 'id': k} for k, v in sorted(graph.items())],
            'review_checks': ['Check exact hypotheses and statement',
                              'Validate every sufficient route',
                              'Identify omitted dependencies and alternatives',
                              'Attach theorem locators or counterexamples'],
            'status': 'authored_routes_require_expert_review'}


def benchmark(graph, target, repeats=5):
    if type(repeats) is not int or repeats < 1:
        raise ValueError('Positive repeat count required')
    if tracemalloc.is_tracing():
        raise ValueError('Benchmark requires ownership of tracemalloc')
    expected = exhaustive_sets(graph, target)
    observed = completion_sets(graph, target)
    if set(expected) != set(observed):
        raise ValueError('Analyzer disagrees with exhaustive baseline')
    functions = {'completion_sets': completion_sets, 'exhaustive_sets': exhaustive_sets}
    timings, peaks = {k: [] for k in functions}, {k: [] for k in functions}
    for iteration in range(repeats):
        # Alternate execution order. Time and allocation measurements are separate.
        names = list(functions) if iteration % 2 == 0 else list(reversed(functions))
        for name in names:
            fn, sample = functions[name], deepcopy(graph)
            start = perf_counter_ns()
            result = fn(sample, target)
            timings[name].append(perf_counter_ns() - start)
            if set(result) != set(expected):
                raise ValueError('Nondeterministic or incorrect benchmark result')
            tracemalloc.start()
            try:
                fn(deepcopy(graph), target)
                peaks[name].append(tracemalloc.get_traced_memory()[1])
            finally:
                tracemalloc.stop()
    import platform
    return {'schema_version': '1.0', 'graph_sha256': graph_digest(graph),
            'target': target, 'repeats': repeats, 'correctness_agreement': True,
            'python': platform.python_version(), 'platform': platform.platform(),
            'measurements': {k: {'elapsed_ns': timings[k],
                                 'median_elapsed_ns': median(timings[k]),
                                 'python_peak_bytes': peaks[k]} for k in functions},
            'status': 'local_measurements_not_external_validation',
            'limitations': ['Python allocations are not process RSS',
                           'Repeated timings are not independent external trials',
                           'Baseline limited to 16 open leaves']}


def review_comparison(rows):
    """Paired reviewer/case summaries; observations must be collected externally.

    Each pair requires equal graph digest, counterbalanced distinct order, and
    identical adjudicated issue IDs. Self-reported time is not independently verified.
    """
    groups = {}
    for row in rows:
        for key in ('reviewer_id', 'case_id', 'graph_sha256'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError('Reviewer, case and graph identity required')
        if len(row['graph_sha256']) != 64 or any(c not in '0123456789abcdef' for c in row['graph_sha256']):
            raise ValueError('Invalid graph digest')
        if row.get('condition') not in {'baseline', 'assisted'} or type(row.get('order')) is not int or row['order'] not in (1, 2):
            raise ValueError('Invalid review condition/order')
        seconds = row.get('seconds')
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0:
            raise ValueError('Positive finite review time required')
        for key in ('expected_issue_ids', 'found_issue_ids'):
            ids = row.get(key)
            if not isinstance(ids, list) or any(not isinstance(x, str) or not x.strip() for x in ids) or len(ids) != len(set(ids)):
                raise ValueError('Unique issue identifiers required')
        group = groups.setdefault((row['reviewer_id'], row['case_id']), {})
        if row['condition'] in group:
            raise ValueError('Duplicate review condition')
        group[row['condition']] = row
    if not groups:
        raise ValueError('No review observations')
    pairs = []
    for (reviewer, case), group in sorted(groups.items()):
        if set(group) != {'baseline', 'assisted'}:
            raise ValueError('Unmatched review observations')
        a, b = group['baseline'], group['assisted']
        if a['graph_sha256'] != b['graph_sha256'] or set(a['expected_issue_ids']) != set(b['expected_issue_ids']) or a['order'] == b['order']:
            raise ValueError('Pairs require same graph/truth and distinct order')
        scores = {}
        for label, row in group.items():
            truth, found = set(row['expected_issue_ids']), set(row['found_issue_ids'])
            scores[label] = {'seconds': row['seconds'], 'missed': sorted(truth-found),
                             'spurious': sorted(found-truth),
                             'recall': len(truth & found)/len(truth) if truth else None}
        pairs.append({'reviewer_id': reviewer, 'case_id': case, 'scores': scores,
                      'seconds_saved': a['seconds']-b['seconds']})
    return {'pairs': pairs, 'status': 'descriptive_observations_not_causal_evidence',
            'limitations': ['Review order and learning can confound paired results',
                           'Reviewer independence and adjudication require external verification']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--reviews', action='store_true')
    parser.add_argument('--repeats', type=int, default=5)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text())
        if args.reviews:
            report = review_comparison(data)
        else:
            report = {'review_packet': review_packet(data['graph'], data['target']),
                      'benchmark': benchmark(data['graph'], data['target'], args.repeats)}
        print(json.dumps(report, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
