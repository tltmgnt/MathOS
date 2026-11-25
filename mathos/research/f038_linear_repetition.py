"""Shared-prefix path CNF encoding; finite exact regression, not a lower-bound proof."""
from collections import defaultdict
from mathos.research.f038_monotone_choice import sat, restrict


def template(n, trees):
    top = n + 1
    fixed = []
    leaves = defaultdict(list)
    membership = defaultdict(list)

    def gate(a, b, is_or):
        nonlocal top
        top += 1
        c = top
        if is_or:
            fixed.extend(((a, b, -c), (-a, c), (-b, c)))
        else:
            fixed.extend(((-a, -b, c), (a, -c), (b, -c)))
        return c

    for i, (root, edges) in enumerate(trees):
        assert 0 <= root < n
        prefix = {root: root + 2}
        paths = {root: (root,)}
        parents = set()
        for u, v in edges:
            assert u in prefix and v not in prefix and 0 <= v < n
            parents.add(u)
            prefix[v] = gate(prefix[u], v + 2, True)
            paths[v] = paths[u] + (v,)
        for v in prefix:
            is_leaf = v not in parents
            membership[v].append((i, is_leaf))
            if is_leaf:
                leaves[v].append((prefix[v], paths[v], i))
    assert set(membership) == set(range(n))
    assert all(len(v) == 1 and not v[0][1] or
               len(v) == 2 and all(is_leaf for _, is_leaf in v)
               for v in membership.values())
    assert leaves and all(len(v) == 2 for v in leaves.values())
    pairs = set()
    outputs, clauses = [], []
    for ((a, pa, i), (b, pb, j)) in leaves.values():
        pair = tuple(sorted((i, j)))
        assert pair not in pairs and i != j
        pairs.add(pair)
        outputs.append(gate(a, b, True))
        clauses.append(tuple(sorted(set(pa) | set(pb))))
    out = outputs[0]
    for v in outputs[1:]:
        out = gate(out, v, False)
    g = n + 3*len(leaves) - len(trees) - 1
    assert top == n + 1 + g and g <= 4*n
    fixed.extend(((-1, out), (1, -out)))
    assert len(fixed) == 3*g + 2
    slots = tuple(fixed) + tuple(c for v in range(2, n+2) for c in ((v,), (-v,)))
    assert len(set(slots)) == len(slots)
    assert all(1 <= len(c) <= 3 for c in slots)
    return top, tuple(fixed), tuple(clauses), n


def instantiate(t, mask):
    _, fixed, _, n = t
    bits = tuple(bool(mask & (1 << i)) for i in range(n))
    pins = tuple((v if b else -v,) for v, b in enumerate(bits, 2))
    flags = (True,)*len(fixed) + tuple(v for b in bits for v in (b, not b))
    return fixed + pins, flags


def audit():
    families = (
        (3, ((0, ((0, 2),)), (1, ((1, 2),)))),
        (6, ((0, ((0, 3), (0, 4))), (1, ((1, 3), (1, 5))),
             (2, ((2, 4), (2, 5))))),
        (8, ((0, ((0, 6), (6, 3), (6, 4))), (1, ((1, 3), (1, 5))),
             (2, ((2, 7), (7, 4), (7, 5))))),
        (7, ((0, ((0, 5), (5, 3), (0, 6), (6, 4))),
             (1, ((1, 3),)), (2, ((2, 4),)))),
    )
    cases = checks = zero = one = flips = max_v = max_c = 0
    for n, trees in families:
        t = template(n, trees)
        top, fixed, clauses, _ = t
        for mask in range(1 << n):
            f, flags = instantiate(t, mask)
            want = all(any(mask & (1 << i) for i in c) for c in clauses)
            a = sat(restrict(f, {1: False}))
            b = sat(restrict(f, {1: True}))
            assert (a, b) == (not want, want)
            for i in range(n):
                _, other = instantiate(t, mask ^ (1 << i))
                changed = tuple(j for j, (u, v) in enumerate(zip(flags, other))
                                if u != v)
                assert changed == (len(fixed)+2*i, len(fixed)+2*i+1)
                flips += len(changed)
            cases += 1
            checks += 2
            zero += a
            one += b
            max_v = max(max_v, top)
            max_c = max(max_c, len(f))
    assert (cases, checks, zero, one, flips, max_v, max_c) == (
        456, 912, 70, 386, 6704, 22, 49)
    print(f'F038_LINEAR_REPETITION_OK cases={cases} branch_checks={checks} '
          f'zero={zero} one={one} changed_coordinates={flips} '
          f'max_variables={max_v} max_clauses={max_c}')


if __name__ == '__main__':
    audit()
