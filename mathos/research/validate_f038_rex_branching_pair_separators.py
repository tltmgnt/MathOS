"""REX-016: independent finite relational and full-model replay."""
import json
import sys
from itertools import product
if __package__:
    from .finite_relational_elimination import Factor, Solver
else:
    from finite_relational_elimination import Factor, Solver


def fixtures():
    def root(b,c,x):
        return [[(x>>(j*b+i))&1 for i in range(b)] for j in range(c)]
    def child(b,c,u,x,y):
        return dict(u=u,t=[[[[(x>>(i+len(u)*(j+b*k)))&1,(y>>(i+len(u)*(j+b*k)))&1] for i in range(len(u))] for j in range(b)] for k in range(c)])
    for b,c in product(range(1,4),repeat=2):
        for x in range(min(16,2**(b*c))):
            yield root(b,c,x),[],x<2
    for x,y in product(range(16),repeat=2):
        yield root(2,2,15),[child(2,2,[1],x,y)],x==y and x%3==0
    for x,y in product(range(16),repeat=2):
        yield root(2,2,15),[child(2,2,[1],x,15),child(2,2,[1],y,15)],x==y and x%5==0
    yield root(2,2,15),[child(2,2,[1],9,15),child(2,2,[1],6,15)],True
    yield root(2,2,15),[child(2,2,[1,1],85,170)],True
    seed=0x52455816
    def rand():
        nonlocal seed
        seed=(1664525*seed+1013904223)&0xffffffff
        return seed
    for i in range(36):
        b=1+(rand()>>28)%3; c=1+(rand()>>28)%3; g=1+i%3
        R=[[rand()>>31 for _ in range(b)] for _ in range(c)]
        children=[]
        for j in range(g):
            m=1+(rand()>>28)%4
            u=[rand()>>31 for _ in range(m)]
            t=[[[[rand()>>31,rand()>>31] for _ in range(m)] for _ in range(b)] for _ in range(c)]
            children.append(dict(u=u,t=t))
        if i%2:
            B=(rand()>>16)%b; C=(rand()>>16)%c; R[C][B]=1
            for ch in children:
                a=(rand()>>16)%len(ch['u']); ch['u'][a]=1; ch['t'][C][B][a]=[1,1]
        yield R,children,i<8
    yield root(2,3,32),[dict(u=[1]*m,t=[[[[int(b==1 and c==2 and j==a)]*2 for j in range(m)] for b in range(2)] for c in range(3)]) for a,m in zip((1,3,2),(2,4,3))],True


def encode(root,children):
    def bit(x): return '001' if x else '000'
    return ''.join('010'+''.join(map(bit,g))+'101' for g in root)+'110'+''.join(''.join(map(bit,ch['u']))+'111'+''.join('010'+''.join('011'+''.join(bit(b) for row in p for b in row)+'100' for p in g)+'101' for g in ch['t'])+'110' for ch in children)


def audit():
    cases=sat=physical_cases=physical_sat=steps=candidates=projected=0
    digest=physical_digest=2166136261
    for root,children,physical in fixtures():
        b,c=len(root[0]),len(root)
        names=('b','c',*(f'a{i}' for i in range(len(children))))
        domains=dict(zip(names,(range(b),range(c),*(range(len(ch['u'])) for ch in children))))
        fs=[Factor(names[:2],tuple((i,j) for i,j in product(range(b),range(c)) if root[j][i]))]
        for k,ch in enumerate(children):
            v=names[k+2]; m=len(ch['u'])
            fs.append(Factor((v,),tuple((a,) for a in range(m) if ch['u'][a])))
            for f in range(2):
                fs.append(Factor(('b','c',v),tuple((i,j,a) for i,j,a in product(range(b),range(c),range(m)) if ch['t'][j][i][a][f])))
        models=[a for a in product(*domains.values()) if root[a[1]][a[0]] and all(ch['u'][a[k+2]] and all(ch['t'][a[1]][a[0]][a[k+2]]) for k,ch in enumerate(children))]
        solver=Solver(domains,batch_size=2); state=solver.initial_state(fs)
        for v in names[2:]+names[:2]:
            state,trace=solver.stage(state,v)
            expected=tuple(sorted({tuple(a[names.index(w)] for w in state.order) for a in models}))
            assert solver.relation(state).rows==expected
            assert trace.candidate_count==(c if v=='c' else b*c if v=='b' else b*c*len(domains[v]))
            steps+=1; candidates+=trace.candidate_count; projected+=len(expected)
        assert bool(solver.relation(state).rows)==bool(models)
        a=min(models,key=lambda a:(a[1],a[0],*a[2:])) if models else None
        out='-' if a is None else ''.join(str(int(i==a[0] and j==a[1])) for j in range(c) for i in range(b))+''.join(str(int(j==a[k+2])) for k,ch in enumerate(children) for j in range(len(ch['u'])))
        for ch in encode(root,children)+':'+out+';':
            digest=((digest^ord(ch))*16777619)&0xffffffff
            if physical: physical_digest=((physical_digest^ord(ch))*16777619)&0xffffffff
        cases+=1; sat+=bool(models); physical_cases+=physical; physical_sat+=physical and bool(models)
    return dict(cases=cases,sat=sat,unsat=cases-sat,physical_cases=physical_cases,physical_sat=physical_sat,stages=steps,candidates=candidates,projected=projected,digest=digest,physicalDigest=physical_digest)


if __name__=='__main__':
    r=audit()
    assert (r['digest'],r['physicalDigest'])==(1105793626,640776826)
    if len(sys.argv)>1:
        with open(sys.argv[1]) as f: p=json.load(f)
        assert (p['digest'],p['physicalDigest'])==(r['digest'],r['physicalDigest'])
        assert (p['counts']['logicalCases'],p['counts']['physicalCases'],p['counts']['sat'],p['counts']['physicalSat'])==(r['cases'],r['physical_cases'],r['sat'],r['physical_sat'])
    print('REX_BRANCHING_PAIR_REFERENCE_OK '+json.dumps(r,separators=(',',':')))
