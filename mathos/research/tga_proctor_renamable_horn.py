"""F029: constructive renamable-Horn deletion backdoor discovery.

The 2-SAT recognition step is exact. Greedy deletion is not minimum
backdoor discovery. All decision claims are scoped; budget exhaustion is UNKNOWN.
"""
from itertools import combinations, product
from mathos.research.tga_proctor_affine_backdoor import compress
from mathos.research.tga_proctor_resolution_gates import (
    _rules, _closure, plan as global_plan, verify as horn_verify,
    obstruction as global_obstruction)
from mathos.research.tga_proctor_unrestricted_scope import evaluate


def pair_constraints(rows, deleted=()):
    """Flip bit true means complement the corresponding original variable."""
    deleted = set(deleted)
    return tuple(sorted({tuple(sorted((a, b))) for _, c in rows
                        for a, b in combinations(c, 2)
                        if abs(a) not in deleted and abs(b) not in deleted}))


def _finish(graph):
    """Iterative DFS postorder, each vertex entered exactly once."""
    seen, order = set(), []
    for v in graph:
        if v in seen:
            continue
        seen.add(v)
        stack = [(v, iter(graph[v]))]
        while stack:
            u, children = stack[-1]
            w = next(children, None)
            if w is None:
                order.append(u)
                stack.pop()
            elif w not in seen:
                seen.add(w)
                stack.append((w, iter(graph[w])))
    return order


def recognize(n, rows, deleted=()):
    """Return (flips, ()) or (None, contradictory variable IDs).

    A pair (a,b) is the 2-SAT clause a OR b over flip variables.
    SCC IDs are in topological order; assign true to the later component.
    """
    deleted = set(deleted)
    active = [v for v in range(1, n+1) if v not in deleted]
    graph = {s*v: [] for v in active for s in (1, -1)}
    reverse = {v: [] for v in graph}
    pairs = pair_constraints(rows, deleted)
    for a, b in pairs:
        for u, v in ((-a, b), (-b, a)):
            graph[u].append(v)
            reverse[v].append(u)
    comp = {}
    count = 0
    for v in reversed(_finish(graph)):
        if v in comp:
            continue
        comp[v] = count
        stack = [v]
        while stack:
            for w in reverse[stack.pop()]:
                if w not in comp:
                    comp[w] = count
                    stack.append(w)
        count += 1
    bad = tuple(v for v in active if comp[v] == comp[-v])
    if bad:
        return None, bad
    flips = tuple(v for v in active if comp[v] > comp[-v])
    f = set(flips)
    if not all((a > 0) == (abs(a) in f) or (b > 0) == (abs(b) in f)
               for a, b in pairs):
        raise AssertionError("invalid 2-SAT orientation")
    return flips, ()


def orient(clauses, flips):
    f = set(flips)
    return tuple(tuple(-l if abs(l) in f else l for l in c) for c in clauses)


def valid_plan(rows, cover, flips):
    b, f = set(cover), set(flips)
    return all(sum((l > 0) != (abs(l) in f)
                   for l in c if abs(l) not in b) <= 1 for _, c in rows)


def plan(n, clauses):
    cs, rows, _ = compress(n, clauses)
    deleted = set()
    rounds = 0
    while True:
        flips, bad = recognize(n, rows, deleted)
        rounds += 1
        if not bad:
            break
        # Deterministically delete a high-incidence contradictory variable.
        degree = dict.fromkeys(bad, 0)
        for a, b in pair_constraints(rows, deleted):
            for v in (abs(a), abs(b)):
                if v in degree:
                    degree[v] += 1
        deleted.add(min(bad, key=lambda v: (-degree[v], v)))
    # Inclusion-minimal for this greedy candidate, not cardinality optimal.
    for v in sorted(deleted):
        trial = deleted - {v}
        new, bad = recognize(n, rows, trial)
        rounds += 1
        if not bad:
            deleted, flips = trial, new
    _, _, global_cover, _, polarity = global_plan(n, cs)
    global_flips = tuple(range(1, n+1)) if polarity == -1 else ()
    cover, flips = min(((tuple(sorted(deleted)), flips),
                        (global_cover, global_flips)),
                       key=lambda pair: (len(pair[0]), pair))
    if not valid_plan(rows, cover, flips):
        raise AssertionError("invalid deletion backdoor")
    return cs, rows, cover, flips, rounds


def solve(n, clauses, branch_limit=1024):
    if type(branch_limit) is not int or branch_limit < 0:
        raise ValueError("invalid branch limit")
    cs, rows, cover, flips, rounds = plan(n, clauses)
    oriented_rows = tuple((i, c) for (i, _), c in
                          zip(rows, orient((c for _, c in rows), flips)))
    f = set(flips)
    traces, scans = [], 0
    common = dict(cover=cover, flips=flips, recognition_calls=rounds,
                  branch_limit=branch_limit)
    for j, bits in enumerate(product((False, True), repeat=len(cover))):
        if j >= branch_limit:
            return dict(status="UNKNOWN", branches=j, rule_scans=scans, **common)
        fixed = dict(zip(cover, bits))
        true, trace, work = _closure(tuple(_rules(oriented_rows, fixed, 1)))
        scans += work
        if true is not None:
            witness = tuple(fixed.get(v, v in true) != (v in f)
                            for v in range(1, n+1))
            if not evaluate(cs, witness):
                raise AssertionError("invalid original witness")
            return dict(status="SAT", witness=witness, branches=j+1,
                        rule_scans=scans, **common)
        traces.append(trace)
    return dict(status="UNSAT", traces=tuple(traces), branches=len(traces),
                rule_scans=scans, **common)


def verify(n, clauses, result):
    """Replay original witnesses or translate all traces to F028's verifier."""
    cs, _, _ = compress(n, clauses)
    try:
        if result["status"] == "SAT":
            return horn_verify(n, cs, result)
        if result["status"] != "UNSAT":
            return False
        flips = tuple(result["flips"])
        if (any(type(v) is not int or not 1 <= v <= n for v in flips)
                or tuple(sorted(set(flips))) != flips):
            return False
        return horn_verify(n, orient(cs, flips), {**result, "polarity": 1})
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def sparse_input(n, clauses):
    """Compact occurring IDs without allocating n entries; retain reverse map.

    Decision-equivalent even when declared n is binary-encoded and huge.
    The compact witness can be interpreted with all omitted variables false.
    """
    if type(n) is not int or n < 0:
        raise ValueError("invalid variable count")
    cs = tuple(tuple(c) for c in clauses)
    if any(len(c) != 3 or any(type(l) is not int or not 1 <= abs(l) <= n
                              for l in c) for c in cs):
        raise ValueError("invalid 3-CNF")
    ids = tuple(sorted({abs(l) for c in cs for l in c}))
    rank = {v: i+1 for i, v in enumerate(ids)}
    compact = tuple(tuple(rank[abs(l)] if l > 0 else -rank[abs(l)]
                          for l in c) for c in cs)
    return ids, compact


def obstruction(t):
    """Connected satisfiable formulas whose syntactic deletion minimum is t."""
    if type(t) is not int or t < 1:
        raise ValueError("t >= 1 required")
    c = 2*t+1
    return c, tuple((s*(2*i+1), p*(2*i+2), c)
                    for i in range(t) for s, p in product((-1, 1), repeat=2))


def controls():
    triples = tuple(product((-2, -1, 1, 2), repeat=3))
    fixtures = [(0, ()), (2, ())] + [(2, (c,)) for c in triples]
    fixtures += [(2, (a, b)) for a, b in product(triples, repeat=2)]
    sat = unsat = recognition_checks = 0
    for n, cs in fixtures:
        _, rows, _ = compress(n, cs)
        for bits in product((False, True), repeat=n):
            deleted = tuple(v for v in range(1, n+1) if bits[v-1])
            f, bad = recognize(n, rows, deleted)
            brute = any(valid_plan(rows, deleted,
                         [v for v in range(1, n+1) if flags[v-1]])
                        for flags in product((False, True), repeat=n))
            if (f is not None) != brute or (f is not None and not valid_plan(rows, deleted, f)):
                raise AssertionError("recognition mismatch")
            recognition_checks += 1
        r = solve(n, cs, branch_limit=2**n)
        expected = any(evaluate(cs, x) for x in product((False, True), repeat=n))
        if r["status"] != ("SAT" if expected else "UNSAT") or not verify(n, cs, r):
            raise AssertionError("decision mismatch")
        sat += expected
        unsat += not expected
    n, cs = global_obstruction(12)
    r = solve(n, cs, 1)
    if r["status"] != "SAT" or r["cover"] or not verify(n, cs, r):
        raise AssertionError("global obstruction should be renamable Horn")
    families = []
    for t in (1, 2, 4, 8, 16, 32):
        n, cs = obstruction(t)
        _, rows, cover, flips, rounds = plan(n, cs)
        if len(cover) < t or not valid_plan(rows, cover, flips):
            raise AssertionError("obstruction lower bound")
        if not valid_plan(rows, range(1, 2*t+1, 2), (n,)):
            raise AssertionError("obstruction upper bound")
        families.append(dict(t=t, n=n, clauses=len(cs), cover=len(cover),
                             exact_minimum=t, recognition_calls=rounds))
    return dict(cases=len(fixtures), sat=sat, unsat=unsat,
                recognition_checks=recognition_checks, obstruction=families,
                universal_bound=False, machine_refinement=False, independent_review=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(), indent=2))
