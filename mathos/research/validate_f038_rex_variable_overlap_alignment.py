"""Independent relational replay of the REX-018 explicit-row edge kernel."""
import json
import sys
from itertools import product
if __package__:
    from .finite_relational_elimination import Factor, Solver
else:
    from finite_relational_elimination import Factor, Solver

PAIRS = ((0, 1), (0, 2), (1, 2))


def fixtures():
    for k, (x, y) in enumerate(PAIRS):
        yield k, [], [], True
        yield k, [('0','1','10',1)], [], True
        yield k, [], [('0','1','10',1)], True
        for p, c, m in product(range(8), range(8), range(4)):
            yield k, [(*format(p,'03b'),m&1)], [(*format(c,'03b'),m>>1)], (p==5 and c%3==0 and m==3) or (p==0 and c==0 and m!=3)
        P = [('0','10','101',1),('1','10','101',1),('0','10','101',0),('101','1','0',1)]
        C = [(P[0][x]+'1',P[0][y],'0',1),(P[0][x],P[0][y],'111',0),(P[1][x],P[1][y],'10',1),(P[0][x],P[0][y],'1',1),(P[0][x],P[0][y],'0',1)]
        yield k, P, C, True
        yield k, [('0','0','0',1)], [('00','0','0',1),('0','00','0',1)], True
    for k,(x,y) in enumerate(PAIRS):
        def p(a,b,v):
            row=['101','101','101',v]; row[x]=a; row[y]=b
            return tuple(row)
        yield k, [p('0','0',1),p('1','1',1)], [('0','1','11',1),('1','0','10',1)], True
        yield k, [p('10','101',0),p('10','101',1),p('10','101',1)], [('10','101','1',0),('10','101','11',1),('10','101','0',1)], True
    seed=0x52455818
    labels=['0','1','10','101']
    def rand():
        nonlocal seed
        seed=(1664525*seed+1013904223)&0xffffffff
        return seed
    def rows(n):
        return [(*[labels[(rand()>>16)%4] for _ in range(3)],rand()>>31) for _ in range(n)]
    for i in range(36):
        k=i%3; P=rows(1+i%3); C=rows(1+(i>>2)%3)
        if i%2:
            x,y=PAIRS[k]; P[0]=(*P[0][:3],1); C[0]=(P[0][x],P[0][y],C[0][2],1)
        yield k,P,C,i<6


def encode(k,P,C):
    def row(r):
        return '011'+''.join(''.join('00'+b for b in s)+'010' for s in r[:3])+('101' if r[3] else '100')
    return format(k,'02b')+''.join(map(row,P))+'110'+''.join(map(row,C))


def audit():
    cases=positive=physical_cases=physical_positive=flags_checked=0
    digest=physical_digest=2166136261
    for k,P,C,physical in fixtures():
        x,y=PAIRS[k]
        # Map opaque labels injectively to integers for the relational reference.
        labels=sorted({s for r in P+C for s in r[:3]})
        ids={s:i for i,s in enumerate(labels)}
        names=('a','b','c')
        domains={v:range(len(labels)) for v in (*names,'fresh')}
        domains['row_id']=range(len(P))
        fs=[Factor(('row_id',*names),tuple((i,*(ids[s] for s in r[:3])) for i,r in enumerate(P) if r[3])),Factor((names[x],names[y],'fresh'),tuple(tuple(ids[s] for s in r[:3]) for r in C if r[3]))]
        solver=Solver(domains,batch_size=2)
        st=solver.initial_state(fs)
        st,_=solver.stage(st,'fresh')
        rel=solver.relation(st)
        live={row[rel.scope.index('row_id')] for row in rel.rows}
        supports=[[j for j,c in enumerate(C) if p[3] and c[3] and (p[x],p[y])==c[:2]] for p in P]
        expected={i for i,s in enumerate(supports) if s}
        assert live==expected
        first=min(expected) if expected else None
        chosen=supports[first][0] if first is not None else -1
        out=''.join(str(int(i in live)) for i in range(len(P)))+''.join(str(int(j==chosen)) for j in range(len(C)))
        for ch in encode(k,P,C)+':'+out+';':
            digest=((digest^ord(ch))*16777619)&0xffffffff
            if physical: physical_digest=((physical_digest^ord(ch))*16777619)&0xffffffff
        cases+=1; positive+=bool(expected); physical_cases+=physical; physical_positive+=physical and bool(expected); flags_checked+=len(P)
    return dict(cases=cases,positive=positive,negative=cases-positive,physical_cases=physical_cases,physical_positive=physical_positive,flags_checked=flags_checked,digest=digest,physicalDigest=physical_digest)


if __name__=='__main__':
    r=audit()
    assert (r['digest'],r['physicalDigest'])==(3392018395,1193114046)
    if len(sys.argv)>1:
        with open(sys.argv[1]) as f: p=json.load(f)
        assert (p['digest'],p['physicalDigest'])==(r['digest'],r['physicalDigest'])
        assert (p['counts']['logicalCases'],p['counts']['physicalCases'],p['counts']['positiveCases'],p['counts']['physicalPositive'])==(r['cases'],r['physical_cases'],r['positive'],r['physical_positive'])
    print('REX_VARIABLE_OVERLAP_REFERENCE_OK '+json.dumps(r,separators=(',',':')))
