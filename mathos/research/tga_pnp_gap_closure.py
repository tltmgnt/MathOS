"""TGA-PNP: constructive join-tree gap, local consistency and bridge ledger.

Zero overlap deficit certifies a clause-scope join tree, not SAT itself.
Positive deficit is not an UNSAT certificate. F026 supplies exact tables;
F030 is a bounded fallback. No unrestricted polynomial-time claim.
"""
from itertools import combinations, product
from mathos.research.tga_proctor_renamable_horn import sparse_input
from mathos.research.tga_proctor_affine_backdoor import compress
from mathos.research import tga_proctor_tree_decomposition as tree
from mathos.research import tga_proctor_adaptive_propagation as adaptive
from mathos.research.tga_proctor_unrestricted_scope import evaluate
from mathos.proof_analysis.gap_analysis import Claim, analyze
from mathos.research.tga_universal_bridges import graph as inherited_graph


def scope_bags(n, clauses):
    ids, cs = sparse_input(n, clauses)
    _, rows, _ = compress(len(ids), cs)
    bags = tuple(sorted({tuple(sorted(abs(l) for l in c)) for _, c in rows})) or ((),)
    return ids, cs, rows, bags


def topology(bags):
    """Maximum weight spanning tree on scopes; zero edges join components."""
    t = len(bags)
    if not t:
        raise ValueError("nonempty bags required")
    sets = tuple(map(set, bags))
    target = sum(map(len, sets)) - len(set().union(*sets))
    candidates = sorted((-len(sets[i] & sets[j]), i, j)
                        for i, j in combinations(range(t), 2))
    parent = list(range(t))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    edges, weight = [], 0
    for neg, i, j in candidates:
        a, b = root(i), root(j)
        if a != b:
            parent[b] = a
            edges.append((i, j))
            weight -= neg
            if len(edges) == t-1:
                break
    gap = target - weight
    if gap < 0:
        raise AssertionError("impossible overlap deficit")
    return dict(bags=bags, edges=tuple(edges), overlap_weight=weight,
                overlap_target=target, gap=gap,
                candidate_edges=len(candidates))


def local_consistency(rows, bags):
    """Pairwise semijoin fixed point on original clause-scope relations."""
    scopes = tuple(map(set, bags))
    by_scope = {b: [] for b in bags}
    for _, c in rows:
        by_scope[tuple(sorted(abs(l) for l in c))].append(c)
    tables = []
    for b in bags:
        tables.append([bits for bits in product((False, True), repeat=len(b))
                       if tree.local_ok(by_scope[b], dict(zip(b, bits)))])
    pairs = [(i, j, tuple(sorted(scopes[i] & scopes[j])))
             for i in range(len(bags)) for j in range(len(bags)) if i != j]
    while True:
        changed = False
        for i, j, shared in pairs:
            pi = tuple(bags[i].index(v) for v in shared)
            pj = tuple(bags[j].index(v) for v in shared)
            support = {tuple(y[k] for k in pj) for y in tables[j]}
            keep = [x for x in tables[i] if tuple(x[k] for k in pi) in support]
            changed |= len(keep) != len(tables[i])
            tables[i] = keep
        if not changed:
            return tuple(tuple(t) for t in tables)


def solve(n, clauses, node_limit=1024):
    if type(node_limit) is not int or node_limit < 0:
        raise ValueError("invalid fallback node limit")
    ids, cs, rows, bags = scope_bags(n, clauses)
    g = topology(bags)
    if not g["gap"]:
        result = tree.solve(len(ids), tuple(cs[i] for i, _ in rows), bags, g["edges"])
        if result["sat"] and not evaluate(cs, result["witness"]):
            raise AssertionError("original witness failed")
        return dict(status="SAT" if result["sat"] else "UNSAT",
                    method="JOIN_TREE", ids=ids, topology=g, evidence=result)
    result = adaptive.solve(n, tuple(tuple(ids[abs(l)-1] if l > 0 else -ids[abs(l)-1]
                                          for l in c) for c in cs), node_limit)
    return dict(status=result["status"], method="ADAPTIVE", ids=ids,
                topology=g, evidence=result)


def verify(n, clauses, result):
    ids, cs, rows, bags = scope_bags(n, clauses)
    try:
        if tuple(result["ids"]) != ids:
            return False
        g = topology(bags)
        if result["topology"] != g:
            return False
        e = result["evidence"]
        if result["status"] not in ("SAT", "UNSAT"):
            return False
        if result["method"] == "JOIN_TREE" and g["gap"] == 0:
            if e["sat"] is not (result["status"] == "SAT"):
                return False
            return (tree.verify(len(ids), tuple(cs[i] for i, _ in rows), bags, g["edges"], e)
                    and (not e["sat"] or evaluate(cs, e["witness"])))
        if result["method"] == "ADAPTIVE" and g["gap"] > 0:
            original = tuple(tuple(ids[abs(l)-1] if l > 0 else -ids[abs(l)-1]
                                   for l in c) for c in cs)
            return e["status"] == result["status"] and adaptive.verify(n, original, e)
        return False
    except (KeyError, ValueError, TypeError, IndexError):
        return False


def parity_cycle(n, odd):
    """n binary equality edges, with optional last edge inequality."""
    if type(n) is not int or n < 3 or type(odd) is not bool:
        raise ValueError("cycle requires n >= 3 and Boolean parity")
    clauses = []
    for i in range(1, n+1):
        j = i % n + 1
        if odd and i == n:
            clauses.extend(((i, j, j), (-i, -j, -j)))
        else:
            clauses.extend(((-i, j, j), (i, -j, -j)))
    return tuple(clauses)


def bridge_report():
    g = inherited_graph()
    leaves = {
        "PNP.tga_faithful": "Faithful constructive representation of all encoded SAT",
        "PNP.tga_complete": "Complete obstruction characterization and correct closure",
        "PNP.tga_termination": "Termination for every input including malformed encodings",
        "PNP.tga_size": "Uniform polynomial intermediate representation and state count",
        "PNP.tga_bit_time": "Uniform polynomial total bit time including construction and replay",
        "PNP.tga_standard_bridge": "Faithful standard machine and NP-completeness bridge",
    }
    for k, label in leaves.items():
        g[k] = Claim(label, "open")
    g["PNP.tga_route"] = Claim("TGA-based unrestricted polynomial SAT", "derived",
                               (tuple(leaves),))
    # Preserve the canonical routes; this is an additional modeled route only.
    g["PNP"] = Claim(g["PNP"].label, "derived",
                     g["PNP"].routes + (("PNP.tga_route",),))
    return analyze(g, "PNP")


def controls():
    triples = tuple(product((-2, -1, 1, 2), repeat=3))
    cases = [(0, ()), (2, ())] + [(2, (c,)) for c in triples]
    cases += [(2, (a, b)) for a, b in product(triples, repeat=2)]
    signs = tuple(tuple(s*(i+1) for i, s in enumerate(p))
                  for p in product((-1, 1), repeat=3))
    cases += [(3, tuple(c for i, c in enumerate(signs) if mask >> i & 1))
              for mask in range(256)]
    for n, cs in cases:
        r = solve(n, cs, 2**(n+1)-1)
        brute = any(evaluate(cs, x) for x in product((False, True), repeat=n))
        if r["status"] != ("SAT" if brute else "UNSAT") or not verify(n, cs, r):
            raise AssertionError("decision mismatch")
    cycles = []
    for n in (3, 4, 8, 16, 32):
        a, b = parity_cycle(n, False), parity_cycle(n, True)
        _, _, ra, ba = scope_bags(n, a)
        _, _, rb, bb = scope_bags(n, b)
        ga, gb = topology(ba), topology(bb)
        ta, tb = local_consistency(ra, ba), local_consistency(rb, bb)
        if ga != gb or ga["gap"] != 1 or not all(ta) or not all(tb):
            raise AssertionError("cycle obstruction mismatch")
        sa, sb = solve(n, a, 4*n+1), solve(n, b, 4*n+1)
        if (sa["status"], sb["status"]) != ("SAT", "UNSAT") or not (
                verify(n, a, sa) and verify(n, b, sb)):
            raise AssertionError("cycle decision mismatch")
        cycles.append(dict(n=n, gap=ga["gap"], local_tables_nonempty=True,
                           even_status=sa["status"], odd_status=sb["status"]))
    n = 64
    cs = tuple((-i, i+1, i+1) for i in range(1,n)) + ((1,1,1),)
    r = solve(n, cs, 0)
    if r["method"] != "JOIN_TREE" or r["status"] != "SAT" or not verify(n, cs, r):
        raise AssertionError("chain gap closure failed")
    return dict(cases=len(cases), cycles=cycles,
                chain=dict(n=n, gap=r["topology"]["gap"],
                           table_candidates=r["evidence"]["table_candidates"]),
                proof_obligations=bridge_report(), resolution_status="OPEN",
                universal_bound=False, machine_refinement=False, independent_review=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(), indent=2))
