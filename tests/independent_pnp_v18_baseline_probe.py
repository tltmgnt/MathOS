"""Independent semantic probes; does not import or certify MathOS code."""
from itertools import product, permutations
import json


def sat(n, clauses):
    return any(all(any(a[abs(x)-1] == (x > 0) for x in c) for c in clauses)
               for a in product((False, True), repeat=n))


def run():
    clauses = [frozenset(s*i for i, s in enumerate(signs, 1) if s)
               for signs in product((-1, 0, 1), repeat=2)]
    formulas = [tuple(c for i, c in enumerate(clauses) if mask >> i & 1)
                for mask in range(1 << len(clauses))]
    truth = [sat(2, f) for f in formulas]
    injections = [tuple(x*s for x, s in zip(p, signs))
                  for p in permutations((1, 2)) for signs in product((-1, 1), repeat=2)]
    strengthened = exact = 0
    for t, satisfiable in zip(formulas, truth):
        if satisfiable:
            continue
        for e in injections:
            mapped = tuple(frozenset(e[abs(x)-1] * (1 if x > 0 else -1) for x in c) for c in t)
            for f, target_sat in zip(formulas, truth):
                if all(c in f for c in mapped):
                    exact += 1
                    assert not target_sat
                if all(any(q <= c for q in f) for c in mapped):
                    strengthened += 1
                    assert not target_sat
    deletions = 0
    for n in range(1, 11):
        f = [(1,)] + [(-i, i+1) for i in range(1, n)] + [(-n,)]
        assert not sat(n, f)
        for i in range(len(f)):
            assert sat(n, f[:i] + f[i+1:])
            deletions += 1
        assert sat(n, f[:-1] + [(n,)])
    return dict(formulas=len(formulas), unsat_formulas=truth.count(False),
                signed_injections=len(injections), exact_witness_cases=exact,
                strengthening_witness_cases=strengthened, false_positives=0,
                chain_unsat_cases=10, chain_deletion_sat_cases=deletions,
                chain_endpoint_flip_sat_cases=10)


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
