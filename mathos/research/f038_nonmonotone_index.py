"""F038 nonmonotone one-way index barrier. Exact finite audit only."""
from itertools import combinations
from mathos.research.f038_monotone_choice import (
    template, instantiate, graph_properties, sat, restrict,
)


def graph(a, b, k, data, query):
    assert a >= 1 and b >= 1 and k >= 4
    assert 0 <= data < 1 << (a * b)
    assert 0 <= query < a * b
    n = a + b + k - 2
    core = range(a + b, n)
    u, v = query // b, a + query % b
    edges = {(i, a + j) for i in range(a) for j in range(b)
             if data & (1 << (i * b + j))}
    edges.update(combinations(core, 2))
    edges.update((w, c) for w in (u, v) for c in core)
    return n, edges


def audit():
    cases = zero = one = distinct = branch_checks = 0
    for a, b, k in ((1, 1, 4), (2, 2, 4), (2, 3, 4), (2, 2, 5)):
        m = a * b
        n = a + b + k - 2
        t = template(n, k)
        _, _, pairs, edge_rows, nonedge_rows = t
        split = []
        for u, v in pairs:
            split.extend([u < a <= v < a + b] *
                         (len(edge_rows[u, v]) + len(nonedge_rows[u, v])))
        data_flags, query_flags, signatures = {}, {}, set()
        for x in range(1 << m):
            answers = []
            for q in range(m):
                _, edges = graph(a, b, k, x, q)
                mask = sum(1 << i for i, e in enumerate(pairs) if e in edges)
                f, flags = instantiate(t, mask)
                want = bool(x & (1 << q))
                c, d = graph_properties(n, k, pairs, mask)
                assert (c, d) == (not want, want)
                assert sat(restrict(f, {1: False})) == c
                assert sat(restrict(f, {1: True})) == d
                branch_checks += 2
                assert len(flags) == len(split)
                df = tuple(v for v, part in zip(flags, split) if part)
                qf = tuple(v for v, part in zip(flags, split) if not part)
                assert data_flags.setdefault(x, df) == df
                assert query_flags.setdefault(q, qf) == qf
                answers.append(d)
                cases += 1
                zero += c
                one += d
            signature = tuple(answers)
            assert signature not in signatures
            signatures.add(signature)
        assert len(set(data_flags.values())) == len(signatures) == 1 << m
        distinct += len(signatures)
    assert (cases, branch_checks, zero, one, distinct) == (514, 1028, 257, 257, 98)
    print(f'F038_NONMONOTONE_INDEX_OK graphs={cases} branch_checks={branch_checks} zero={zero} one={one} distinct={distinct}')


if __name__ == '__main__':
    audit()
