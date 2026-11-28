"""Certified opposing bounds on treewidth, not on unrestricted SAT time.

Convention: empty graph has width zero. Every promoted bound has a replayable
certificate. Exact search is bounded and exponential, not a polynomial solver.
"""
from itertools import combinations
from .pnp_structural_kernel import Exhausted, ordering, verify_order

EXACT_LIMIT = 10


def validate_graph(g):
    if len(g) > 512:
        raise ValueError("graph exceeds 512 vertices")
    if any(type(v) is not int or v < 1 for v in g):
        raise ValueError("positive integer vertex labels required")
    for v, ns in g.items():
        if v in ns or any(u not in g or v not in g[u] for u in ns):
            raise ValueError("expected a simple undirected graph")


def _clique(g, budget):
    chosen = []
    remaining = set(g)
    while remaining:
        budget.tick(1 + len(remaining))
        v = min(remaining, key=lambda x: (-len(g[x] & remaining), x))
        chosen.append(v)
        remaining.intersection_update(g[v])
    return chosen


def minor_candidate(g, budget):
    """Greedy contraction, retaining original connected branch sets."""
    h = {v: set(ns) for v, ns in g.items()}
    branches = {v: {v} for v in h}
    best = []
    while h:
        clique = _clique(h, budget)
        if len(clique) > len(best):
            best = [sorted(branches[v]) for v in clique]
        if len(clique) == len(h):
            break
        edges = [(v, u) for v in h for u in h[v] if v < u]
        if not edges:
            break
        budget.tick(1 + len(edges))
        a, b = max(edges, key=lambda e: (
            len(h[e[0]] & h[e[1]]), -len(h[e[0]] | h[e[1]]), -e[0], -e[1]))
        neighbors = (h[a] | h[b]) - {a, b}
        for u in neighbors:
            budget.tick()
            h[u].discard(b)
            h[u].add(a)
        h[a] = neighbors
        del h[b]
        branches[a].update(branches.pop(b))
    return {"kind": "clique_minor", "branches": best}


def degree_candidate(g, budget):
    """Find a subgraph whose minimum degree lower-bounds treewidth."""
    h = {v: set(ns) for v, ns in g.items()}
    best, width = [], -1
    while h:
        budget.tick(1 + len(h))
        v = min(h, key=lambda x: (len(h[x]), x))
        if len(h[v]) > width:
            width, best = len(h[v]), sorted(h)
        for u in h.pop(v):
            budget.tick()
            h[u].remove(v)
    return {"kind": "min_degree", "vertices": best}


def _neighbors(g, v, removed, budget):
    """Search paths whose internal vertices were eliminated."""
    seen = {v}
    pending = [v]
    result = set()
    while pending:
        u = pending.pop()
        budget.tick(1 + len(g[u]))
        for x in g[u] - seen:
            seen.add(x)
            if x in removed:
                pending.append(x)
            else:
                result.add(x)
    return result


def _filled(g, removed, budget):
    """Independent certificate replay: explicit fill in a canonical order."""
    h = {v: set(ns) for v, ns in g.items()}
    for v in sorted(removed):
        ns = h.pop(v)
        for u in ns:
            budget.tick(1 + len(ns))
            h[u].remove(v)
            h[u].update(ns - {u})
    return h


def threshold_search(g, k, budget):
    """Find an order of width <= k, or a closed reachable-subset certificate.

    The residual graph depends only on the eliminated subset, not its ordering.
    Each edge exists iff an original path has only eliminated internal vertices.
    """
    if len(g) > EXACT_LIMIT:
        raise ValueError("bounded exact search vertex limit")
    if type(k) is not int or not 0 <= k < len(g):
        raise ValueError("invalid threshold")
    vs = sorted(g)
    full = (1 << len(vs)) - 1
    budget.cells(full + 1)
    parent = {0: None}
    queue = [0]
    for mask in queue:
        budget.tick()
        if mask == full:
            order = []
            while mask:
                prev, v = parent[mask]
                order.append(v)
                mask = prev
            return {"kind": "order", "order": list(reversed(order))}
        removed = {v for i, v in enumerate(vs) if mask & (1 << i)}
        for i, v in enumerate(vs):
            if v in removed:
                continue
            nxt = mask | (1 << i)
            if nxt not in parent and len(_neighbors(g, v, removed, budget)) <= k:
                parent[nxt] = (mask, v)
                queue.append(nxt)
    return {"kind": "closed_frontier", "threshold": k, "states": sorted(parent)}


def verify_lower(g, cert, budget):
    """Validate evidence rather than trusting claimed numeric lower bounds."""
    validate_graph(g)
    kind = cert["kind"]
    if kind == "zero":
        return 0
    if kind == "min_degree":
        vertices = cert["vertices"]
        s = set(vertices)
        if len(s) != len(vertices) or not s <= set(g) or not s:
            raise ValueError("invalid induced subgraph certificate")
        budget.tick(1 + sum(len(g[v]) for v in s))
        return min(len(g[v] & s) for v in s)
    if kind == "clique_minor":
        used, sets = set(), []
        for branch in cert["branches"]:
            s = set(branch)
            if not s or len(s) != len(branch) or s & used or not s <= set(g):
                raise ValueError("invalid branch set")
            pending = [min(s)]
            seen = set(pending)
            while pending:
                v = pending.pop()
                budget.tick(1 + len(g[v]))
                new = (g[v] & s) - seen
                seen.update(new)
                pending.extend(new)
            if seen != s:
                raise ValueError("disconnected branch set")
            used.update(s)
            sets.append(s)
        for a, b in combinations(sets, 2):
            budget.tick(1 + sum(len(g[v]) for v in a))
            if not any(g[v] & b for v in a):
                raise ValueError("missing minor edge")
        return max(0, len(sets) - 1)
    if kind == "closed_frontier":
        vs = sorted(g)
        k, states = cert["threshold"], cert["states"]
        if len(vs) > EXACT_LIMIT or type(k) is not int or not 0 <= k < len(vs):
            raise ValueError("invalid frontier threshold")
        full = (1 << len(vs)) - 1
        budget.cells(full + 1)
        if len(states) > full or any(type(s) is not int or not 0 <= s < full for s in states):
            raise ValueError("invalid frontier states")
        reached = set(states)
        if 0 not in reached or len(reached) != len(states):
            raise ValueError("frontier must contain empty state and exclude full state")
        for mask in reached:
            budget.tick()
            removed = {v for i, v in enumerate(vs) if mask & (1 << i)}
            h = _filled(g, removed, budget)
            for i, v in enumerate(vs):
                if v in h and len(h[v]) <= k and (mask | (1 << i)) not in reached:
                    raise ValueError("frontier not closed under legal eliminations")
        return k + 1
    raise ValueError("unknown lower certificate")


def verify_bounds(g, report, budget):
    validate_graph(g)
    lo = verify_lower(g, report["lower_certificate"], budget)
    hi = verify_order(g, report["upper_order"], budget)
    if (lo != report["lower"] or hi != report["upper"] or lo > hi or
            report["gap"] != hi - lo or report["exact"] != (lo == hi)):
        raise ValueError("inconsistent bound report")
    return True


def converge(g, budget, *, exact_limit=EXACT_LIMIT):
    """Alternate constructive and obstruction improvements on the SAME graph.

    Keep only replayed bounds after exhaustion. If initial replay is interrupted,
    return no upper certificate rather than invent one.
    """
    validate_graph(g)
    if type(exact_limit) is not int or not 0 <= exact_limit <= EXACT_LIMIT:
        raise ValueError("invalid exact limit")
    lo, hi = 0, None
    lower_cert, upper_order = {"kind": "zero"}, None
    history = []
    reason = None

    def upper(order, source, claimed=None):
        nonlocal hi, upper_order
        value = verify_order(g, order, budget)
        if claimed is not None and value != claimed:
            raise AssertionError("ordering replay mismatch")
        if value < lo:
            raise AssertionError("upper contradicts lower")
        if hi is None or value < hi:
            hi, upper_order = value, list(order)
            history.append({"side": "constructive", "source": source, "lower": lo, "upper": hi})

    def lower(cert):
        nonlocal lo, lower_cert
        value = verify_lower(g, cert, budget)
        if hi is not None and value > hi:
            raise AssertionError("lower contradicts upper")
        if value > lo:
            lo, lower_cert = value, cert
            history.append({"side": "obstruction", "source": cert["kind"], "lower": lo, "upper": hi})

    try:
        upper(sorted(g), "initial_order")
        if lo < hi:
            lower(degree_candidate(g, budget))
        for strategy in ("min_degree", "min_fill"):
            if lo == hi:
                break
            order, claimed = ordering(g, budget, strategy)
            upper(order, strategy, claimed)
        if lo < hi:
            lower(minor_candidate(g, budget))
        while lo < hi and len(g) <= exact_limit:
            k = (lo + hi) // 2
            result = threshold_search(g, k, budget)
            if result["kind"] == "order":
                upper(result["order"], "bounded_threshold_search")
                if hi > k:
                    raise AssertionError("threshold upper mismatch")
            else:
                lower(result)
                if lo <= k:
                    raise AssertionError("threshold lower mismatch")
        if lo != hi:
            reason = "exact search vertex limit"
    except Exhausted as exc:
        reason = str(exc)
    return {"lower": lo, "upper": hi, "gap": None if hi is None else hi - lo,
            "exact": hi is not None and hi == lo, "lower_certificate": lower_cert,
            "upper_order": upper_order, "history": history, "stop_reason": reason,
            "scope": "treewidth of this finite graph only; not a SAT-time lower bound"}
