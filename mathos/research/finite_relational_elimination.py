"""Finite Boolean relational elimination using sorted row streams.

Reference software model, not hardware. Python 3.10+; no dependencies.
Optional batch_size bounds candidate materialization, not outgoing relation size.
"""
from dataclasses import dataclass
from itertools import islice, product
from typing import Iterable, Mapping, Sequence

Row = tuple[int, ...]


@dataclass(frozen=True)
class Factor:
    scope: tuple[str, ...]
    rows: tuple[Row, ...]


@dataclass(frozen=True)
class State:
    order: tuple[str, ...]
    factors: tuple[Factor, ...]


@dataclass(frozen=True)
class StageTrace:
    eliminated: str
    candidate_scope: tuple[str, ...]
    candidate_count: int
    factor_matches: tuple[int, ...]
    joint_count: int
    outgoing_scope: tuple[str, ...]
    outgoing_rows: tuple[Row, ...]
    next_order: tuple[str, ...]


def sorted_unique(rows: Iterable[Row]) -> tuple[Row, ...]:
    result = []
    for row in sorted(rows):
        if not result or row != result[-1]:
            result.append(row)
    return tuple(result)


def project_row(row: Row, indices: Sequence[int]) -> Row:
    return tuple(row[i] for i in indices)


def attach_membership(candidates: tuple[Row, ...], scope: tuple[str, ...],
                      factor: Factor) -> tuple[bool, ...]:
    """Sort projected keys, merge sorted unique factor rows, scatter by ID."""
    indices = tuple(scope.index(v) for v in factor.scope)
    stream = sorted((project_row(row, indices), i)
                    for i, row in enumerate(candidates))
    flags = [False] * len(candidates)
    j = 0
    for key, row_id in stream:
        while j < len(factor.rows) and factor.rows[j] < key:
            j += 1
        flags[row_id] = j < len(factor.rows) and factor.rows[j] == key
    return tuple(flags)


def joint_membership(candidates: tuple[Row, ...], scope: tuple[str, ...],
                     factors: Sequence[Factor]) -> tuple[tuple[Row, ...], tuple[int, ...]]:
    """Conjoin at full candidate identity BEFORE existential projection."""
    joint = [True] * len(candidates)
    counts = []
    for factor in factors:
        flags = attach_membership(candidates, scope, factor)
        counts.append(sum(flags))
        joint = [a and b for a, b in zip(joint, flags)]
    return tuple(row for row, keep in zip(candidates, joint) if keep), tuple(counts)


class Solver:
    def __init__(self, domains: Mapping[str, Iterable[int]], *,
                 batch_size: int | None = None):
        # Validate before sorting or deduplicating (e.g. 1 and 1.0 compare equal).
        self.domains = {}
        for v, values in domains.items():
            if not isinstance(v, str):
                raise ValueError("variable names must be strings")
            values = tuple(values)
            if any(not isinstance(x, int) for x in values):
                raise ValueError("domain values must be integers")
            self.domains[v] = tuple(sorted(set(values)))
        if batch_size is not None and (type(batch_size) is not int or batch_size < 1):
            raise ValueError("batch_size must be a positive integer or None")
        self.batch_size = batch_size

    def _check_order(self, order: tuple[str, ...], expected: Iterable[str]) -> None:
        if (any(not isinstance(v, str) for v in order)
                or len(set(order)) != len(order) or set(order) != set(expected)):
            raise ValueError("order must be a permutation of the expected variables")

    def _normalize(self, factor: Factor, order: tuple[str, ...]) -> Factor:
        scope = tuple(factor.scope)
        if (any(not isinstance(v, str) for v in scope)
                or len(set(scope)) != len(scope) or not set(scope) <= set(order)):
            raise ValueError("factor scope must contain distinct active variables")
        new_scope = tuple(v for v in order if v in scope)
        indices = tuple(scope.index(v) for v in new_scope)
        rows = []
        for row in factor.rows:
            if len(row) != len(scope):
                raise ValueError("row arity does not match factor scope")
            if any(not isinstance(x, int) or x not in self.domains[v]
                   for v, x in zip(scope, row)):
                raise ValueError("factor row contains value outside integer domain")
            rows.append(project_row(row, indices))
        return Factor(new_scope, sorted_unique(rows))

    def initial_state(self, factors: Iterable[Factor],
                      order: Iterable[str] | None = None) -> State:
        order = tuple(self.domains if order is None else order)
        self._check_order(order, self.domains)
        return State(order, tuple(self._normalize(f, order) for f in factors))

    def _validate(self, state: State) -> None:
        self._check_order(state.order, state.order)
        if not set(state.order) <= set(self.domains):
            raise ValueError("unknown active variable")
        for factor in state.factors:
            if factor != self._normalize(factor, state.order):
                raise ValueError("state is not normalized")

    def _candidates(self, scope: tuple[str, ...]) -> tuple[Row, ...]:
        return tuple(product(*(self.domains[v] for v in scope)))

    def _batches(self, scope: tuple[str, ...]):
        if self.batch_size is None:
            yield self._candidates(scope)
            return
        stream = product(*(self.domains[v] for v in scope))
        while batch := tuple(islice(stream, self.batch_size)):
            yield batch

    def stage(self, state: State, variable: str,
              next_order: Iterable[str] | None = None) -> tuple[State, StageTrace]:
        self._validate(state)
        if variable not in state.order:
            raise ValueError("eliminated variable must be active")
        remaining = tuple(v for v in state.order if v != variable)
        new_order = tuple(remaining if next_order is None else next_order)
        self._check_order(new_order, remaining)
        bucket = tuple(f for f in state.factors if variable in f.scope)
        untouched = tuple(f for f in state.factors if variable not in f.scope)
        variables = {variable} | {v for f in bucket for v in f.scope}
        scope = tuple(v for v in state.order if v in variables)
        outgoing_scope = tuple(v for v in new_order if v in variables)
        indices = tuple(scope.index(v) for v in outgoing_scope)
        candidate_count = joint_count = 0
        counts = [0] * len(bucket)
        outgoing_rows = set()
        for candidates in self._batches(scope):
            joint, matches = joint_membership(candidates, scope, bucket)
            candidate_count += len(candidates)
            joint_count += len(joint)
            counts = [a + b for a, b in zip(counts, matches)]
            outgoing_rows.update(project_row(r, indices) for r in joint)
        outgoing = Factor(outgoing_scope, sorted_unique(outgoing_rows))
        result = State(new_order, tuple(self._normalize(f, new_order)
                                        for f in untouched) + (outgoing,))
        self._validate(result)
        trace = StageTrace(variable, scope, candidate_count, tuple(counts), joint_count,
                           outgoing.scope, outgoing.rows, new_order)
        return result, trace

    def eliminate(self, state: State, variables: Iterable[str],
                  next_orders: Iterable[Iterable[str] | None] | None = None
                  ) -> tuple[State, tuple[StageTrace, ...]]:
        self._validate(state)
        variables = tuple(variables)
        orders = (None,) * len(variables) if next_orders is None else tuple(next_orders)
        if len(orders) != len(variables):
            raise ValueError("one optional next_order per elimination stage is required")
        if len(set(variables)) != len(variables) or not set(variables) <= set(state.order):
            raise ValueError("elimination variables must be distinct and active")
        traces = []
        for v, order in zip(variables, orders):
            state, trace = self.stage(state, v, order)
            traces.append(trace)
        return state, tuple(traces)

    def relation(self, state: State) -> Factor:
        """Materialize the remaining relation (possibly exponential output)."""
        self._validate(state)
        rows = []
        for candidates in self._batches(state.order):
            joint, _ = joint_membership(candidates, state.order, state.factors)
            rows.extend(joint)
        return Factor(state.order, tuple(rows))

    def solve(self, state: State, order: Iterable[str] | None = None
              ) -> tuple[bool, tuple[StageTrace, ...]]:
        order = tuple(state.order if order is None else order)
        self._check_order(order, state.order)
        final, traces = self.eliminate(state, order)
        return bool(self.relation(final).rows), traces


if __name__ == "__main__":
    solver = Solver({"k": [0], "a": [0, 1]})
    state = solver.initial_state([
        Factor(("k", "a"), ((0, 0),)),
        Factor(("k", "a"), ((0, 1),)),
    ])
    next_state, trace = solver.stage(state, "a")
    print("Conflicting witness example:")
    print(trace)
    print("Remaining relation:", solver.relation(next_state))
    print("Satisfiable:", solver.solve(state)[0])
