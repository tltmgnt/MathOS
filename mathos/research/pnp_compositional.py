"""Certified componentwise strong backdoors into the v7 relation algebras.

The target class is syntactic: a normalized residual must compile entirely
into one of the v7 direct modes. Different branches/components may use
different modes. No universal SAT or algorithm-independent lower bound.
"""
from itertools import combinations, product

from .pnp_structural_kernel import normalize
from .pnp_constraint_algebra import MODES, propose, verify

MAX_K = 3
MAX_CANDIDATES = 256


def components(n, f, budget):
    """Partition normalized clauses by shared variables (union-find)."""
    parent = list(range(n+1))
    def root(v):
        while parent[v] != v:
            budget.tick()
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    for c in f:
        budget.tick(1 + len(c))
        if c:
            a = abs(c[0])
            for x in c[1:]:
                parent[root(abs(x))] = root(a)
    groups = {}
    for i, c in enumerate(f):
        budget.tick()
        key = root(abs(c[0])) if c else 0
        groups.setdefault(key, []).append(i)
    return tuple(tuple(v) for v in sorted(groups.values()))


def _restrict(f, vs, bits, budget):
    fixed = dict(zip(vs, bits))
    residual = []
    for c in f:
        budget.tick(1 + len(c))
        if any(fixed.get(abs(x)) == (x > 0) for x in c):
            continue
        residual.append(tuple(x for x in c if abs(x) not in fixed))
    return tuple(residual)


def _direct(n, f, budget):
    for mode in MODES:
        p = propose(n, f, mode, budget)
        if p is not None:
            verify(n, f, p, budget)
            return p
    return None


def _candidate(n, f, vs, budget):
    branches = []
    for bits in product((False, True), repeat=len(vs)):
        budget.tick()
        proof = _direct(n, _restrict(f, vs, bits, budget), budget)
        if proof is None:
            return None
        branches.append({"values": bits, "proof": proof})
    return {"backdoor": vs, "branches": branches,
            "sat": any(not b["proof"]["clauses"] for b in branches)}


def _options(k, candidate_limit):
    if type(k) is not int or not 0 <= k <= MAX_K:
        raise ValueError("k must be in 0..3")
    if type(candidate_limit) is not int or not 1 <= candidate_limit <= MAX_CANDIDATES:
        raise ValueError("candidate limit must be in 1..256")


def search(n, clauses, budget, *, k=2, candidate_limit=MAX_CANDIDATES):
    """Try subsets by increasing size, then lexicographic order per component.

    All 2^|B| assignments must compile, even if a SAT leaf was already found:
    this proves strong, rather than weak, backdoor membership for B. A failed
    bounded search reports unknown. Search and certificate size are distinct.
    """
    _options(k, candidate_limit)
    nn, f, mapping = normalize(n, clauses)
    pieces = components(nn, f, budget)
    certified, unresolved = [], []
    for indices in pieces:
        local = tuple(f[i] for i in indices)
        active = sorted({abs(x) for c in local for x in c})
        tried = 0
        found = None
        stopped = False
        for size in range(min(k, len(active))+1):
            for vs in combinations(active, size):
                if tried >= candidate_limit:
                    stopped = True
                    break
                tried += 1
                budget.tick()
                found = _candidate(nn, local, vs, budget)
                if found is not None:
                    break
            if found is not None or stopped:
                break
        if found is None:
            unresolved.append({"clause_indices": indices, "candidates_tried": tried,
                               "reason": "candidate_limit" if stopped else "no_backdoor_within_k"})
        else:
            certified.append({"clause_indices": indices, "candidates_tried": tried, **found})
    if any(not p["sat"] for p in certified):
        decision = "unsat"
    elif unresolved:
        decision = "unknown"
    else:
        decision = "sat"
    artifact = {"schema": "mathos-pnp-compositional/1", "normalized_n": nn,
                "new_to_old": mapping, "k": k, "candidate_limit": candidate_limit,
                "certified_components": certified, "unresolved_components": unresolved,
                "decision": decision, "complete_strong_backdoor_cover": not unresolved,
                "leaf_count": sum(len(p["branches"]) for p in certified)}
    verify_certificate(n, clauses, artifact, budget)
    return artifact


def verify_certificate(n, clauses, artifact, budget):
    """Replay disjoint variable partition, complete branch coverage, and leaves.

    Does not trust the union-find search, minimality, or failed-search claims.
    A partition may be coarser than connected components but may not share
    variables across pieces or omit normalized clauses.
    """
    nn, f, mapping = normalize(n, clauses)
    k, limit = artifact["k"], artifact["candidate_limit"]
    _options(k, limit)
    if (artifact["schema"] != "mathos-pnp-compositional/1" or
            type(artifact["normalized_n"]) is not int or artifact["normalized_n"] != nn or
            tuple(artifact["new_to_old"]) != mapping):
        raise ValueError("normalization mismatch")
    used_clauses, used_vars = set(), set()
    decisions = []
    count = 0
    certs, unknown = artifact["certified_components"], artifact["unresolved_components"]
    for certified, pieces in ((True, certs), (False, unknown)):
        for p in pieces:
            ids = p["clause_indices"]
            if (not ids or any(type(i) is not int or not 0 <= i < len(f) for i in ids) or
                    len(set(ids)) != len(ids) or used_clauses.intersection(ids)):
                raise ValueError("invalid clause partition")
            used_clauses.update(ids)
            local = tuple(f[i] for i in ids)
            active = {abs(x) for c in local for x in c}
            budget.tick(1 + sum(map(len, local)))
            if used_vars.intersection(active):
                raise ValueError("components share variables")
            used_vars.update(active)
            if not certified:
                continue  # failure metadata is informational, never a proof
            vs = tuple(p["backdoor"])
            if (len(vs) > k or any(type(v) is not int or v not in active for v in vs)
                    or tuple(sorted(set(vs))) != vs):
                raise ValueError("invalid backdoor")
            seen = set()
            sat = False
            branches = p["branches"]
            if len(branches) != 1 << len(vs):
                raise ValueError("incomplete branch enumeration")
            for b in branches:
                values = tuple(b["values"])
                if (len(values) != len(vs) or any(type(x) is not bool for x in values)
                        or values in seen):
                    raise ValueError("invalid or duplicate branch")
                seen.add(values)
                true_lits = {v if bit else -v for v, bit in zip(vs, values)}
                fixed_vars = set(vs)
                residual = []
                for c in local:
                    budget.tick(1 + len(c))
                    if not true_lits.intersection(c):
                        residual.append(tuple(x for x in c if abs(x) not in fixed_vars))
                verify(nn, residual, b["proof"], budget)
                sat = sat or not b["proof"]["clauses"]
            if type(p["sat"]) is not bool or p["sat"] != sat:
                raise ValueError("component decision mismatch")
            count += len(branches)
            decisions.append(sat)
    if used_clauses != set(range(len(f))):
        raise ValueError("missing normalized clauses")
    decision = "unsat" if False in decisions else ("unknown" if unknown else "sat")
    if (artifact["decision"] != decision or
            type(artifact["complete_strong_backdoor_cover"]) is not bool or
            artifact["complete_strong_backdoor_cover"] != (not unknown) or
            type(artifact["leaf_count"]) is not int or artifact["leaf_count"] != count):
        raise ValueError("global decision or coverage mismatch")
    return True


def isolated_obstruction(n, clauses, budget):
    """Disjoint isolated ternary OR scopes force distinct backdoor hits.

    Each such scope is neither affine nor bijunctive. Without fixing one of
    its variables it remains an unchanged exact-support relation in every
    residual, irrespective of assignments outside that scope.
    """
    nn, f, mapping = normalize(n, clauses)
    occurrences = {}
    for i, c in enumerate(f):
        budget.tick(1 + len(c))
        for x in c:
            occurrences.setdefault(abs(x), set()).add(i)
    indices = [i for i, c in enumerate(f) if len(c) == 3 and
               all(occurrences[abs(x)] == {i} for x in c)]
    cert = {"schema": "mathos-pnp-isolated-or-bound/1", "new_to_old": mapping,
            "clause_indices": indices, "lower_bound": len(indices),
            "scope": "global strong backdoor into v7 direct algebra, not SAT runtime"}
    verify_obstruction(n, clauses, cert, budget)
    return cert


def verify_obstruction(n, clauses, artifact, budget):
    """Independent scan plus explicit majority/XOR nonclosure witnesses."""
    _, f, mapping = normalize(n, clauses)
    ids = artifact["clause_indices"]
    if (artifact["schema"] != "mathos-pnp-isolated-or-bound/1" or
            tuple(artifact["new_to_old"]) != mapping or
            any(type(i) is not int or not 0 <= i < len(f) for i in ids) or
            len(set(ids)) != len(ids) or type(artifact["lower_bound"]) is not int or
            artifact["lower_bound"] != len(ids)):
        raise ValueError("invalid obstruction metadata")
    used = set()
    for i in ids:
        c = f[i]
        variables = {abs(x) for x in c}
        if len(c) != 3 or len(variables) != 3 or used & variables:
            raise ValueError("non-disjoint ternary scope")
        used.update(variables)
        for j, d in enumerate(f):
            budget.tick(1 + len(d))
            if i != j and variables.intersection(abs(x) for x in d):
                raise ValueError("scope is not isolated")
        # Work in literal truth coordinates. Sign flips commute with majority
        # and ternary XOR, so these also witness nonclosure in variable bits.
        allowed = lambda a: any(a)
        for a, b, d, op in (
            ((True,False,False),(False,True,False),(False,False,True),
             lambda x,y,z: sum((x,y,z)) >= 2),
            ((True,False,False),(False,True,False),(True,True,False),
             lambda x,y,z: x ^ y ^ z)):
            if not (allowed(a) and allowed(b) and allowed(d)) or allowed(tuple(op(x,y,z) for x,y,z in zip(a,b,d))):
                raise AssertionError("closure witness invalid")
    return True
