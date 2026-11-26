"""Experimental exact finite-domain min-sum elimination; not a tape machine.
Run with --self-test for deterministic differential checks. No dependencies.
"""
import argparse
import itertools
import json
import math
import random
from collections import Counter


def assignments(domains, scope):
    return itertools.product(*(range(domains[v]) for v in scope))


def validate(domains, factors):
    if any(type(d) is not int or d < 1 for d in domains.values()):
        raise ValueError('domain sizes must be positive integers')
    for scope, table in factors:
        if len(set(scope)) != len(scope) or any(v not in domains for v in scope):
            raise ValueError('invalid factor scope')
        for key, cost in table.items():
            if (len(key) != len(scope) or any(type(x) is not int or not 0 <= x < domains[v]
                                               for v, x in zip(scope, key))
                    or type(cost) is not int):
                raise ValueError('invalid factor entry')


def score(factors, witness):
    total = 0
    for scope, table in factors:
        cost = table.get(tuple(witness[v] for v in scope))
        if cost is None:
            return None  # absent tuple is forbidden
        total += cost
    return total


def min_fill(domains, factors):
    graph = {v: set() for v in domains}
    for scope, _ in factors:
        for v, u in itertools.combinations(scope, 2):
            graph[v].add(u)
            graph[u].add(v)
    order = []
    rank = {v: i for i, v in enumerate(domains)}
    while graph:
        def key(v):
            nbr = graph[v]
            fill = sum(b not in graph[a] for a, b in itertools.combinations(nbr, 2))
            return fill, math.prod(domains[u] for u in nbr) * domains[v], rank[v]
        v = min(graph, key=key)
        nbr = graph.pop(v)
        for a, b in itertools.combinations(nbr, 2):
            graph[a].add(b)
            graph[b].add(a)
        for u in nbr:
            graph[u].remove(v)
        order.append(v)
    return order


def recover(trace):
    """Recover one witness from JSON-round-trippable elimination records."""
    witness = {}
    for v, boundary, rows in reversed(trace):
        target = [witness[u] for u in boundary]
        witness[v] = next(value for row, value in rows if row == target)
    return witness


def solve(domains, factors, order=None):
    """Exact optimum or None (infeasible). Variable IDs must be strings.

    Factors are (scope tuple, {assignment tuple: integer cost}); missing rows
    are forbidden. The trace stores a minimizing value per feasible separator
    assignment. Counts are logical enumerations, not physical transitions.
    """
    if any(not isinstance(v, str) for v in domains):
        raise ValueError('variable IDs must be strings')
    factors = [(tuple(s), dict(t)) for s, t in factors]
    validate(domains, factors)
    order = min_fill(domains, factors) if order is None else list(order)
    if len(order) != len(domains) or set(order) != set(domains):
        raise ValueError('order must be a permutation of variables')
    active, trace = factors[:], []
    width = visits = 0
    for v in order:
        bucket = [(s, t) for s, t in active if v in s]
        active = [(s, t) for s, t in active if v not in s]
        boundary = tuple(sorted({u for s, _ in bucket for u in s if u != v}))
        width = max(width, len(boundary))
        table, rows = {}, []
        for row in assignments(domains, boundary):
            a = dict(zip(boundary, row))
            best = arg = None
            for x in range(domains[v]):
                a[v] = x
                visits += 1
                cost = score(bucket, a)
                if cost is not None and (best is None or cost < best):
                    best, arg = cost, x
            if best is not None:
                table[row] = best
                rows.append([list(row), arg])
        active.append((boundary, table))
        trace.append([v, list(boundary), rows])
    optimum = score(active, {})
    witness = None if optimum is None else recover(trace)
    return dict(optimum=optimum, witness=witness, trace=trace,
                induced_width=width, assignments_evaluated=visits, order=order)


def brute(domains, factors):
    best = None
    variables = tuple(domains)
    for row in itertools.product(*(range(domains[v]) for v in variables)):
        candidate = dict(zip(variables, row))
        try:
            cost = sum(table[tuple(candidate[v] for v in scope)] for scope, table in factors)
        except KeyError:
            continue
        if best is None or cost < best:
            best = cost
    return best


def self_test():
    rng = random.Random(38017)
    # Each case specifies a constraint hypergraph, not a graph of machine states.
    families = {
        'isolated': (4, [(0,), (1,)], None),
        'chain': (6, [(i, i+1) for i in range(5)], None),
        'single_separator': (6, [(0, i) for i in range(1, 6)], [1,2,3,4,5,0]),
        'joint_branching': (6, [(0,1,i) for i in range(2,6)], [2,3,4,5,0,1]),
        'wide_separator': (7, [(0,1,2,3,i) for i in range(4,7)], [4,5,6,0,1,2,3]),
        'heterogeneous_nested': (7, [(0,1,2),(1,2,3),(1,4),(3,5),(4,6)], [5,6,3,4,2,1,0]),
        'cycle': (6, [(i,(i+1)%6) for i in range(6)], None),
        'grid': (9, [(i,i+1) for i in range(9) if i%3 != 2] + [(i,i+3) for i in range(6)], None),
        'dense': (6, list(itertools.combinations(range(6),2)), None),
        'hypergraph': (7, [(0,1,2,3),(2,3,4,5),(0,4,6)], None),
    }
    counts = Counter()
    max_width = {}
    feasibility = Counter()
    visits = 0

    def check(name, domains, factors, order=None):
        nonlocal visits
        result = solve(domains, factors, order)
        expected = brute(domains, factors)
        assert result['optimum'] == expected, (name, result, expected)
        if expected is None:
            assert result['witness'] is None
            feasibility['infeasible'] += 1
        else:
            witness = recover(json.loads(json.dumps(result['trace'])))
            assert set(witness) == set(domains)
            assert all(0 <= x < domains[v] for v, x in witness.items())
            assert witness == result['witness'] and score(factors, witness) == expected
            feasibility['feasible'] += 1
        counts[name] += 1
        visits += result['assignments_evaluated']
        max_width[name] = max(max_width.get(name, 0), result['induced_width'])

    for name, (n, scopes, order) in families.items():
        for trial in range(24):
            domains = {str(i): rng.randint(2,3) for i in range(n)}
            target = {v: rng.randrange(d) for v, d in domains.items()}
            factors = []
            for s in scopes:
                s = tuple(map(str, s))
                table = {a: rng.randint(-4,8) for a in assignments(domains,s) if rng.random() < .75}
                table.setdefault(tuple(target[v] for v in s), 0)
                factors.append((s, table))
            if trial % 4 == 0:
                factors += [(('0',), {})]  # explicit contradictory constraint
            check(name, domains, factors, None if order is None else list(map(str,order)))
            if name == 'heterogeneous_nested':
                s = ('0','5','6')
                added = (s, {a: rng.randint(-4,8) for a in assignments(domains,s) if sum(a)%2 == 0})
                check('dynamic_full_recompute', domains, factors+[added])
                check('dynamic_full_recompute', domains, factors[1:])
    check('boundary_cases', {}, [])
    check('boundary_cases', {}, [((), {})])
    check('boundary_cases', {}, [((), {(): -9})])
    check('boundary_cases', {'x': 1}, [])
    unequal = {(0,1): 0, (1,0): 0}
    check('adversarial', {'a':2,'b':2,'c':2},
          [(('a','b'), unequal), (('b','c'), unequal), (('c','a'), unequal)])
    check('adversarial', {'x':2}, [(('x',), {(0,):0}), (('x',), {(1,):0})])
    check('adversarial', {'a':2,'b':2,'c':2},
          [(('a','b'), {(0,0):0,(1,1):0}), (('b','c'), unequal),
           (('a','c'), {(0,0):0,(1,1):0})])
    assert max_width['wide_separator'] >= 4
    assert max_width['dense'] == 5
    print(json.dumps(dict(cases=dict(counts), total=sum(counts.values()),
                          feasibility=dict(feasibility), max_induced_width=max_width,
                          logical_assignments_evaluated=visits,
                          scope='Python reference only; no physical tape or competitor benchmark'), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true', required=True)
    parser.parse_args()
    self_test()
