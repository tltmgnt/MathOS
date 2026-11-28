"""A semantic escape route from local CNF preprocessing obstructions.

The recognizer only tries constant assignments or a bounded five-variable
contradictory core. It does not decide general SAT.
"""
from itertools import combinations
from .pnp_structural_kernel import normalize, brute, truth


def propose(n, clauses, budget):
    nn, f, mapping = normalize(n, clauses)
    for value in (True, False):
        assignment = (value,) * nn
        budget.tick(1 + len(f) + sum(map(len, f)))
        if truth(f, assignment):
            return {"kind": "sat_witness", "assignment": assignment,
                    "n": 0, "clauses": ()}
    if nn >= 5:
        core = {tuple(sorted(sign*x for x in q))
                for q in combinations(range(1, 6), 3) for sign in (-1, 1)}
        budget.tick(1 + len(f))
        if core <= set(f):
            return {"kind": "unsat_core", "core": sorted(core),
                    "n": 0, "clauses": ((),)}
    return None


def verify(n, clauses, artifact, budget):
    nn, f, mapping = normalize(n, clauses)
    if artifact["kind"] == "sat_witness":
        a = artifact["assignment"]
        if len(a) != nn or any(type(x) is not bool for x in a):
            raise ValueError("invalid witness")
        budget.tick(1 + len(f) + sum(map(len, f)))
        if not truth(f, a):
            raise ValueError("witness does not satisfy input")
        output = ()
    elif artifact["kind"] == "unsat_core":
        core = tuple(tuple(c) for c in artifact["core"])
        budget.tick(1 + len(f) + len(core))
        if len(core) > 32 or any(len(c) > 5 for c in core):
            raise ValueError("core outside bounded verifier scope")
        if not set(core) <= set(f):
            raise ValueError("core is not a subformula")
        variables = sorted({abs(x) for c in core for x in c})
        if len(variables) > 5:
            raise ValueError("core exceeds five variables")
        index = {v: i+1 for i, v in enumerate(variables)}
        dense = tuple(tuple(index[abs(x)] if x > 0 else -index[abs(x)] for x in c) for c in core)
        if brute(len(variables), dense, budget):
            raise ValueError("core is satisfiable")
        output = ((),)
    else:
        raise ValueError("unknown escape certificate")
    if artifact["n"] != 0 or tuple(tuple(c) for c in artifact["clauses"]) != output:
        raise ValueError("incorrect constant formula")
    return True
