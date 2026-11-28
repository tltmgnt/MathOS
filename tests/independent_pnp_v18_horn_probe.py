"""Standalone Horn certificate prototype and exhaustive development probe.
A non-Horn input is UNKNOWN. No unrestricted SAT claim.
"""
from collections import defaultdict, deque, Counter
from itertools import product
import json, random, time


def normalize(n, f):
    if type(n) is not int or n < 0:
        raise ValueError('variable count')
    out = []
    for c in f:
        if any(type(x) is not int or not 0 < abs(x) <= n for x in c):
            raise ValueError('literal range')
        s = frozenset(c)
        out.append(s if not any(-x in s for x in s) else None)
    return out


def verify(n, f, result):
    """Direct model check or original-clause Horn inference replay."""
    g = normalize(n, f)
    d = result['decision']
    if d == 'sat':
        a = result['model']
        if len(a) != n or any(type(v) is not bool for v in a):
            raise ValueError('invalid model')
        if any(c is not None and not any(a[abs(x)-1] == (x > 0) for x in c) for c in g):
            raise ValueError('false model')
    elif d == 'unsat':
        known = set()
        trace = result['trace']
        if not trace:
            raise ValueError('missing trace')
        for j, i in enumerate(trace):
            if type(i) is not int or not 0 <= i < len(g) or g[i] is None:
                raise ValueError('invalid premise')
            c = g[i]
            heads = [x for x in c if x > 0]
            if len(heads) > 1 or any(-x not in known for x in c if x < 0):
                raise ValueError('unjustified inference')
            if not heads:
                if j != len(trace)-1:
                    raise ValueError('trailing steps')
                return True
            if heads[0] in known:
                raise ValueError('duplicate derivation')
            known.add(heads[0])
        raise ValueError('missing conflict')
    elif d == 'unknown':
        if set(result) != {'decision'}:
            raise ValueError('uncredited evidence')
    else:
        raise ValueError('invalid verdict')
    return True


def solve(n, f):
    """Queue-based forward chaining. One watch visit per body occurrence."""
    g = normalize(n, f)
    remaining, head, watch, ready = {}, {}, defaultdict(list), deque()
    for i, c in enumerate(g):
        if c is None:
            continue
        h = [x for x in c if x > 0]
        if len(h) > 1:
            return {'decision':'unknown'}
        head[i] = h[0] if h else None
        body = [-x for x in c if x < 0]
        remaining[i] = len(body)
        for v in body:
            watch[v].append(i)
        if not body:
            ready.append(i)
    known, trace = set(), []
    while ready:
        i = ready.popleft()
        h = head[i]
        if h is None:
            result = {'decision':'unsat','trace':trace+[i]}
            verify(n, f, result)
            return result
        if h in known:
            continue
        known.add(h)
        trace.append(i)
        for j in watch[h]:
            remaining[j] -= 1
            if remaining[j] == 0:
                ready.append(j)
    result = {'decision':'sat','model':[v in known for v in range(1,n+1)]}
    verify(n, f, result)
    return result


def reference(n, f):
    return any(all(any(a[abs(x)-1] == (x > 0) for x in c) for c in f)
               for a in product((False,True),repeat=n))


def probe():
    counts = Counter()
    start = time.perf_counter()
    # Exhaustive canonical n=2 Horn clause sets, including empty clause.
    cs = [tuple(s*i for i,s in enumerate(signs,1) if s)
          for signs in product((-1,0,1),repeat=2) if signs.count(1)<=1]
    for mask in range(1<<len(cs)):
        f = [c for i,c in enumerate(cs) if mask>>i&1]
        r = solve(2,f)
        assert r['decision'] == ('sat' if reference(2,f) else 'unsat')
        counts['exhaustive_'+r['decision']] += 1
    # Fixed independent development generator, not a blinded external corpus.
    rng = random.Random(180031)
    for _ in range(500):
        n=rng.randint(1,8); f=[]
        for _ in range(rng.randint(0,4*n)):
            body=rng.sample(range(1,n+1),rng.randint(0,min(3,n)))
            choices=[v for v in range(1,n+1) if v not in body]
            h=[rng.choice(choices)] if choices and rng.randrange(2) else []
            f.append([-v for v in body]+h)
        r=solve(n,f)
        assert r['decision']==('sat' if reference(n,f) else 'unsat')
        counts['random_'+r['decision']]+=1
        # Variable relabeling, clause reorder, tautology, duplicate literals.
        p=list(range(1,n+1));rng.shuffle(p)
        g=[[p[abs(x)-1]*(1 if x>0 else -1) for x in c+c[:1]] for c in f]
        g.append([1,-1]);rng.shuffle(g)
        assert solve(n,g)['decision']==r['decision']
        counts['metamorphic']+=1
    scaling=[]
    for n in (20,40,80,160,320,640,1280,2560,5120):
        f=[[1]]+[[-i,i+1] for i in range(1,n)]
        t=time.perf_counter();u=solve(n,f+[[-n]]);s=solve(n,f+[[n]])
        assert u['decision']=='unsat' and len(u['trace'])==n+1 and s['decision']=='sat'
        scaling.append({'n':n,'unsat_trace_steps':len(u['trace']),'sat_model_bits':len(s['model']),
                        'paired_seconds':time.perf_counter()-t})
    for bad in ({'decision':'unsat','trace':[1]}, {'decision':'unsat','trace':[0]},
                {'decision':'sat','model':[False]}):
        try:verify(1,[[1],[-1]],bad)
        except ValueError:counts['tamper_rejected']+=1
        else:raise AssertionError('forgery accepted')
    assert solve(2,[[1,2]])=={'decision':'unknown'}
    return {'counts':dict(counts),'scaling':scaling,'elapsed_seconds':time.perf_counter()-start,
            'scope':'standalone development prototype; not integrated or blind'}

if __name__=='__main__': print(json.dumps(probe(),sort_keys=True,indent=2))
