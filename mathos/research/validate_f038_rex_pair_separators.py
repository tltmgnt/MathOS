"""REX-014 independent finite relational and full-predicate replay."""
import json
import sys
from itertools import product

if __package__:
    from .finite_relational_elimination import Factor, Solver
else:
    from finite_relational_elimination import Factor, Solver


def bits(x, n):
    return [(x >> i) & 1 for i in range(n)]


def stage(x, y):
    return [[[(x >> (2*j+a)) & 1, (y >> (2*j+a)) & 1]
             for a in range(2)] for j in range(4)]


def fixtures():
    all_true = [1]*4
    for x in range(16):
        yield bits(x, 4), []
    for x in range(256):
        yield all_true, [stage(x, 255)]
    for x, y in product(range(16), repeat=2):
        yield all_true, [stage(17*x, 17*y)]
    yield all_true, [stage(85, 170)]
    yield all_true, [stage(195, 255), stage(90, 255)]
    seed = 0x52455814

    def rand():
        nonlocal seed
        seed = (1664525*seed+1013904223)&0xffffffff
        return seed

    for i in range(64):
        g = 1+i%6
        initial = bits(rand() >> 16, 4)
        stages = [stage(rand() >> 16, rand() >> 16) for _ in range(g)]
        if i%2:
            a = [rand() >> 31 for _ in range(g+2)]
            initial[2*a[0]+a[1]] = 1
            for j in range(g):
                stages[j][2*a[j+1]+a[j+2]][a[j]] = [1,1]
        yield initial, stages


def audit():
    cases = sat = stages_checked = candidates = projected = 0
    digest = 2166136261
    for initial, stages in fixtures():
        n = len(stages)+2
        names = tuple(map(str, range(n)))
        domains = {v: (0,1) for v in names}
        fs = [Factor(names[:2], tuple((a,b) for a,b in product(range(2),repeat=2)
                                     if initial[2*a+b]))]
        for j,s in enumerate(stages):
            for f in range(2):
                fs.append(Factor(names[j:j+3], tuple((a,b,c) for a,b,c in product(range(2),repeat=3)
                                                      if s[2*b+c][a][f])))
        models = [a for a in product(range(2), repeat=n)
                  if initial[2*a[0]+a[1]] and all(all(s[2*a[j+1]+a[j+2]][a[j]]) for j,s in enumerate(stages))]
        solver = Solver(domains,batch_size=2)
        state = solver.initial_state(fs)
        for j,v in enumerate(names):
            state,trace = solver.stage(state,v)
            expected = tuple(sorted({a[j+1:] for a in models}))
            assert solver.relation(state).rows == expected
            assert trace.candidate_count == (8 if j<n-2 else 4 if j==n-2 else 2)
            stages_checked += 1
            candidates += trace.candidate_count
            projected += len(expected)
        assert bool(solver.relation(state).rows) == bool(models)
        witness = ''.join(map(str,min(models,key=lambda a:a[::-1]))) if models else '-'
        raw = ''.join(map(str,initial))+''.join(str(b) for s in stages for col in s for pair in col for b in pair)
        for ch in raw+':'+witness+';':
            digest = ((digest^ord(ch))*16777619)&0xffffffff
        cases += 1
        sat += bool(models)
    return dict(cases=cases,sat=sat,unsat=cases-sat,stages=stages_checked,candidates=candidates,projected=projected,digest=digest)


if __name__ == '__main__':
    result = audit()
    assert result['digest'] == 2653112972
    if len(sys.argv)>1:
        with open(sys.argv[1]) as f:
            physical = json.load(f)
        assert physical['digest']==result['digest']
        assert (physical['counts']['valid'],physical['counts']['sat'],physical['counts']['unsat'])==(result['cases'],result['sat'],result['unsat'])
    print('REX_PAIR_SEPARATOR_REFERENCE_OK '+json.dumps(result,separators=(',',':')))
