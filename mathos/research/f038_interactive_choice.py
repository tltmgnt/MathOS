"""Direct disjointness transfer to interactive branch selection; finite audit."""
from itertools import combinations
from mathos.research.f038_monotone_choice import sat, restrict


def template(m):
    assert m >= 1
    t = tuple(range(2, m + 2))
    w = tuple(range(m + 2, 2 * m + 2))
    top = 1 + 2 * m
    fixed = [(-1, -v, u) for u, v in zip(t, w)]
    row = (-1, *w)
    while len(row) > 3:
        top += 1
        fixed.append((row[0], row[1], top))
        row = (-top, *row[2:])
    fixed.append(row)
    alice = tuple(((-1, -v), (1, -u)) for u, v in zip(t, w))
    bob = tuple(((-1, -u), (1, u)) for u in t)
    slots = tuple(fixed) + tuple(c for block in (alice, bob)
                                 for pair in block for c in pair)
    assert len(set(slots)) == len(slots)
    assert all(1 <= len(c) <= 3 for c in slots)
    assert top == 1 + 2 * m + max(0, m - 2)
    return top, tuple(fixed), alice, bob


def local(block, mask):
    return tuple(pair[(mask >> i) & 1] for i, pair in enumerate(block))


def audit():
    cases = checks = zero = one = fooling = max_vars = max_clauses = 0
    for m in range(1, 7):
        top, fixed, a, b = template(m)
        n = 1 << m
        left = [local(a, x) for x in range(n)]
        right = [local(b, y) for y in range(n)]
        assert len(set(left)) == len(set(right)) == n
        assert not ({c for pair in a for c in pair} &
                    {c for pair in b for c in pair})
        outcomes = {}
        for x in range(n):
            for y in range(n):
                f = fixed + left[x] + right[y]
                assert len(f) == len(set(f)) == 3*m + max(1, m-1)
                z0 = sat(restrict(f, {1: False}))
                z1 = sat(restrict(f, {1: True}))
                assert (z0, z1) == (not bool(x & y), bool(x & y))
                outcomes[x, y] = z1
                cases += 1
                checks += 2
                zero += z0
                one += z1
                max_vars = max(max_vars, top)
                max_clauses = max(max_clauses, len(f))
        mask = n - 1
        for x in range(n):
            assert not outcomes[x, mask ^ x]
        for x, y in combinations(range(n), 2):
            assert outcomes[x, mask ^ y] or outcomes[y, mask ^ x]
            fooling += 1
    assert (cases, checks, zero, one, fooling, max_vars, max_clauses) == (
        5460, 10920, 1092, 4368, 2667, 17, 23)
    print(f'F038_INTERACTIVE_CHOICE_OK cases={cases} branch_checks={checks} '
          f'zero={zero} one={one} fooling_pairs={fooling} '
          f'max_variables={max_vars} max_clauses={max_clauses}')


if __name__ == '__main__':
    audit()
