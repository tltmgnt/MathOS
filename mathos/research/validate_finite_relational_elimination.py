"""Independent finite truth-table oracle and optional REX physical bridge replay."""
import json
import random
import sys
import unittest
from itertools import permutations, product
from pathlib import Path

if __package__:
    from .finite_relational_elimination import Factor, Solver, State, attach_membership
else:
    from finite_relational_elimination import Factor, Solver, State, attach_membership


def oracle(domains, state):
    """Direct predicate evaluation, without using solver join/project routines."""
    rows = []
    for row in product(*(domains[v] for v in state.order)):
        assignment = dict(zip(state.order, row))
        if all(tuple(assignment[v] for v in f.scope) in f.rows for f in state.factors):
            rows.append(row)
    return tuple(rows)


class Validation(unittest.TestCase):
    def stage_check(self, solver, state, variable, order):
        expected = tuple(sorted({tuple(dict(zip(state.order, row))[v] for v in order)
                                 for row in oracle(solver.domains, state)}))
        out, trace = solver.stage(state, variable, order)
        self.assertEqual(solver.relation(out).rows, expected)
        bucket = [f for f in state.factors if variable in f.scope]
        bag = tuple(v for v in state.order if v == variable or any(v in f.scope for f in bucket))
        scope = tuple(v for v in order if v in bag)
        count = 0
        matches = [0] * len(bucket)
        joint = 0
        outgoing = set()
        for row in product(*(solver.domains[v] for v in bag)):
            a = dict(zip(bag, row))
            flags = [tuple(a[v] for v in f.scope) in f.rows for f in bucket]
            count += 1
            matches = [x + y for x, y in zip(matches, flags)]
            if all(flags):
                joint += 1
                outgoing.add(tuple(a[v] for v in scope))
        self.assertEqual((trace.candidate_scope, trace.candidate_count, trace.factor_matches,
                          trace.joint_count, trace.outgoing_scope, trace.outgoing_rows, trace.next_order),
                         (bag, count, tuple(matches), joint, scope, tuple(sorted(outgoing)), tuple(order)))
        return out, trace

    def test_conflicting_witness(self):
        s = Solver({'k': [0], 'a': [0, 1]}, batch_size=1)
        state = s.initial_state([Factor(('k', 'a'), ((0, 0),)), Factor(('k', 'a'), ((0, 1),))])
        out, trace = self.stage_check(s, state, 'a', ('k',))
        self.assertEqual((trace.factor_matches, trace.joint_count, trace.outgoing_rows), ((1, 1), 0, ()))
        self.assertFalse(s.solve(out)[0])

    def test_shared_witness_and_scatter(self):
        s = Solver({'a': [0, 1], 'k': [0, 1]})
        state = s.initial_state([Factor(('k', 'a'), ((0, 1), (1, 0), (0, 1))),
                                 Factor(('a',), ((1,),))])
        rows = ((1, 0), (0, 0), (0, 1), (1, 1))
        self.assertEqual(attach_membership(rows, state.order, state.factors[0]), (True, False, True, False))
        _, trace = self.stage_check(s, state, 'a', ('k',))
        self.assertEqual(trace.outgoing_rows, ((0,),))

    def test_reordering(self):
        s = Solver({'a': [0, 1], 'b': [-3, 7], 'c': [2, 8]}, batch_size=1)
        state = s.initial_state([Factor(('c', 'a'), ((8, 1),)), Factor(('a', 'b'), ((1, -3),)),
                                 Factor(('b', 'c'), ((-3, 8), (7, 2)))])
        out, trace = self.stage_check(s, state, 'a', ('c', 'b'))
        self.assertEqual(trace.outgoing_rows, ((8, -3),))
        self.assertEqual(out.factors[0], Factor(('c', 'b'), ((2, 7), (8, -3))))

    def test_exhaustive_factor_pairs(self):
        universe = tuple(product(range(2), repeat=2))
        for i, j in product(range(16), repeat=2):
            fs = [Factor(('a', 'b'), tuple(row for k, row in enumerate(universe) if mask >> k & 1))
                  for mask in (i, j)]
            for order in permutations(('a', 'b')):
                dense = Solver({'a': range(2), 'b': range(2)})
                batch = Solver(dense.domains, batch_size=1)
                state = dense.initial_state(fs)
                a, trace = self.stage_check(dense, state, order[0], order[1:])
                self.assertEqual(batch.stage(state, order[0], order[1:]), (a, trace))
                self.assertEqual(batch.solve(state, order), dense.solve(state, order))
                self.assertEqual(dense.solve(state, order)[0], bool(oracle(dense.domains, state)))

    def test_nullary_empty_domains(self):
        for da, db, truth in product(((), (0,), (0, 1)), ((), (2,)), (False, True)):
            for cap in (None, 1, 3):
                s = Solver({'a': da, 'b': db}, batch_size=cap)
                st = s.initial_state([Factor((), ((),) if truth else ())])
                out, trace = self.stage_check(s, st, 'a', ('b',))
                self.assertEqual(trace.outgoing_rows, ((),) if da else ())
                self.assertEqual(s.solve(out)[0], bool(da and db and truth))
        for truth in (False, True):
            s = Solver({}, batch_size=1)
            self.assertEqual(s.solve(s.initial_state([Factor((), ((),) if truth else ())]))[0], truth)
        for cap in (None, 1):
            s = Solver({'a': [], 'b': [0]}, batch_size=cap)
            _, trace = self.stage_check(s, s.initial_state([Factor(('a', 'b'), ())]), 'a', ('b',))
            self.assertEqual((trace.candidate_count, trace.factor_matches), (0, (0,)))

    def test_randomized_multistage(self):
        rng = random.Random(0x52455808)
        for _ in range(500):
            names = tuple('abcd'[:rng.randrange(5)])
            domains = {v: tuple(sorted(rng.sample([-7, 0, 2, 11], rng.randrange(4)))) for v in names}
            fs = []
            for _ in range(rng.randrange(7)):
                scope = tuple(rng.sample(names, rng.randrange(len(names)+1)))
                rows = tuple(row for row in product(*(domains[v] for v in scope)) if rng.randrange(2))
                fs.append(Factor(scope, rows + rows[:1]))
            dense = Solver(domains)
            batch = Solver(domains, batch_size=rng.randrange(1, 5))
            st = dense.initial_state(fs, rng.sample(names, len(names)))
            sat = bool(oracle(dense.domains, st))
            elimination = rng.sample(names, len(names))
            self.assertEqual(batch.solve(st, elimination), dense.solve(st, elimination))
            for v in elimination:
                order = rng.sample([w for w in st.order if w != v], len(st.order)-1)
                out, trace = self.stage_check(dense, st, v, order)
                self.assertEqual(batch.stage(st, v, order), (out, trace))
                st = out
            self.assertEqual(bool(dense.relation(st).rows), sat)

    def test_invalid_state(self):
        s = Solver({'a': [0, 1], 'b': [0, 1]})
        for f in (Factor(('a', 'a'), ()), Factor(('x',), ()), Factor(('a',), ((2,),)),
                  Factor(('a',), ((0, 1),)), Factor(('a',), ((0.0,),)), Factor((), ((1,),))):
            with self.assertRaises(ValueError):
                s.initial_state([f])
        for st in (State(('a', 'a'), ()), State(('x',), ()), State(('a',), (Factor(('a',), ((1,), (0,))),)),
                   State(('a',), (Factor(('a',), ((0,), (0,))),))):
            with self.assertRaises(ValueError):
                s.relation(st)
        for domains in ({'a': [1, 1.0]}, {'a': [1, '2']}, {1: [0]}):
            with self.assertRaises(ValueError):
                Solver(domains)
        for cap in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                Solver({'a': [0]}, batch_size=cap)
        with self.assertRaises(ValueError):
            s.eliminate(s.initial_state([]), ['a', 'a'])
        with self.assertRaises(ValueError):
            s.stage(s.initial_state([]), 'a', ('a',))

    def test_explicit_stage_composition(self):
        s = Solver({'a': [0, 1], 'b': [0, 1], 'c': [0, 1]}, batch_size=2)
        st = s.initial_state([Factor(('a', 'b'), ((0, 0), (1, 1))),
                              Factor(('b', 'c'), ((0, 1), (1, 0)))])
        for order in permutations(st.order):
            orders = [tuple(reversed([v for v in st.order if v not in order[:i+1]])) for i in range(3)]
            final, traces = s.eliminate(st, order, orders)
            now = st
            for v, next_order, trace in zip(order, orders, traces):
                now, actual = self.stage_check(s, now, v, next_order)
                self.assertEqual(actual, trace)
            self.assertEqual(now, final)
            self.assertEqual(s.relation(final).rows, ((),))


def bridge(path):
    data = json.loads(Path(path).read_text())
    for case in data['cases']:
        domains = case['domains']
        s = Solver(domains, batch_size=case['cap'])
        state = s.initial_state([Factor(tuple(f['scope']), tuple(map(tuple, f['rows']))) for f in case['factors']], case['order'])
        _, trace = s.stage(state, case['eliminate'], case['nextOrder'])
        assert trace.outgoing_scope == tuple(case['nextOrder'])
        assert trace.outgoing_rows == tuple(map(tuple, case['outgoingRows'])), case['name']
        expected = {}
        for row in oracle(s.domains, state):
            a = dict(zip(state.order, row))
            q = tuple(a[v] for v in case['nextOrder'])
            expected[q] = min(expected.get(q, a[case['eliminate']]), a[case['eliminate']])
        assert sorted(expected.items()) == [(tuple(q), a) for q, a in case['witnesses']], case['name']
    print('REX_BRIDGE_OK cases=' + str(len(data['cases'])), flush=True)


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else None
    result = unittest.main(argv=[sys.argv[0]], verbosity=2, exit=False).result
    if not result.wasSuccessful():
        sys.exit(1)
    if path:
        bridge(path)
    print('FINITE_RELATIONAL_ELIMINATION_OK suites=8 pairs=256 orders=512 randomized=500')
