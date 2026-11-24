"""F031 native root-component adapter, not a port of the missing scratch code.

CNF width at most three, sparse binary IDs, shared F030 search-node budget.
Root partition only; no dynamic residual splitting or universal time bound.
"""
from itertools import product
from random import Random

from . import tga_proctor_adaptive_propagation as adaptive
from .tga_proctor_factor_decomposition import partition
from .tga_proctor_renamable_horn import sparse_input

PNP_RESOLUTION_STATUS = "OPEN"


def _input(n, clauses):
    if type(n) is not int or n < 0:
        raise ValueError("invalid variable count")
    cs = tuple(tuple(c) for c in clauses)
    if any(len(c) > 3 or any(type(l) is not int or not 1 <= abs(l) <= n
                             for l in c) for c in cs):
        raise ValueError("expected signed CNF of width at most three")
    ids = tuple(sorted({abs(l) for c in cs for l in c}))
    return cs, ids


def _pad(c):
    return c + (c[-1],) * (3 - len(c))


def _holds(cs, assignment):
    return all(any(assignment[abs(l)] == (l > 0) for l in c) for c in cs)


def solve(n, clauses, node_limit=1024):
    """Solve independent root components smallest first, or return UNKNOWN."""
    if type(node_limit) is not int or node_limit < 0:
        raise ValueError("invalid node limit")
    cs, ids = _input(n, clauses)
    nodes = calls = component_count = 0

    def result(status, **kw):
        return dict(status=status, ids=ids, nodes=nodes, component_calls=calls,
                    components=component_count, node_limit=node_limit,
                    cost_model="ABSTRACT_F030_SEARCH_NODES", **kw)

    if node_limit == 0:
        return result("UNKNOWN")
    empty = next((i for i, c in enumerate(cs) if not c), None)
    if empty is not None:
        return result("UNSAT", certificate=("empty", empty))
    padded = tuple(_pad(c) for c in cs)
    normalized_ids, compact = sparse_input(n, padded)
    if normalized_ids != ids:
        raise AssertionError("normalization mismatch")
    bad, components = partition(compact, {})
    if bad is not None:
        raise AssertionError("unexpected empty padded clause")
    component_count = len(components)
    witness = {}
    for component in sorted(components, key=lambda c: (len(c.variables), c.indices)):
        if nodes >= node_limit:
            return result("UNKNOWN")
        # Reuse F025 indices, but replay F030 on original sparse IDs. The
        # F030 normalizer keeps each local search independent of declared n.
        indices = component.indices
        local = tuple(padded[i] for i in indices)
        r = adaptive.solve(n, local, node_limit - nodes)
        calls += 1
        nodes += r["nodes"]
        if r["status"] == "UNKNOWN":
            return result("UNKNOWN")
        if not adaptive.verify(n, local, r):
            raise AssertionError("local certificate rejected")
        if r["status"] == "UNSAT":
            return result("UNSAT", certificate=("subset", indices, r))
        for v, b in zip(r["ids"], r["witness"]):
            if v in witness:
                raise AssertionError("component overlap")
            witness[v] = b
    if set(witness) != set(ids) or not _holds(cs, witness):
        raise AssertionError("assembled witness failed")
    return result("SAT", witness=tuple(witness[v] for v in ids))


def verify(n, clauses, result):
    """Check original witness or original-clause subset refutation.

    Does not call partition or trust component IDs, costs or search ordering.
    Shares input normalization and F030 verifier; not independent review.
    """
    cs, ids = _input(n, clauses)
    try:
        if tuple(result["ids"]) != ids:
            return False
        if result["status"] == "SAT":
            w = tuple(result["witness"])
            return (len(w) == len(ids) and all(type(b) is bool for b in w)
                    and _holds(cs, dict(zip(ids, w))))
        if result["status"] != "UNSAT":
            return False
        tag, *payload = result["certificate"]
        if tag == "empty" and len(payload) == 1:
            i = payload[0]
            return type(i) is int and 0 <= i < len(cs) and not cs[i]
        if tag != "subset" or len(payload) != 2:
            return False
        indices, proof = payload
        indices = tuple(indices)
        if (not indices or any(type(i) is not int or not 0 <= i < len(cs)
                              or not cs[i] for i in indices)
                or tuple(sorted(set(indices))) != indices):
            return False
        return (proof["status"] == "UNSAT"
                and adaptive.verify(n, tuple(_pad(cs[i]) for i in indices), proof))
    except (KeyError, TypeError, ValueError, IndexError, AttributeError):
        return False


def guarded_root_obstruction(t):
    """Connected before propagation; F030 disjoint obstruction after a unit.

    Non-tautological guard clauses connect one representative of every
    gadget and the UNSAT core to a fresh forced-true variable.
    This defeats root-only splitting, not dynamic residual decomposition.
    """
    n, cs = adaptive.search_obstruction(t)
    guard = n + 1
    reps = tuple(4*i+1 for i in range(t+1))
    bridges = tuple((guard, a, b) for a, b in zip(reps, reps[1:]))
    return guard, cs + ((guard, guard, guard),) + bridges


def guarded_controls():
    results = []
    for t in (1, 2, 4, 6, 8):
        n, cs = adaptive.search_obstruction(t)
        base = adaptive.solve(n, cs, 100000)
        n, cs = guarded_root_obstruction(t)
        guarded = solve(n, cs, 100000)
        if (base["status"] != "UNSAT" or guarded["status"] != "UNSAT"
                or guarded["components"] != 1 or guarded["component_calls"] != 1
                or not adaptive.verify(n-1, adaptive.search_obstruction(t)[1], base)
                or not verify(n, cs, guarded)
                or guarded["nodes"] != base["nodes"]
                or guarded["nodes"] < 2**t):
            raise AssertionError("guarded root obstruction mismatch")
        results.append(dict(t=t, base_nodes=base["nodes"],
                            guarded_root_nodes=guarded["nodes"],
                            lower_bound=2**t, root_components=guarded["components"]))
    return results


def controls():
    rng = Random(31032)
    counts = dict(cases=0, sat=0, unsat=0, unknown=0)
    for _ in range(600):
        r = rng.randrange(1, 7)
        ids = tuple(10**9 + 97*i for i in range(r))
        n = 2**100
        cs = tuple(tuple(rng.choice((-1, 1))*rng.choice(ids)
                         for _ in range(rng.randrange(1, 4)))
                   for _ in range(rng.randrange(15)))
        expected = any(_holds(cs, dict(zip(ids, bits)))
                       for bits in product((False, True), repeat=r))
        out = solve(n, cs, 2**(r+1))
        if out["status"] != ("SAT" if expected else "UNSAT") or not verify(n, cs, out):
            raise AssertionError("brute-force mismatch")
        counts["cases"] += 1
        counts[out["status"].lower()] += 1
        short = solve(n, cs, 0)
        if short["status"] != "UNKNOWN" or verify(n, cs, short):
            raise AssertionError("budget status invalid")
        counts["unknown"] += 1
    disjoint = []
    connected = []
    for t in (1, 2, 4, 6, 8):
        n, cs = adaptive.search_obstruction(t)
        a, b = adaptive.solve(n, cs, 100000), solve(n, cs, 100000)
        if (a["status"] != "UNSAT" or b["status"] != "UNSAT"
                or not adaptive.verify(n, cs, a) or not verify(n, cs, b)
                or b["components"] != t+1 or b["component_calls"] != 1
                or b["nodes"] >= a["nodes"]):
            raise AssertionError("disjoint family mismatch")
        disjoint.append(dict(t=t, plain_nodes=a["nodes"], component_nodes=b["nodes"]))
        n, cs = adaptive.obstruction(t)
        a, b = adaptive.solve(n, cs, 100000), solve(n, cs, 100000)
        if (a["status"] != "SAT" or b["status"] != "SAT"
                or not adaptive.verify(n, cs, a) or not verify(n, cs, b)
                or b["components"] != 1 or a["nodes"] != b["nodes"]):
            raise AssertionError("connected control mismatch")
        connected.append(dict(t=t, plain_nodes=a["nodes"], component_nodes=b["nodes"]))
    return dict(**counts, disjoint=disjoint, connected_sat_control=connected,
                guarded_root_obstruction=guarded_controls(),
                cost_model="ABSTRACT_F030_SEARCH_NODES", resolution_status=PNP_RESOLUTION_STATUS,
                machine_refinement=False, independent_review=False, original_scratch_port=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(), indent=2))
