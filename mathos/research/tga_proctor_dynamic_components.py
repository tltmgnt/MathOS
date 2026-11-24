"""Dynamic residual component search, with preorder UNSAT replay.

Native follow-up, not the missing scratch implementation. Width <= 3 by default; optional explicit wide CNF.
Search-node budget is abstract; no universal polynomial bound.
"""
from collections import Counter
from itertools import product
from random import Random

from . import tga_proctor_adaptive_propagation as adaptive
from . import tga_proctor_component_search as root
from .tga_proctor_affine_backdoor import compress
from .tga_proctor_factor_decomposition import partition
from .tga_proctor_renamable_horn import recognize

PNP_RESOLUTION_STATUS = "OPEN"


def _compact(cs, ids):
    ranks = {v: i+1 for i, v in enumerate(ids)}
    return tuple(tuple(ranks[abs(l)] if l > 0 else -ranks[abs(l)]
                       for l in c) for c in cs)


def _input(n, clauses, wide):
    if type(wide) is not bool:
        raise ValueError("wide must be Boolean")
    if not wide:
        return root._input(n, clauses)
    if type(n) is not int or n < 0:
        raise ValueError("invalid variable count")
    cs = tuple(tuple(c) for c in clauses)
    if any(type(l) is not int or not 1 <= abs(l) <= n for c in cs for l in c):
        raise ValueError("invalid literal")
    return cs, tuple(sorted({abs(l) for c in cs for l in c}))


def _wide_rows(cs):
    seen, rows = set(), []
    for i,c in enumerate(cs):
        key = tuple(sorted(set(c)))
        if key not in seen and not any(-l in key for l in key):
            seen.add(key)
            rows.append((i,key))
    return tuple(rows)


def _groups(rows):
    # F025 partition supports arbitrary nonempty rows; its compact
    # clause output is not used here, only original index groups.
    bad, groups = partition(tuple(c for _, c in rows), {})
    if bad is not None:
        raise AssertionError("empty clause after simplification")
    groups = sorted(groups, key=lambda g: (len(g.variables), g.indices))
    return tuple(tuple(rows[i] for i in g.indices) for g in groups)


def _flatten(proof):
    stack, out = [proof], []
    while stack:
        events, terminal, children = stack.pop()
        out.append((events, terminal))
        stack.extend(reversed(children))
    return tuple(out)


def solve(n, clauses, node_limit=1024, *, wide=False):
    """Explicit continuation stack; split residuals after every propagation."""
    if type(node_limit) is not int or node_limit < 0:
        raise ValueError("invalid node limit")
    cs, ids = _input(n, clauses, wide)
    compact = _compact(cs, ids)
    nodes = partitions = decompositions = splits = 0

    def report(status, **kw):
        return dict(status=status, ids=ids, nodes=nodes, partition_calls=partitions,
                    decomposition_nodes=decompositions, splits=splits,
                    node_limit=node_limit, cost_model="ABSTRACT_DYNAMIC_SEARCH_NODES", **kw)

    if node_limit == 0:
        return report("UNKNOWN")
    empty = next((i for i, c in enumerate(compact) if not c), None)
    if empty is not None:
        return report("UNSAT", tree=(((), ("conflict", empty)),))
    if wide:
        rows = _wide_rows(compact)
    else:
        _, rows, _ = compress(len(ids), tuple(root._pad(c) for c in compact))
    # A visit's input rows are already restricted by its ancestors.
    # Only a binary branch passes a nonempty initial local assignment.
    work = [("visit", rows, {})]
    ret = None
    while work:
        tag, *args = work.pop()
        if tag == "visit":
            if nodes >= node_limit:
                return report("UNKNOWN")
            nodes += 1
            rows, initial = args
            fixed = dict(initial)
            residual, events, conflict, _ = adaptive.simplify(rows, fixed)
            if conflict is not None:
                ret = ("UNSAT", (events, ("conflict", conflict), ()))
                continue
            if not residual:
                ret = ("SAT", fixed)
                continue
            groups = _groups(residual)
            partitions += 1
            if len(groups) > 1:
                decompositions += 1
                work.append(("components", groups, 0, fixed, events))
                work.append(("visit", groups[0], {}))
                continue
            active = {abs(l) for _, c in residual for l in c}
            flips, bad = recognize(len(ids), residual, set(range(1, len(ids)+1))-active)
            if not bad:
                # No units remain. Every oriented nonempty Horn clause
                # therefore has a negative literal; all-false satisfies.
                f = set(flips)
                ret = ("SAT", {**fixed, **{v: v in f for v in active}})
                continue
            counts = Counter(l for _, c in residual for l in c)
            v = min(active, key=lambda v: (-(counts[v]+counts[-v]), v))
            first = counts[v] >= counts[-v]
            splits += 1
            work.append(("first", residual, fixed, events, v, first))
            work.append(("visit", residual, {v: first}))
        elif tag == "components":
            groups, j, fixed, events = args
            status, payload = ret
            if status == "UNSAT":
                indices = tuple(i for i, _ in groups[j])
                ret = ("UNSAT", (events, ("subset", indices), (payload,)))
            else:
                if set(fixed) & set(payload):
                    raise AssertionError("overlapping component witnesses")
                fixed.update(payload)
                if j+1 == len(groups):
                    ret = ("SAT", fixed)
                else:
                    work.append(("components", groups, j+1, fixed, events))
                    work.append(("visit", groups[j+1], {}))
        elif tag == "first":
            residual, fixed, events, v, first = args
            status, payload = ret
            if status == "SAT":
                ret = ("SAT", {**fixed, **payload})
            else:
                work.append(("second", fixed, events, v, first, payload))
                work.append(("visit", residual, {v: not first}))
        elif tag == "second":
            fixed, events, v, first, left = args
            status, payload = ret
            if status == "SAT":
                ret = ("SAT", {**fixed, **payload})
            else:
                ret = ("UNSAT", (events, ("split", v, first), (left, payload)))
        else:
            raise AssertionError("bad continuation")
    status, payload = ret
    if status == "SAT":
        w = tuple(payload.get(v, False) for v in range(1, len(ids)+1))
        if not root._holds(cs, dict(zip(ids, w))):
            raise AssertionError("original witness failed")
        return report("SAT", witness=w)
    return report("UNSAT", tree=_flatten(payload))


def _restrict(rows, fixed):
    """Replay from original literal sets, independent of solver compression."""
    return {i: {l for l in c if abs(l) not in fixed}
            for i, c in rows.items()
            if not any(abs(l) in fixed and fixed[abs(l)] == (l > 0) for l in c)}


def verify(n, clauses, result, *, wide=False):
    """Replay subset and binary refutations without partition or recognition."""
    cs, ids = _input(n, clauses, wide)
    try:
        if tuple(result["ids"]) != ids:
            return False
        if result["status"] == "SAT":
            w = tuple(result["witness"])
            return (len(w) == len(ids) and all(type(b) is bool for b in w)
                    and root._holds(cs, dict(zip(ids, w))))
        if result["status"] != "UNSAT":
            return False
        compact = _compact(cs, ids)
        rows = {i: set(c) for i, c in enumerate(compact)
                if not any(-l in c for l in c)}
        stack = [rows]
        for events, terminal in result["tree"]:
            if not stack:
                return False
            residual = stack.pop()
            for kind, lit, i in events:
                if type(lit) is not int or not 1 <= abs(lit) <= len(ids):
                    return False
                if kind == "unit":
                    if type(i) is not int or residual.get(i) != {lit}:
                        return False
                elif kind == "pure":
                    if i is not None:
                        return False
                    signs = set().union(*residual.values())
                    if lit not in signs or -lit in signs:
                        return False
                else:
                    return False
                residual = _restrict(residual, {abs(lit): lit > 0})
            tag, *args = terminal
            if tag == "conflict" and len(args) == 1:
                i = args[0]
                if type(i) is not int or residual.get(i) != set():
                    return False
            elif tag == "subset" and len(args) == 1:
                ix = tuple(args[0])
                if (not ix or any(type(i) is not int or i not in residual for i in ix)
                        or tuple(sorted(set(ix))) != ix):
                    return False
                # No need to establish independence to lift UNSAT.
                stack.append({i: residual[i] for i in ix})
            elif tag == "split" and len(args) == 2:
                v, first = args
                if (type(v) is not int or not 1 <= v <= len(ids)
                        or type(first) is not bool
                        or not any(v in c or -v in c for c in residual.values())):
                    return False
                stack.append(_restrict(residual, {v: not first}))
                stack.append(_restrict(residual, {v: first}))
            else:
                return False
        return not stack
    except (KeyError, TypeError, ValueError, IndexError, AttributeError):
        return False


def controls():
    rng = Random(31033)
    counts = dict(cases=0, sat=0, unsat=0, zero_budget=0)
    for _ in range(800):
        r = rng.randrange(1, 7)
        ids = tuple(10**9 + 113*i for i in range(r))
        n = 2**100
        cs = tuple(tuple(rng.choice((-1, 1))*rng.choice(ids)
                         for _ in range(rng.randrange(1, 4)))
                   for _ in range(rng.randrange(18)))
        expected = any(root._holds(cs, dict(zip(ids, bits)))
                       for bits in product((False, True), repeat=r))
        out = solve(n, cs, 10000)
        if out["status"] != ("SAT" if expected else "UNSAT") or not verify(n, cs, out):
            raise AssertionError("decision mismatch")
        counts["cases"] += 1
        counts[out["status"].lower()] += 1
        short = solve(n, cs, 0)
        if short["status"] != "UNKNOWN" or verify(n, cs, short):
            raise AssertionError("budget mismatch")
        counts["zero_budget"] += 1
    guarded = []
    for t in (1, 2, 4, 8, 16, 32):
        n, cs = root.guarded_root_obstruction(t)
        out = solve(n, cs, 8)
        if (out["status"] != "UNSAT" or out["nodes"] != 8
                or out["decomposition_nodes"] < 1 or not verify(n, cs, out)):
            raise AssertionError("guarded family not discharged")
        guarded.append(dict(t=t, dynamic_nodes=out["nodes"],
                            root_lower_bound=2**t, decomposition_nodes=out["decomposition_nodes"]))
    return dict(**counts, guarded=guarded, resolution_status=PNP_RESOLUTION_STATUS,
                cost_model="ABSTRACT_DYNAMIC_SEARCH_NODES", machine_refinement=False,
                independent_review=False, original_scratch_port=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(), indent=2))
