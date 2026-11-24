"""F030: adaptive renamable-Horn search after unit/pure simplification.

Iterative bounded search with independently replayable UNSAT trees.
No universal small search tree or polynomial-time decision is claimed.
"""
from collections import Counter
from itertools import product
from mathos.research.tga_proctor_affine_backdoor import compress
from mathos.research.tga_proctor_renamable_horn import (
    sparse_input, recognize, orient, obstruction as prior_obstruction, plan)
from mathos.research.tga_proctor_resolution_gates import _rules, _closure
from mathos.research.tga_proctor_unrestricted_scope import evaluate


def residual_rows(rows, fixed):
    return tuple((i, tuple(l for l in c if abs(l) not in fixed))
                 for i, c in rows
                 if not any(abs(l) in fixed and fixed[abs(l)] == (l > 0) for l in c))


def simplify(rows, fixed):
    """Log forced units and satisfiability-preserving pure assignments."""
    events = []
    scans = 0
    while True:
        residual = residual_rows(rows, fixed)
        scans += len(rows)
        empty = next((i for i, c in residual if not c), None)
        if empty is not None:
            return residual, tuple(events), empty, scans
        unit = next(((i, c[0]) for i, c in residual if len(c) == 1), None)
        if unit is not None:
            i, lit = unit
            events.append(("unit", lit, i))
        else:
            signs = {l for _, c in residual for l in c}
            pure = sorted((l for l in signs if -l not in signs), key=lambda l: (abs(l), l))
            if not pure:
                return residual, tuple(events), None, scans
            lit = pure[0]
            events.append(("pure", lit, None))
        fixed[abs(lit)] = lit > 0


def solve(n, clauses, node_limit=1024):
    if type(node_limit) is not int or node_limit < 0:
        raise ValueError("invalid node limit")
    ids, cs = sparse_input(n, clauses)
    size = len(ids)
    _, rows, _ = compress(size, cs)
    stack, tree = [{}], []
    scans = rule_scans = recognitions = splits = assigned = nodes = 0
    def report(status, **kw):
        return dict(status=status, ids=ids, nodes=nodes, splits=splits,
                    propagation_assignments=assigned, residual_scans=scans,
                    rule_scans=rule_scans, recognition_calls=recognitions,
                    node_limit=node_limit, **kw)
    while stack:
        if nodes >= node_limit:
            return report("UNKNOWN")
        fixed = stack.pop()
        nodes += 1
        residual, events, conflict, work = simplify(rows, fixed)
        scans += work
        assigned += len(events)
        if conflict is not None:
            tree.append((events, ("conflict", conflict)))
            continue
        flips, bad = recognize(size, residual, fixed)
        recognitions += 1
        if not bad:
            oriented = tuple((i, c) for (i, _), c in
                             zip(residual, orient((c for _, c in residual), flips)))
            true, trace, work = _closure(tuple(_rules(oriented, {}, 1)))
            rule_scans += work
            if true is not None:
                f = set(flips)
                witness = tuple(fixed[v] if v in fixed else (v in true) != (v in f)
                                for v in range(1, size+1))
                if not evaluate(cs, witness):
                    raise AssertionError("original witness failed")
                return report("SAT", witness=witness)
            tree.append((events, ("horn", flips, trace)))
            continue
        counts = Counter(l for _, c in residual for l in c)
        active = {abs(l) for l in counts}
        v = min(active, key=lambda v: (-(counts[v]+counts[-v]), v))
        preferred = counts[v] >= counts[-v]
        tree.append((events, ("split", v, preferred)))
        splits += 1
        # Preorder: preferred child first, opposite child second.
        stack.append({**fixed, v: not preferred})
        stack.append({**fixed, v: preferred})
    return report("UNSAT", tree=tuple(tree))


def _original_residual(cs, fixed):
    """Independent replay on original clauses, not solver compression."""
    result = {}
    for i, c in enumerate(cs):
        literals = set(c)
        if any(-l in literals for l in literals):
            continue
        if any(abs(l) in fixed and fixed[abs(l)] == (l > 0) for l in literals):
            continue
        result[i] = {l for l in literals if abs(l) not in fixed}
    return result


def verify(n, clauses, result):
    """Check original witness or the entire preorder refutation tree."""
    ids, cs = sparse_input(n, clauses)
    size = len(ids)
    def valid_id(v):
        return type(v) is int and 1 <= v <= size
    def clause_id(i):
        return type(i) is int and 0 <= i < len(cs)
    try:
        if tuple(result["ids"]) != ids:
            return False
        if result["status"] == "SAT":
            w = result["witness"]
            return len(w) == size and all(type(b) is bool for b in w) and evaluate(cs, w)
        if result["status"] != "UNSAT":
            return False
        stack = [{}]
        for events, terminal in result["tree"]:
            if not stack:
                return False
            fixed = stack.pop()
            for kind, lit, i in events:
                if type(lit) is not int or not valid_id(abs(lit)) or abs(lit) in fixed:
                    return False
                residual = _original_residual(cs, fixed)
                if kind == "unit":
                    if not clause_id(i) or residual.get(i) != {lit}:
                        return False
                elif kind == "pure":
                    signs = set().union(*residual.values())
                    if i is not None or lit not in signs or -lit in signs:
                        return False
                else:
                    return False
                fixed[abs(lit)] = lit > 0
            residual = _original_residual(cs, fixed)
            tag, *payload = terminal
            if tag == "conflict" and len(payload) == 1:
                i = payload[0]
                if not clause_id(i) or residual.get(i) != set():
                    return False
            elif tag == "split" and len(payload) == 2:
                v, first = payload
                if not valid_id(v) or v in fixed or type(first) is not bool:
                    return False
                stack.append({**fixed, v: not first})
                stack.append({**fixed, v: first})
            elif tag == "horn" and len(payload) == 2:
                flips, trace = payload
                flips = tuple(flips)
                if (any(not valid_id(v) or v in fixed for v in flips)
                        or tuple(sorted(set(flips))) != flips or not trace):
                    return False
                f = set(flips)
                clauses2 = {i: {-l if abs(l) in f else l for l in c}
                            for i, c in residual.items()}
                if any(sum(l > 0 for l in c) > 1 for c in clauses2.values()):
                    return False
                true = set()
                for j, i in enumerate(trace):
                    if not clause_id(i) or i not in clauses2:
                        return False
                    c = clauses2[i]
                    heads = {l for l in c if l > 0}
                    if any(-l not in true for l in c if l < 0):
                        return False
                    if j == len(trace)-1:
                        if heads:
                            return False
                    elif len(heads) != 1 or heads <= true:
                        return False
                    else:
                        true.update(heads)
            else:
                return False
        return not stack
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def obstruction(t):
    """Connected, SAT, no initial units/pure literals, minimum deletion 2t."""
    if type(t) is not int or t < 1:
        raise ValueError("t >= 1 required")
    cs = [tuple(s*(3*i+j+1) for j, s in enumerate(signs))
          for i in range(t) for signs in product((-1, 1), repeat=3)
          if signs != (-1, -1, -1)]
    cs += [(3*i, 3*i+1, 3*i+1) for i in range(1, t)]
    return 3*t, tuple(cs)


def controls():
    triples = tuple(product((-2, -1, 1, 2), repeat=3))
    cases = [(0, ()), (2, ())] + [(2, (c,)) for c in triples]
    cases += [(2, (a, b)) for a, b in product(triples, repeat=2)]
    signs = tuple(tuple(s*(i+1) for i, s in enumerate(p))
                  for p in product((-1, 1), repeat=3))
    cases += [(3, tuple(c for i, c in enumerate(signs) if mask >> i & 1))
              for mask in range(256)]
    sat = unsat = 0
    for n, cs in cases:
        result = solve(n, cs, 2**(n+1)-1)
        brute = any(evaluate(cs, w) for w in product((False, True), repeat=n))
        if result["status"] != ("SAT" if brute else "UNSAT") or not verify(n, cs, result):
            raise AssertionError("decision mismatch")
        sat += brute
        unsat += not brute
    families = []
    for t in (1, 2, 4, 8, 16, 32):
        n, cs = prior_obstruction(t)
        r = solve(n, cs, 1)
        if r["status"] != "SAT" or r["splits"] or not verify(n, cs, r):
            raise AssertionError("prior family not eliminated")
        n, cs = obstruction(t)
        _, rows, _ = compress(n, cs)
        residual, events, conflict, _ = simplify(rows, {})
        if events or conflict is not None or recognize(n, residual)[0] is not None:
            raise AssertionError("new family should survive root simplification")
        deletion = tuple(v for v in range(1, n+1) if v % 3 != 2)
        if recognize(n, rows, deletion)[0] is None:
            raise AssertionError("deletion upper bound failed")
        r = solve(n, cs, 4*n+1)
        if r["status"] != "SAT" or not verify(n, cs, r):
            raise AssertionError("bounded adaptive family check failed")
        families.append(dict(t=t, minimum_static_deletion=2*t, nodes=r["nodes"],
                             splits=r["splits"], root_propagation=0))
    return dict(cases=len(cases), sat=sat, unsat=unsat, families=families,
                universal_bound=False, machine_refinement=False, independent_review=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(), indent=2))
