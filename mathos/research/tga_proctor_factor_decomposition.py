"""F025: exact factor-graph decomposition and supplied separator conditioning.

The F024 affine-backdoor engine is used on compact independent components.
No universal small-separator or polynomial-time SAT claim.
"""
from dataclasses import dataclass
from itertools import product
from mathos.research import tga_proctor_unrestricted_scope as prior


@dataclass(frozen=True)
class Component:
    variables: tuple
    clauses: tuple  # compact signed 3-CNF
    indices: tuple  # original clause indices


def normalize(n, clauses, separator=()):
    clauses = tuple(tuple(c) for c in clauses)
    # F024 validates explicit n and signed length-three clauses.
    prior.compile_cnf(n, clauses)
    separator = tuple(separator)
    if (any(type(v) is not int or not 1 <= v <= n for v in separator)
            or len(set(separator)) != len(separator)):
        raise ValueError("invalid separator")
    return clauses, tuple(sorted(separator))


def partition(clauses, fixed):
    """Return (false clause index or None, canonical components).

    Satisfied clauses disappear; false literals are removed. The remaining
    nonempty clauses connect their unfixed variables. Repeated literals pad
    residual clauses to length three without changing their meaning.
    """
    rows = []
    parent = {}
    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    def union(a,b):
        a,b = find(a),find(b)
        if a != b:
            parent[max(a,b)] = min(a,b)
    for i,c in enumerate(clauses):
        if any(abs(l) in fixed and fixed[abs(l)] == (l > 0) for l in c):
            continue
        rest = tuple(l for l in c if abs(l) not in fixed)
        if not rest:
            return i, ()
        vs = [abs(l) for l in rest]
        for v in vs:
            parent.setdefault(v,v)
        for v in vs[1:]:
            union(vs[0],v)
        rows.append((i,rest))
    groups = {}
    for i,c in rows:
        groups.setdefault(find(abs(c[0])),[]).append((i,c))
    result = []
    for _,group in sorted(groups.items()):
        vs = tuple(sorted({abs(l) for _,c in group for l in c}))
        mapping = {v:j+1 for j,v in enumerate(vs)}
        local = []
        for _,c in group:
            row = tuple(mapping[abs(l)] if l>0 else -mapping[abs(l)] for l in c)
            local.append(row+(row[-1],)*(3-len(row)))
        result.append(Component(vs,tuple(local),tuple(i for i,_ in group)))
    return None, tuple(result)


def solve(n, clauses, separator=()):
    clauses,sep = normalize(n,clauses,separator)
    failures = []
    component_calls = affine_branches = steps = 0
    max_components = max_backdoor = 0
    for bits in product((False,True),repeat=len(sep)):
        fixed = dict(zip(sep,bits))
        bad,components = partition(clauses,fixed)
        max_components = max(max_components,len(components))
        if bad is not None:
            failures.append(("clause",bad))
            continue
        witness = [False]*n
        for v,b in fixed.items():
            witness[v-1] = b
        for j,c in enumerate(components):
            component_calls += 1
            max_backdoor = max(max_backdoor,len(prior.backdoor(
                prior.compile_cnf(len(c.variables),c.clauses))))
            r = prior.solve(len(c.variables),c.clauses)
            affine_branches += r["branches"]
            steps += r["affine_structural_steps"]
            if not prior.verify(len(c.variables),c.clauses,r):
                raise AssertionError("invalid component certificate")
            if not r["sat"]:
                failures.append(("component",j,r["duals"]))
                break
            for v,b in zip(c.variables,r["witness"]):
                witness[v-1] = b
        else:
            if not prior.evaluate(clauses,witness):
                raise AssertionError("invalid assembled witness")
            return {"sat":True,"witness":tuple(witness),"failures":(),
                    "separator_branches":len(failures)+1,
                    "component_calls":component_calls,
                    "affine_branches":affine_branches,"affine_structural_steps":steps,
                    "max_components":max_components,"max_backdoor":max_backdoor}
    return {"sat":False,"witness":(),"failures":tuple(failures),
            "separator_branches":len(failures),"component_calls":component_calls,
            "affine_branches":affine_branches,"affine_structural_steps":steps,
            "max_components":max_components,"max_backdoor":max_backdoor}


def verify(n, clauses, separator, result):
    """Recompute decomposition and all separator branches; ignore cost claims."""
    clauses,sep = normalize(n,clauses,separator)
    try:
        if result["sat"] is True:
            x = result["witness"]
            return len(x)==n and all(b in (0,1) for b in x) and prior.evaluate(clauses,x)
        if result["sat"] is not False:
            return False
        fs = result["failures"]
        if len(fs) != 2**len(sep):
            return False
        for bits,proof in zip(product((False,True),repeat=len(sep)),fs):
            bad,cs = partition(clauses,dict(zip(sep,bits)))
            if bad is not None:
                if tuple(proof)!=("clause",bad):
                    return False
            else:
                if len(proof)!=3 or proof[0]!="component":
                    return False
                j = proof[1]
                if type(j) is not int or not 0 <= j < len(cs):
                    return False
                c = cs[j]
                if not prior.verify(len(c.variables),c.clauses,
                                    {"sat":False,"duals":proof[2]}):
                    return False
        return True
    except (KeyError,TypeError,ValueError,IndexError):
        return False


def controls():
    base=((1,1,1),(-1,-1,-1),(1,-2,1),(-1,2,-1))
    fixtures=[(0,(),()),(2,(),(1,2))]
    fixtures += [(2,(a,b),s) for a,b in product(base,repeat=2)
                 for s in ((),(1,),(2,),(1,2))]
    # Two disconnected components, one contradictory.
    fixtures += [(4,((1,2,1),(3,4,3),(-3,-3,-3),(-4,-4,-4)),s)
                 for s in ((),(1,),(3,),(2,4))]
    # Connected before fixing the articulation variable, independent after.
    fixtures += [(5,((1,2,3),(-1,4,5),(2,2,2),(-4,-4,-4)),s)
                 for s in ((),(1,),(1,2))]
    # Every branch directly falsifies one of the original clauses.
    fixtures.append((1,((1,1,1),(-1,-1,-1)),(1,)))
    counts=dict(cases=0,sat=0,unsat=0,separator_branches=0,
                component_calls=0,affine_branches=0,affine_structural_steps=0)
    for n,cs,s in fixtures:
        r = solve(n,cs,s)
        brute = any(prior.evaluate(cs,x) for x in product((False,True),repeat=n))
        assert r["sat"] == brute and verify(n,cs,s,r)
        if not brute:
            assert not verify(n,cs,s,{**r,"failures":r["failures"][:-1]})
            assert not verify(n,cs,s,{**r,"failures":(("component",-1,()),)+r["failures"][1:]})
        counts["cases"] += 1
        counts["sat" if brute else "unsat"] += 1
        for k in ("separator_branches","component_calls","affine_branches","affine_structural_steps"):
            counts[k] += r[k]
    return counts
