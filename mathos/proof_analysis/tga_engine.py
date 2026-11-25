"""Exact, bounded finite AND/OR gap analysis. Authored routes are assumptions."""
from dataclasses import dataclass
from heapq import heapify, heappop, heappush


class ResourceLimitError(RuntimeError):
    """No exact result was returned; never interpret as a closed proof."""


@dataclass(frozen=True)
class Limits:
    max_nodes: int = 20_000
    max_edges: int = 100_000
    max_frontier: int = 10_000
    max_retained_sets: int = 100_000
    max_work: int = 5_000_000

    def __post_init__(self):
        for value in vars(self).values():
            if type(value) is not int or value < 1:
                raise ValueError("limits must be positive integers")


class Budget:
    def __init__(self, limits):
        self.limits = limits
        self.work = 0
        self.peak_frontier = 0

    def tick(self, amount=1):
        self.work += amount
        if self.work > self.limits.max_work:
            raise ResourceLimitError("TGA work limit exceeded")

    def insert(self, frontier, candidate):
        # Incremental inclusion pruning is exact: union is monotone.
        # Compare before modifying so exhaustion cannot leak a partial result.
        self.tick()
        dominated = []
        for old in frontier:
            self.tick()
            if old <= candidate:
                return
            if candidate < old:
                dominated.append(old)
        if len(frontier) - len(dominated) + 1 > self.limits.max_frontier:
            raise ResourceLimitError("TGA frontier limit exceeded")
        frontier.difference_update(dominated)
        frontier.add(candidate)
        self.peak_frontier = max(self.peak_frontier, len(frontier))


def topology(graph, target, budget):
    """Validate the whole graph, even disconnected or dominated alternatives."""
    if len(graph) > budget.limits.max_nodes:
        raise ResourceLimitError("TGA node limit exceeded")
    if target not in graph:
        raise ValueError("Unknown target: " + str(target))
    if any(not isinstance(key, str) or not key for key in graph):
        raise ValueError("Claim IDs must be nonempty strings")
    deps, successors = {}, {key: [] for key in graph}
    edges = 0
    for key, claim in graph.items():
        budget.tick()
        if claim.state not in {"open", "derived", "established_external"}:
            raise ValueError("Unknown state: " + str(claim.state))
        if claim.state == "derived" and (not claim.routes or any(not r for r in claim.routes)):
            raise ValueError("Derived claims need nonempty proof routes")
        if claim.state != "derived" and claim.routes:
            raise ValueError("Leaf states cannot carry proof routes")
        parents = set()
        for route in claim.routes:
            for parent in route:
                edges += 1
                if edges > budget.limits.max_edges:
                    raise ResourceLimitError("TGA edge limit exceeded")
                budget.tick()
                if parent not in graph:
                    raise ValueError("Missing dependency: " + str(parent))
                parents.add(parent)
        deps[key] = parents
        for parent in parents:
            successors[parent].append(key)
    degree = {key: len(parents) for key, parents in deps.items()}
    ready = [key for key in graph if not degree[key]]
    heapify(ready)
    order = []
    while ready:
        key = heappop(ready)
        order.append(key)
        for child in successors[key]:
            budget.tick()
            degree[child] -= 1
            if not degree[child]:
                heappush(ready, child)
    if len(order) != len(graph):
        raise ValueError("Dependency cycle")
    reachable, stack = set(), [target]
    while stack:
        key = stack.pop()
        if key not in reachable:
            reachable.add(key)
            stack.extend(deps[key])
    return [key for key in order if key in reachable]


def sorted_sets(frontier):
    return sorted((sorted(s) for s in frontier), key=lambda s: (len(s), s))


def ordered(frontier):
    return sorted(frontier, key=lambda s: (len(s), sorted(s)))


def solve(graph, target, *, limits=None):
    """Return exact legacy-shaped answer plus resource counters on success."""
    budget = Budget(limits if limits is not None else Limits())
    order = topology(graph, target, budget)
    memo = {}
    retained = 0
    for key in order:
        claim = graph[key]
        if claim.state == "open":
            frontier = {frozenset({key})}
        elif claim.state == "established_external":
            frontier = {frozenset()}
        else:
            frontier = set()
            for route in claim.routes:
                partial = {frozenset()}
                # Every prefix can be pruned before joining the next dependency.
                for dependency in dict.fromkeys(route):
                    joined = set()
                    for left in ordered(partial):
                        for right in ordered(memo[dependency]):
                            budget.tick()
                            budget.insert(joined, left | right)
                    partial = joined
                for candidate in ordered(partial):
                    budget.insert(frontier, candidate)
                if frozenset() in frontier:
                    break
        budget.peak_frontier = max(budget.peak_frontier, len(frontier))
        retained += len(frontier)
        if retained > budget.limits.max_retained_sets:
            raise ResourceLimitError("TGA retained-set limit exceeded")
        memo[key] = frontier
    sets = memo[target]
    result = {
        "target": target,
        "status": "EXTERNAL_RESULT_OR_ROUTE_CLOSED" if frozenset() in sets else "BLOCKED",
        "minimal_completion_sets": sorted_sets(sets),
        "common_to_all_modeled_routes": sorted(set.intersection(*(set(s) for s in sets))) if sets else [],
        "claims": {k: {"label": c.label, "state": c.state, "routes": c.routes, "note": c.note}
                   for k, c in graph.items()},
    }
    return result, {"work_units": budget.work, "peak_frontier_sets": budget.peak_frontier,
                    "retained_sets": retained, "reachable_nodes": len(order)}


def analyze_exact(graph, target, *, limits=None):
    return solve(graph, target, limits=limits)[0]


def minimal_blockers(completion_sets, *, limits=None):
    """Inclusion-minimal hitting sets: withholding these blocks all modeled routes."""
    budget = Budget(limits if limits is not None else Limits())
    frontier = {frozenset()}
    for route in completion_sets:
        if not route:
            return []  # An already closed modeled route cannot be blocked by open leaves.
        joined = set()
        for prior in ordered(frontier):
            if prior.intersection(route):
                budget.insert(joined, prior)
            else:
                for leaf in sorted(set(route)):
                    budget.insert(joined, prior | {leaf})
        frontier = joined
    return sorted_sets(frontier)
