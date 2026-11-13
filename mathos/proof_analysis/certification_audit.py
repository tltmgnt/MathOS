"""Independent finite-model checker. Certifies Boolean graph calculations only.

No mathematical claim is promoted by this checker. External claims and the
sufficiency of authored proof routes remain assumptions.
"""
import hashlib
import json
from itertools import combinations
from pathlib import Path
import random
from .gap_analysis import Claim, analyze, models


def canonical_graph(graph):
    return {k: {'label': c.label, 'state': c.state, 'routes': c.routes, 'note': c.note}
            for k, c in sorted(graph.items())}


def graph_hash(graph):
    return hashlib.sha256(json.dumps(canonical_graph(graph), sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def exhaustive_check(graph, target, completion_sets, max_open=16):
    """Compare certificate with direct Boolean evaluation on every leaf assignment.

    Does not call analyze(), minimal(), or its recursive obligation algorithm.
    """
    if target not in graph:
        raise ValueError('Unknown target')
    pending = set(graph)
    order = []
    while pending:
        ready = []
        for k in sorted(pending):
            c = graph[k]
            if c.state not in {'open', 'derived', 'established_external'}:
                raise ValueError('Unknown state')
            if c.state == 'derived' and (not c.routes or any(not r for r in c.routes)):
                raise ValueError('Empty derivation')
            if c.state != 'derived' and c.routes:
                raise ValueError('Leaf with derivation')
            deps = {d for r in c.routes for d in r}
            if not deps <= graph.keys():
                raise ValueError('Missing dependency')
            if not deps & pending:
                ready.append(k)
        if not ready:
            raise ValueError('Cycle')
        order.extend(ready)
        pending.difference_update(ready)
    leaves = sorted(k for k, c in graph.items() if c.state == 'open')
    if len(leaves) > max_open:
        raise ValueError('Exhaustive-check resource limit exceeded')
    supplied = [frozenset(s) for s in completion_sets]
    if any(not s <= set(leaves) for s in supplied):
        raise ValueError('Certificate contains a non-open claim')
    if len(set(supplied)) != len(supplied):
        raise ValueError('Duplicate certificate set')
    if any(a < b for a in supplied for b in supplied):
        raise ValueError('Nonminimal certificate set')
    checked = 0
    for size in range(len(leaves) + 1):
        for selection in combinations(leaves, size):
            enabled = set(selection)
            truth = {}
            for k in order:
                c = graph[k]
                if c.state == 'open':
                    truth[k] = k in enabled
                elif c.state == 'established_external':
                    truth[k] = True
                else:
                    truth[k] = any(all(truth[d] for d in route) for route in c.routes)
            claimed = any(s <= enabled for s in supplied)
            if truth[target] != claimed:
                raise ValueError('Certificate disagrees with graph on assignment ' + repr(selection))
            checked += 1
    return {'verified_scope': 'Boolean completion-set calculation only',
            'assignments_checked': checked, 'graph_sha256': graph_hash(graph)}


def regression(seed=173, cases=1000):
    rng = random.Random(seed)
    assignments = 0
    for _ in range(cases):
        g = {f'x{i}': Claim(f'x{i}', 'open') for i in range(rng.randint(1, 6))}
        g['external'] = Claim('externally assumed', 'established_external')
        for j in range(rng.randint(1, 7)):
            keys = list(g)
            routes = tuple(tuple(rng.sample(keys, rng.randint(1, min(3, len(keys)))))
                           for _ in range(rng.randint(1, 3)))
            target = f'd{j}'
            g[target] = Claim(target, 'derived', routes)
        result = analyze(g, target)
        assignments += exhaustive_check(g, target, result['minimal_completion_sets'])['assignments_checked']
    return {'seed': seed, 'graphs_checked': cases, 'assignments_checked': assignments}


def main(output_dir="."):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checks = {}
    for name, graph in models().items():
        result = analyze(graph, 'target')
        checks[name] = exhaustive_check(graph, 'target', result['minimal_completion_sets'])
    report = {
        'overall_mathematical_certification': 'NOT_CERTIFIED',
        'rating': 'No 5/5 rating awarded; no calibrated rating benchmark exists here.',
        'gates': {
            'finite_graph_certificate_checks': 'PASS',
            'seeded_cross_implementation_regression': 'PASS',
            'precise_formalization_of_all_mathematical_claims': 'NOT_MET',
            'all_mathematical_dependencies_proved': 'NOT_MET',
            'proof_assistant_kernel_check': 'NOT_RUN_NO_TOOLCHAIN',
            'independent_external_audit': 'NOT_PERFORMED'},
        'trusted_assumptions': [
            'Authored dependency routes are mathematically sufficient (not verified).',
            'External background claims are accepted as supplied (not proof checked).',
            'Python interpreter, host arithmetic and both checker implementations behave correctly.',
            'SHA-256 provides content identification, not source authenticity or proof.'],
        'graph_checks': checks,
        'regression': regression(),
        'new_millennium_proofs': 0}
    (output_dir / 'certification_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
