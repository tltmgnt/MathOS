"""F032 hybrid certificate router, not a universal polynomial SAT solver.

Direct XOR, blind bounded elimination, then width-three dynamic search.
Separate abstract pair and node budgets; original-CNF SAT witnesses.
"""
from collections import Counter
from random import Random

from . import tga_proctor_xor_cnf as xor
from . import tga_proctor_xor_bve as bve
from . import tga_proctor_blind_parity as blind
from . import tga_proctor_dynamic_components as dynamic
from .tga_proctor_dynamic_resolution import cubic_graph, tseitin

PNP_RESOLUTION_STATUS = "OPEN"
ROUTES = ("DIRECT_XOR", "BVE_XOR", "DYNAMIC_ORIGINAL", "DYNAMIC_PROJECTED")


def _ids(cs):
    return tuple(sorted({abs(l) for c in cs for l in c}))


def _holds(cs, x):
    return all(any(x[abs(l)] == (l > 0) for l in c) for c in cs)


def _narrow(cs):
    return all(len(c) <= 3 for c in cs)


def _lift(cs, pre, result):
    """Back-substitute from a verified residual SAT result.

    The caller has checked the exact projection log. Reconstruct line
    literals, default absent non-eliminated variables to false, restore
    each pivot in reverse order. Final original witness is checked.
    """
    lines = [set(c) for c in cs]
    for a, b, v in pre["steps"]:
        lines.append((lines[a]-{v}) | (lines[b]-{-v}))
    eliminated = {v for v,_,_,_ in pre["eliminations"]}
    x = {v:False for v in _ids(cs) if v not in eliminated}
    x.update(zip(result["ids"], result["witness"]))
    for v,pos,neg,_ in reversed(pre["eliminations"]):
        require_true = any(not any(x[abs(l)] == (l>0) for l in lines[i] if l != v)
                           for i in pos)
        require_false = any(not any(x[abs(l)] == (l>0) for l in lines[i] if l != -v)
                            for i in neg)
        if require_true and require_false:
            raise AssertionError("projection back-substitution conflict")
        x[v] = require_true
    if not _holds(cs,x):
        raise AssertionError("lifted witness invalid")
    return tuple(x[v] for v in _ids(cs))


def solve(n, clauses, pair_limit=100000, node_limit=1024):
    bve._budget(pair_limit)
    bve._budget(node_limit)
    cs = xor._input(n,clauses)
    ids = _ids(cs)
    pairs = nodes = 0

    def report(status, route, **kw):
        out = dict(status=status, route=route, ids=ids,
                   pair_tests=pairs, search_nodes=nodes,
                   pair_limit=pair_limit, node_limit=node_limit,
                   cost_model="SEPARATE_ABSTRACT_PAIR_AND_NODE_COUNTS",
                   resolution_status=PNP_RESOLUTION_STATUS, **kw)
        if status != "UNKNOWN" and not verify(n,cs,out):
            raise AssertionError("hybrid certificate rejected")
        return out

    direct = xor.solve(n,cs)
    if direct["status"] == "UNSAT":
        return report("UNSAT","DIRECT_XOR", proof=direct)
    reduced = blind.solve(n,cs,pair_limit=pair_limit)
    pairs = reduced["pair_tests"]
    if pairs > pair_limit:
        raise AssertionError("pair budget exceeded")
    if reduced["status"] == "UNSAT":
        return report("UNSAT","BVE_XOR", proof=reduced)
    if node_limit == 0:
        return report("UNKNOWN","NONE", reason="ZERO_SEARCH_BUDGET")
    pre = reduced["preprocessing"]
    residual = bve.replay(n,cs,pre)
    if residual is None:
        raise AssertionError("invalid preprocessing log")
    if _narrow(residual):
        route, target = "DYNAMIC_PROJECTED", residual
    elif _narrow(cs):
        route, target = "DYNAMIC_ORIGINAL", cs
    else:
        return report("UNKNOWN","NONE", reason="UNSUPPORTED_SEARCH_WIDTH")
    search = dynamic.solve(n,target,node_limit)
    nodes = search["nodes"]
    if nodes > node_limit:
        raise AssertionError("node budget exceeded")
    if search["status"] == "UNKNOWN":
        return report("UNKNOWN","NONE", reason="SEARCH_BUDGET")
    if not dynamic.verify(n,target,search):
        raise AssertionError("dynamic proof rejected")
    if search["status"] == "SAT":
        w = _lift(cs,pre,search) if route == "DYNAMIC_PROJECTED" else search["witness"]
        return report("SAT",route,witness=w)
    if route == "DYNAMIC_PROJECTED":
        return report("UNSAT",route,proof=(pre,search))
    return report("UNSAT",route,proof=search)


def verify(n, clauses, result):
    """Check original SAT witness or dispatch an UNSAT certificate.

    Costs, reason, solver scheduling and search order are not evidence.
    UNKNOWN is never accepted as a certificate.
    """
    cs = xor._input(n,clauses)
    try:
        ids = _ids(cs)
        if tuple(result["ids"]) != ids:
            return False
        route, status = result["route"], result["status"]
        if status == "SAT":
            w = tuple(result["witness"])
            return (route in ("DYNAMIC_ORIGINAL","DYNAMIC_PROJECTED")
                    and len(w) == len(ids) and all(type(b) is bool for b in w)
                    and _holds(cs,dict(zip(ids,w))))
        if status != "UNSAT":
            return False
        proof = result["proof"]
        if proof is None:
            return False
        if route == "DIRECT_XOR":
            return xor.verify(n,cs,proof)
        if route == "BVE_XOR":
            return bve.verify(n,cs,proof)
        if route == "DYNAMIC_ORIGINAL":
            return (_narrow(cs) and proof["status"] == "UNSAT"
                    and dynamic.verify(n,cs,proof))
        if route == "DYNAMIC_PROJECTED":
            pre, search = proof
            residual = bve.replay(n,cs,pre)
            return (residual is not None and _narrow(residual)
                    and search["status"] == "UNSAT" and dynamic.verify(n,residual,search))
        return False
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return False


def controls():
    rng = Random(32004)
    counts = Counter()
    routes = Counter()
    for width in (3,5):
        for _ in range(700):
            ids = tuple(10**40+37*i for i in range(rng.randrange(1,7)))
            n = 2**200
            cs = tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                             for _ in range(rng.randrange(width+1)))
                       for _ in range(rng.randrange(15)))
            sat = xor._brute(cs)
            for pairs,nodes in ((20,10000),(0,0),(3,1)):
                r = solve(n,cs,pairs,nodes)
                status = r["status"]
                if r["pair_tests"] > pairs or r["search_nodes"] > nodes:
                    raise AssertionError("budget violation")
                if status == "UNKNOWN":
                    if verify(n,cs,r):
                        raise AssertionError("unknown accepted")
                    if width == 3 and nodes == 10000:
                        raise AssertionError("unexpected width-three exhaustion")
                elif status != ("SAT" if sat else "UNSAT") or not verify(n,cs,r):
                    raise AssertionError("unsound hybrid decision")
                counts[status] += 1
                routes[r["route"]] += 1
    graphs = []
    for q in (4,8,16,32,64,80):
        n,cs = tseitin(q,cubic_graph(q,11),(True,)+(False,)*(q-1))
        m,hidden = blind.chain_split(n,cs,29,2)
        sn,shuffled = blind.relabel(m,hidden,47)
        direct = solve(n,cs,0,0)
        recovered = solve(sn,shuffled,1000,0)
        gn,guarded = blind.shared_selector(n,cs)
        negative = solve(gn,guarded,1000,10000)
        if (direct["route"] != "DIRECT_XOR" or recovered["route"] != "BVE_XOR"
                or not verify(n,cs,direct) or not verify(sn,shuffled,recovered)
                or negative["status"] != "UNKNOWN"
                or negative["reason"] != "UNSUPPORTED_SEARCH_WIDTH"):
            raise AssertionError("hybrid family mismatch")
        graphs.append(dict(vertices=q, direct_route=direct["route"],
                           recovered_route=recovered["route"], pair_tests=recovered["pair_tests"],
                           search_nodes=recovered["search_nodes"],
                           shared_selector_status=negative["status"]))
    return dict(random_formulas=1400, budgeted_runs=4200, outcomes=dict(counts),
                routes=dict(routes), graph_controls=graphs,
                resolution_status=PNP_RESOLUTION_STATUS, universal_bound=False,
                machine_refinement=False, independent_review=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(),indent=2))
