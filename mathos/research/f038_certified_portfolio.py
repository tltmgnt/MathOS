"""Bounded, verified geometric-restart portfolio for affine semantic repair."""
import sys
from itertools import product
from mathos.research import f038_separator_repair as explicit
from mathos.research import f038_symbolic_affine as symbolic
from mathos.research import f038_factored_affine as factored
from mathos.research import f038_affine_obdd as obdd
from mathos.research.f038_affine_repair import flat, find_flip, safe


class BudgetExceeded(Exception):
    pass


def metered(fn,budget):
    """Python opcode meter, not a native CPU/memory resource sandbox."""
    if budget<1:
        raise ValueError('positive budget required')
    spent=0
    prior=sys.gettrace()
    def trace(frame,event,arg):
        nonlocal spent
        if event=='call':
            frame.f_trace_lines=False
            frame.f_trace_opcodes=True
        elif event=='opcode':
            if spent>=budget:
                raise BudgetExceeded
            spent+=1
        return trace
    try:
        sys.settrace(trace)
        result=fn()
    except BudgetExceeded:
        return 'timeout',None,spent
    finally:
        sys.settrace(prior)
    return result[0],result[1],spent


def checked_attempt(produce,verify,budget):
    def work():
        answer=produce()
        if answer is None:
            return 'abstain',None
        d,cert=answer
        if not verify(d,cert):
            return 'rejected',None
        return ('negative' if d is None else 'positive'),answer
    return metered(work,budget)


def schedule(names,attempt,cap):
    if cap<1 or cap&(cap-1):
        raise ValueError('cap must be a positive power of two')
    log=[]
    B=1
    while B<=cap:
        for name in names:
            status,answer,spent=attempt(name,B)
            assert 0<=spent<=B
            log.append((name,B,status,spent))
            if status in ('positive','negative'):
                return status,name,answer,tuple(log)
            assert status in ('timeout','abstain','rejected')
        B*=2
    return 'unknown',None,None,tuple(log)


ENGINES={'explicit':explicit,'affine_union':symbolic,
         'factored':factored,'obdd':obdd}
NAMES=('local',)+tuple(ENGINES)


def local_plan(f,n,c,tree):
    p=explicit.prepare(f,n,tree)
    if p is None or not 0<=c<len(p[3]):
        return None
    forms,db=p[2:4]
    return tuple(flat(D,forms) for D in db),tuple(range(len(db)))


def produce_local(f,n,c,tree):
    p=local_plan(f,n,c,tree)
    if p is None:
        return None
    flats,active=p
    d=find_flip(flats,active,c,n)
    return None if d is None else (d,('local',c,d))


def verify_local(f,n,c,tree,d,cert):
    p=local_plan(f,n,c,tree)
    return p is not None and d is not None and cert==('local',c,d) and safe(
        p[0],p[1],c,d,n)


def engine_attempt(name,f,n,c,tree,budget):
    if name=='local':
        return checked_attempt(lambda:produce_local(f,n,c,tree),
            lambda d,cert:verify_local(f,n,c,tree,d,cert),budget)
    engine=ENGINES[name]
    def produce():
        p=explicit.prepare(f,n,tree)
        if p is None or not 0<=c<len(p[3]):
            return None
        result=engine.produce(p,c)
        return result[:2]
    return checked_attempt(produce,
        lambda d,cert:engine.verify(f,n,c,d,cert,tree),budget)


def run(f,n,c,tree=None,cap=1<<22,names=NAMES):
    return schedule(names,lambda name,B:engine_attempt(name,f,n,c,tree,B),cap)


def schedule_audit():
    cases=solved=unknown=attempts=charged=0
    max_num,max_den=0,1
    for ts in product((1,2,3,5,9,17),repeat=4):
        for cap in (1,4,16,32):
            def attempt(i,B):
                t=ts[i]
                return ('positive',i,t) if t<=B else ('timeout',None,B)
            status,winner,answer,log=schedule(tuple(range(4)),attempt,cap)
            T=min(ts)
            spent=sum(row[-1] for row in log)
            assert (status=='positive')==(T<=cap)
            assert spent<=4*len(ts)*min(T,cap)
            if status=='positive':
                assert ts[winner]<=cap and answer==winner
            cases+=1
            solved+=status=='positive'
            unknown+=status=='unknown'
            attempts+=len(log)
            charged+=spent
            den=len(ts)*min(T,cap)
            if spent*max_den>max_num*den:
                max_num,max_den=spent,den
    assert (cases,solved,unknown,attempts,charged)==(5184,4477,707,24190,38546)
    assert 4*max_num==13*max_den
    print('F038_PORTFOLIO_SCHEDULE_OK cases=5184 solved=4477 unknown=707 '
          'attempts=24190 charged=38546 max_ratio=3.25')


def implementation_audit():
    fixtures=(
        (((-1,-2),),0,'positive'),
        (((1,),(2,),(-1,-2)),0,'negative'),
        (((1,),(-1,-2),(2,3),(-1,-2,-3)),0,'positive'))
    positive=negative=abstain=0
    for j,(f,c,want) in enumerate(fixtures):
        for name in NAMES:
            status,answer,spent=engine_attempt(name,f,3,c,None,1<<22)
            expected='abstain' if name=='local' and j in (1,2) else want
            assert status==expected,(name,j,status,spent)
            positive+=status=='positive'
            negative+=status=='negative'
            abstain+=status=='abstain'
        status,name,answer,log=run(f,3,c)
        assert status==want and name in NAMES
        assert all(row[-1]<=row[1] for row in log)
    assert (positive,negative,abstain)==(9,4,2)
    f,c,want=fixtures[0]
    assert run(f,3,c,cap=1)[0]=='unknown'
    status,answer,spent=checked_attempt(lambda:(0,()),lambda d,c:False,1024)
    assert status=='rejected' and answer is None
    def slow_verify(d,c):
        s=0
        for i in range(100000):
            s+=i
        return bool(s)
    status,answer,spent=checked_attempt(lambda:(0,()),slow_verify,256)
    assert status=='timeout' and answer is None and spent==256
    status,answer,spent=checked_attempt(lambda:(None,()),lambda d,c:True,1024)
    assert status=='negative' and answer==(None,())
    status,answer,spent=checked_attempt(lambda:None,lambda d,c:True,1024)
    assert status=='abstain' and answer is None
    print('F038_PORTFOLIO_ENGINES_OK fixtures=3 engines=5 positive=9 negative=4 '
          'abstain=2 integrated=3 tiny_cap_unknown=1 rejected=1 verifier_timeout=1')


def grid_audit():
    sizes=(2,3,4,8,16,32)
    counts=[]
    for k in sizes:
        n=k*k
        edges=[(i,j) for i in range(n) for j in (i+1,i+k)
               if j<n and (j==i+k or i%k<k-1)]
        assert len(edges)==2*k*(k-1)
        adj=[{i} for i in range(n)]
        for a,b in edges:
            adj[a].add(b)
            adj[b].add(a)
        orig=len(edges)
        chosen=[]
        while edges:
            a,b=edges[0]
            chosen.append((a,b))
            forbidden=adj[a]|adj[b]
            edges=[(x,y) for x,y in edges if x not in forbidden and y not in forbidden]
        assert 40*len(chosen)>=orig
        for i,(a,b) in enumerate(chosen):
            for x,y in chosen[i+1:]:
                assert not ({x,y}&(adj[a]|adj[b]))
        counts.append(len(chosen))
    assert counts==[1,2,4,15,60,231]
    print('F038_PORTFOLIO_COMMON_MESSAGE_OK grids=2,3,4,8,16,32 '
          'induced_matching=1,2,4,15,60,231 max_rank=1024')


if __name__=='__main__':
    schedule_audit()
    implementation_audit()
    grid_audit()
