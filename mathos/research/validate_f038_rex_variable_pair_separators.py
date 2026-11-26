"""REX-015 independent relational reference and predicate enumeration."""
import json
import sys
from itertools import product
if __package__:
    from .finite_relational_elimination import Factor, Solver
else:
    from finite_relational_elimination import Factor, Solver


def fixtures():
    def bits(x,n): return [(x>>j)&1 for j in range(n)]
    def tensor(a,b,c,x,y):
        return [[[[ (x>>(i+a*(j+b*k)))&1,(y>>(i+a*(j+b*k)))&1] for i in range(a)] for j in range(b)] for k in range(c)]
    for a,b in product(range(1,4),repeat=2):
        for x in range(min(2**(a*b),16)):
            yield [bits(x>>(j*a),a) for j in range(b)],[],x<3
    full=[[1,1],[1,1]]
    for x in range(256):
        yield full,[tensor(2,2,2,x,255)],x%32==0
    for x,y in product(range(16),repeat=2):
        yield full,[[g+g for g in tensor(2,1,2,x,y)]],False
    yield full,[tensor(2,2,2,85,170)],True
    yield full,[tensor(2,2,2,195,255),tensor(2,2,2,102,255)],True
    seed=0x52455815
    def rand():
        nonlocal seed
        seed=(1664525*seed+1013904223)&0xffffffff
        return seed
    for i in range(32):
        g=1+i%3; d=[1+(rand()>>28)%3 for _ in range(g+2)]
        initial=[[rand()>>31 for _ in range(d[0])] for _ in range(d[1])]
        stages=[[[[ [rand()>>31,rand()>>31] for _ in range(d[j])] for _ in range(d[j+1])] for _ in range(d[j+2])] for j in range(g)]
        if i%2:
            a=[(rand()>>16)%m for m in d]
            initial[a[1]][a[0]]=1
            for j in range(g): stages[j][a[j+2]][a[j+1]][a[j]]=[1,1]
        yield initial,stages,i<12
    d=[2,3,1,4,2]; w=[1,2,0,3,1]
    yield [[int(a==w[0] and b==w[1]) for a in range(d[0])] for b in range(d[1])],[[[[[int(a==w[j] and b==w[j+1] and c==w[j+2])]*2 for a in range(d[j])] for b in range(d[j+1])] for c in range(d[j+2])] for j in range(3)],True


def encode(initial,stages):
    def bit(x): return '001' if x else '000'
    return ''.join('010'+''.join(map(bit,col))+'101' for col in initial)+'110'+''.join(''.join('010'+''.join('011'+''.join(bit(b) for pair in col for b in pair)+'100' for col in g)+'101' for g in s)+'110' for s in stages)


def audit():
    cases=sat=physical_cases=physical_sat=steps=candidates=projected=0
    digest=physical_digest=2166136261
    for initial,stages,physical in fixtures():
        d=[len(initial[0]),len(initial),*(len(s) for s in stages)]
        names=tuple(map(str,range(len(d))))
        domains={v:tuple(range(m)) for v,m in zip(names,d)}
        fs=[Factor(names[:2],tuple((a,b) for a,b in product(range(d[0]),range(d[1])) if initial[b][a]))]
        for j,s in enumerate(stages):
            for f in range(2):
                fs.append(Factor(names[j:j+3],tuple((a,b,c) for a,b,c in product(*(range(m) for m in d[j:j+3])) if s[c][b][a][f])))
        models=[a for a in product(*domains.values()) if initial[a[1]][a[0]] and all(all(s[a[j+2]][a[j+1]][a[j]]) for j,s in enumerate(stages))]
        solver=Solver(domains,batch_size=2); state=solver.initial_state(fs)
        for j,v in enumerate(names):
            state,trace=solver.stage(state,v)
            expected=tuple(sorted({a[j+1:] for a in models}))
            assert solver.relation(state).rows==expected
            from math import prod
            assert trace.candidate_count==prod(d[j:j+3])
            steps+=1; candidates+=trace.candidate_count; projected+=len(expected)
        assert bool(solver.relation(state).rows)==bool(models)
        a=min(models,key=lambda a:a[::-1]) if models else None
        out='-' if a is None else ''.join(str(int(b==a[1] and i==a[0])) for b in range(d[1]) for i in range(d[0]))+''.join(str(int(i==a[j])) for j in range(2,len(d)) for i in range(d[j]))
        for ch in encode(initial,stages)+':'+out+';':
            digest=((digest^ord(ch))*16777619)&0xffffffff
            if physical: physical_digest=((physical_digest^ord(ch))*16777619)&0xffffffff
        cases+=1; sat+=bool(models); physical_cases+=physical; physical_sat+=physical and bool(models)
    return dict(cases=cases,sat=sat,unsat=cases-sat,physical_cases=physical_cases,physical_sat=physical_sat,stages=steps,candidates=candidates,projected=projected,digest=digest,physicalDigest=physical_digest)


if __name__=='__main__':
    r=audit()
    assert (r['digest'],r['physicalDigest'])==(2820171537,268898126)
    if len(sys.argv)>1:
        with open(sys.argv[1]) as f: p=json.load(f)
        assert (p['digest'],p['physicalDigest'])==(r['digest'],r['physicalDigest'])
        assert (p['counts']['logicalCases'],p['counts']['physicalCases'],p['counts']['sat'],p['counts']['physicalSat'])==(r['cases'],r['physical_cases'],r['sat'],r['physical_sat'])
    print('REX_VARIABLE_PAIR_REFERENCE_OK '+json.dumps(r,separators=(',',':')))
