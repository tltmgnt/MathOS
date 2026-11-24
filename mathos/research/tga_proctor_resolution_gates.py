"""F028: polarity-sensitive Horn backdoors, bounded search and replay.

All results are scoped to explicit-n signed 3-CNF. No universal small
backdoor or unrestricted polynomial-time bound is claimed.
"""
from itertools import combinations, product
from mathos.research.tga_proctor_affine_backdoor import compress, cover_plan
from mathos.research.tga_proctor_unrestricted_scope import evaluate


def polarity_edges(rows, polarity):
    """Edges join literals positive in the selected global orientation."""
    return tuple(sorted({e for _, c in rows for e in combinations(
        sorted(abs(l) for l in c if l * polarity > 0), 2)}))


def plan(n, clauses):
    cs, rows, _ = compress(n, clauses)
    choices = []
    for polarity in (1, -1):
        edges = polarity_edges(rows, polarity)
        cover, matching = cover_plan(edges)
        choices.append((cover, matching, polarity))
    cover, matching, polarity = min(choices, key=lambda v: (len(v[0]), -v[2]))
    return cs, rows, cover, matching, polarity


def _rules(rows, fixed, polarity):
    for i, clause in rows:
        oriented = tuple(l * polarity for l in clause)
        if any(abs(l) in fixed and fixed[abs(l)] == (l > 0)
               for l in oriented):
            continue
        rest = [l for l in oriented if abs(l) not in fixed]
        heads = [l for l in rest if l > 0]
        if len(heads) > 1:
            raise ValueError("non-Horn residual")
        yield i, tuple(-l for l in rest if l < 0), heads[0] if heads else None


def _closure(rules):
    true = set()
    trace = []
    scans = 0
    while True:
        changed = False
        for i, body, head in rules:
            scans += 1
            if all(v in true for v in body):
                if head is None:
                    return None, tuple(trace + [i]), scans
                if head not in true:
                    true.add(head)
                    trace.append(i)
                    changed = True
        if not changed:
            return true, (), scans


def solve(n, clauses, branch_limit=1024):
    """SAT/UNSAT are certified; a budget exhaustion is UNKNOWN, never UNSAT."""
    if type(branch_limit) is not int or branch_limit < 0:
        raise ValueError("invalid branch limit")
    cs, rows, cover, matching, polarity = plan(n, clauses)
    traces = []
    scans = 0
    common = dict(cover=cover, matching=matching, polarity=polarity,
                  branch_limit=branch_limit)
    for j, bits in enumerate(product((False, True), repeat=len(cover))):
        if j >= branch_limit:
            return dict(status="UNKNOWN", branches=j, rule_scans=scans, **common)
        fixed = dict(zip(cover, bits))
        true, trace, work = _closure(tuple(_rules(rows, fixed, polarity)))
        scans += work
        if true is not None:
            oriented = tuple(fixed.get(v, v in true) for v in range(1, n+1))
            witness = oriented if polarity == 1 else tuple(not b for b in oriented)
            if not evaluate(cs, witness):
                raise AssertionError("invalid original witness")
            return dict(status="SAT", witness=witness, branches=j+1,
                        rule_scans=scans, **common)
        traces.append(trace)
    return dict(status="UNSAT", traces=tuple(traces), branches=len(traces),
                rule_scans=scans, **common)


def verify(n, clauses, result):
    """Check original SAT witness or every branch's Horn refutation.

    Does not trust matching, heuristic, counters or compressed clause indices
    other than re-reading the original clauses. UNKNOWN is not a certificate.
    """
    cs, _, _ = compress(n, clauses)
    try:
        if result["status"] == "SAT":
            x = result["witness"]
            return len(x) == n and all(type(v) is bool for v in x) and evaluate(cs, x)
        if result["status"] != "UNSAT":
            return False
        cover = tuple(result["cover"])
        p = result["polarity"]
        if (type(p) is not int or p not in (-1, 1)
            or any(type(v) is not int or not 1 <= v <= n for v in cover)
            or tuple(sorted(set(cover))) != cover):
            return False
        traces = result["traces"]
        if len(traces) != 2 ** len(cover):
            return False
        for bits, trace in zip(product((False, True), repeat=len(cover)), traces):
            fixed = dict(zip(cover, bits))
            true = set()
            if not trace:
                return False
            for j, i in enumerate(trace):
                if type(i) is not int or not 0 <= i < len(cs):
                    return False
                c = {p*l for l in cs[i]}
                if any(-l in c for l in c):
                    return False
                if any(abs(l) in fixed and fixed[abs(l)] == (l > 0) for l in c):
                    return False
                r = {l for l in c if abs(l) not in fixed}
                heads = {l for l in r if l > 0}
                if len(heads) > 1 or any(-l not in true for l in r if l < 0):
                    return False
                if j == len(trace)-1:
                    if heads:
                        return False
                else:
                    if len(heads) != 1 or heads <= true:
                        return False
                    true.update(heads)
        return True
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def obstruction(t):
    """Connected, trivially SAT family with both polarity graphs containing K_t."""
    if type(t) is not int or t < 3:
        raise ValueError("t >= 3 required")
    n = 2*t-1
    cs = tuple(combinations(range(1, t+1), 3)) + tuple(
        tuple(-v for v in c) for c in combinations(range(t, n+1), 3))
    return n, cs


def controls():
    cases = [(0, ()), (2, ())]
    triples = tuple(product((-2, -1, 1, 2), repeat=3))
    cases.extend((2, (c,)) for c in triples)
    cases.extend((2, (a, b)) for a, b in product(triples, repeat=2))
    sat = unsat = 0
    for n, cs in cases:
        r = solve(n, cs, branch_limit=2**n)
        brute = any(evaluate(cs, x) for x in product((False, True), repeat=n))
        if r["status"] != ("SAT" if brute else "UNSAT") or not verify(n, cs, r):
            raise AssertionError((n, cs, r))
        sat += brute
        unsat += not brute
    families = []
    for t in (3, 6, 12, 24):
        n, cs = obstruction(t)
        _, rows, cover, matching, p = plan(n, cs)
        witness = tuple(v <= t for v in range(1, n+1))
        if not evaluate(cs, witness) or len(cover) < t-1:
            raise AssertionError("obstruction failed")
        for sign in (1, -1):
            if len(polarity_edges(rows, sign)) != t*(t-1)//2:
                raise AssertionError("incorrect clique")
        families.append(dict(t=t, n=n, clauses=len(cs), cover=len(cover),
                             exact_minimum=t-1, matching=len(matching), polarity=p))
    return dict(cases=len(cases), sat=sat, unsat=unsat, obstruction=families,
                status="BOUNDED_CONTROLS_ONLY", universal_bound=False,
                machine_refinement=False, independent_review=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(), indent=2))
