"""REX-009: exact bounded structural planning for finite relational elimination.
Host reference, not a physical compiler. Exponential subset DP is intentional.
"""
from dataclasses import dataclass
from functools import lru_cache
from math import prod

if __package__:
    from .finite_relational_elimination import Solver, State
else:
    from finite_relational_elimination import Solver, State


@dataclass(frozen=True)
class Step:
    variable: str
    scope: tuple[str, ...]
    outgoing_scope: tuple[str, ...]
    candidates: int
    outgoing_bound: int
    batches: int


@dataclass(frozen=True)
class Plan:
    order: tuple[str, ...]
    steps: tuple[Step, ...]
    peak_candidates: int
    total_candidates: int
    peak_bag_width: int
    peak_outgoing_bound: int
    batches: int
    cap: int


class Planner:
    def __init__(self, solver: Solver, state: State, *, retain=(), cap=1,
                 max_width=None, max_outgoing=None, max_candidates=None):
        solver._validate(state)
        self.solver, self.state = solver, state
        self.names = state.order
        self.n = len(self.names)
        self.sizes = tuple(len(solver.domains[v]) for v in self.names)
        retain = tuple(retain)
        if len(set(retain)) != len(retain) or not set(retain) <= set(self.names):
            raise ValueError('retain must contain distinct active variables')
        self.target = sum(1 << i for i, v in enumerate(self.names) if v not in retain)
        for x in (cap, max_width, max_outgoing, max_candidates):
            if x is not None and (type(x) is not int or x < 0):
                raise ValueError('limits must be nonnegative integers')
        if cap is None or cap < 1:
            raise ValueError('cap must be positive')
        self.cap, self.max_width = cap, max_width
        self.max_outgoing, self.max_candidates = max_outgoing, max_candidates
        g = [0] * self.n
        for f in state.factors:
            mask = sum(1 << self.names.index(v) for v in f.scope)
            for i in self.indices(mask):
                g[i] |= mask ^ (1 << i)
        self.initial = tuple(g)
        # Per-instance cache; retained coordinates never enter the eliminated mask.
        self.graph = lru_cache(None)(self._graph)

    @staticmethod
    def indices(mask):
        while mask:
            bit = mask & -mask
            yield bit.bit_length() - 1
            mask ^= bit

    def _graph(self, mask):
        if not mask:
            return self.initial
        bit = mask & -mask
        i = bit.bit_length() - 1
        g = list(self.graph(mask ^ bit))
        neighbors = g[i]
        for j in self.indices(neighbors):
            g[j] = (g[j] | (neighbors ^ (1 << j))) & ~bit
        g[i] = 0
        return tuple(g)

    def step(self, mask, i):
        nbr = self.graph(mask)[i]
        bag = nbr | (1 << i)
        scope = tuple(self.names[j] for j in self.indices(bag))
        outgoing = tuple(self.names[j] for j in self.indices(nbr))
        C = prod(self.sizes[j] for j in self.indices(bag))
        U = prod(self.sizes[j] for j in self.indices(nbr))
        return Step(self.names[i], scope, outgoing, C, U, (C + self.cap - 1)//self.cap)

    def allowed(self, step):
        return all(limit is None or value <= limit for value, limit in (
            (len(step.scope), self.max_width), (step.outgoing_bound, self.max_outgoing),
            (step.candidates, self.max_candidates)))

    def certificate(self, order):
        order = tuple(order)
        expected = tuple(self.names[i] for i in self.indices(self.target))
        if len(order) != len(expected) or set(order) != set(expected):
            raise ValueError('order must eliminate exactly the requested variables')
        mask, steps = 0, []
        for v in order:
            i = self.names.index(v)
            step = self.step(mask, i)
            if not self.allowed(step):
                return None
            steps.append(step)
            mask |= 1 << i
        return Plan(order, tuple(steps), max((s.candidates for s in steps), default=0),
                    sum(s.candidates for s in steps), max((len(s.scope) for s in steps), default=0),
                    max((s.outgoing_bound for s in steps), default=0), sum(s.batches for s in steps), self.cap)

    def exact(self, *, max_eliminated=12):
        """Minimize (peak candidates, total candidates, original-index order).

        None means no order meets structural limits, NOT unsatisfiable.
        Two passes avoid an invalid lexicographic one-best-prefix recurrence.
        """
        if self.target.bit_count() > max_eliminated:
            raise ValueError('exact subset search exceeds authorized variable limit')

        @lru_cache(None)
        def peak(mask):
            if mask == self.target:
                return 0
            best = None
            for i in self.indices(self.target & ~mask):
                s = self.step(mask, i)
                if not self.allowed(s):
                    continue
                tail = peak(mask | (1 << i))
                if tail is not None:
                    val = max(s.candidates, tail)
                    best = val if best is None else min(best, val)
            return best

        threshold = peak(0)
        if threshold is None:
            return None

        @lru_cache(None)
        def total(mask):
            if mask == self.target:
                return (0, ())
            best = None
            for i in self.indices(self.target & ~mask):
                s = self.step(mask, i)
                if not self.allowed(s) or s.candidates > threshold:
                    continue
                tail = total(mask | (1 << i))
                if tail is not None:
                    val = (s.candidates + tail[0], (i,) + tail[1])
                    best = val if best is None else min(best, val)
            return best

        result = total(0)
        assert result is not None
        plan = self.certificate(self.names[i] for i in result[1])
        assert (plan.peak_candidates, plan.total_candidates) == (threshold, result[0])
        return plan

    def greedy(self):
        mask, order = 0, []
        while mask != self.target:
            choices = []
            for i in self.indices(self.target & ~mask):
                s = self.step(mask, i)
                if self.allowed(s):
                    choices.append((s.candidates, s.outgoing_bound, len(s.scope), i))
            if not choices:
                return None
            i = min(choices)[-1]
            order.append(self.names[i])
            mask |= 1 << i
        return self.certificate(order)

    def execute(self, plan):
        """Replay certificate against the actual reference stage implementation."""
        if plan is None or plan != self.certificate(plan.order):
            raise ValueError('invalid plan certificate')
        solver = Solver(self.solver.domains, batch_size=self.cap)
        state, traces = self.state, []
        for s in plan.steps:
            state, t = solver.stage(state, s.variable)
            assert (t.candidate_scope, t.outgoing_scope, t.candidate_count) == (s.scope, s.outgoing_scope, s.candidates)
            assert len(t.outgoing_rows) <= s.outgoing_bound
            traces.append(t)
        return state, tuple(traces)
