"""F032: blind degree-two elimination before syntactic parity recovery.

Only the input CNF and a pair budget determine the schedule. This is
a bounded heuristic, not an arbitrary hidden-XOR discovery algorithm.
"""
from collections import Counter
from random import Random

from . import tga_proctor_xor_cnf as xor
from . import tga_proctor_xor_bve as bve
from .tga_proctor_dynamic_resolution import cubic_graph, tseitin

PNP_RESOLUTION_STATUS = "OPEN"


def schedule(n, clauses):
    """Initially one positive and one negative occurrence in distinct clauses.

    Count after tautology removal and exact duplicate normalization.
    Visit the selected occurring IDs once, without supplied auxiliary labels.
    """
    cs = xor._input(n, clauses)
    rows = {frozenset(c) for c in cs}
    counts = Counter(l for c in rows if not any(-l in c for l in c) for l in c)
    return tuple(sorted(v for v in counts if v > 0 and counts[v] == counts[-v] == 1))


def solve(n, clauses, pair_limit=100000):
    cs = xor._input(n, clauses)
    order = schedule(n, cs)
    r = bve.solve(n, cs, order=order, pair_limit=pair_limit, max_width=5)
    return dict(r, scheduled=len(order), schedule="INITIAL_OPPOSITE_DEGREE_TWO",
                resolution_status=PNP_RESOLUTION_STATUS)


def verify(n, clauses, result):
    """The resolution and parity evidence, not the heuristic, establishes UNSAT."""
    return bve.verify(n, clauses, result)


def chain_split(n, clauses, seed, depth):
    """Hide each ternary clause behind a private chain of depth 1 or 2."""
    cs = xor._input(n, clauses)
    if depth not in (1, 2) or type(depth) is not int:
        raise ValueError("depth must be 1 or 2")
    if any(len(c) != 3 or len({abs(l) for l in c}) != 3 for c in cs):
        raise ValueError("expected distinct ternary clauses")
    rng = Random(seed)
    out = []
    top = n
    for clause in cs:
        a, b, c = rng.sample(clause, 3)
        top += 1
        z = top
        out.append((a, z))
        if depth == 2:
            top += 1
            out.append((-z, top))
            z = top
        out.append((-z, b, c))
    return top, tuple(out)


def relabel(n, clauses, seed):
    """Shuffle IDs, polarities, clause order and literal order.

    The solving interface receives only the resulting n and CNF.
    All IDs are sparse; original and auxiliary labels are intermingled.
    """
    cs = xor._input(n, clauses)
    ids = sorted({abs(l) for c in cs for l in c})
    rng = Random(seed)
    labels = [10**40 + 97*i for i in range(len(ids))]
    rng.shuffle(labels)
    mapping = {v: label*rng.choice((-1, 1)) for v, label in zip(ids, labels)}
    rows = [tuple(mapping[abs(l)] if l > 0 else -mapping[abs(l)] for l in c) for c in cs]
    rows = [tuple(rng.sample(c, len(c))) for c in rows]
    rng.shuffle(rows)
    return 2**200, tuple(rows)


def shared_selector(n, clauses):
    """Negative control: all clauses guarded by both signs of a shared bit.

    C becomes (C OR g) AND (C OR NOT g). The conjunction equals C,
    but the guard has high incidence and every resulting parity support
    contains both guard signs for the same original forbidden pattern.
    """
    cs = xor._input(n, clauses)
    g = n+1
    return g, tuple(c+(s*g,) for c in cs for s in (-1,1))


def controls():
    positive = []
    for q in (4, 8, 16, 32, 64, 80):
        for seed in (11, 29, 47):
            for depth in (1, 2):
                edges = cubic_graph(q, seed)
                for charge in (True, False):
                    n, cs = tseitin(q, edges, (charge,)+(False,)*(q-1))
                    m, hidden = chain_split(n, cs, seed, depth)
                    sn, shuffled = relabel(m, hidden, seed+100)
                    direct = xor.solve(sn, shuffled)
                    limit = depth*len(cs)
                    out = solve(sn, shuffled, pair_limit=1000)
                    if direct["status"] != "UNKNOWN" or direct["recognized_rows"] != 0:
                        raise AssertionError("unexpected direct detection")
                    if (out["scheduled"] != limit or out["eliminated"] != limit
                            or out["pair_tests"] != limit
                            or out["recognized_rows"] != q
                            or len(out["preprocessing"]["clauses"]) != len(cs)
                            or out["status"] != ("UNSAT" if charge else "UNKNOWN")
                            or verify(sn, shuffled, out) != charge):
                        raise AssertionError("blind recovery mismatch")
                    if charge:
                        zero = solve(sn, shuffled, pair_limit=0)
                        if zero["status"] != "UNKNOWN" or zero["eliminated"] != 0:
                            raise AssertionError("zero budget mismatch")
                        positive.append(dict(vertices=q, seed=seed, depth=depth,
                                             hidden_clauses=len(hidden), scheduled=out["scheduled"],
                                             recovered_rows=out["recognized_rows"],
                                             pair_tests=out["pair_tests"],
                                             resolution_lines=out["resolution_lines"]))
    negative = []
    for q in (4, 8, 16, 32):
        for seed in (11, 29, 47):
            n, cs = tseitin(q, cubic_graph(q,seed), (True,)+(False,)*(q-1))
            m, hidden = shared_selector(n, cs)
            sn, shuffled = relabel(m, hidden, seed+200)
            direct = xor.solve(sn, shuffled)
            out = solve(sn, shuffled)
            if (direct["status"] != "UNKNOWN" or direct["recognized_rows"] != 0
                    or out["status"] != "UNKNOWN" or out["scheduled"] != 0
                    or verify(sn, shuffled, out)):
                raise AssertionError("shared-selector negative control failed")
            negative.append(dict(vertices=q, seed=seed, hidden_clauses=len(hidden),
                                 scheduled=out["scheduled"], recognized_rows=out["recognized_rows"],
                                 status=out["status"]))
    rng = Random(32003)
    counts = dict(random_cases=0, brute_sat=0, certified_unsat=0, unknown=0)
    for _ in range(1200):
        ids = tuple(10**30+31*i for i in range(rng.randrange(1,7)))
        n = 2**200
        cs = tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                         for _ in range(rng.randrange(0,5)))
                   for _ in range(rng.randrange(15)))
        limit = rng.randrange(15)
        out = solve(n,cs,pair_limit=limit)
        reduced = bve.replay(n,cs,out["preprocessing"])
        sat = xor._brute(cs)
        if reduced is None or xor._brute(reduced) != sat or out["pair_tests"] > limit:
            raise AssertionError("random projection mismatch")
        if out["status"] == "UNSAT":
            if sat or not verify(n,cs,out):
                raise AssertionError("false certificate")
            counts["certified_unsat"] += 1
        elif out["status"] == "UNKNOWN" and not verify(n,cs,out):
            counts["unknown"] += 1
        else:
            raise AssertionError("bad status")
        counts["random_cases"] += 1
        counts["brute_sat"] += sat
    return dict(**counts, blind_odd=positive, even_controls=len(positive),
                zero_budget_controls=len(positive), shared_selector_negative=negative,
                fixture_pair_limit=1000, oracle_auxiliary_ids=False, resolution_status=PNP_RESOLUTION_STATUS,
                complete_cnf_solver=False, independent_review=False, machine_refinement=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(),indent=2))
