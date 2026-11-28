"""Adaptive bounded separator selection; decisions use the v5 certificate verifier."""
import argparse
import json
from itertools import combinations

from .pnp_generalized_escape import (
    LEAF_CAP, _components, _condition, _vars, propose, verify,
)
from .pnp_structural_kernel import Budget, Exhausted


def _residual_profile(f, budget):
    budget.tick(1 + len(f) + sum(map(len, f)))
    if () in f:
        return 0, 0, 0
    widths = []
    for indices in _components(f, budget):
        widths.append(len(_vars(tuple(f[i] for i in indices))))
    return (max(widths, default=0),
            sum(w for w in widths if w > LEAF_CAP), sum(widths))


def rank(f, budget):
    """Score both polarities of every active variable, deterministically.

    Minimize worst largest residual component, unresolved variable mass,
    then aggregate residual mass. Scores are heuristics, not SAT certificates.
    """
    budget.tick(1 + len(f) + sum(map(len, f)))
    rows = []
    for v in _vars(f):
        neg = _residual_profile(_condition(f, -v, budget), budget)
        pos = _residual_profile(_condition(f, v, budget), budget)
        score = (max(neg[0], pos[0]), neg[1] + pos[1], neg[2] + pos[2], v)
        rows.append({"variable": v, "negative": neg, "positive": pos, "score": score})
    return sorted(rows, key=lambda row: row["score"])


def adaptive(n, clauses, budget, *, depth=2):
    choices = []

    def select(f, b):
        rows = rank(f, b)
        best = rows[0]
        b.cells(len(choices) + 1)
        choices.append({"candidates": len(rows), **best})
        return best["variable"]

    cert = propose(n, clauses, budget, depth=depth, choose=select)
    if cert is not None:
        verify(n, clauses, cert, budget)
    return {"certificate": cert, "certificate_replayed": cert is not None,
            "choices": choices, "work_steps": budget.steps}


def _block(vs, contradictory=False):
    for q in combinations(vs, 3):
        patterns = [(1,1,1), (-1,-1,-1)] if contradictory else [
            tuple(-1 if i == j else 1 for i in range(3)) for j in range(3)] + [
            tuple(1 if i == j else -1 for i in range(3)) for j in range(3)]
        for signs in patterns:
            yield [v*s*(-1 if v%2 else 1) for v,s in zip(q,signs)]


def separator_family(blocks=3, contradictory=False):
    """Low-occurrence separator with high-occurrence internal distractors."""
    if type(blocks) is not int or not 3 <= blocks <= 12:
        raise ValueError("blocks must be 3..12")
    f = []
    for j in range(blocks):
        vs = list(range(2+6*j, 8+6*j))
        f.extend(_block(vs, contradictory and j == blocks-1))
        a,b = vs[:2]
        f.extend([[1,a,b], [-1,-a,-b]])
    return 1+6*blocks, f


def dense_control():
    """No small components after one conditioning step; not a SAT-hardness claim."""
    return 10, list(_block(range(1,11)))


def experiment():
    rows = []
    for name, (n,f) in [
        ("separator_sat", separator_family()),
        ("separator_unsat", separator_family(contradictory=True)),
        ("dense_control", dense_control()),
    ]:
        row = {"name": name, "n": n, "clauses": len(f)}
        for method in ("frequency", "adaptive"):
            budget = Budget(seconds=30, max_steps=20_000_000)
            try:
                if method == "adaptive":
                    data = adaptive(n,f,budget,depth=1)
                else:
                    cert = propose(n,f,budget,depth=1)
                    if cert is not None:
                        verify(n,f,cert,budget)
                    data = {"certificate": cert, "certificate_replayed": cert is not None,
                            "work_steps": budget.steps}
                cert = data["certificate"]
                row[method] = {**data, "status": cert["kind"] if cert else "unknown"}
            except Exhausted as exc:
                row[method] = {"status": "resource_exhausted", "reason": str(exc),
                               "work_steps": budget.steps}
        rows.append(row)
    return {"schema":"mathos-pnp-adaptive-separators/1", "depth":1,
            "leaf_cap": LEAF_CAP, "universal_obligation":"unresolved",
            "p_equals_np_established":False, "p_not_equals_np_established":False,
            "controls":rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(experiment(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
