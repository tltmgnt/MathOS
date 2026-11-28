"""Bounded semantic escape via component decomposition and Boolean conditioning.

SAT outputs carry a full signed witness; UNSAT outputs carry a replayable
tree of subformula, split, and bounded exhaustive refutations.
Neither unrecognized inputs nor resource exhaustion imply UNSAT.
"""
from collections import Counter
from itertools import product

from .pnp_structural_kernel import normalize

LEAF_CAP = 8
DEPTH_CAP = 4


def _options(depth):
    if type(depth) is not int or not 0 <= depth <= DEPTH_CAP:
        raise ValueError("split depth must be 0..4")


def _vars(f):
    return sorted({abs(x) for c in f for x in c})


def _satisfies(f, signed, budget):
    budget.tick(1 + len(f) + sum(map(len, f)))
    return all(any(x in signed for x in c) for c in f)


def _components(f, budget):
    """Partition clause indices by shared variables without quadratic edges."""
    occurrences = {}
    for i, c in enumerate(f):
        budget.tick(1 + len(c))
        for x in c:
            occurrences.setdefault(abs(x), []).append(i)
    unseen = set(range(len(f)))
    groups, expanded = [], set()
    for i in range(len(f)):
        if i not in unseen:
            continue
        unseen.remove(i)
        group, stack = [], [i]
        while stack:
            j = stack.pop()
            group.append(j)
            budget.tick(1 + len(f[j]))
            for x in f[j]:
                v = abs(x)
                if v in expanded:
                    continue
                expanded.add(v)
                for k in occurrences[v]:
                    budget.tick()
                    if k in unseen:
                        unseen.remove(k)
                        stack.append(k)
        groups.append(sorted(group))
    return groups


def _condition(f, literal, budget):
    out = []
    for c in f:
        budget.tick(1 + len(c))
        if literal not in c:
            out.append(tuple(x for x in c if x != -literal))
    return tuple(out)


def _complete(vs, signed):
    present = {abs(x) for x in signed}
    return signed | {-v for v in vs if v not in present}


def _solve(f, depth, budget, choose=None):
    budget.tick(1 + len(f) + sum(map(len, f)))
    vs = _vars(f)
    if () in f:
        return False, {"rule": "subset", "indices": [f.index(())],
                       "child": {"rule": "enumerate"}} if len(f) > 1 else {"rule": "enumerate"}
    for sign in (1, -1):
        a = {sign*v for v in vs}
        if _satisfies(f, a, budget):
            return True, a
    if len(vs) <= LEAF_CAP:
        for bits in product((-1, 1), repeat=len(vs)):
            a = {s*v for s, v in zip(bits, vs)}
            if _satisfies(f, a, budget):
                return True, a
        return False, {"rule": "enumerate"}
    groups = _components(f, budget)
    if len(groups) > 1:
        witness, unknown = set(), False
        for indices in groups:
            status, proof = _solve(tuple(f[i] for i in indices), depth, budget, choose)
            if status is False:
                # An empty-clause subset cannot arise here: handled above.
                return False, {"rule": "subset", "indices": indices, "child": proof}
            if status is None:
                unknown = True
            else:
                witness.update(proof)
        return (None, None) if unknown else (True, witness)
    if depth == 0:
        return None, None
    if choose is None:
        counts = Counter(abs(x) for c in f for x in c)
        v = min(vs, key=lambda x: (-counts[x], x))
    else:
        v = choose(f, budget)
        if type(v) is not int or v not in vs:
            raise ValueError("selector must choose an active variable")
    children = []
    for literal in (-v, v):
        status, proof = _solve(_condition(f, literal, budget), depth-1, budget, choose)
        if status is True:
            return True, _complete(vs, proof | {literal})
        children.append((status, proof))
    if all(status is False for status, _ in children):
        return False, {"rule": "split", "variable": v,
                       "negative": children[0][1], "positive": children[1][1]}
    return None, None


def propose(n, clauses, budget, *, depth=2, choose=None):
    """Return a certificate for a constant formula, or None if unrecognized."""
    _options(depth)
    nn, f, _ = normalize(n, clauses)
    status, proof = _solve(f, depth, budget, choose)
    if status is None:
        return None
    return {"schema": "mathos-generalized-escape/1", "depth": depth,
            "kind": "sat_witness" if status else "unsat_tree",
            "proof": sorted(proof, key=abs) if status else proof,
            "n": 0, "clauses": [] if status else [[]]}


def _replay_unsat(f, proof, depth, allow_subset, budget):
    budget.tick(1 + len(f) + sum(map(len, f)))
    if not isinstance(proof, dict):
        raise ValueError("invalid proof node")
    rule = proof.get("rule")
    vs = sorted({abs(x) for c in f for x in c})
    if rule == "enumerate":
        if set(proof) != {"rule"} or len(vs) > LEAF_CAP:
            raise ValueError("invalid bounded leaf")
        for bits in product((False, True), repeat=len(vs)):
            values = dict(zip(vs, bits))
            budget.tick(1 + len(f) + sum(map(len, f)))
            if all(any(values[abs(x)] == (x > 0) for x in c) for c in f):
                raise ValueError("purported UNSAT leaf has a model")
    elif rule == "subset":
        ix = proof.get("indices")
        if (set(proof) != {"rule", "indices", "child"} or not allow_subset
                or not isinstance(ix, list) or not 0 < len(ix) < len(f)
                or any(type(i) is not int or not 0 <= i < len(f) for i in ix)
                or ix != sorted(set(ix))):
            raise ValueError("invalid strict subformula")
        _replay_unsat(tuple(f[i] for i in ix), proof["child"], depth, False, budget)
    elif rule == "split":
        v = proof.get("variable")
        if (set(proof) != {"rule", "variable", "negative", "positive"}
                or depth <= 0 or type(v) is not int or v not in vs):
            raise ValueError("invalid split")
        # Replay conditioning separately from the search implementation.
        for value, child in ((False, "negative"), (True, "positive")):
            residual = []
            for c in f:
                budget.tick(1 + len(c))
                if not any(abs(x) == v and (x > 0) == value for x in c):
                    residual.append(tuple(x for x in c if abs(x) != v))
            _replay_unsat(tuple(residual), proof[child], depth-1, True, budget)
    else:
        raise ValueError("unknown refutation rule")


def verify(n, clauses, artifact, budget):
    """Check the witness/refutation against the normalized signed input."""
    if (not isinstance(artifact, dict) or
            set(artifact) != {"schema", "depth", "kind", "proof", "n", "clauses"}
            or artifact["schema"] != "mathos-generalized-escape/1"
            or type(artifact["n"]) is not int or artifact["n"] != 0):
        raise ValueError("invalid certificate envelope")
    depth = artifact["depth"]
    _options(depth)
    nn, f, _ = normalize(n, clauses)
    proof = artifact["proof"]
    if artifact["kind"] == "sat_witness":
        if (not isinstance(proof, list) or len(proof) != nn
                or any(type(x) is not int or abs(x) != i
                       for i, x in enumerate(proof, 1))
                or artifact["clauses"] != []):
            raise ValueError("invalid total witness")
        signs = set(proof)
        budget.tick(1 + len(f) + sum(map(len, f)))
        if any(all(x not in signs for x in c) for c in f):
            raise ValueError("witness fails input")
    elif artifact["kind"] == "unsat_tree":
        if artifact["clauses"] != [[]] or not isinstance(artifact["clauses"][0], list):
            raise ValueError("invalid contradiction output")
        _replay_unsat(f, proof, depth, True, budget)
    else:
        raise ValueError("unknown certificate kind")
    return True
