"""REX-011 independent finite relational and direct predicate replay."""
from itertools import product
import json
import sys

if __package__:
    from .finite_relational_elimination import Factor, Solver
else:
    from finite_relational_elimination import Factor, Solver


def encode(u, e):
    def bit(x):
        return '0' + str(x)
    return ''.join(map(bit, u[0])) + '11' + ''.join(
        ''.join(bit(b) + ''.join(bit(row[j]) for row in matrix) + '10'
                for j, b in enumerate(u[i+1])) + '11'
        for i, matrix in enumerate(e))


def fixtures():
    def bits(x, n):
        return [(x >> i) & 1 for i in range(n)]
    for m in range(1, 6):
        for x in range(2**m):
            yield [bits(x, m)], []
    for m, n in ((1, 1), (1, 2), (2, 1), (2, 2), (1, 3), (3, 1)):
        for x in range(2**(m+n+m*n)):
            b = bits(x, m+n+m*n)
            yield [b[:m], b[m:m+n]], [
                [b[m+n+i*n:m+n+(i+1)*n] for i in range(m)]]
    seed = 0x52455811

    def rand():
        nonlocal seed
        seed = (1664525*seed + 1013904223) & 0xffffffff
        return seed

    for i in range(40):
        n = 3+i%3
        sizes = [1+(rand() >> 28)%4 for _ in range(n)]
        u = [[rand() >> 31 for _ in range(m)] for m in sizes]
        e = [[[rand() >> 31 for _ in range(m)] for _ in range(sizes[j])]
             for j, m in enumerate(sizes[1:])]
        if i%2:
            a = [(rand() >> 16)%m for m in sizes]
            for j in range(n):
                u[j][a[j]] = 1
            for j in range(n-1):
                e[j][a[j]][a[j+1]] = 1
        yield u, e
    yield [[1,1],[1,1],[1,1]], [[[1,0],[0,0]],[[0,0],[0,1]]]
    yield [[0,1,0],[1,1,1,1],[1,1]], [
        [[0,0,0,0],[0,0,0,1],[0,0,0,0]], [[0,0],[0,0],[0,0],[0,1]]]


def audit():
    digest = 2166136261
    cases = sat = stages = candidates = projected = 0
    for u, e in fixtures():
        names = tuple(map(str, range(len(u))))
        domains = {v: tuple(range(len(u[i]))) for i, v in enumerate(names)}
        fs = [Factor((v,), tuple((b,) for b in domains[v] if u[i][b]))
              for i, v in enumerate(names)]
        fs += [Factor(names[i:i+2], tuple((a,b) for a,b in product(
            domains[names[i]], domains[names[i+1]]) if matrix[a][b]))
               for i, matrix in enumerate(e)]
        models = [a for a in product(*domains.values())
                  if all(u[i][b] for i,b in enumerate(a))
                  and all(matrix[a[i]][a[i+1]] for i,matrix in enumerate(e))]
        s = Solver(domains, batch_size=2)
        state = s.initial_state(fs)
        for i,v in enumerate(names):
            state, trace = s.stage(state, v)
            expected = tuple(sorted({a[i+1:] for a in models}))
            assert s.relation(state).rows == expected
            assert trace.candidate_count == (len(u[i])*len(u[i+1]) if i+1<len(u) else len(u[i]))
            stages += 1
            candidates += trace.candidate_count
            projected += len(expected)
        assert bool(s.relation(state).rows) == bool(models)
        a = min(models, key=lambda a:a[::-1]) if models else None
        witness = '-' if a is None else ''.join(str(int(b==a[i])) for i,d in enumerate(u) for b in range(len(d)))
        for ch in encode(u,e)+':'+witness+';':
            digest = ((digest ^ ord(ch))*16777619)&0xffffffff
        cases += 1
        sat += bool(models)
    return dict(cases=cases,sat=sat,unsat=cases-sat,stages=stages,candidates=candidates,projected=projected,digest=digest)


if __name__ == '__main__':
    result = audit()
    assert result['digest'] == 1242392580
    if len(sys.argv)>1:
        with open(sys.argv[1]) as f:
            physical = json.load(f)
        assert physical['digest'] == result['digest']
        assert (physical['counts']['valid'],physical['counts']['sat'],physical['counts']['unsat']) == (result['cases'],result['sat'],result['unsat'])
    print('REX_VARIABLE_DOMAIN_REFERENCE_OK '+json.dumps(result,separators=(',',':')))
