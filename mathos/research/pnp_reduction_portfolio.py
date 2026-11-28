"""Certificate-producing restricted CNF preprocessing portfolio.

All rules preserve existential satisfiability. This is not a complete solver,
nor a universal reduction to logarithmic treewidth.
"""
from itertools import product
from .pnp_structural_kernel import normalize

PROFILES = ("unit", "simplify", "bounded_resolution")


def _occurrences(f, budget):
    pos = {}
    for clause in f:
        budget.tick(1 + len(clause))
        for x in clause:
            pos.setdefault(x, []).append(clause)
    return pos


def _resolve(a, b, v):
    s = (set(a) - {v}) | (set(b) - {-v})
    return None if any(-x in s for x in s) else tuple(sorted(s))


def _candidate(f, profile, cap, budget):
    if () in f:
        return None
    for c in sorted(f):
        budget.tick()
        if len(c) == 1:
            return {"rule": "unit", "literal": c[0]}
    if profile == "unit":
        return None
    occ = _occurrences(f, budget)
    for x in sorted(occ):
        budget.tick()
        if -x not in occ:
            return {"rule": "pure", "literal": x}
    # Every possible subsumer has strictly smaller size; duplicate clauses
    # were removed by normalization. Avoid same-length quadratic comparisons.
    by_size = {}
    for clause in sorted(f, key=lambda c: (len(c), c)):
        s = set(clause)
        for size, candidates in by_size.items():
            if size >= len(clause):
                continue
            for small in candidates:
                budget.tick(1 + size)
                if small <= s:
                    return {"rule": "subsumption", "remove": clause,
                            "witness": tuple(sorted(small))}
        by_size.setdefault(len(clause), []).append(s)
    if profile != "bounded_resolution":
        return None
    for v in sorted({abs(x) for x in occ}):
        p, q = occ.get(v, []), occ.get(-v, [])
        budget.tick(1 + len(p) + len(q))
        neighbors = {abs(x) for c in p + q for x in c if abs(x) != v}
        if len(neighbors) > cap:
            continue
        resolved = set()
        for a, b in product(p, q):
            budget.tick(1 + len(a) + len(b))
            r = _resolve(a, b, v)
            if r is not None:
                resolved.add(r)
                budget.cells(len(resolved))
            if len(resolved) > len(p) + len(q):
                break
        else:
            return {"rule": "resolve", "variable": v}
    return None


def _apply(f, step, budget):
    rule = step["rule"]
    if rule in ("unit", "pure"):
        x = step["literal"]
        result = set()
        for c in f:
            budget.tick(1 + len(c))
            if x not in c:
                result.add(tuple(y for y in c if y != -x))
        return result
    if rule == "subsumption":
        return f - {tuple(step["remove"])}
    v = step["variable"]
    p, q = [], []
    result = set()
    for c in f:
        budget.tick(1 + len(c))
        if v in c:
            p.append(c)
        elif -v in c:
            q.append(c)
        else:
            result.add(c)
    for a, b in product(p, q):
        budget.tick(1 + len(a) + len(b))
        r = _resolve(a, b, v)
        if r is not None:
            result.add(r)
    return result


def _check_options(profile, cap):
    if profile not in PROFILES or type(cap) is not int or not 0 <= cap <= 12:
        raise ValueError("profile or neighbor cap invalid (cap 0..12)")


def reduce_cnf(n, clauses, budget, *, profile="bounded_resolution", cap=4):
    _check_options(profile, cap)
    nn, normalized, mapping = normalize(n, clauses)
    f, steps = set(normalized), []
    while True:
        step = _candidate(f, profile, cap, budget)
        if step is None:
            break
        f = _apply(f, step, budget)
        steps.append(step)
    m, result, active = normalize(nn, tuple(f))
    return {"profile": profile, "neighbor_cap": cap, "steps": steps,
            "n": m, "clauses": result,
            "new_to_old": tuple(mapping[i-1] for i in active)}


def verify_reduction(n, clauses, artifact, budget):
    """Replay exact local rules without trusting the generator's choices.

    Checks SAT preservation and profile constraints, not maximality of the
    output reduction. A valid prefix is sufficient for these claims.
    """
    profile, cap = artifact["profile"], artifact["neighbor_cap"]
    _check_options(profile, cap)
    nn, normalized, mapping = normalize(n, clauses)
    f = {frozenset(c) for c in normalized}
    allowed = {"unit"} if profile == "unit" else {"unit", "pure", "subsumption"}
    if profile == "bounded_resolution":
        allowed.add("resolve")
    for step in artifact["steps"]:
        budget.tick()
        rule = step["rule"]
        if rule not in allowed or frozenset() in f:
            raise ValueError("step forbidden by profile or terminal contradiction")
        if rule in ("unit", "pure"):
            x = step["literal"]
            if type(x) is not int or not 0 < abs(x) <= nn:
                raise ValueError("invalid literal")
            if rule == "unit":
                valid = frozenset((x,)) in f
            else:
                valid = any(x in c for c in f) and not any(-x in c for c in f)
            if not valid:
                raise ValueError("unit/purity premise not satisfied")
            new = set()
            for c in f:
                budget.tick(1 + len(c))
                if x not in c:
                    new.add(c - {-x})
            f = new
        elif rule == "subsumption":
            a, b = frozenset(step["witness"]), frozenset(step["remove"])
            if a not in f or b not in f or not a < b:
                raise ValueError("invalid subsumption witness")
            f.remove(b)
        else:
            v = step["variable"]
            if type(v) is not int or not 1 <= v <= nn:
                raise ValueError("invalid resolution variable")
            positives, negatives, kept = [], [], set()
            for c in f:
                budget.tick(1 + len(c))
                if v in c:
                    positives.append(c - {v})
                elif -v in c:
                    negatives.append(c - {-v})
                else:
                    kept.add(c)
            if not positives or not negatives:
                raise ValueError("resolution requires both polarities")
            neighbors = {abs(x) for c in positives + negatives for x in c}
            if len(neighbors) > cap:
                raise ValueError("resolution neighbor cap exceeded")
            resolvents = set()
            for a in positives:
                for b in negatives:
                    budget.tick(1 + len(a) + len(b))
                    merged = a | b
                    if merged.isdisjoint({-x for x in merged}):
                        resolvents.add(merged)
                        budget.cells(len(resolvents))
                    if len(resolvents) > len(positives) + len(negatives):
                        raise ValueError("resolution clause growth cap exceeded")
            f = kept | resolvents
    m, result, active = normalize(nn, tuple(tuple(c) for c in f))
    if (m != artifact["n"] or result != tuple(tuple(c) for c in artifact["clauses"])
            or tuple(mapping[i-1] for i in active) != tuple(artifact["new_to_old"])):
        raise ValueError("final reduction artifact mismatch")
    return True
