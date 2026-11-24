"""Native bounded Davis–Putnam elimination followed by F032 parity replay.

Explicit projection log, resolution parents and original-clause UNSAT proof.
Incomplete, UNSAT-only; no universal SAT or machine-refinement claim.
"""
from itertools import product
from random import Random

from . import tga_proctor_xor_cnf as xor
from .tga_proctor_dynamic_resolution import cubic_graph, tseitin

PNP_RESOLUTION_STATUS = "OPEN"


def _canonical(c):
    return tuple(sorted(set(c)))


def _taut(c):
    return any(-l in c for l in c)


def _initial(cs):
    active = {}
    for i,c in enumerate(cs):
        c = _canonical(c)
        if not _taut(set(c)):
            active.setdefault(c,i)
    return active


def _budget(k):
    if type(k) is not int or k < 0:
        raise ValueError("nonnegative integer budget required")


def eliminate(n, clauses, order=None, pair_limit=100000, max_width=5):
    """Bound total tested pairs and accepted resolvent width; no clause growth.

    Skipped pivots are left untouched. Explicit order is optional; default
    visits occurring IDs in descending order once (not an oracle).
    """
    _budget(pair_limit)
    _budget(max_width)
    cs = xor._input(n,clauses)
    ids = {abs(l) for c in cs for l in c}
    order = tuple(sorted(ids,reverse=True)) if order is None else tuple(order)
    if (any(type(v) is not int or v not in ids for v in order)
            or len(set(order)) != len(order)):
        raise ValueError("invalid elimination order")
    active = _initial(cs)
    lines = [_canonical(c) for c in cs]
    steps, log = [], []
    pairs = skipped = 0
    for v in order:
        pos = sorted((i for c,i in active.items() if v in c))
        neg = sorted((i for c,i in active.items() if -v in c))
        if not pos and not neg:
            continue
        if len(pos)*len(neg) > pair_limit-pairs:
            skipped += 1
            continue
        rest = {c:i for c,i in active.items() if v not in c and -v not in c}
        new = {}
        wide = False
        for a in pos:
            for b in neg:
                pairs += 1
                c = _canonical((set(lines[a])-{v}) | (set(lines[b])-{-v}))
                if _taut(set(c)):
                    continue
                if len(c) > max_width:
                    wide = True
                if c not in rest:
                    new.setdefault(c,(a,b))
        if wide or len(new) > len(pos)+len(neg):
            skipped += 1
            continue
        added = []
        for c,(a,b) in sorted(new.items()):
            i = len(lines)
            steps.append((a,b,v))
            lines.append(c)
            rest[c] = i
            added.append(i)
        log.append((v,tuple(pos),tuple(neg),tuple(added)))
        active = rest
    residual = tuple(sorted(active.values()))
    return dict(steps=tuple(steps), eliminations=tuple(log), residual=residual,
                pair_tests=pairs, pair_limit=pair_limit, max_width=max_width,
                skipped=skipped, eliminated=len(log),
                clauses=tuple(lines[i] for i in residual))


def replay(n, clauses, proof):
    """Verify exact projection batches and reconstruct final clauses.

    Checks all resolution parents/pivots, complete non-tautological
    cross-products, no growth, width and exact active-set deletion.
    The claimed search counters and skipped-pivot order are not evidence.
    Returns reconstructed residual or None on malformed proof.
    """
    cs = xor._input(n,clauses)
    try:
        width = proof["max_width"]
        _budget(width)
        # Rebuild originals with sets, independently of _initial.
        lines = [frozenset(c) for c in cs]
        active = {}
        for i,c in enumerate(lines):
            if not any(-l in c for l in c) and c not in active:
                active[c] = i
        steps = tuple(proof["steps"])
        cursor = 0
        used = set()
        for v,positive,negative,added in proof["eliminations"]:
            if type(v) is not int or not 1 <= v <= n or v in used:
                return None
            used.add(v)
            pos = tuple(sorted(i for c,i in active.items() if v in c))
            neg = tuple(sorted(i for c,i in active.items() if -v in c))
            if (not pos and not neg or tuple(positive) != pos or tuple(negative) != neg
                    or any(type(i) is not int for i in (*positive,*negative))):
                return None
            rest = {c:i for c,i in active.items() if v not in c and -v not in c}
            expected = set()
            for a in pos:
                for b in neg:
                    c = (lines[a]-{v}) | (lines[b]-{-v})
                    if any(-l in c for l in c):
                        continue
                    if len(c) > width:
                        return None
                    if c not in rest:
                        expected.add(c)
            added = tuple(added)
            if len(added) != len(expected) or len(added) > len(pos)+len(neg):
                return None
            for i in added:
                if type(i) is not int or i != len(lines) or cursor >= len(steps):
                    return None
                a,b,p = steps[cursor]
                cursor += 1
                if (type(a) is not int or type(b) is not int or type(p) is not int
                        or p != v or a not in pos or b not in neg):
                    return None
                c = (lines[a]-{v}) | (lines[b]-{-v})
                if c not in expected:
                    return None
                expected.remove(c)
                lines.append(c)
                rest[c] = i
            if expected:
                return None
            active = rest
        residual = tuple(proof["residual"])
        if (cursor != len(steps) or any(type(i) is not int for i in residual)
                or residual != tuple(sorted(active.values()))):
            return None
        return tuple(tuple(sorted(lines[i])) for i in residual)
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return None


def solve(n, clauses, order=None, pair_limit=100000, max_width=5):
    cs = xor._input(n,clauses)
    pre = eliminate(n,cs,order,pair_limit,max_width)
    result = xor.solve(n,pre["clauses"])
    out = dict(status=result["status"], preprocessing=pre, parity=result,
               pair_tests=pre["pair_tests"], eliminated=pre["eliminated"],
               resolution_lines=len(pre["steps"]), recognized_rows=result["recognized_rows"])
    if result["status"] == "UNSAT" and not verify(n,cs,out):
        raise AssertionError("combined proof rejected")
    return out


def verify(n, clauses, result):
    cs = xor._input(n,clauses)
    try:
        if result["status"] != "UNSAT":
            return False
        reduced = replay(n,cs,result["preprocessing"])
        return reduced is not None and xor.verify(n,reduced,result["parity"])
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return False


def obfuscate(n, clauses, seed):
    """Split each width-three clause using a private fresh auxiliary.

    C=(a,b,c) becomes (a,z) AND (-z,b,c), with seeded literal order.
    Existentially eliminating z restores C exactly. Fresh IDs are n+i+1.
    """
    cs = xor._input(n,clauses)
    if any(len(c)!=3 or len({abs(l) for l in c})!=3 for c in cs):
        raise ValueError("expected three distinct variables per clause")
    rng = Random(seed)
    out = []
    for i,c in enumerate(cs,1):
        a,b,c = rng.sample(c,3)
        z = n+i
        out.extend(((a,z),(-z,b,c)))
    return n+len(cs),tuple(out)


def controls():
    rng = Random(32002)
    counts = dict(random_cases=0, certified_unsat=0, unknown=0, brute_sat=0)
    for _ in range(1500):
        ids = tuple(10**9+17*i for i in range(rng.randrange(1,7)))
        n = 2**100
        cs = tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                         for _ in range(rng.randrange(0,5)))
                   for _ in range(rng.randrange(14)))
        limit = rng.randrange(20)
        r = solve(n,cs,pair_limit=limit,max_width=3)
        reduced = replay(n,cs,r["preprocessing"])
        sat = xor._brute(cs)
        if (reduced is None or xor._brute(reduced)!=sat
                or r["pair_tests"]>limit or len(reduced)>len(cs)):
            raise AssertionError("projection mismatch")
        if r["status"]=="UNSAT":
            if sat or not verify(n,cs,r):
                raise AssertionError("unsound combined proof")
            counts["certified_unsat"] += 1
        elif r["status"]=="UNKNOWN" and not verify(n,cs,r):
            counts["unknown"] += 1
        else:
            raise AssertionError("invalid status")
        counts["random_cases"] += 1
        counts["brute_sat"] += sat
    fixtures = []
    for q in (4,8,16,32,64,80):
        for seed in (11,29):
            edges = cubic_graph(q,seed)
            n,cs = tseitin(q,edges,(True,)+(False,)*(q-1))
            m,hidden = obfuscate(n,cs,seed)
            direct = xor.solve(m,hidden)
            r = solve(m,hidden,order=range(n+1,m+1),pair_limit=len(cs))
            if (direct["status"]!="UNKNOWN" or direct["recognized_rows"]!=0
                    or r["status"]!="UNSAT" or not verify(m,hidden,r)
                    or r["eliminated"]!=len(cs) or r["resolution_lines"]!=len(cs)
                    or set(r["preprocessing"]["clauses"])!={_canonical(c) for c in cs}):
                raise AssertionError("obfuscated fixture recovery failed")
            limited = solve(m,hidden,order=range(n+1,m+1),pair_limit=0)
            if limited["status"]!="UNKNOWN" or limited["pair_tests"]!=0:
                raise AssertionError("zero pair budget mismatch")
            _,even = tseitin(q,edges,(False,)*q)
            em,eh = obfuscate(n,even,seed)
            er = solve(em,eh,order=range(n+1,em+1),pair_limit=len(even))
            if er["status"]!="UNKNOWN" or er["recognized_rows"]!=q:
                raise AssertionError("even charge control failed")
            fixtures.append(dict(vertices=q,seed=seed,hidden_variables=m,
                                 hidden_clauses=len(hidden),direct_rows=0,
                                 recovered_rows=r["recognized_rows"],
                                 pair_tests=r["pair_tests"],resolution_lines=r["resolution_lines"],
                                 even_status=er["status"]))
    return dict(**counts,fixtures=fixtures,order_uses_known_auxiliaries=True,
                resolution_status=PNP_RESOLUTION_STATUS,complete_cnf_solver=False,
                machine_refinement=False,independent_review=False,original_scratch_port=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(),indent=2))
