"""F032 native syntactic parity extraction with original-clause GF(2) duals.

UNSAT-only incomplete preprocessor, not a port of the missing scratch code.
All discovered equations are entailed by complete forbidden-parity blocks.
"""
from itertools import product
from random import Random

from .tga_proctor_gf2_solver import certificate_solver, verify_result
from .tga_proctor_dynamic_resolution import cubic_graph, tseitin

PNP_RESOLUTION_STATUS = "OPEN"
MAX_WIDTH = 5


def _input(n, clauses):
    if type(n) is not int or n < 0:
        raise ValueError("invalid variable count")
    cs = tuple(tuple(c) for c in clauses)
    if any(any(type(l) is not int or not 1 <= abs(l) <= n for l in c) for c in cs):
        raise ValueError("invalid signed literal")
    return cs


def _signature(c):
    """Return support and bitmask of the unique assignment falsifying c."""
    signs = set(c)
    if any(-l in signs for l in signs):
        return None
    support = tuple(sorted(abs(l) for l in signs))
    if not 1 <= len(support) <= MAX_WIDTH:
        return None
    mask = sum(1 << i for i,v in enumerate(support) if -v in signs)
    return support, mask


def detect(n, clauses):
    """Canonical (variables, rhs, original clause indices) blocks."""
    cs = _input(n, clauses)
    groups = {}
    for i,c in enumerate(cs):
        s = _signature(c)
        if s is not None:
            support, mask = s
            groups.setdefault(support, {}).setdefault(mask, i)
    blocks = []
    for support, patterns in sorted(groups.items()):
        for rhs in (0,1):
            forbidden = [p for p in range(1 << len(support)) if p.bit_count()%2 != rhs]
            if all(p in patterns for p in forbidden):
                blocks.append((support, rhs, tuple(sorted(patterns[p] for p in forbidden))))
    return tuple(blocks)


def solve(n, clauses):
    cs = _input(n, clauses)
    empty = next((i for i,c in enumerate(cs) if not c), None)
    if empty is not None:
        return dict(status="UNSAT", certificate=("empty", empty),
                    recognized_rows=0, affine_variables=0, row_xors=0)
    blocks = detect(n, cs)
    ids = tuple(sorted({v for vs,_,_ in blocks for v in vs}))
    ranks = {v:i for i,v in enumerate(ids)}
    rows = tuple((sum(1 << ranks[v] for v in vs), rhs) for vs,rhs,_ in blocks)
    result = certificate_solver(len(ids), rows)
    if not verify_result(len(ids), rows, result):
        raise AssertionError("GF2 solver certificate invalid")
    common = dict(recognized_rows=len(rows), affine_variables=len(ids),
                  row_xors=result["row_xors"])
    if result["sat"]:
        # Other clauses may constrain or refute this affine model.
        return dict(status="UNKNOWN", **common)
    selected = tuple(blocks[i] for i in result["certificate"])
    out = dict(status="UNSAT", certificate=("xor", selected), **common)
    if not verify(n, cs, out):
        raise AssertionError("original CNF certificate invalid")
    return out


def verify(n, clauses, result):
    """Check original blocks by enumerating local assignments, then XOR sets.

    Does not call detect, signature, GF(2) solver or its bitmask verifier.
    Supports finite ordinary Python proof data, not arbitrary hostile objects.
    """
    cs = _input(n, clauses)
    try:
        if result["status"] != "UNSAT":
            return False
        tag, payload = result["certificate"]
        if tag == "empty":
            return type(payload) is int and 0 <= payload < len(cs) and not cs[payload]
        if tag != "xor":
            return False
        blocks = tuple(payload)
        if not blocks:
            return False
        acc, b, seen = set(), 0, set()
        for support, rhs, indices in blocks:
            support, indices = tuple(support), tuple(indices)
            if (not 1 <= len(support) <= MAX_WIDTH
                    or any(type(v) is not int or not 1 <= v <= n for v in support)
                    or tuple(sorted(set(support))) != support
                    or type(rhs) is not int or rhs not in (0,1)
                    or len(indices) != 1 << (len(support)-1)
                    or any(type(i) is not int or not 0 <= i < len(cs) for i in indices)
                    or tuple(sorted(set(indices))) != indices
                    or (support,rhs) in seen):
                return False
            seen.add((support,rhs))
            local = []
            for i in indices:
                c = set(cs[i])
                if {abs(l) for l in c} != set(support) or any(-l in c for l in c):
                    return False
                local.append(c)
            if len({frozenset(c) for c in local}) != len(local):
                return False
            for bits in product((False,True), repeat=len(support)):
                x = dict(zip(support,bits))
                sat = all(any(x[abs(l)] == (l>0) for l in c) for c in local)
                if sat != (sum(bits)%2 == rhs):
                    return False
            acc.symmetric_difference_update(support)
            b ^= rhs
        return not acc and b == 1
    except (KeyError, TypeError, ValueError, IndexError, AttributeError):
        return False


def encode_parity(support, rhs):
    """Fixture generator independent of block detection."""
    support = tuple(support)
    return tuple(tuple(-v if b else v for v,b in zip(support,bits))
                 for bits in product((False,True),repeat=len(support))
                 if sum(bits)%2 != rhs)


def _brute(cs):
    ids = tuple(sorted({abs(l) for c in cs for l in c}))
    for bits in product((False,True),repeat=len(ids)):
        x = dict(zip(ids,bits))
        if all(any(x[abs(l)] == (l>0) for l in c) for c in cs):
            return True
    return False


def controls():
    rng = Random(32001)
    n = 2**100
    counts = dict(random_cases=0, certified_unsat=0, unknown=0, brute_sat=0)
    for j in range(3000):
        ids = tuple(10**9+31*i for i in range(rng.randrange(1,7)))
        cs = tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                         for _ in range(rng.randrange(1,6)))
                   for _ in range(rng.randrange(14)))
        if j%3 == 0:
            support = tuple(sorted(rng.sample(ids, rng.randrange(1,min(5,len(ids))+1))))
            cs += encode_parity(support,0) + encode_parity(support,1)
        sat = _brute(cs)
        out = solve(n,cs)
        if out["status"] == "UNSAT":
            if sat or not verify(n,cs,out):
                raise AssertionError("unsound parity refutation")
            counts["certified_unsat"] += 1
        elif out["status"] == "UNKNOWN" and not verify(n,cs,out):
            counts["unknown"] += 1
        else:
            raise AssertionError("bad result status")
        counts["random_cases"] += 1
        counts["brute_sat"] += sat
    graphs = []
    for q in (4,8,16,32,64,128,256,400):
        for seed in (11,29):
            edges = cubic_graph(q,seed)
            m, cs = tseitin(q,edges,(True,)+(False,)*(q-1))
            out = solve(m,cs)
            if (out["status"] != "UNSAT" or not verify(m,cs,out)
                    or out["recognized_rows"] != q
                    or len(out["certificate"][1]) != q):
                raise AssertionError("odd Tseitin block refutation invalid")
            even_n, even_cs = tseitin(q,edges,(False,)*q)
            even = solve(even_n,even_cs)
            if even["status"] != "UNKNOWN" or even["recognized_rows"] != q:
                raise AssertionError("even Tseitin negative control failed")
            graphs.append(dict(vertices=q, seed=seed, variables=m, clauses=len(cs),
                               rows=out["recognized_rows"], dual_rows=len(out["certificate"][1]),
                               row_xors=out["row_xors"], even_status=even["status"]))
    return dict(**counts, graphs=graphs, max_width=MAX_WIDTH,
                resolution_status=PNP_RESOLUTION_STATUS, complete_cnf_solver=False,
                row_xors_are_bit_steps=False, machine_refinement=False,
                independent_review=False, original_scratch_port=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(), indent=2))
