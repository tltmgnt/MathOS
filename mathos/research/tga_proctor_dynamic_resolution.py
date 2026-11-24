"""Translate dynamic UNSAT certificates to ordinary resolution.

No weakening, extension variables or algebraic inference. Native F031 work.
"""
from itertools import product
from random import Random

from . import tga_proctor_dynamic_components as dynamic
from . import tga_proctor_component_search as root

PNP_RESOLUTION_STATUS = "OPEN"


def extract(n, clauses, result, *, wide=False):
    cs, ids = dynamic._input(n, clauses, wide)
    if result.get("status") != "UNSAT" or not dynamic.verify(n, cs, result, wide=wide):
        raise ValueError("valid dynamic UNSAT certificate required")
    compact = dynamic._compact(cs, ids)
    steps, derived, rows = [], [], {}

    def axiom(i, clause):
        j = len(steps)
        steps.append(("axiom", i))
        derived.append(frozenset(clause))
        return j

    def resolve(a, b, lit):
        if lit not in derived[a] or -lit not in derived[b]:
            raise AssertionError("missing resolution pivot")
        j = len(steps)
        steps.append(("resolve", a, b, lit))
        derived.append((derived[a]-{lit}) | (derived[b]-{-lit}))
        return j

    for i, c in enumerate(compact):
        if not any(-l in c for l in c):
            rows[i] = (frozenset(c), axiom(i, c))

    def restrict(rows, lit, reason=None):
        out = {}
        for i, (c, j) in rows.items():
            if lit in c:
                continue
            if -lit in c and reason is not None:
                j = resolve(reason, j, lit)
            out[i] = (c-{-lit}, j)
        return out

    stream = iter(result["tree"])
    work, conclusions = [("visit", rows)], []
    visits = 0
    while work:
        tag, arg = work.pop()
        if tag == "join":
            lit = arg
            right, left = conclusions.pop(), conclusions.pop()
            if -lit not in derived[left]:
                conclusions.append(left)
            elif lit not in derived[right]:
                conclusions.append(right)
            else:
                conclusions.append(resolve(right, left, lit))
            continue
        rows = arg
        visits += 1
        events, terminal = next(stream)
        for kind, lit, i in events:
            rows = restrict(rows, lit, rows[i][1] if kind == "unit" else None)
        tag, *args = terminal
        if tag == "conflict":
            conclusions.append(rows[args[0]][1])
        elif tag == "subset":
            work.append(("visit", {i: rows[i] for i in args[0]}))
        else:
            v, first = args
            lit = v if first else -v
            work.append(("join", lit))
            work.append(("visit", restrict(rows, -lit)))
            work.append(("visit", restrict(rows, lit)))
    if next(stream, None) is not None or len(conclusions) != 1:
        raise AssertionError("incomplete conversion")
    end = conclusions[0]
    if derived[end]:
        raise AssertionError("expected empty clause")
    if len(steps) > len(cs) + visits*(len(cs)*len(ids)+1):
        raise AssertionError("line bound exceeded")
    return dict(ids=ids, steps=tuple(steps), conclusion=end)


def verify(n, clauses, proof, *, wide=False):
    """Ordinary resolution checker; no solver or dynamic certificate required."""
    cs, ids = dynamic._input(n, clauses, wide)
    compact = dynamic._compact(cs, ids)
    try:
        if tuple(proof["ids"]) != ids:
            return False
        lines = []
        for tag, *args in proof["steps"]:
            if tag == "axiom" and len(args) == 1:
                i = args[0]
                if type(i) is not int or not 0 <= i < len(cs):
                    return False
                c = set(compact[i])
            elif tag == "resolve" and len(args) == 3:
                a, b, lit = args
                if (any(type(j) is not int or not 0 <= j < len(lines) for j in (a,b))
                        or type(lit) is not int or not 1 <= abs(lit) <= len(ids)
                        or lit not in lines[a] or -lit not in lines[b]):
                    return False
                c = (lines[a]-{lit}) | (lines[b]-{-lit})
            else:
                return False
            lines.append(c)
        j = proof["conclusion"]
        return type(j) is int and 0 <= j < len(lines) and not lines[j]
    except (KeyError, TypeError, ValueError, IndexError, AttributeError):
        return False


def cubic_graph(vertices, seed):
    """Cycle plus random perfect matching avoiding cycle edges.

    Connected simple cubic graph, not a certified expander or uniform sample.
    Bounded attempts; deterministic fallback is the opposite-vertex matching.
    """
    if type(vertices) is not int or vertices < 4 or vertices % 2:
        raise ValueError("even vertex count >=4 required")
    cycle = {tuple(sorted((i, (i+1)%vertices))) for i in range(vertices)}
    rng = Random(seed)
    for _ in range(1000):
        vs = list(range(vertices))
        rng.shuffle(vs)
        matching = {tuple(sorted((a,b))) for a,b in zip(vs[::2], vs[1::2])}
        if not matching & cycle:
            break
    else:
        matching = {(i, i+vertices//2) for i in range(vertices//2)}
    return tuple(sorted(cycle | matching))


def tseitin(vertices, edges, charges):
    """Encode every violated local degree-three parity assignment as a clause."""
    if type(vertices) is not int or vertices < 4:
        raise ValueError("invalid vertex count")
    edges = tuple(tuple(e) for e in edges)
    charges = tuple(charges)
    if (len(charges) != vertices or any(type(b) is not bool for b in charges)
            or any(len(e) != 2 or any(type(v) is not int or not 0 <= v < vertices for v in e)
                   or e[0] >= e[1] for e in edges)
            or len(set(edges)) != len(edges)):
        raise ValueError("invalid graph or charges")
    incidence = [[] for _ in range(vertices)]
    for i, (a,b) in enumerate(edges, 1):
        incidence[a].append(i)
        incidence[b].append(i)
    if any(len(row) != 3 for row in incidence):
        raise ValueError("expected cubic graph")
    cs = tuple(tuple(-v if b else v for v,b in zip(row,bits))
               for row, charge in zip(incidence, charges)
               for bits in product((False, True), repeat=3)
               if (sum(bits)%2 == 1) != charge)
    return len(edges), cs


def controls():
    rng = Random(31034)
    checked = 0
    for _ in range(600):
        k = rng.randrange(1, 7)
        ids = tuple(10**9+19*i for i in range(k))
        n = 2**100
        cs = tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                         for _ in range(rng.randrange(1,4)))
                   for _ in range(rng.randrange(18)))
        r = dynamic.solve(n, cs, 10000)
        if not dynamic.verify(n, cs, r):
            raise AssertionError("dynamic decision invalid")
        if r["status"] == "UNSAT":
            p = extract(n, cs, r)
            if not verify(n, cs, p):
                raise AssertionError("resolution conversion invalid")
            checked += 1
    graphs = []
    for v in (4, 6, 8, 10, 12, 14, 16):
        for seed in (11, 29):
            edges = cubic_graph(v, seed)
            n, cs = tseitin(v, edges, (True,)+(False,)*(v-1))
            r = dynamic.solve(n, cs, 100000)
            if r["status"] != "UNSAT" or not dynamic.verify(n, cs, r):
                raise AssertionError("odd charge not refuted within control budget")
            p = extract(n, cs, r)
            if not verify(n, cs, p):
                raise AssertionError("Tseitin resolution conversion invalid")
            graphs.append(dict(vertices=v, seed=seed, variables=n, clauses=len(cs),
                               nodes=r["nodes"], resolution_lines=len(p["steps"])))
    return dict(random_cases=600, random_unsat_extracted=checked, cubic_graphs=graphs,
                resolution_status=PNP_RESOLUTION_STATUS, certified_expanders=False,
                machine_refinement=False, independent_review=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(), indent=2))
