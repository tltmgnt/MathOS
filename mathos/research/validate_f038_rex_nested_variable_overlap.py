"""REX-020 independent row-product and normalized relational replay."""
import json
import sys
from itertools import product
if __package__:
    from .finite_relational_elimination import Factor, Solver
else:
    from finite_relational_elimination import Factor, Solver

PAIRS=((0,1),(0,2),(1,2))


def node(k,rows,children=None):
    return dict(k=k,rows=rows,children=[] if children is None else children)


def row(x,v):
    return [*format(x,'03b'),v]


def fixtures():
    for k,p,c,m in product(range(3),range(8),range(8),range(4)):
        yield node(3,[row(p,m&1)],[node(k,[row(c,m>>1)])]), (p==0 and c==0 and m==3) or (p==5 and c==3 and m==3)
    yield node(3,[]),True
    yield node(3,[row(0,1)]),True
    yield node(3,[row(0,1)],[node(2,[])]),True
    eq=[row(0,1),row(6,1)]; neq=[row(2,1),row(4,1)]
    yield node(3,[row(i,1) for i in range(8)],[node(0,eq),node(1,eq),node(2,neq)]),True
    yield node(3,[['0','10','101',1],['1','10','101',0],['1','10','101',1]],[node(1,[['1','101','00',1],['1','101','0',1]],[node(2,[['101','0','11',1]])]),node(0,[['1','10','1',1]])]),True
    seed=0x52455820; labels=['0','1','00','10','101']
    def rand():
        nonlocal seed
        seed=(1664525*seed+1013904223)&0xffffffff
        return seed
    def rows():
        return [[*[labels[(rand()>>16)%len(labels)] for _ in range(3)],rand()>>31] for _ in range(1+(rand()>>16)%3)]
    def plant(v,r):
        v['rows'].append(r)
        for c in v['children']:
            x,y=PAIRS[c['k']]
            plant(c,[r[x],r[y],labels[(rand()>>16)%len(labels)],1])
    for i in range(60):
        n=2+i%4; nodes=[node(3,rows())]
        for j in range(1,n):
            k=(rand()>>16)%3; p=(rand()>>16)%j
            nodes.append(node(k,rows())); nodes[p]['children'].append(nodes[j])
        if i%2: plant(nodes[0],['0','10','101',1])
        yield nodes[0],i<8


def encode(t):
    def record(r):
        return '011'+''.join(''.join('00'+b for b in x)+'010' for x in r[:3])+('101' if r[3] else '100')
    return '111'+format(t['k'],'02b')+''.join(map(record,t['rows']))+'110'+''.join(map(encode,t['children']))+'010'


def flatten(t):
    nodes=[]; n=3
    def visit(v,scope):
        nonlocal n
        nodes.append((v,scope))
        for c in v['children']:
            a,b=PAIRS[c['k']]; fresh=n; n+=1
            visit(c,(scope[a],scope[b],fresh))
    visit(t,(0,1,2))
    return nodes,n


def audit():
    cases=sat=physical_cases=physical_sat=stages=candidates=projected=0
    digest=physical_digest=2166136261
    for t,physical in fixtures():
        nodes,n=flatten(t)
        names=tuple(map(str,range(n)))
        labels=sorted({x for v,_ in nodes for r in v['rows'] for x in r[:3]})
        ids={x:i for i,x in enumerate(labels)}
        domains={v:set() for v in names}
        for v,scope in nodes:
            for r in v['rows']:
                for i,x in zip(scope,r): domains[names[i]].add(ids[x])
        fs=[Factor(tuple(names[i] for i in scope),tuple(tuple(ids[x] for x in r[:3]) for r in v['rows'] if r[3])) for v,scope in nodes]
        models=set(); witness=None
        for indices in product(*(range(len(v['rows'])) for v,_ in nodes)):
            assignment={}
            good=True
            for (v,scope),j in zip(nodes,indices):
                r=v['rows'][j]
                if not r[3] or any(i in assignment and assignment[i]!=ids[x] for i,x in zip(scope,r)):
                    good=False; break
                assignment.update((i,ids[x]) for i,x in zip(scope,r))
            if good:
                models.add(tuple(assignment[i] for i in range(n)))
                if witness is None: witness=indices
        solver=Solver(domains,batch_size=2); state=solver.initial_state(fs)
        for j in reversed(range(n)):
            state,trace=solver.stage(state,names[j])
            expected=tuple(sorted({a[:j] for a in models}))
            assert solver.relation(state).rows==expected
            stages+=1; candidates+=trace.candidate_count; projected+=len(expected)
        assert bool(solver.relation(state).rows)==bool(models)
        out='-' if witness is None else ''.join(str(int(i==j)) for (v,_),j in zip(nodes,witness) for i in range(len(v['rows'])))
        for ch in encode(t)+':'+out+';':
            digest=((digest^ord(ch))*16777619)&0xffffffff
            if physical: physical_digest=((physical_digest^ord(ch))*16777619)&0xffffffff
        cases+=1; sat+=bool(models); physical_cases+=physical; physical_sat+=physical and bool(models)
    return dict(cases=cases,sat=sat,unsat=cases-sat,physical_cases=physical_cases,physical_sat=physical_sat,stages=stages,candidates=candidates,projected=projected,digest=digest,physicalDigest=physical_digest)


if __name__=='__main__':
    r=audit()
    assert (r['digest'],r['physicalDigest'])==(1422736753,3143557437)
    if len(sys.argv)>1:
        with open(sys.argv[1]) as f: p=json.load(f)
        assert (p['digest'],p['physicalDigest'])==(r['digest'],r['physicalDigest'])
        assert (p['counts']['logicalCases'],p['counts']['physicalCases'],p['counts']['sat'],p['counts']['physicalSat'])==(r['cases'],r['physical_cases'],r['sat'],r['physical_sat'])
    print('REX_NESTED_VARIABLE_OVERLAP_REFERENCE_OK '+json.dumps(r,separators=(',',':')))
