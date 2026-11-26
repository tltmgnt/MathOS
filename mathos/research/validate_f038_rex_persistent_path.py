"""Independent Python reference replay of the REX-010 physical path fixtures."""
from itertools import product
import json
import sys

if __package__:
    from .finite_relational_elimination import Factor, Solver
else:
    from finite_relational_elimination import Factor, Solver


def fixtures():
    for N in (2, 8):
        for i in range(2**N):
            yield format(i, f'0{N}b')
    seed = 0x52455810

    def bit():
        nonlocal seed
        seed = (1664525 * seed + 1013904223) & 0xffffffff
        return seed >> 31

    for i in range(48):
        n = 3 + i % 6
        yield ''.join(str(bit()) for _ in range(2+6*(n-1)))
    for i in range(32):
        n = 3 + i % 6
        a = [bit() for _ in range(n)]
        raw = [str(bit()) for _ in range(2+6*(n-1))]
        raw[a[0]] = '1'
        for j in range(1,n):
            p = 2+6*(j-1)
            raw[p+2*a[j-1]+a[j]] = '1'
            raw[p+4+a[j]] = '1'
        yield ''.join(raw)
    yield '11100011000111'
    yield '11001011'


def audit():
    digest = 2166136261
    cases = sat = stages = candidates = 0
    for raw in fixtures():
        n = 1+(len(raw)-2)//6
        names = tuple(map(str,range(n)))
        fs = [Factor((names[0],),tuple((a,) for a in range(2) if raw[a]=='1'))]
        for i in range(1,n):
            j = 2+6*(i-1)
            fs.extend((Factor(names[i-1:i+1],tuple((a,b) for a,b in product(range(2),repeat=2) if raw[j+2*a+b]=='1')),
                       Factor((names[i],),tuple((a,) for a in range(2) if raw[j+4+a]=='1'))))
        s = Solver({v:(0,1) for v in names},batch_size=2)
        st = s.initial_state(fs)
        # Direct complete-assignment predicate, independent of elimination.
        models = []
        for a in product(range(2),repeat=n):
            if all(tuple(a[int(v)] for v in f.scope) in f.rows for f in fs):
                models.append(a)
        result, traces = s.solve(st,names)
        assert result == bool(models)
        assert tuple(t.candidate_count for t in traces)==(4,)*(n-1)+(2,)
        stages += len(traces)
        candidates += sum(t.candidate_count for t in traces)
        witness = ''.join(map(str,min(models,key=lambda a:a[::-1]))) if models else '-'
        for ch in raw+':'+witness+';':
            digest = ((digest ^ ord(ch))*16777619)&0xffffffff
        cases += 1
        sat += bool(models)
    return dict(cases=cases,sat=sat,unsat=cases-sat,stages=stages,candidates=candidates,digest=digest)


if __name__=='__main__':
    result=audit()
    assert result['digest']==2946600415
    if len(sys.argv)>1:
        with open(sys.argv[1]) as f:
            physical=json.load(f)
        assert physical['digest']==result['digest']
        assert (physical['counts']['valid'],physical['counts']['sat'],physical['counts']['unsat'])==(result['cases'],result['sat'],result['unsat'])
    print('REX_PERSISTENT_PATH_REFERENCE_OK '+json.dumps(result,separators=(',',':')))
