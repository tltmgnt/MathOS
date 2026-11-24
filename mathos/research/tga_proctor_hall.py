"""F033: disjoint positive demands, negative conflict cliques, Hall duals.

Incomplete CNF UNSAT preprocessor; no claim about general SAT complexity.
"""
from collections import Counter, deque
from itertools import combinations, product
from random import Random

from . import tga_proctor_xor_cnf as xor
from . import tga_proctor_hybrid_sat as hybrid
from . import tga_proctor_xor_bve as bve
from .tga_proctor_hybrid_adversary import pigeonhole

PNP_RESOLUTION_STATUS = "OPEN"


def _discover(cs):
    """Find disjoint positive demand clauses and capacity-one groups."""
    demands, edges = {}, {}
    for i,c in enumerate(cs):
        s = frozenset(c)
        if s and all(l > 0 for l in s):
            demands.setdefault(tuple(sorted(s)),i)
        elif len(s)==2 and all(l < 0 for l in s):
            edges.setdefault(tuple(sorted(-l for l in s)),i)
    chosen, used = [], set()
    for vs,i in sorted(demands.items(), key=lambda item:(len(item[0]),item[0])):
        if not used.intersection(vs):
            chosen.append((i,vs))
            used.update(vs)
    # Restrict to demand variables. A whole connected conflict component
    # is used only if complete; noncliques fall back to singleton groups.
    adj = {v:set() for v in used}
    for a,b in edges:
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)
    groups, seen = [], set()
    for start in sorted(adj):
        if start in seen:
            continue
        stack, comp = [start], []
        seen.add(start)
        while stack:
            v = stack.pop()
            comp.append(v)
            for w in adj[v]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        comp.sort()
        if all(len(adj[v])==len(comp)-1 for v in comp):
            groups.append(tuple(comp))
        else:
            groups.extend((v,) for v in comp)
    owner = {v:j for j,g in enumerate(groups) for v in g}
    neighbors = tuple(tuple(sorted({owner[v] for v in vs})) for _,vs in chosen)
    return tuple(chosen),tuple(groups),neighbors,edges


def _deficiency(neighbors):
    """Iterative augmenting paths. First failed augmentation gives a Hall set."""
    left_match, right_match = {}, {}
    scans = 0
    for start in range(len(neighbors)):
        queue = deque([start])
        left_seen = {start}
        parent = {}
        free = None
        while queue and free is None:
            u = queue.popleft()
            for v in neighbors[u]:
                scans += 1
                if v in parent:
                    continue
                parent[v] = u
                if v not in right_match:
                    free = v
                    break
                w = right_match[v]
                if w not in left_seen:
                    left_seen.add(w)
                    queue.append(w)
        if free is None:
            # All neighbors of reached left vertices were scanned.
            if len(parent) >= len(left_seen):
                raise AssertionError("invalid failed augmentation")
            return tuple(sorted(left_seen)),scans
        v = free
        while True:
            u = parent[v]
            old = left_match.get(u)
            left_match[u] = v
            right_match[v] = u
            if old is None:
                break
            v = old
    return None,scans


def solve(n, clauses):
    cs = xor._input(n,clauses)
    demands,groups,neighbors,edges = _discover(cs)
    subset,scans = _deficiency(neighbors)
    common = dict(demands=len(demands), groups=len(groups), edge_scans=scans,
                  resolution_status=PNP_RESOLUTION_STATUS)
    if subset is None:
        return dict(status="UNKNOWN",**common)
    used = {v for i in subset for v in demands[i][1]}
    cert_groups = []
    for group in groups:
        vs = tuple(v for v in group if v in used)
        if vs:
            cert_groups.append((vs,tuple(edges[a,b] for a,b in combinations(vs,2))))
    certificate = dict(demands=tuple(sorted(demands[i][0] for i in subset)),
                       groups=tuple(sorted(cert_groups)))
    out = dict(status="UNSAT",certificate=certificate,**common)
    if not verify(n,cs,out):
        raise AssertionError("invalid Hall certificate")
    return out


def verify(n, clauses, result):
    """Replay original demand clauses and all pairwise conflict references.

    No matching, graph discovery or solver invocation. A certificate
    partitions all distinct demand variables into fewer conflict cliques
    than disjoint demands. Each model would choose a distinct clique per
    demand, contradicting the finite pigeonhole principle.
    """
    cs = xor._input(n,clauses)
    try:
        if result["status"] != "UNSAT":
            return False
        cert = result["certificate"]
        ds = tuple(cert["demands"])
        if (not ds or any(type(i) is not int or not 0<=i<len(cs) for i in ds)
                or tuple(sorted(set(ds))) != ds):
            return False
        required = set()
        for i in ds:
            vs = set(cs[i])
            if not vs or any(v<=0 for v in vs) or required.intersection(vs):
                return False
            required.update(vs)
        groups = tuple(cert["groups"])
        if not groups or len(groups)>=len(ds):
            return False
        covered = set()
        for variables,refs in groups:
            vs,refs = tuple(variables),tuple(refs)
            if (not vs or any(type(v) is not int or v not in required for v in vs)
                    or tuple(sorted(set(vs))) != vs or covered.intersection(vs)
                    or len(refs)!=len(vs)*(len(vs)-1)//2):
                return False
            covered.update(vs)
            for (a,b),i in zip(combinations(vs,2),refs):
                if type(i) is not int or not 0<=i<len(cs) or set(cs[i])!={-a,-b}:
                    return False
        return covered == required
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return False


def solve_hybrid(n,clauses,pair_limit=100000,node_limit=1024,*,allow_wide=False):
    """Add Hall inference before the unchanged F032 policy."""
    bve._budget(pair_limit)
    bve._budget(node_limit)
    if type(allow_wide) is not bool:
        raise ValueError("allow_wide must be Boolean")
    cs = xor._input(n,clauses)
    h = solve(n,cs)
    if h["status"] == "UNSAT":
        return dict(status="UNSAT",route="HALL",proof=h,ids=hybrid._ids(cs),
                    pair_tests=0,search_nodes=0,pair_limit=pair_limit,node_limit=node_limit,
                    hall_edge_scans=h["edge_scans"],
                    cost_model="SEPARATE_ABSTRACT_PAIR_NODE_AND_HALL_EDGE_COUNTS",
                    resolution_status=PNP_RESOLUTION_STATUS)
    return dict(hybrid.solve(n,cs,pair_limit,node_limit,allow_wide=allow_wide),
                hall_edge_scans=h["edge_scans"])


def verify_hybrid(n,clauses,result,*,allow_wide=False):
    cs = xor._input(n,clauses)
    try:
        if result["route"]=="HALL":
            return (result["status"]=="UNSAT" and tuple(result["ids"])==hybrid._ids(cs)
                    and verify(n,cs,result["proof"]))
        return hybrid.verify(n,cs,result,allow_wide=allow_wide)
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return False


def matching_cnf(neighbors):
    """One distinct variable per allowed demand/resource edge."""
    resources, rows = {}, []
    top = 0
    for ns in neighbors:
        row = []
        for j in sorted(set(ns)):
            top += 1
            row.append(top)
            resources.setdefault(j,[]).append(top)
        if not row:
            raise ValueError("empty fixture demand")
        rows.append(tuple(row))
    rows.extend((-a,-b) for vs in resources.values() for a,b in combinations(vs,2))
    return top,tuple(rows)


def relabel(n,clauses,seed):
    """Polarity-preserving sparse renaming; randomize clause/literal order."""
    cs = xor._input(n,clauses)
    ids = sorted({abs(l) for c in cs for l in c})
    rng = Random(seed)
    labels = [10**40+31*i for i in range(len(ids))]
    rng.shuffle(labels)
    mapping = dict(zip(ids,labels))
    rows = [tuple(mapping[abs(l)] if l>0 else -mapping[abs(l)] for l in c) for c in cs]
    rows = [tuple(rng.sample(c,len(c))) for c in rows]
    rng.shuffle(rows)
    return 2**200,tuple(rows)


def controls():
    rng = Random(33001)
    random_counts = Counter()
    for _ in range(1500):
        ids = tuple(10**40+19*i for i in range(rng.randrange(1,7)))
        n = 2**200
        cs = tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                         for _ in range(rng.randrange(0,5)))
                   for _ in range(rng.randrange(18)))
        sat = xor._brute(cs)
        r = solve(n,cs)
        if r["status"]=="UNSAT":
            if sat or not verify(n,cs,r):
                raise AssertionError("unsound Hall certificate")
        elif r["status"]!="UNKNOWN" or verify(n,cs,r):
            raise AssertionError("bad status")
        random_counts[r["status"]] += 1
    matching_counts = Counter()
    for seed in range(600):
        left,right = rng.randrange(1,7),rng.randrange(1,7)
        neighbors = tuple(tuple(sorted(rng.sample(range(right),rng.randrange(1,right+1))))
                          for _ in range(left))
        expected = any(len(set(choice))==left for choice in product(*neighbors))
        n,cs = matching_cnf(neighbors)
        n,cs = relabel(n,cs,seed)
        r = solve(n,cs)
        if r["status"]!=("UNKNOWN" if expected else "UNSAT") or verify(n,cs,r)==expected:
            raise AssertionError("matching control failed")
        matching_counts[r["status"]] += 1
    php = []
    for holes in (2,3,4,5,6,7,16,32,64):
        n,cs = pigeonhole(holes)
        n,cs = relabel(n,cs,holes)
        r = solve_hybrid(n,cs,0,0)
        if r["route"]!="HALL" or not verify_hybrid(n,cs,r):
            raise AssertionError("PHP Hall proof failed")
        cert = r["proof"]["certificate"]
        if len(cert["demands"])!=holes+1 or len(cert["groups"])!=holes:
            raise AssertionError("PHP deficiency mismatch")
        php.append(dict(holes=holes,clauses=len(cs),variables=len(r["ids"]),
                        demands=len(cert["demands"]),groups=len(cert["groups"]),
                        conflict_refs=sum(len(ix) for _,ix in cert["groups"]),
                        edge_scans=r["hall_edge_scans"],search_nodes=r["search_nodes"],
                        pair_tests=r["pair_tests"]))
        en,ec = pigeonhole(holes,holes)
        if solve(en,ec)["status"]!="UNKNOWN":
            raise AssertionError("satisfiable PHP refuted")
    return dict(random_cases=1500,random_outcomes=dict(random_counts),
                matching_cases=600,matching_outcomes=dict(matching_counts),php=php,
                resolution_status=PNP_RESOLUTION_STATUS,complete_cnf_solver=False,
                machine_refinement=False,independent_review=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(),indent=2))
