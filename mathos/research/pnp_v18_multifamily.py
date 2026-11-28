"""Experimental metered unit, Hall, signed-Horn and affine routing."""
import time
from collections import defaultdict, deque
from itertools import combinations
from .pnp_bounded_matching import Meter, Limit, normalize, check
from .pnp_hall_shared_index import solve as hall
from .pnp_xor_subsystem import attempt as xor_attempt


def verify_unit(n,f,c,b):
    normalize(n,f,b)  # validate every original input clause
    trace=c['trace'];known=set()
    if set(c)!={'decision','trace'} or c['decision']!='unsat' or not isinstance(trace,list) or not 1<=len(trace)<=n+1:
        raise ValueError('unit trace shape')
    for j,i in enumerate(trace):
        if type(i) is not int or not 0<=i<len(f):raise ValueError('premise index')
        q=set(f[i]);b.tick(1+len(f[i]))
        if any(-x in q for x in q) or q&known:raise ValueError('satisfied premise')
        rem={x for x in q if -x not in known}
        if not rem:
            if j!=len(trace)-1:raise ValueError('trailing trace')
            return True
        if len(rem)!=1:raise ValueError('not unit')
        known.update(rem)
    raise ValueError('no conflict')


def quick(n,f,b):
    # Raw unit/empty-clause probe. No result until full original validation.
    if type(n) is not int or n<0 or not isinstance(f,(list,tuple)):raise ValueError('input shape')
    if n>512 or len(f)>20000:raise Limit('input dimensions')
    seen={}
    for i,q in enumerate(f):
        b.tick()
        if not isinstance(q,(list,tuple)):raise ValueError('clause shape')
        trace=None
        if not q:trace=[i]
        elif len(q)==1:
            x=q[0]
            if type(x) is not int or not 0<abs(x)<=n:raise ValueError('literal range')
            if -x in seen:trace=[seen[-x],i]
            else:seen[x]=i
        if trace is not None:
            c={'decision':'unsat','trace':trace};verify_unit(n,f,c,b);return c
    return None


def polarity(n,clauses,b):
    # Renamable-Horn feasibility: not both literals of any clause become positive.
    g={s*v:set() for v in range(1,n+1) for s in (-1,1)}
    rev={v:set() for v in g};b.tick(1+4*n)
    for q in clauses:
        for x,y in combinations(q,2):
            b.tick(3)
            g[x].add(-y);rev[-y].add(x);g[y].add(-x);rev[-x].add(y)
    seen=set();order=[]
    for root in g:
        b.tick()
        if root in seen:continue
        seen.add(root);stack=[(root,iter(g[root]))]
        while stack:
            b.tick();x,it=stack[-1];y=next(it,None)
            if y is None:order.append(x);stack.pop()
            elif y not in seen:seen.add(y);stack.append((y,iter(g[y])))
    comp={};k=0
    for root in reversed(order):
        b.tick()
        if root in comp:continue
        comp[root]=k;stack=[root]
        while stack:
            x=stack.pop();b.tick(1+len(rev[x]))
            for y in rev[x]:
                if y not in comp:comp[y]=k;stack.append(y)
        k+=1
    b.tick(1+n)
    if any(comp[v]==comp[-v] for v in range(1,n+1)):return None
    signs=[1 if comp[v]>comp[-v] else -1 for v in range(1,n+1)]
    for q in clauses:
        b.tick(1+len(q))
        if sum(x*signs[abs(x)-1]>0 for x in q)>1:raise AssertionError('invalid Horn rename')
    return signs


def propagation(n,f,b):
    normalized=normalize(n,f,b)
    # Keep original indices for independently replayable unit steps.
    cs={};watch=defaultdict(list);ready=deque()
    for i,q in enumerate(f):
        b.tick(1+len(q));s=set(q)
        if any(-x in s for x in s):continue
        cs[i]=s
        for x in s:watch[x].append(i)
        if len(s)<=1:ready.append(i)
    known=set();trace=[]
    while ready:
        i=ready.popleft();q=cs[i];b.tick(1+len(q))
        if q&known:continue
        if not q:
            c={'decision':'unsat','trace':trace+[i]};verify_unit(n,f,c,b);return c
        if len(q)!=1:continue
        x=next(iter(q));known.add(x);trace.append(i)
        for j in watch[-x]:
            b.tick();cs[j].discard(-x)
            if len(cs[j])<=1:ready.append(j)
    # A signed least model is complete on renamable Horn CNF. On arbitrary
    # CNF the default candidate only earns SAT after checking every clause.
    def model(signs):
        b.tick(1+n)
        a=[v in known or (-v not in known and signs[v-1]==-1) for v in range(1,n+1)]
        for q in normalized:
            b.tick(1+len(q))
            if not any(a[abs(x)-1]==(x>0) for x in q):return None
        c={'decision':'sat','model':a};check(n,f,c,b);return c
    c=model([1]*n)
    if c is not None:return c
    # Use the original signed-Horn polarity criterion, not an assumption
    # that a failed recognition or failed model implies UNSAT.
    signs=polarity(n,normalized,b)
    return model(signs) if signs is not None else None


def _attempt(fn,n,f,q,t):
    b=Meter(q,t)
    try:
        c=fn(n,f,b)
        return {'decision':c['decision'] if c else 'unknown','status':'verified' if c else 'not_found',
                'certificate':c,'work_steps':b.used}
    except Limit:
        return {'decision':'unknown','status':'resource_exhausted','certificate':None,'work_steps':q}


def solve(n,f,records,*,steps=25000,seconds=1.25,use_hall=True):
    Meter(steps,seconds)
    if type(use_hall) is not bool or steps<20:raise ValueError('portfolio envelope')
    deadline=time.monotonic()+seconds;used=0;attempts=[];decision='unknown';cert=None
    routes=('quick','hall','propagation','affine') if use_hall else ('quick','propagation','affine')
    for route in routes:
        left=deadline-time.monotonic();remaining=steps-used
        if remaining<5 or left<=0:break
        # Quick scan bounded at 10%; Hall gets all remaining allowance and
        # retains its own 80% retrieval reserve; propagation reserves half
        # of its remaining budget for the existing affine route.
        q=min(remaining,max(1,steps//10)) if route=='quick' else max(1,remaining//2) if route=='propagation' else remaining
        t=left*q/remaining
        if route=='hall':r=hall(n,f,records,steps=q,seconds=t)
        elif route=='affine':
            raw=xor_attempt(n,f,q,t)
            r={'decision':raw['decision'],'status':raw['status'],'certificate':raw['proof'],'work_steps':raw['work_steps']}
        else:r=_attempt(quick if route=='quick' else propagation,n,f,q,t)
        if type(r['work_steps']) is not int or not 0<=r['work_steps']<=q:raise ValueError('route budget')
        attempts.append({'route':route,'quota':q,'report':r});used+=r['work_steps']
        if r['decision']!='unknown':decision=r['decision'];cert=r['certificate'];break
    return {'decision':decision,'certificate':cert,'work_steps':used,'attempts':attempts,'use_hall':use_hall}
