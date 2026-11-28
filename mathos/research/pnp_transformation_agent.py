"""Restricted constructive transformation with independently replayed unit trace."""
from .pnp_structural_kernel import normalize, Budget


def _simplify(f, assignment, budget):
    out = []
    for c in f:
        budget.tick(1 + len(c))
        if any(assignment.get(abs(x)) == (x > 0) for x in c):
            continue
        out.append(tuple(x for x in c if abs(x) not in assignment))
    return tuple(out)


def unit_transform(n, clauses, budget):
    n, f, mapping = normalize(n, clauses)
    residual, units = f, []
    while () not in residual:
        budget.tick(1 + len(residual))
        unit = next((c[0] for c in residual if len(c) == 1), None)
        if unit is None:
            break
        units.append(unit)
        # Incremental substitution, unlike the independent verifier.
        updated = []
        for c in residual:
            budget.tick(1 + len(c))
            if unit not in c:
                updated.append(tuple(x for x in c if x != -unit))
        residual = tuple(updated)
    nn, reduced, active = normalize(n, residual)
    return {"units": units, "n": nn, "clauses": reduced,
            "new_to_old": tuple(mapping[i-1] for i in active),
            "forced_original_literals": tuple(
                mapping[abs(x)-1] if x > 0 else -mapping[abs(x)-1] for x in units)}


def verify_transform(n, clauses, artifact, budget):
    nn, f, mapping = normalize(n, clauses)
    assigned = {}
    for x in artifact["units"]:
        if type(x) is not int or not 0 < abs(x) <= nn or abs(x) in assigned:
            raise ValueError("invalid forced literal")
        residual = _simplify(f, assigned, budget)
        if () in residual or (x,) not in residual:
            raise ValueError("forced literal is not a valid unit")
        assigned[abs(x)] = x > 0
    residual = _simplify(f, assigned, budget)
    if () not in residual and any(len(c) == 1 for c in residual):
        raise ValueError("unfinished unit propagation")
    count, reduced, active = normalize(nn, residual)
    forced = tuple(mapping[abs(x)-1] if x > 0 else -mapping[abs(x)-1]
                   for x in artifact["units"])
    if (count != artifact["n"] or reduced != tuple(tuple(c) for c in artifact["clauses"])
            or tuple(mapping[i-1] for i in active) != tuple(artifact["new_to_old"])
            or forced != tuple(artifact["forced_original_literals"])):
        raise ValueError("residual or reconstruction map mismatch")
    return True
