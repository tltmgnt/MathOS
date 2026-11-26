"""RE-X: bidirectional authored proof-route analysis, not theorem proving."""
from fractions import Fraction
from itertools import product
from mathos.proof_analysis.gap_analysis import Claim, analyze


def inspect_routes(graph, target):
    """Compute forward closure and reverse residual routes without editing claims."""
    reference = analyze(graph, target)  # validates the entire dependency DAG
    known = {k for k, c in graph.items() if c.state == 'established_external'}
    layers = [sorted(known)]
    while True:
        new = {k for k, c in graph.items() if k not in known and
               c.state == 'derived' and any(set(r) <= known for r in c.routes)}
        if not new:
            break
        layers.append(sorted(new))
        known.update(new)

    def minimal(sets):
        unique = set(sets)
        return sorted((s for s in unique if not any(t < s for t in unique)),
                      key=lambda s: (len(s), sorted(s)))

    memo = {}

    def combine(route):
        return minimal(frozenset().union(*items)
                       for items in product(*(reverse(k) for k in route)))

    def reverse(k):
        if k not in memo:
            c = graph[k]
            if k in known:
                memo[k] = [frozenset()]
            elif c.state == 'open':
                memo[k] = [frozenset([k])]
            else:
                memo[k] = minimal(s for r in c.routes for s in combine(r))
        return memo[k]

    sets = reverse(target)
    residuals = [sorted(s) for s in sets]
    if residuals != reference['minimal_completion_sets']:
        raise AssertionError('Forward/backward gap mismatch with TGA')
    closed = target in known
    if closed != (frozenset() in sets):
        raise AssertionError('Closure mismatch')
    frontier = sorted(set().union(*sets))
    common = sorted(set.intersection(*(set(s) for s in sets)))
    return {
        'target': target, 'status': reference['status'],
        'scope': 'AUTHORED_DEPENDENCIES_NOT_PROOF',
        'forward_layers': layers, 'forward_closure': sorted(known),
        'minimal_completion_sets': residuals,
        'common_to_all_modeled_routes': common, 'research_frontier': frontier,
        'direct_routes': [{'prerequisites': list(r),
                           'residuals': [sorted(s) for s in combine(r)]}
                          for r in graph[target].routes],
    }


def authorize_one(report, authorized_costs, budget):
    """Select at most one explicitly authorized open task; never change a claim.

    Costs and budget are integer user-defined effort units, not probabilities.
    Coverage per effort is a scheduling heuristic, not mathematical merit.
    """
    if type(budget) is not int or budget < 0:
        raise ValueError('Budget must be a nonnegative integer')
    if any(type(v) is not int or v <= 0 for v in authorized_costs.values()):
        raise ValueError('Costs must be positive integers')
    sets = report['minimal_completion_sets']
    if [] in sets:
        return {'decision': 'PRESERVE', 'task': None, 'spent': 0}
    candidates = []
    for k in report['research_frontier']:
        if k in authorized_costs and authorized_costs[k] <= budget:
            cost = authorized_costs[k]
            coverage = sum(k in s for s in sets)
            candidates.append((-Fraction(coverage, cost), cost, k, coverage))
    if not candidates:
        return {'decision': 'STOP_NO_AUTHORIZED_AFFORDABLE_TASK', 'task': None, 'spent': 0}
    _, cost, k, coverage = min(candidates)
    return {'decision': 'ADVANCE_ONE_BOUNDED_TASK', 'task': k,
            'reserved_effort': cost, 'modeled_routes_touched': coverage,
            'spent': 0, 'requires_new_evidence': True}


def self_test():
    """Exhaustive truth-assignment controls on seeded small authored DAGs."""
    from random import Random
    rng = Random(0x524558)
    counts = {'graphs': 0, 'hypothetical_assignments': 0, 'rejected_graphs': 0,
              'governance_checks': 0}
    for _ in range(80):
        g = {str(i): Claim(str(i), 'open' if i else 'established_external') for i in range(6)}
        for i in range(6, 10):
            routes = tuple(tuple(sorted(rng.sample(list(g), rng.randint(1, 3))))
                           for _ in range(rng.randint(1, 3)))
            g[str(i)] = Claim(str(i), 'derived', routes)
        before = dict(g)
        result = inspect_routes(g, '9')
        good = []
        for bits in product((0, 1), repeat=5):
            selected = frozenset(str(i+1) for i, b in enumerate(bits) if b)
            known = {'0'} | set(selected)
            for i in range(6, 10):
                if any(set(r) <= known for r in g[str(i)].routes):
                    known.add(str(i))
            if '9' in known:
                good.append(selected)
            predicts = any(set(r) <= selected for r in result['minimal_completion_sets'])
            assert predicts == ('9' in known)
            counts['hypothetical_assignments'] += 1
        expected = sorted((s for s in good if not any(t < s for t in good)),
                          key=lambda s: (len(s), sorted(s)))
        assert result['minimal_completion_sets'] == [sorted(s) for s in expected]
        assert g == before
        counts['graphs'] += 1
    for g in ({'a': Claim('a', 'derived', (('a',),))},
              {'a': Claim('a', 'derived', (('missing',),))},
              {'a': Claim('a', 'open', (('a',),))},
              {'a': Claim('a', 'derived', ())}):
        try:
            inspect_routes(g, 'a')
        except ValueError:
            counts['rejected_graphs'] += 1
        else:
            raise AssertionError('Invalid graph admitted')
    g = {k: Claim(k, 'open') for k in ('a', 'b', 'c')}
    g['t'] = Claim('t', 'derived', (('a', 'b'), ('a', 'c')))
    r = inspect_routes(g, 't')
    assert r['common_to_all_modeled_routes'] == ['a']
    assert authorize_one(r, {'a': 2, 'b': 1, 'c': 1}, 2)['task'] == 'b'
    assert authorize_one(r, {'a': 1}, 1)['task'] == 'a'
    assert authorize_one(r, {}, 10)['task'] is None
    assert authorize_one(r, {'a': 2}, 1)['task'] is None
    assert authorize_one(r, {'unknown': 1}, 10)['task'] is None
    assert authorize_one(inspect_routes({'a': Claim('a', 'established_external')}, 'a'), {}, 0)['decision'] == 'PRESERVE'
    assert g['a'].state == 'open'
    counts['governance_checks'] = 8
    return counts


if __name__ == '__main__':
    import json
    print(json.dumps(self_test(), sort_keys=True))
