"""Scoped CNF structural research kernel; no claim about unrestricted P vs NP."""
from dataclasses import dataclass
from itertools import combinations, product
import time


class Exhausted(RuntimeError):
    """A configured research resource limit was reached; never an UNSAT result."""


@dataclass
class Budget:
    seconds: float = 10.0
    max_steps: int = 2_000_000
    max_cells: int = 100_000

    def __post_init__(self):
        import math
        if (not isinstance(self.seconds, (int, float)) or
                not math.isfinite(self.seconds) or self.seconds <= 0 or
                type(self.max_steps) is not int or self.max_steps < 1 or
                type(self.max_cells) is not int or self.max_cells < 1):
            raise ValueError("positive finite budget required")
        self.deadline = time.monotonic() + self.seconds
        self.steps = 0

    def tick(self, count=1):
        if time.monotonic() >= self.deadline or self.steps + count > self.max_steps:
            raise Exhausted("time or work limit")
        self.steps += count

    def cells(self, count):
        self.tick()
        if count > self.max_cells:
            raise Exhausted("factor-cell limit")


def validate(n, clauses):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative integer variable count required")
    if not isinstance(clauses, (list, tuple)):
        raise ValueError("clauses must be a list or tuple")
    if n > 512 or len(clauses) > 20_000:
        raise Exhausted("input dimension limit")
    literals = 0
    for c in clauses:
        if not isinstance(c, (list, tuple)):
            raise ValueError("clause must be a list or tuple")
        literals += len(c)
        if literals > 100_000:
            raise Exhausted("literal occurrence limit")
        if any(type(x) is not int or not 0 < abs(x) <= n for x in c):
            raise ValueError("invalid signed literal")
    return tuple(tuple(c) for c in clauses)


def normalize(n, clauses):
    """Remove syntactic redundancy; return dense CNF and new-to-old variable map.

    An empty clause is retained; unused variables can be assigned arbitrarily.
    This is not canonicalization modulo logical equivalence or variable renaming.
    """
    formula = validate(n, clauses)
    unique = set()
    for c in formula:
        s = set(c)
        if not any(-x in s for x in s):
            unique.add(tuple(sorted(s)))
    active = tuple(sorted({abs(x) for c in unique for x in c}))
    mapping = {x: i + 1 for i, x in enumerate(active)}
    dense = tuple(sorted(tuple(sorted(mapping[abs(x)] if x > 0 else
                                      -mapping[abs(x)] for x in c)) for c in unique))
    return len(active), dense, active


def primal(n, clauses, budget):
    g = {i: set() for i in range(1, n + 1)}
    for c in clauses:
        for u, v in combinations(sorted({abs(x) for x in c}), 2):
            budget.tick()
            g[u].add(v)
            g[v].add(u)
    return g


def topology(g, budget):
    unseen = set(g)
    components = 0
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            v = stack.pop()
            budget.tick(1 + len(g[v]))
            new = g[v] & unseen
            unseen.difference_update(new)
            stack.extend(new)
    edges = sum(map(len, g.values())) // 2
    return {"vertices": len(g), "edges": edges, "beta0": components,
            "beta1": edges - len(g) + components,
            "euler": len(g) - edges}


def signed_incidence(clauses):
    return [(i, abs(x), 1 if x > 0 else -1)
            for i, c in enumerate(clauses) for x in c]


def ordering(graph, budget, strategy):
    g = {v: set(ns) for v, ns in graph.items()}
    order, width = [], 0

    def score(v):
        ns = g[v]
        budget.tick()
        if strategy == "min_degree":
            return len(ns), v
        if strategy != "min_fill":
            raise ValueError("unknown ordering strategy")
        fill = 0
        for a, b in combinations(ns, 2):
            budget.tick()
            fill += b not in g[a]
        return fill, len(ns), v

    while g:
        v = min(g, key=score)
        ns = g.pop(v)
        order.append(v)
        width = max(width, len(ns))
        for u in ns:
            budget.tick(1 + len(ns))
            g[u].discard(v)
            g[u].update(ns - {u})
    return tuple(order), width


def verify_order(graph, order, budget):
    """Independent replay using an edge set, not the heuristic adjacency updates."""
    if len(order) != len(graph) or set(order) != set(graph):
        raise ValueError("order must be a permutation")
    edges = {(u, v) for u, ns in graph.items() for v in ns if u < v}
    width = 0
    for v in order:
        ns = set()
        budget.tick(1 + len(edges))
        for a, b in edges:
            if a == v:
                ns.add(b)
            elif b == v:
                ns.add(a)
        width = max(width, len(ns))
        edges = {(a, b) for a, b in edges if a != v and b != v}
        for a, b in combinations(sorted(ns), 2):
            budget.tick()
            edges.add((a, b))
    return width


def structural(n, clauses, c, budget, strategies=("min_degree", "min_fill")):
    """c is a fixed positive integer; threshold computed exactly, without floats."""
    if type(c) is not int or not 1 <= c <= 16:
        raise ValueError("c must be an integer in 1..16")
    graph = primal(n, clauses, budget)
    candidates = []
    for strategy in strategies:
        order, width = ordering(graph, budget, strategy)
        if verify_order(graph, order, budget) != width:
            raise AssertionError("width certificate replay mismatch")
        candidates.append((width, strategy, order))
    width, strategy, order = min(candidates)
    size = max(2, n + len(clauses) + sum(map(len, clauses)))
    threshold = (size ** c).bit_length() - 1
    return {**topology(graph, budget), "N": size, "c": c, "width": width,
            "threshold": threshold, "gap": width - threshold,
            "width_condition": width <= threshold,
            "order": order, "strategy": strategy,
            "candidate_widths": {s: w for w, s, _ in candidates},
            "certificate_replayed": True}


def truth(clauses, assignment):
    return all(any(assignment[abs(x) - 1] == (x > 0) for x in c) for c in clauses)


def brute(n, clauses, budget):
    for values in product((False, True), repeat=n):
        budget.tick(1 + sum(map(len, clauses)) + len(clauses))
        if truth(clauses, values):
            return True
    return False


def two_sat(n, clauses, budget):
    """Implication graph; mutual reachability test (polynomial, not linear SCC)."""
    if any(len(c) > 2 for c in clauses):
        raise ValueError("not 2-CNF")
    g = {s * i: set() for i in range(1, n + 1) for s in (-1, 1)}
    for c in clauses:
        budget.tick()
        if not c:
            return False
        a, b = c[0], c[-1]
        g[-a].add(b)
        g[-b].add(a)

    def reaches(a, b):
        seen, stack = {a}, [a]
        while stack:
            v = stack.pop()
            budget.tick(1 + len(g[v]))
            if v == b:
                return True
            new = g[v] - seen
            seen.update(new)
            stack.extend(new)
        return False

    return not any(reaches(i, -i) and reaches(-i, i) for i in range(1, n + 1))


def horn_sat(clauses, budget):
    """Least-model forward chaining, including empty and negative-only clauses."""
    if any(sum(x > 0 for x in c) > 1 for c in clauses):
        raise ValueError("not Horn CNF")
    true = set()
    changed = True
    while changed:
        changed = False
        for c in clauses:
            budget.tick(1 + len(c))
            if all(-x in true for x in c if x < 0):
                head = next((x for x in c if x > 0), None)
                if head is None:
                    return False
                if head not in true:
                    true.add(head)
                    changed = True
    return True


def eliminate(n, clauses, order, budget):
    """Exact existential Boolean factor elimination; explicit truth tables.

    Stored cells are capped cumulatively across live tables, including the new
    table while old tables are live. This is not a hard process RSS limit.
    """
    if len(order) != n or set(order) != set(range(1, n + 1)):
        raise ValueError("invalid elimination permutation")
    factors = []
    live = 0

    def allocate(k):
        if k >= budget.max_cells.bit_length():
            raise Exhausted("factor-cell limit")
        cells = 1 << k
        budget.cells(live + cells)
        return cells

    for clause in clauses:
        scope = tuple(sorted({abs(x) for x in clause}))
        cells = allocate(len(scope))
        indices = {v: i for i, v in enumerate(scope)}
        table = []
        for mask in range(cells):
            budget.tick(1 + len(clause))
            table.append(any(bool(mask & (1 << indices[abs(x)])) == (x > 0)
                             for x in clause))
        if not any(table):
            return False
        factors.append((scope, table))
        live += cells

    for v in order:
        budget.tick(1 + len(factors))
        bucket = [(s, t) for s, t in factors if v in s]
        if not bucket:
            continue
        remaining = [(s, t) for s, t in factors if v not in s]
        scope = tuple(sorted({x for s, _ in bucket for x in s if x != v}))
        cells = allocate(len(scope))
        positions = {x: i for i, x in enumerate(scope)}
        maps = [(tuple(-1 if x == v else positions[x] for x in s), t)
                for s, t in bucket]
        table = []
        for mask in range(cells):
            possible = False
            for bit in (0, 1):
                valid = True
                for indices, old in maps:
                    budget.tick(1 + len(indices))
                    idx = sum((bit if j == -1 else (mask >> j) & 1) << i
                              for i, j in enumerate(indices))
                    if not old[idx]:
                        valid = False
                        break
                if valid:
                    possible = True
                    break
            table.append(possible)
        if not any(table):
            return False
        live += cells - sum(len(t) for _, t in bucket)
        factors = remaining + [(scope, table)]
    return all(t[0] for _, t in factors)


def analyze(n, clauses, c, budget):
    raw = validate(n, clauses)
    nn, normalized, mapping = normalize(n, raw)
    a = structural(n, raw, c, budget)
    b = structural(nn, normalized, c, budget)
    criteria = {"logarithmic_width": b["width_condition"],
                "two_cnf": all(len(q) <= 2 for q in normalized),
                "horn": all(sum(x > 0 for x in q) <= 1 for q in normalized)}
    return {"raw": a, "normalized": b, "normalized_clauses": normalized,
            "new_to_old": mapping, "signed_incidence": signed_incidence(normalized),
            "criteria": criteria, "recognized": any(criteria.values()),
            "scope": "encoding-dependent sufficient criteria; not intrinsic hardness"}


def decide(n, clauses, analysis, budget):
    nn, f, mapping = normalize(n, clauses)
    # Recompute recognizers instead of trusting externally supplied metadata.
    if all(len(q) <= 2 for q in f):
        method, value = "two_sat", two_sat(nn, f, budget)
    elif all(sum(x > 0 for x in q) <= 1 for q in f):
        method, value = "horn_sat", horn_sat(f, budget)
    else:
        order = analysis["normalized"]["order"]
        method, value = "factor_elimination", eliminate(nn, f, order, budget)
    return {"method": method, "sat": value,
            "independent_crosscheck": None}


def duplication_example(budget):
    """Counterexample to raw-gap duplication invariance, not to tractability."""
    f = tuple(combinations(range(1, 9), 2))
    a, b = analyze(8, f, 1, budget), analyze(8, f + f, 1, budget)
    sat_a, sat_b = brute(8, f, budget), brute(8, f + f, budget)
    if not (sat_a and sat_b and a["raw"]["gap"] == 1 and b["raw"]["gap"] == 0
            and a["normalized"] == b["normalized"]):
        raise AssertionError("counterexample replay failed")
    return {"claim_refuted": "raw gap is invariant under exact clause duplication",
            "raw_original": a["raw"], "raw_duplicated": b["raw"],
            "normalized": a["normalized"], "both_sat": True,
            "scope": "one verified finite counterexample; F and F AND F are equivalent"}
