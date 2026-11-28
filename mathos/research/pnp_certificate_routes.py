"""Independently replayable semantic routes for a restricted SAT portfolio.

The routes return either a checked reduction to a constant SAT instance or
no candidate. Neither absence of a candidate nor exhaustion means UNSAT.
All variable identifiers in certificates refer to the normalized CNF.
"""
from collections import deque
from itertools import combinations, product

from .pnp_structural_kernel import normalize, truth, brute

ROUTES = ("constant", "two_sat", "horn", "renamable_horn", "bounded_core")
CORE_SEARCH_LIMIT = 12
CORE_WIDTH = 5


def _implications(n, f, budget):
    budget.cells(2*n + 2*len(f))
    g = {s*i: set() for i in range(1, n+1) for s in (-1, 1)}
    reverse = {i: set() for i in g}
    for c in f:
        budget.tick(1 + len(c))
        if not 1 <= len(c) <= 2:
            raise ValueError("expected nonempty 2-CNF clauses")
        a, b = c[0], c[-1]
        for u, v in ((-a, b), (-b, a)):
            g[u].add(v)
            reverse[v].add(u)
    return g, reverse


def _finish_order(g, budget):
    seen, finished = set(), []
    for root in sorted(g):
        budget.tick()
        if root in seen:
            continue
        seen.add(root)
        stack = [(root, iter(sorted(g[root])))]
        while stack:
            budget.tick()
            v, it = stack[-1]
            u = next(it, None)
            if u is None:
                finished.append(v)
                stack.pop()
            elif u not in seen:
                seen.add(u)
                stack.append((u, iter(sorted(g[u]))))
    return finished


def _path(g, start, goal, budget):
    parent = {start: None}
    pending = deque([start])
    while pending:
        v = pending.popleft()
        budget.tick(1 + len(g[v]))
        if v == goal:
            result = []
            while v is not None:
                result.append(v)
                v = parent[v]
            return list(reversed(result))
        for u in sorted(g[v]):
            if u not in parent:
                parent[u] = v
                pending.append(u)
    raise AssertionError("SCC path not found")


def _two_sat_proof(n, f, budget):
    if () in f:
        return {"kind": "empty_clause"}
    g, reverse = _implications(n, f, budget)
    finished = _finish_order(g, budget)
    comp = {}
    index = 0
    for root in reversed(finished):
        budget.tick()
        if root in comp:
            continue
        comp[root] = index
        stack = [root]
        while stack:
            v = stack.pop()
            budget.tick(1 + len(reverse[v]))
            for u in sorted(reverse[v]):
                if u not in comp:
                    comp[u] = index
                    stack.append(u)
        index += 1
    for v in range(1, n+1):
        budget.tick()
        if comp[v] == comp[-v]:
            return {"kind": "opposing_paths", "variable": v,
                    "positive_to_negative": _path(g, v, -v, budget),
                    "negative_to_positive": _path(g, -v, v, budget)}
    a = tuple(comp[v] > comp[-v] for v in range(1, n+1))
    budget.tick(1 + len(f) + sum(map(len, f)))
    if not truth(f, a):
        raise AssertionError("SCC assignment failed")
    return {"kind": "sat_witness", "assignment": a}


def _rename(f, flips, budget):
    out = []
    for c in f:
        budget.tick(1 + len(c))
        out.append(tuple(-x if flips[abs(x)-1] else x for x in c))
    return tuple(out)


def _horn(f):
    return all(sum(x > 0 for x in c) <= 1 for c in f)


def _horn_proof(n, f, flips, budget):
    renamed = _rename(f, flips, budget)
    if not _horn(renamed):
        return None
    yes, trace = set(), []
    changed = True
    while changed:
        changed = False
        for i, c in enumerate(renamed):
            budget.tick(1 + len(c))
            if not all(-x in yes for x in c if x < 0):
                continue
            head = next((x for x in c if x > 0), None)
            if head is None:
                return {"kind": "unit_conflict", "renaming": flips,
                        "trace": trace, "conflict": i}
            if head not in yes:
                yes.add(head)
                trace.append(i)
                changed = True
    assignment = tuple((v in yes) != flips[v-1] for v in range(1, n+1))
    budget.tick(1 + len(f) + sum(map(len, f)))
    if not truth(f, assignment):
        raise AssertionError("Horn assignment failed")
    return {"kind": "sat_witness", "renaming": flips, "assignment": assignment}


def _renamable_horn(n, f, budget):
    # Let r_i be the flip bit. A signed literal x in the original clause is
    # positive after renaming iff the literal -x is true on r. Forbid every
    # pair of positives using the binary clause (x OR y) on flip bits.
    constraints = set()
    for c in f:
        for a, b in combinations(c, 2):
            budget.tick()
            constraints.add(tuple(sorted((a, b))))
            budget.cells(len(constraints))
    result = _two_sat_proof(n, tuple(sorted(constraints)), budget)
    if result["kind"] != "sat_witness":
        return None
    proof = _horn_proof(n, f, result["assignment"], budget)
    if proof is None:
        raise AssertionError("renaming did not produce Horn CNF")
    return proof


def _small_core(n, f, budget):
    # Preserve v4's fast control even when n is large.
    if n >= 5:
        fixed = {tuple(sorted(s*x for x in q))
                 for q in combinations(range(1, 6), 3) for s in (-1, 1)}
        budget.tick(1 + len(f))
        if fixed <= set(f):
            return {"kind": "unsat_core", "core": sorted(fixed)}
    if n > CORE_SEARCH_LIMIT:
        return None
    scoped = [(c, frozenset(abs(x) for x in c)) for c in f]
    for variables in combinations(range(1, n+1), min(n, CORE_WIDTH)):
        support = set(variables)
        budget.tick(1 + len(scoped))
        local = [c for c, s in scoped if s <= support]
        if not local:
            continue
        pos = {v: i for i, v in enumerate(variables)}
        selected = set()
        for bits in product((False, True), repeat=len(variables)):
            violated = None
            for c in local:
                budget.tick(1 + len(c))
                if not any(bits[pos[abs(x)]] == (x > 0) for x in c):
                    violated = c
                    break
            if violated is None:
                break
            selected.add(violated)
        else:
            # At most one violated clause per assignment, hence <=32 clauses.
            return {"kind": "unsat_core", "core": sorted(selected)}
    return None


def propose(n, clauses, route, budget):
    if route not in ROUTES:
        raise ValueError("unknown route")
    nn, f, _ = normalize(n, clauses)
    proof = None
    if route == "constant":
        for bit in (True, False):
            budget.tick(1 + len(f) + sum(map(len, f)))
            a = (bit,) * nn
            if truth(f, a):
                proof = {"kind": "sat_witness", "assignment": a}
                break
    elif route == "two_sat":
        if all(len(c) <= 2 for c in f):
            proof = _two_sat_proof(nn, f, budget)
    elif route == "horn":
        proof = _horn_proof(nn, f, (False,) * nn, budget)
    elif route == "renamable_horn":
        proof = _renamable_horn(nn, f, budget)
    else:
        proof = _small_core(nn, f, budget)
    if proof is None:
        return None
    return {"route": route, **proof, "n": 0,
            "clauses": () if proof["kind"] == "sat_witness" else ((),)}


def _check_path(fset, n, path, start, goal, budget):
    if (not isinstance(path, (list, tuple)) or not 2 <= len(path) <= 2*n or
            any(type(x) is not int or not 0 < abs(x) <= n for x in path) or
            path[0] != start or path[-1] != goal or len(set(path)) != len(path)):
        raise ValueError("invalid implication path")
    for a, b in zip(path, path[1:]):
        budget.tick()
        pair = tuple(sorted((-a, b)))
        if pair not in fset and not (b == -a and (-a,) in fset):
            raise ValueError("implication edge is not justified by a clause")


def _check_trace(f, n, trace, conflict, budget):
    if not isinstance(trace, (list, tuple)) or len(trace) > n:
        raise ValueError("invalid unit trace")
    assigned = {}
    for idx in trace:
        if type(idx) is not int or not 0 <= idx < len(f):
            raise ValueError("invalid trace clause index")
        c = f[idx]
        budget.tick(1 + len(c))
        if any(assigned.get(abs(x)) == (x > 0) for x in c):
            raise ValueError("trace clause already satisfied")
        pending = [x for x in c if abs(x) not in assigned]
        if len(pending) != 1:
            raise ValueError("trace clause is not unit")
        x = pending[0]
        assigned[abs(x)] = x > 0
    if type(conflict) is not int or not 0 <= conflict < len(f):
        raise ValueError("invalid conflict clause index")
    c = f[conflict]
    budget.tick(1 + len(c))
    if not all(abs(x) in assigned and assigned[abs(x)] != (x > 0) for x in c):
        raise ValueError("conflict clause is not false under the forced assignment")


def verify(n, clauses, artifact, budget):
    """Check proof semantics independently of SCC/forward-chain/core search.

    The checker also validates the named route's applicability. Its accepted
    constant formula is equisatisfiable with the normalized input.
    """
    nn, f, _ = normalize(n, clauses)
    route, kind = artifact["route"], artifact["kind"]
    if route not in ROUTES:
        raise ValueError("unknown route")
    allowed = {
        "constant": {"sat_witness"},
        "two_sat": {"sat_witness", "empty_clause", "opposing_paths"},
        "horn": {"sat_witness", "unit_conflict"},
        "renamable_horn": {"sat_witness", "unit_conflict"},
        "bounded_core": {"unsat_core"},
    }
    if kind not in allowed[route]:
        raise ValueError("certificate kind not allowed for route")
    if route == "two_sat" and any(len(c) > 2 for c in f):
        raise ValueError("input is not 2-CNF")
    if route in ("horn", "renamable_horn"):
        flips = artifact["renaming"]
        if (not isinstance(flips, (list, tuple)) or len(flips) != nn or
                any(type(x) is not bool for x in flips) or
                (route == "horn" and any(flips))):
            raise ValueError("invalid Horn renaming")
        for c in f:
            budget.tick(1 + len(c))
            if sum((x > 0) != flips[abs(x)-1] for x in c) > 1:
                raise ValueError("renaming does not produce Horn CNF")
    if kind == "sat_witness":
        a = artifact["assignment"]
        if (not isinstance(a, (list, tuple)) or len(a) != nn or
                any(type(x) is not bool for x in a) or
                (route == "constant" and len(set(a)) > 1)):
            raise ValueError("invalid assignment")
        budget.tick(1 + len(f) + sum(map(len, f)))
        if not truth(f, a):
            raise ValueError("witness rejected")
    elif kind == "empty_clause":
        if () not in f:
            raise ValueError("missing empty clause")
    elif kind == "opposing_paths":
        v = artifact["variable"]
        if type(v) is not int or not 1 <= v <= nn:
            raise ValueError("invalid contradictory variable")
        fset = set(f)
        _check_path(fset, nn, artifact["positive_to_negative"], v, -v, budget)
        _check_path(fset, nn, artifact["negative_to_positive"], -v, v, budget)
    elif kind == "unit_conflict":
        _check_trace(f, nn, artifact["trace"], artifact["conflict"], budget)
    else:
        raw = artifact["core"]
        if (not isinstance(raw, (list, tuple)) or not 1 <= len(raw) <= 32 or
                any(not isinstance(c, (list, tuple)) or len(c) > CORE_WIDTH or
                    any(type(x) is not int or not 0 < abs(x) <= nn for x in c)
                    for c in raw)):
            raise ValueError("invalid bounded core")
        core = tuple(tuple(c) for c in raw)
        budget.tick(1 + len(f) + len(core))
        variables = sorted({abs(x) for c in core for x in c})
        if (len(variables) > CORE_WIDTH or not set(core) <= set(f) or
                len(set(core)) != len(core)):
            raise ValueError("core not a bounded subformula")
        pos = {v: i+1 for i, v in enumerate(variables)}
        dense = tuple(tuple(pos[abs(x)] if x > 0 else -pos[abs(x)] for x in c)
                      for c in core)
        if brute(len(variables), dense, budget):
            raise ValueError("core is satisfiable")
    expected = () if kind == "sat_witness" else ((),)
    if (type(artifact["n"]) is not int or artifact["n"] != 0 or
            tuple(tuple(c) for c in artifact["clauses"]) != expected):
        raise ValueError("incorrect constant output")
    return True


def execute(n, clauses, program, budget):
    """Try the synthesized route sequence; return only a replayed certificate."""
    if (not isinstance(program, (tuple, list)) or len(set(program)) != len(program)
            or any(r not in ROUTES for r in program)):
        raise ValueError("invalid program")
    for route in program:
        proof = propose(n, clauses, route, budget)
        if proof is not None:
            verify(n, clauses, proof, budget)
            return proof
    return None
